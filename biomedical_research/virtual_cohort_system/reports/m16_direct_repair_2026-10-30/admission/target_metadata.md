# Locked target metadata

NHANES 2017-2018 is admitted for this new-cycle urate task. A metadata-only local audit found no prior urate evaluation for that cycle; other outcomes from the cycle have been used. This does not establish model-unseen or participant-unseen status.

Serum urate is LBXSUA in mg/dL in BIOPRO_J. The assay uses Roche Cobas 6000 (c501) and a uricase/peroxidase two-point endpoint method. The official component includes examined participants aged at least 12 years. The target restricts to the precommitted adult 20-56 population. No assay cross-cycle calibration is applied to target values.

DEMO_J provides screening age RIDAGEYR, sex RIAGENDR (1 male, 2 female), race RIDRETH3 (3 non-Hispanic White, 4 non-Hispanic Black), examination status RIDSTATR (2 interviewed and examined), WTMEC2YR, SDMVSTRA and SDMVPSU. WTMEC2YR is the correct two-year MEC examination weight; it is retained under its actual name and never relabeled WTPH2YR. DIQ_J DIQ010=2 means no reported professional diabetes diagnosis; it is not laboratory-defined nondiabetes. BMX_J BMXBMI is measured kg/m^2.

Eligibility additionally requires finite positive BMI and WTMEC2YR, valid design identifiers, and available LBXSUA. Urate magnitude is not an eligibility condition. No pregnancy, fasting, medication, or extra BMI restriction is imposed.

Select 50 participants per Black/White × female/male group by the ascending SHA256 rank specified in selection_frozen.json, total 200. The benchmark is finite and balanced; raw survey weights cannot alone reverse quota selection. Stop on insufficient groups or acquisition/integrity issues without outcome inspection.

Only sample_id, race, sex, age, bmi enter visible/observed.csv. Raw files, actual urate, SEQN, weight and survey design stay private. Only Bogalusa/Ferrara source papers may provide numerical generation evidence; NHANES paper numerical evidence is prohibited.

Official sources:
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BIOPRO_J.htm
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BMX_J.htm
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DIQ_J.htm

Outcome evaluation and release remain locked until all candidates are frozen and root explicitly authorizes evaluation.
