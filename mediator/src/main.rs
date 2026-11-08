//! Command-line mediator: read a policy file and a list of actions, print the decision for each.
//!
//! Used by `scripts/policy_diff.py` to compare three implementations (Lean, Python, Rust) on the same cases.
//!
//! Usage:
//!   mediator --policy policy.txt --actions actions.txt
//!
//! Both files are line-based (see `mediator::Policy::parse`). Output is one line per action:
//!   who|what|res|may|owner|forbidden

use mediator::{Action, Policy};
use std::env;
use std::fs;
use std::process;

fn usage() -> ! {
    eprintln!("usage: mediator --policy <policy.txt> --actions <actions.txt>");
    process::exit(2);
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
            _ => usage(),
        }
    }
    let (Some(pp), Some(ap)) = (policy_path, actions_path) else { usage() };

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
        println!("{}|{}|{}|{}|{}|{}", a.who, a.what, a.res, d.may, d.owner, d.forbidden);
    }
}
