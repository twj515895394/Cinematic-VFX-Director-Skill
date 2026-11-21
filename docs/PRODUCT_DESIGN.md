# Cinematic VFX Director Skill — 产品详细设计文档

> 版本：v1.6（P5 双视频模型与面向新手的方案选择）｜日期：2026-11-21｜状态：P0–P3完成，P4首批知识案例索引完成，P5新手方案门禁/双模型适配/多镜头状态已完成结构测试；P6–P7待实施  
> 项目定位：通用影视 CG / AI 视频视觉特效导演 Skill 和可检索知识库，而非游戏战斗特效生成器。

## 1. 产品背景与目标
本项目帮助独立创作者将模糊特效意图、既有故事/分镜/镜头提示词或参考画面，转化为具有物理/超自然因果、可读的时序、空间连续性和媒介风格一致性的镜头级 VFX 设计及模型适配提示词。
- **不重复造轮子**：能直接复制并合法复用的上游成熟模块优先复制、再做薄适配；整合和引用成熟的游戏 VFX、影视 VFX、动画特效美术知识、案例元数据和 Skill 工作流。
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
├── third_party/                 # 原样复制的上游 Skill、词库、脚本、专业参考
│   ├── skill-movie/             # 两个 VFX Skill + 566 双语原子 + 检索脚本
│   ├── rng-vfx/                 # 专业特效美术/物理/风格资料
│   └── effekseer-vfx-skill/     # 特效设计/分层/时序/QC
├── adapters/                    # 薄适配层，不重写上游原件
│   ├── upstream-routing.md
│   └── skill_movie_family_map.json
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
- `snowfrost/skill-movie`：已直接导入原始 `cinematic-vfx-director` 与 `vfx-effect-construction-engine` 两个 Skill、完整 566 条原子库、上游 Python 搜索脚本及配套 references；通过薄适配层统一四维分类，详见上游复用记录。
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
| snowfrost/skill-movie: vfx-effect-construction-engine | 特效家族选择、566条原子、原始检索脚本、阶段拼装 | third_party/skill-movie/、adapters/skill_movie_family_map.json、scripts/search_atoms.py | 566词库/搜索代码已原样导入，项目只做映射与调用 |
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
先由导演输出模型无关 `Effect Card` 和最小必要的 VFX Prompt Delta；模型适配器只负责翻译/压缩表述与风险提示，不可擅自增加第二套特效概念。模型适配元数据：adapter_id、supported_scenarios、prompt_pattern、known_limitations、evidence_date、evidence_url、confidence；没有验证过的能力不写为确定事实。**P5用户已明确只做 MiniMax H3 和 Seedance 两种视频模型，未指明默认 MiniMax H3**。当前 `scripts/adapt_prompt.py` 只产生模型专属VFX-only插入段，完整有声模型提示词由Agent在用户授权后按照官方规范编排；不提供 Kling、Veo、Wan 等第三模型适配。

### 15.7 非侵入式协议与 QC 定向修复
输入保留 `source_prompt`（原始文本）、`immutable_constraints`、`editable_scope` 和镜头事实；默认输出 `vfx_delta`，不覆写 `source_prompt`。可选 integrated_prompt 必须基于用户允许的范围，并列出 `changes`，禁止暗改镜头数量、动作先后、机位、服装、身份或时长。
QC 不仅打分，还分类诊断：CAUSALITY（来源/因果）、TIMING（提前/拖延）、SPATIAL（错位/遮挡）、LOOK（过曝/廉价）、CONTINUITY（颜色/形态跳变）、COMPOSITION（主次失焦）、MODEL_RISK（语义过载/变形风险）、SCOPE（越权修改）。每项返回 evidence、severity、affected_beat、minimal_fix、protected_constraints。优先局部修复而非全篇重写。

## 16. P1 首批交付范围（设计门禁）
P1 必须落地：四维分类 `taxonomy.md`、事件语法 `effect-grammar.md`、`lifecycle.md`、`intensity-and-hierarchy.md`、`composition-rules.md`、两个可解析 JSON Schema、至少 16 条精选原子（横跨战斗与非战斗）、至少 5 个跨风格代表性 Effect Card 示例。还应明确定义 Case schema（可先实现空案例集）。P1 以设计语法、数据模型和上游复用为主要范围；原始检索与薄适配检索已提前落地，P2 继续完善查询、自动校验与回归；自动视觉 QC 落在 P6。

## 17. Copy-First / Adapt-Second：上游优先复用（2026-11-21 决策）
**最高优先级：上游已有成熟实现，能直接复制复用再调整适配，就不要重新造轮子或重写。** 此原则适用 P1～P7 全阶段，包括专业特效知识、术语数据、检索工具、Skill 工作流、案例元数据与 QC。

1. **先查再做**：每项开发先盘点上游现成模块，比较契约/依赖/授权/质量。已有模块满足大部分需求时先复制并复用，而不是“看过以后重新写一遍”。
2. **Vendor 原件 + 薄适配**：保留上游原始文件于 `third_party/<source-repo>/`，本地 `adapters/` 只处理四维分类、中文别名、影视模型提示词、Effect Card 接口和其他明确差异。上游代码与原创增量物理分离。
3. **优先直接使用成熟代码与知识**：上游检索脚本、术语库、物理/运动规律、质量审核和参考资料在可复用时均不重新实现；只对缺失、冲突或不兼容处新增内容。
4. **支持上游同步**：记录源 repo、源文件路径、commit SHA、LICENSE、改动记录以及原件更新方式；避免修改 vendor 原件使升级困难。
5. **许可边界**：个人非商用不自动授权公开再分发；本 GitHub 为公开仓库。MIT 等允许复制的资源附带原始许可证与署名即可复用；无明确授权的内容仅研究、链接或在获得许可后再复制。第三方媒体与代码许可证独立评估。
6. **复用优先级**：合法复制原件 > 原件 + Adapter > 以外部链接/调用复用 > 针对实际缺口原创；如果不采用现成方案，须记录不复用的具体理由。
7. **验收必须可追踪**：每个阶段说明直接复用了哪些原文件、适配了哪些差异、哪些真正新增，避免虚构“已整合”的状态。

### 17.1 上游优先接入图
| 上游 | 首选直接复用 | 本项目适配 |
|---|---|---|
| rng-vfx | craft、elements、motion、physics、brightness、styles 等 MIT 原件 | 四维风格路由、效果卡字段与中文使用说明 |
| effekseer-vfx-skill | vfx-review、可复用规则与样例（MIT，逐文件确认） | 视频/镜头特效 QC 输出结构与原稿保护 |
| skill-movie | 特效导演、特效构建、566条原子与原搜索脚本 | 15个原始文件已导入；项目通过映射与薄封装调用原件，而非重写 |
| kanaworks-sakuga-vfx | MIT 代码/工具（需要才复制） | 动态案例首先链接与元数据映射，特效媒体遵循单独许可 |

### 17.2 P1 调整
P1 保留原创 `references/` 文档与 Schema 作为四维映射桥接层，优先使用已导入的上游 566 原子和原始检索逻辑。31条精选原子是指向上游 ID 的索引，不复制或重写它们。只对确实不存在的影视特效原子增量补充。

## 18. P1 实际落地与兼容契约（2026-11-21）
- 已固定 `skill-movie` 上游 commit：`69f6db670ecf305e84f199e418bddbf2c1d988fe`；15 个原始文件置于 `third_party/skill-movie/`。
- 566 原子原生字段为 `id/category/role/family/zh/en`，**不要直接声称它们满足本项目扩展的 rich Atom schema**。`data/schemas/atom.schema.json` 为新增原子模板；原有 566 条始终保留其原生格式。
- `adapters/skill_movie_family_map.json` 将上游 20 个家族映射为本项目效果家族候选；不强行将视觉媒介或题材写入原子。样式、媒介、题材属于查询上下文，须由主 Skill 在结合具体镜头后决策。
- `scripts/search_atoms.py` 复用上游 `query_terms/score` 函数并增补影视分类过滤；`data/curated_atoms.json` 提供31条跨战斗/非战斗的上游 ID 索引；`examples/effect-cards.json` 提供六种应用。
- 原始导演 Skill 提及的动作、摄影、材质、声音和模型适配等其他 Skill **均属于可选集成**；在本仓库不是强制依赖。主 Skill 保持独立运行。
- 自动化 CI：`python scripts/validate_data.py` 与 `python -m unittest discover -s tests -v` 已在 GitHub Actions 通过（8项单元测试），但不等于已完成模型效果实测或自动视频 QC。

## 19. P3 实际交付与边界（2026-11-21）
- **六类请求路由**（knowledge/explore/augment/design/repair/multi-shot）与四维风格判断：`references/director-workflow.md`，根 `SKILL.md` 负责指挥 Agent 按已有上游规范作特效判断。
- **组合与保护边界**：`references/combination-gates.md`，强调事件存在性、真实接触、来源锚点、一节拍一个 Primary Read、禁止默认冲击波/脱体剑气及覆盖人物与镜头。
- **输出契约**：`references/output-contract.md`，默认原稿 + 独立 VFX delta；用户授权且 Effect Card 同时标记批准范围时才能追加式整合，禁止隐式重写原有提示词章节。
- **可执行编译**：`scripts/compile_prompt.py` 将已由导演或创作者确认的 `vfx_delta` 编成可复制文本；复用 JSON Schema 来验证卡片及上游 atom ID。工具不会根据镜头文字凭空生成 Effect Card，也不会自动识别画面或判断视觉美学。
- **可使用的10张单镜头卡**：`examples/p3-ten-cards.json` 与 `examples/ten-shot-validation.md`，覆盖日系CG、武侠动作、真实环境、机甲、空间、材质变形、符文、雪暴、人物发力和水下散射。
- **验收**：自动化测试 50项通过（GitHub Actions: https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44861128206），涵盖原文逐字保留、未授权整合拒绝、Atom 引用、Schema、十个可运行场景；这属于**结构/功能测试**，不是视频生成质量测试。
- P4继续扩充各视觉家族和动态案例；P5处理具体视频模型适配和多镜头；P6需独立评测影片/渲染结果并给定向修复，不得将本阶段的字段校验冒称自动影视 QC。

## 20. P4 已落地架构与证据边界（2026-11-21）

### 20.1 46条四维指导配置
`data/profiles/cinematic_profiles.json`：14类特效家族、9种媒介（含unknown）、14类题材与9种审美 Profile。每项包含镜头级VFX工作、材质/锚点或审美处理原则、可操作避免项和原始上游参考文件路径。`scripts/lookup_profile.py` 按明确 Axis/ID 定位所需的单个配置。原始艺术知识来自已复制的 skill-movie、rng-vfx、effekseer 原件；Profile 仅负责多来源间电影创作适配，避免重新书写同一套物理、美术和动画基础知识。

### 20.2 原 Sakuga 90条动态案例目录原样复用
原 `kanaworksai-hue/kanaworks-sakuga-vfx` 的 `catalog.json` 与 `LICENSE.md` 已作为固定版本直接复制到 `third_party/kanaworks-sakuga-vfx/`，上游commit `7cfc9e6bd6ecc0239f3c141e9c5c42cbdc8bb365`。原目录包含90条、9元素、9形态，保留 frames/fps/contact_frame、loop、tags、use_cases、pairs、FX 组件结构。由 `adapters/sakuga_catalog.py` 投影到 `data/catalog/cases.json` 的统一 Case schema；`scripts/search_cases.py` 支持基于源数据的元素/形态/标签/配对/媒体查询，源原件从不改动，`--check` 防止脱离源版本。

每条记录保存来源资产目录、预览 WebP 外链、真实来源信息和版权署名、元数据来源状态。**90案例仅代表原上游动漫游戏特效库，且均为metadata-only**；不宣称每个都做过逐帧视觉审核、不把其生成方式当作大模型视频生成能力、不自动添加电影题材、MJ柔光、真人写实适用性或未验证的566条Atom对应ID。

### 20.3 质量门禁与待补差距
自动验证扩展到6类JSON Schema、全部46 Profile/关联上游参考路径、90 Case/来源完整映射及其配对关系，并以 [CI #44862387129](https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44862387129) 验证67项单测全部成功。
P4 对“视觉案例库”的**首批**承诺已实现，覆盖的是动漫游戏类参考和完整的全题材**知识路由**；写实电影、日系半写实CG、MJ审美、动画电影和非战斗灾害的真实视觉案例证据尚需增补。该扩充不应阻塞 P5 的通用模型适配和多镜头状态开发，也不应以无证据推断填充。

## 21. P5 完成：新手友好的选择优先工作流（2026-11-21）

### 21.1 输入不再要求用户懂 VFX
默认适配“仅提供某个场景、原视频提示词、图片/参考视频，然后说帮我加点特效”的普通创作者。Agent 必须根据可见事实（角色、环境、动作、光源、材质、机位、世界观）、四轴 Profile、上游566词 VFX 原子与专业构建规则作出专业判断，并提供 **3–5个匹配且有明显差异的可选VFX方案**，逐一解释：
1. 普通用户可理解的方案标题（不要只有专业缩写）；
2. 画面具体会发生什么变化；
3. 为什么适用于该用户给的镜头/图片；
4. 特效强度以及副作用/不应修改内容。

标出一项推荐，但**不替用户预选**；在用户明确选定或授权组合前不生成被视为最终的 Effect Card/模型提示词。图片只有单帧时，未来动作不能凭空认定，未知部分需标注。若用户指定了非常明确的特效则直达效果设计，不机械要求多轮选择。用户要求不加特效时尊重。完整规则见 `references/choice-first-workflow.md`，结构契约见 `data/schemas/recommendation-package.schema.json`；`scripts/recommend_options.py` 提供3–5候选包验证和已选方案门禁，**不假装能自行识别图片内容**。已有三种测试输入、共12个候选方案。

### 21.2 只支持两个视频模型，H3 为默认
- **MiniMax H3**：用户未明说模型时使用；官方 `MiniMax-AI/MiniMax-H3` Skill及两份原始提示词指南已复制到 `third_party/minimax-h3/`（固定上游 SHA `199b7d0e1fd95e7b3eafa8c15eca692534142427`）。Agent 按官方 T2VA/I2VA/FL2VA/L2VA/Ref2VA 选择输入模式，不能假设用户提供了参考附件。
- **Seedance**：仅用户明确选择时使用；参考字节跳动官方 Seedance 2.0/2.5 资料，不强制猜测用户实际版本/平台参数。按用户提供的真实引用媒体和镜头特效因果编排，不改动作和原镜头语言。
- `data/model_profiles.json` 为仅含 `minimax-h3` / `seedance` 的模型策略表，`scripts/adapt_prompt.py` 复用P3已审核的卡片和原稿保护编译。返回的模型专属文本是**VFX插入片段，不是完整的官方有声模型提示词**；用户要求完整稿时需再由Agent按照实际模型官方模板做审稿与编排，不能任意插入不存在的演员、镜头、对白、音轨、参考标签或隐藏模型参数。
- 默认用户没明说要完整整合稿时输出“原内容逐字保留 + 独立特效补充”，双授权门禁仍然生效。

### 21.3 多镜头剧情和独立混剪并存
`data/schemas/shot-sequence.schema.json` 与 `scripts/check_shot_states.py` 结构性校验：`continue` 明确延续同一特效的身份/颜色/锚点/尺度/状态，`reset` 需注明原因，`independent` 不强行继承上一镜头。测试包含3个连续剧情、3个独立混剪和1个明确跳时重置例；不强制轻剧情Vlog变成MV式解耦，也不让剪辑混剪被强制连续。

### 21.4 验收与能力边界
现有 [GitHub Actions #44863374042](https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44863374042) 已通过 **92项自动化测试、9套Schema检查**，覆盖默认H3/显式Seedance、3–5选项/确认、图像媒体引用门禁、原稿无侵入及镜头状态矛盾。测试验证的是**Agent可执行指令与离线数据/脚本**，不等于真实图片已被脚本自动理解，也不等于已调用 MiniMax/Seedance 视频生成或完成视频画面质量评测。P6才将真实输出QC与修复放进核心目标。
