# Cinematic-VFX-Director-Skill

**中文简介：** 面向 AI 视频创作者的通用电影级 VFX 特效导演与知识库。覆盖真人写实、日系半写实 CG、二维动漫、卡通电影、武侠仙侠、科幻机甲、MJ 梦境审美、自然灾害、环境、变形和非战斗特效。可从场景、图片、视频或分镜判断特效需求，模糊情况下先推荐 3–5 个方案供用户选择；默认 MiniMax H3，也支持明确指定 Seedance。保留原剧情、人物、动作与机位，并提供特效提示词补充和审核建议。

**English introduction:** A cinematic VFX direction skill and searchable knowledge base for AI video creators. It supports live action, semi-realistic Japanese CG, 2D anime, stylized film CG, wuxia/xianxia, sci-fi and mecha, dreamlike aesthetics, weather and disasters, environmental effects, transformations, and noncombat scenes. Given a scene, image, video, or storyboard, it recommends 3–5 suitable effects when the VFX direction is unclear, waits for user selection, and then supplies causally grounded, model-aware VFX prompt additions and review guidance. MiniMax H3 is the default, with Seedance available on explicit request; the original story, characters, actions, and camera remain intact.

**版本：0.1.0-rc.1（待用户实测）**。P0–P5核心模块及P6设计QC/证据合同/单问题修复已实现；P7一键验收、版本文档、实测手册与真实视频取证准备已交付。**实际MiniMax H3/Seedance出片和独立视觉验收等待用户进行**，因此当前为发布候选而非画质已验证的稳定版。现有90条动漫游戏视觉案例仅是来源元数据。

## 从这里开始（使用与实测）

把完整仓库作为 Agent Skill 读取根 [SKILL.md](SKILL.md)。新手给场景/图片只说“加点VFX”时先收到**3–5个推荐方案**，选定后才拿到 VFX-only 提示词；默认 **MiniMax H3**，用户明确选择 Seedance 时才切换。

```bash
# 在仓库根目录：Windows / macOS / Linux
python -m pip install -r requirements-dev.txt
python scripts/verify_all.py
```

`verify_all.py` 一次完成数据完整性、全量单元测试、外链元数据一致性、模型/用户确认保护、QC回归以及来源和文档检查。**不需要 GPU，也不会调用付费视频模型。** 如需实际从生成视频中抽帧取证（独立的可选能力），本地安装 `ffmpeg`/`ffprobe` 后：

```bash
python scripts/prepare_visual_evidence.py --video my_h3_clip.mp4 --shot-id S01 --model minimax-h3
python scripts/prepare_visual_evidence.py --video my_seedance_clip.mp4 --shot-id S02 --model seedance
```

帧和 SHA-256 记录将写入忽略提交的 `reviews/S01`、`reviews/S02`。可用 `python scripts/check_visual_evidence.py --manifest reviews/S01/evidence-manifest.json --video my_h3_clip.mp4` 验证素材版本及抽帧哈希，**采样或哈希通过都不代表视觉评分通过**。拿到真实视频后请按 [10项用户实测手册](docs/USER_ACCEPTANCE.md) 实际播放、对照原稿、记录问题与帧号。参见 [RC发布说明](docs/RELEASE_NOTES.md) / [变更记录](CHANGELOG.md)。

## 为什么不重复造轮子
目前已经**实际复制并引用**五个成熟上游项目的45个源文件：

| 上游项目 | 原样复用的关键内容 | 文件数 |
|---|---|---:|
| [skill-movie](https://github.com/snowfrost/skill-movie) | cinematic-vfx-director、vfx-effect-construction-engine、**566条原子词库**、原始 Python 检索脚本及 References | 15 |
| [rng-vfx](https://github.com/MRRengi/rng-vfx) | 特效美术理论、元素、物理、运动、亮度、六种风格 | 13 |
| [effekseer-vfx-skill](https://github.com/kanaworksai-hue/effekseer-vfx-skill) | 特效设计、分层、动画时序、独立 QC 规则与流程 | 12 |
| [kanaworks-sakuga-vfx](https://github.com/kanaworksai-hue/kanaworks-sakuga-vfx) | 原版90条动态VFX案例元数据与来源说明（素材保持外链） | 2 |
| [MiniMax H3官方Skill](https://github.com/MiniMax-AI/MiniMax-H3) | 官方完整H3提示词Skill、基础/多参考模式指南（原样保留） | 3 |

原件均保存在 `third_party/`，项目专属逻辑集中在 `adapters/` 与 `references/`。其他上游引用及快照版本见 [来源登记](docs/SOURCE_REUSE.md)。

## Skill 使用
让兼容 Agent Skill 的工具读取根目录 [SKILL.md](SKILL.md)，即可使用导演工作流。**未指定生成模型时默认MiniMax H3，只有用户指定Seedance才切换。** 用户不熟悉VFX、只给场景/图片要“加点特效”时，先提供3–5种解释清楚的适用方案，**等用户选择**后才生成VFX提示词。已有原稿保留人物、动作、机位和时长；整合版本仍需明确授权。

示例请求：
- 「保持原 5 秒镜头和校园少女设定，握住紫色长剑时增加克制的激活能量与环境光响应，但不能挥剑或发射剑气。」
- 「真人写实的暴雨街道如何做湿地反射、水花和空气透视？」
- 「动画二维刀剑碰撞，仅在刀刃真实接触时产生火花。」
- 「给科幻机甲护盾的启动设计薄层扫描、接触式反射，保持外形不变。」
- 「只知道想要 MJ 梦境柔光，先帮我判断适用的特效方向。」

## 检索：原始上游脚本与薄适配脚本
检索运行仅依赖 Python 3.10+ 标准库；完整 Schema 验证复用开发依赖 `jsonschema[format]`，无需云服务或数据库：

```bash
# 上游原始算法：直接使用566条中英双语原子
python third_party/skill-movie/vfx-effect-construction-engine/scripts/search_vfx_atoms.py "剑气" --limit 8

# 项目薄封装：调用上游原始评分逻辑，并使用四维分类上下文
python scripts/search_atoms.py "剑气" --family weapon --limit 5
python scripts/search_atoms.py "雨滴" --family environment-weather --json
# 可重复的精选标签必须全部匹配，当前71种标签覆盖31条精选原子
python scripts/search_atoms.py "雨滴" --tag rain --tag weather --json
# 上游原生字段可过滤
python scripts/search_atoms.py "火花" --role contact-peak --category 命中
python scripts/search_atoms.py "辉光" --medium semi-realistic-japanese-cg --style mj-dreamlike --json

# 数据与回归检查：先安装一次开发验证依赖
python -m pip install -r requirements-dev.txt
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

四维体系：`medium`（媒介）、`genre`（题材）、`style_profiles`（审美）、`family`（特效家族）。**媒介、题材和审美目前是检索上下文，不是对566条原子进行真正筛选；只有 family、role、category 和精选 tag 是实际过滤条件。** 详见 [P2 使用与验证说明](docs/SEARCH_AND_VALIDATION.md)。

## P3 非侵入式 VFX 提示词编排

P3 复用上游导演及构建逻辑，新增 [导演工作流](references/director-workflow.md)、[组合门禁](references/combination-gates.md)、[输出契约](references/output-contract.md)。**默认不重写用户的原提示词**：主 Skill 先理解动作与特效因果，再用 [编译脚本](scripts/compile_prompt.py) 输出原稿+独立的 VFX 增量。

已审核效果卡可以用下面的命令直接编译：

```bash
python -m pip install -r requirements-dev.txt
python scripts/compile_prompt.py --card sample.sword-activation
python scripts/compile_prompt.py --cards examples/p3-ten-cards.json --card p3.power-aura
python scripts/compile_prompt.py --cards examples/p3-ten-cards.json --card p3.dark-ritual --json
```

整合输出只有用户**明确批准**且卡片 `editable_scope=explicitly-approved-integration` 时才能调用 `--integrated --approved`；脚本只追加 VFX 段落，不擅自改动原剧情、动作、机位或时长。原始卡片中的 `vfx_delta` 由 Agent/创作者先审核，脚本不会自行理解剧本或创建未经确认的效果。

[10个单镜头案例及验收说明](examples/ten-shot-validation.md) | [10张可直接运行的效果卡](examples/p3-ten-cards.json)

## P4 四维电影特效知识与90条可检索视觉参考

P4 提供46条带上游来源的影视指导配置：**14个特效家族 × 9种媒介 × 14类题材 × 9种审美配置**（四轴分别查询，不是所有组合已经实测）。

```bash
python scripts/lookup_profile.py --axis family --id environment-weather
python scripts/lookup_profile.py --axis medium --id photoreal-live-action
python scripts/lookup_profile.py --axis style --id mj-dreamlike

# 使用原版 Sakuga 目录生成的90条外部视觉案例索引
python scripts/search_cases.py --element water --form impact --limit 8
python scripts/search_cases.py --paired-with water_charge_01 --json
python scripts/search_cases.py --family impact --style anime-sakuga

# 确认案例索引与上游原版目录完全对应
python adapters/sakuga_catalog.py --check
```

90条案例都是**手绘动漫游戏 VFX** 的原始元数据索引，不是经过逐帧审查的真实电影镜头，也不能视为已验证的 MiniMax H3、Seedance 等模型输出。完整参数和预览链接见 [案例库使用与来源说明](docs/VISUAL_CASE_LIBRARY.md)，专业风格路由见 [四轴电影特效指导](references/cinematic-profile-routing.md)。

## P5 两个视频模型 + 新手优先的特效推荐

**入口规则**：用户只给图片、已有视频场景或一句“帮我加点特效”时，Agent 基于可见/明确事实、原始566条特效原子与46项专业指导，推荐 **3–5个真正不同的选项**。每个用通俗文字解释“看到什么、为什么适合、强度、风险”，并等待用户选定。例如“少女握剑”可以考虑剑刃逐步点亮、剑周轻雾、局部能量聚集、柔和光照反射；不得自动加入挥剑、攻击或变形。

模型仅两个：
- **MiniMax H3（默认）**：上游官方 `h3-prompt-writing` Skill 已复制到 `third_party/minimax-h3/`。按实际输入选择 T2VA、I2VA、FL2VA、L2VA、Ref2VA 规范。
- **Seedance（用户指定）**：采用字节跳动官方资料的通用因果与多模态参考表达；未知具体版本时不假定2.0/2.5隐藏参数。

```bash
# 以下为演示数据包：真实用户图片由Agent分析后动态创建3–5选项
python scripts/recommend_options.py --package examples/recommendations/sword-image.json
python scripts/recommend_options.py --package examples/recommendations/rainy-street.json

# 用户明确确认A1后，才能做下一阶段的已选方案brief
python scripts/recommend_options.py --package examples/recommendations/sword-image.json --select A1 --user-confirmed --json

# 生成已经审核的Effect Card的模型专属VFX插入；默认MiniMax H3
python scripts/adapt_prompt.py --card sample.sword-activation
python scripts/adapt_prompt.py --card sample.rainy-street --model seedance --json

# 三组连续剧情、三组独立混剪和一次重置；本脚本只校验VFX状态
python scripts/check_shot_states.py --file examples/sequences/continuous-sword.json
python scripts/check_shot_states.py --file examples/sequences/montage-weather.json
```

实际从场景/图片分析并设计特效由 Agent 完成；脚本负责结构、用户选择与原稿保护，**不自动识别图片，也不保证模型出片视觉质量**。模型适配输出默认是VFX-only片段，完整H3/Seedance提示词仍按官方规则、用户授权后由Agent排版。

详见：[新手3–5特效方案流程](references/choice-first-workflow.md) · [两模型适配](references/model-adapters.md) · [连续/独立镜头](references/multishot-states.md)

## P6 六维 VFX 审核：设计检查与成片视觉检查分开

优先直接复用已复制的 [effekseer独立特效审核Skill](third_party/effekseer-vfx-skill/skills/vfx-review/SKILL.md) 及 [review](third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/review.md)、[rng-vfx物理规则](third_party/rng-vfx/skills/rng-vfx/references/physics.md)。本项目的薄层适配使用**六维0–2分**：因果、空间、时序、风格强度、环境交互、可读性。

**通过设计评分**需：总分≥10/12、全部维度≥1、没有任何硬性失败。14类硬性失败包括未授权改动作、人物变脸、提前出现碰撞、特效漂移、过曝遮挡、未确认用户特效选项以及跨镜头状态跳变。**每轮只建议一个最优先修复点**；不会自动修改人物、动作、构图或原剧本。

```bash
python -m pip install -r requirements-dev.txt

# 两个是手写的设计审核夹具，绝不是已生成视频证据
python scripts/review_vfx.py --review tests/fixtures/qc/design-good-sword.json
python scripts/review_vfx.py --review tests/fixtures/qc/design-bad-early-contact.json --json

# 设计审核完整性与回归
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

已提供16个跨媒介/题材设计案例（7个达标、9个必须拦截）。**没有生成视频时只能说“设计审核通过、等待真实成片审核”**。真实出片要由能打开实际视频/帧的审核者查看并记录来源和帧号；此Python脚本只能检查证据字段与汇总评分，不能自动识别画面、证明真实视频质量或独立审核身份。

参见：[六维Rubric](references/qc-rubric.md) · [独立审核流程](references/qc-review-workflow.md) · [16个正反例](examples/qc-regression.md)

## 关键文件
- [产品详细设计 v1.8](docs/PRODUCT_DESIGN.md)
- [分阶段实施计划](docs/IMPLEMENTATION_PLAN.md)
- [上游直接复用路由](adapters/upstream-routing.md)
- [四维分类](references/taxonomy.md)
- [31条精选上游原子索引](data/curated_atoms.json)
- [6张 P1 基础 Effect Card](examples/effect-cards.json)
- [10张 P3 可执行 Effect Card](examples/p3-ten-cards.json)
- [P3 导演流程](references/director-workflow.md)
- [P3 输出规范](references/output-contract.md)
- [P4 46条四轴指导配置](data/profiles/cinematic_profiles.json)
- [P4 90条可查视觉案例](data/catalog/cases.json)
- [P4 案例查询与真实来源](docs/VISUAL_CASE_LIBRARY.md)
- [P5 新手3–5方案优先](references/choice-first-workflow.md)
- [P5 两个视频模型](data/model_profiles.json)
- [P5 多镜头状态校验](scripts/check_shot_states.py)
- [P6 六维QC与一轮一修](scripts/review_vfx.py)
- [P6 设计/视觉证据审核规范](references/qc-review-workflow.md)
- [P7 本地一键完整验收](scripts/verify_all.py)
- [P7 10项用户实测手册](docs/USER_ACCEPTANCE.md)
- [P7 发布候选说明](docs/RELEASE_NOTES.md)
- [数据验证脚本](scripts/validate_data.py)
- [P2 检索与完整性校验说明](docs/SEARCH_AND_VALIDATION.md)
- [查看最新 GitHub Actions 验证](https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/workflows/p1-checks.yml)

## 仍待完成
P4可以持续补充真人电影/CG/MJ动态案例；P6实测还需真实 MiniMax H3/Seedance 视频及独立审核者的修复前后验证；正式稳定版需用户实测批准。其余代码、文档、自动化预验收工具已进入发布候选。

**原则：能用成熟上游就直接复用并做薄适配；只对真正缺失的能力开发新模块。**
