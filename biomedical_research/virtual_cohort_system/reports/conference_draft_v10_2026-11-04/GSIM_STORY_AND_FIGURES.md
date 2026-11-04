# G-Sim：故事线与图表对照，用于本项目 v0.10

2026-11-04。只做原论文阅读与写作/呈现建议；没有读取患者或生成行、运行实验、修改旧文件。使用 PDF skill 做原版页面检查。下列改稿建议是对我们现有证据的编辑判断，不是 G-Sim 的结论。

## 阅读与来源

- 官方身份已重新核查：[G-Sim, ICML 2025 / PMLR 267](https://proceedings.mlr.press/v267/holt25b.html)。作者 Samuel Holt、Max Ruiz Luyten、Antonin Berthon、Mihaela van der Schaar；页码 23513–23561。
- 原论文：[PMLR 链接的 PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/holt25b/holt25b.pdf)。本次网页 PDF 读取因服务器返回 `application/octet-stream` 失败，改用既有原文缓存，没有重新下载。
- 缓存：`work/neighbor_deep_read_2026-10-31/gsim/holt25b.pdf`，1,525,687 bytes，49页；本次重新计算 SHA-256：`77a62c51eff5fbfaf3f64cc16aa0de1b520dc038c834fa0df074baab623f770f`，与原来源清单一致。
- 本次逐页阅读主文 PDF 第1–8页文字，并从该 PDF 直接渲染、实际查看第3、7、8页。第3页是 Figure 1；第7页是主结果 Table 2；第8页含 Figures 2–3、Table 3。未声称本轮重新读完全部附录或运行作者代码。渲染在内存中完成，未复制论文图到我们的稿件。
- 对照本项目 [v0.9](../../manuscript/DRAFT_v0_9.md) 的摘要、引言、方法和全部章节层级，以及已完成的主实验/新图身份。

## 原论文的可核实结构（精简摘要）

G-Sim starts from system-level “what-if” use, states required simulator properties, and links each to structural design, numerical calibration and diagnostic refinement (pp.1–6). Figure 1 gives a full-width worked workflow with actual inputs, code, calibration branches and feedback. Table 2 concentrates the principal three-environment comparison and refinement ablations (p.7). The benchmark trajectories come from designed simulators, not patient cohorts. Figure 2 then shows intervention trajectories; Figure 3 shows paired resource-cost landscapes; Table 3 connects simulation to a decision (p.8). Thus the empirical story advances from fidelity to an enabled use. The paper explicitly uses LLM structural proposals and feedback; it should not be described as non-agentic. The visible layout combines two-column prose, a full-width method figure, compact numeric tables, restrained colors and small multiples. Caption text carries interpretation. Some labels are very small at column width and should not be imitated uncritically.

## 对我们最重要的启发：把用途变成论文的组织轴

v0.9 已保存完整证据，但方法部分有11个三级小节、结果部分也有11个，读者需要在很多实验历史之间寻找共同贡献。新稿应当回答一条递进问题链：

1. **需要什么数据、手里有什么证据？** 在开头用一个具体需求说明：请求年龄、性别、BMI、血糖和 HbA1c 的完整虚拟人群，允许没有个体输入。补列是相邻用途，不能成为唯一动机。
2. **为什么这需要科学建模？** 同一响应的不同调整系数、边际相关和分组摘要不能直接拼成联合分布。这是方法选择的理由。
3. **Agent 实际完成哪一项困难工作？** 将有研究条件的证据解释成数值约束，选择未被证据完全确定的联合结构，并生成可执行数据。保留 A01 的分别调整投影实例，短公式比一长段工作流日志更有解释力。
4. **交付的数据能完成什么分析？** CHNS/ENSANUT 六项预定分析为主要规模证据；L/R 为给定摘要重构；HRS 为纵向使用；它们承担不同问题，不合并成一个成功率。
5. **多出的证据或缺失的证据，会改变什么？** E0/E1 是已完成的信息条件比较；最新 copula 的两点解析敏感性说明一个缺失关系会改变哪项条件分析。这样的结果具有方法意义，不只是“某个系数偏差较大”。

可用的摘要顺序是：应用缺口一句 → 科学困难一句 → 方法动作两句 → 主实验一条量化结果 → 一个不同用途实例 → 作用边界一句。建议约200–250英文词，避免摘要罗列每次执行与审查数量。

## v0.10 的建议结构

| 主文位置 | 要回答的问题 | 从现有稿保留什么 | 移到补充的内容 |
|---|---|---|---|
| Introduction | 为什么研究者需要这种数据产品？为什么现有信息不能直接拼表？ | 完整队列需求、研究条件下的证据、三个有结果对应的贡献 | 项目推进时间线、不同旧版本的逐项身份细节 |
| Problem formulation | 输入、输出和分析用途是什么？ | 研究请求、目标总体、证据条目、可选观测；研究问题可告知 Agent | 全部字段清单、每种模式的接口差异 |
| Method | Agent 作哪些科学选择，工具负责哪些计算？ | 证据资格与数值使用、联合模型、生成与有界检查、A01短例 | host调度日志、异常恢复、审查次数、所有字段schema |
| Experimental design | 每一项结果究竟检验什么？ | 一个紧凑表区分外部证据、给定摘要、公开模型、开放检索示例 | seeds全清单、全部源文件哈希、历史版本全过程 |
| Results: analytical utility | 主要预定分析能否得到有用结果？ | 完整六项 E0/E1、所有构造者、统计参照；无只挑阳性 | 全部非主要分布诊断，仍保持可访问 |
| Results: information and use | 不同可用信息支持什么产品？ | L/R的五项分析、HRS两项预定交互；完整结果补充 | 重复的“初末没有变化”逐次叙述 |
| Results: end-to-end case | 真实 Agent 链路如何从证据到科学用途？ | 最新七个回归项与缺失依赖的两个解析情景 | 旧live A/B每次检索和下载的过程细节、36指标完整表 |
| Discussion / limitations | 已得到什么，哪些使用仍需进一步验证？ | 分析用途、可用证据边界、开发参照身份、无revision gain | 不需要重复所有前文限制句；完整失败账仍在补充 |

这是一份紧凑主文设计，不要求删除原始证据或改变冻结结论。可保留 v0.9 为完整长稿，并在 v0.10 主文链接补充；具体字数要在选定会议/期刊后按其官方规则调整。

## 图表的具体改法

**Figure 1 应帮助读者理解科学动作。** 使用完整队列生成的一个贯穿例子，将输入证据中的“研究人群/调整集/统计量”与 Agent 选择的联合模型、生成表和下游分析连接。突出一个实质转换，而不把排队、文件验证、冻结哈希画成核心方法。需要注明研究者/Agent/确定性工具的实际角色；不增加未实现的训练、闭环优化或自由查询能力。

**Figure 2 保留全部六个主分析。** 用一致颜色编码 E0、E1、统计参照；每位构造者的三种子范围与样本参照区间用不同符号语法。不要按有利程度重新排序：按预定病例与分析顺序即可。原量纲不同，不把所有面板强行共用数值轴。

**Figure 3 与 Figure 4 回答不同用途。** 前者是摘要辅助的联合数据；后者是纵向公开模型。保留所有预定关系与对照，减少重复大标题、长框和图内免责声明，让同一颜色在全稿保持同一角色。限制和区间含义进入图注。

**Figure 5 是我们的解释性实例。** 七个回归项必须完整出现；可以用两行紧凑面板加一个敏感性面板。把目前画布中的长主标题、整段说明与底部长限制移到图注，图内只留简短模型式、单位、图例、种子/构造身份。两点敏感性只有两个已有情景，仍不可画成未经计算的连续曲线。

**全稿视觉语法。** 白底、少量角色色、细轴线、直接单位、统一字号；不用装饰渐变/阴影或面板卡片。宽度先按双栏全宽约170–180 mm规划，再在实际投稿版面检查7–9 pt量级标注。宽度是当前工作建议，不是任何会议的官方尺寸规定。PNG只是检查用途，SVG/PDF保留可编辑文字与矢量内容。

不建议照搬他人的checkmark比较表来宣称“自动化/泛化”等能力全有。我们的主文适合用“输入信息—数据产品—实际分析—已完成证据”的具体比较表；普通Agent亦可实现核心流程，论文没有必要变成Agent名称之争。

## 不能通过改写解决的证据边界

G-Sim的实验对象与我们不同，不宜借其叙事把我们的参照称作模拟器已知真值，也不把我们的模型假设敏感性说成真实干预验证。已有主实验有充分结果可写；最新版开放检索当前只有一个构造实例。当前适合主张“实现并展示这种证据到可分析数据的过程及其信息依赖”，不能仅靠更紧凑图表升级为广泛自主泛化、普遍性能优越或修订改善。

最重要的编辑动作是：**让每一节只承担一个贡献问题，每张图回答一个能被完整结果检验的问题。** 这会使我们的方法与已有实验形成清楚的因果叙述顺序，但不会为结果制造因果结论。
