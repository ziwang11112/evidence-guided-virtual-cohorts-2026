"""Reconcile independent aggregates and write a bounded descriptive result."""
import json,math,statistics
from pathlib import Path
import controller as c
U=Path(__file__).resolve().parent
primary=c.load(U/"PRIMARY_EVALUATION.json")
ind=c.load(U/"INDEPENDENT_EVALUATION.json")
checks=[]; maximum=0.0
for row in primary["runs"]:
    other=next(x for x in ind["new_final_records"] if x["seed"]==row["seed"])
    if row["status"]!="success":
        checks.append({"seed":row["seed"],"check":"failure_retained","pass":other["status"]!="complete"})
        continue
    checks.append({"seed":row["seed"],"check":"output_hash","pass":row["output_sha256"]==other["sha256"]})
    for item in row["statistics"]["analyses"]+row["statistics"]["diagnostics"]:
        a,b=item["value"],other["values"][item["id"]]
        delta=abs(a-b) if a is not None and b is not None else None
        if delta is not None: maximum=max(maximum,delta)
        ok=(a is None and b is None) or (delta is not None and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9))
        checks.append({"seed":row["seed"],"metric":item["id"],"absolute_difference":delta,"pass":ok})
audit={"status":"pass" if all(x["pass"] for x in checks) else "fail",
  "max_absolute_difference":maximum,"checks":checks,"primary_sha256":c.sha(U/"PRIMARY_EVALUATION.json"),
  "independent_sha256":c.sha(U/"INDEPENDENT_EVALUATION.json")}
c.write(U/"FINAL_ARITHMETIC_AUDIT.json",audit)
if audit["status"]!="pass": raise ValueError("independent arithmetic mismatch")
summary=ind["constructor_metric_summaries"]
def metric(constructor,key):return next(x for x in summary if x["constructor"]==constructor and x["id"]==key)
def fmt(v):return "不可用" if v is None else f"{v:.6f}"
fit=c.load(U/"FIT.json"); d=fit["fit_diagnostics"]
closure=c.load(U/"RECOVERY_DRAW_CLOSURE.json")
lines=["# CHNS 摘要辅助生成的统计对照结果","",
"2026-11-03。本次补充实验完成一个预先规定的统计构造，与历史三个 Agent 构造比较。各方可以使用相同的 CHNS 目标摘要及原始证据包。这里评价的是摘要校准和有限样本分析用途，不是独立临床验证。","",
"## 完成情况","",
f"- 一次固定拟合程序，三个预定最终种子；成功输出 {sum(x['status']=='success' for x in closure['results'])}/3 张，每张3,000行。没有临床试生成、重新拟合或补种子。",
"- 原控制器三次调用因候选路径格式错误在启动前失败；全部记录保留。经独立审查作路径修正后，另计三个恢复调用。因此共有六次编排尝试、至多三次真正生成器执行；这是明确披露的协议偏离。",
f"- 三项回归与27项诊断由两个实现计算；共 {sum('metric' in x for x in checks)} 项数值比对，最大绝对差异 {maximum:.3g}。",
"- 不读取原始患者记录，也没有重新生成或调整历史 Agent 输出。原72张主实验保持关闭。",
"- 统计结构使用有界边际与尾部分块依赖，参数通过已开放摘要拟合；未对最终样本强行配平。","",
"## 三项主要分析","",
"| 分析 | 已提供样本参照 | 新统计构造三种子均值 | 历史三个Agent构造的三种子均值范围 |",
"|---|---:|---:|---:|"]
labels={"E1":"BMI系数，调整年龄/性别","E2":"血糖系数，调整年龄/性别","E3":"年龄系数，调整性别/BMI/血糖"}
for key in ("E1","E2","E3"):
    s=metric("STAT_R30",key)
    old=[metric(k,key)["mean"] for k in ("R01","R02","R03")]
    lines.append(f"| {labels[key]} | {fmt(s['reference'])} | {fmt(s['mean'])} | {fmt(min(old))}–{fmt(max(old))} |")
lines+=["","单位依次为 HbA1c 百分点/(kg/m²)、百分点/(mmol/L)、百分点/年。范围跨模型构造，不是置信区间。各方法逐种子的绝对差异和全部30项指标见独立结果。","",
"## 相关和分布诊断","",
"| 指标 | 已提供参照 | 新统计构造三种子均值 | 历史Agent构造均值范围 |","|---|---:|---:|---:|"]
for key in ("glucose_hba1c_pearson","glucose_hba1c_spearman","bmi_mean","bmi_sd","glucose_mean","glucose_sd","hba1c_mean","hba1c_sd"):
    s=metric("STAT_R30",key);old=[metric(k,key)["mean"] for k in ("R01","R02","R03")]
    lines.append(f"| {key} | {fmt(s['reference'])} | {fmt(s['mean'])} | {fmt(min(old))}–{fmt(max(old))} |")
lines+=["","完整分位数、年龄/性别诊断和每次输出均保留在 [独立比较](INDEPENDENT_EVALUATION.md)，没有按优劣筛选。","",
"## 这次比较能说明什么","",
"统计校准器的完整拟合记录、模型期望与实际样本分析必须分开看。拟合模型可以接近输入摘要，而3,000行随机数据的系数仍会波动。最终解释依据上表和完整诊断；不以拟合器目标值替代数据评价。",
"若两条路线均能提供相近结果，说明摘要校准能力由多种方法共享。该结果不能单独证明 Agent 不需要，也不能单独证明 Agent 方法更优。Agent 的任务适应、人工建模负担与外部证据处理仍需相应过程实验。",
"本统计族由研究实现过程在可见摘要条件下专门设计，使用了编码 Agent 辅助；冻结后执行固定统计拟合。它不是盲态人类专家对照，也不是移除所有 Agent 参与的消融。历史三次 Agent 构造与一个固定统计算法的预算、模型选择及反馈机会不同。",
"所有30项参照统计均已提供，没有未见分析增益结论。性别独立、尾部成员共享和未报告联合关系是模型假设；边界和抽样数不会制造新的临床证据。","",
"## 实现审查与成本","",
"拟合前修复了协方差重复相加、whole-cohort入口、浮点CDF尾部表示及中断槽位保留问题。四项生成模型测试、两项控制器测试、七项独立评价测试及独立数学oracle使用人工构造数据。随后实际编排暴露了模拟测试未覆盖的候选路径错误；三个原始失败均保留，技术恢复没有改动模型或种子。",
f"固定拟合内部耗时 {d['wall_seconds']:.3f} 秒；拟合进程总耗时 {c.load(U/'FIT_EXECUTION.json')['elapsed_seconds']:.3f} 秒；三次隔离生成合计 {sum(x['elapsed_seconds'] for x in closure['results']):.3f} 秒。这不含模型设计、编码、输入整理和审查，也不能据此比较端到端成本。",
"独立审查的通过消息发生在拟合前，正式PRE_FIT_REVIEW文件随后补记；发布记录如实保留该顺序。拟合后还经过数学/参数审查才允许最终采样。","",
"## 决定","",
"关闭这个最小补充单元，不调整已生成数据、不追加种子或扩大为48表研究。保留比较结果供论文定位；下一步优先依据该结果确定任务切换评价和一个近邻方法适配是否必要。","",
"核心工件：PROTOCOL.md、SPEC.md、INPUT_COMPARABILITY_AUDIT.md、PRE_FIT_RELEASE.json、FIT.json、POST_FIT_REVIEW.json、DRAW_CLOSURE.json、PRIMARY_EVALUATION.json、INDEPENDENT_EVALUATION.json、FINAL_ARITHMETIC_AUDIT.json。"]
with (U/"RESULTS.md").open("x",encoding="utf-8") as f:f.write("\n".join(lines)+"\n")
state=c.load(U/"STATE.json")
state.update(phase="complete_pending_public_sync",execution_enabled=False,clinical_fit_started=True,
 clinical_fit_completed=True,final_tables_generated=sum(x["status"]=="success" for x in closure["results"]),
 final_attempts=6,prelaunch_failures=3,recovery_attempts=3,independent_arithmetic_status=audit["status"],further_generation_allowed=False)
(U/"STATE.json").write_text(json.dumps(state,indent=2)+"\n")
print(json.dumps({"audit":audit["status"],"maximum_error":maximum,"completed":True}))

