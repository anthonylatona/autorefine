# Optimization Goals

## What This Document Is
A product specification for a B2B SaaS product. It will be read by:
- A developer deciding whether to build it
- An investor evaluating the opportunity
- A co-founder deciding whether to join

## What We Are Optimizing For
Score the document on these four dimensions (25 points each, 100 total):

1. **Internal Consistency** — Do all sections agree with each other? Does the pricing match the target customer? Does the architecture support the features? Are there contradictions?

2. **Completeness** — Are there obvious gaps? Things mentioned but not defined? Sections that raise questions they don't answer? Open questions that should be answered by now?

3. **Specificity** — Are claims concrete and defensible, or vague and generic? "Start low to raise prices later" is not a strategy. "Scores recalculated nightly" may be too slow for the use case. Find the hand-waving.

4. **Strategic Soundness** — Does the go-to-market make sense for this product? Is the competitive positioning realistic? Are the risks properly assessed with mitigations?

## Constraints for the Agent
- Make exactly ONE improvement per iteration
- Do not rewrite entire sections
- Do not change the product idea itself
- State your hypothesis before making the change
- The change must be specific and traceable — someone reading the git diff should immediately understand what changed and why
- Prefer fixing real problems over polishing already-good sections
