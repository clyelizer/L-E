---
name: subagent-diagnostic
description: Diagnose and fix silent subagent failures caused by missing model providers — check agent definitions, override with available models at project level.
source: auto-skill
extracted_at: '2026-06-14T16:00:08.463Z'
---

# Subagent Silent Failure Diagnostic

Use this skill when a subagent (e.g., `code-reviewer`, `planner`, `architect`) fails silently with a generic error like "Subagent execution failed" and no useful error details are provided.

## Root Cause

The most common cause is that the subagent's agent definition specifies a `model:` that the user does not have configured in their `modelProviders`. The subagent spawning mechanism does **not** correctly apply `fallback_model: default` — it simply fails silently instead.

## Diagnostic Steps

1. **Find the agent definition files.** Search in order of precedence (highest to lowest):
   - Project-level: `.qwen/agents/<agent-name>.agent.md`
   - User-level: `~/.qwen/agents/<agent-name>.agent.md`
   - Extension-level: `.qwen/extensions/<extension>/agents/<agent-name>.agent.md`

2. **Check the `model:` field in the frontmatter.** Look for model names like `sonnet`, `opus`, `claude-sonnet-4-*`, `gpt-4`, etc.

3. **Check your configured modelProviders.** Read `~/.qwen/settings.json` or `~/.config/qwen/settings.json` and look at the `modelProviders` section to see which models you actually have available.

4. **If the specified model is not in your modelProviders**, that's the root cause.

## Fix: Create a Project-Level Override

1. Create the file `.qwen/agents/<agent-name>.agent.md` (project-level takes highest precedence).

2. Copy the full content from the extension-level or user-level definition.

3. Change the `model:` field in the frontmatter to a model you have configured (e.g., `model: deepseek-chat`).

4. Update the **Model Fallback** section at the bottom of the file to match (change the model name in the fallback text).

5. That's it — the project-level override will be used instead of the extension-level one.

## Verification

After creating the override, try invoking the subagent again. It should now execute using your available model instead of failing silently.

## Edge Cases

- **Multiple failing subagents**: Apply the same fix for each agent that fails silently — create separate `.agent.md` files for each.
- **Agent uses `.md` instead of `.agent.md`**: Some agents may use the `.md` extension without `.agent.md`. Check both and create the override with the same extension.
- **Other silent failures**: If a different agent (like `planner`, `tdd-guide`, etc.) fails silently, apply the same diagnostic — it's almost always a model mismatch.

## Example

If `code-reviewer` fails silently:

1. Read `/home/coulibaly/.qwen/extensions/ai-dev-kit/agents/code-reviewer.agent.md` — see `model: sonnet`
2. Check settings.json — no Claude/Sonnet model configured
3. Create `.qwen/agents/code-reviewer.agent.md` with `model: deepseek-chat`
4. Subagent now runs successfully
