#!/usr/bin/env python3
"""backfill.py —— 真机验证结果回填置信度账本（confirm/refute/inconclusive）。

规则：
  confirm      → confidence 向 1.0 靠（+0.2，封顶 0.95，留开放心态）
  refute       → confidence 置 0.05，同时把 probe_hint 标记为"需重审机制"
  inconclusive → 不变，记录待重试
每次回填在账本尾部追加 evidence 记录（文件名+判定+时间），全程可追溯。
"""
import argparse, datetime, sys

try:
    import yaml
except ImportError:
    print("需要 pyyaml：pip install pyyaml"); sys.exit(1)

DELTA = {"confirm": +0.2, "refute": None, "inconclusive": 0.0}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confidence", default="probe/confidence.yaml")
    ap.add_argument("--mech", required=True, help="机制 id，如 M-001")
    ap.add_argument("--verdict", required=True, choices=list(DELTA))
    ap.add_argument("--evidence", required=True, help="证据文件路径")
    a = ap.parse_args()
    text = open(a.confidence, encoding="utf-8").read()
    import yaml as _y
    book = _y.safe_load(text)
    mech = next((m for m in book["mechanisms"] if m["id"] == a.mech), None)
    if mech is None:
        print(f"账本里没有 {a.mech}"); sys.exit(1)
    old = mech["confidence"]
    if a.verdict == "confirm":
        mech["confidence"] = min(0.95, round(old + 0.2, 2))
    elif a.verdict == "refute":
        mech["confidence"] = 0.05
        mech["probe_hint"] = "★ REFUTED：机制需重审，旧 probe_hint 作废"
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    mech.setdefault("evidence_log", []).append(
        {"verdict": a.verdict, "evidence": a.evidence, "at": stamp,
         "confidence_before": old, "confidence_after": mech["confidence"]})
    with open(a.confidence, "w", encoding="utf-8") as w:
        _y.safe_dump(book, w, allow_unicode=True, sort_keys=False)
    print(f"{a.mech} [{a.verdict}] 置信度 {old} → {mech['confidence']}（证据 {a.evidence}）")

if __name__ == "__main__":
    main()
