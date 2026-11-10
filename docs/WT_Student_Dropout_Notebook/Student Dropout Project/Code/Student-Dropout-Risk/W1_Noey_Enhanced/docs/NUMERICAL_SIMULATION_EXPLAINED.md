# W1 numerical example: feature improvements and risk simulation

**Scientific status:** Synthetic illustration, not a learned TabICL model or result from a student record. The genuine TabICL results require running the separate `student_improvement_simulation.py --run` on the pinned project machine.

## Student profile (hypothetical)

- First-semester grade = 9/20; approved = 2 of 6 enrolled units, hence pass rate = 2/6 = 0.3333.
- Tuition overdue = 1; debtor = 1.
- Suggested support: future tutoring and assessment completion; verified payment plan / appropriate financial aid. Grade and approved-unit changes in the current first-semester input are **retrospective what-ifs**, NOT real recourse after those records are fixed.

## Invented illustrative probability formula

\[
z=-2+1.4(1-g/20)+1.7(1-a/e)+1.0t+0.6d+0.7(1-g/20)t,\quad p=\frac{1}{1+e^{-z}}.
\]

Here g = grade (0–20), a = approved curricular units, e = enrolled curricular units, t = tuition-overdue indicator (1 overdue, 0 resolved), d = debtor indicator (1 yes, 0 resolved). The last product is an explicit grade × tuition-status interaction. **These coefficients were invented for education; no TabICL parameter estimates are implied.**

Baseline:
\[
z_0=-2+1.4(0.55)+1.7(4/6)+1+0.6+0.7(0.55)=1.88833,\quad p_0=0.86857=86.86\%.
\]

With grade raised to 12, approved units raised to 4, overdue status resolved, debt status resolved:
\[
z_1=-2+1.4(0.40)+1.7(2/6)=-0.87333,\quad p_1=0.29456=29.46\%.
\]

Thus the illustrative model probability decreases by \(100(0.29456-0.86857)=-57.40\) **percentage points**. This is neither a real model evaluation nor a causal treatment effect.

| Illustrative input scenario | Estimated probability | Change vs baseline (pp) |
|---|---:|---:|
| Original | 86.86% | 0.00 |
| Grade 9→12 | 82.83% | -4.03 |
| Approved 2→4 of 6 | 78.95% | -7.91 |
| Tuition payment status resolved | 62.32% | -24.53 |
| Debtor status resolved | 78.39% | -8.47 |
| Grade + approved units | 73.24% | -13.62 |
| Tuition + debtor resolved | 47.59% | -39.27 |
| Grade + tuition resolved | 57.28% | -29.58 |
| All four changed | 29.46% | -57.40 |

### Interaction as a numerical contrast

For grade and tuition status, with approved units and debtor status unchanged:
\[
I_{g,t}=p(g=12,t=0)-p(g=12,t=1)-p(g=9,t=0)+p(g=9,t=1)\\
=0.57281-0.82826-0.62324+0.86857=-0.01012.
\]

This is a **-1.01-percentage-point nonadditive contrast** on the probability scale in the toy function. It is not SHAP interaction, not proof of real feature interaction in TabICL, and not evidence of support effectiveness.

### Actual TabICL simulation (after local execution)

For each altered validation profile, the real script computes:
\[
\widehat p_{\mathrm{new}}=\operatorname{TabICL}(x_{\mathrm{new}}),\quad
\Delta\widehat p=\widehat p_{\mathrm{new}}-\widehat p_{\mathrm{original}}.
\]

It also substitutes the one student's probability into the *unchanged validation cohort* and recomputes their place in the top-20%-capacity ranking. Unlike a fixed 0.5 cutoff, a probability reduction may or may not remove the flag. Interpreting historical first-semester edits as prospective treatment outcomes would be invalid.
