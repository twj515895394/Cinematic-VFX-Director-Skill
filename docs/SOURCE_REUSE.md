# 上游来源与复用边界（持续维护）

日期：2026-11-21。本文件登记**拟参考**的上游仓库；项目采取 Copy-First：能从上游合法复制并经过薄适配复用的，优先直接保留原件，不再手工重写；实际移植状态应随 P1 实施更新。

| 上游 | URL | 拟学习/复用 | 当前处理 |
|---|---|---|---|
| snowfrost/skill-movie | https://github.com/snowfrost/skill-movie | cinematic-vfx-director / vfx-effect-construction-engine，因果包络、主次层级、术语索引 | 核验入口文件，参考设计 |
| MRRengi/rng-vfx | https://github.com/MRRengi/rng-vfx | craft / elements / physics / motion / mediums 与评测 | MIT 原件已导入 13 文件（包含 LICENSE 与 SKILL） |
| kanaworksai-hue/effekseer-vfx-skill | https://github.com/kanaworksai-hue/effekseer-vfx-skill | 特效构建过程、案例拆分与 QA | MIT 原件已导入 12 文件（包含 LICENSE、工作流与 QC） |
| kanaworksai-hue/kanaworks-sakuga-vfx | https://github.com/kanaworksai-hue/kanaworks-sakuga-vfx | 动态案例的分类与元数据 | 核验仓库存在，暂不复制素材 |

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
- `snowfrost/skill-movie`：暂未查到仓库级许可证，不在公开仓库直接复制源码或术语库，先参考架构并记录接口差异。
- `kanaworksai-hue/kanaworks-sakuga-vfx`：代码和媒体授权分开，案例先存链接；不把动态素材当成 MIT 代码复制。

## 实际导入记录（2026-11-21）
- **rng-vfx** 上游 commit `4d906cff49a82aeb7c0b3a99b82b193320934fa0`：`third_party/rng-vfx/` 共 13 文件，含 MIT LICENSE、原始 SKILL、craft/elements/motion/physics/brightness 和 6 类 styles。
- **effekseer-vfx-skill** 上游 commit `b0eea1085f2e3e0fa0b5cc77c58c9a845f0bec96`：`third_party/effekseer-vfx-skill/` 共 12 文件，含 MIT LICENSE、两份 SKILL、design/layering/review/craft/motion/realism/sequence/stylized/timing。
- **真实接入**：主 `SKILL.md` 增加优先读取与路由规则；`adapters/upstream-routing.md` 逐场景指向原始上游文件。原件均未经修改；尚未实现代码级动态检索与自动 QC。
