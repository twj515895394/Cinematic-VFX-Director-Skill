# P3/P5 · 通用 VFX 提示词输出契约

## 0. 先确认效果：P5 的选项门禁
若用户只提供场景、图片、参考视频或“帮我加点特效”等模糊需求，**禁止直接输出下面的最终提示词**。先按 [choice-first-workflow](choice-first-workflow.md) 给出3–5个有差异的VFX方案并等用户明确选择。用户选定前不创建被视为已确认的 Effect Card；用户已经明确指定具体效果的情况无需额外菜单。

后续仅支持两种目标模型：未指明时默认 MiniMax H3；明确指定 Seedance 时使用 Seedance。见 [model-adapters.md](model-adapters.md)。

## 1. 默认：非侵入式输出（delta）
有原提示词时，必须保留逐字一致的原文，包括换行、标点、对白、原镜头时长和已有负面限制。**默认只有两块：**

```text
原始提示词（原文保留）
<原文>

建议附加的 VFX 描述
<effect card 中已确认的 vfx_delta>
```

有明确不可改项时，另附审查提示，但不将内部原子 ID、调度信息、未确认推测混入可直接复制的提示词增量。

没有原稿（knowledge/explore/design）时不要生成虚构的原文块。只回答特效设计建议，必要时给几种方向；其选择取决于题材和画面信息。

## 2. 用户明确同意后：追加式完整提示词（integrated）
`scripts/compile_prompt.py` 只能在 `--approved` **且** Effect Card 的 `editable_scope = explicitly-approved-integration` 时输出整合稿。P3 只支持原稿逐字不变 + 单独追加 VFX 增量的安全方案：

```text
<source_prompt原始文字>

【VFX 特效补充】
<经过审查的 vfx_delta>
```

若用户要求将 VFX 语句插入原稿既有章节，需由 Agent 根据原结构编辑，并生成改动清单；P3 的脚本不会擅自作这种语义级编辑。不可通过“已经填写了 Card”来推断用户授权。

## 3. 源数据、编译结果与审计字段
- **输入**：已批准的 `Effect Card`（`card_id, source_prompt, editable_scope, immutable_constraints, primary_read, related_atom_ids, events, vfx_delta` 等），必须引用真实上游原子。
- **编译器输出**（JSON）：`mode, source_prompt, vfx_delta, immutable_constraints, compiled_prompt, card_id, atom_ids_for_audit, phase_summary`。
- `compiled_prompt` 在 delta 模式下 **只包含 VFX 增量**；集成模式才为“完整原稿 + 附加段落”。
- `atom_ids_for_audit`、`phase_summary` 仅为审计元信息；**不进入人类可复制的最终提示词**。
- 编译器必须拒绝不存在的原子 ID、空 `vfx_delta`、错误 Schema、缺少整合授权；不能依据关键词自行改写 VFX 方案。

## 4. 与现有提示词模板兼容
如果用户使用自定义六段式、十段式或自由格式视频提示词，**以用户原有格式为准**。上游 `skill-movie` 的六段式结构不是本项目的硬约束。对于 8/10/12/15 秒短视频，只引用原文中明确的动作、时长与时点；不能为填满时长强制加释放、命中和消散全部阶段。

## 5. 用法
```bash
python scripts/compile_prompt.py --card sample.sword-activation
python scripts/compile_prompt.py --card sample.sword-activation --json
python scripts/compile_prompt.py --cards examples/p3-ten-cards.json --card p3.dark-ritual
python scripts/compile_prompt.py --card sample.sword-activation --integrated --approved
# 最后一条会拒绝：该样例仍标记为 vfx-only；只有用户明确批准并同步更新Card才允许整合。
```
编译脚本是**Effect Card → 文本的确定性转换**，不是 AI 自动理解原始提示词的替代品，也不是视频像素级 QC。P5 的 `scripts/adapt_prompt.py` 调用此编译器并给出 MiniMax H3 / Seedance 的镜头 VFX 插入文本，但并非完整的有声模型提示词。只有 Agent 已分析场景并获用户方案确认，完成镜头意图、原子选型与因果判断后才能交给它编译。
