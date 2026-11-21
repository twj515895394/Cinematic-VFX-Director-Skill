# P2 检索与数据验证使用规范

> 2026-11-21 · Copy-First 模式。上游词库、检索评分代码均未改动，影视分类与标签是本项目适配层。

## 1. 数据分层
| 数据集 | 文件 | 作用 |
|---|---|---|
| 上游完整原子库 | `third_party/skill-movie/vfx-effect-construction-engine/references/vfx-atoms.json` | 566条双语原子、唯一事实来源 |
| 上游检索逻辑 | `third_party/skill-movie/vfx-effect-construction-engine/scripts/search_vfx_atoms.py` | 原始分词、别名扩展、排序打分 |
| 项目家族映射 | `adapters/skill_movie_family_map.json` | 20 个上游家族 → 14 个项目效果家族，允许多对多、空映射 |
| 精选标签 | `data/curated_atoms.json` | 31 个上游ID的手工适配标签和应用注释，不是第二套原子数据 |
| 路由分类 | `data/taxonomy.json` | medium / genre / style / family 枚举 |
| 效果卡示例 | `examples/effect-cards.json` | 6 个跨题材的结构化示例 |
| 视觉案例 | `data/catalog/cases.json` | 当前空集合，P4 补有出处的真实案例 |

**重要**：上游原子的 `category`、`role` 和 `family` 与本项目的 `family` 是不同字段。项目标签只覆盖已精选的31条；没有标签的上游原子继续全文检索，并不因为缺少标签被丢弃。

## 2. 常用检索
```bash
# 完全使用原版检索
python third_party/skill-movie/vfx-effect-construction-engine/scripts/search_vfx_atoms.py "剑气" --limit 8

# 使用原版打分 + 本项目效果家族映射
python scripts/search_atoms.py "剑气" --family weapon --limit 8 --json

# 精准精选标签：重复 --tag 表示 AND（同时匹配所有标签）
python scripts/search_atoms.py "雨滴" --tag rain --tag weather --json
python scripts/search_atoms.py --curated-only --tag optics --limit 30

# 上游原生 role/category 过滤
python scripts/search_atoms.py "火花" --role contact-peak --category 命中

# 将媒介、题材与审美作为设计路由上下文
python scripts/search_atoms.py "辉光" --medium semi-realistic-japanese-cg --genre slice-of-life-fantasy --style mj-dreamlike --json

# 无关键词时显示按上游原始 ID 排序的词汇；最大查询 limit 100
python scripts/search_atoms.py --limit 5
```

**四维查询边界**：`--family` 是真实过滤，`--role` 与 `--category` 使用上游原生字段，`--tag` 仅在31个精选原子中进行准确的 AND 标签过滤。**`--medium`、`--genre`、`--style` 只记录为检索结果的 `context`，不会改变返回候选的排序或范围。** 上游原子没有这些属性；在 P4 完善可靠的适用范围索引之前，不可宣称已完成真实四维精确过滤。需要这类约束时由主 Skill 根据镜头与参考信息做人工判断。

## 3. 质量门禁
```bash
# 开发/验证阶段安装一次，运行时原子搜索不依赖 jsonschema
python -m pip install -r requirements-dev.txt

python scripts/validate_data.py
python -m unittest discover -s tests -v
```

验证直接使用成熟 `jsonschema` 库的 Draft 2020-12 引擎（含 URI 格式校验），而非自己编造完整 JSON Schema 实现。主要检查：

- 原始库声明 566 条、唯一ID、6个原生字段、20个家族映射；
- 项目精选索引与原子名称/家族完全一致、标签合法、ID唯一、来源存在；
- 扩展 Atom、Effect Card 与视觉案例 Schema 定义合法，实例必填字段、枚举、嵌套结构合法；
- 项目 taxonomy 与 schema 枚举一致，Effect Card 引用的原子确实存在；
- 上游原件目录存在、文件数与记录一致，来源与实际集成路径存在；
- 连续镜头 Effect Card 的入/出状态属于同一 effect ID，真实案例时间点不乱序；
- 测试通过故障注入验证出现重复、未定义 ID、非法 enum、缺必填字段时会阻断。

项目额外设计的 `Atom` 丰富 Schema **不用于验证原始6字段上游原子**；如今后有本项目新增原子，才在 `data/atoms/*.jsonl` 中按此 Schema 验证。

## 4. 未实现项
- 对全部566条原子真实媒介/题材/审美的逐项适用性标注与自动过滤（P4）。
- 视频像素级视觉 QC、动态提示词自动修复（P6）。
- MiniMax H3、Seedance、Kling、Veo、Wan 的可靠模型适配（P5）。
- 标准案例目录的外部视频预览和时间点检索（P4/P5）。

本文件记录实际可运行的检索及数据检查，不代表模型生成的视频效果已经实测。
