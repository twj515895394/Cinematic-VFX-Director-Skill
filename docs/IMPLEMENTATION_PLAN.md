# Cinematic VFX Director Skill — 分阶段实施计划

> 日期 2026-11-21｜版本 v1.9｜状态：发布候选准备完成，等待用户真实视频验收  
> 原则：产品设计与覆盖差距审查 → 实施计划 → 分批开发 → 单元/案例测试 → 更新验收记录；逐步推进；成熟上游优先直接复用，保留原件并在薄适配层补差异。

## 阶段概览
| 阶段 | 任务 | 交付成果 | 验收标准 | 状态 |
|---|---|---|---|---|
| P0 | 文档与入口骨架 | 产品设计、实施计划、README、SKILL.md、来源登记 | 文件可访问、Skill 入口与边界明确（真实触发待集成测试） | 已完成文档验收 |
| P1 | 核心知识与数据模型 | 四维分类、生命周期、三种 Schema、31条上游精选索引、6个Effect Card、skill-movie原件 | 566原子校验、跨题材效果卡与8项测试通过 | 已完成（CI通过） |
| P2 | 检索与校验脚本 | 复用原始搜索算法，补精选标签/原生字段过滤与 Schema/来源完整校验 | 35项测试通过、566原子/31精选/6卡/5 Schema校验 | 已完成（CI通过） |
| P3 | VFX 设计与提示词工作流 | Agent导演决策流程、组合门禁、输出契约、可执行卡片编译器、10场景 | 50项自动测试通过，原文保护/双重整合授权门禁 | 已完成（结构/流程验收） |
| P4 | 全题材知识扩展 | 14家族、9媒介、14题材、9审美Profile，90 Sakuga原始视觉案例索引 | 67项回归、90源案例一致性、46Profile覆盖 | 核心基线完成（跨媒介真实案例继续扩展） |
| P5 | 新手交互、两模型适配与多镜头 | MiniMax H3（默认）/Seedance 双适配、3–5方案先选后写、多镜头状态合同 | 93项测试通过；只有两模型、3–5候选与明确确认门禁；3连续/3独立/1重置案例 | 已完成（结构/功能验收，未实机出片） |
| P6 | 质量审核与定向修复 | 6维0–2设计/成片证据分流、14种硬失败、单问题修复、16个正反例 | 7个设计审核合格、9个问题拦截，实际成片不虚称验证 | 设计QC与报告门禁完成（真实渲染审片待进行） |
| P7 | 发布候选与实测交接 | 一键离线自检、文档/来源检查、真实视频取证、10项验收、RC说明与快照 | CI验证后固定候选分支；稳定版需用户实测批准 | 开发交付完成（RC待最终CI） |

## 设计基线审查（在 P1 前）
- [x] 对照原始整合方案与仓库实际内容，区分覆盖/部分覆盖/缺失。
- [x] 产品设计更新为 v1.1：修正风格与媒介混用，补充四大上游复用地图、静态/动态案例规范、非侵入式协议、模型适配和 QC 分类。
- [x] 按修订方案实施 P1；GitHub Actions 8项测试及数据完整性校验通过。

## P0 文档与骨架（已完成）
- [x] P0.1 阅读目标仓库状态，确认默认分支与写权限（空仓库）。
- [x] P0.2 核验上游至少两个核心模块，记录复用依据。
- [x] P0.3 提交 `docs/PRODUCT_DESIGN.md`。
- [x] P0.4 提交本实施计划。
- [x] P0.5 建立 README 和初始 SKILL.md。
- [x] P0.6 建立 docs/SOURCE_REUSE.md、data/sources.json。
- [x] P0.7 验收 GitHub 路径、入口 Frontmatter 以及文档互相引用。

## Copy-First 开发决策（P1～P7 强制执行）
上游已有成熟模块时，优先直接复制可合法复用的原文件（包括知识、原子、检索、QC），置于 `third_party/`；再通过 `adapters/` 整合。本项目特有差异才原创。每阶段登记来源、原始路径/commit/许可、实际复用、适配差异与测试；不接受无理由重写。

## P1 详细任务
- [x] P1.0 实际导入 rng-vfx 13文件、effekseer-vfx-skill 12文件、skill-movie 15文件；更新实际调用路由并记录来源 commit。
- [x] P1.1 四维 taxonomy（媒介×题材×审美风格×效果家族）和常用中英文同义词。
- [x] P1.2 事件 envelope、特效生命周期与多镜头状态。
- [x] P1.3 Atom（项目增量字段）、Effect Card、Case JSON Schema；保留上游原子原生字段与来源引用，不混淆格式。
- [x] P1.4 复用上游566条原子；精选31个上游ID覆盖武器、人物、光学、雨雪环境、变形、科幻和空间。无需重复创作词库。
- [x] P1.5 强度 L0~L4、Primary/Secondary/Tertiary 层级与禁配规则。
- [x] P1.6 六个跨媒介/题材/风格的 Effect Card，涵盖连续与独立片段。
- [x] P1.7 GitHub Actions 数据完整性检查成功：566原子/566唯一ID、31精选ID、6效果卡、20个上游家族；8项单测通过。完整JSON Schema引擎校验与异常边界仍在P2。
**P1验收已通过**：见 https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44859588112 。源数据与31条索引保持原ID并跨越战斗/非战斗；P2脚本的基础搜索/校验提前落地，完善功能继续执行。

## P2 详细任务
- [x] P2.0 已复制原始 Python 检索脚本；薄适配直接调用上游 query_terms/score，未重新实现检索排名；初步双语、家族、媒介/题材/风格上下文查询已通过测试。
- [x] P2.1 已支持原词库双语关键词及别名排序、上游 category/role、本项目 family、31精选原子的可重复 AND tag、Top-K/JSON；medium/genre/style 属查询上下文，不虚构全量原子适用性过滤（P4 增加适配元数据）。
- [x] P2.2 复用 jsonschema Draft 2020-12 进行5种 Schema/实例验证，覆盖 URI、原子ID、精选标签、Effect Card、来源文件和引用及连续镜头状态；开发阶段依赖 requirements-dev.txt。
- [x] P2.3 新增27个搜索/破坏性注入用例，连同P1共35项测试全部通过；覆盖空查询、无匹配、重复ID、错误来源、缺失字段、错误强度、Case URL及跨镜头状态。
**P2验收完成**：运行 `python -m pip install -r requirements-dev.txt` 后执行 `python scripts/validate_data.py`、`python -m unittest discover -s tests -v`、`python scripts/search_atoms.py sword --limit 5`。GitHub Actions 通过：https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44860320672 。筛选与上下文边界详见 `docs/SEARCH_AND_VALIDATION.md`。

## P3 详细任务
- [x] P3.1 根 SKILL.md 导入六类意图处理、四维风格判定、上游特效选择、非侵入式输出与导演审核分支。
- [x] P3.2 新增 references/combination-gates.md，与上游构建引擎联用；同节拍一项主视觉、接触时序、非必要特效禁配及最小修复。
- [x] P3.3 新增 references/output-contract.md 与 scripts/compile_prompt.py：仅将已确认的 Effect Card.vfx_delta 编译成可复制文本，保证原稿逐字保留；不声称自动创作/选择全新特效。
- [x] P3.4 默认为独立 VFX delta；完整追加稿必须 --approved 且 editable_scope=explicitly-approved-integration，不隐式改写用户原有剧本/镜头。
- [x] P3.5 六个 P1 原有卡 + 四个 P3 特色卡组成10个可运行单镜头样例；测试 data/schema/原始文本/原子ID/授权逻辑，真实视频视觉评价仍为 P6。

**P3验收**：GitHub Actions https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44861128206 通过 50项测试和 CLI smoke test，详见 examples/ten-shot-validation.md。以上为结构化导演流程及文字编译验收，不包含视频模型生成实测或自动语义/视觉判断。

## P4 详细任务
- [x] P4.1 在 docs/SOURCE_REUSE.md 区分原件复制并执行、Agent按需原文阅读、外部素材链接和项目薄适配；Sakuga 原始catalog与LICENSE已直接引入。
- [x] P4.2 为14个特效家族补上视觉任务、锚点、生命周期、交互、错误与非战斗/场景示例，资料链接引用原skill-movie/rng-vfx/effekseer文件而非重新编写其专业知识。
- [x] P4.3 9媒介/14题材/9审美风格的46个结构化Profile，严格区分风格/题材/效果；scripts/lookup_profile.py 精确查询，逐条有上游来源。
- [x] P4.4 复用 Sakuga 原始90条/9元素 catalog.json，外部preview.webp索引，保留FPS/帧/组合/触发标记、使用案例、来源与review状态；scripts/search_cases.py支持元素、形态、配对、标签、媒体等筛选。
- [x] P4.5 比较派生90条与上游源文件完全一致；检测唯一 ID/合法配对与目录；上游重复 use_cases 保留原文，不伪装人工视觉审核；资料/Schema/来源路径全部自动校验。

**P4核心验收**：GitHub Actions https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44862387129 已通过 67/67 测试、6种Schema以及90案例/46Profile完整性检查。可执行 `python adapters/sakuga_catalog.py --check`、`python scripts/search_cases.py --element water`、`python scripts/lookup_profile.py --axis style --id mj-dreamlike`。以上案例仅涵盖动漫游戏风格，不能作为真人、MJ或Pixar等媒介已有视觉样本的证据。

**P4扩展Backlog（不阻塞P5）**：继续寻找有真实预览、可核实来源的写实电影/科幻/日系CG/柔光MJ/动画电影与非战斗灾害案例；先补证据再补索引，绝不自动将90个动漫游戏案例标注为所有媒介通用。

## P5 详细任务（已完成结构/功能验收）
- [x] P5.0 面向新手：模糊场景/图片输入时先根据566原子及四轴Profile提供3–5个清楚的VFX候选，用户选择后才生成已批准的特效卡及提示词。
- [x] P5.1 仅 MiniMax H3 / Seedance 两个视频模型，未指明默认MiniMax H3；推荐包记录模型选择来源（默认或明确选择），防止不经意切换。
- [x] P5.2 原样复用官方 MiniMax H3 Prompt Skill/基础及参考规范3文件；Seedance按官方文档作不臆测子版本的薄适配。
- [x] P5.3 已审核Effect Card输出两模型VFX-only补充，保留原剧本与必要授权门禁。
- [x] P5.4 状态衔接、重置、独立镜头分流；3连续 + 3独立 + 1显式重置的回归样例。
**P5验收**：CI #44863649037 共93项测试通过；模型侧未做真实出片能力保证。

## P6 详细任务（设计/报告工具已完成；真实视频待验证）
- [x] P6.1 六维0–2：因果、空间、时序、风格强度、环境交互、可读性。总分>=10/12、任一维不能为0、不能有硬失败，达标才通过评分门槛。
- [x] P6.2 复用原始 `effekseer-vfx-skill/skills/vfx-review` 独立审核方法；增加14类硬失败与定向修复建议。每轮只修一个主要VFX问题、用户原文和不可改项原样保留。
- [x] P6.3 提供16个跨题材/媒介的**人工编写设计审核正反例**（7合格/9拦截），并针对合成“视频审核证据”做格式/缺失帧/虚构帧/独立性回归测试。
- [x] P6.4 区分`design-only`（只称设计审核通过）与`rendered-frames/video`（必须真实看画面和记录帧）；脚本检查报告证据元数据、汇总打分，但绝不冒充像素级视觉审核、无法验证帧资源真实存在。默认H3、可选Seedance。
- [ ] P6.5 **待真实素材**：选取实际MiniMax H3和Seedance出片/抽帧，由独立Reviewer观片、记录实际帧及版本，完成真正视觉QC、修复再比对；没有实际生成素材时不能标记此项完成。

## P7 详细任务（预验收发布候选）
- [x] P7.1 文档、命令、示例一致性与本地链接检查：`scripts/release_check.py` 对项目拥有的Markdown链接、五个已复制上游快照、明确的H3默认与Seedance适配、说明文档进行校验；第三方原件保持不改动。
- [x] P7.2 跨平台一键离线验收：`python -m pip install -r requirements-dev.txt` 后 `python scripts/verify_all.py` 运行全部测试/Schema/上游索引/推荐/编译/多镜头/QC/门禁；`--fast` 仅用于快速smoke。
- [x] P7.3 真实视频QC实测准备：`scripts/prepare_visual_evidence.py` 可在用户本地有`ffmpeg/ffprobe`时抽取H3/Seedance视频真实帧、计算源和候选帧SHA-256、保存`not-reviewed`清单；不伪称脚本已视觉审核。
- [x] P7.4 发布材料：`VERSION=0.1.0-rc.1`、`CHANGELOG.md`、`docs/RELEASE_NOTES.md`、`docs/USER_ACCEPTANCE.md` 十项实测矩阵、`.gitignore` 防止私人视频帧被提交。
- [ ] P7.5 用户真实模型出片及独立视觉QC后，再明确批准正式版tag/release；**当前只发布可验收RC，不将真实画质未测标记为稳定验收通过**。

**P7验收范围**：代码、数据、Agent使用规范、一键离线测试、发布说明及手动视频测试路径；剩余的不确定性必须由用户真实H3/Seedance出片、实际图片/视频输入和人工/多模态Reviewer实测验证。RC可在测试前交付，不构成稳定版发布或模型实际画质的背书。

## 关键依赖与验收节奏
P1→P2→P3 的顺序不可颠倒；P4 可按需扩充；P5 依赖 P3 稳定的 Effect Card；P6 应贯穿开发而非最后一次性执行。任何阶段只在实际文件存在、校验通过、提交 SHA 可验证后标记完成。

## 开发原则
1. 上游复制复用优先：允许导入大量可合法再分发的上游代码/知识/数据，优先做薄适配，而非重新手写成熟模块。
2. 默认主控只负责 VFX，不吞并打斗编排、摄影、剪辑和声音的职责。
3. 用户只要“创意”时不强制编造详细剧情；用户已有文案时保存原文。
4. 特效总量不等于质量；检索精度、因果与风格适配高于条目数。
5. **状态如实**：计划中的空白模块不是已实现，不宣称具备尚未实测的功能。

## 实施记录
- 2026-11-21：P7候选发布材料和测试入口落地，补充`VERSION 0.1.0-rc.1`、一键离线全量校验、来源/文档链接一致性、真实视频候选帧SHA-256取证、10项用户实测清单、CHANGELOG及候选版说明。保留P6真实视觉QC和稳定版tag为用户验收后处理。
- 2026-11-21：P6六维设计/证据报告检查与局部修复引擎完成；直接复用effekseer独立Review和rng物理参考；16个合成设计QC正反例（7过/9拦）、14个硬失败、评论/证据Schema及CI；真实H3/Seedance画面审核独立列入P6.5未完成。
- 2026-11-21：P5已完成离线结构与工作流验收：仅MiniMax H3/Seedance（默认H3）、官方H3原始Skill三文件优先复用、面向非专业用户的场景/图片分析后3–5候选方案确认门禁、双模型VFX插入适配、跨镜头连续/独立/重置状态检查；CI #44863649037 93项通过。真实性能/视觉出片QC归P6。
- 2026-11-21：P4核心知识与首批案例库落地：Sakuga原始元数据90条（9种元素）、46套四轴Profile（14效果家族/9媒介/14题材/9审美）、来源目录查询和QA；GitHub Actions #44862387129 67/67 测试通过。真实跨媒介影片案例仍在扩展Backlog。
- 2026-11-21：P3完成：根 SKILL 接入上游两个导演/构建 Skill 的实际工作流，补全组合门禁、非侵入式输出契约、确定性 prompt compiler、10个可运行场景；CI #44861128206 通过 50项测试。自动理解新剧本/自动渲染视频/视觉QC 不属于已完成项。
- 2026-11-21：P2 完成；CI #44860320672 通过 35/35 测试、5套 JSON Schema，数据统计 566原子/31精选/71标签/6效果卡；新增精确 tag 过滤和来源/连续性/异常验证。已确认 medium/genre/style 仅上下文，后续 P4 才能提供有依据的逐原子适配过滤。
- 2026-11-21：CI验证（GitHub Actions #44859588112）：8项单测通过，原子库566条、精选31条、样例6张通过完整性检查；P1完成，P2正在完善。
- 2026-11-21：三个上游共40个源文件已原样导入，其中 skill-movie 15文件含566双语原子和检索算法；P1数据模型、31条精选索引、6个效果卡已完成。
- 2026-11-21：用户强调上游 Copy-First；P1 优先 vendor 上游原件并建立适配，禁止为追求原创重复造轮子。
- 2026-11-21：核查 GitHub 新仓库和上游核心 Skill，完成产品设计与实施计划初稿。
