# Report verification

The standalone HTML contains all 75 planned coefficient records and all 25 table count/exclusion records. 390 static checks passed against ANALYSIS.json, including displayed r and r-squared rounding, constructor means/ranges, local links, embedded figures and the near-zero sign-crossing statement.

Both plot PNGs were visually inspected: no clipped labels or overlaps; shared axes/colors; all six initial constructors retained. The matrix uses ~0.00 for rounded near-zero entries instead of a misleading negative zero. This is a display convention, not an analysis threshold.

No individual records were opened by the renderer or this verification. Full HTML browser layout/interactivity was not verified. This does not replace the independent statistical recomputation.
