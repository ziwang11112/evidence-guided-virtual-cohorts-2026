suppressPackageStartupMessages(library(lme4))
suppressPackageStartupMessages(library(jsonlite))
args <- commandArgs(trailingOnly=TRUE)
runtime <- list(R=R.version.string, platform=R.version$platform,
               packages=as.list(setNames(vapply(c("lme4", "Matrix", "minqa", "nloptr", "Rcpp", "RcppEigen", "jsonlite"), function(x) as.character(packageVersion(x)), character(1)),
                                        c("lme4", "Matrix", "minqa", "nloptr", "Rcpp", "RcppEigen", "jsonlite"))),
               libraries=.libPaths(), session_info=capture.output(sessionInfo()),
               native_historical_R="4.0.1", native_historical_lme4="1.1-23",
               interpretation="Compatible current binary runtime, not bitwise historical runtime reproduction.")
if (length(args)) write_json(runtime, args[1], pretty=TRUE, auto_unbox=TRUE)
cat(toJSON(runtime, pretty=TRUE, auto_unbox=TRUE), "\n")
