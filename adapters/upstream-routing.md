# 上游原件复用路由（Copy-First Adapter）

> 文件用途：只提供调用与选型映射，不替上游重写相同的美术理论或规则。这里标注的目录路径均为本仓库已导入的文件。

## 0. 首选：原样导入的 skill-movie 影视特效导演与构建引擎
| 使用情境 | **直接复用**的文件 | 本项目薄适配 |
|---|---|---|
| 镜头级意图识别、特效视觉目的、主体可读性 | [cinematic-vfx-director/SKILL.md](../third_party/skill-movie/cinematic-vfx-director/SKILL.md) 及原始 `references/` | 不改变用户角色、动作、机位、时长 |
| 选择特效家族、时序、材料、消散、作用结果 | [vfx-effect-construction-engine/SKILL.md](../third_party/skill-movie/vfx-effect-construction-engine/SKILL.md) 及原始 `references/` | 合并项目四维分类与 Effect Card |
| 566条双语特效原子 | [vfx-atoms.json](../third_party/skill-movie/vfx-effect-construction-engine/references/vfx-atoms.json) | [四维映射](skill_movie_family_map.json) 与 [精选索引](../data/curated_atoms.json) |
| 原子检索与排序 | [原始 search_vfx_atoms.py](../third_party/skill-movie/vfx-effect-construction-engine/scripts/search_vfx_atoms.py) | [薄封装 search_atoms.py](../scripts/search_atoms.py)，直接调用原始 query_terms/score；原数据不改 |

命令：
```bash
python third_party/skill-movie/vfx-effect-construction-engine/scripts/search_vfx_atoms.py "剑气" --limit 8
python scripts/search_atoms.py "剑气" --family weapon --medium semi-realistic-japanese-cg --limit 8 --json
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

**上游依赖说明**：原来的导演/构建 Skill 提到 action-choreography-reference、ai-material-realism、cinematic-audiovisual-language、cinematic-music-sound-design、seedance-vfx 等 Skill；它们属于上游可选协作伙伴，不是本项目运行所必需的强制依赖，不得在本地宣称这些 Skill 已安装。

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
1. 读取原剧本/提示词中的**不可改项**，调用 skill-movie 原始影视 VFX 导演原则并判断四维路由。
2. 根据 skill-movie 的特效家族与原始 566 词库检索，结合 rng-vfx、effekseer 中现成的物理、美术、QC 指南。
3. 必要时再读取本项目专属 [effect-grammar](../references/effect-grammar.md)、[lifecycle](../references/lifecycle.md) 与 [composition](../references/composition-rules.md) 规范以确定镜头节拍和特效层级。
4. 将选型结果转换为 `Effect Card`（预定 Schema），输出独立 `VFX delta`，而不是照抄游戏引擎参数。
5. 审核失败时根据上游原有的审查规则与本项目额外的硬约束做**局部定向修复**。

## 3. 尚待完成
- **P1 已有实际原子检索与单元测试**，并通过 GitHub Actions；仍未实现自动视频画面 QC 和正式模型适配。
- `snowfrost/skill-movie` 两个 Skill、9 篇 references、2 份 agent 元数据、1 份 566 词库及 1 份检索脚本已全部作为原始快照引入，共 15 个文件。
- `sakuga-vfx` 的动态案例元数据和可视化尚待建立；其实际特效素材受独立许可条款约束。

## 4. 上游版本与来源
- skill-movie: `69f6db670ecf305e84f199e418bddbf2c1d988fe`，15 文件，见 `third_party/skill-movie/`；对应原始检索与原子库均未改动。
- rng-vfx: `4d906cff49a82aeb7c0b3a99b82b193320934fa0`，MIT，见 [LICENSE](../third_party/rng-vfx/LICENSE)
- effekseer-vfx-skill: `b0eea1085f2e3e0fa0b5cc77c58c9a845f0bec96`，MIT，见 [LICENSE](../third_party/effekseer-vfx-skill/LICENSE)
- `third_party/` 原样保留上游文件，不直接做内容修改；变更集中在本地 `adapters/` 或专属 `references/`。
