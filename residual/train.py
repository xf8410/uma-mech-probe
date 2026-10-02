#!/usr/bin/env python3
"""train.py —— 攒多回合残差样本，训小模型定位系统性盲区。

模型：HistGradientBoosting（sklearn，CPU 秒级，可解释优先）。
特征：字段路径段 one-hot + 回合号；标签：|residual| 是否超阈值。
输出：模型 + 按路径聚合的盲区评分（哪个字段族系统性偏）。
"""
import argparse, json, glob, re, os
import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

THRESHOLD = 0.5  # 数值残差绝对值超过该值记为盲区样本（可按字段量纲调整）

DIM = 64  # 固定特征维度（字段族哈希袋词）

def path_features(path):
    """把 residual.json 的字段路径拆成粗粒度族特征（避免过拟合到单字段）。"""
    segs = re.findall(r"[A-Za-z_]+|\[\d+\]", path)
    return [s for s in segs if not s.startswith("[")]

def vec(segs):
    v = np.zeros(DIM + 1)
    for s in segs:
        v[hash(s) % DIM] += 1.0
    v[DIM] = len(segs)
    return v

def load_rows(data_dir):
    X, y, meta = [], [], []
    for fp in sorted(glob.glob(os.path.join(data_dir, "residual_*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        for row in d["rows"]:
            if row["kind"] == "numeric":
                X.append(vec(path_features(row["path"])))
                y.append(1 if abs(row["residual"]) > THRESHOLD else 0)
                meta.append(row)
    return np.array(X, dtype=float), np.array(y), meta

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="含 residual_*.json 的目录")
    ap.add_argument("--model", default="out/residual_model.joblib")
    ap.add_argument("--report", default="out/blindspots.md")
    a = ap.parse_args()
    X, y, meta = load_rows(a.data)
    if len(X) == 0:
        print("没有可训练样本（先跑 compare.py 攒 residual_*.json）"); return
    model = HistGradientBoostingClassifier(max_iter=120, random_state=0)
    model.fit(X, y)
    os.makedirs(os.path.dirname(a.model) or ".", exist_ok=True)
    joblib.dump(model, a.model)
    # 盲区评分：按字段族聚合"残差超阈比例"
    fam = {}
    for xi, yi, row in zip(X, y, meta):
        key = ".".join(path_features(row["path"])[:3])
        f = fam.setdefault(key, [0, 0])
        f[0] += yi; f[1] += 1
    ranked = sorted(fam.items(), key=lambda kv: kv[1][0] / max(kv[1][1], 1), reverse=True)
    with open(a.report, "w", encoding="utf-8") as w:
        w.write("# 模拟器盲区报告（残差超阈比例排序）\n\n")
        w.write("| 字段族 | 超阈样本 | 总样本 | 超阈率 |\n|---|---|---|---|\n")
        for k, (bad, tot) in ranked[:20]:
            w.write(f"| {k} | {bad} | {tot} | {bad/tot:.0%} |\n")
    print(f"训练样本 {len(X)}，正样本(盲区) {y.sum()}；报告 → {a.report}")

if __name__ == "__main__":
    main()
