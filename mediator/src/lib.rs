//! Policy mediator: the small piece of code that decides what an agent may do.
//!
//! Level B in the herness model. The policy is proved in `formal/Policy.lean`; the Python rule lives in
//! `scripts/check_autonomy.py`; this crate is the third implementation, and `scripts/policy_diff.py` checks
//! that all three agree.
//!
//! Why no dependencies. Every dependency brings a build script, and a build script needs a linker the machine
//! may not have (MSVC was absent on 08.11, and the GNU toolchain failed on `GetHostNameW`). A mediator whose
//! proof is in Lean does not need a serialisation library: the format is one line per action.
//!
//! Format (both input and output), one action per line, fields separated by `|`:
//!
//!   policy:   allowed|needs_owner|forbidden|who|what|res
//!   action:   who|what|res
//!   decision: who|what|res|may|owner|forbidden
//!
//! The rule, in one sentence: **forbid beats everything; an action is allowed without asking only if it is in
//! the allowed list and in neither of the other two.**

use std::env;
use std::fs;
use std::process;

/// One action: who, what, over which resource.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Action {
    pub who: String,
    pub what: String,
    pub res: String,
}

impl Action {
    pub fn parse(line: &str) -> Option<Action> {
        let line = line.strip_prefix('\u{feff}').unwrap_or(line);
        let f: Vec<&str> = line.split('|').map(|s| s.trim()).collect();
        if f.len() != 3 {
            return None;
        }
        Some(Action { who: f[0].into(), what: f[1].into(), res: f[2].into() })
    }
}

/// The three lists of the policy.
#[derive(Debug, Clone, Default)]
pub struct Policy {
    pub allowed: Vec<Action>,
    pub needs_owner: Vec<Action>,
    pub forbidden: Vec<Action>,
}

/// What the mediator decides.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Decision {
    /// may be done without asking the owner
    pub may: bool,
    /// requires the owner
    pub owner: bool,
    /// forbidden outright
    pub forbidden: bool,
}

impl Policy {
    /// Read a policy file: `list|who|what|res` per line, `#` starts a comment.
    ///
    /// A leading UTF-8 BOM is stripped: editors on Windows write one, and a parser that silently ignores the
    /// first rule because of an invisible byte is exactly the kind of hole this crate exists to close.
    pub fn parse(text: &str) -> Policy {
        let mut p = Policy::default();
        let text = text.strip_prefix('\u{feff}').unwrap_or(text);
        for raw in text.lines() {
            let line = raw.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            let f: Vec<&str> = line.split('|').map(|s| s.trim()).collect();
            if f.len() != 4 {
                continue;
            }
            let a = Action { who: f[1].into(), what: f[2].into(), res: f[3].into() };
            match f[0] {
                "allowed" => p.allowed.push(a),
                "needs_owner" => p.needs_owner.push(a),
                "forbidden" => p.forbidden.push(a),
                _ => {}
            }
        }
        p
    }

    fn has(list: &[Action], a: &Action) -> bool {
        list.iter().any(|x| x == a)
    }

    /// The decision. This is the only place the rule is written, so there is one place to compare.
    pub fn decide(&self, a: &Action) -> Decision {
        let in_allowed = Self::has(&self.allowed, a);
        let in_owner = Self::has(&self.needs_owner, a);
        let in_forbidden = Self::has(&self.forbidden, a);
        Decision {
            // forbid beats everything
            may: in_allowed && !in_forbidden && !in_owner,
            // a forbidden action cannot be done even with the owner's consent
            owner: in_owner && !in_forbidden,
            forbidden: in_forbidden,
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut policy_path = None;
    let mut actions_path = None;
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--policy" => {
                policy_path = args.get(i + 1).cloned();
                i += 2;
            }
            "--actions" => {
                actions_path = args.get(i + 1).cloned();
                i += 2;
            }
            _ => {
                eprintln!("usage: mediator --policy <policy.txt> --actions <actions.txt>");
                process::exit(2);
            }
        }
    }
    let (Some(pp), Some(ap)) = (policy_path, actions_path) else {
        eprintln!("usage: mediator --policy <policy.txt> --actions <actions.txt>");
        process::exit(2);
    };

    let policy = match fs::read_to_string(&pp) {
        Ok(s) => Policy::parse(&s),
        Err(e) => {
            eprintln!("cannot read policy {pp}: {e}");
            process::exit(1);
        }
    };
    let text = match fs::read_to_string(&ap) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("cannot read actions {ap}: {e}");
            process::exit(1);
        }
    };

    for raw in text.lines() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let Some(a) = Action::parse(line) else { continue };
        let d = policy.decide(&a);
        println!(
            "{}|{}|{}|{}|{}|{}",
            a.who, a.what, a.res, d.may, d.owner, d.forbidden
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn act(what: &str) -> Action {
        Action { who: "lead".into(), what: what.into(), res: "repo".into() }
    }

    fn policy(allowed: &[&str], owner: &[&str], forbidden: &[&str]) -> Policy {
        Policy {
            allowed: allowed.iter().map(|w| act(w)).collect(),
            needs_owner: owner.iter().map(|w| act(w)).collect(),
            forbidden: forbidden.iter().map(|w| act(w)).collect(),
        }
    }

    /// F-POLICY-1: forbid beats allow.
    #[test]
    fn forbid_beats_allow() {
        let p = policy(&["commit"], &[], &["commit"]);
        let d = p.decide(&act("commit"));
        assert!(!d.may, "an action in both lists must not be allowed");
        assert!(d.forbidden);
    }

    /// F-POLICY-2: forbid beats the owner's consent.
    #[test]
    fn forbid_beats_owner() {
        let p = policy(&[], &["publish"], &["publish"]);
        let d = p.decide(&act("publish"));
        assert!(!d.owner, "a forbidden action cannot be done even with consent");
        assert!(d.forbidden);
    }

    /// F-POLICY-3: allowed without asking does not need the owner.
    #[test]
    fn allowed_not_owner() {
        let p = policy(&["commit"], &[], &[]);
        let d = p.decide(&act("commit"));
        assert!(d.may && !d.owner && !d.forbidden);
    }

    /// F-POLICY-6: an empty policy allows nothing.
    #[test]
    fn empty_allows_nothing() {
        let p = Policy::default();
        let d = p.decide(&act("commit"));
        assert!(!d.may && !d.owner && !d.forbidden);
    }

    /// An action in no list is not silently allowed.
    #[test]
    fn unknown_action_is_not_allowed() {
        let p = policy(&["commit"], &[], &[]);
        let d = p.decide(&act("dance"));
        assert!(!d.may && !d.owner && !d.forbidden);
    }

    /// Parsing: a policy file yields the three lists.
    #[test]
    fn parses_policy() {
        let p = Policy::parse("allowed|lead|commit|repo\nneeds_owner|lead|publish|zenodo\nforbidden|lead|force_push|repo\n");
        assert_eq!(p.allowed.len(), 1);
        assert_eq!(p.needs_owner.len(), 1);
        assert_eq!(p.forbidden.len(), 1);
    }
}
