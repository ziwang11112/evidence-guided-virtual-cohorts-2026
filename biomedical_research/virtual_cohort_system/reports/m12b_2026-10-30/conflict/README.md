# Invented M12-B calibration fixture

No patients, target outcomes or clinical interpretation. Covariates are id,x,z; y is generated.
Source z counts are 8 and 4. Within each z, x is centered. Residual (-1,1,-1,1) repeats three times.
Literal reference y=(0,2,4,6,0,2,4,6,2,4,6,8). Mean=11/3; adjusted x coefficient=2; sample SD=sqrt(212/33).
Sum(x^2)=12, sum((z-1/3)^2)=8/3, sum(residual^2)=12; cross products vanish.
Fixed model y=a+b*x+2*z+c*residual uses a seed-dependent residual sign. This preserves all three checks.
Initial (a,b,c)=(1,1,0.5); reference (3,2,1); steps all 0.5; maximum 25 trials includes the initial trial.
Fit seeds 101,102; independent replay seeds 201,202. All source checks enter the fixed scaled objective.
Negative controls use only three trials. The incompatible variant adds mean 17/3; its objective is bounded below by 0.5 analytically.
The noncomputable variant makes adjusted OLS rank deficient.
Tests use a labeled mock backend. The CLI requires a real runtime configuration and routes through WSL/bubblewrap.
