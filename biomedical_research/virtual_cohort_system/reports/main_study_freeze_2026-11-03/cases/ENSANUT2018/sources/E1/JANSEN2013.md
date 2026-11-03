# JANSEN2013: E1-scoped admitted extraction

Jansen2013 DOI10.1111/joim.12010; PMID23121487; authored summary of original, independent source audit completed, previously admitted with restrictions

Population: Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.

Measurement: HbA1c IFCC-standardized turbidimetric inhibition immunoassay; FPG fresh fasting venous plasma, hexokinase/G6PD. Table1 spreads SD; coefficients HbA1c mmol/mol. Hours fasted unspecified.

Only the following evidence records are supplied in this condition. This is an authored scoped extract, not the full paper. Other source results are not admitted through this file.

## J_T1_age_mean_task

```json
{
  "evidence": {
    "id": "J_T1_age_mean_task",
    "source_id": "JANSEN2013",
    "locator": "Table1 Age (years) row and SD footnote",
    "variables": [
      "age"
    ],
    "kind": "mean",
    "estimate": 55.5,
    "unit": "year",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_age_mean_task",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_age_mean"
  }
}
```

## J_T1_age_sd_task

```json
{
  "evidence": {
    "id": "J_T1_age_sd_task",
    "source_id": "JANSEN2013",
    "locator": "Table1 Age (years) row and SD footnote",
    "variables": [
      "age"
    ],
    "kind": "sd",
    "estimate": 9.9,
    "unit": "year",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_age_sd_task",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_age_sd"
  }
}
```

## J_T1_bmi_mean_task

```json
{
  "evidence": {
    "id": "J_T1_bmi_mean_task",
    "source_id": "JANSEN2013",
    "locator": "Table1 BMI row and SD footnote",
    "variables": [
      "bmi"
    ],
    "kind": "mean",
    "estimate": 26.5,
    "unit": "kg/m^2",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_bmi_mean_task",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_bmi_mean"
  }
}
```

## J_T1_bmi_sd_task

```json
{
  "evidence": {
    "id": "J_T1_bmi_sd_task",
    "source_id": "JANSEN2013",
    "locator": "Table1 BMI row and SD footnote",
    "variables": [
      "bmi"
    ],
    "kind": "sd",
    "estimate": 4.1,
    "unit": "kg/m^2",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_bmi_sd_task",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_bmi_sd"
  }
}
```

## J_T1_glucose_mean_mmol_L

```json
{
  "evidence": {
    "id": "J_T1_glucose_mean_mmol_L",
    "source_id": "JANSEN2013",
    "locator": "Table1 Fasting plasma glucose row and SD footnote",
    "variables": [
      "glucose"
    ],
    "kind": "mean",
    "estimate": 5.1,
    "unit": "mmol/L",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_glucose_mean_mmol_L",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_glucose_mean"
  }
}
```

## J_T1_glucose_sd_mmol_L

```json
{
  "evidence": {
    "id": "J_T1_glucose_sd_mmol_L",
    "source_id": "JANSEN2013",
    "locator": "Table1 Fasting plasma glucose row and SD footnote",
    "variables": [
      "glucose"
    ],
    "kind": "sd",
    "estimate": 0.5,
    "unit": "mmol/L",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_glucose_sd_mmol_L",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_glucose_sd"
  }
}
```

## J_T1_hba1c_mean_pct

```json
{
  "evidence": {
    "id": "J_T1_hba1c_mean_pct",
    "source_id": "JANSEN2013",
    "locator": "Table1 HbA1c (%) row and SD footnote",
    "variables": [
      "hba1c"
    ],
    "kind": "mean",
    "estimate": 5.6,
    "unit": "%",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_hba1c_mean_pct",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_hba1c_mean"
  }
}
```

## J_T1_hba1c_sd_pct

```json
{
  "evidence": {
    "id": "J_T1_hba1c_sd_pct",
    "source_id": "JANSEN2013",
    "locator": "Table1 HbA1c (%) row and SD footnote",
    "variables": [
      "hba1c"
    ],
    "kind": "sd",
    "estimate": 0.3,
    "unit": "%",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_hba1c_sd_pct",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_hba1c_sd"
  }
}
```

## J_T1_hba1c_mean_ifcc

```json
{
  "evidence": {
    "id": "J_T1_hba1c_mean_ifcc",
    "source_id": "JANSEN2013",
    "locator": "Table1 HbA1c (mmol/mol) row and SD footnote",
    "variables": [
      "hba1c"
    ],
    "kind": "mean",
    "estimate": 38.0,
    "unit": "mmol/mol",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_hba1c_mean_ifcc",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_hba1c_mean"
  }
}
```

## J_T1_hba1c_sd_ifcc

```json
{
  "evidence": {
    "id": "J_T1_hba1c_sd_ifcc",
    "source_id": "JANSEN2013",
    "locator": "Table1 HbA1c (mmol/mol) row and SD footnote",
    "variables": [
      "hba1c"
    ],
    "kind": "sd",
    "estimate": 3.0,
    "unit": "mmol/mol",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value."
  },
  "normalization": {
    "item_id": "J_T1_hba1c_sd_ifcc",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "reported_sample_n": 2921,
    "spread_label": "SD",
    "same_quantity_group": "J_T1_hba1c_sd"
  }
}
```

## J_T1_male_proportion_reported

```json
{
  "evidence": {
    "id": "J_T1_male_proportion_reported",
    "source_id": "JANSEN2013",
    "locator": "Table1 Male (%) row",
    "variables": [
      "female"
    ],
    "kind": "proportion",
    "estimate": 0.403,
    "unit": "1",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "P(female=0), NOT P(female=1); reported 40.3% (1176 males). Task female coding is 1=female,0=male, distinct from unknown regression coding."
  },
  "normalization": {
    "item_id": "J_T1_male_proportion_reported",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "event": {
      "female": 0
    },
    "reported_count": 1176,
    "reported_percent": 40.3,
    "reported_sample_n": 2921
  }
}
```

## J_T1_female_proportion_derived

```json
{
  "evidence": {
    "id": "J_T1_female_proportion_derived",
    "source_id": "JANSEN2013",
    "locator": "Derived from Table1 reported male40.3%; fixed task binary coding",
    "variables": [
      "female"
    ],
    "kind": "proportion",
    "estimate": 0.597,
    "unit": "1",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "P(female=1)=1-0.403; complement of rounded reported percentage, not an exact-count fraction. Not source regression coding."
  },
  "normalization": {
    "item_id": "J_T1_female_proportion_derived",
    "status": "source_constraint_pending_root",
    "representation": "derived",
    "derived_from": [
      "J_T1_male_proportion_reported"
    ],
    "formula": "1-0.403",
    "event": {
      "female": 1
    },
    "same_quantity_group": "J_T1_sex_composition"
  }
}
```

## J_T1_glucose_mean_mg_dL_derived

```json
{
  "evidence": {
    "id": "J_T1_glucose_mean_mg_dL_derived",
    "source_id": "JANSEN2013",
    "locator": "Table1 FPG; fixed protocol glucose conversion",
    "variables": [
      "glucose"
    ],
    "kind": "mean",
    "estimate": 91.8,
    "unit": "mg/dL",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value. Original retained; conventional rounded factor18.0 is fixed, not fitted."
  },
  "normalization": {
    "item_id": "J_T1_glucose_mean_mg_dL_derived",
    "status": "source_constraint_pending_root",
    "representation": "derived",
    "derived_from": [
      "J_T1_glucose_mean_mmol_L"
    ],
    "formula": "5.1*18.0",
    "same_quantity_group": "J_T1_glucose_mean"
  }
}
```

## J_T1_glucose_sd_mg_dL_derived

```json
{
  "evidence": {
    "id": "J_T1_glucose_sd_mg_dL_derived",
    "source_id": "JANSEN2013",
    "locator": "Table1 FPG; fixed protocol glucose conversion",
    "variables": [
      "glucose"
    ],
    "kind": "sd",
    "estimate": 9.0,
    "unit": "mg/dL",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Source-context marginal only; does not identify joint dependence, support or residual distribution. Previously admitted with restrictions; source-specific, not a target value. Original retained; conventional rounded factor18.0 is fixed, not fitted."
  },
  "normalization": {
    "item_id": "J_T1_glucose_sd_mg_dL_derived",
    "status": "source_constraint_pending_root",
    "representation": "derived",
    "derived_from": [
      "J_T1_glucose_sd_mmol_L"
    ],
    "formula": "0.5*18.0",
    "same_quantity_group": "J_T1_glucose_sd"
  }
}
```

## J_T1_hba1c_mean_pct_from_ifcc

```json
{
  "evidence": {
    "id": "J_T1_hba1c_mean_pct_from_ifcc",
    "source_id": "JANSEN2013",
    "locator": "Table1 IFCC row; NGSP master equation",
    "variables": [
      "hba1c"
    ],
    "kind": "mean",
    "estimate": 5.62824,
    "unit": "%",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Derived unit representation only. Keep separately from published rounded percent row; do not count both as independent constraints or force exact agreement."
  },
  "normalization": {
    "item_id": "J_T1_hba1c_mean_pct_from_ifcc",
    "status": "alternative_unit_representation_not_independent",
    "representation": "derived",
    "derived_from": [
      "J_T1_hba1c_mean_ifcc"
    ],
    "formula": "38.0*0.09148+2.152",
    "conversion_source": "NGSP",
    "same_quantity_group": "J_T1_hba1c_mean"
  }
}
```

## J_T1_hba1c_sd_pct_from_ifcc

```json
{
  "evidence": {
    "id": "J_T1_hba1c_sd_pct_from_ifcc",
    "source_id": "JANSEN2013",
    "locator": "Table1 IFCC row; NGSP master equation",
    "variables": [
      "hba1c"
    ],
    "kind": "sd",
    "estimate": 0.27444,
    "unit": "%",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Derived unit representation only. Keep separately from published rounded percent row; do not count both as independent constraints or force exact agreement."
  },
  "normalization": {
    "item_id": "J_T1_hba1c_sd_pct_from_ifcc",
    "status": "alternative_unit_representation_not_independent",
    "representation": "derived",
    "derived_from": [
      "J_T1_hba1c_sd_ifcc"
    ],
    "formula": "3.0*0.09148+0",
    "conversion_source": "NGSP",
    "same_quantity_group": "J_T1_hba1c_sd"
  }
}
```

## J_T2_bmi_slope_original

```json
{
  "evidence": {
    "id": "J_T2_bmi_slope_original",
    "source_id": "JANSEN2013",
    "locator": "Table2 bmi row, header and separate-addition footnote; Statistical methods",
    "variables": [
      "hba1c",
      "bmi"
    ],
    "kind": "ols_coefficient",
    "estimate": 0.13,
    "unit": "mmol/mol per kg/m^2",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [
      "age",
      "female"
    ],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Separate HbA1c-on-bmi projection adjusted age/female (binary sex covariate); other Table2 predictors were not included together. Source gender numeric coding unknown, but adjustment for a binary complement spans the same intercept-adjusted covariate space. Printed CI [0.1,0.16], confidence level unspecified; uncertainty.kind=not_reported encodes absent level/SE, not absence of printed bounds. Table2 row-specific n unknown; do not substitute Table1 n or Table3 II."
  },
  "normalization": {
    "item_id": "J_T2_bmi_slope_original",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "outcome": "hba1c",
    "predictor": "bmi",
    "reported_ci": {
      "low": 0.1,
      "high": 0.16,
      "level": null
    },
    "row_n": null,
    "same_quantity_group": "J_T2_bmi_slope"
  }
}
```

## J_T2_bmi_slope_task_derived

```json
{
  "evidence": {
    "id": "J_T2_bmi_slope_task_derived",
    "source_id": "JANSEN2013",
    "locator": "Derived from J_T2_bmi_slope_original; NGSP conversion; fixed glucose factor18.0 if applicable",
    "variables": [
      "hba1c",
      "bmi"
    ],
    "kind": "ols_coefficient",
    "estimate": 0.0118924,
    "unit": "% per kg/m^2",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [
      "age",
      "female"
    ],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Separate HbA1c-on-bmi projection adjusted age/female (binary sex covariate); other Table2 predictors were not included together. Source gender numeric coding unknown, but adjustment for a binary complement spans the same intercept-adjusted covariate space. Printed CI [0.1,0.16], confidence level unspecified; uncertainty.kind=not_reported encodes absent level/SE, not absence of printed bounds. Table2 row-specific n unknown; do not substitute Table1 n or Table3 II. Derived task-unit CI [0.009148,0.0146368], level unknown; no affine offset on slopes."
  },
  "normalization": {
    "item_id": "J_T2_bmi_slope_task_derived",
    "status": "source_constraint_pending_root",
    "representation": "derived",
    "derived_from": [
      "J_T2_bmi_slope_original"
    ],
    "formula": "0.13*0.09148/1",
    "outcome": "hba1c",
    "predictor": "bmi",
    "reported_ci": {
      "low": 0.009148,
      "high": 0.0146368,
      "level": null
    },
    "row_n": null,
    "conversion_source": "NGSP",
    "same_quantity_group": "J_T2_bmi_slope"
  }
}
```

## J_T2_glucose_slope_original

```json
{
  "evidence": {
    "id": "J_T2_glucose_slope_original",
    "source_id": "JANSEN2013",
    "locator": "Table2 glucose row, header and separate-addition footnote; Statistical methods",
    "variables": [
      "hba1c",
      "glucose"
    ],
    "kind": "ols_coefficient",
    "estimate": 2.29,
    "unit": "mmol/mol per mmol/L",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [
      "age",
      "female"
    ],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Separate HbA1c-on-glucose projection adjusted age/female (binary sex covariate); other Table2 predictors were not included together. Source gender numeric coding unknown, but adjustment for a binary complement spans the same intercept-adjusted covariate space. Printed CI [2.07,2.51], confidence level unspecified; uncertainty.kind=not_reported encodes absent level/SE, not absence of printed bounds. Table2 row-specific n unknown; do not substitute Table1 n or Table3 II."
  },
  "normalization": {
    "item_id": "J_T2_glucose_slope_original",
    "status": "source_constraint_pending_root",
    "representation": "reported",
    "derived_from": [],
    "formula": null,
    "outcome": "hba1c",
    "predictor": "glucose",
    "reported_ci": {
      "low": 2.07,
      "high": 2.51,
      "level": null
    },
    "row_n": null,
    "same_quantity_group": "J_T2_glucose_slope"
  }
}
```

## J_T2_glucose_slope_task_derived

```json
{
  "evidence": {
    "id": "J_T2_glucose_slope_task_derived",
    "source_id": "JANSEN2013",
    "locator": "Derived from J_T2_glucose_slope_original; NGSP conversion; fixed glucose factor18.0 if applicable",
    "variables": [
      "hba1c",
      "glucose"
    ],
    "kind": "ols_coefficient",
    "estimate": 0.01163828888888889,
    "unit": "% per mg/dL",
    "uncertainty": {
      "kind": "not_reported"
    },
    "adjustment": [
      "age",
      "female"
    ],
    "selection": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
    "applicability": "Separate HbA1c-on-glucose projection adjusted age/female (binary sex covariate); other Table2 predictors were not included together. Source gender numeric coding unknown, but adjustment for a binary complement spans the same intercept-adjusted covariate space. Printed CI [2.07,2.51], confidence level unspecified; uncertainty.kind=not_reported encodes absent level/SE, not absence of printed bounds. Table2 row-specific n unknown; do not substitute Table1 n or Table3 II. Derived task-unit CI [0.0105202,0.012756377777777777], level unknown; no affine offset on slopes."
  },
  "normalization": {
    "item_id": "J_T2_glucose_slope_task_derived",
    "status": "source_constraint_pending_root",
    "representation": "derived",
    "derived_from": [
      "J_T2_glucose_slope_original"
    ],
    "formula": "2.29*0.09148/18.0",
    "outcome": "hba1c",
    "predictor": "glucose",
    "reported_ci": {
      "low": 0.0105202,
      "high": 0.012756377777777777,
      "level": null
    },
    "row_n": null,
    "conversion_source": "NGSP",
    "same_quantity_group": "J_T2_glucose_slope"
  }
}
```

