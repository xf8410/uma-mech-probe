# uma-mech-probe

机制自主探索实验仓 —— 对模拟器**低置信机制**生成扰动实验，真机验证后回填置信度。

克隆自 `xulai1001/umaai-rs`（umasim 完整保留于 `crates/umasim`，源码零改动）。
本仓只新增 `probe/` 实验目录，不碰上游任何代码。

## 思路（stmonty 式自主探索的落地变体）

```
probe/confidence.yaml          机制置信度账本（初始值来自 ledger/历史考古结论）
        │
        ▼
design.py 选出置信度最低的机制 → 生成扰动实验矩阵（每组含预期判据）
        │
        ▼
真机跑实验（hlpatch 采集）→ collect.py 折算成判定结果
        │
        ▼
backfill.py 回填 confidence.yaml（置信度↑或改写机制参数）→ 循环
```

## 用法

```bash
# 1. 列出当前最值得验证的机制
python3 probe/design.py --confidence probe/confidence.yaml --top 3

# 2. 真机跑完后回填（判定=confirm/refute/inconclusive）
python3 probe/backfill.py --confidence probe/confidence.yaml \
  --mech M-001 --verdict confirm --evidence out/evidence_M001.json
```

## 置信度账本初始条目

`confidence.yaml` 预填了 5 条拉面杯机制的当前认知（含依据出处），
其中 `skill_evaluate_bonus`（技能评价加成的游戏内数值映射）置信度最低，
是第一个候选实验。

## 边界

- 本仓不写入 xulai1001 名下任何仓库；回填结论以 PR 形式提给项目组
- 探索对象是**模拟器机制认知**，不是游戏外挂——所有实验在单机育成规则内
