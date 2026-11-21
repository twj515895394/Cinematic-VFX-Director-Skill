# 上游原件复用路由（Copy-First Adapter）

> 文件用途：只提供调用与选型映射，不替上游重写相同的美术理论或规则。这里标注的目录路径均为本仓库已导入的文件。

## 1. 先查阅已有上游，再增补项目特有逻辑

| 任务类型 | 优先直接读取的上游原件 | 本项目额外处理 |
|---|---|---|
| 特效形状与运动规律 | [rng-vfx/elements](../third_party/rng-vfx/skills/rng-vfx/references/elements.md)、[motion](../third_party/rng-vfx/skills/rng-vfx/references/motion.md) | 绑定用户镜头与动作而非游戏战斗动作 |
| 物理运动与环境反馈 | [rng-vfx/physics](../third_party/rng-vfx/skills/rng-vfx/references/physics.md)、[craft](../third_party/rng-vfx/skills/rng-vfx/references/craft.md) | 区分写实/超自然因果、只保留镜头可见内容 |
| 发光、曝光、后期 | [rng-vfx/brightness](../third_party/rng-vfx/skills/rng-vfx/references/brightness.md) | 从引擎参数提取视觉效果要求，不照搬引擎命令 |
| 动漫/卡通/写实风格 | [rng-vfx/styles](../third_party/rng-vfx/skills/rng-vfx/references/styles) | 通过 [四维 taxonomy](../references/taxonomy.md) 再路由 MJ 柔光、日系 CG、2.5D 等 |
| 特效设计分层 | [effekseer/design](../third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/design.md)、[layering](../third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/layering.md) | 输出 Effect Card，而不是 Effekseer 粒子项目 |
| 动作触发和动画节奏 | [effekseer/motion](../third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/motion.md)、[timing](../third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/timing.md)、[sequence](../third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/sequence.md) | 相对动作时点，时间必须与输入镜头吻合 |
| 质量检查与修复 | [effekseer/review](../third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/review.md)、[vfx-review/SKILL.md](../third_party/effekseer-vfx-skill/skills/vfx-review/SKILL.md) | 增加人物/镜头不变约束、AI 视频常见变形与遮挡、明确最小修复 |
| 真实感与风格化审美 | [effekseer/realism](../third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/realism.md)、[stylized](../third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/stylized.md) | 依照 medium/style_profiles 做差异化调整 |

## 2. 典型调用顺序
1. 读取原剧本/提示词中的**不可改项**，判断意图和四维路由。
2. 在上述 vendored 文件中优先查找到已存在的规则、案例、设计/审核方法。
3. 必要时再读取本项目专属 [effect-grammar](../references/effect-grammar.md)、[lifecycle](../references/lifecycle.md) 与 [composition](../references/composition-rules.md) 规范以确定镜头节拍和特效层级。
4. 将选型结果转换为 `Effect Card`（预定 Schema），输出独立 `VFX delta`，而不是照抄游戏引擎参数。
5. 审核失败时根据上游原有的审查规则与本项目额外的硬约束做**局部定向修复**。

## 3. 尚待完成
- 当前为 **P1 上游实文件导入与路由文档**，尚未实现从这些文件自动提取原子、执行检索或自动 QC。
- `snowfrost/skill-movie` 中的 566 原子检索工具/词库非常贴合，但上游仓库未查到清晰可供公开再分发的许可证；暂先使用原理与外部引用，不把它的原文或脚本复制到公开仓库。
- `sakuga-vfx` 的动态案例元数据和可视化尚待建立；其实际特效素材受独立许可条款约束。

## 4. 版本和许可证
- rng-vfx: `4d906cff49a82aeb7c0b3a99b82b193320934fa0`，MIT，见 [LICENSE](../third_party/rng-vfx/LICENSE)
- effekseer-vfx-skill: `b0eea1085f2e3e0fa0b5cc77c58c9a845f0bec96`，MIT，见 [LICENSE](../third_party/effekseer-vfx-skill/LICENSE)
- `third_party/` 原样保留上游文件，不直接做内容修改；变更集中在本地 `adapters/` 或专属 `references/`。
