# Final figure and numerical presentation review

Version1's legend overlapped the final analytical row. Version2 moved it outside the plotting area, and its PNG was visually inspected with all eight labels, estimates, interval/range bars, legend and footer visible. Version3 retains that layout and adds evidence/assumption roles to the CSV/Markdown report. Its numerical estimates come from the same frozen evaluation.

Grey bars are real survey confidence intervals. Teal bars are min–max point estimates across20 conditional simulation draws, not confidence intervals. The row-specific contrasts retain their own labels and units. The PDF is saved from the same Matplotlib figure.

The generated_median_ratio CSV field is exp(median(log-effect)), rather than the arithmetic median of the20 exponentiated draws. This reporting clarification changes no coefficient or scientific conclusion.
