# Figure 3. Iron status from published threshold counts to three target analyses

`fig3-iron-utility.pdf` is the vector figure for two-column typesetting. `fig3-iron-utility.png` is the 300-dpi version. The physical page size is 7.00 × 3.80 inches. Use the PDF at full manuscript text width.

The top row is a post hoc analytical reading of the two sealed programs. Zhu et al. reported four counts in the order both low, low hemoglobin only, low ferritin only and neither low: 173, 85, 331 and 1,082. The renderer normalizes these into a probability table. Under law A it multiplies the two low-ferritin masses by 2/3 and renormalizes. It then forms a mixture of 80% of that weighted joint law and 20% of the product of its two margins, corresponding to independently redrawing hemoglobin from the weighted marginal for 20% of individuals. Law B carries the threshold probabilities from source to target directly. “Low” denotes hemoglobin below 12 g/dL and raw ferritin below 15 µg/L.

| Calculation | Odds ratio | Both low (%) |
|---|---:|---:|
| Source and law B | 6.653137 | 10.353082 |
| A after reweighting | 6.653137 | 7.673542 |
| A after independent hemoglobin redraw | 4.645566 | 6.734776 |

The lower row reuses the three registered estimands of Figure 3 in v0.18. Circles and triangles are the three fixed 5,000-row tables from each law. Their vertical separation identifies distinct draws from the same law. The dark diamond and bar show the weighted estimate and design-based 95% survey interval in the 979 measured women with both biomarkers. The protocol specified the log odds ratio for the primary comparison, shown on the original OR scale. Joint burden and continuous ranks were secondary analyses. A law-level OR computed from cell probabilities and the OR computed on any one finite sample are different quantities.

The accompanying `fig3-iron-inputs.json` gives all 18 generated point estimates, all three measured point estimates and intervals, source counts, model rules, and the path, size and SHA-256 of each input, including the preceding figure's PNG and PDF. Each identifier refers to the original scientific commit. The self-contained figure directory can rebuild the image without cohort data or network access. From this folder, run:

```console
python render_iron.py
```

To additionally verify the pinned Git blobs, all displayed estimates, source cells and A's weights against a clone of the public repository, run:

```console
python render_iron.py --verify-repo /path/to/evidence-guided-virtual-cohorts-2026
```

[Original scientific snapshot](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/tree/0dd16840fd7ab175d3f5aa61f125cefbed62908b/biomedical_research/virtual_cohort_system/reports/iron_breadth_2026-11-05) · [Zhu et al., original source paper](https://doi.org/10.1024/0300-9831/a000014)

