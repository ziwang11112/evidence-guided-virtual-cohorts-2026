# Clarification from the closed-program audit

Recorded before the new clinical comparison was opened. This clarification changes no generator, protocol, seed, estimator, reference or frozen file.

Independent code review identified that `PNS_BASE_R3` samples a shared BMI-slope pair and residual-correlation parameter once per generated cohort, then samples participants conditional on those draws. Thus seed-to-seed variability includes Agent-encoded parameter/scenario variation as well as individual sampling. Other selected programs are being checked for the same distinction under the uniform audit.

The frozen plan's conditional-on-a-selected-law interpretation applies to the whole stochastic program, not necessarily to a fixed numerical parameter vector. We will describe final points/ranges as the three prescribed seeds under the selected program, including any global scenario draws. They are neither independent constructors nor calibrated intervals for source validity or population transport. An Agent-declared uncertainty distribution is an assumption unless justified and separately evaluated. Three draws are also insufficient to characterize its tails or calibrate coverage.

No additional seeds or favorable replacement draws are added. Constructor means and all individual seed outputs remain in the complete report. The figure captions are clarified accordingly; the original frozen interpretation plan remains unchanged.
