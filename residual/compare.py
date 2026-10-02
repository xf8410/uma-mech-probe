#!/usr/bin/env python3
"""compare.py —— umasim 预测 vs 真机实际 的字段级对齐与残差提取。

输入：同种子同输入下，模拟器输出 JSON 与真机采集 JSON（hlpatch 管道产物）。
输出：残差 JSON（每字段路径 → {sim, real, residual, kind}）。
"""
import argparse, json, sys

NUMERIC = (int, float)

def flatten(obj, prefix=""):
    """递归展平 JSON 为 {路径: 值}，列表用 [i] 下标。"""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out

def compare(sim, real):
    fs, fr = flatten(sim), flatten(real)
    rows = []
    for path in sorted(set(fs) | set(fr)):
        s, r = fs.get(path, "<missing>"), fr.get(path, "<missing>")
        if s == "<missing>" or r == "<missing>":
            rows.append({"path": path, "sim": s, "real": r, "kind": "structure_gap"})
        elif isinstance(s, NUMERIC) and isinstance(r, NUMERIC):
            rows.append({"path": path, "sim": s, "real": r,
                         "residual": r - s, "kind": "numeric"})
        elif s != r:
            rows.append({"path": path, "sim": s, "real": r, "kind": "categorical"})
    return {"meta": {"sim_fields": len(fs), "real_fields": len(fr),
                     "compared": len(rows)},
            "rows": rows}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", required=True, help="umasim 输出 JSON")
    ap.add_argument("--real", required=True, help="真机采集 JSON")
    ap.add_argument("-o", "--out", required=True, help="残差 JSON 输出")
    a = ap.parse_args()
    sim = json.load(open(a.sim, encoding="utf-8"))
    real = json.load(open(a.real, encoding="utf-8"))
    result = compare(sim, real)
    gaps = sum(1 for x in result["rows"] if x["kind"] == "structure_gap")
    resid = sum(1 for x in result["rows"] if x["kind"] == "numeric" and x["residual"] != 0)
    print(f"字段对比 {result['meta']['compared']}：数值残差 {resid}、结构缺口 {gaps}、其余一致")
    json.dump(result, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if gaps or resid:
        sys.exit(2)  # 有偏差=实验有发现，退出码供 CI 提醒

if __name__ == "__main__":
    main()
