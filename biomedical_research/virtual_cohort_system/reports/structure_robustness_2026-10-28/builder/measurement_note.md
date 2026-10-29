# Target measurement metadata

The target is reference-method fasting serum triglycerides in mg/dL, measured in the NHANES August 2021-August 2023 morning-examination subsample. Qualifying fasting is at least 8 and less than 24 hours. The required variable is LBXTLG in TRIGLY_L, not the standard biochemistry-profile triglyceride variable.

CDC documents a change to a non-glycerol-blanked method and a new instrument for this collection period. The official measurement comparison equations are:

- Forward: new-method TG (mg/dL) = 12.45 + 1.022 × old-method TG (mg/dL).
- Backward: old-method TG (mg/dL) = -12.19 + 0.9785 × new-method TG (mg/dL).

CDC reports coefficient intervals for the method comparison, but these equations are not population age/BMI/sex relationships. They do not establish assay interchangeability or justify modifying a target relationship to match a desired sign. Native LBXTLG units are the generation target; source-to-target assay transfer must be recorded as a modeling decision. The custodian also prespecifies a separate backward-calibration sensitivity.

Source: [CDC TRIGLY_L analytic notes](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/TRIGLY_L.htm). This excerpt is a measurement-only allowance. Builders must not follow the page into outcome data or use NHANES-derived population association studies.
