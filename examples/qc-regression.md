# P6 · 16个影视 VFX QC 正反向设计回归案例

这些文件是**人为编写的文字/Effect Card 设计报告**，不是通过 MiniMax H3、Seedance 渲染产生的真实视频，也不是从真实用户图片中自动检测出来的视觉问题。

- 七个设计可通过样例：`design-good-sword`（日系CG剑）、`design-good-rain`（写实暴雨）、`design-good-mecha`（机甲护盾）、`design-good-underwater`（深海探灯）、`design-good-paperflower`（卡通纸花变化）、`design-good-snow`（雪山风向）、`design-good-sakuga`（二维刀剑接触）。
- 九个设计应拦截样例：`design-bad-early-contact`（接触前火花）、`design-bad-detached-anchor`（剑光漂移）、`design-bad-overexposure`（角色被过曝遮挡）、`design-bad-identity`（角色/道具身份改变）、`design-bad-no-choice`（用户没选就定稿）、`design-bad-state-jump`（连续护盾无故变色）、`design-bad-weather-physics`（风雨逆重力）、`design-bad-unauthorized-action`（擅加攻击）、`design-bad-no-environment`（护盾受光缺失）。

共16例、覆盖两个模型与写实/日系半写实CG/2D动漫/电影CG/卡通等媒介，每例6个分数，共96项维度评估记录。所有案例 `evidence.kind=design-only`、`observed_frame_ids=[]`，不能冒充真实视频审核结果。

## 预期验收

- 7个合格设计：返回 `rubric_passed=true` 且 `design-pass-pending-rendered-review`；不能返回“视频视觉通过”。
- 9个反例：不论是否总分达标都必须返回 `rubric_passed=false`，`next_fix` 恰好一个。包括12分但违反用户确认门禁的案例。
- 任何硬失败直接阻断，不允许通过总分抵消；即使是无硬失败，`0` 分维度和总分不足10仍阻断。
- 经过模拟的“渲染帧报告”只用于测试证据类型、帧索引、独立审核状态与不可能由工具自动验证的边界，绝不在仓库保存伪造的渲染示例并宣称真实出片。

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_data.py
python -m unittest discover -s tests -v
python scripts/review_vfx.py --review tests/fixtures/qc/design-good-sword.json
python scripts/review_vfx.py --review tests/fixtures/qc/design-bad-overexposure.json --json
```
