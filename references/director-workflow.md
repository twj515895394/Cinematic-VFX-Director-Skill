# P3 · 通用影视 VFX 导演工作流（上游原件 + 本项目薄适配）

核心依据直接复用：
- `third_party/skill-movie/cinematic-vfx-director/SKILL.md`：视觉信息任务、Primary Read、媒介路由、可见事件因果、硬性失败。
- `third_party/skill-movie/vfx-effect-construction-engine/SKILL.md`：形态/生命周期/原子词语检索、动态过程、光照环境响应。
- `third_party/rng-vfx/skills/rng-vfx/references/`：运动物理、材质、亮度与风格；`third_party/effekseer-vfx-skill/skills/vfx-review/`：审核经验。

**不重写上游导演知识；本文件只规定独立影视 Skill 的输入分类、决策权、调用次序和输出契约。**

## 1. 输入模式判定

| 模式 | 触发内容 | 默认产物 |
|---|---|---|
| knowledge | 用户咨询术语、机制、类型、案例原理 | 解说、可检索原子与参考链接；不凭空生成新剧本 |
| explore | 简单意图，如“真实感火焰蔓延” | 1–3个风格适配方向、主效果与关键约束 |
| augment | **已有**镜头提示词/剧本，让特效更好 | 原始内容原样保留 + 独立 VFX 增量（默认） |
| design | 镜头或已有动作明确，要求特效设计 | 可见事件卡 + 简洁 VFX 增量 |
| repair | 特效漂移、遮挡、不符合物理、过曝、时序错 | 可观察问题 → 原因 → 最小修复变量 → 保持不变的部分 |
| multi-shot | 分镜序列或剪辑短片需要多个 VFX | 逐镜头效果卡；是否衔接由剧本决定，默认不强制连续 |

用户只要术语时不要求 Effect Card；无源提示词时不杜撰 `source_prompt`。用户未要求生成完整稿时只输出独立 VFX 增量。

## 2. 主控决定与职责边界
先提取：`source_prompt`（原样）、`immutable_constraints`、`editable_scope`、已存在的动作与触发点、镜头拍摄与时长；未声明的信息标记未知，而不是补写动作。
随后确定**四维**：medium（载体）、genre（题材）、style_profiles（审美）、family（特效目的）；强度 L0–L4 与否需要特效。顺序：用户明确约束 > 源画面/原稿 > 场景语境 > 保守默认。可以建议“不加特效”。

导演（来自上游）决定 `intent/primary_read/intensity/medium`；构建引擎仅在该范围选择 `family/trigger/source/anchor/path/response/decay`。动作编排、角色身份、摄影、声音、剪辑均由已有原稿或其他专属 Skill 决定，本 Skill 不夺权。用户说“MJ 风格”≠魔法，柔光审美只属于 style 层；无攻击动作时不能派生离体剑气。

## 3. 操作流水线（执行次序）
1. **锁定已知事实**：人物身份、道具数量、动作次序、真实接触点、镜头语言、长度、镜头连续或解耦。
2. **判断特效工作**：观众必须在何时看懂哪种状态/力量/接触/空间变化？不服务该信息就不加。
3. **主视觉阅读点**：每个关键节拍只设一个 Primary；Secondary 描述物理/受体/环境证据；Tertiary 可有可无。
4. **利用已复制上游原件**：读取原 `cinematic-vfx-director`、`vfx-effect-construction-engine` 的相应参考；需复杂时查 `rng-vfx` 美术与 `effekseer` 分层。
5. **按需检索，不堆辞藻**：使用 `python scripts/search_atoms.py "<keyword>" --family <family> --limit 8 --json`，原算法来自 skill-movie；选 2–8 个有独立职责的词条（小镜头不强求下限），记录其内部 ID，不将 ID 输出为提示词。
6. **构建 Effect Card**：主体/来源、可观察触发、形态材质、路径与空间、实际操作/接触、环境/光照、峰值、衰减与最终状态。只写镜头可见阶段。静态提示词只写决定性瞬间。
7. **组合判定**：读取 [combination-gates.md](combination-gates.md) 检查从属效果与硬性禁配；不增加无剧本依据的冲击波、攻击、法阵、变形或摄像机运动。
8. **输出编译**：参照 [output-contract.md](output-contract.md) 产生原稿+独立 delta；用户显式批准，才可做追加式完整稿，严禁隐式重写。
9. **交付前编辑审查**：动作→特效触发→作用对象→环境反应→终态因果闭合；视觉主次、空间遮挡、风格合成、人物/武器身份稳定；有疑点给出保守版/修复点，必要时不添加 VFX。

## 4. 与上游固定六段式提示词的关系
上游 `skill-movie` 某些内容采用特定创作框架的六段结构。**本项目是通用影视 Skill，不强制所有用户使用该结构**。遇到用户已经使用固定模板，则将 VFX 信息放进原有相关段落；未提供模板时默认独立 VFX 增量或追加式完整稿。不能擅自插入新镜头、声音或剪辑章节。

## 5. 多镜头
- 连续剧情：追踪 `effect_state_in/out`，确认同一效果的颜色、锚点、状态、前后因果。
- 非连续混剪：可 `independent`，不得要求共用前一镜头的力量状态。
- 跳时或用户明确重置：`reset`。
- P3 演示只验证单镜头与结构约束；多镜头自动一致性生产属于 P5，不应误称已实现。

## 6. 特别注意
搜索返回的 `medium/genre/style` 只是上下文，**不是全量566原子的真实适用性标签**；选择需由当前镜头视觉事实决定。提示词脚本只能将已批准的 Effect Card 编译为文字，不能自行理解视频像素、诊断风格或凭空选型。P6 才扩展自动化审查与针对已渲染视频的 QC。
