# run_agents_demo.py

from protocols.utils.skills import EmbodiedAgent, Skill
from protocols.utils.messaging import MessageHub

# --- Setup Message Bus ---
bus = MessageHub()

# --- Define Example Skills ---


def analyze_patch(data):
    return {"insight": f"Patch complexity score = {len(str(data)) % 7}"}


def draft_fix(data):
    return {"fix": f"auto_fix_for::{data.get('bug', 'unknown')}"}


def warn_if_risky(data):
    if "delete" in str(data).lower():
        return {"warning": "Potentially destructive operation flagged."}
    return {"status": "Safe"}


# --- Create Agents ---
ci_agent = EmbodiedAgent("CI Watcher")
ci_agent.register_skill(Skill("analyze_patch", analyze_patch))

patch_bot = EmbodiedAgent("PatchBot")
patch_bot.register_skill(Skill("draft_fix", draft_fix))

red_flagger = EmbodiedAgent("RedFlagger")
red_flagger.register_skill(Skill("warn_if_risky", warn_if_risky))

# --- Subscribe to Bus ---


def handle_ci_patch(msg):
    result = ci_agent.invoke("analyze_patch", msg.data)
    print(f"[CI Watcher] {result}")
    bus.publish("patch_analysis_done", result)


def handle_patch_analysis(msg):
    fix = patch_bot.invoke("draft_fix", msg.data)
    print(f"[PatchBot] {fix}")
    bus.publish("fix_drafted", fix)


def handle_fix_drafted(msg):
    warn = red_flagger.invoke("warn_if_risky", msg.data)
    print(f"[RedFlagger] {warn}")


bus.subscribe("ci_patch", handle_ci_patch)
bus.subscribe("patch_analysis_done", handle_patch_analysis)
bus.subscribe("fix_drafted", handle_fix_drafted)

# --- Simulate Event ---
print("\n--- Simulated Agent Chain ---")
bus.publish("ci_patch", {"bug": "deleting critical index", "line": 120})
