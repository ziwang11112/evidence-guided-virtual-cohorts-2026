**建议继续，但把论文主张收紧到一个可以被推翻的问题：在没有目标个体记录时，Agent 能否把外部研究的汇总证据转成一份冻结的虚拟队列，并在揭盲前判断，这份队列能支持哪些分析、哪些分析仍取决于未经验证的假设？**

现有项目已经得到一个有科学价值的结果。两次真实参照研究中，完全生成的队列都保留了若干预设关联的方向，但同一张表对不同分析的误差相差很大。ENSANUT 是最清楚的例子。次要血糖效应较接近实测参照，而加入血糖调整后的 BMI 效应在全部六张表中低估约 50%–71%。这比“系统成功生成了患者数据”更值得写。当前最缺的是一次前瞻检验，看能否在看到目标结果**之前**区分这两类用途。现阶段我支持继续做这一个实验，不支持以通用生物医学生成算法或迭代改进方法的名义投稿。

## A．实际读取、运行与核查范围

| 范围 | 本次实际完成 |
|---|---|
| 固定版本 | 读取 `COMMON_REVIEW_PROMPT.md` 和两份附件。通过公开 GitHub 固定提交取得原始文件，将 12 份文档和 11 份实现、规格及接口文件与附件逐一比较，**23/23 个 SHA-256 一致**。历史文档中的“private”已不能描述当前公开状态。 [固定提交](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/tree/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562) |
| 文档和代码 | 读了手稿、当前 checklist、core v0 规格和结果、M17-B、ENSANUT、C3–C5、准入与近邻报告。检查了六个 harness 模块、F1 控制器、Gamma 程序及规格，并沿链接核对了 M17-B 的预设协议、终点暴露分类与审计裁定、F1 收尾审计、ENSANUT 汇总表、C3/C5 审计及 CHNS 接入记录。另查了附件以外的 `source_checks.py` 等相关实现。 |
| 实际运行 | 在本地运行固定提交的 `tests/test_source_checks.py`，**11 项通过**。另调用真实的元数据校验函数测试回归方向、系数项和筛选条件。用独立算术复核了 Gamma 理论矩、C4 的一个误差下界，以及 ENSANUT 公开的 31 个终点和 40 项来源检查中的残差与范围。 |
| 核查边界 | 没有访问参与者记录或生成的个体行，没有重跑生成器、完整测试套件、Agent 会话或 WSL 隔离环境，也没有从原始记录重估临床模型。下文的 1,482 项吻合等数字来自我读到的项目审计。近邻工作按原论文和可得官方实现核查，未复跑其性能结果。未查阅其他模型的评审意见。 |

## B．主张与证据

| 记录 | 结果与我认为它能支持的主张 |
|---|---|
| **Core v0 / F1** | 一个 Agent 根据虚构来源中三个分层的均值和个体 SD 选择 Gamma 模型。形状 4、尺度 0.5、0.75、1，确实给出均值 2、3、4 和 SD 1、1.5、2。六项反馈绑定到真实执行，Agent 选择保留。两次同种子执行得到**一张**独特的 768 行表。来源矩、执行和保留决定之间的链条成立。尾部形状、零值概率、跨人群迁移和数值修订效果均未由此检验。 [F1 收尾审计](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/core_v0_2026-10-31/review/postrun/F1_INDEPENDENT_CLOSEOUT.md) |
| **M17-B / NHANES** | 两次独立构建，各三个种子，共六张 320 行表，对照一个按年龄、性别配额选取的实测样本。调整后的 BMI、年龄及女性对比方向均保留。每增加 5 kg/m² BMI，尿酸参照效应为 **0.2722 mg/dL**，B1 为 **0.3083–0.4684**，B2 为 **0.2561–0.3266**。六张表的 BMI 均值都低于该样本均值。曲率与交互的参照区间均跨零。两位作者都选了年龄、性别条件下的双变量对数正态模型，均保留初始模型。可以主张部分关联迁移，不能主张结构稳健、修订有效或总体无偏。 [结果](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/MILESTONE_17B_RESULTS.md) · [揭盲前终点分类](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/m17b_whole_cohort_2026-10-31/ENDPOINT_EXPOSURE.md) |
| **ENSANUT Cycle 2** | 6,931 名符合条件的实测对象构成有限、年龄性别标准化的参照。两次构建都采用线性高斯结构，并假设 BMI 与血糖残差相关为 0.30。我的汇总表复算见下表。六张表的三个主要系数均为正，但三个幅度均出现一致的偏离方向。生成的 HbA1c SD 仅 **0.328–0.338**，参照为 **0.527**。两位作者均保留原模型。 [完整案例](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31/results_report/REPORT.md) |
| **C3 / 来源校准** | 线性模型的加权来源损失在两个未参与拟合的种子上从 **0.669→0.360、0.699→0.414**，但高龄组 HbA1c 仍失配。另一年龄结构在拟合种子改善，在两个未用种子上却从 **0.173→0.205、0.237→0.260**，且新增两次年龄斜率失败。单一平均损失可以用一个统计量的改善补偿另一个重要统计量的恶化。该实验没有目标端结果。 [C3 报告](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/docs/C3_SOURCE_CONSTRAINED_GENERATION_RESULTS_2026-10-31.md) |
| **C4 / C5** | C4 全部提案都是保留，三个选择器选中相同模型，无法估计选择器增益。但同一可见证据容许调整系数 **+0.242424** 和 **−0.235294**。据此可直接推出，任何只依赖该证据的单点答案，至少在一个构造世界中绝对误差达到 **0.238859**。C5 在完全指定的高斯世界完成九次执行，三次扩列精确保留原单元格及原分析。前者给出信息限制，后者验证条件扩列实现。两个实验都没有新增生物学证据。 [C4](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/docs/C4_REVISION_ACCEPTANCE_RESULTS_2026-10-31.md) · [C5](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/c5_dynamic_extension_2026-10-31/RESULTS.md) |

**ENSANUT 尤其适合作为正文主图。** 下表单位均为相应协变量增量对应的 HbA1c 百分点。年龄按十年，BMI 按 5 kg/m²，血糖按 10 mg/dL。参照带是对既定有限样本进行聚类扰动的经验稳定带，生成范围是六张表的最小值至最大值。两者都不能充当方法等效界限。[公开汇总表](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31/results_report/all_31_endpoints.csv)

| 同一冻结发布上的分析 | 实测参照 | 六张生成表 | 相对于参照稳定带 |
|---|---:|---:|---|
| Q1，调整后的年龄效应 | 0.07513 | 0.09532–0.10444 | 6/6 高于上界 |
| Q2，未加入血糖时的 BMI 效应 | 0.08364 | 0.05032–0.05904 | 6/6 低于下界 |
| Q3，加入血糖后的 BMI 效应 | 0.05664 | 0.01631–0.02811 | 6/6 低于下界 |
| 次要血糖效应 | 0.11420 | 0.10466–0.12267 | 6/6 位于带内 |

Q3 没有直接用于来源校准，因此确实检验了一种复用用途。但它的偏差不能全部归咎于假定的残差相关 0.30。**加入血糖之前，Q2 已低估约 29%–40%。** 同样，M17-B 的八项分析也不能算八次独立验证。正反向斜率共享协方差，男女分层斜率和交互项又有代数联系。其价值在于同一份数据允许研究者看到这些结论如何共同变化。

我认为，可复用数据在这里有实质用途。研究者可以冻结一个共同假设下的联合分布，让不同分析者运行相同的分层、阈值和调整分析，观察哪些结论对假设敏感。若一个问题的答案已由公开矩直接给出，生成几万行不会增加信息；若两个相容分布给出不同答案，保留这种分歧本身就是有用的分析结果。整队列生成应继续作为主场景。整列增补与缺失单元补全各自拥有更多观测信息，宜分别评价。

## C．论文方向排序

| 排名与主线 | 可成立的贡献及现有依据 | 最少缺什么 | 什么结果会削弱它 |
|---|---|---|---|
| **1．外部文献生成的整队列，究竟支持哪些分析** | 对一份没有任何目标个体输入的冻结队列，在揭盲前区分来源直接支持、代数可推、依赖结构假设的用途，再用独立人群检验。M17-B 和 ENSANUT 已说明这种区分有实际后果。 | 一个真正入组的新参考案例，三个预先定义的用途，一个能改变依赖信息的对照，以及明确的幅度标准。 | 连来源支持最充分的用途也明显失准，或只有代数必然成立的量通过。此时只能报告迁移失败及其边界。 |
| **2．稀疏联合证据下，什么时候应给多个答案** | 给出多个满足同一来源约束的虚拟队列，显示哪些下游结论能翻转，以及补哪一条联合统计才会改变判断。C3、C4 已给出动机。 | 至少一个真实文献案例，揭盲前给出相容范围，并验证新证据缩小的范围是否仍与实测参照相容。 | 范围宽到什么都能包含，或者缩窄完全依靠作者设定。高斯缺失协方差与正定补全已有成熟研究，C4 单独不足以支撑方法论文。[PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5423529/?utm_source=chatgpt.com) |
| **3．按来源研究条件修订生成器** | 把选择人群、测量和调整集不同的来源分别重放，检验修订是否保住所关心的分析。C3 已显示平均损失会选错修订。 | 真正产生差异的候选池，同证据、同预算的统计综合，以及独立目标上的配对比较。 | 提案继续全部保留，或仅来源损失下降，目标端没有收益。此时应停止选择器分支。 |

我会用第一项做论文主线，把第二项放进方法和结果。可用的英文工作标题是 **Which Analyses Transfer? Building Virtual Biomedical Cohorts from Published Summary Evidence**。

## D．与已有工作的实质差别

| 近邻及版本 | 实际输入、产物和验证 | 对本项目的约束 |
|---|---|---|
| **KMGen，MLHC 2026** | 从目标试验自己的 Kaplan–Meier 曲线和登记资料提取分臂信息，以 LLM 和机制采样生成患者生存及不良事件轨迹。在三个留出肿瘤试验中，每个重复生成 30 次，并与实测患者数据比较。论文链接了官方代码。 | 这是最应正面讨论的临床近邻。差别在于本项目要把**其他研究**的局部关系迁移到新目标，并验证未直接拟合的用途。重复生成刻画采样变异，不能自行说明迁移不确定性。 [官方实现](https://github.com/chufangao/kmgen/tree/6ded223b44ed8dc8aaf7f26d6c89824e1b649e2f) [proceedings.mlr.press](https://proceedings.mlr.press/v340/jiang26a.html?utm_source=chatgpt.com) |
| **Cossio 与 Gilardino，ISPOR 2026 会议海报** | 一个 Agent 从 CHRYSALIS-2 的已发表材料提取人群特征，第二个编写 Python 生成患者。按原报告评价，提示修订后仍出现虚构的低频突变。 | “Agent 读临床论文并编写整队列生成程序”已有直接先例。该海报没有展示异来源到独立人群的迁移或校准的不确定性。本次未核实公开可执行实现。[ispor.org](https://www.ispor.org/conferences-education/conferences/past-conferences/ispor-2026/program/program/presentation/ispor-2026/poster-session-1-4/generative-ai-secures-synthetic-datasets-of-nsclc-trial-cohorts-for-rwd-analysis-a-privacy-preserving-case-study?utm_source=chatgpt.com) |
| **LLMSynthor，KDD 2026，arXiv v4** | 由目标边际及可得的联合汇总生成微记录，根据汇总偏差逐批提出范围、类别和数量。某些实验的汇总取自目标微数据，ACS 评价包含 16 个政策查询。v4 日期为 **2026-06-08**。 | 它已有跨查询复用，也处理近似依赖。差异应落在异质医学来源的统计语义、目标信息层级和外部检验。核查的官方提交只有 README 和资源文件，自行实现应标为论文重构。 [作者仓库](https://github.com/YihongT/LLMSynthor/tree/92e443f93c6edecc0fa9ca3045d4204da7d42aa5) [arxiv.org](https://arxiv.org/html/2505.14752v4?utm_source=chatgpt.com) |
| **G-Sim，ICML 2025** | LLM 提出和修订可执行随机模拟器，结合无梯度点估计或模拟推断得到条件参数后验。原实验可利用轨迹或真模拟器反馈，评价转移分布和决策用途。 | “Agent 写程序、数值校准、反馈修订”已成立。把轨迹换成发表的少量汇总后运行，应称 G-Sim 启发的适配。其条件后验也不能直接覆盖跨研究的测量和迁移误差。 [官方实现](https://github.com/samholt/generative-simulations/tree/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece) [proceedings.mlr.press](https://proceedings.mlr.press/v267/holt25b.html?utm_source=chatgpt.com) |
| **Bonofiglio 等，Statistics in Medicine 2020** | 各中心从自己的患者数据提供边际矩和成对相关，中央端用 Gaussian copula 生成多份伪个体表，再与原患者的多变量分析比较。作者报告，仅保留约三分之一相关对时，推断可有明显偏差。 | 这是强统计基线的直接来源。原方法拥有同源相关矩阵，本项目不能偷偷提供目标相关矩阵。应让统计综合只看 Agent 也看到的外部矩，并把补全未知依赖的规则公开。 [作者应用代码](https://github.com/bonorico/gcipdr-application-to-multi-center-IST-data) [Wiley Online Library](https://onlinelibrary.wiley.com/doi/full/10.1002/sim.8470?utm_source=chatgpt.com) |
| **Gu 等，SynDI，Biometrics 2023** | 将多个外部预测模型与内部个体数据结合，生成外部合成结局，再用堆叠多重插补和加权回归处理异质性。其推断针对明确模型参数，并有真实前列腺癌案例。 | 它表明外部模型的调整集和人群差异早已是统计综合的核心问题。它需要内部个体数据，更适合与富集场景比较。直接拿来与零记录整队列比准确率，会混淆信息量。 [官方 R 包](https://github.com/umich-biostatistics/SynDI) [Wiley Online Library](https://onlinelibrary.wiley.com/doi/10.1111/biom.13852?utm_source=chatgpt.com) |

这组近邻没有消除论文空间，但改变了举证责任。值得发表的差量是，**面对真实、异质、部分缺失的来源证据，能否事前说明一份虚拟队列可用于什么，并让未见的实测数据检验这个说明。**

## E．最小前瞻实验：一份血压队列，检验三种用途

**我会选 CHNS 2009 作为条件候选**，研究一次访视中收缩压和舒张压的联合分布。选择理由来自证据结构。两项血压的边际分布、两者的协方差，以及跨阈值组合所需的信息逐步增加，恰好可以区分“来源拟合”“关系迁移”和“未拟合用途”。项目记录中 PNS 已用作目标，ANSUR 有分性别人体测量摘要暴露，CHNS 也有尿酸、胰岛素、BMI、血脂等关系暴露。当前官方页面能确认下载路径，快照仍没有已核实的文件获取或已批准的 F2 合同。本次文献检索也出现了 CHNS 血压分型研究的题录，应加入暴露登记；我没有提取本方案三个目标量的 CHNS 数值。[CHNS](https://chns.cpc.unc.edu/data/datasets/?utm_source=chatgpt.com)

**1．先做准入，再承诺验证。** 由独立保管者核对版本、许可、2009 波次、每人唯一访视、年龄与性别字段、血压测量次数和取均值规则、用药与缺失处理。预设一个中老年年龄范围及年龄、性别标准化权重，把目标定义为该波次符合条件的有限样本。实测个体和目标汇总留在保管端。按每项分析及等价公式查项目历史、文献结果片段、来源队列别名及波次。若主用途已暴露、无法核实来源独立性、两端测量差异无法界定，或参照精度不足，记录准入失败。维持原来的三候选家族、最多六篇新原始研究上限。

**2．用一条确实存在的联合证据。** Zhang 等的北京老龄纵向研究在同一张表中按年龄层报告了收缩压 \(S\)、舒张压 \(D\) 和脉压 \(S-D\) 的 SD。对相同人群和测量，三者给出

\[
\operatorname{Cov}(S,D)
=\frac{\operatorname{Var}(S)+\operatorname{Var}(D)-\operatorname{Var}(S-D)}{2}.
\]

按其全组公开值 20.35、10.93、17.20 mmHg，我算得 \(r\approx0.534\)。这是**北京来源样本**的近似相关。论文使用两次电子血压读数均值，排除了部分心血管病史者，并有大量拒绝采血者。年代相近、都属于中国人群，仍不足以把 0.534 当成 CHNS 参数。入组还须找到适用的年龄、性别边际证据，核对目标测量方案，并说明从北京来源向目标转移哪一部分关系。该论文是可核查的线索，尚未成为项目正式准入来源。[PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9278591/?utm_source=chatgpt.com)

**3．同一张主发布表回答三个问题。** 整表从零生成。年龄、性别配额是设计输入，不能计作学到的结果。

| 用途 | 在目标上计算的量 | 揭盲前应作的解释 |
|---|---|---|
| Q1．边际水平迁移 | 两个预定年龄层的平均收缩压差，单位 mmHg | 来源有年龄分层边际。它考察水平能否跨人群迁移。 |
| Q2．联合信息迁移 | 预定高龄层的脉压 SD，单位 mmHg | 若来源提供同层两项血压的方差和协方差，其来源值由代数确定。新信息是该关系在目标上能否保持。 |
| Q3．未直接拟合的复用 | 男女分别按同一年龄分布标准化后，计算一次访视中 \(S\ge140\) 且 \(D<90\) 的比例差，单位为百分点 | 这是对筛查记录构成的描述。边际均值、SD 和相关系数不能唯一确定该比例差。须审查全文、图形和可还原的交叉表；若其等价量已在输入中，就不能再标为未拟合。 |

**4．只改变一块证据。** 给一个普通科学 Agent 和确定性工具使用固定材料。先以边际证据冻结生成结构、默认依赖假设和程序，形成 E0。再开放事先指定的联合证据块，形成 E1，只允许更新该证据所约束的依赖参数。删除 E0 中能反推该块的脉压 SD、相关图或等价描述，保留完整材料供独立审计。两个版本共享边际、测量映射、种子、预算和分析代码。E1 是拟交付版本，E0 是证据消融。两者差异回答“这块证据值多少”。若以后主张 Agent 具有算法优势，再加一个同样材料、同样来源重放和预算的分层矩匹配或 copula 综合；用目标个体表训练的 CTGAN 等须另列信息层级。

**5．预先固定发布、误差和停止规则。** 一个可执行的小预算是每臂至多两个来源情境、每情境一次初始反馈及一次固定核验，一次保留或修订机会，零自由优化搜索。每臂三个预列目标种子、每表 20,000 行，第一张预指定为主发布，另两张仅核查 Monte Carlo 波动。这样两臂最多八次来源执行、六次目标执行，失败照记。建模者只收批准材料，保管者在所有输出哈希提交后一次揭盲，第二位分析者独立重算全部三项。

- **用途尺度须来自实际决策。** 例如，若比较每 1,000 次男女访视的筛查工作量，使用者认为组间差异估错超过 30 次便会影响安排，那么 Q3 的容许误差为 **3 个百分点**。这是拟议决策标准，须由用途方在揭盲前认可。Q1、Q2 也须各自给出有根据的 mmHg 界限。缺少依据就报告绝对差，不能事后认定“接近”。
- **把不确定性拆开。** 来源 SE、取整、同队列重复报告分别处理。对假定的依赖迁移和尾部形状，至少给出两种满足相同来源矩的结构及相应 Q3；称为情景范围。目标按实际抽样、家庭或社区聚类结构报告适当的不确定性。若只定义有限样本，可报告该样本的精确描述和扰动稳定性。三个种子的范围只说明生成误差。
- **继续规则。** 先独立核对来源统计及测量映射。若 E1 在 Q1、Q2 满足预设用途标准，Q3 在主发布及预设敏感性分析中也达到决策精度，支持这份发布的多用途可行性。只有在 E1 相对 E0 的误差减少达到预定有用幅度时，才增加“联合证据有增量价值”的主张。两臂都好，也可以支持可行性。
- **停止或改写规则。** 若只有 Q1 或代数约束很强的 Q2 成功，保留有限迁移结论，停止更广的复用主张。若揭盲前相容模型已使 Q3 跨越相反的用途判断，正确输出应是“该用途未确定”，随后检验这项判断。若给了窄范围却漏掉参照，连同来源、结构、迁移三层误差一起报告，关闭该目标，不再调参重发。

## F．最可能使科学结论失效的实现问题

| 优先级与证据强度 | 实际发现 | 最小修正 |
|---|---|---|
| **1．来源统计语义，已复现的通用缺口** | `source_replay.py` 的 `_check_metadata` 主要核对统计类型、单位、变量集合和调整变量包含关系。我用“Y 对 X 回归、调整 Z”的元数据测试，把所取系数从 X 换成 Z、反转 Y 与 X，或删除文字描述中的样本筛选，仍可得到 `aligned=True` 并声明 `computed`。对照测试中的错误分位概率被正确拒绝。现有 11 项算子测试全部通过，仍捕捉不到这一层问题。M17-B 的专门审计核对了反向回归，F1 也另查六个分层操作，因此没有依据追溯判定它们算错。 [元数据核对](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/cohort_harness/source_replay.py#L24-L58) · [统计算子](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/cohort_harness/source_checks.py) | 为每个关键来源量明确绑定结局、暴露、目标系数、调整集、事件、分母、筛选、权重、尺度和测量规则。将上述反例加入回归测试。 |
| **2．来源人群和测量映射，已确认的能力范围** | `whole_cohort_feedback._read_plan` 要求反馈人口等于实际执行人口，测量模式只接受 `identity`；`_compute` 在这一张输出表上计算。历史 ENSANUT 个案另有来源情境重建，其中 Pani 的调查加权均值对的是未加权近似。Pani 原文也明确区分 NHANES 的年龄调整模型。把这些近似统称为“已重现多研究”会直接影响结论。 [反馈代码](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/cohort_harness/whole_cohort_feedback.py#L43-L111) [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2551641/?utm_source=chatgpt.com) | 只为入组案例实现必要的来源选择、测量和加权操作。每项标明可精确重放、近似或无法计算。新增适配器独立冻结，保留历史 F1 的原范围。 |
| **3．依赖识别、来源重叠和不确定性，科学风险已由结果暴露** | 反向调整斜率不能取倒数得到正向斜率；分别调整年龄和性别的两条投影也不能直接当作同一联合模型的系数。M17-B 用协方差关系、ENSANUT 在假定相关下联立投影，较有根据，但未报告的依赖仍是自由度。`analysis_evidence.py` 能标出已声明的共用队列和队列未知项，不能由此估出研究间相关。Pani 与 Liu 的 NHANES 年份有重叠。 [来源重叠汇总逻辑](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/cohort_harness/analysis_evidence.py#L216-L233) | 给出每项分析依赖哪些未知参数、哪些研究共享参与者。能算相容范围就算范围；只能列情景时保留情景标签。把文献个体 SD、估计量 SE 和人群迁移分别传递。 |
| **4．真实反馈、费用和目标隔离，局部严格、全程仍有边界** | `verify_feedback` 重新计算绑定结果；F1 的 `final_submission` 比较原反馈字节、父候选和证据清单，`run` 固定种子且封顶两次。这部分可信。通用任务预算覆盖查询、下载和修订，实际生成调用数另由控制器限制。生成器进程有 OS 隔离，外部 Agent 的一般工具访问靠流程管理。模型 ID、token 和全程成本有未计量项。 [F1 控制器](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/core_v0_2026-10-31/run_integration.py) | 为 F2 使用只读白名单材料、独立保管者和完整调用账本，明确区分构建次数、优化尝试、执行次数、唯一表数和目标队列数。不得用几秒钟的执行器时间推算科研总成本。 |
| **5．第三方复现，已确认的可移植性问题** | F1 的 `seal/verify_assembly` 依赖绝对路径和一个 `D:` 盘外部技能副本，执行后端绑定特定 WSL 配置。原环境的哈希承诺有用，其他实验室仍难以按原命令重放。M17-B 的路由标签也曾触发四个误报，后来根据实际执行收据单独裁定。 [执行后端](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/cohort_harness/execution.py) · [原始误报裁定](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/m17b_whole_cohort_2026-10-31/independent_audit/AUDIT_ADJUDICATION.json) | 保留历史收据，增加相对路径清单、固定依赖和一个无受限数据的第三方重放入口。对新案例公布生成程序、允许公开的证据摘要和独立的汇总核验脚本。 |

## G．投稿定位与接下来三步

**当前包。** 我会把它定位为可公开讨论的开发研究或工作坊稿。若单独写一篇严谨的回顾性论文，主题可以是“两次整队列生成中，方向一致与幅度失真如何共存”。必须明确使用不同开发版本，完整展示失败。F1 已完成其限定的实现冻结，F2 和最终结果／主张锁定 R1 仍待完成。当前证据不足以支撑主流医学信息学方法期刊上的通用性能主张。

**完成一次合格的前瞻案例后。** 首选考虑 **BMC Medical Research Methodology**。它的范围明确包含方法选择如何影响研究结果的实证研究。若结果混合，但预设用途、目标独立性、完整报告和可复核材料都过关，**PLOS ONE** 也是合理选择。审稿人最可能追问的是，哪些结果能由公开矩直接算出，哪些真正检验了数据复用；为什么这一个新目标足以支撑摘要所用的措辞。[Springer Nature Link](https://link.springer.com/journal/12874/aims-and-scope?utm_source=chatgpt.com)

**若要投更强的方法论文。** 争取 **Journal of Biomedical Informatics** 或 **MLHC**，我会要求至少在另一个独立目标上复现分析边界，加入同信息的强统计综合，并检验来源语义或人群映射究竟改善了哪种结论。JBI 强调可推广的方法贡献；MLHC 已发表 KMGen，可直接看到该领域对临床生成、实测验证和公开实现的比较标准。若目标是统计方法期刊，还需进一步发展识别界限、估计或不确定性性质。[AMIA - American Medical Informatics Association](https://amia.org/news-publications/journals/journal-biomedical-informatics?utm_source=chatgpt.com)

接下来信息价值最高的三步是：

1. **先判定一个案例是否真能回答问题。** 完成 CHNS 的关系级暴露、正式文件、来源独立性、测量方式和精度核查。能通过才签 F2，不能通过就记录具体失败条件。
2. **把语义核查放在生成之前。** 修复已复现的回归角色与筛选盲点，锁定三个用途、来源映射、实际容许误差，以及至少两个相容结构对 Q3 的预测。请独立审查者在未见目标前签下“哪些用途有希望、哪些应当保留判断”。
3. **运行一次配对的证据信息实验并只揭盲一次。** 发布 E0、E1 全部预设结果，以一张图并列显示每个用途的来源约束、事前判断、目标误差和剩余分歧。**若最后只有来源直接约束的量通过，就把这个边界写成论文结论。**