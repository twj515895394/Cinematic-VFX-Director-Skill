# 上游来源与复用边界（持续维护）

日期：2026-11-21。本文件登记**实际导入并接入**的上游原件以及待复用资源。项目采取 Copy-First：成熟文件原样保留，项目差异由 Adapter 负责。

| 上游 | URL | 拟学习/复用 | 当前处理 |
|---|---|---|---|
| snowfrost/skill-movie | https://github.com/snowfrost/skill-movie | 两个VFX Skill、9个References、566原子JSON、原搜索脚本、2份Agent元数据 | **15个原始文件已复制，主Skill与薄适配检索已接入** |
| MRRengi/rng-vfx | https://github.com/MRRengi/rng-vfx | craft / elements / physics / motion / mediums 与评测 | MIT 原件已导入 13 文件（包含 LICENSE 与 SKILL） |
| kanaworksai-hue/effekseer-vfx-skill | https://github.com/kanaworksai-hue/effekseer-vfx-skill | 特效构建过程、案例拆分与 QA | MIT 原件已导入 12 文件（包含 LICENSE、工作流与 QC） |
| kanaworksai-hue/kanaworks-sakuga-vfx | https://github.com/kanaworksai-hue/kanaworks-sakuga-vfx | 动态案例90条原始元数据、元素分类、组合属性 | 已导入 catalog.json 与 LICENSE（2文件），派生90条可查索引；不复制实际图像素材包 |

## 复用规范
1. **公开代码与媒体有不同的许可条件**，不能因个人非商业用途就忽略。当前目标仓库为公开仓库。
2. 拟复制任何上游文件之前核查其 LICENSE、素材单独授权、引用依赖与署名条件，记录原始路径、commit、修改与许可证。
3. 对 MIT 等有明确复制权限的上游，直接复制并保留许可证和署名；以轻量 Adapter 接入，避免无意义重写。授权不清时仅保留外链或原创摘要。
4. 如果以后并入上游代码，应在本文件记录逐文件归属与附带许可证。
5. 外部平台特效视频、音乐和图像默认仅保存链接/元数据，不上传第三方素材。

## Copy-First 实施结构
`third_party/<repo>/` 存原始快照和 LICENSE，后续 `adapters/` 存四维分类/中文/影视提示词转换层。复制件不修改，便于升级；每个上游原始文件记录源 URL 和 commit。

- `MRRengi/rng-vfx`：MIT，优先原样复制 craft、elements、motion、physics、brightness、styles；游戏引擎说明按需，避免复制无用大工程。
- `kanaworksai-hue/effekseer-vfx-skill`：MIT，优先原样复制 vfx-review，并评估可复用制作规范。
- `snowfrost/skill-movie`：现已按用户确定的个人项目复用方式导入两个VFX Skill、566词库和原始检索脚本；不对 vendor 原件做内容修改。
- `kanaworksai-hue/kanaworks-sakuga-vfx`：代码和媒体授权分开，案例先存链接；不把动态素材当成 MIT 代码复制。

## 实际导入记录（2026-11-21）
- **skill-movie** 上游 commit `69f6db670ecf305e84f199e418bddbf2c1d988fe`：`third_party/skill-movie/` 共15文件（2个SKILL、9篇references、2份agents、1个原始search_vfx_atoms.py和1个566条原子词库）。主 `SKILL.md`、`adapters/upstream-routing.md` 和 `scripts/search_atoms.py` 已实际引用，后者直接调用原搜索模块。
- **测试事实**：GitHub Actions https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44859588112 完成数据检查和8项搜索/映射单测，结果成功。
- **rng-vfx** 上游 commit `4d906cff49a82aeb7c0b3a99b82b193320934fa0`：`third_party/rng-vfx/` 共 13 文件，含 MIT LICENSE、原始 SKILL、craft/elements/motion/physics/brightness 和 6 类 styles。
- **effekseer-vfx-skill** 上游 commit `b0eea1085f2e3e0fa0b5cc77c58c9a845f0bec96`：`third_party/effekseer-vfx-skill/` 共 12 文件，含 MIT LICENSE、两份 SKILL、design/layering/review/craft/motion/realism/sequence/stylized/timing。
- **真实接入**：主 `SKILL.md` 增加优先读取与路由规则；`adapters/upstream-routing.md` 逐场景指向原始上游文件。原件均未经修改；P2已接入原始代码检索，P3已完成提示词编译；自动视频画面 QC 仍待 P6。

## P4 上游复用类型（来源/摘要/实际可执行）
| 资源 | 复用级别 | 说明 |
|---|---|---|
| skill-movie 的 2个导演/构建 Skill + 566词库 + 查询脚本 | 原件复制 + 可执行调用 | 影视 VFX 机制和原始评分直接使用，项目薄映射 |
| rng-vfx 的美术/物理/亮度/风格原件 | 原件复制 + Agent 阅读 | 电影媒介和风格约束从源文档按需读，不重新手写全部原理 |
| effekseer 的 design/layering/timing/review | 原件复制 + Agent 阅读 | 提炼视频可读的因果与独立审核，游戏引擎内容不强制执行 |
| sakuga-vfx/catalog.json | 原件复制 + 派生索引 | 上游90条各有帧数/元素/形态/组合关系，转换为案例 Schema |
| sakuga 动态图片/序列帧资源 | 来源链接、非本地打包 | 使用 pinned GitHub 目录和 preview.webp 链接，未实测逐帧画质 |
| 本项目四轴风格/题材/Profile | 薄适配原创 | 只写上游没有直接提供的跨行业映射和非侵入式规则 |

### Sakuga 原版快照与目录版本
- 上游 `kanaworksai-hue/kanaworks-sakuga-vfx` commit `7cfc9e6bd6ecc0239f3c141e9c5c42cbdc8bb365`，原版 `catalog.json`、`LICENSE.md` 存在 `third_party/kanaworks-sakuga-vfx/`。
- 原目录统计 90条、9种元素、9种形态；`adapters/sakuga_catalog.py` 转换为 `data/catalog/cases.json`。可运行 `python adapters/sakuga_catalog.py --check` 检测派生索引变化。
- 所有案例标记 `metadata-only`，保留原始 source tags 和 use_cases（含重复词标签），保留源帧率、接触帧和配对关系。
- 上述资产数据与代码采用不同许可；具体署名按 vendored LICENSE。当前没有将实际媒体文件复制成素材包。
