# uma-sim-residual

残差世界模型实验仓 —— 学 **umasim 预测 vs 真机实际** 的偏差，定位模拟器盲区。

克隆自 `xulai1001/umaai-rs`（umasim 模拟器完整保留于 `crates/umasim`，源码零改动）。
本仓只新增 `residual/` 实验目录，不碰上游任何代码。

## 思路

```
真机采集(hlpatch /summary 等)  ──┐
                                ├─→ compare.py 字段级对齐 → 残差向量
umasim 预测(同种子同输入)      ──┘        │
                                           ▼
                              train.py 小模型(GBDT) 学偏差
                                           │
                                           ▼
                        report.py 盲区排序报告（哪类字段/哪段流程偏差最大）
```

价值：**AI 找模拟器盲区**，而不是替代模拟器——偏差大的地方就是没逆向到的机制。

## 用法

```bash
# 1. 对齐一次真机局与模拟器复现
python3 residual/compare.py --sim sample/sim_turn12.json --real sample/real_turn12.json -o out/residual_turn12.json

# 2. 攒够样本后训练残差模型
python3 residual/train.py --data out/ --model out/residual_model.joblib

# 3. 生成盲区报告
python3 residual/report.py --model out/residual_model.joblib --data out/ -o out/blindspots.md
```

## 样例

`sample/` 内含一回合的最小样例（sim/real 各一份），`pytest residual/` 可直接跑通全链路。

## 边界

- 本仓不写入 xulai1001 名下任何仓库；结论与补丁以 PR 形式提给项目组
- 模型刻意从 GBDT 起步（可解释、CPU 可训），神经网络版等盲区清单稳定后再说
