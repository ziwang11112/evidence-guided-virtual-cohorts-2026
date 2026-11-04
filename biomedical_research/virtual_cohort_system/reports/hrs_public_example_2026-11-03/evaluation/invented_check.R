# Artificial numerical fixture only. No source/patient parameters or observations.
args <- commandArgs(trailingOnly=TRUE)
if(length(args)!=1L) stop("Pass evaluation directory")
root <- normalizePath(args[1], mustWork=TRUE)
source(file.path(root,"native_evaluate.R"))
out <- file.path(root,"invented_native_bobyqa_local")
dir.create(out,showWarnings=FALSE)
set.seed(902211)
n <- 120L
ids <- rep(sprintf("toy%03d",seq_len(n)),each=4)
t <- rep(c(0,2,4,6),n)
base_age <- rep(runif(n,52,78),each=4)
d <- data.frame(id=paste0(ids,"v",t),subject_id=ids,visit_time=t,
                baseline_age=base_age,age=base_age+t,age60=(base_age+t-60)/10,
                sex=rep(sample(c("female","male"),n,TRUE),each=4),
                race=rep(sample(c("white","black"),n,TRUE),each=4),
                educ=rep(sample(c("College","HS","LessThanHS"),n,TRUE),each=4),
                cses=rep(rnorm(n),each=4),hba1c=rep(runif(n,4.5,8.5),each=4),mem_s=0)
b0 <- rnorm(n,0,.3); b1 <- .05*b0+rnorm(n,0,.12)
d$mem_s <- .2-.18*d$age60+.03*pmin(d$hba1c-6.5,0)-.02*pmax(d$hba1c-6.5,0)+
 .05*(d$race=="black")-.07*(d$educ=="HS")-.12*(d$educ=="LessThanHS")+
 .04*(d$sex=="male")+.08*d$cses+.015*d$age60*d$cses+
 rep(b0,each=4)+rep(b1,each=4)*d$age60+rnorm(4*n,0,.15)
checks <- list()
checks$valid_schema <- is.list(validate_input(d,n))
expect_failure <- function(x){inherits(tryCatch(validate_input(x,n),error=function(e)e),"error")}
z<-d;z$id[2]<-z$id[1]; checks$duplicate_visit_id_rejected<-expect_failure(z)
z<-d;z$visit_time[2]<-3;checks$invalid_age_time_rejected<-expect_failure(z)
z<-d;z$hba1c[2]<-z$hba1c[2]+.1;checks$changing_baseline_attribute_rejected<-expect_failure(z)
z<-d;z$sex[1]<-"Female";checks$noncanonical_category_rejected<-expect_failure(z)
z<-d;z$mem_s[1]<-NA_real_;checks$missing_observation_rejected<-expect_failure(z)
csv<-file.path(out,"toy.csv")
write.csv(d,csv,row.names=FALSE)
fit_result<-evaluate(csv,file.path(out,"NATIVE.json"),n,TRUE)
checks$native_fit_completed<-identical(fit_result$status,"computed")
checks$all_16_terms<-length(fit_result$fixed_effects)==16L
checks$runtime_REML<-isTRUE(fit_result$REML)
checks$three_factor_reference_levels<-identical(vapply(fit_result$fixed_effects,function(x)x$term,character(1)),fixed_terms)
summary<-list(status=if(all(unlist(checks)))"pass" else "fail",invented_only=TRUE,
              seed=902211,subjects=n,rows=4*n,checks=checks,
              native_status=fit_result$status,native_warnings=fit_result$warnings,
              native_singular=fit_result$singular,native_elapsed_seconds=fit_result$elapsed_seconds,
              native_input_sha256=fit_result$input_sha256,
              interpretation="Implementation fixture; not HRS generation, biological accuracy or scientific validation.")
write_json(summary,file.path(root,"INVENTED_NATIVE_BOBYQA_CHECK.json"),pretty=TRUE,auto_unbox=TRUE,digits=17)
cat(toJSON(summary,pretty=TRUE,auto_unbox=TRUE),"\n")
if(!all(unlist(checks)))quit(status=2L)
