#!/usr/bin/env python3
"""design.py —— 从置信度账本选出最该验证的机制，生成扰动实验矩阵。

实验矩阵 = {实验 id、自变量、对照组、样本量、预期判据（sim 预测值区间）}
判据的 sim 预测值留接口给 umasim 输出（当前用占位区间，接入后自动填）。
"""
import argparse, sys

try:
    import yaml
except ImportError:
    print("需要 pyyaml：pip install pyyaml"); sys.exit(1)

def design(mech):
    hint = mech.get("probe_hint", "")
    return {
        "experiment_id": f"EXP-{mech['id']}",
        "mechanism": mech["name"],
        "current_confidence": mech["confidence"],
        "independent_variable": hint or "待定义",
        "control": "同种子同输入，只改自变量",
        "sample_size": 5,
        "expected_criterion": f"真机观测值落入 umasim 预测区间（{mech['name']}），落入=confirm",
        "evidence_file": f"out/evidence_{mech['id']}.json",
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confidence", default="probe/confidence.yaml")
    ap.add_argument("--top", type=int, default=3, help="取置信度最低的 N 条")
    a = ap.parse_args()
    book = yaml.safe_load(open(a.confidence, encoding="utf-8"))
    ranked = sorted(book["mechanisms"], key=lambda m: m["confidence"])[:a.top]
    print(f"== 最值得验证的 {len(ranked)} 条机制 ==\n")
    for mech in ranked:
        exp = design(mech)
        print(f"[{exp['experiment_id']}] {mech['name']}（置信度 {mech['confidence']}）")
        print(f"  自变量：{exp['independent_variable']}")
        print(f"  判据：{exp['expected_criterion']}")
        print(f"  依据：{mech['source']}\n")

if __name__ == "__main__":
    main()
