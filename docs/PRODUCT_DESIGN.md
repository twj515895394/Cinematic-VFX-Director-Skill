# Cinematic VFX Director Skill — 产品详细设计文档

> 版本：v1.0（设计基线）｜日期：2026-11-21｜状态：设计已起草，功能待实现  
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

## 3. 覆盖范围（题材 ≠ 视觉媒介）
**媒介 / 渲染轴**：photoreal-live-action、premium-cg、semi-realistic-japanese-cg、anime-2d、stylized-3d、toon-pixar-like（仅风格描述，不仿制特定受保护资产）、npr-2.5d、mj-dreamlike（审美方向）、mixed-media。
**题材轴**：modern-action、wuxia、xianxia、mythology、science-fiction、mecha、cyberpunk、superpower、high-fantasy、dark-fantasy、natural-disaster、environmental、transformation、slice-of-life-fantasy。
**效果家族轴**：weapon、character、motion、impact、elemental、energy、ritual、spatial、technology、environment-weather、destruction-material、transformation、optical-compositing、atmospheric。
三轴正交；例如“真人写实 + 东方武侠 + 武器拖尾”与“日系半写实 CG + 校园奇幻 + 武器激活”不应该调用同一套强度与材质描写。

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
│   ├── taxonomy.md               # 三轴分类和术语
│   ├── effect-grammar.md         # 来源→触发→路径→反馈→消散
│   ├── lifecycle.md              # 时序和跨镜头状态
│   ├── intensity-and-hierarchy.md
│   ├── composition-rules.md      # 分层/禁配/组合
│   ├── physics-and-optics.md     # 物理与光照合成
│   ├── qc-rubric.md
│   ├── families/                 # weapon/character/motion/impact/... 各类
│   ├── mediums/                  # photoreal/cg/anime/npr/mixed ...
│   ├── genres/                   # wuxia/xianxia/sci-fi/mythology...
│   └── model-adapters/           # generic/minimax-h3/seedance/...
├── data/
│   ├── atoms/                    # JSONL 分类数据集，默认精选而非整库
│   ├── catalog/                  # 引用案例元数据，不默认复制素材
│   ├── schemas/                  # atom/effect-card JSON Schema
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
