# 下一病例验证：方法实现准备审查

审查日期：2026-11-09（America/Chicago）；只读运行环境检查时间：2026-11-10 03:14:04 UTC。

**结论：现有冻结引擎可复用，指定 WSL 解释器和 bubblewrap 可访问；新病例的宿主封装、模型调用记录、分析接口及批次评价门禁尚须建立并冻结。本审查不授权生成或打开目标参考结果。** 根任务告知暂选 PNS SBP/DBP 作为候选，尚未完成病例准入；本审查没有读取该候选的记录或结果，也不据此决定分析公式、临床参数、参考值或容许误差。

本次只阅读方法文档、接口/封存代码及历史实现审查清单，核对代码哈希，并作 WSL 状态、可执行路径及版本元数据检查。未执行任何作者程序、生成器、分析器、已通过测试或 sandbox smoke；未读取临床/生成行表或新病例结果文件，未下载来源，未创建付费 API。阅读的历史 `finalize.py` 本身含旧报告文字；这些文字不作为新病例建模输入或效果证据。

## 1. 建议复用的最小路径

使用 **2026-11-09 additive `cohort_harness/adaptive_session_v2.py`**，不是旧实验目录中任何同名 v2/pilot。真实新 Agent 由现有宿主 collaboration 工具以 fresh context 调度，读取冻结请求，自主选择来源、统计结构、参数、假设和下一动作；宿主将其动作送入现有 controller。该 controller 不含模型 API client，也不能单独代替 Agent 作者。

| 层 | 直接复用 | 新病例需要的薄封装 |
|---|---|---|
| 作者和调用记录 | 现有真实 Agent dispatch/follow-up 工具；项目 authoring skill | 5 个 fresh 作者槽位、实际调用回执、任务/提示词与模型元数据清单。不能由确定性脚本预写科学模型后标为 Agent。 |
| 动作执行 | `cohort_harness/adaptive_session_v2.py` | 每作者独立 bundle/config；宿主 allowlist、审查阶段和冻结规则。 |
| 检索 | `cohort_harness/literature.py`、`web_evidence_v1.py` | 新任务允许的工具、排除目标来源别名、预算和暴露处理规则。查询与选文由作者决定。 |
| 构建/采样 | `contracts.py`、`lifecycle.py`、`execution.py`、`_worker.py` | 新病例 task/schema；无需改采样引擎或增加另一条无隔离路径。 |
| 反馈 | `semantic_feedback_v1.py` 与 `descriptive_feedback_v1.py` | 按实际证据定义 recipe/semantic/descriptive sidecar；不能沿用旧病例的数字或 operator。 |
| 源人群重放（可选） | `whole_cohort_source_replay_v1.py` | 仅当作者有足够源上下文时冻结源任务/排程及 source-to-target mapping。无充分上下文时保留 unavailable；不强制制造一个重放模型。 |
| 生成结果分析 | v2 的 hash-bound `analysis` 接口 | 新的 generated-only SBP/DBP 分析 adapter，具体公式和单位由新病例研究请求锁定。不得自动调用旧 lipid provider。 |
| 临床参考评价 | 借鉴 Q5 的先 closure、后 reference-read 结构 | 新病例 evaluator + 五作者总批 seal；不是旧 source-conditioned `finalize.py`。 |

`analysis_use_v1` 是可选声明/一致性工具，非最小执行路径的必需新增组件。原有源复现、方法文件和数值结果不得修改以配合新病例。

## 2. 真实 Agent 与可核验模型元数据

v2 的 config 使用 exact-key schema；其 manifest 只记录 `model_dispatch: external_host`，不会自动记录模型身份。不要向冻结 schema 私塞 `model` 字段。最小办法是把调用前已知的作者配置写入 `input/author_runtime.json` 或 `SETUP_NOTES.md`，由现有 `_inputs()` 在 session 创建时绑定；实际调用回执另存宿主 append-only ledger，最终写入作者/批次 seal 的 commitments。

每个作者至少记录：author ID、实际外部 session/agent ID、UTC、fresh context/是否继承上下文、实际发出的 dispatch 与 follow-up 指令及其哈希、平台/服务、requested model alias、服务实际返回的 effective alias、reasoning 配置（若有）、exact snapshot（若公开）、工具边界、协议/skill/input 哈希、token/cost 回执（若公开）、各缺失字段的原因。

**requested、effective、exact snapshot 必须分开。** 当前审查没有获得权威的 run-specific effective-model 回执，不能把当前助手的通用模型家族说明、应用默认配置或推测写成历史/未来调用的 exact snapshot。若现有宿主只返回 inherited model，应如实保存该值，并将未公开字段置为 null、标明 `not_exposed_by_host`。这仍能完整记录实际调度及缺失边界，但不能声称模型快照级复现。若新验证必须绑定某一确切模型，需在 dispatch 前取得可信配置/服务回执；无需为此创建新的付费 API。

只有 skill/task/协议等固定输入应在 session 创建前完成；不可在创建后改写 `input/` 来补填新的 dispatch ID。可先冻结调用前声明，再把实际调用回执作为独立宿主记录随最终 seal 绑定。

## 3. 五作者、三种子与一次可选修订

根任务指定 **5 位独立 fresh 作者、每位 3 个预先固定种子、最多一次基于允许反馈的修订**。v2 已有一个不可忽略的语义：成功 `finish` 要求**每个已提交候选**尝试全部 `allowed_seeds`，且每次成功执行都具备 strict+descriptive feedback 和所有配置的 generated analysis。

最小兼容方案是每位作者 1 个初稿、最多 1 个修订稿；每个候选固定 3 seeds。每作者最多 6 张、全批最多 30 张生成表。作者预先记录选定 law；选定 law 的 3 张计为最终交付，全批最多 15 张选定交付，其余阶段完整保留。失败尝试计入预算，未用修订额度不补作者/不换种子；所有候选阶段和不可计算指标应保留。这里的数值是排程上限，不是已经发生的执行。

不能把这个排程同时写成“每作者仅 1 次试跑，再 3 次独立 final”而只给 v2 三个 seeds。若研究确需后一排程，需要单独、明确的阶段调度设计及新封装审查；不应改变冻结 v2 的 finish 规则。新病例的行数、具体 seed 数字、分析次数、检索/HTTP/字节上限尚待根任务冻结。

作者可见的是允许的来源、源定义检查和自己生成数据的诊断；任何真实参考值或参考比较均不可作为修订反馈。可选源上下文重放产生自己的来源回执；它不是临床 target evaluation。生成结果分析与参考结果分析必须由不同 adapter/路径承担。是否将所有生成结果在最终选择前返回作者，应在新 protocol 明写，不能默默继承旧 source-only 实验的更严格门禁。

## 4. source/target 接口与 semantic v1

常规 whole-cohort ABI 为 `generate(observed, specification, seed)`，其中 `observed=None`。worker 从只读 `/input/task.json` 读取 task，作者程序可按已声明约定读取同一文件获得 population、n_rows、columns；不是铁研究的特殊 `generate(n, rng, context)` ABI。

可选 `whole_cohort_source_replay_v1` 从冻结候选复制相同 generator/spec/evidence/decision 及来源记录，仅改变 child task 的 population、n_rows、columns。源任务可以有 target 输出不含的调整变量和标准化列；它们仍须在同一个 spec 和科学 source-to-target mapping 中说明。仅用 population 字符串选择互不相关的两套拟合并不建立证据迁移。

源重放 plan 在冻结前声明 budget、schedule、contexts、recipe/semantics hashes、predictor checks 和 assumed diagnostics。外层 wrapper 必须把作者填入的预算与根任务批准预算比较；通用 adapter 本身不能知道用户批准了多少。新增 source-replay 模块不在 v2 自带 engines 清单中，使用时须另纳入新 wrapper 的 DESIGN_LOCK。

严格 semantic v1 与 assumption-dependent 数值层应同时保留。缺失 weighting、adjustment、单位或标准化定义不能为获得数字而改写为 matched。源 adapter 的 assumed lane 仍要求定义已指定的同一 operator；非 identity 目前仅支持已检查 zscore term 的 OLS，且其并行估计器是 unweighted。加权源回归、未定义 operator 或其他变换不是自动支持项。源上下文不足时可继续透明的 assumption-dependent 建模，但不能宣称完成精确源复现。

## 5. 自由检索/建模的可复用范围

现有 v2 可调度 Europe PMC/PMC 查询/获取，也可获取作者选定的公开 HTTPS HTML/text/PDF；没有预置概率分布或生物学参数。`web_evidence` 与 literature 共享 task 的 source_downloads 计数；web 另记 HTTP/字节限额。fetch metadata 也可能消耗 query credit。所有预算须在新任务开始前冻结，错误照计；不得重置 bundle 来刷新额度。

旧 `work/source_conditioned_replay_2026-11-09/act.py` 在第 79 行禁止 literature，且保留旧病例的 5 次剩余 discovery、24 source slots、200 objective calls 和固定 context IDs。它适合其原有 source-only 单元，**不能不改配置/封装就称作新病例自由检索流程**。应在新目录写参数化 wrapper，调用现有 v2；旧文件保持不动。

若允许 native web search 发现 URL，它在 v2 外，必须额外保留查询、返回/跟随 URL、时间、预算及意外目标信息暴露日志；snippet 不能直接变成量化约束，需经记录的原文入库。最小路径可先使用已有受计量的 literature search 和 web fetch，无需添加另一检索系统。目标记录、旧结果/模型和 custodian 路径不得出现在 author config、analysis adapter 依赖或 author prompt allowlist 中。技术边界只隔离生成程序；作者工具的限制仍需 fresh context、清晰 allowlist 及过程记录，不能声称已建立 Agent OS 隔离。

## 6. 必须新增的门禁及不能直接照搬的文件

以下是新验证必须补齐的适配工作，不是本次发现了冻结引擎的数值缺陷：

1. **新病例配置和 estimator adapter。** 待准入后冻结变量/单位/eligibility/weighting/分析公式、输出诊断、接受或描述性规则。generated adapter 的接口为 `analyze(output_path, task_path, request_path) -> finite JSON dict`；其代码和 transitive dependencies 全部 hash-bound，且不读临床参考。宿主 adapter 本身不受 sandbox 隔离，必须静态审查其读取路径。
2. **新作者调度和元数据 ledger。** 真正 dispatch 五个 fresh Agent，实际动作、初稿/修订、反馈和停机理由逐一绑定；模型字段按上文保留来源与未知状态。
3. **新通用 wrapper。** 用新协议替代旧 case/额度/候选 context 的硬编码，允许已授权的 retrieval 路径，执行 reviewer gates 和预算。既有 `run_source_stage.py`、`seal_author.py`、`run_sealed_outputs.py` 仅供结构参考，不能在原目录跑或照搬旧 scientific checklist。
4. **五作者共同 seal 后才 reference-read。** 每作者固定选择、全部已提交阶段的排程处置、程序/输出/反馈/分析 hashes 与任何失败封存后，再创建 batch seal。新 evaluator 首先核验 5 槽位、所有 required outcomes/seed attempts 及 protocol/engine/author seals；然后才在独立 custodian 阶段读被批准的参考。临床引用路径放在 evaluator-only 配置，而非 author bundle。参考获取/既有缓存是否已暴露由病例准入审查决定，本实现审查不打开它们。
5. **通用终态报告。** 旧 `source_conditioned_replay/finalize.py:17–18` 限定单候选 retain，后续计数也硬编码且 `reference_data_reads=0`。它不是新病例的临床 evaluator，也不覆盖修订/失败/弃权。新报告必须明确各终态，完整列出所有预定分析，不用有利 seed 或成功作者替代失败。

可以借鉴 Q5 `evaluator.py` 的 closure gate 在任何 reference load 之前调用的顺序，但不能调用其旧 cached reference mapping、固定 6 作者分配或旧统计量。现有 source-conditioned wrapper 的 author-seal 原则同样可借鉴；它原来禁止在 source-only seal 前返回任何 target-like generated results，并非新病例已经自动决定的反馈策略。

## 7. WSL 只读可用性与冻结模块核对

`wsl --status` 与 `wsl --list --verbose` 显示默认 Ubuntu-24.04、WSL2；检查开始时处于 stopped。随后只运行指定 venv 的 `python -I -B -c`，读取 `sys.version`、`importlib.metadata` 版本和 bwrap 路径权限；未导入 NumPy/pandas 科学模块或任何作者程序。再执行 `bwrap --version`。两条只读调用返回 0：Python 3.12.3，NumPy metadata 2.4.5，pandas metadata 3.0.3，bubblewrap 文件存在且可执行，版本 0.9.0。

这证明当前解释器、安装元数据和可执行文件可访问，不等同于本次重新验证了 namespace isolation 或完成了新病例预跑。旧 source-replay 实现审查记录已有 68 项检查和 invented isolated smoke；本次没有重跑。当前 adaptive_v2、semantic_v1、web_evidence、execution 和 whole-cohort source replay 的五个代码哈希均匹配该历史实现审查。额外记录 worker/v1/descriptive 的当前哈希，见 JSON；不以新读到的哈希冒充原始预承诺。

## 8. 根任务的下一步

先完成候选准入和新任务/estimand 定义；再只在新目录建立最小 wrapper、generated adapter、evaluator-only contract、作者 metadata 模板和五作者批次 seal。独立静态核对这些新增连接及新接口必要的非临床检查后冻结，即可真实派发作者。无需重建核心 harness、重跑所有历史测试、复制旧科学参数、增加必需多 Agent 结构、训练模型或创建付费 API。

本次交付只含本报告及对应 JSON；没有创建可执行新 wrapper，也没有开始 scientific session。

## 直接证据位置

项目相对路径；行号指本次只读版本：

- `docs/ADAPTIVE_SESSION_V1.md`；`docs/ADAPTIVE_SESSION_V2.md`：实际 host dispatch、动作范围、源/目标限制及完成规则。
- `cohort_harness/adaptive_session_v2.py:52–81` config；`:102–112` 固定输入；`:115–142` actions；`:232–279` seed/finish；`:282–305` create+external model；`:319–338` generated analysis；`:400–434` real adapter dispatch。
- `cohort_harness/whole_cohort_source_replay_v1.py:132–204` source metadata/semantics；`:250–270` 相同 code/spec child；`:381–411` 真实隔离 source execution；`docs/WHOLE_COHORT_SOURCE_REPLAY_V1.md`。
- `cohort_harness/_worker.py:34–50` 标准 ABI；`cohort_harness/execution.py:25–48` 指定 runtime；`docs/EXECUTION_ADAPTER.md:18–36` 原隔离边界。
- `docs/WEB_EVIDENCE_V1.md` shared budget；`cohort_harness/literature.py:169–183` query/permission；`cohort_harness/web_evidence_v1.py:405–409`, `:494` 预算和权限。
- `work/source_conditioned_replay_2026-11-09/act.py:21–48`, `:69–106` 旧病例约束与 dispatch；`run_source_stage.py:12–35` reviewer gate；`seal_author.py:13–34` source-only author seal；`run_sealed_outputs.py:12–29` 固定所有候选种子。
- 同目录 `start_session.py:20–35` 旧配置与额外 source-engine binding；`finalize.py:17–18`, `:47–58` 不可通用的单阶段/非临床报告；`IMPLEMENTATION_REVIEW.json` 历史工程检查与代码承诺（不是本次重跑结果）。
- `work/evidence_use_cross_task_2026-11-05/evaluator.py:42–46`, `:71–80`, `:140–145` closure-before-reference 的参考结构。
