# Final report (LaTeX)

CVPR-style two-column report for the student-dropout project. Body sections are in `sec/`
(1 abstract to 8 conclusion; 9 appendix). The body must stay within 10 pages, excluding references
and the appendix. `main.tex` begins with the normal title and five-author block (no cover page).

Compile from this directory:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Use `../docs/report_notes/REPORT_PREPARATION_BRIEF.md` and `../tables/report_ready/project_numbers.json` when
writing. Do not rerun the final test or introduce claims not supported by the saved aggregate files.
