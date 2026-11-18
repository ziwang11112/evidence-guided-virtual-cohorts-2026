# C01/C02解析诊断：独立静态公式复核

2026-11-05。复核对象：本目录 `analytic_c01_c02.py` 与 `ANALYTIC_C01_C02.json`，以及实际冻结的 C01/C02 `generator.py` 和 `model_spec.json`。本次只读与数学推导；没有运行审计脚本、生成器、数值重算、患者分析或测试，也没有修改任何既有文件。

**结论：公式与这两份冻结生成law一致，静态复核通过。** JSON中的数值是根任务本次解析诊断输出，不标作本复核者独立重跑的结果。以下结论仅适用于当前参数与生成器，不能未经修订就用于未来改变结构的候选。

## C01：总体矩、回归投影与混合Spearman

1. 年龄35–74离散均匀，潜在组别与年龄/性别独立；已冻结的三个性别offset均为零。因此按每个年龄构造背景权重`(1-pi)/40`和已知病情替代组权重`pi/40`，与生成器一致。年龄给定时连续变量算术协方差为`corr * outer(sd, sd)`；多元lognormal采样器正是用`log(1+corr*CV_i*CV_j)`获得这一协方差。累加组内二阶矩与组间均值乘积，再减总体均值乘积，是正确的混合总体协方差。
2. OLS系数用`Cov(X,X)^(-1) Cov(X,Y)`计算，等价于带截距总体线性投影。性别独立且对连续变量没有offset，省略其零协方差项不会改变这些总体系数；这不意味着一般情况下都可以省略性别。
3. Spearman部分保留全部40个年龄背景成分，将不随年龄变化的替代组折叠为一个成分。这个折叠对G/H二维边际合法。每个成分从算术均值/SD和raw Pearson构造lognormal参数，符合冻结采样器的二维边际。
4. 对成分j的每个二维正态积分点，代码计算的是**总体混合边际CDF**：`F_G(g)=Σ_k w_k Φ((log(g)-mu_Gk)/sigma_Gk)`，HbA1c同理；随后求`Σ_j w_j E_j[F_G(G)F_H(H)]`，最终使用连续边际的`rho_S=12E[F_G(G)F_H(H)]-3`。这不是把各成分Spearman简单加权，亦没有误用单Gaussian copula的相关公式。
5. `hermgauss`的节点乘sqrt(2)、权重除sqrt(pi)转换到标准正态正确；`Z_H=rZ_G+sqrt(1-r²)Z_2`及二维乘积权重展平顺序匹配。

记录中16、24、40、64阶结果为约0.6368807702、0.6368807325、0.6368807325、0.6368807325，支持这里所需精度的数值稳定。**阶数收敛不是经过证明的严格误差上界**；该量仍应标为确定性数值积分近似。它接近冻结生成表均值0.6351、远于目标样本参照0.3615，支持“秩关系差异是该law的结构性结果，增加相同law的行数不会修复”这一诊断，但不识别到底哪项来源/混合假设是唯一原因。

依据：[C01混合矩](D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/quality_attribution_2026-11-04/analytic_c01_c02.py:29)、[混合CDF积分](D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/quality_attribution_2026-11-04/analytic_c01_c02.py:47)、[冻结C01生成器](D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcRepC01/candidates/initial/generator.py:6)。

## C02：离散年龄倾斜正态协方差

记年龄由标准正态Z_A的40个等概率区间决定，区间端点为`c_i=Phi^-1(i/40)`；移位血糖为`G=c+m*exp(sigma_G Z_G-sigma_G²/2)`，其中`m=mean_G-c`。令`t=sigma_G Corr(Z_A,Z_G)`。条件期望的指数倾斜给出

`E[(G-c) 1(c_i<Z_A<=c_{i+1})] = m [Phi(c_{i+1}-t)-Phi(c_i-t)]`。

所以代码中`Cov(A,G)=m [Σ_i age_i*tilted_prob_i-E(A)]`正确，保留了实际离散年龄映射；没有把年龄直接近似成连续正态。端点±∞通过CDF处理自然正确。

BMI与移位血糖的协方差`mean_B*m*expm1(sigma_B*sigma_G*r_BG)`符合二元lognormal恒等式。冻结spec中`r_AB=0`，故离散A与B独立、Cov(A,B)=0；性别独立。脚本设置的预测变量协方差矩阵因此正确。

HbA1c是线性条件均值加独立Uniform(-h,h)残差，残差方差`h²/3`、`Cov(X,H)=Cov(X,X)beta`、`Var(H)=beta'Cov(X,X)beta+h²/3`均与生成器一致。冻结年龄均值54.5、方差133.25与35–74离散均匀相符，中心化保证总体HbA1c均值为spec均值。

`Corr(logBMI,H)`的简式合法依赖当前的`r_AB=0`、direct-BMI系数为0、性别独立；这三点已从冻结spec核对。**若以后允许非零direct-BMI或age–BMI依赖，该简式及缺失的Cov(A,B)项必须更新，不能把当前脚本当通用求解器。** 当前计算得到age相关0.208、logBMI相关0.21、方差差约1.1e-16，是同一law兑现其已指定约束的依据；不构成这些约束能正确迁移的证据。

依据：[C02公式](D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/quality_attribution_2026-11-04/analytic_c01_c02.py:80)、[冻结C02生成器](D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcRepC02/candidates/initial/generator.py:9)。

## 解释与复用边界

- `seed_mean_minus_law`与`law_minus_reference`是描述性恒等分拆；真实样本参照有抽样与选择不确定性，不能称为“采样错误与机制错误的已识别比例”，也不能由数值接近直接认定统计等价。
- 当前没有复算Monte Carlo标准误或假设检验；不能用三个seed的差异给结构有效性置信区间。
- 审计针对理想实数概率law；未测试极端浮点溢出概率或失败条件，不替代此前数值/有限矩审查。
- C01脚本已断言性别offset为零；C02有若干依赖冻结spec的简化。若未来作为可复用工具，宜显式断言其适用条件并记录生成器哈希。此处已经逐项静态核对，不需要为本次诊断重跑旧测试。

本次复核与之前方法流程审查相一致：**C02已实现相当完整的联合矩协调，C01主要秩结构差异可由冻结law本身解释。不能把二者的目标不匹配笼统归因为缺少一个优化器。**
