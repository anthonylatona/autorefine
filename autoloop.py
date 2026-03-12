#!/usr/bin/env python3
"""
autoloop.py — A self-improving document loop inspired by Karpathy's autoresearch.
No GPU needed. Runs entirely via API calls.

Usage:
    python3 autoloop.py --iterations 20
    python3 autoloop.py --iterations 5 --verbose
"""

import anthropic
import git
import json
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

ARTIFACT_PATH = "artifact.md"
GOALS_PATH    = "goals.md"
LOG_PATH      = "loop_log.json"
MODEL         = "claude-sonnet-4-20250514"

# ── Helpers ───────────────────────────────────────────────────────────────────

def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def write_file(path: str, content: str):
    Path(path).write_text(content, encoding="utf-8")

def get_git_repo() -> git.Repo:
    """Get or initialize the git repo in the current directory."""
    try:
        return git.Repo(".")
    except git.exc.InvalidGitRepositoryError:
        print("  → Initializing git repo...")
        repo = git.Repo.init(".")
        # Initial commit so we have a HEAD to revert to
        repo.index.add([ARTIFACT_PATH, GOALS_PATH])
        repo.index.commit("Initial: baseline artifact before optimization loop")
        print("  → Git repo initialized with baseline commit.")
        return repo

def get_iteration_history(repo: git.Repo) -> list:
    """Pull commit history to show the agent what has already been tried."""
    history = []
    try:
        for commit in list(repo.iter_commits())[:10]:  # last 10 commits
            history.append({
                "message": commit.message.strip(),
                "time": commit.committed_datetime.isoformat()
            })
    except Exception:
        pass
    return history

def load_log() -> list:
    if Path(LOG_PATH).exists():
        return json.loads(Path(LOG_PATH).read_text())
    return []

def save_log(log: list):
    Path(LOG_PATH).write_text(json.dumps(log, indent=2))

def print_divider():
    print("\n" + "─" * 60 + "\n")

# ── Core API Calls ─────────────────────────────────────────────────────────────

def get_mutation(client: anthropic.Anthropic, artifact: str, goals: str, history: list, verbose: bool) -> tuple[str, str, str]:
    """
    Ask the agent to propose ONE specific improvement.
    Returns: (modified_artifact, hypothesis, change_summary)
    """

    history_text = ""
    if history:
        history_text = "\n\nPREVIOUS ITERATIONS (do not repeat these):\n"
        for h in history:
            history_text += f"- {h['message']}\n"

    prompt = f"""You are an expert product strategist and technical writer optimizing a product specification document.

GOALS AND SCORING CRITERIA:
{goals}

CURRENT DOCUMENT:
{artifact}
{history_text}

YOUR TASK:
1. Identify the SINGLE weakest element in the document right now
2. State your hypothesis: what is wrong and why fixing it will improve the score
3. Make exactly ONE targeted improvement — fix that specific weakness
4. Do not rewrite entire sections. Make a surgical change.

RESPOND IN THIS EXACT FORMAT — do not deviate:

HYPOTHESIS: [one sentence explaining what is weak and why your change will improve the score]

CHANGE_SUMMARY: [one sentence describing exactly what you changed, suitable for a git commit message]

IMPROVED_DOCUMENT:
[the complete improved document — every section, with your one change applied]"""

    if verbose:
        print("  → Calling agent for mutation proposal...")

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text

    # Parse the structured response
    try:
        hypothesis = raw.split("HYPOTHESIS:")[1].split("CHANGE_SUMMARY:")[0].strip()
        change_summary = raw.split("CHANGE_SUMMARY:")[1].split("IMPROVED_DOCUMENT:")[0].strip()
        improved_doc = raw.split("IMPROVED_DOCUMENT:")[1].strip()
    except IndexError:
        print("  ⚠ Agent response format was unexpected. Skipping iteration.")
        return artifact, "parse error", "parse error"

    return improved_doc, hypothesis, change_summary


def evaluate_document(client: anthropic.Anthropic, artifact: str, goals: str, verbose: bool) -> float:
    """
    Ask a judge to score the document 0-100.
    Uses a separate prompt so the judge has no knowledge of what changed.
    """

    prompt = f"""You are a rigorous product document evaluator. Score the following product specification on a scale of 0-100.

SCORING CRITERIA (25 points each):
1. Internal Consistency — sections agree, no contradictions, architecture matches features
2. Completeness — no obvious gaps, open questions are answered, nothing is hand-waved
3. Specificity — claims are concrete, strategies are real, numbers are justified
4. Strategic Soundness — GTM makes sense, risks have mitigations, positioning is realistic

DOCUMENT TO EVALUATE:
{artifact}

RESPOND IN THIS EXACT FORMAT:
SCORE: [number 0-100]
REASONING: [2-3 sentences explaining the score — what dragged it down, what held it up]"""

    if verbose:
        print("  → Calling judge for evaluation...")

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text

    try:
        score_line = raw.split("SCORE:")[1].split("\n")[0].strip()
        score = float(score_line)
        reasoning = raw.split("REASONING:")[1].strip() if "REASONING:" in raw else ""
    except (IndexError, ValueError):
        print("  ⚠ Could not parse judge score. Defaulting to 0.")
        return 0.0, ""

    return score, reasoning

# ── Main Loop ─────────────────────────────────────────────────────────────────

def run_loop(iterations: int, verbose: bool):

    print("\n⚙  AUTOLOOP — Self-Improving Document Optimizer")
    print("   Inspired by Karpathy's autoresearch")
    print(f"   Model: {MODEL}")
    print(f"   Iterations: {iterations}")
    print(f"   Artifact: {ARTIFACT_PATH}")
    print_divider()

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("✗ ANTHROPIC_API_KEY environment variable not set.")
        print("  Run: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Check files exist
    if not Path(ARTIFACT_PATH).exists():
        print(f"✗ {ARTIFACT_PATH} not found. Create it first.")
        sys.exit(1)
    if not Path(GOALS_PATH).exists():
        print(f"✗ {GOALS_PATH} not found. Create it first.")
        sys.exit(1)

    # Initialize git
    repo = get_git_repo()
    log = load_log()

    # Get baseline score
    print("📊 Scoring baseline document...")
    artifact = read_file(ARTIFACT_PATH)
    goals    = read_file(GOALS_PATH)
    baseline_score, baseline_reasoning = evaluate_document(client, artifact, goals, verbose)
    print(f"   Baseline score: {baseline_score:.1f}/100")
    print(f"   {baseline_reasoning}")
    print_divider()

    current_score = baseline_score
    wins = 0
    losses = 0

    for i in range(1, iterations + 1):
        print(f"🔄 Iteration {i}/{iterations}")

        artifact = read_file(ARTIFACT_PATH)
        goals    = read_file(GOALS_PATH)
        history  = get_iteration_history(repo)

        # Get proposed mutation
        improved_doc, hypothesis, change_summary = get_mutation(
            client, artifact, goals, history, verbose
        )

        if hypothesis == "parse error":
            losses += 1
            continue

        print(f"   Hypothesis: {hypothesis}")

        # Apply mutation to file
        write_file(ARTIFACT_PATH, improved_doc)

        # Score the new version
        new_score, new_reasoning = evaluate_document(client, improved_doc, goals, verbose)

        print(f"   Score: {current_score:.1f} → {new_score:.1f}", end="  ")

        iteration_result = {
            "iteration": i,
            "hypothesis": hypothesis,
            "change_summary": change_summary,
            "score_before": current_score,
            "score_after": new_score,
            "reasoning": new_reasoning,
            "timestamp": datetime.now().isoformat()
        }

        if new_score > current_score:
            # Winner — commit it
            repo.index.add([ARTIFACT_PATH])
            commit_message = (
                f"Iteration {i}: {change_summary} | "
                f"score: {current_score:.1f} → {new_score:.1f}"
            )
            repo.index.commit(commit_message)
            print(f"✓ KEPT")
            if verbose:
                print(f"   {new_reasoning}")
            current_score = new_score
            wins += 1
            iteration_result["outcome"] = "kept"
        else:
            # Loser — revert file to HEAD
            repo.git.checkout(ARTIFACT_PATH)
            print(f"✗ REVERTED")
            losses += 1
            iteration_result["outcome"] = "reverted"

        log.append(iteration_result)
        save_log(log)
        print()

    # Final summary
    print_divider()
    print("✅ LOOP COMPLETE")
    print(f"   Baseline score:  {baseline_score:.1f}/100")
    print(f"   Final score:     {current_score:.1f}/100")
    print(f"   Improvement:     +{current_score - baseline_score:.1f} points")
    print(f"   Iterations:      {iterations}")
    print(f"   Wins / Losses:   {wins} / {losses}")
    print(f"\n   Git log (winning iterations):")
    print()

    # Print the winning commit history
    try:
        for commit in list(repo.iter_commits())[:wins + 1]:
            print(f"   {commit.hexsha[:7]}  {commit.message.strip()}")
    except Exception:
        pass

    print()
    print(f"   Full log saved to: {LOG_PATH}")
    print(f"   Optimized doc:     {ARTIFACT_PATH}")
    print_divider()


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Self-improving document loop")
    parser.add_argument("--iterations", type=int, default=10, help="Number of iterations to run (default: 10)")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    run_loop(iterations=args.iterations, verbose=args.verbose)
