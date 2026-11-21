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
- P4 已通过原始 `catalog.json` 建立90条可检索 Sakuga 视觉案例元数据与预览外链，`scripts/search_cases.py` 可按元素、形态、标签、组合关系查询；真实视觉逐帧审核仍未进行。

## 3.1 P4 视觉案例与全题材风格指导（直接复用原上游）

| 用途 | 优先使用的已存在资源 | 本项目薄适配 |
|---|---|---|
| 14类特效家族 / 9种媒介 / 14类题材 / 9种审美风格 | skill-movie 特效家族图鉴和媒介整合、rng-vfx 运动物理、effekseer 风格化/写实指南 | `data/profiles/cinematic_profiles.json`；`scripts/lookup_profile.py` 按实际四维路由 |
| 手绘特效动态案例、元素属性、可组合素材 | [Sakuga 原版 catalog.json](../third_party/kanaworks-sakuga-vfx/catalog.json)，原始90条元数据 | [90条来源案例](../data/catalog/cases.json) 与 `scripts/search_cases.py` |
| 可观察的触发、组合链和音画层级 | 原目录 `contact_frame`、`pairs`、`fx` 元数据 | 源 Contact Frame 和 `paired_source_ids` 索引；未审核的视觉信息不编造 |
| 来源索引版本与更新 | 原 catalog 与 [LICENSE](../third_party/kanaworks-sakuga-vfx/LICENSE.md) | `adapters/sakuga_catalog.py --check` 保证派生案例未漂移 |

**只有 Sakuga 源案例被标记为二维动漫游戏特效**，绝不把它作为真人写实/MJ柔光/非战斗电影场景的已验证成品案例。具体的风格适配仍使用上述直接复用的专业参考资料，而不是简单给所有原子贴上 “Pixar/MJ/科幻” 标签。

## 4. 上游版本与来源
- skill-movie: `69f6db670ecf305e84f199e418bddbf2c1d988fe`，15 文件，见 `third_party/skill-movie/`；对应原始检索与原子库均未改动。
- rng-vfx: `4d906cff49a82aeb7c0b3a99b82b193320934fa0`，MIT，见 [LICENSE](../third_party/rng-vfx/LICENSE)
- effekseer-vfx-skill: `b0eea1085f2e3e0fa0b5cc77c58c9a845f0bec96`，MIT，见 [LICENSE](../third_party/effekseer-vfx-skill/LICENSE)
- kanaworks-sakuga-vfx: `7cfc9e6bd6ecc0239f3c141e9c5c42cbdc8bb365`，2个源文件（catalog.json + LICENSE.md）；对应90条已转成可查询引用，没有复制预览与游戏特效素材集合。
- `third_party/` 原样保留上游文件，不直接做内容修改；变更集中在本地 `adapters/` 或专属 `references/`。

## P5 只接入 MiniMax H3 与 Seedance（不做第三模型）

- 原版 MiniMax H3 上游 Skill：`third_party/minimax-h3/skills/h3-prompt-writing/SKILL.md`，原始 `references/base-en.txt`、`ref-en.txt`。上游 `MiniMax-AI/MiniMax-H3` commit `199b7d0e1fd95e7b3eafa8c15eca692534142427`，3文件原样复制。Agent 需按真实媒体输入选择 T2VA/I2VA/FL2VA/L2VA/Ref2VA，不重新发明其提示词字段。
- Seedance：参考字节跳动官方 [2.0发布](https://seed.bytedance.com/en/blog/seedance-2-0-official-launch) 和 [2.5发布](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)，采用不限定小版本的参考与可见因果规则；不复制不可证实的 API 参数。
- `data/model_profiles.json` 只有 `minimax-h3`、`seedance` 两个条目，默认 `minimax-h3`；`scripts/adapt_prompt.py` 复用现有 P3 编译器，只输出模型专属 **VFX-only 插入**，不重写故事。
- 模糊场景/图片输入先调用 [新手3–5推荐流程](../references/choice-first-workflow.md)，Agent 读原文和原始566原子后产出备选；用户明确确认后才出 Effect Card。
- 多镜头状态 `scripts/check_shot_states.py`：只检查连续镜头的同一个VFX在剪辑点的字段，不强制混剪镜头互相承接。
