# Aggregate-only HRS native longitudinal evaluator. No generator execution.
# CLI: native_evaluate.R INPUT.csv OUTPUT.json [--toy SUBJECTS]
suppressPackageStartupMessages(library(lme4))
suppressPackageStartupMessages(library(jsonlite))

required_columns <- c("id", "subject_id", "visit_time", "baseline_age", "age", "age60",
                      "sex", "race", "educ", "cses", "hba1c", "mem_s")
fixed_terms <- c("(Intercept)", "age60", "hba1c_U65", "hba1c_O65", "raceBlack", "educHS",
                 "educLessThanHS", "sexMale", "cses", "age60:hba1c_U65", "age60:hba1c_O65",
                 "age60:raceBlack", "age60:educHS", "age60:educLessThanHS", "age60:sexMale", "age60:cses")

hash_file <- function(path) {
  output <- system2("sha256sum", shQuote(normalizePath(path, mustWork=TRUE)), stdout=TRUE)
  strsplit(output, " +")[[1]][1]
}

validate_input <- function(d, expected_subjects=11509L) {
  if (!identical(names(d), required_columns)) stop("CSV schema or column order differs from the frozen 12-column contract")
  if (anyNA(d) || any(!nzchar(d$id)) || any(!nzchar(d$subject_id))) stop("Missing or empty values")
  if (anyDuplicated(d$id)) stop("Visit IDs must be unique")
  numeric_columns <- c("visit_time", "baseline_age", "age", "age60", "cses", "hba1c", "mem_s")
  if (!all(vapply(d[numeric_columns], is.numeric, logical(1)))) stop("Required numerical columns are not numeric")
  if (!all(vapply(d[numeric_columns], function(x) all(is.finite(x)), logical(1)))) stop("Nonfinite numerical value")
  if (!all(d$sex %in% c("female", "male")) || !all(d$race %in% c("white", "black")) ||
      !all(d$educ %in% c("College", "HS", "LessThanHS"))) stop("Unknown factor category")
  if (any(d$hba1c<=0)) stop("HbA1c must be positive under the admitted schema")
  if (any(d$baseline_age<50 | d$baseline_age>100)) stop("Baseline age outside the native published support [50,100]")
  if (any(abs(d$age-d$baseline_age-d$visit_time)>1e-9) || any(abs(d$age60-(d$age-60)/10)>1e-9)) stop("Age scaling or visit time mismatch")
  groups <- split(seq_len(nrow(d)), d$subject_id)
  if (length(groups)!=expected_subjects || nrow(d)!=4L*expected_subjects) stop("Incorrect subject or visit count")
  stable <- c("baseline_age", "sex", "race", "educ", "cses", "hba1c")
  for (ix in groups) {
    if (!identical(sort(d$visit_time[ix]), c(0,2,4,6))) stop("Every subject requires visits 0,2,4,6 exactly once")
    if (!all(vapply(d[ix, stable, drop=FALSE], function(x) length(unique(x))==1L, logical(1)))) stop("Baseline-only attribute changed between visits")
  }
  list(subjects=length(groups), visits=nrow(d), visits_per_subject=4L,
       schedule=c(0,2,4,6), validation="passed")
}

numeric_summary <- function(x) {
  list(n=length(x), mean=if(length(x)) mean(x) else NULL,
       sd=if(length(x)>1L) sd(x) else NULL,
       sd_definition="sample SD; denominator n-1")
}

factor_summary <- function(x, levels) {
  list(denominator=length(x), categories=lapply(levels, function(v) {
    list(category=v, count=sum(x==v), proportion=mean(x==v), percentage=100*mean(x==v))
  }))
}

baseline_diagnostics <- function(d) {
  b <- d[d$visit_time==0, , drop=FALSE]
  list(denominator="one record per subject at visit_time=0",
       subjects=nrow(b), visits=nrow(d), age=numeric_summary(b$baseline_age),
       hba1c_overall=numeric_summary(b$hba1c),
       hba1c_below_6_5=numeric_summary(b$hba1c[b$hba1c<6.5]),
       hba1c_at_or_above_6_5=numeric_summary(b$hba1c[b$hba1c>=6.5]),
       female_male=factor_summary(b$sex,c("female","male")),
       white_black=factor_summary(b$race,c("white","black")),
       education=factor_summary(b$educ,c("College","HS","LessThanHS")),
       cses=numeric_summary(b$cses), baseline_memory=numeric_summary(b$mem_s),
       threshold_definition="Below: <6.5; above group: >=6.5; equality has zero mass under continuous generators but is explicitly assigned")
}

evaluate <- function(input, output, expected_subjects=11509L, toy=FALSE) {
  if (file.exists(output)) stop("Refusing to overwrite an existing evaluation output")
  before <- proc.time()[[3]]
  result <- list(schema_version="hrs_native_evaluation_v1", status="started", invented_test=toy,
                 input_sha256=hash_file(input), subject_contract=expected_subjects,
                 formula="mem_s ~ age60*(hba1c_U65+hba1c_O65+race+educ+sex+cses)+(1+age60|subject_id)",
                 REML=TRUE, optimizer_policy="native recipient RCTSim2: bobyqa, maxfun=2e8; exactly one fit; external 300-second cap; no retries",
                 R_version=R.version.string, lme4_version=as.character(packageVersion("lme4")),
                 factor_reference_levels=list(sex="Female",race="White",educ="College"),
                 age_scale="age60=(age-60)/10; age=baseline_age+visit_time",
                 knot_definition="hba1c_U65=min(hba1c-6.5,0); hba1c_O65=max(hba1c-6.5,0)",
                 fixed_effects=list(), warnings=character(), messages=character())
  tryCatch({
    d <- read.csv(input, colClasses=c("character", "character", "numeric", "numeric", "numeric", "numeric",
                                    "character", "character", "character", "numeric", "numeric", "numeric"),
                  check.names=FALSE, stringsAsFactors=FALSE)
    result$validation <- validate_input(d, expected_subjects)
    result$table2_diagnostics <- baseline_diagnostics(d)
    d$sex <- factor(d$sex, levels=c("female","male"), labels=c("Female","Male"))
    d$race <- factor(d$race, levels=c("white","black"), labels=c("White","Black"))
    d$educ <- factor(d$educ, levels=c("College","HS","LessThanHS"))
    for (v in c("sex","race","educ")) contrasts(d[[v]]) <- contr.treatment(levels(d[[v]]), base=1)
    d$subject_id <- factor(d$subject_id)
    d$hba1c_U65 <- pmin(d$hba1c-6.5,0)
    d$hba1c_O65 <- pmax(d$hba1c-6.5,0)
    fit <- withCallingHandlers(
      lmer(mem_s ~ age60*(hba1c_U65+hba1c_O65+race+educ+sex+cses)+(1+age60|subject_id),
           data=d, REML=TRUE, na.action=na.fail,
           control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=2e8))),
      warning=function(w){ result$warnings <<- c(result$warnings, conditionMessage(w)); invokeRestart("muffleWarning") },
      message=function(m){ result$messages <<- c(result$messages, conditionMessage(m)); invokeRestart("muffleMessage") })
    beta <- fixef(fit, add.dropped=TRUE)
    if (!identical(names(beta), fixed_terms) || anyNA(beta)) stop("Not all 16 native fixed effects are estimable")
    covariance <- as.matrix(vcov(fit)); se <- sqrt(diag(covariance))
    result$fixed_effects <- lapply(fixed_terms, function(v) list(term=v, estimate=unname(beta[v]),
       se=unname(se[v]), wald_lower=unname(beta[v]-qnorm(.975)*se[v]),
       wald_upper=unname(beta[v]+qnorm(.975)*se[v]),
       interval_meaning="model-conditional asymptotic Wald interval; synthetic rows are not new source patients"))
    result$focal_terms <- c("age60:hba1c_U65", "age60:hba1c_O65")
    rv <- as.matrix(VarCorr(fit)$subject_id)
    result$random_effect_covariance <- unname(rv)
    result$random_effect_covariance_terms <- c("(Intercept)","age60")
    result$random_effect_sd <- unname(sqrt(diag(rv)))
    result$random_effect_correlation <- unname(attr(VarCorr(fit)$subject_id,"correlation")[1,2])
    result$residual_variance <- sigma(fit)^2
    result$residual_sd <- sigma(fit)
    result$fixed_effect_covariance <- unname(covariance)
    result$fixed_effect_order <- fixed_terms
    result$logLik <- as.numeric(logLik(fit))
    result$REML_criterion <- REMLcrit(fit)
    result$singular <- isSingular(fit, tol=1e-4)
    result$singularity_tolerance <- 1e-4
    result$convergence <- list(optimizer=fit@optinfo$optimizer,
       optimizer_code=fit@optinfo$conv$opt, lme4_messages=fit@optinfo$conv$lme4$messages,
       optimizer_converged=all(fit@optinfo$conv$opt==0),
       lme4_convergence_messages_absent=is.null(fit@optinfo$conv$lme4$messages),
       evaluations=fit@optinfo$feval,
       derivative_gradient=fit@optinfo$derivs$gradient,
       optimizer_message=fit@optinfo$message)
    result$all_fixed_effects_finite <- all(is.finite(beta)) && all(is.finite(se))
    result$status <- "computed"
    result$interpretation <- "All estimates retained including warnings/singularity; computed does not assert optimizer convergence, biological truth, independent validation or equivalent clinical precision."
  }, error=function(e) {
    result$status <<- "failed"
    result$error <<- conditionMessage(e)
  })
  result$elapsed_seconds <- proc.time()[[3]]-before
  write_json(result, output, pretty=TRUE, auto_unbox=TRUE, digits=17, null="null", na="null")
  invisible(result)
}

if (sys.nframe()==0L) {
  args <- commandArgs(trailingOnly=TRUE)
  if (!(length(args)==2L || (length(args)==4L && args[3]=="--toy"))) stop("Usage: native_evaluate.R INPUT.csv OUTPUT.json [--toy SUBJECTS]")
  n <- if (length(args)==4L) as.integer(args[4]) else 11509L
  result <- evaluate(args[1], args[2], n, length(args)==4L)
  cat(result$status,"\n")
  if (result$status!="computed") quit(status=2L)
}
