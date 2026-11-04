# 论文支撑、数据复用与图表审计

日期：2026-11-04。范围：既有 manuscript、公开范围的 RESULTS、protocol、聚合 report 及独立审查记录。本审计没有读取患者或生成行，没有运行生成器、患者分析或新实验，没有修改历史文件。采用 arise-evidence-to-manuscript 的证据—主张—图表一致性原则；不扩展成新的研究计划。

## 核心判断

现有结果已经可以支撑一篇正面的、以科学用途为中心的方法论文：**Agent 接收科研问题与人口/测量定义，获取或使用研究证据，自选联合模型与数值用法，生成可以交给普通分析软件的数据，并说明哪些分析得到了支持、哪些依赖缺失的联合证据。** 最有力的论据是具体建模操作与实际分析结果，不是“检查全部通过”，也不需要把 Agent 胜过统计模型或逐项复制一个真实样本当作论文成立条件。

现有证据的三个最强支点是：

1. **模型作者确实完成了科学转换。** 主实验 CHNS E1 A01 把两个分别调整的已发表投影解成联合模型参数；11-04 新构造把 Pearson/Spearman 与选定边际分布转成相容的潜在依赖，并显式保留不能直接转用的条件系数。两者比“调用了工具”更直接地说明 Agent 的科学角色。
2. **生成数据有可展示的分析用处。** 主实验中新增关系证据使六项预定系数中的五项平均绝对差异减小；CHNS 摘要辅助结果接近所给回归/相关摘要；HRS 完整纵向表可以运行原生混合模型并保留下阈值负交互。11-04 模型若干系数的差异也与真实样本重分样差异处于相近数量级。上述是不同条件下的用途证据，不能合成一个成功率。
3. **端到端链路现在已有一个真实完成案例。** `gap_search` 无预设 DOI 地检索五篇原始研究，`evidence_to_generation` 接收其审查后证据，自主构造并交付三个固定最终样本。预生成解析敏感性还定位了条件 BMI 分析依赖的缺失 BMI–glucose 关系。这条新证据尚未进入 11-03 的 v0.8，值得整合；它目前只有一名构造者、一个已暴露 CHNS 参照，不能代表六家族的统一新系统验证。

## Contribution → 实际支持 → 完整对照 → 展示 → 缺口

| 论文贡献/可写主张 | 最强已完成支持 | 必须一起保留的比较与结果 | 最合适的展示 | 当前缺口及写作处理 |
|---|---|---|---|---|
| 科研需求驱动的证据→联合模型→数据过程已经实现 | 主实验所有十个 E1 Agent 至少把一条量化关系用作约束；A01 的分开投影转换有冻结代码追踪。新链路由 Agent 自选高斯 copula、边际、依赖转换与运输假设 | 研究者、检索 Agent、构造 Agent、数值工具的实际角色；约束/检查/背景/拒用；未报告的补全假设 | 图1；一张紧凑证据使用表；完整来源—操作表置补充 | 不是新概率分布或所有情况下的自动化，也未隔离“任务适应”本身的性能增益。写实际决策，不写第一性优越或降低人工成本 |
| 外部关系证据可增加特定分析的信息 | 主实验 CHNS glucose 平均绝对差异 0.134019→0.024079；ENSANUT 三项均减小；六项中五项减小 | 六项全呈现；CHNS BMI 0.020380→0.031557；CHNS E1 A03 条件 age 均值为负；ENSANUT 量级偏差；所有五名/条件作者、三种子、四个统计构造 | 图2全六面板；原量纲六行结果表 | 不把五项写成 83% accuracy；不同作者/法律/证据用法不是配对或单一机制因果效应。参照是已暴露的选定样本 |
| 可获得摘要能够成为可分析的联合数据 | L/R 三名/条件；R 的 BMI 作者均值 0.052821–0.055789，对所给 0.054946；三个回归与两个相关量均有明确结果 | 同一实验完整 L/R 六名作者；全部30指标；单独标注后补统计校准器；初末不变与重复表去重 | 图3五个分析面板；完整30项补充表 | R 已拿到所有30摘要及相关元信息，是有用的重构，不是隐藏结果预测。后补统计族也能接近这些量；非移除 Agent 消融，预算不对称 |
| 无个体输入也能生成复杂纵向分析数据 | HRS：11,509虚拟人×4访视；Agent 与原始法重构各3有效表；下阈值 age×HbA1c −0.04464，对所给 −0.046837 | 两个预定交互；全部16固定效应；27项基线诊断；更正后的原始法；3张最初无效比较表及恢复记录 | 图4两个交互为主体，增加上/下HbA1c散布摘要；S图列全16效应 | 所有分析系数均输入；只是 published-model reconstruction。高HbA1c SD 0.563，对原样本公开1.4、原论文模拟0.6；弱上阈值交互不稳定。不能算第七个真实患者家族 |
| 开放检索能够接到自主构造与分析交付 | 11-04 无预设DOI检索五篇原始研究→1模型→1试表+3最终表；二级 BMI 0.04217–0.05176，对参照0.05495；age关系相近 | 新模型两项回归全部7个非截距项，截距与全部诊断附表；11可用近似/23不可用source checks；retain无修订 | 图5A和过程注释；搜索与证据台账补充 | 不能将此前 live A/B 与新模型差异归因于检索：作者、来源、人口描述、法律和种子均变了。仍由host派发，Agent工具仅程序化隔离 |
| 科学用处应按分析判断，并以真实样本变动为背景 | 100次社区不交叠CHNS重分样；A BMI真实—真实中位绝对差异0.007239，对生成对称中位差异0.004383–0.012727；A age、female与部分B age亦为相近量级 | 全36指标和100split；B glucose 0.079642–0.109154，对真实0.023839；B female 0.077716–0.117915，对0.021398；分位数差异 | 图5B；完整36项表 | 这是同一有限样本条件下的描述背景，不是等价阈值、交换性检验或跨人群验证；不宣称小于真实—真实即优于真实 |
| 显式模型能把缺失证据定位到具体科研分析 | 新模型预生成解析报告：仅未报告BMI–glucose潜在相关0.10→0.40，条件BMI系数+0.03422→−0.01095；二级回归与边际保持不变；独立数学复核 | 两个端点及固定其余参数的定义；采用0.25仍为假设；这是解析敏感性，不是新增生成实验 | 图5C两个解析情景点；补充推导 | 可以写“发现该模型下分析的证据缺口”，不写校准置信区间、普遍适用性分类器或证明它导致全部失配 |
| 该思路有相邻的数据任务适用性 | M10 NHANES胰岛素和PNS HbA1c的未测变量增补；胰岛素BMI和曲率方向、HbA1c age/BMI方向跨两作者保持 | 每家族四个预定分析；性别×BMI不稳定、HbA1c曲率错误/不稳、量级偏差；观察协变量输入与保留规则 | 补充图/模式表，主文一句 | 不与whole-cohort零个体输入混用；missing-cell模式尚无相应验证。当前不为扩大范围统一重跑 |

“完整对照”指让问题的替代解释可见，不要求人为增添比赛：主实验已有 E0/E1 和固定统计参照；摘要辅助已有L/R与后来统计补充；HRS已有原始法重构；新端到端实例已有明确证据/参数来源、预定分析、已冻结真实参照及解析敏感性。它们足以支撑本论文的有界主张，不足以支撑通用性能优越、修订收益或独立临床确认。

## 五张主图的建议版式

**图1：研究问题如何变成可分析的数据。** 一条主路径：人口/测量/分析请求→证据获取或输入→Agent的数值解释与模型选择→执行生成→实际科研分析。嵌入A01分开投影变联合参数的短例，标明 reported/derived/assumed。通过图例说明主实验是 curated evidence，新端到端例是 open search；不能把所有历史实验画成同一自主流程。目标参照放在评估侧；可选保留/修订支路不画成已验证的性能增益循环。

**图2：全部六个外部证据分析。** 保留当前2×3布局、所有作者和种子及统计构造。作者标签A01–A05跨E0/E1不配对，不连线。均值和种子范围与参照区间明确区分；CHNS CR1-t与ENSANUT等八单元稳定带分开解释。配六行原量纲差异表，不再增加重复排名图。

**图3：摘要能支持什么重构。** 三回归+Pearson/Spearman五个面板，显示全部六名L/R作者和三固定种子。后补统计校准器用独立栏或符号标注“separate supplement”，不悄悄纳入同次随机分配。初末全是retain，主图只显示一个数值阶段并说明别名；完整初末清单留补充，不画假改善箭头。

**图4：纵向数据与原生分析。** 两个预定交互必须并列；不只强调负的下阈值交互。保留两条实现所有有效种子及所给公开系数。图旁小表或下部面板显示分段HbA1c散布，直接呈现模型复现与原始队列分布差异。全16效应和27基线诊断放补充；3张解析器错误表留失败账，不作对原论文的方法劣势。

**图5：从开放检索到科学使用及证据缺口。** A：11-04模型的两项回归全部七个非截距效应；B：同七效应的真实—真实与生成—真实描述背景，直接读既有100split聚合；C：未报告BMI–glucose依赖的两个已复核解析情景。不用一个整体质量分数，不把解析端点连成未经计算的曲线。若最终单页过密，主图保留A+C，B完整七面板移补充，并在主文保留真实样本背景的主要正反结果；无需第六张主图。

所有主图可由既有公开聚合重绘。图注必须标明每个点属于作者、种子、split还是published summary；五图不共享一个临床验证分母。

建议主表最多四张：①各实验/信息/模式/参照角色与精确计数；②六主分析的算子、单位及样本参照；③完整六项E0/E1差异，附统计参照；④信息充分度与可支持分析的结果摘要（不是accuracy排名）。现有v0.8表4的五项L/R精确值可保留，第四表不必另加，避免重复图3。

## 数据复用：现在应统一的是报告层，不是把所有旧模型重新生成

| 既有包 | 可直接复用的聚合入口与结构 | 本轮值得统一重做 | 本轮不需要重开 |
|---|---|---|---|
| `main_study_freeze` | `final_evaluation/RESULTS.json`：72 `all_scheduled_slots`、24 `construction_summaries`、6 `agent_information_contrasts`、4统计参照；所有图2量都在这里 | 提取标准长表、保留原native units、重画可读图2和六行表、核对author→seed聚合顺序 | 79次物理执行、患者参照、已冻结法律/参数 |
| `information_revision_ablation` | `COMPLETE_RESULTS.json`：42 runs、360 constructor/stage/statistic行、180配对变化；24独立表、18独立交付 | 显式初末别名与重复去除，完整30指标出版附表；关联单独`summary_comparator` | 重新生成重复的final、重复临床评价、把retain改写成改进 |
| `hrs_public_example` | `summary/AGGREGATE_RESULTS.json`含32 arm×effect与54 arm×distribution；两个 all_seeds CSV 为**聚合系数/诊断**而非个体记录 | 从all-seed聚合画精确区间/范围，核验original-source vs published-synthetic vs reconstructed-law标签 | 原生混合模型拟合、恢复前三无效表的科学比较资格、增加有利种子 |
| `agent_system_live` | `evaluation/REPORT.json`：12初末slot、6独立交付；两request完整系数与分布 | 补充过程/历史表；保留A/B联合建模与失败信息 | 当作与11-04模型配对消融；按12独立表计数 |
| `evidence_to_generation` | `evaluation/REPORT.json`：6初末slot、3独立交付；`SENSITIVITY_REVIEW.json`；独立数值审查final pass | 新增端到端主文/图5，系数、诊断、假设和数学敏感性相互绑定 | 重跑生成器、修改0.25假设、针对新参照调参 |
| `real_real_calibration` | `REPORT.json`：100 splits、36 metric summary、fixed generated seeds 7401–7403；`COMPLETE_METRIC_TABLE.md` | 把其结果绑定到11-04新模型而非live A/B；全36指标附表；重绘现有七系数 | 重新读取患者、再抽更多split、把分位点制成事后通过线 |
| NHANES/PNS、HAALSI/Turkana及更早历史 | 各自RESULTS/聚合包及原协议 | 一张模式/版本/信息条件/所有预定终点的完整补充索引；可统一字体配色 | 并入当前同版benchmark、为了增加案例数重新跑旧输出 |

建议报告长表至少有：`study_version / family / task_mode / information_regime / reference_role / constructor / stage / distinct_table_or_alias / seed / analysis / term / adjustment_set / unit / estimate / uncertainty_kind / source_status / failure_status / source_artifact`。这只是展示层共同schema；不把不同算子、信息条件、重复输出或权重定义变成共同估计量。不跨家族平均系数误差，不按虚拟行数加权。

新的生成实验不是整理稿件的前置条件。如果论文要改称“同一个当前自主检索系统在全部六个真实家族都已验证”，那么历史结果确实不能承担该主张，须另作同版新实验；但这会改变研究范围。当前合理选择是收紧该主张、保留版本区别并完成既有证据论文，不能以“统一重跑”掩盖版本更换，也不能把已暴露家族重新命名为首次验证。

## 必须纠正的证据身份与分母

- **当前六个真实参照家族**是NHANES、PNS、CHNS、ENSANUT、HAALSI、Turkana；不是六个同协议、同版本或同输入模式实验。它们属于不同的主实验、增补模式及历史whole-cohort发展阶段。
- 更早NAGALA、DIETFITS、FIReWoRk、Queen's、CHANGE、Travers12、He44属于兄弟目录的历史材料。本审计未逐一重核其结果，不能据名称/文件存在直接加入统一benchmark或主图。其身份应由独立历史清点决定；没有必要为了本篇主线逐一重跑。
- HRS与Plaza是published-summary/model例，不能加入实际患者参照家族分母。HRS可强力支持纵向数据能力；本审计没有读到可支撑Plaza具体性能主张的已完成报告，先只保留身份，不补写结果。
- v0.8目前主要整合三种信息设置；11-03 live、11-04自主检索→生成与真实重分样尚未成为其结果。修订稿需要在新的证据台账中新增这些单元，不能只换摘要措辞。
- 主实验72张最终表来自24构造；L/R 42执行只有24独立表、18独立交付；HRS9物理生成只有6有效比较表；新端到端4执行只有3最终交付。真实重分样100次仍是一个既有CHNS参照；不把这些分母相加当作研究样本量。
- `evidence_to_generation/evaluation/REPORT.json`保留评估时`independent_reviewer_status=pending_separate_review`。独立审查后续已是`pass_final`且核对同一report hash。出版汇总应连到完成后的独立审查记录，不修改冻结report，也不要误写审查尚未完成。

## 需要补齐的是写作/复现，不是新的科学赛道

| 缺口 | 对论文的实际影响 | 现在足够的处理 |
|---|---|---|
| 新端到端结果与v0.8脱节 | 摘要仍主要说curated evidence，读者看不到最近已经完成的真实链路 | 新版稿中独立加入一个完成案例，与规模较大的curated主实验并列分工；更新证据台账和图表 |
| 多版本聚合的单位、别名及参照角色不统一 | 容易混淆表数、模型数、研究数与已提供/未提供目标量 | 出版派生长表与schema校验；保留原始input hashes和source路径；只做聚合重算/重绘 |
| 缺少独立未暴露的当前系统泛化证据 | 限制广泛可靠性与外部确认的措辞 | 在本文明确为开发性、分析特定用途；不把新增实验列为既有论文必须补齐的门槛 |
| 无修订收益 | 多个单元retain且初末不变 | 方法允许review/retain；结果如实零改动；不增加循环来制造亮点 |
| 统计对照作者/预算不对称 | 不能推通用Agent优势或人工成本优势 | 保留全部已有对照，结果写混合排序与共享重构能力，不再扩展竞赛 |
| 证据、结构、运输不确定性未校准 | 三种子范围不能承担科学不确定性 | 解释seed范围条件于法律；新解析敏感性作为明确假设依赖示例，不冒充置信区间 |
| 公开可复现范围与本地原始数据不同 | “可复现展示”容易被写成“完整重跑一切” | 明确aggregate-only figure/table reproduction与本地原始数据分析的不同前提；保留完整失败账 |
| 投稿格式、作者/伦理/资金/AI说明仍未完成 | 已有科学草稿不等于投稿就绪 | 在科学结果整合后按目标期刊处理；无需为格式工作启动新队列 |

推荐新的Results顺序：①具体模型作者操作与交付内容；②外部证据的六项完整结果；③摘要辅助重构；④纵向published-model例；⑤开放检索到交付的完成案例、真实样本变动背景和一个明确证据缺口；⑥简短保留增补模式与历史失败。主线始终是“能做什么科学分析，以及凭什么”，而不是实施审计次数或总体胜负。

## 主要已读依据

- [当前稿v0.8](../../manuscript/DRAFT_v0_8.md)、[v0.7整合台账](../../manuscript/INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md)、[贡献与图表](../../manuscript/STORY_AND_CONTRIBUTIONS_v07_2026-11-03.md)、[既有图表审计](../../manuscript/STORY_AND_FIGURE_AUDIT_2026-11-03.md)。
- [主实验RESULTS](../main_study_freeze_2026-11-03/RESULTS.md)、[主实验聚合](../main_study_freeze_2026-11-03/final_evaluation/RESULTS.json)。
- [L/R结果](../information_revision_ablation_2026-11-03/RESULTS.md)、[完整聚合](../information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json)、[统计补充](../summary_comparator_2026-11-03/RESULTS.md)。
- [HRS结果](../hrs_public_example_2026-11-03/RESULTS.md)、[HRS聚合](../hrs_public_example_2026-11-03/summary/AGGREGATE_RESULTS.json)。
- [Live结果](../agent_system_live_2026-11-03/RESULTS.md)、[Live协议](../agent_system_live_2026-11-03/PROTOCOL.json)、[Live聚合](../agent_system_live_2026-11-03/evaluation/REPORT.json)。
- [自主检索结果](../gap_search_2026-11-04/RESULTS.md)、[新构造结果](../evidence_to_generation_2026-11-04/RESULTS.md)、[协议](../evidence_to_generation_2026-11-04/PROTOCOL.json)、[聚合](../evidence_to_generation_2026-11-04/evaluation/REPORT.json)、[完成的独立数值审查](../evidence_to_generation_2026-11-04/evaluation/INDEPENDENT_NUMERICAL_REVIEW.md)。
- [真实重分样结果](../real_real_calibration_2026-11-04/RESULTS.md)、[协议](../real_real_calibration_2026-11-04/PROTOCOL.json)、[聚合](../real_real_calibration_2026-11-04/REPORT.json)。
- [M10两家族增补](../../MILESTONE_10_RESULTS.md)、Wave A完整结果 (local-only historical artifact; not included in this export)、[历史结果补充](../../manuscript/SUPPLEMENT_HISTORICAL_RESULTS_v05.md)。

以上具体数值来自已完成聚合报告。此审计对report结构、分母与叙事含义进行了交叉核对，没有声称重新独立验证患者或生成行层面的统计。
