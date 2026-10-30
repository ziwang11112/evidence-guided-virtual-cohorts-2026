# 文献驱动虚拟生物医学数据：研究分析与 Agent 系统设计

**版本：设计草案 v1.0｜日期：2026-10-30（UTC）**

**状态：方法与工程设计建议。尚未实现本设计中的新增模块，尚未运行新的真实队列实验。**

本设计沿用已经确认的总问题：

> 将发表文献中分散的证据，转化为可复用的虚拟生物医学数据，缓解真实数据与指标不足，并验证这些数据能够支持哪些科学分析。

代码核查基于仓库 `ziwang11112/evidence-guided-virtual-cohorts-2026` 的固定提交 `d33d0cbad4c199fe5b450688fe8050d72afd9861`。本次工作包括相关实现、既有结果和公开方法文献的审阅，以及新案例的文献和元数据筛选；没有修改仓库，没有下载或分析新案例的个体目标数据。公开队列代码本会包含部分结果摘要，因此不能将本次筛选称为“从未接触任何目标相关信息”；后续须记录暴露范围，并给生成方提供经过筛选的元数据。

---

## 1. 总体判断与推荐决策

方向可以继续推进。应用问题已经足够清楚，下一阶段的瓶颈是把“正确使用发表证据”变成可执行的方法，并获得独立真实数据上的分析证据。

推荐默认架构：

> 一个科学 Agent ＋ 确定性 Controller ＋ 来源分析算子 ＋ 数值校准工具 ＋ 可冻结的随机生成器。

Agent 解释文献、选择结构、提出修订；统计程序完成拟合和检验；Controller 管理版本、预算、状态与冻结。无需先建设多个常驻 Agent。独立复核角色只在具体错误风险值得额外检查时调用。

推荐首个方法重点：

> 在每项来源研究的适用人口、测量尺度和分析定义下，重现该研究发表的统计量，用这些计算约束生成器，再将冻结生成器应用于目标队列。

这使方法有一个明确的科学中心。证据缺口检索、候选保留、来源追溯和用途说明都服务于生成与科学分析，暂不发展成互相竞争的多个研究主题。

首阶段的产物是**个体级分析表及其生成配方**。测序 reads、原始影像、仪器波形等需要另建测量过程模型，不能由本阶段对临床表格的验证自动覆盖。

## 2. 三种用途怎样统一，怎样分别验证

| 用途 | 统计目标 | 可以复用的内核 | 必须新增的依据 |
|---|---|---|---|
| 整列指标增补 | 目标只有 X，生成 Y 条件于 X | 证据解释、来源算子、校准、生成与冻结 | 来源到目标的关系与基线迁移假设 |
| 部分缺失补充 | 使用已观测的 Y，填补缺失单元 | 同上，并加入目标内部信息 | 缺失机制、观测部分的选择性、适当的不确定性传播 |
| 完整虚拟队列 | 同时生成 X 与 Y | 同上，并生成协变量分布 | 目标人口结构、X 的联合分布、更多指标之间的依赖 |

模式枚举可以现在保留，但“接口能接受该模式”不能当成“已验证其科学能力”。当前应完整实施整列增补，再逐项扩展。

合成 10 万行可以降低模拟误差，却不会创造 10 万个新观察对象。下游分析的精度必须区分真实来源的信息量、模型假设和模拟规模。

## 3. 首个任务的正式定义

令：

- 目标可见协变量为 $D_T^X=\{x_i\}_{i=1}^{n_T}$；
- 待增补指标为 $Y$，生成阶段整列不可见；
- 第 $s$ 项来源研究报告统计向量 $\widehat t_s$；
- $\nu_s$ 描述来源人口、选择条件、测量方式、时间与协变量分布；
- $\lambda$ 表示模型结构，$\theta$ 表示可拟合参数；
- $G_{\lambda,\theta}$ 为随机生成器。

目标输出为：

\[
\widetilde Y_i=G_{\lambda,\theta}(x_i,\epsilon_i).
\]

来源约束为：

\[
\widehat t_{sk}\approx T_{sk}(G_{\lambda,\theta},\nu_s).
\]

$T_{sk}$ 的含义是：在该来源的条件下生成数据，再执行该来源对应的分析。例如，原研究报告调整后的回归系数，算子就应拟合同样的回归公式、变换、调整集和权重，然后抽取相同系数。

目标真实 $Y$ 不进入拟合。独立评价在生成器冻结后，对真实表和增补表执行相同分析：

\[
A_j(D_T^X,Y_T)\quad\text{与}\quad
A_j(D_T^X,\widetilde Y_T).
\]

成功应按事先定义的用途判断。不能把某一相关系数接近、来源损失较低或 Agent 自信，概括为“虚拟数据真实”。

## 4. 真正困难的四个问题

### 4.1 发表统计量与生成参数不是同一对象

来源均值是来源人口混合后的结果，通常不等于某个参考个体的条件均值。调整后的斜率依赖调整集、变换、选择和模型形式。

| 发表内容 | 正确操作 | 常见错误 |
|---|---|---|
| 均值、SD | 在来源人口生成后计算同样的均值、SD | 直接当作目标截距与条件残差 SD |
| 中位数、分位数 | 对来源混合分布计算相同分位数 | 直接指定给“平均年龄、平均 BMI”的个体 |
| 相关系数 | 用原变换计算 Pearson 或 Spearman | 直接当成回归斜率 |
| 调整后系数 | 重现公式、调整集、权重与编码 | 混合不同调整集后平均或复制系数 |
| 分层统计 | 重现分层与组内分析 | 由男女均值差推断男女 BMI 斜率差 |
| 阈值比例 | 在对应尺度和纳入条件下计算 | 用任意截断掩盖尾部失配 |
| 纵向关系 | 建立相应时间结构 | 当成同期横断面关系 |

如果原回归调整了额外变量 L，而目标只有 X，不能把其系数自动转成 $Y\mid X$。需要额外的 $L\mid X$ 信息和相应模型；首版可以将此类数值约束暂列不可计算，只使用合格的较简调整模型或明确的结构线索。

### 4.2 来源人口也存在未知部分

论文通常不提供完整的 $P_s(X)$。来源重建可以利用分层比例、边缘分布和已报告的联合统计，但没有报告的相关性不能自动设为零后标成“复现成功”。

来源协变量应有独立规格：

- 直接报告的部分；
- 经过合法换算得到的部分；
- 由校准得到的部分；
- 仍需假设的部分。

未知年龄—BMI 依赖可以形成少数明确情景。不能允许优化器随意改变这些依赖，只为让生成器更接近发表结果。

ML-NMR 已提供利用来源协变量分布连接个体模型与汇总证据的方法基础；本设计借鉴其思想，但不自动继承其推断保证。[2]

### 4.3 目标基线需要明确迁移依据

若每个来源都有任意截距或任意检测偏移，而目标完全没有 Y，来源拟合不能识别目标的绝对水平。

首版必须选择并记录：

1. 一个兼容来源作为参考，并声明相应关系或基线迁移；
2. 有依据的来源—目标测量桥接；
3. 或若干明确的基线迁移情景。

物理单位换算不等于检测方法校准；检测方法校准也不等于跨国家、跨选择标准的人口迁移。

若没有可辩护的锚点，可以研究某些形状或相对关系，但不能宣称已恢复目标均值、分位数和阈值比例。

### 4.4 部分关系吻合不能保证任意后续分析成立

如果生成器只学到 $Y\mid X$，随后用户研究 Y 与另一个变量 Z 的条件关联，而模型从未接触它们的联合信息，那么独立生成的残差可能自动施加 $Y\perp Z\mid X$。

统计匹配研究明确指出，这类未共同观察的关系可能不可识别，条件独立假设会决定而非估计相关结构。[3]

因此，可复用性需要在明确范围内验证。首轮可覆盖主效应、曲线形状和分层关系；加入新的结局、多个指标或因果问题时，必须重新检查所需联合结构。

## 5. 与既有工作的关系和可主张的贡献

G-Sim 已包含 LLM 提议模拟器结构、数值校准和反馈修订；其作者全文也讨论了多个相容结构。因此，“LLM 写代码＋优化器调参数＋Agent 反思”不能单独作为新颖性依据。[1]

ML-NMR 和统计匹配已经建立来源人口积分、汇总证据融合、整列合成增补和可识别性方面的基础。[2–3]

建议把项目贡献分成三个层次：

| 层次 | 建议定位 | 目前证据状态 |
|---|---|---|
| 应用问题 | 将发表证据转为可复用的虚拟生物医学数据 | 方向已确定 |
| 主要方法候选 | 将不同定义的来源统计编译成可执行约束，处理人口、测量和调整条件 | 需实现并检验 |
| 后续机制候选 | 按来源失配与分析敏感性触发定向补证或科学修订 | 需单独显示收益 |
| 配套能力 | 版本、来源追溯、情景输出与冻结复用 | 必要工程，不宜全部包装成算法创新 |

论文可以先证明一个完整实例和其科学用途。若要声称某个机制改善结果，则增加同信息条件下的比较或消融。不能因方案具有多个组件就预先认定为新的方法论贡献。

## 6. 推荐系统架构

~~~mermaid
flowchart TD
    I["任务、可见协变量、来源文献"] --> C["Controller：状态与版本"]
    C --> A["科学 Agent：解释、建模、修订"]
    A --> E["证据卡与来源分析算子"]
    E --> F["数值校准与来源重放"]
    F --> D{"诊断与下一步"}
    D -->|"定义或结构需修改"| A
    D -->|"缺少具体证据"| R["定向检索"]
    R --> E
    D -->|"可保留或预算结束"| B["冻结生成器与情景"]
    B --> G["生成并交付增补数据"]
    B --> V["独立真实数据评价"]
    G --> V
~~~

图中独立评价只用于研究验证，不返回同一确认案例的生成循环。真实部署没有隐藏的真实 Y 可供评价。

| 组件 | 责任 | 主要输出 |
|---|---|---|
| Controller | 工具调度、状态、预算、版本、冻结 | 运行状态和发布包 |
| 一个科学 Agent | 证据解释、候选结构、失配诊断、定向检索建议 | 结构规格和科学决定 |
| 统计工具 | 来源上下文、分析算子、校准、重放、敏感性 | 可重复的数值报告 |
| 可选复核调用 | 核查明确的统计语义错误或不合理迁移 | 有证据定位的问题清单 |
| 独立 evaluator | 冻结后真实与生成数据的同定义分析 | 外部科学表现 |

同一个 Agent 可以依次扮演文献整理者、建模者和修订者。阶段提示词、可见材料和工具集合不同，无需把它们变成常驻角色。

工程上使用普通 Python 模块和 provider adapter 即可；不必先采用特定多 Agent 框架或训练基础模型。

## 7. 数据契约：每个科学决定必须落到对象上

建议保留以下对象；新字段使用新版本或带校验的 sidecar，不修改旧版严格 schema 的含义。

### 7.1 TaskSpec

包含任务模式、可见变量、待生成变量、单位、人口、测量时间、允许用途、来源排除规则和预算。复杂抽样的权重、PSU、strata 作为保留列管理；是否用于生成和来源分析须分别声明。

### 7.2 EvidenceCard

至少包含：

- 论文、研究和队列标识；
- 原文表格、图、段落定位；
- 统计量种类、值、单位和变换；
- 不确定性、样本量和分析样本；
- 暴露与结局方向；
- 调整变量、编码、分层、权重；
- 来源人口、选择条件、测量方式和时间；
- 同队列依赖分组；
- 提取状态与准入用途。

用途枚举建议为：calibration、source_check、qualitative、unusable。不能把所有抽取到的数字都自动写进优化目标。

若原文正文、表格和图注相互矛盾，应生成可定位的问题记录，重新核查；未解决前不能任意选择有利的一项。

### 7.3 SourceContextSpec

独立定义来源 schema、纳入条件、协变量分布、未知依赖情景及测量映射。它不继承目标的年龄范围或其他人群限制。

来源 eligibility、目标 eligibility、模型 computational domain 是三个不同概念。如果来源在模型定义域外，应限制该来源的使用或扩展模型并说明依据，不能静默裁剪来源。

### 7.4 AnalysisOperator

把来源分析定义编译为受限操作：单位换算、变量变换、编码、筛选、分层、统计计算。先支持 mean、SD、quantile、correlation 和清晰定义的线性回归；复杂模型逐项增加，不伪装成现有能力。

### 7.5 GeneratorSpec 与 AssumptionRecord

每个参数标记为 reported、derived、calibrated 或 assumed，并连接证据与假设。

参数分为：

- 固定值：来自明确单位转换或预定常量；
- 拟合参数：由来源约束优化；
- 情景参数：当前信息不能识别，不能伪装成拟合结论。

### 7.6 CalibrationSession

冻结一次数值拟合的模型结构、代码、参数边界、来源上下文、算子、损失、随机化计划和数值预算。内部 θ 试探单独计数，完成后产出正式候选。

### 7.7 ScientificDecision / ScientificPatch

记录触发问题、证据位置、动作、修改对象、预期改善的来源统计和受影响的下游分析。必须保留失败记录和保留原样的理由。

### 7.8 ReleaseBundle

固定生成代码、参数、证据版本、上下文情景、算子版本、决策记录、随机化计划和执行依赖。发布之后任何影响输出的修改都产生新版本。

## 8. 默认科学算法

### 8.1 选择小而可解释的模型族

首版针对一个连续指标，采用：

\[
h(Y)=m_{\lambda,\theta}(X)+\sigma_{\lambda,\theta}(X)\epsilon.
\]

候选可以包括线性、低自由度平滑项和少量有依据的分组斜率；残差先采用简单分布，只有来源证据需要时再扩展异方差或混合结构。

选择 h 时考虑指标支持集和已发表变换。来源在原尺度报告统计时，必须回到原尺度计算，不能把 log 尺度参数直接比较。

候选库面向变量类型和分析结构，不写死“BMI 对胰岛素一定是某种函数”。禁止看过目标答案后为该案例硬编码一个斜率。

### 8.2 构造来源上下文情景

每个来源保持已知边缘和分层约束。对未报告依赖，优先获取文献中已有信息；仍未知的部分形成少数可解释的情景。

情景不是随意画出的“可信范围”。若不能给出有根据的范围，应报告该方向缺乏约束，而非制造狭窄区间。

多个来源情景采用少量整体组合，避免无控制的笛卡尔展开。

### 8.3 数值校准

对来源 s 的统计 k：

\[
r_{sk}(\theta)=
\frac{T_{sk}(G_{\lambda,\theta},\nu_s)-\widehat t_{sk}}{a_{sk}}.
\]

其中 $a_{sk}$ 是事先规定的尺度，可由来源 SE 或有单位的拟合容限定义。四舍五入误差、来源抽样误差和 Monte Carlo 误差分别记录。

一个可实现的默认目标为：

\[
L(\theta)=
\sum_s\frac{1}{K_s}\sum_{k\in s}\rho(r_{sk}(\theta))
+\lambda_C C(\theta).
\]

ρ 可采用 Huber 损失；复杂度惩罚及其系数若使用，须事前声明并做相应敏感性说明。存在可靠的统计量协方差时，可以使用来源分块的协方差加权。

这个默认目标是数值匹配准则，不是自动有效的似然。来源内归一化只是减少“发表更多统计量的研究”对目标的支配；它不能消除统计相关性，也不能提供正确的后验。

拟合时固定来源抽样和残差随机数，减少优化目标的随机抖动；拟合后用新的随机数重放，检验是否只是适应了某一次模拟。

只增加模拟人数不能提高来源研究的精度。若数值误差仍足以改变结论，应先增加计算或报告精度不足。

### 8.4 按原因诊断失配

| 诊断 | 检查内容 | 允许动作 |
|---|---|---|
| 提取错误 | 数值、符号、单位、每 SD 或每单位 | 重新核查原文 |
| 分析映射错误 | log、调整集、分层、编码、权重 | 修改算子并重新校准 |
| 数值不稳定 | Monte Carlo、局部最优、边界 | 增加适当计算或换预定优化设置 |
| 来源上下文不足 | 边缘、相关、选择与测量 | 补证或增加明确情景 |
| 参数失配 | 结构能表达但尚未拟合 | 重新拟合参数 |
| 结构不足 | 候选族无法同时满足关键统计 | 有依据的科学结构修订 |
| 迁移冲突 | 来源间关系不能共同解释 | 分层情景或限制适用范围 |
| 信息不足 | 多种解释同样相容且用途结论不同 | 保留分歧、定向补证或停止该用途 |

不能通过无限放宽来源误差、删掉不利研究或添加任意来源截距来让所有候选“通过”。

### 8.5 定向补证

在没有目标 Y 的情况下，比较相容候选对预定分析的输出。如果结果差异主要来自某个假设，Agent 找出能约束该假设的具体统计量，再发起中性的检索。

例如，候选在 sex×BMI 分组斜率上不同，应寻找分层斜率或相应联合统计，不能用更多男女均值替代。

检索目标是缺失统计对象，不是希望得到的效应方向。新增来源须重新经过准入。检索失败也需要记录。

更复杂的局部 Jacobian 敏感性诊断可以以后增加，首版不要求实现，更不能把它称为全局可识别性证明。

### 8.6 保留相容候选与停止

来源检查不能唯一决定模型时，保留少数预先限定的结构和情景。输出范围仅反映已检查情景，不是后验概率或完整识别区间。

停止条件包括：满足预定来源要求且没有具体修订依据；关键矛盾仍无法解释；需要的联合信息不可得；或预算耗尽。

“没有相容生成器”“相容但目标迁移未知”“部分分析得到支持”是不同结果，应分别报告。

## 9. 不确定性与数据复用

至少区分：

1. 发表估计的抽样不确定性；
2. 来源协变量重建不确定性；
3. 模型结构的不确定性；
4. 测量与人口迁移假设；
5. 固定模型下的个体残差；
6. 目标真实参考分析自身的抽样误差。

每张表记录：

~~~text
release_id
hypothesis_id
source_context_scenario_id
transport_scenario_id
parameter_draw_id
residual_seed
~~~

不能把不同情景的行拼成一个更大的样本，也不能未经推导就用普通多重插补规则合并它们。

同一冻结发布包应用于多个后续分析时，不因看到各项真实答案而逐项换生成器。可以公布一个预定主情景并附敏感性情景，也可以并列交付多个相容情景，但必须保持分析可追溯。

“多种情景都同意”仍可能存在共同偏差；“多次残差生成很稳定”也不能说明迁移假设正确。

## 10. 当前代码能复用什么，优先改什么

审阅位置：固定提交中的 `biomedical_research/virtual_cohort_system/`。[R1–R6]

### 已有基础

| 文件或模块 | 已有能力 | 解释边界 |
|---|---|---|
| contracts.py | 三种任务模式与输入输出结构校验 | 结构校验不能判定科学意义正确 |
| lifecycle.py | 候选冻结、哈希与 lineage | 需区分正式候选与校准内部 trial |
| execution.py | 执行冻结生成器和核验 | 现有生成器隔离不等于完整 LLM 工具隔离 |
| literature.py | 任务绑定的来源检索与记录 | 不等于自动完成科学修订 |
| source_checks.py | 部分基本统计与 OLS 系数检查 | 变换、编码、权重等不能隐式假定 |
| source_replay.py | 在来源输入上执行候选并检查 | 当前只覆盖特定 enrichment 程序路径 |
| source_portfolio.py | 汇总、比较来源检查 | 没有自动证明目标有效性 |
| analysis_evidence.py | 用途、证据、假设、缺口与行动声明 | 声明不等于动作已完成或用途已获验证 |

### 必须优先解决的两个接口问题

**问题一：来源与目标的人口契约尚未分离。**

现有 `source_replay._input_task` 复制目标 task，仅修改 population 和 n_rows，再验证来源表。来源因而继承目标范围和类别。来源老人年龄分布若超出目标上限，就可能被迫截断或无法重放。

改法：新增独立 SourceContextSpec；分开来源纳入、目标纳入和模型计算域；增加显式变量与测量映射。不能以放宽目标任务的边界来修复来源语义。

**问题二：数值校准尚无独立执行契约。**

现有 `run_candidate` 要求 frozen candidate。修改 model_spec 会使 freeze 失效；正式 parent-linked candidate 受 revision 预算约束。

改法：新增 CalibrationSession。先锁定结构与优化计划，记录数值 trial，完成后把拟合参数物化为正式候选并冻结。数百次数值试探不能被当成数百次科学修订，也不能在冻结文件上原地改参数。

新增算子和 sidecar 必须配合语义与结构校验。仅把文件列入 hash 只能证明字节未变，不能证明内容合法。

历史 v1 运行和 receipt 依赖旧实现，须保留验证路径；不能静默替换引擎后声称历史结果由新方法产生。

## 11. 既有 M10 结果提供了什么信息

既有实验包含整列胰岛素和 HbA1c 增补，每个任务两次科学构建，每个构建三次残差输出。它们不是 12 个独立生物学任务。[R2]

源代码与结果给出三个方法设计线索：

- 部分主效应可被保留，但分组斜率和曲率更脆弱；
- 胰岛素候选的 BMI 响应主要共用于两性，不能仅凭 sex 截距保证分组斜率；
- HbA1c 候选的 BMI 作用中存在明确假设，不能把相应正向结果全部算作文献证据转译的成功。

未显式写入交互，不意味着任何分析投影下交互估计必然严格为零；它意味着该关系没有得到有针对性的建模与证据约束。

这些既有目标已经用于开发，适合诊断和回归检查。新的确认实验不应在看到目标结果后反复修改同一生成器。M10 的来源包是 curated，选定生成器未发生科学结构修订；因此它尚不能证明自动补证或反馈修订的收益。

## 12. 下一完整实例：尿酸增补候选

### 12.1 选择状态

建议将 **NHANES 2017–2018 血清尿酸整列增补**列为优先候选，而非现在宣称已经完成的新实验。

官方 BIOPRO_J 文档提供尿酸变量 `LBXSUA` 及 SI 单位等价变量 `LBDSUASI`。构建方应同时屏蔽这两列及直接派生标签，防止通过等价测量获得目标答案。[4]

公开元数据还提示检测平台变化，说明测量兼容性需要显式管理。平台桥接只适用于有文档支持的对应测量系统，不能拿来自动校准所有外部国家的检测。[4]

当前归档筛选在固定提交的路径、31 份 README/MILESTONE 报告和相关证据记录中未发现尿酸既往使用；这不覆盖其他分支、未归档会话或本地探索。因此状态为 freshness_pending。

这个案例是方法验证载体。不能因为选了一个公开常规生化指标，就宣称已量化节约昂贵检测的成本。

### 12.2 Agent 的可见输入

建议起始可见协变量：年龄、性别、BMI；人口年龄范围在来源准入后确定，例如优先考虑与主要来源重叠的成人范围。保留样本标识和适当的抽样设计字段。

Agent 收到：

- 仅含允许协变量的数据或其摘要；
- 经筛选的变量字典与测量元数据；
- 预定的科学使用范围；
- 外部发表原文及准入规则；
- 有限的检索和修订预算。

首次研究中可使用人工准备的原文包，让 Agent 完成解释与生成；若以后声称自动检索能力，则另行评价检索覆盖和来源准入。

### 12.3 已找到的来源与应采取的动作

**Koo 等的韩国一般人群研究**报告按年龄与性别的尿酸分布，可作为来源分布和分层统计的候选证据。它不能自动提供美国目标人口的绝对水平。[5]

**Zhou 等的中国研究**报告 BMI 与尿酸的线性和非线性关系，并调整多项额外变量。Agent 应核查原表、调整集和尺度；如果只有 age、sex、BMI，就不能直接把充分调整后的斜率写进目标模型。[6]

该论文网页的部分正文对关联方向的措辞与带符号的数值呈现不一致，这恰好说明“抽到数字”之后仍需核查原表、图注和定义。未解决的证据应留作待核查，不得自信选择。

### 12.4 一个可执行的候选结构

~~~text
h(uric_acid) =
    intercept
  + sex_effect
  + age_function(age, sex)
  + bmi_function(BMI)
  + optional_sex_by_bmi(BMI, sex)
  + residual
~~~

这只是模板。h、函数复杂度、是否保留交互、参数范围均由合格证据和显式假设确定；这里不填入未经校准的“真实系数”。

可比较两个低复杂度候选：共同 BMI 响应，以及允许分组 BMI 响应的情景。后一项若缺乏足够联合信息，不能被称为已估计。

### 12.5 完整实例必须展示的过程

1. 展示具体允许的 X 和来源包；
2. 展示每条证据如何进入校准、来源检查或定性线索；
3. 构建来源人口和迁移锚点；
4. 在固定结构下数值校准；
5. 展示失配诊断和实际采取的行动；
6. 冻结候选和情景；
7. 用同一发布包生成数据并执行预定分析；
8. 独立 evaluator 揭示目标参考后，报告成功、失败及不确定结果。

如果缺少可用 BMI 联合证据，应在查看目标结果前补证或缩小该分析的支持声明。不能因为希望尿酸案例成功而事后补入目标斜率。

### 12.6 可预定的分析

| 分析 | 作用 | 解释要求 |
|---|---|---|
| age、sex 调整后的 BMI 关联 | 主要科学关系 | 来源调整集和目标估计量必须明确 |
| 年龄曲线或 sex 分组曲线 | 同一生成器的复用分析 | 至少一项不直接作为拟合目标 |
| sex 分组均值、分位数 | 分布与基本关系保留 | 对目标基线迁移更敏感 |
| sex×BMI | 有证据条件下的挑战项 | 无联合证据时允许报告不足 |
| 阈值比例 | 可选探索项 | 对尾部与测量差异敏感，不能超前作临床用途声明 |

最终主次分析应在生成前固定，不必全部列为必须成功。没有实质误差容限时，报告连续误差和参考不确定性，不强行判定“临床可用”。

## 13. 最小验证：先证明实例，再检验新增机制

### 13.1 第一轮必须完成的证据链

**来源使用正确。** 独立核查少量关键 EvidenceCard 与算子；确认没有把边际量当条件参数、没有重复来源计权、没有漏掉调整集。

**外部分析有用。** 冻结后真实与生成数据使用同一分析定义，报告效应大小、形状、分层关系和误差。

**同一生成器可复用。** 至少一个后续分析没有被直接作为来源校准目标，且无需看到真实答案后重写生成器。

来源拟合是构建诊断，独立真实队列评价才提供目标效用证据。二者不能互换。

### 13.2 第一轮的建议规模

以下仅是可调整工程预算，不是统计功效、成本或最佳配置的测量结果：

- 一个新任务；
- 两次独立 Agent 构建，用于观察构建稳定性；
- 每次最多两个候选结构；
- 最多少数整体来源／迁移情景；
- 每候选一次科学结构修订；
- 可选一次定向补证；
- 每冻结情景三次残差输出。

数值拟合另设初值、目标函数调用和模拟精度预算。不要把这些重复当成独立任务数。

### 13.3 何时需要比较组

若只展示完整方法实例，普通 Agent 完成流程是有效起点。

若主张“来源条件编译改善科学表现”，在同一证据、相近表达能力和计算预算下，对照适用的常规统计校准实现。关闭某个来源条件的消融可用于解释机制，但不能冒充强方法基线。

若比较“少证据”和“补证后”，所得差异首先说明新增信息及其使用的价值，不能单独证明算法优越。

不建议为了形式完整先构造大量 Agent 数量、提示词风格和模型品牌排行榜。

## 14. 工程实施顺序与验收

### 阶段 A：修正基础契约

- 实现独立 SourceContextSpec；
- 建立有版本的变量、单位和分析映射；
- 增加 CalibrationSession；
- 保留旧接口与历史 receipt 验证；
- 明确 builder 与 evaluator 的实际工具和文件边界。

验收：来源范围不被目标范围静默改变；单位与调整回归有可核验例子；数值 trial 不修改 frozen 文件；builder 工具无法直接读取参考目标。

### 阶段 B：完成普通 Agent 工作循环

- 实现 provider-neutral Controller；
- 阶段提示、有限工具集合和结构化动作；
- 接入文献原文、证据卡、候选、校准、重放；
- 保存实际科学决定与失败原因；
- 支持有界修订和停止。

验收：从任务和原文包产生一个可运行的冻结生成器，所有关键参数可追溯，失败也能完整交付诊断。

### 阶段 C：新案例冻结与评价

- 完成候选来源准入与既往接触记录；
- 固定分析计划；
- 执行两次构建；
- 冻结并生成；
- 统一评价全部预定结果；
- 输出真实改善、失败和不确定情况。

验收不预先要求所有分析通过。科学验收是结果可信、可解释、可复查；方法有效性的强度由实际表现决定。

### 阶段 D：只扩展得到支持的机制

若来源语义处理确有收益，扩展复杂调整或更多来源；若假设敏感性决定结论，扩展相容候选和针对性补证；若新案例未体现可复用效用，先修正方法或限定用途，再扩展任务数量。

## 15. 必要的验证样例

无需为每个低影响实现细节堆积测试；优先覆盖会改变科学结论的地方：

1. **边际与条件量区别**：手工构造存在协变量混合的样例，检验不能将边际均值直接复制为截距。
2. **调整集区别**：用已知联合分布验证调整与未调整斜率不同，算子能正确区分。
3. **来源范围区别**：来源年龄范围超出目标时，系统既不裁剪来源，也不放宽目标契约。
4. **单位与变换**：原尺度、log 尺度、每 SD 与每单位正确转换并可追溯。
5. **数值精度区别**：增加模拟人数只改变 Monte Carlo 误差，不改变来源样本量或 SE。
6. **冻结与隔离**：输出变化触发新版本；参考数据不可由 builder 工具读取。
7. **行与单元保持**：enrichment 不改变原列、顺序或权重；completion 不能覆盖已观测值。
8. **用途限制**：未知 Y–Z 条件关系不会被报告成已验证关系。

已存在且可靠的分析测试继续复用；不要为了新目录复制同样测试。

## 16. 发布包应交付什么

~~~text
release/
  manifest.json
  task.json
  evidence.json
  evidence_semantics.json
  source_contexts.json
  analysis_operators.json
  assumptions.json
  generator.py
  model_spec.json
  calibration_plan.json
  calibration_summary.json
  source_replay_report.json
  scientific_decisions.jsonl
  draw_plan.json
  data_dictionary.json
  generated/
  analysis_support.md
  reproduction.md
~~~

文件名为建议新增设计。正式实现应与现有 artifact 格式兼容，不应假装全部已存在。

analysis_support.md 说明证据覆盖、假设依赖、已测试和未测试的用途。它是数据交付的一部分，不需要变成另一个独立的质量分类产品。

研究验证的 reference_results 放在 evaluator 侧，在冻结后另行合并展示，不进入 builder 上下文。

## 17. 本轮明确没有完成的内容

- 没有实现或运行新增校准器、Controller 或来源算子；
- 没有生成新尿酸数据；
- 没有查看新案例的个体目标结果或分析目标关联；
- 尚未核定新案例的完整来源包、人口范围与迁移锚点；
- 尚未获得任何新机制改善目标结果的证据；
- 没有证明跨指标、部分缺失或完整虚拟队列能力。

这些属于下一阶段工作，不能在论文中写成已实现结果。

## 18. 推荐下一步

优先实现 **SourceContextSpec、AnalysisOperator 和 CalibrationSession**，把它们接到已有冻结生成器接口上，再用一个普通 Agent 跑完整实例。

第一个实例需要回答的具体问题是：

> 在不给生成方目标指标答案的情况下，Agent 能否正确转译异质发表证据、构建并校准一个可冻结的生成器，使同一份增补数据支持多个预定科学分析；当证据不足时，能否清楚展示结论依赖于哪些假设？

回答这一问题之后，再决定最值得扩展和比较的机制。

---

## 参考资料与代码定位

以下方法论文用于说明统计和系统设计的已有基础，不表示本方案已得到这些工作的推断保证。

1. Holt S, et al. **G-Sim: Generative Simulations with Large Language Models and Gradient-Free Calibration.** ICML 2025. [正式论文页面](https://proceedings.mlr.press/v267/holt25b.html)；[作者全文](https://arxiv.org/html/2506.09272v1)。
2. Phillippo DM, et al. **Multilevel network meta-regression for population-adjusted treatment comparisons.** JRSS A, 2020. [原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7362893/)。
3. **Statistical matching using fractional imputation**, `2 Basic setup. Statistics Canada, Survey Methodology, 2016. [原文方法章节](https://www150.statcan.gc.ca/n1/pub/12-001-x/2016001/article/14539/02-eng.htm)。
4. CDC/NCHS. **NHANES 2017–2018 Standard Biochemistry Profile, BIOPRO_J.** [官方文档](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BIOPRO_J.htm)。
5. Koo BS, et al. **Distribution of serum uric acid levels and prevalence of hyper- and hypouricemia in a Korean general population of 172,970.** Korean J Intern Med, 2021. DOI: 10.3904/kjim.2020.116. [原文](https://www.kjim.org/journal/view.php?number=170514&viewtype=pubreader)。
6. Zhou H, et al. **Nonlinear relationship between serum uric acid and body mass index: a cross-sectional study of a general population in coastal China.** J Transl Med, 2019. DOI: 10.1186/s12967-019-02142-9. [原文](https://link.springer.com/article/10.1186/s12967-019-02142-9)。

**代码引用，均固定在本次审阅提交：**

- [R1：系统 README](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/d33d0cbad4c199fe5b450688fe8050d72afd9861/biomedical_research/virtual_cohort_system/README.md)
- [R2：MILESTONE_10_RESULTS](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/d33d0cbad4c199fe5b450688fe8050d72afd9861/biomedical_research/virtual_cohort_system/MILESTONE_10_RESULTS.md)
- [R3：source_replay.py](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/d33d0cbad4c199fe5b450688fe8050d72afd9861/biomedical_research/virtual_cohort_system/cohort_harness/source_replay.py)
- [R4：lifecycle.py](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/d33d0cbad4c199fe5b450688fe8050d72afd9861/biomedical_research/virtual_cohort_system/cohort_harness/lifecycle.py)
- [R5：execution.py](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/d33d0cbad4c199fe5b450688fe8050d72afd9861/biomedical_research/virtual_cohort_system/cohort_harness/execution.py)
- [R6：SOURCE_REPLAY 文档](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/d33d0cbad4c199fe5b450688fe8050d72afd9861/biomedical_research/virtual_cohort_system/docs/SOURCE_REPLAY.md)

---

# 附录：可交给 Codex 的实现规格

下列附录为 proposed implementation，与正文共享同一科学定义。具体代码应先核查现有接口，再按新版本扩展。


## 实现附录概述（Proposed）

**状态：拟议设计，尚未实施或完成性能验证。** 本附录供开发拆解使用。复用现有 `cohort_harness`，保留 `generate(observed, spec, seed) -> DataFrame` ABI；运行模式沿用 `enrichment`、`completion`、`whole_cohort`。首版先贯通 `enrichment`，其他模式分别完成信息条件、生成契约和真实参考验证后再声明支持。

## A. 执行结构与职责（Proposed）

系统由确定性 Controller、一个可调用工具的 Agent 和统计工具组成。Agent 负责解释发表结果、选择生成结构、提出证据请求和科学修订；普通代码负责参数优化、来源分析重放、随机生成和结果汇总。独立 critique 是可选检查步骤，不是必需的多 Agent 架构。

新增 `agent_runtime/runner.py`、`actions.py`、`state.py`、`provider.py`。分别承担循环调度、动作验证、状态持久化和模型服务适配。`cohort_harness` 增加 `evidence_semantics`、`source_context`、`analysis_operators`、`calibration`、`sensitivity`、`release` 模块。既有生成执行、文件契约和分析工具优先复用，不因增加 Agent 重写已经正确的统计实现。

Controller 维护版本与允许动作。Agent 不能自行宣布候选已冻结，也不能通过自然语言覆盖工具计算结果。模型服务适配层记录实际返回的模型标识、请求配置和用量；服务没有提供的字段保留为空，不估造精确成本。

研究运行与真实部署共用构建流程。研究运行在冻结后由独立 evaluator 读取真实参考结果；部署时没有这一步。来源拟合通过在两种模式下均只能表示与已使用证据相容，不能自动表示真实目标准确。

## B. 数据对象与版本兼容（Proposed）

### B1. 不扩写 v1 的精确字段对象

原有 v1 `model_spec`、`evidence`、`source_replay`、receipt 等精确字段 schema 继续由原 validator 验证。新语义不得直接塞进旧对象。建议采用独立 v2 外层包，里面保存原封不动的 v1 候选及 v2 sidecars：

```text
proposed_release/
  candidate_v1/                 # 原契约验证的代码、spec 与冻结材料
  sidecars_v2/
    evidence_semantics.json
    source_contexts.json
    analysis_operators.json
    assumption_set.json
    calibration_session.json
    calibration_result.json
    sensitivity_plan.json
    decision_trace.jsonl
  release_v2.json
```

新增对象必须各自具备版本、validator 和内容 hash；外层 release 绑定候选原 hash 与全部 sidecar hash。validator 应检查引用对象存在、版本一致和科学含义必要字段，而不只检查 JSON 能解析。旧候选依旧能在原路径使用；v2 消费者必须先验证外层包，不能把未验证 sidecar 当成正式科学配置。

### B2. Proposed Python interfaces

```python
from typing import Literal, Protocol
from pandas import DataFrame

Mode = Literal["enrichment", "completion", "whole_cohort"]

class Generator(Protocol):
    def generate(self, observed: DataFrame | None, spec: dict,
                 seed: int) -> DataFrame: ...

def validate_evidence_semantics(document: dict) -> "EvidenceSemantics": ...
def validate_source_context(document: dict) -> "SourceContextSpec": ...
def validate_operator(document: dict) -> "AnalysisOperatorSpec": ...
def materialize_source_context(spec: "SourceContextSpec") -> "ContextArtifact": ...
def start_calibration(session: "CalibrationSession") -> "CalibrationResult": ...
def replay_sources(candidate_ref: str, plan_ref: str) -> "ReplayReport": ...
def run_sensitivity(candidate_ref: str, plan_ref: str) -> "SensitivityReport": ...
def freeze_release(candidate_ref: str, sidecar_refs: list[str]) -> "ReleaseRef": ...
```

这些名称是建议接口，不代表目前已有函数。实际合入时由薄适配层调用旧 harness；禁止以“兼容”为由复制一套略有不同的生成逻辑。

### B3. EvidenceSemantics 与参数来源

每条证据包含 `evidence_id`、原文定位、`cohort_id`、变量定义、单位、变换、时间关系、纳入条件、调整集、统计量定义、数值引用和不确定性引用。多个来自同一队列的统计量用 `dependence_group` 连接；尚不清楚的协方差必须显式缺失，不能默认独立。

每个生成参数的来源取 `reported`、`derived`、`calibrated`、`assumed` 之一。转换公式保存在 `derived` 记录中；校准值引用 session 和参与的证据；假设值说明依据及替代选项。论文没有报告某关系，不等于该关系为零。若省略某个模型项，作为结构假设保留，不能写成发表事实。

## C. SourceContextSpec 与 CalibrationSession（Proposed）

### C1. 来源人群独立于生成器定义

`SourceContextSpec` 描述用于重放某篇来源研究的协变量与测量环境；它独立于目标生成器。直接报告的边际、联合信息与重建假设分开存放。来源样本量与模拟行数分开记录，增加模拟行数不得改变证据精度。

下列对象仅为拟议模板，所有引用均为占位符，不代表真实研究数值：

```json
{
  "schema_version": "source-context-v2-proposed",
  "context_id": "<context-id>",
  "cohort_id": "<source-cohort-id>",
  "population_ref": "<population-spec-ref>",
  "reported_covariate_evidence": ["<evidence-id>"],
  "joint_structure_assumptions": ["<assumption-id>"],
  "measurement_map_ref": "<measurement-map-ref>",
  "selection_rule_ref": "<source-selection-ref>",
  "source_sample_size_ref": "<published-sample-size-ref>",
  "simulation_plan_ref": "<rows-and-seeds-ref>",
  "context_artifact_ref": "<immutable-context-artifact-ref>"
}
```

来源协变量分布未知时，可以预设多个可解释情景。不能让校准器自由选择未报告相关性，使来源误差变小后就宣称未知关系已被识别。若确实要估计来源情景参数，必须有额外信息或明确先验，并在 session 中说明这种识别依据；否则将其保留为敏感性维度。

### C2. 校准会话锁定什么

`CalibrationSession` 在数值拟合开始前锁定：生成结构及代码 hash、可优化参数及边界、使用来源与上下文版本、分析算子、loss 与权重规则、随机数方案、优化器配置和预算。允许优化的参数以白名单给出；未列出的参数不能被工具更改。

```json
{
  "schema_version": "calibration-session-v2-proposed",
  "session_id": "<session-id>",
  "base_candidate_ref": "<immutable-parent-ref>",
  "generator_code_hash": "<sha256>",
  "structure_hash": "<sha256>",
  "parameter_space_ref": "<names-bounds-transforms-ref>",
  "evidence_bundle_hash": "<sha256>",
  "source_context_refs": ["<validated-context-ref>"],
  "operator_refs": ["<validated-operator-ref>"],
  "loss_spec_ref": "<fixed-objective-ref>",
  "random_plan_ref": "<fixed-random-plan-ref>",
  "optimizer_config_ref": "<fixed-optimizer-ref>",
  "budget_ref": "<max-evaluations-and-time-ref>"
}
```

**数值 trial 不属于科学 revision。** 在锁定的参数空间内尝试若干参数，只是在执行同一个校准任务。更换函数结构、扩大参数边界、更改来源上下文、移除冲突证据、改变 loss 或更换算子，均终止当前 session，记录科学修改，再创建新的 session。

校准结果保存全部 trial 的状态、选定参数、来源拟合及计算失败。session 的临时参数替换只作用于隔离的 trial 工作副本。完成后将选定参数物化为一个新的正式候选，保留父候选引用，重新执行原契约验证及 freeze。**任何已冻结候选都不得被原地改写。**

原文未给标准误时，不能用生成样本计算的标准误冒充来源精度。同源统计相关性未知时，不能把独立加权误差自动解释为完整似然。loss 的用途和局限写入固定规格；拟合优度是来源相容性诊断，不直接作为目标真实性概率。

## D. Agent prompt contract 与 action schema（Proposed）

### D1. Proposed Agent prompt contract

```text
任务：依据当前 TaskSpec 与获准的发表证据，构建可复用随机生成器。
模式名称：enrichment / completion / whole_cohort。
接口：generate(observed, spec, seed) -> DataFrame。

允许：解释证据；提出候选结构；请求有明确缺口目标的来源检索；
启动经验证的校准与来源重放；根据获准证据提出科学修订。

必须：引用 evidence_id 或 assumption_id；区分 reported、derived、
calibrated、assumed；说明拟议改变预计影响哪项来源统计或适用分析。
来源信息不足时保留未识别部分；不能把它们自动设为已知零。

边界：目标参考结果不属于你的可见信息；不得请求或使用它。
不得修改冻结候选；不得把残差抽样称为来源或迁移不确定性。
不得把来源拟合重现称为独立目标验证。

输出：每次只提交一个符合 Action schema 的动作。
说明应简明、可检查，不要求暴露私有思维链。
```

### D2. Proposed action envelope

```json
{
  "schema_version": "agent-action-v2-proposed",
  "action_id": "<unique-id>",
  "expected_state_version": "<version>",
  "type": "<allowed-action>",
  "input_refs": ["<validated-artifact-ref>"],
  "payload": {},
  "scientific_reason": "<short-checkable-rationale>",
  "evidence_refs": [],
  "assumption_refs": []
}
```

动作类型包括 `admit_evidence`、`request_evidence`、`propose_candidate`、`start_calibration`、`replay_sources`、`propose_scientific_patch`、`request_technical_repair`、`retain_candidate`、`declare_insufficient_evidence`。各类型用判别联合 schema 限定 payload，拒绝无关字段。`freeze_release`、`evaluate_reference` 不属于 Agent 动作，由 Controller 在满足流程条件后调用。

字段修复、路径修复与科学修改分开记录；如果 bug 修复改变统计量、参数或生成值，应记录科学影响。Agent 提出“工程修复”标签不足以证明科学结果不变。Controller 以变更对象和必要的数值对照判断。

## E. Controller 运行与上下文（Proposed）

状态依次为 `TASK_READY → EVIDENCE_READY → CANDIDATE_READY → SOURCE_CHECKED → FROZEN → GENERATED → PACKAGED`，科学修订回到 `CANDIDATE_READY`。研究评估在冻结后进入独立的 `REFERENCE_EVALUATED`；真实部署跳过该状态。

```python
state = load_or_create_run(task_spec)
while not state.terminal:
    context = build_bounded_context(state, artifact_store)
    action = provider.next_action(context, allowed_actions(state))
    validate_action(action, state)

    if action.type == "start_calibration":
        session = lock_and_validate_session(action, state)
        result = cohort_harness.calibration.run(session)
        # trials 是隔离副本；创建新候选，绝不覆盖父版本。
        candidate = materialize_new_candidate(session, result)
        validate_with_existing_harness(candidate)
        freeze_new_candidate(candidate, session, result)
        state = record_calibration_result(state, candidate, result)
    else:
        state = execute_and_record_action(state, action)

    state = apply_budget_and_stop_rules(state)

if not state.retained_candidates:
    return package_insufficient_evidence_or_failure(state)

release = assemble_and_validate_release(state)
tables = execute_existing_generate_abi(release)
evaluation_if_available = None
if run_mode == "research":
    # 由隔离 evaluator 执行；结果不回流构建循环。
    evaluation_if_available = evaluate_frozen_reference(
        release, tables, analysis_plan
    )
package_outputs(release, tables, evaluation_if_available)
```

状态记录区分“候选科学冻结”与“最终交付 release”。前者使一次科学构建不可变；后者绑定实际选择保留的候选、抽样方案与交付文件。运行中可以有多个冻结候选，全部保留；最终选择只能依据事先确定的来源条件。

Agent 上下文只含当前任务、候选版本、相关证据引用、最近反馈和未解决问题。完整论文、历史 trial、决策与假设保存在 artifact store，按 ID 读取。已经确定的建模决定不能在上下文压缩后被默认为未决。参考结果目录不注册为 builder 工具，执行程序也不挂载该目录；仅有提示词约束时，应如实称为程序约定，不能宣称严格隔离。

预算区分来源检索次数、候选数、科学修订数、每个 session 的数值评估次数和总运行时间。无具体证据依据的继续修订、重复无改变、预算耗尽、关键证据不可得均可结束构建。结束可以得到有边界的情景输出或 `insufficient_evidence`，不自动代表成功。

## F. 随机方案、测试与验收（Proposed）

输出 provenance 分为 `hypothesis_id`、`source_context_scenario_id`、`parameter_draw_id`、`residual_seed`。结构候选、来源情景、参数变化和个体残差分别汇总。未经校准的候选等权集合称为情景集合，不称后验分布；增加残差种子只改变条件 Monte Carlo 精度。

必要测试应覆盖以下实质风险，优先复用已有测试：

1. 用可手算或已知生成机制的 fixtures 检验单位转换、变换后统计、调整回归及来源算子；明确边际位置不能无条件替代条件位置。
2. 校准器只能改白名单参数；换边界、loss、来源或随机方案必须产生新 session；中断恢复保持原锁定内容。
3. 父候选冻结字节始终不变；新的科学结果生成新候选，v2 sidecar hash 变化会使旧 release 验证失败。
4. 生成前后真实协变量、参与者顺序、标识和样本权重保持一致；completion 模式将来另测原有结果值不被覆盖。
5. evaluator 复用相同分析定义处理真实与生成数据；参考结果不能经 builder 可见工具或摘要泄露。
6. 试验残差数增多不会被汇总为更多独立任务或更精确的来源证据。源码相同、假设相同的候选一致也不能自动转成可靠性概率。

工程验收是整条流程可恢复、可执行、版本一致。科学验收另行使用新目标：在揭示真实结果之前固定一个主要分析、一个未直接校准的复用分析及一个保留检查；按用途设误差和退化容限。参考效应不确定时允许判为不充分。仅声称实例可行时不强制 Agent 排行榜；声称某机制改善结果时，增加该机制消融或适用的同证据比较。

## G. 可交付开发任务（Proposed）

| 顺序 | 开发任务 | 完成标准 |
|---|---|---|
| 1 | 旧 ABI 与 v1 validator 适配 | 一个原有候选通过新 runner 执行，科学输入输出未改变 |
| 2 | v2 sidecars、validator 与 hash | 能验证引用完整性，发现版本混用与文件变化 |
| 3 | 独立来源上下文和分析算子 | 已知 fixtures 下重放计算正确，直接信息与假设可分别追溯 |
| 4 | 锁定校准会话 | trials 可恢复、预算有效、参数白名单有效，产出新的冻结候选 |
| 5 | Agent actions 与决策循环 | 单 Agent 完成证据到候选及一次有依据的修订；无修订也如实记录 |
| 6 | 敏感性输出与 release | 输出可关联至结构、来源情景和残差层；交付包通过完整验证 |
| 7 | 新案例端到端实例 | 只按元数据和证据可得性选案例；冻结后一次参考评估，保留成功与失败 |

部署交付物包括生成表、生成配方、数据字典、证据及假设来源、来源检查和分析适用说明。真实缺失场景没有目标真值，因此交付说明不能把来源相容性写成目标验证。第一轮完整实例完成后，再根据实际失败决定扩展哪个机制；不得把所有拟议模块预先写成论文已实现贡献。

## H. 动作负载与失败处理细则（Proposed）

`admit_evidence` 必须指向原文版本及具体表格、段落或补充材料；Agent 对含义的解释单独保存。原文报告值、转换后值和拟采用约束不能合成一个失去来源的数字。若原文存在更正，保留实际使用版本。发现单位或调整集不明时，可以继续阅读原文；不能通过猜测把证据状态改成已检查。

`propose_candidate` 的 payload 指向代码、原 v1 spec、结构说明和假设集合。结构说明应声明哪些变量可以影响哪些生成变量、哪些函数族在候选范围内、哪些关系无法由此结构表达。Controller 检查结构说明与可执行模型是否一致；它不因为说明中出现“生物学合理”就自动承认有效性。

`start_calibration` 只接收完整且经过验证的 session 引用。优化器不能调用检索或修改源文件。可在单个会话内使用固定随机数减少目标函数的 Monte Carlo 波动，但最终来源检查还应报告这一固定抽样设计的局限。不能把一个种子上更好的 loss 直接解释为结构改善。

`propose_scientific_patch` 需要提供变更前后对象引用、触发依据、预计改变的来源统计和可能受影响的分析。若新证据使原模型项失去依据，删除也是科学修订；保留一个不理想的候选也应记录理由。审查者需要看得到相应数值变化，而不需要阅读冗长的 Agent 思考文本。

`retain_candidate` 引用事先确定的保留规则，给出满足、未满足和未能检查的条件。Agent 可以建议保留多个解释不同的候选，但不得凭自报置信度赋予概率权重。来源误差较低与目标用途较广是不同判断，后一项在参考评估之前只作有依据的预期。

技术失败按三类处理：执行失败可以在科学对象不变时重试；证据格式或含义错误必须回到证据处理；科学相容性不足进入模型修订或证据请求。每次失败留下原记录，重试成功不会删除失败记录。重试和恢复不能重置全局预算。

## I. Trial 记录、恢复与敏感性输出（Proposed）

单次数值 trial 记录 session 引用、参数向量引用、执行状态、来源统计向量、分组 loss、随机方案引用、耗时和错误。禁止仅保存最优 loss：否则无法判断优化是否稳定，或某项来源被其他项掩盖。不同来源的误差除了总目标值，还应分别展示。

一个最小拟议记录如下；占位符不包含真实来源数据：

```json
{
  "schema_version": "calibration-trial-v2-proposed",
  "session_ref": "<locked-session-ref>",
  "trial_id": "<unique-trial-id>",
  "parameter_vector_ref": "<trial-parameters-ref>",
  "status": "<completed-or-failed>",
  "statistics_ref": "<source-statistics-ref>",
  "loss_components_ref": "<per-source-loss-ref>",
  "random_plan_hash": "<sha256>",
  "error_ref": null
}
```

Controller 在动作执行前写入意图，成功后原子提交结果和新状态。恢复时先检查意图是否已经产生有效结果，避免重复创建 session 或重复计费调用。无法确认已经完成的外部调用应标记状态未知，而不冒称失败后直接当作独立重复。缓存键至少覆盖代码、spec、来源上下文、算子、证据和随机方案。

敏感性输出先回答哪个科学结论随哪个假设改变，再报告数值范围。若来源参数有完整估计协方差，可以按预定联合方案采样；只有若干边际标准误时，不能自动当成独立正态参数。无法建立适当概率模型时，采用明示的参数或结构情景，并且不给这些范围附加概率覆盖解释。

个体残差还要区分两种用途：它描述条件模型内个体值的变化；多次生成后分析估计量的变化描述抽样实现的波动。两者都不能代表跨人群迁移偏差。汇总程序应始终保留外层结构和来源情景分组，避免把全部表混合成一个看似精确的总体区间。

## J. 参考评估与实例验收交接（Proposed）

新案例的 eligibility 记录只使用目标数据字典、测量时间、纳入设计和既有项目使用历史。目标指标的分位数、相关系数和亚组摘要同样属于保留结果，不能为了挑选“适合案例”先发给 builder。来源与目标研究重叠检查在生成前完成；任何公开目标摘要的暴露都应记录。若构建者已接触预定分析的真实答案，该构建属于开发；无法核清时保留 freshness_pending，或更换保留任务。只有文件隔离不能证明此前完全未接触公开结果。

参考 evaluator 的输入是 release ID、预定分析计划 ID 和参考数据句柄。它先验证 freeze，再读取参考值，并对所有保留候选执行相同计划。失败分析和不可估计结果也进入报告，不能只展示成功输出。若参考设计不足以估计适当区间，则报告相应点估计和限制；不得套用普通独立样本标准误补齐。

冻结后的生成输出若表现很差，仍完成这一实例的评价与交付。解释可指向证据不足、模型表达不足或迁移假设失效，但原任务不进入答案驱动的修订循环。后续科学修改形成新的开发版本，验证使用另一个事先选定的保留任务。

一份合格的端到端实例报告，应使读者能够依次找到允许输入、已采纳文献、统计含义解释、生成结构、关键假设、来源拟合、实际科学修改、冻结对象和下游结果。没有发生科学修改就如实报告保留；缺少联合证据就报告哪些分析仍由假设主导。该实例的完成标准是形成可检查的生成与分析链条，而不是必须获得正向结果。
