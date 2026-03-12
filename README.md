# autoloop

A self-improving document optimizer inspired by Karpathy's autoresearch.
No GPU required. Runs entirely via the Anthropic API.

---

## How It Works

1. You give it a document (`artifact.md`) and a goals file (`goals.md`)
2. An AI agent reads the document and proposes one targeted improvement
3. A separate AI judge scores the document before and after the change
4. If the score went up → the change is committed to git
5. If the score went down → the change is thrown away, document reverts
6. Repeat N times while you do something else

The git log at the end is a record of every decision the machine made,
in order, with the reasoning. That's the interesting output.

---

## Setup (WSL / Ubuntu)

### Step 1 — Copy the project to your WSL home directory

```bash
cp -r /mnt/c/xampp/experiment/autoloop ~/autoloop
cd ~/autoloop
```

### Step 2 — Install dependencies

```bash
pip install anthropic gitpython --break-system-packages
```

### Step 3 — Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY=your_key_here
```

To make this permanent, add it to your ~/.bashrc:
```bash
echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.bashrc
source ~/.bashrc
```

### Step 4 — Run the loop

```bash
cd ~/autoloop
python3 autoloop.py --iterations 10
```

For more detail on what's happening:
```bash
python3 autoloop.py --iterations 10 --verbose
```

---

## Output

- `artifact.md` — the optimized document after all iterations
- `loop_log.json` — full record of every iteration, score, hypothesis, and outcome
- Git log — run `git log --oneline` to see every winning commit

---

## Customizing

To use your own document:
1. Replace `artifact.md` with your document (must be Markdown)
2. Edit `goals.md` to describe what you're optimizing for
3. Delete the `.git` folder if one exists, so the loop starts fresh
4. Run the loop

---

## Cost Estimate

Each iteration makes 2 API calls (one agent, one judge).
At roughly 2000-3000 tokens per call with claude-sonnet:
- ~$0.01-0.02 per iteration
- 20 iterations ≈ $0.20-0.40
- 50 iterations ≈ $0.50-1.00
