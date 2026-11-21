# P4 · 四轴影视特效指导库路由（基于成熟上游，按需查询）

## 核心原则
- **Medium**：影像载体、运动语言、光学合成约束；9个选项（含 unknown）。
- **Genre**：人物和世界的因果/审美情境；14类，允许多个。
- **Style profile**：审美表现，如 MJ 梦境柔光、动画电影质感或二维作画；9个选项。
- **Family**：本镜头特效解决的视觉问题；14类。

这四者绝不互相覆盖。**“仙侠”并不自动等于重粒子魔法，MJ柔光不自动生成光环；游戏动漫案例不自动变为真人电影的适配素材。**

首版实用指导存在 [data/profiles/cinematic_profiles.json](../data/profiles/cinematic_profiles.json)；46个条目均包含适配原则、避免事项和已有上游的实际知识文件路径。对特效物理/风格/生命周期的专业原理，请**直接阅读 upstream 原件**，不要重复编写同一份教程。

## 按需检索，而不是全文加载
```bash
python scripts/lookup_profile.py --axis family --id transformation
python scripts/lookup_profile.py --axis medium --id photoreal-live-action --json
python scripts/lookup_profile.py --axis style --id mj-dreamlike
python scripts/lookup_profile.py --axis genre --id xianxia
python scripts/lookup_profile.py --axis genre
```

在现有提示词中，只需打开当前镜头对应的1个 primary family、1个 medium、1个主要 genre 和实际命中的 style。若涉及多个题材可以补另一个 genre，但不要拼所有 Profile。

## 运行时示例
**情况A：日系半写实 CG、少女握住紫剑、MJ柔光审美、无攻击**

1. 查 `family=weapon` 确定武器激活与近身附着；查 `medium=semi-realistic-japanese-cg` 保护柔和面部与空间；查 `genre=slice-of-life-fantasy`；查 `style=mj-dreamlike` 或 `soft-diffused`。
2. 原始原子检索 `python scripts/search_atoms.py "剑刃 逐层点亮" --limit 8`，如关键词找不到则只用 `逐层点亮`，选实际有独立功能的术语。
3. 轻微能量沿原剑刃，手部/袖口受光，无新挥砍、离体剑气或冲击波。
4. 作为独立 VFX delta，**原有镜头不重写**。

**情况B：写实灾难电影中的暴雨与滑坡**

1. `medium=photoreal-live-action`、`genre=natural-disaster`、`family=environment-weather` 与必要的 `family=destruction-material`。
2. 用上游物理与材料指南校准泥土/石块来源、雨线风向、颗粒速度、积水与反射，而不是从风元素游戏法术直接拷贝粒子形态。
3. **sakuga** 中的 `water_impact` 只可作动画飞溅形态的参考，不是实拍水体的已验证效果。

**情况C：Pixar 式卡通电影里纸花展开**

1. `medium=toon-3d`、`style=pixar-like-animation`、`genre=transformation`、`family=transformation`。
2. 焦点在纸花展开的连续形变前缘，材质阴影变化要跟随真实纸张折线；不额外爆炸、变成粒子或新增角色。
3. 查 `rng-vfx` 的风格化运动原理和 `effekseer` 层级参考，轻量化表达。

## 复用路径（严禁把源文件当作自动素材包）
- 原始专业特效分类：`third_party/skill-movie/vfx-effect-construction-engine/references/effect-family-atlas.md`
- 原始构建机制：`third_party/skill-movie/vfx-effect-construction-engine/references/effect-construction-grammar.md`
- 原始媒介合成：`third_party/skill-movie/vfx-effect-construction-engine/references/medium-integration.md`
- 美术物理/运动/亮度：`third_party/rng-vfx/skills/rng-vfx/references/`
- 风格化与真实感：`third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/`

## 边界与下一阶段
P4 让 Agent 能访问并读取**有出处的分门别类指导**；它不是自然语言的完全自动分类模型，不能凭几行文字保证所有视觉美学选择正确。P5 才做视频模型适配和跨镜头连续状态。P6 进一步开展视频画面审稿与定向修复。
