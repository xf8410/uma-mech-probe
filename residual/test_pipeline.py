"""链路自测：样例对齐→训练→报告全链路可跑。"""
import subprocess, sys, os, json

HERE = os.path.dirname(os.path.abspath(__file__))

def test_compare_finds_seeded_gaps():
    out = os.path.join(HERE, "out_test_residual.json")
    r = subprocess.run([sys.executable, os.path.join(HERE, "compare.py"),
                        "--sim", os.path.join(HERE, "sample/sim_turn12.json"),
                        "--real", os.path.join(HERE, "sample/real_turn12.json"),
                        "-o", out], capture_output=True, text=True)
    assert r.returncode == 2, "样例含已知偏差，退出码应为 2"
    d = json.load(open(out, encoding="utf-8"))
    paths = {row["path"] for row in d["rows"] if row["kind"] == "structure_gap"}
    assert "secret_bonus" in paths, "结构缺口应抓到 secret_bonus"

def test_train_produces_report():
    rep = os.path.join(HERE, "sample/blindspots.md")
    assert os.path.exists(rep) and os.path.getsize(rep) > 50
