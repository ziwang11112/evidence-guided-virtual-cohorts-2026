# Method identity and minimum rerun audit

审计日期：2026-11-04。此文件是新的只读审计结论与前瞻建议，不是实验 release，不启动任何构造、评估或检索。

**结论：已有可描述的共同方法核心，但没有一个覆盖全部历史案例的、字节级且实验设计一致的全局 frozen method。存在 `core_method_v1_2026-11-03` 的程序级冻结，以及各批次分别冻结的任务、信息包、作者规则、控制器、运行环境和评估。最新升级不要求全部旧案例重跑。若论文要声称“新版开放检索完整流程已在不同请求/人群中重复执行”，才需另建一个小而统一的新批次；旧实验不能改名为该批次，也不能删除失败来换取整齐故事。**

**本轮决定：CHNS/ENSANUT 统一主实验已经完成，不重复生成。当前新增工作是已有聚合结果的整理、必要重绘与论文起草；没有任何新 scientific run 是本轮交稿的前提。下文的小统一新批次只是当论文坚持“新版开放检索流程跨 case 泛化”等更强主张时的条件缺口，不自动成为当前任务。**

## 1. 本次实际检查范围

- 阅读当前研究方向、系统贡献计划、核心方法冻结、各指定批次的协议/任务/锁/公开结果和源材料 metadata，以及相关 harness 源码。
- 公开结果仅用于确认批次归属、完成状态、保留/修订、技术事故和已经公开的限制；未据结果优劣筛选案例。本报告不重算或重新排列旧目标效果。
- 没有打开患者、观察协变量、真实参考或生成行表；没有执行 generator、fit、临床分析、科学测试或旧脚本；没有下载、网络检索或修改旧冻结文件。对若干数据路径只做 `Test-Path`，未读取其字节。
- 校验了最新 `CONTROL_MANIFEST.json` 中 9 个 harness 源文件和 4 个 controller/evaluation 源文件的 SHA-256：全部与当前文件相符。这是代码完整性核对，不是科学复现或当前运行环境验证。
- 本审计不声称所有历史 hash 已重新验证。旧 case README 中“pending release”等表述是历史准备状态；最终 `RELEASE`、closure、结果和 claim lock 决定是否已经完成。
- 本审计覆盖下文指定的关键批次，并非对项目全部 13 个历史数据家族逐一重新验证。若整合清单列出 13 家族，该数字只表示身份/历史清点，不是 13 个同版本 benchmark case、13 次独立验证或 13 个当前运行器可直接重跑的数据集。未逐一核清的家族应明确标记 `identity inventory only`。

主要依据：[当前研究方向](../../docs/CURRENT_RESEARCH_FOCUS.md)、[系统贡献计划](../../docs/AGENT_SYSTEM_CONTRIBUTION_AND_EVALUATION_2026-11-03.md)、[core method v1](../../docs/CORE_METHOD_AND_MAIN_RUN_FREEZE_2026-11-03.md)、[snapshot](../main_study_freeze_2026-11-03/METHOD_SPECIFICATION_SNAPSHOT.json)、[最新 control manifest](../evidence_to_generation_2026-11-04/evaluation/CONTROL_MANIFEST.json)。

## 2. 应冻结的是什么

方法核心是：接收研究需求和人群/测量定义，取得允许的信息，Agent 选择证据及联合生成结构和参数，工具执行与检查，Agent 修订或保留，交付数据及其证据/假设/用途说明。不同请求允许不同生成器。不能把同一个 copula、方程或固定统计分布当成这个系统的必要身份。

但共同概念不等于共同实验版本。至少需要分开以下四层：

| 层级 | 已有事实 | 对论文和重跑的含义 |
|---|---|---|
| 程序/方法核心 | `core_method_v1_2026-11-03` 已冻结；允许 task-specific model、数值 uptake、有限矩检查、可选反馈及保留 | 可以统一写方法的稳定原则；不能声称所有更早实验都执行了后来新增的检查 |
| 实验批次 | 各批次有独立协议、信息条件、预算、作者分配、种子和 release | 结果应按版本和信息条件归属；不能跨批次合并为一个处理效应 |
| 任务和科学模型 | 人群、测量、信息包、模式、变量和 law 均可不同；每个最终配置另行冻结 | 换 source、目标信息、law 或反馈机会，是新的科学构造，不是“重算同一个结果” |
| 实现和评估 | harness 有复用组件，但有独立的 case controller、source operators 和 evaluator | 可统一审计/呈现；不能将新脚本直接套旧案例并称同一已验证接口 |

`METHOD_SPECIFICATION_SNAPSHOT.json` 的 `scope` 明确是 procedure/prospective allocation，`execution_released=false`；它要求另行绑定 case information、operator/comparator、analysis/budget 和 independent release。后来的 main-study `RELEASE.json` 才启用该批次。最新 11/4 control manifest 又绑定了独立的 `run_session.py`、两个回归的评价和历史 CHNS aggregate reference。因此答案不是“完全没有冻结”，而是“方法原则有版本冻结，实际实验是批次/任务冻结”。

另一个重要实现边界：[最新 implementation notes](../evidence_to_generation_2026-11-04/evaluation/IMPLEMENTATION_NOTES.md) 明写 controller **supports only request B**。`cohort_harness/request_intake.py` 仍只准备结构化 request 和外部 author packet，不自行解释任意自然语言、启动 LLM、检索或执行生成。`semantic_feedback_v1.py` 只接受 `whole_cohort`；intake 对 enrichment/completion 的 source feedback 返回 `not_selected_for_this_mode`。不能把当前 B demonstration 叫作已经自动适配所有历史任务的统一运行器。

## 3. 各批次实际身份与处置

“直接使用”指在原协议对应的结论内纳入论文；“仅重算评估”指保持原生成器和输出不变，必要时另存有清楚标签的分析；“新构造”指新协议和新科学 author，不重开旧预算。以下分类不依据哪个真实结果更好。

| 案例/批次 | 实际方法与信息身份 | 建议处置 | 何时才需要新构造 |
|---|---|---|---|
| **CHNS main study** | whole-cohort；E0/E1 预整理外部信息；每条件 5 fresh authors，另有 1 固定 statistical specification；禁止新 browsing；有数值 uptake、law-derived analytic operators、有限矩和独立算术检查；最多 2 exploratory attempts，3 final seeds；source replay 不可用 | **直接作为受控信息比较主证据**。保留全部作者、比较器、指标和反例。若仅统一单位/图表，使用既有 aggregate；无需重新生成 | 要把它声称为“自主检索 + 当前 analysis-oriented review”的重复证据时，需要新批次；旧 E0/E1 对比不能升级改名 |
| **ENSANUT main study** | 与 CHNS 同一 main-study release；人群、fasting/diagnosis selection、8-cell equal weighting 和 mg/dL units 不同；Jansen/Pani projection helpers；不是全国 survey estimand | **直接使用**；与 CHNS 分 panel，保留实际人口定义和 estimator | 当前完整流程跨人群复用时，是与 CHNS 配对的新构造候选；不能直接使用 CHNS request B controller 而忽略配额和权重 |
| **CHNS information/revision ablation** | 6 authors，L 为外部证据，R 再获完整目标 development summaries；初始/追加允许信息诊断阶段；有 retrieval allowance；全部保留导致无额外 revision gain | **直接作为信息充分度/修订限制的独立支持单元**。不并入 main study E0/E1，也不把 R 称为外部证据预测 | 若研究问题改变为新 review/search 机制的收益，应另定对照；旧 L/R 数据不需要因最新 workflow 更新而重生 |
| **HRS published example** | source-rich longitudinal reconstruction；给出了生成模型和待分析关系系数；一 Agent 与 published-law comparator；native R/lme4；无患者输入；非独立 transport | **直接作为纵向能力/公开模型重建证据**。保留 3 次错误 comparator 和独立修复协议；6 valid tables 来自两构造 | 没有未解决的旧模型科学错误要求再次生成。若要证明当前 request intake 可处理 longitudinal task，只需新的接口适配验证；若要声称新完整流程生成过 HRS，则需另开新构造，但不是最小优先项 |
| **NHANES 2015–2016 insulin，M10** | enrichment；真实 age/sex/BMI/glucose 可见，仅 insulin 生成；固定外部 evidence；2 authors × 3 residual seeds；原 source replay 是假设下的 approximate contexts | **直接保留为历史 enrichment 能力与分析用途边界**；不能并入 whole-cohort 主效果。仅统一绘图/单位时无需生成 | 若把“当前系统同样支持 enrichment”作为实证主张，须适配非 whole-cohort feedback 并重新构造；重算旧评估不能证明新版流程运行过 |
| **PNS HbA1c，M10** | enrichment；baseline age/sex/BMI 与 later HbA1c；2 authors × 3 draws；provided weights，缺 PSU/strata | **与 NHANES 成对保留**。不伪造 survey CI，不把 baseline 与后续 HbA1c 改写为同访视；无需因界面升级重跑 | 与 NHANES 相同；若扩展 enrichment 新批次，预先选择两任务，不能在旧表现中挑一个 |
| **HAALSI glucose，Wave A** | whole-cohort；5 authors + 1 statistical reference；预设 source contexts 和统一 gate；POC pooled glucose；连续 glucose joint evidence 很稀疏 | **历史补充/边界，保留完整失败 gate 和 zero-anchor 问题**。不改原 pass rule；可用旧 aggregate 做透明的描述图 | 只有当前方法跨 biomarker/区域推广成为主张时才有必要新构造；需先固定可用证据和含义明确的新评价，不以“修好失败”为目标 |
| **Turkana lipids，Wave A** | whole-cohort；5 authors + 1 comparator；Greiner 6 site/sex contexts；geometric means、unknown weights、regression transform/adjustment 不全；target unit mapping 单独审查 | **与 HAALSI 共同保留为历史边界**，不能因为失败从总证据记录消失 | 同上；如做该扩展，应预先同时纳入两个旧 Wave A case，保留来源/operator 不足和失败，不只选容易改善的一例 |
| **Live A/B，11/3** | 两 fresh authors 分别处理两个不同请求；限制为 3 个既有 DOI 的原文检索；实际 law 不同；A/B 作者与请求混杂 | **直接作为系统连接过程证据**，不作为大样本跨请求性能比较。旧缺陷和保留决策不覆盖 | 若要分离 author variability 与 request adaptability，必须在统一新批次中每请求超过一位 author；补画旧结果不能解决 |
| **Reviewed evidence → generation，11/4** | 先有独立 gap search 的 5-paper packet，再由一 fresh constructor 写完整 6-column law；一 trial + 三 delivery，全部反馈后保留；新的 joint implication/sensitivity 检查 | **直接作为当前实现示例和分析敏感证据缺口主案例**。已完成 independent audit，无代码漂移发现，无重跑必要 | 要扩大到跨请求/人群重复时，做新的统一批次。它与旧 live B 的历史差异不能估计 search 或 review 的因果收益 |
| **Real–real context，11/4** | 对已存在 CHNS 样本的 prescribed splits；解释 frozen 最新 table 的差异尺度 | **独立解释上下文**，不计新增 case、患者来源、generator improvement 或新方法运行 | 若只整理当前结果无需复跑。换 evaluator/metric 时先判断既有 aggregates 是否足够；不得事后用阈值把结果改为等效通过 |

依据：[main author contract](../main_study_freeze_2026-11-03/AUTHOR_CONTRACT_TEMPLATE.md)、[main claim lock](../main_study_freeze_2026-11-03/CLAIM_LOCK.json)、[CHNS case](../main_study_freeze_2026-11-03/cases/CHNS2009/README.md)、[ENSANUT case](../main_study_freeze_2026-11-03/cases/ENSANUT2018/README.md)、[information protocol](../information_revision_ablation_2026-11-03/PROTOCOL.md)、[HRS protocol](../hrs_public_example_2026-11-03/PROTOCOL.md)、[HRS repair](../hrs_public_example_2026-11-03/recovery_v1/PROTOCOL.md)、[M10 protocol](../analysis_utility_feasibility_2026-10-30/protocols/feasibility.md)、[M10 results](../../MILESTONE_10_RESULTS.md)、Wave A release summary (local-only historical artifact; not included in this export)、[live protocol](../agent_system_live_2026-11-03/PROTOCOL.json)、[latest protocol](../evidence_to_generation_2026-11-04/PROTOCOL.json)。

## 4. 最新升级中哪些是实质差异

1. **自主 retrieval 的范围变了。** Main study 使用封闭整理包；live A/B 只检索预定 DOI；gap search 无 DOI seed、无目标方向提示，独立挑选研究。最新 construction 使用该搜集结果，不在自己的生成单元重开检索。不能把“同一 Agent 从任意需求自动独立完成所有阶段”写成已经证明；实际是 host-dispatched acquisition、review、construction 和 coordinator execution。
2. **目标 metadata 更完整。** 最新明确 Chinese adults、2009 era、35–74、selection 和 glucose measurement。旧 live assignment 的 geography/era 不完整。必须给未来所有 case 完整 metadata；不能给旧结果补写“作者当时已知”。
3. **联合证据/分析含义审查更突出。** 11/4 强调研究问题对应的 joint/subgroup evidence、调整集兼容性，以及 law 对 intended analysis 的含义。最新 sensitivity 把一个未提供的 dependence 与条件 BMI projection 联系起来。它是 pre-generation 模型分析，不是事后 target-based repair。Main study 已有数值 uptake 和 finite-moment review，不能把这两点说成 11/4 首创。
4. **信息条件与反馈阶段不同。** Main study 可以不做 trial 即 initial-final；IA 有额外阶段和 R reference feedback；最新运行 review 了 trial 和全部 initial deliveries 后 retain。不同机会、预算和输入会影响行为；不能将全部 retained 案例混成一个 revision-benefit experiment。
5. **evaluation 不同。** Main study 各 3 focal regressions；最新 primary/secondary 两回归全系数与相关/分布；M10 有曲率和 sex×BMI；HRS 是 repeated-effects model；Wave A 有 frozen resolution gate。统一画风不意味着共同 endpoint 或同一个“通过率”。
6. **source replay 不是版本身份要求。** [11/4 diagnosis](../agent_diagnosis_2026-11-04/DECISION.md) 明确撤销“先补 replay 才继续”的优先级。缺 replay 不是已证明的误差原因；允许 analytic implication、approximate source comparisons 或 unavailable。把所有 case 重跑 source populations 既不是必需，也不能补上不存在的 joint evidence。

因此，真正需要补齐的是**将当前流程的边界、author contract、输入政策、审查和评估写成一个面向新批次的统一可执行版本**，不是把所有旧数字重新算一遍。不同法则和 case-specific evaluators 可以保留，只需冻结其适配契约。

## 5. 什么时候只需重算评估

| 改动 | 正确处理 | 不需要做的事 |
|---|---|---|
| 图表版式、单位显示、种子/作者汇总顺序 | 优先从已审计 aggregate 计算新显示；检查 provenance 和分母 | 不重新生成或拟合患者数据 |
| 新增共同指标，但旧 aggregate 已足以代数推得 | 新建 analysis-only 输出并标为 post hoc；独立核对 | 不覆盖原 report，不伪称原预注册 endpoint |
| 新指标需要 frozen generated rows | 后续另定 evaluation-only 协议，复用原输出、全作者/全种子，禁止 retuning；本审计未执行 | 不以新生成替代旧表，也不使用结果决定保留种子 |
| evaluator 实现错误 | 先定位受影响的统计量，再对必要输入统一重算、保留旧错误版本和修正说明 | 不自动重建没有受影响的生成表 |
| source parser/model-spec 数字错误，改变实际 law | 新 repair release，仅修正原文可核实内容；受影响构造才需新生成，旧失败保留 | 不借修复改结构、加 seeds 或改目标；HRS 已完成这种处理 |
| 证据包、任务信息、scientific law、审查或 feedback opportunity 变更 | 新科学构造、新版本、新 freeze；另存历史比较 | 不把它叫原模型的“重复评估” |

当前指定批次中，没有发现尚未修复而迫使整套数据全部重生的共同错误。最新控制器/harness 的文件哈希与冻结记录一致；HRS 已有独立且闭合的 parser repair。这个结论不等于新一轮完整代码/环境认证。

## 6. 最小有价值的统一新批次建议

### 6.1 论文现在可以直接推进，不把全量重跑设为写作前提

可以用当前最新单元说明完整 evidence-to-data 链，用 main study 回答“额外 relational evidence 是否改善预定分析”，用 IA 回答 reference information/追加诊断的限制，用 HRS 展示纵向 reconstruction。M10、Wave A 和早期数学/实施失败完整保留为模式范围及适用边界。各单元明确版本，已经足以写一个诚实的、分层证据的当前论文草稿。

这种写法不能支持“全历史案例均由最终统一系统生成”“当前版本在全部模式已验证”“自主搜索/修订造成普遍收益”。如果坚持这些更强主张，增加针对性新实验，而非消除历史差异。

### 6.2 条件缺口：若坚持新版开放检索流程跨 case 泛化，才考虑小统一批次

**当前不实施。若更强主张不能删减，可供以后冻结的最小新设计为：两既定 whole-cohort cases × 每 case 两位 fresh scientific authors × 三个 final seeds = 12 final tables；每作者最多两个总 exploratory row-producing attempts，整个批次最多 20 次 physical attempts。** 这是条件规划，不是已有授权 release，也不是统计功效充分的 treatment-effect design。实际成本主要是证据适用性、科学作者和审查，不能用 12 个表宣称 12 个独立人群。普通核心 procedure 的两人群应用已有 main study，不需要用此批次重复证明。

选择这两例的预先理由是它们共用 biomarker family、都有闭合的 case definitions、单位映射、analytic source operators 和既有 aggregate reference；ENSANUT 保留不同 selection/weighting，能检验必要的适配。该选择不依赖它们过去哪条效果更接近参考。两 case 全部结果、所有 author、全部种子和缺失/失败必须报告。

共同冻结内容：

- 一个 task-to-author contract：population/era/measurement、intended analyses、source roles、joint evidence gaps、assumptions、finite moments、law-implied analysis 与实际干预记录；不要求特定 family 或方向。
- 一个信息制度：选择**固定既有原文 corpus**还是**允许有边界的开放 gap search**，两 case 一致。若固定 corpus，只声称当前构造/审查流程复用；不能借已有一次 open-search 结果声称新批次独立完成了开放检索。
- 一个诊断和停止制度：最多两个 trials，允许一次有根据的 revise 或 retain，final decision 后才产生三 final deliveries；retention 不重复计表。若必须沿用最新“先三 initial deliveries、再 final”设计，应重新冻结更大的预算，不能把两种 allocation 混称相同。
- case-specific evaluator：CHNS 回归/单位与 ENSANUT eight-cell weighted analyses 分开；共同报告 intended effects、uncertainty role、marginal/joint discrepancies、unavailable 和 intervention burden。不造跨单位总分，不用事后 equivalence threshold。
- all-author/all-case closure barrier：全部构造和预定 final attempts 完成后，才统一读取旧 aggregate references。目标早已 researcher-exposed，故只能是 **developmental repeated application**；fresh author context 不能恢复独立临床确认。
- 同时冻结 model/provider 可见身份、生成/评估运行环境、输入与控制器哈希；不可观测 token/cost 记 unavailable。预算失败照扣，不补有利作者或种子。

如果将来仅增加一个实例，ENSANUT 可提供当前流程的不同人群 demonstration，但不能与现有 CHNS 一作者单元合称一个 balanced replication experiment。两 case 同一新 release 更清楚；两种方案都不是本轮默认待办。

### 6.3 何时才扩展到其他案例

- **跨 biomarker/区域泛化成为主结论时**：Wave A 两例应作为预先指定的 paired extension 进入新批次；不需要事后追求通过旧阈值。先确认 sparse evidence 和 unsupported operators 可以如实进入 current contract。它们不是“必须修好的两个坏 case”。
- **当前 enrichment 支持成为主结论时**：M10 NHANES/PNS 另做同模式批次。必须选择和审查适用的 source-feedback adapter；保持 observed cells、NHANES design variance 和 PNS timing/weighting。不能让 current whole-cohort v1 默认为 enrichment 已支持。
- **longitudinal request integration 成为主结论时**：先做无临床生成的 HRS request/schema/evaluator 适配；现有 HRS 已能支持 reconstruction 能力，不优先重复其 46,036-row generations。
- **search/revision 的收益成为主结论时**：需要冻结同信息/同预算且能分离 author 和 intervention 的新比较；历史 main/live/latest 三阶段不是其对照。上述 12-table repeat demonstration 本身也不是因果消融。
- **fresh clinical confirmation 成为主结论时**：这里审计的所有目标已暴露，不能靠重跑、换 outcome 标签或新 author 达成；[既有 reference feasibility audit](../../manuscript/EXISTING_REFERENCE_FEASIBILITY_v07_2026-11-03.md) 仍未准入新的独立 target。本报告不新增获取或 admission。

## 7. 可用资产、代价和实际限制

以下“可用”是已有 metadata/source/code 或路径存在，未重读患者数据，也未在本次重新加载 runtime。

| 任务 | 已有资产 | 可复用的数值工具 | 关键限制 / 追加工作 |
|---|---|---|---|
| CHNS | main E0/E1 packets；latest 5-study originals/ledger；`evcBuild01` source admission；两个任务的既有 aggregate reference | Jansen covariance projections、Bao Pearson calculations；现有 regression/diagnostic analyzers；latest declared-law moment/sensitivity scripts | 新 5-paper packet 不自动适用于所有目标；MIND rank 不由普通 moments 识别；年龄/性别/transport/measurement assumptions 必须保留；不得用 now-exposed reference 补未知 dependence |
| ENSANUT | main E0/E1 sources、case card、task、analysis definitions、已有 aggregate reference | `source_operators.py::source_projection`；Pani/Jansen adjustment-aware projections；equal-cell analyzer | 3,000 rows = 每 8 个 age/sex cell 375；serum/plasma、selection、Pani survey weighting、≥70 source upper support 未完全解决；最新 request B runner 需适配，不能只改路径 |
| NHANES/PNS | M10 frozen specs、source packets、launch/campaign records；两 observed paths 在本地存在 | 原 enrichment source replay 与统一 scientific analysis；NHANES full-design Taylor variance；PNS weighted/unweighted analyses | 最新 semantic feedback 未覆盖模式；本次未读 rows/验证 data hashes；PNS 无 PSU/strata，不能补造设计 CI；未来生成必须明示与 whole-cohort 不同的信息输入 |
| HRS | public source commit `6708e43…`、修复后的 source-bound comparator、原 Agent、native evaluator、项目本地 R packages | R 4.3.3/lme4 1.1-35.1、REML/bobyqa；conditional GLS checker | 非原 R 4.0.1/lme4 1.1-23 的 bitwise replay；需要特定 longitudinal adapter；本次只确认 runtime 目录存在，未加载 R |
| HAALSI | 原 DUA/access metadata、schema、frozen Wave A case、原数据路径存在 | 原 glucose analyses、MIND/Ayele/Bahendeka context summaries、专门 source descriptives | Ayele/abstract Bahendeka 不给连续 glucose slope；POC 与 serum/fasting transfer 未识别；既有 MIND 数值不等于 HAALSI 可移植系数；strict 与 approximate 应分开 |
| Turkana | 原 admission/schema、Greiner packet、unit mapping、Wave A frozen artifacts | six-context descriptive comparisons，原 lipid/partial-regression evaluator | semantic v1 不支持 geometric mean；unknown source weighting；raw/log regression 映射未定；conditional lipid dependence 仍有假设；不能从 source CI 推个体 SD |

生成环境记录以 WSL Ubuntu-24.04、Python 3.12.3、NumPy 2.4.5、pandas 3.0.3、bubblewrap 为核心；latest `RUNTIME_PREFLIGHT.json` 和 M10 记录一致。Wave A 为 SciPy 缺失保留了初次软件失败，之后固定 isolated SciPy 1.16.3；host analysis 使用过 SciPy 1.17.1，两者不能合称同一 runtime。Main analysis 另记录 Windows Python 3.12.10。新的 release 应重新做必要的软件 preflight 和 hash verification，不能因旧 JSON 存在便声称现在仍可执行。

无需训练、HPC 或新增付费 API 来完成上述最小设计。文献开放检索若被选入新设计，才产生新的检索/下载工作；固定本地 corpus 方案可避免新增取得原文，但缩窄相应自主检索主张。HRS 额外 native mixed models 比普通横断面评价更重；Wave A 和 M10 的主要成本是异质 metadata/operator 适配，不是抽样行数。审计没有测得 wall-time 或货币成本，故不提供伪精确成本预测。

## 8. 可直接用于稿件的版本表述

> We evaluate a shared evidence-to-data procedure through separately frozen experimental releases. Scientific models, admitted information, feedback opportunities and evaluators were task specific. Earlier enrichment and transport studies are retained as historical evidence and failure boundaries; they were not retroactively relabelled as executions of the latest workflow. The latest reviewed-evidence construction demonstrates the current integrated process on an exposed developmental reference. Cross-release differences do not identify a causal benefit of retrieval or revision.

论文主线可集中于：**Agent 对研究任务进行实质科学构造；同一数据的不同分析用途可表现不同；显式 joint-evidence gap 会影响目标分析；过程能够执行并被审计。** 同时保留 main study 的反例、追加 revision 的 no-op、Wave A 的 negative gate、HRS parser incident、来源适用性及有限矩问题。本轮最有价值的新增工作是把这些已完成证据统一到准确的聚合表、图和稿件；只有选择超出这些证据的新版跨 case 泛化主张时，才需另行讨论有限新批次。

本文件不替换 v0.8、旧 protocol、release、结果、exposure registry 或任何 claim lock。后续是否实施新批次应由主任务的具体目标与单独冻结设计决定。
