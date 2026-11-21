# Cinematic VFX Director Skill

面向个人 AI 视频创作的 **通用影视 CG 视觉特效导演与知识库**。覆盖真人写实、日系半写实 CG、2D 动漫、卡通电影、武侠仙侠、科幻机甲、梦境 MJ 审美、灾害环境、角色变形和非战斗奇幻等场景。

**项目状态（2026-11-21）：P1～P3 已完成并通过 GitHub Actions 50项测试；P4～P7 逐步推进。** 不把基础数据检索误认为完整的模型适配或自动特效审核。

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

## 关键文件
- [产品详细设计 v1.3](docs/PRODUCT_DESIGN.md)
- [分阶段实施计划](docs/IMPLEMENTATION_PLAN.md)
- [上游直接复用路由](adapters/upstream-routing.md)
- [四维分类](references/taxonomy.md)
- [31条精选上游原子索引](data/curated_atoms.json)
- [6张 P1 基础 Effect Card](examples/effect-cards.json)
- [10张 P3 可执行 Effect Card](examples/p3-ten-cards.json)
- [P3 导演流程](references/director-workflow.md)
- [P3 输出规范](references/output-contract.md)
- [数据验证脚本](scripts/validate_data.py)
- [P2 检索与完整性校验说明](docs/SEARCH_AND_VALIDATION.md)
- [GitHub Actions 成功运行](https://github.com/twj515895394/Cinematic-VFX-Director-Skill/actions/runs/44861128206)

## 仍待完成
P4：全面非战斗知识拓展、动态案例；P5：具体视频模型适配与跨镜头状态；P6：自动 QC 与定向修复；P7：稳定发布。

**原则：能用成熟上游就直接复用并做薄适配；只对真正缺失的能力开发新模块。**
