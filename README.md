# Cinematic VFX Director Skill

面向个人 AI 视频创作的 **通用影视 CG 视觉特效导演与知识库**。覆盖真人写实、日系半写实 CG、2D 动漫、卡通电影、武侠仙侠、科幻机甲、梦境 MJ 审美、灾害环境、角色变形和非战斗奇幻等场景。

**项目状态（2026-11-21）：P1 已完成并通过 GitHub Actions；P2 检索和校验功能部分实现，P3–P7 逐步推进。** 不把基础数据检索误认为完整的模型适配或自动特效审核。

## 为什么不重复造轮子
目前已经**实际复制并引用**三个成熟上游项目的40个源文件：

| 上游项目 | 原样复用的关键内容 | 文件数 |
|---|---|---:|
| [skill-movie](https://github.com/snowfrost/skill-movie) | cinematic-vfx-director、vfx-effect-construction-engine、**566条原子词库**、原始 Python 检索脚本及 References | 15 |
| [rng-vfx](https://github.com/MRRengi/rng-vfx) | 特效美术理论、元素、物理、运动、亮度、六种风格 | 13 |
| [effekseer-vfx-skill](https://github.com/kanaworksai-hue/effekseer-vfx-skill) | 特效设计、分层、动画时序、独立 QC 规则与流程 | 12 |

原件均保存在 `third_party/`，项目专属逻辑集中在 `adapters/` 与 `references/`。其他上游引用及快照版本见 [来源登记](docs/SOURCE_REUSE.md)。

## Skill 使用
让兼容 Agent Skill 的工具读取根目录 [SKILL.md](SKILL.md)，即可使用导演工作流。默认保留原始剧本、人物、动作、机位和时长，输出单独的 **VFX 提示词增量**；只有得到授权才生成替代整合稿。

示例请求：
- 「保持原 5 秒镜头和校园少女设定，握住紫色长剑时增加克制的激活能量与环境光响应，但不能挥剑或发射剑气。」
- 「真人写实的暴雨街道如何做湿地反射、水花和空气透视？」
- 「动画二维刀剑碰撞，仅在刀刃真实接触时产生火花。」
- 「给科幻机甲护盾的启动设计薄层扫描、接触式反射，保持外形不变。」
- 「只知道想要 MJ 梦境柔光，先帮我判断适用的特效方向。」

## 检索：原始上游脚本与薄适配脚本
依赖仅 Python 3.10+ 标准库，无云服务和数据库：

```bash
# 上游原始算法：直接使用566条中英双语原子
python third_party/skill-movie/vfx-effect-construction-engine/scripts/search_vfx_atoms.py "剑气" --limit 8

# 项目薄封装：调用上游原始评分逻辑，并使用四维分类上下文
python scripts/search_atoms.py "剑气" --family weapon --limit 5
python scripts/search_atoms.py "雨滴" --family environment-weather --json
python scripts/search_atoms.py "辉光" --medium semi-realistic-japanese-cg --style mj-dreamlike --json

# 数据与回归检查
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

四维体系：`medium`（媒介）、`genre`（题材）、`style_profiles`（审美）、`family`（特效家族）。**媒介、题材和审美目前是检索上下文，不是原子本身的固有属性。**

## 关键文件
- [产品详细设计 v1.3](docs/PRODUCT_DESIGN.md)
- [分阶段实施计划](docs/IMPLEMENTATION_PLAN.md)
- [上游直接复用路由](adapters/upstream-routing.md)
- [四维分类](references/taxonomy.md)
- [31条精选上游原子索引](data/curated_atoms.json)
- [6张跨题材 Effect Card](examples/effect-cards.json)
- [数据验证脚本](scripts/validate_data.py)
- [GitHub Actions 成功运行](https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44859588112)

## 仍待完成
P2：完整标签过滤、Schema 全量验证与负面测试；P3：工作流和提示词自动编译；P4：全面非战斗知识拓展、动态案例；P5：具体视频模型适配与跨镜头状态；P6：自动 QC 与定向修复；P7：稳定发布。

**原则：能用成熟上游就直接复用并做薄适配；只对真正缺失的能力开发新模块。**
