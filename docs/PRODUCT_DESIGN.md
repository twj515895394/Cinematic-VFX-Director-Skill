# Cinematic VFX Director Skill — 产品详细设计文档

> 版本：v1.1（设计补充与 P1 基线）｜日期：2026-11-21｜状态：设计已起草，功能待实现  
> 项目定位：通用影视 CG / AI 视频视觉特效导演 Skill 和可检索知识库，而非游戏战斗特效生成器。

## 1. 产品背景与目标
本项目帮助独立创作者将模糊特效意图、既有故事/分镜/镜头提示词或参考画面，转化为具有物理/超自然因果、可读的时序、空间连续性和媒介风格一致性的镜头级 VFX 设计及模型适配提示词。
- **不重复造轮子**：整合和引用成熟的游戏 VFX、影视 VFX、动画特效美术知识、案例元数据和 Skill 工作流。
- **特效不是装饰**：每一个显著效果必须交代来源、触发、空间锚点、路径、作用对象、环境/光照响应及结束状态。
- **不改变创作意图**：保留用户人物、故事、镜头语言、动作、构图、时长、剪辑方式与叙事节奏；默认只增强 VFX。用户授权时才给出完整优化版。
- **可控、可解释、可检索、可验证**：逐步读取匹配条目，不把术语堆进提示词。
- **个人本地使用优先**：Markdown + JSON + Python 标准库，离线可运行，无数据库/云模型依赖。

## 2. 用户与场景
核心用户：AI 视频创作者、CG 短片导演、故事板/提示词设计者、打斗 Skill 与剪辑 Skill 使用者。

输入情形：
1. **无剧本探索**：「普通少女握住紫色长剑时想有精致能量特效」。
2. **已有镜头增强**：保留原提示词中的角色身份、机位、运动、长度，仅注入必要效果和约束。
3. **已有剧本批量编排**：逐镜头识别需要 VFX 的节拍；镜头间决定是否延续特效状态。
4. **特效修复**：「剑气脱离剑身」「命中点不对」「脸被粒子挡住」「特效像贴纸」。
5. **案例学习 / 查询**：查找风格、效果术语、成因、组合范例和参考来源。
6. **模型输出**：通用稿优先；按明确模型标记适配约束，不凭空宣称模型支持的功能。
7. **跨场景**：非战斗环境（风雨、灾害、粉尘、火焰、水、破坏、变形）、超自然、科幻、科幻 UI 与空间异常、梦境、写实合成等。

## 3. 覆盖范围（四维独立：视觉媒介 × 题材 × 审美风格 × 特效家族）
**媒介 / 渲染轴**：photoreal-live-action、premium-cg、semi-realistic-japanese-cg、anime-2d、stylized-3d、toon-3d、npr-2.5d、mixed-media、unknown。
**题材轴**：modern-action、wuxia、xianxia、mythology、science-fiction、mecha、cyberpunk、superpower、high-fantasy、dark-fantasy、natural-disaster、environmental、transformation、slice-of-life-fantasy。**审美风格 / 风格修饰轴（style profile）**：natural-cinematic、soft-diffused、mj-dreamlike、pixar-like-animation、anime-sakuga、graphic-ink、dark-gritty、high-energy-game-cg、user-defined；允许复合选择、顺序优先级和用户自定义。注意“Pixar-like”只描述通用卡通电影视觉语言、不复刻特定角色或受保护画面；MJ 是美术语汇，不是引擎或特效类别。
**效果家族轴**：weapon、character、motion、impact、elemental、energy、ritual、spatial、technology、environment-weather、destruction-material、transformation、optical-compositing、atmospheric。
四维独立；例如“真人写实 + 东方武侠 + 武器拖尾”与“日系半写实 CG + 校园奇幻 + 武器激活”不应该调用同一套强度与材质描写。

## 4. 非目标
- 不生成真实 VFX 素材或依赖 Unreal/Unity/Effekseer 引擎。
- 不替用户编写或重构剧本、打斗动作及摄影调度；允许提出可选建议。
- 不做视频自动渲染、音频混音、资产托管或联网爬虫。
- 不把所有风格强行变成魔法冲击波、霓虹、粒子爆炸。
- 不要求连续剧情或默认剪辑型叙事；依据每镜头原始设定选择。

## 5. 核心概念与数据模型
### 5.1 VFX Atom（特效原子）
每个原子至少包含：
```json
{
  "id":"weapon.energy-flow",
  "name_zh":"剑刃能量流动",
  "name_en":"Blade Energy Flow",
  "family":"weapon",
  "tags":["blade","energy","flow"],
  "purpose":"表示能量已附着于武器",
  "trigger":"weapon-active",
  "anchor":"blade-surface",
  "geometry":"flow along blade",
  "motion":"tipward stream",
  "interaction":["local-light-spill"],
  "lifecycle":["idle","intensify","settle"],
  "avoid":["detached-projectile"],
  "medium_notes":{},
  "source_ids":["author-original"]
}
```
字段扩展：intensity range、scale、visibility priority、compatibility、source URL、provenance、model risk、examples。source_ids 仅来源标识，不等于任何授权。

### 5.2 Effect Card（特效镜头卡）
```yaml
shot_id: S01
intent: 握剑激活时表现克制而神秘的能量苏醒
medium: semi-realistic-japanese-cg
genre: slice-of-life-fantasy
intensity: L2
primary_read: activation
owner_anchor: right-hand sword grip and blade
trigger: fingers fully close around grip
events:
  - phase: idle
    state: subtle blade emission
  - phase: release
    state: brief violet surge along blade
  - phase: decay
    state: particles settle near blade
environment: colored light on fingers/sleeve/face; wind on hair
constraints: [keep-identity, keep-composition, no-attack, no-detached-projectile]
```

### 5.3 状态机与时序
不强制全流程。可选阶段：idle → anticipation/charge → activation/release → propagation → contact/operation → receiver/environment-response → decay/residue → settled。
- **触发必须可观察**（手指握紧、刀刃碰撞、脚步落地、法阵完成、气象条件变化）。
- **接触必须对齐**，不能提前出现命中特效。
- **空间连续性**：锚点、方向、前后遮挡、距离与尺度一致。
- **效果守恒**：已有武器/能量不应无故变色、换手或消失。
- **多镜头状态**：传递「前一镜头结束状态」到下一镜头，若片段解耦则显式标记重置。

## 6. 主工作流
```text
识别输入/原始约束 → 提取镜头事实 → 判断是否真的需要 VFX
 → 风格/题材/强度路由 → 检索少量原子与参考
 → 构建效果卡（主层+辅助层+环境层）
 → 动作与状态时间轴绑定 → 风格、曝光和空间审查
 → 输出原稿保持版+独立VFX建议（可选增强版）
 → 针对指定模型压缩 → QC → 必要时定向修复
```
**用户明确不给改的要素视为硬约束**。对含糊输入只问会影响效果选择的关键问题；可合理推断时给默认方案并标注假设。纯知识查询无需编造镜头。

## 7. 特效分层、强度与约束
三层：Primary（主形状与信息）、Secondary（受体/环境交互）、Tertiary（细粒子/余韵），每个节拍只允许一个 Primary 重点。强度 L0~L4 是**本项目自定义档位**：
- L0 纯物理 / 写实反馈；L1 克制强化；L2 风格化能量；L3 华丽技能；L4 史诗高强度。
- 强度由剧情、媒介、镜头信息密度与用户意图共同确定；允许 L4，但不是所有镜头都应高强度。
- 禁止默认加入冲击波、光环、魔法阵、飞行剑气、全屏粒子、过强 Bloom。
- 禁止无锚点的漂浮光、无接触的打击闪光、忽略光照/反射/遮挡的“贴纸感”。
- 真实物理与超自然规则区别记录，不强行把魔法解释为现实物理。

## 8. 输出契约
**输出 A（默认）**：不改变原稿的特效设计建议（适合复制进现有提示词）。
**输出 B（可选）**：增强版完整提示词，显式保留/修改差异；原稿保留。
**输出 C**：结构化 Effect Card、时序表和 QC；用户要求时展示。
**输出 D**：参考检索结果（来源链接、标签、可用范围）；不得冒充实测模型效果。
输出语言默认跟随用户；专业术语中英对照。模型不明确时采用模型无关提示词，禁止杜撰专属参数。

## 9. 技术与目录设计
```text
Cinematic-VFX-Director-Skill/
├── SKILL.md                     # 主入口：触发/路由/工作流/输出
├── README.md                    # 安装、使用、示例
├── docs/
│   ├── PRODUCT_DESIGN.md         # 本文
│   ├── IMPLEMENTATION_PLAN.md    # 任务与验收
│   ├── SOURCE_REUSE.md           # 上游来源与修改边界
│   └── ADR/                      # 重大设计决策
├── references/
│   ├── taxonomy.md               # 四维分类、风格路由和术语
│   ├── effect-grammar.md         # 来源→触发→路径→反馈→消散
│   ├── lifecycle.md              # 时序和跨镜头状态
│   ├── intensity-and-hierarchy.md
│   ├── composition-rules.md      # 分层/禁配/组合
│   ├── physics-and-optics.md     # 物理与光照合成
│   ├── qc-rubric.md
│   ├── styles/                   # MJ柔光/动画电影审美/写实调色等修饰配置
│   ├── families/                 # weapon/character/motion/impact/... 各类
│   ├── mediums/                  # photoreal/cg/anime/npr/mixed ...
│   ├── genres/                   # wuxia/xianxia/sci-fi/mythology...
│   └── model-adapters/           # generic/minimax-h3/seedance/...
├── data/
│   ├── atoms/                    # JSONL 分类数据集，默认精选而非整库
│   ├── catalog/                  # 静态/动态视觉案例元数据、来源链接与帧时序
│   ├── profiles/                 # 媒介×题材×审美风格组合规则
│   ├── schemas/                  # atom/effect-card/case/profile JSON Schema
│   └── sources.json              # 上游来源登记
├── scripts/
│   ├── search_atoms.py           # Python 标准库检索
│   ├── validate_data.py          # schema/ID/引用/重复校验
│   └── evaluate_cases.py         # 规则与案例验收
├── examples/
│   ├── weapon-activation.md
│   ├── cinematic-environment.md
│   ├── transformation.md
│   └── realistic-impact.md
└── tests/
    ├── fixtures/                 # 正反例/越界输入
    └── test_*.py                 # 标准库 unittest
```
目录在实施期间按需要逐步创建，不建立空目录占位。

## 10. 外部 Skill 集成
可独立使用或被分镜、动作、剪辑、声音 Skill 调用。主 Skill 接收「已确定的动作/镜头事实」并返回 VFX 效果卡和提示词增量；不修改上游业务对象。多镜头可传递 effect_state_in/effect_state_out，镜头解耦时不强制衔接。音效建议单列为可选，不替声音 Skill 完成设计。

## 11. 上游复用策略与来源
- `snowfrost/skill-movie`：参考 `cinematic-vfx-director` 的事件因果/信息层级、`vfx-effect-construction-engine` 的原子检索与阶段构造；是否拷贝词库须先确认各文件授权和依赖。
- `MRRengi/rng-vfx`：参考 craft/elements/motion/physics/styles、测试范式；需将游戏引擎实现与视频提示词逻辑分离。
- `kanaworksai-hue/effekseer-vfx-skill`：参考案例流程、质量审核、分层方案。
- `kanaworksai-hue/kanaworks-sakuga-vfx`：仅建立分类和案例**链接**，素材二次分发须分别核对授权。
- 优先链接、摘要和转换原创 schema，不无条件搬运全部原文、图片或音视频。
- **授权注意**：个人非商用不自动免除开源许可义务；而本仓库为公开仓库。保留相关许可、署名与来源；授权不明的上游内容仅作为参考，不复制受保护的表达或素材。

## 12. 验收与质量门禁
六维评分（每项 0~2）：因果/触发、锚点/空间、动作时序、风格/强度、环境交互、可读性/约束；总分 12，>=10 且任何维度不得为 0 才通过。
硬性失败：篡改用户的明确禁改项、武器/人物异常、未接触先命中、凭空新增超自然效果、遮脸且未经允许、跨镜头状态自相矛盾、编造模型功能。
回归集至少覆盖：写实武打、日系 CG 激活、2D 动漫斩击、仙侠法阵、科幻机甲、自然灾害、梦境效果、非战斗变形、纯知识检索、已有提示词非侵入式增强。

## 13. 风险与对策
- 术语堆积 → 主效果优先+按需检索+层级上限。
- 输入缺少细节 → 保守默认、明确假设而非空泛询问。
- 上游格式异构 → 自有 schema/适配层/版本来源登记。
- 模型实际生成不稳定 → 用可见动作和几何关系描述，不声明保证成功。
- 素材版权 / 来源追踪 → 链接优先、来源表、授权审计。
- 知识库膨胀 → 首批精选条目、自动校验、检索 Top-K。
- 文档规划与代码脱节 → 每阶段验收及测试后再扩展。

## 14. 开发方式与里程碑
以 `docs/IMPLEMENTATION_PLAN.md` 为唯一任务状态来源；先做可运行最小核心，再增量引入上游知识、扩展覆盖面和模型适配器。任何“已完成”必须对应实际提交与验收记录。

## 15. 对原始整合方案的差距修订（v1.1）
本节为 P1 的输入规格，P1 前先修订设计，再开发。四维轴中 **medium 是呈现载体**、**genre 是世界观/题材**、**style_profile 是审美渲染方向**、**family 是特效形态/功能**，不能将“MJ 风格”误判为魔法粒子，亦不能将“科幻”误判为“蓝色全息”。

### 15.1 四个上游项目的模块级复用地图
| 上游 | 借鉴/复用对象 | 放入本项目 | 改造与排除 |
|---|---|---|---|
| snowfrost/skill-movie: cinematic-vfx-director | 意图识别、主信息/次信息、事件因果、媒介适配、因果诊断 | SKILL.md、references/effect-grammar.md、组合规范 | 不复制其对其他影片子 Skill 的硬依赖 |
| snowfrost/skill-movie: vfx-effect-construction-engine | 特效家族选择、原子检索、卡片、阶段拼装 | data/atoms、data/schemas、scripts、references/lifecycle.md | 566 词库属于上游数据，不默认整库复制；独立核对许可和字段 |
| MRRengi/rng-vfx | animation craft、elements、physics、motion、brightness、styles、评测思路 | references/physics-and-optics.md、styles、mediums、tests | 游戏引擎代码与 AI 视频提示词职责分离 |
| kanaworksai-hue/effekseer-vfx-skill | 设计→分层→审核→修复工作流、正反例 | references/qc-rubric.md、tests、examples | 不复用 Effekseer/Unity 可执行资产链 |
| kanaworksai-hue/kanaworks-sakuga-vfx | 视觉案例编目、元素属性、组合映射、动画演示 | data/catalog、data/schemas/case.schema.json | 保留外链、出处、预览说明；不未经许可再分发视觉素材 |

复用等级：A. 仅参考原理；B. 改写为原创数据模型；C. 符合逐文件授权条件后复制代码/数据；D. 仅外链素材。每个条目记录 source_ids、来源 URL、访问日期、类型、复用级别、可用授权状态及上游 commit（获取后填写）；不得将个人非商用等同于可公开分发。

### 15.2 风格自动路由与歧义规则
按 **用户明确约束 > 原视频/参考中可见信息 > 剧情语境 > 预置默认** 的优先级选择效果。风格识别分别产生 medium、genre、style_profiles[]、family_candidates[]、intensity、confidence、assumptions；未知项标记 unknown，不能给用户虚构确定性。只说“MJ 风格”时，保留柔光梦境/艺术电影/精致奇幻等可选风格路线，视场景选择相对保守默认，必要时只澄清最影响结果的一项。**电影感≠Bloom 越高越好**；光学特性受材质、曝光、景深与场景逻辑约束。

### 15.3 意图、自动选型与组合约束
先判断是否真正需要 VFX（若不需要可建议不加）。之后识别信息功能（速度/状态/接触/规模/转变/空间/气象），选择一个主家族与必要的辅助家族。每个节拍指定 1 个 Primary Read；依据 anchor、trigger、path、receiver、environment、intensity 选择原子；不可用多个强主效果彼此争夺焦点。组合记录 compatible_with、conflicts_with、conditional_requirements、reason；禁止武器附着光因“挥动”自动升级为独立远程能量弹。独立场景、连续分镜与混剪按原剧本决定是否传递状态。

### 15.4 动作同步与真实空间反馈
Effect Card 的事件可用相对动作锚点（at grip / on actual contact / after impact / upon completion）和可选相对时间，不强制给用户未提供的秒数。激活、蓄力、释放、传播、碰撞、衰减只选镜头实际看得到的阶段。优先计算视觉上可理解的方向、接触点、前后景遮挡、反射/光照投射、受体的变化；超自然事件需自洽的世界观规则，而不是强行真实物理。

### 15.5 可检索的视觉案例库（不只是术语）
一个 `Case` 至少需要：case_id、title、medium、genres、style_profiles、family_ids、atom_ids、description、source_url、source_id、license_notes、static_preview_url（可空）、motion_preview_url（可空）、time_markers（可空）、observed_strengths、failure_modes、reproduction_notes；对任何无法证实的视觉/许可证信息必须标注 unknown。
- 支持**静态参考**（封面/截图的外部 URL）、**动态参考**（GIF/视频外链）、**分镜关键阶段**（标明时间段与效果变化），不默认打包外部文件。
- 基于静态或动态案例分析特效怎样出现、运动、交互和消散，而不只是列「火球」「剑气」等名称。
- 案例可关联多个原子及其组合角色（primary/secondary/tertiary），支持以场景、媒介、风格、家族及模型风险过滤。
- 第一期仅定义 schema 和字段规范；案例检索及预览接口依 P4/P5 演进。**不把外链图或视频误写为已经本地验证可播放。**

### 15.6 通用提示词输出和模型适配层
先由导演输出模型无关 `Effect Card` 和最小必要的 VFX Prompt Delta；模型适配器只负责翻译/压缩表述与风险提示，不可擅自增加第二套特效概念。模型适配元数据：adapter_id、supported_scenarios、prompt_pattern、known_limitations、evidence_date、evidence_url、confidence；没有验证过的能力不写为确定事实。目标可包括 MiniMax H3、Seedance、Kling、Veo、Wan；P1 只保留通用接口，具体适配晚于 P3。

### 15.7 非侵入式协议与 QC 定向修复
输入保留 `source_prompt`（原始文本）、`immutable_constraints`、`editable_scope` 和镜头事实；默认输出 `vfx_delta`，不覆写 `source_prompt`。可选 integrated_prompt 必须基于用户允许的范围，并列出 `changes`，禁止暗改镜头数量、动作先后、机位、服装、身份或时长。
QC 不仅打分，还分类诊断：CAUSALITY（来源/因果）、TIMING（提前/拖延）、SPATIAL（错位/遮挡）、LOOK（过曝/廉价）、CONTINUITY（颜色/形态跳变）、COMPOSITION（主次失焦）、MODEL_RISK（语义过载/变形风险）、SCOPE（越权修改）。每项返回 evidence、severity、affected_beat、minimal_fix、protected_constraints。优先局部修复而非全篇重写。

## 16. P1 首批交付范围（设计门禁）
P1 必须落地：四维分类 `taxonomy.md`、事件语法 `effect-grammar.md`、`lifecycle.md`、`intensity-and-hierarchy.md`、`composition-rules.md`、两个可解析 JSON Schema、至少 16 条精选原子（横跨战斗与非战斗）、至少 5 个跨风格代表性 Effect Card 示例。还应明确定义 Case schema（可先实现空案例集）。P1 只交付数据与设计语法；脚本检索、自动校验及全面 QC 落在 P2/P6，不提前声称已实现。
