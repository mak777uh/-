"""

memory_manager.py — Управление памятью агента.

[v5.5-EXP FINAL Rev.7]

"""

import json

import os

from datetime import datetime

import config

class MemoryManager:

    def __init__(self, memory_dir=config.MEMORY_DIR):

        self.memory_dir = memory_dir

        self.current_state_path = os.path.join(

            memory_dir,

            "current_state.json",

        )

        self.decisions_log_path = os.path.join(

            memory_dir,

            "decisions_log.jsonl",

        )

        self.goal_state_path = config.GOAL_STATE_PATH

        self.morphogen_effects_path = os.path.join(

            memory_dir,

            "morphogen_channel_effects.json",

        )

        os.makedirs(memory_dir, exist_ok=True)

        os.makedirs(os.path.join(memory_dir, "theories"), exist_ok=True)

        goal_dir = os.path.dirname(self.goal_state_path)

        if goal_dir:

            os.makedirs(goal_dir, exist_ok=True)

    def save_state(

        self,

        step,

        sim_step,

        observation,

        parsed_action,

        action_result,

        topology_metrics=None,

        model_params=None,

        stress_summary=None,

        cost=0.0,

        budget_remaining=None,

        goal_state=None,

        symmetric_chamfer_error=None,

    ):

        observation_summary = observation

        if len(observation_summary) > 2000:

            observation_summary = observation_summary[:2000] + "..."

        state = {

            "step": step,

            "sim_step": sim_step,

            "timestamp": datetime.now().isoformat(),

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

            "observation_summary": observation_summary,

            "action": parsed_action.get("action"),

            "hypothesis": parsed_action.get("hypothesis"),

            "justification": parsed_action.get("justification"),

            "confidence": parsed_action.get("confidence", 0.5),

            "result": action_result,

            "cost": float(cost),

            "budget_remaining": budget_remaining,

        }

        if topology_metrics:

            state["topology"] = topology_metrics

        if model_params:

            state["params"] = model_params

        if stress_summary:

            state["stress"] = stress_summary

        if goal_state:

            state["goal_state"] = goal_state

        if symmetric_chamfer_error is not None:

            state["symmetric_chamfer_error"] = symmetric_chamfer_error

        with open(self.current_state_path, "w", encoding="utf-8") as f:

            json.dump(state, f, indent=2, ensure_ascii=False)

        with open(self.decisions_log_path, "a", encoding="utf-8") as f:

            f.write(json.dumps(state, ensure_ascii=False) + "\n")

    def load_recent_decisions(self, n=5):

        if not os.path.exists(self.decisions_log_path):

            return []

        decisions = []

        with open(self.decisions_log_path, "r", encoding="utf-8") as f:

            lines = f.readlines()

        for line in lines[-n:]:

            try:

                decisions.append(json.loads(line.strip()))

            except json.JSONDecodeError:

                continue

        return decisions

    def save_theory(self, name, content):

        safe_name = "".join(

            c if c.isalnum() or c in "-_." else "_"

            for c in name

        )

        path = os.path.join(

            self.memory_dir,

            "theories",

            f"{safe_name}.md",

        )

        with open(path, "w", encoding="utf-8") as f:

            f.write(f"# Теория: {name}\n\n")

            f.write(f"Дата: {datetime.now().isoformat()}\n\n")

            f.write(content)

        print(f"Теория сохранена: {path}")

    def load_goal_state(self):

        if os.path.exists(self.goal_state_path):

            try:

                with open(self.goal_state_path, "r", encoding="utf-8") as f:

                    return json.load(f)

            except Exception:

                pass

        default_goal = {

            "phase": "UNKNOWN",

            "target_topology": dict(config.TARGET_TOPOLOGY),

            "priority": "stability",

            "notes": "Auto-generated default goal state.",

            "updated_at": datetime.now().isoformat(),

        }

        self.save_goal_state(default_goal)

        return default_goal

    def save_goal_state(self, goal_state):

        goal_state = dict(goal_state or {})

        goal_state["updated_at"] = datetime.now().isoformat()

        if "target_topology" not in goal_state:

            goal_state["target_topology"] = dict(config.TARGET_TOPOLOGY)

        with open(self.goal_state_path, "w", encoding="utf-8") as f:

            json.dump(goal_state, f, indent=2, ensure_ascii=False)

    def save_morphogen_effects(self, entry):

        effects = []

        if os.path.exists(self.morphogen_effects_path):

            try:

                with open(

                    self.morphogen_effects_path,

                    "r",

                    encoding="utf-8",

                ) as f:

                    effects = json.load(f)

            except Exception:

                effects = []

        if not isinstance(effects, list):

            effects = []

        entry = dict(entry or {})

        entry["timestamp"] = datetime.now().isoformat()

        entry["spec_version"] = config.SPEC_VERSION

        entry["revision"] = config.SPEC_REVISION

        effects.append(entry)

        with open(self.morphogen_effects_path, "w", encoding="utf-8") as f:

            json.dump(effects, f, indent=2, ensure_ascii=False)
