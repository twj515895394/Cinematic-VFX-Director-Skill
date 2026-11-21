# P5 · 连续剧情与独立混剪共存的 VFX 状态合同

**视频片段是否承接由用户故事/分镜决定**，而不是“这个 Skill 是剪辑风格”的先入假设。动作导演、摄影、音效、剪辑职责仍在原用户/其他 Skill，本 Skill 只审查 VFX 事件在画面中的连续性。

## 三种模式
- `continue`：这是上一个镜头中**同一股能量/同一烟雾/同一个护盾**的后续。检查前一镜头 `effect_state_out` 和本镜头 `effect_state_in` 的 `id/status/color/anchor/scale` 是否衔接。合法变化应该发生在**当前镜头里**，而非剪辑点处无说明突变。
- `independent`：两个画面或叙事片段不需要 VFX 状态相连。即使同一演员重复出现，也不强制继承能量、颜色、特效状态；适合MV、Vlog、剪辑型人物纪录片等。
- `reset`：有明确的跳时、场景更换或用户重设；记录 `reset_reason`，表示有意取消上镜头延续，无须假装连续。

### CLI
```bash
python scripts/check_shot_states.py --file examples/sequences/continuous-sword.json
python scripts/check_shot_states.py --file examples/sequences/continuous-mecha.json --json
python scripts/check_shot_states.py --file examples/sequences/montage-weather.json
python scripts/check_shot_states.py --file examples/sequences/mixed-explicit-reset.json
```

已提供 3 个连续剧情示例（剑刃激活、机甲护盾、山谷薄雾），3 个独立混剪示例（天气、神话、CG/二维/写实混合），另有1个明确跳时重置示例。**脚本不会修改视频，只会发现结构性状态矛盾**。比如镜头一中紫色长剑能量被保留，镜头二同一特效突然变成蓝色，标记为不一致。用户明确采用独立混剪时，即使两镜颜色/场景完全不同也不报错。

## 资料与边界
- VFX Card 仍使用已有 `effect_state_in/effect_state_out`，本文件的跨镜头序列只负责镜头接缝。
- `data/schemas/shot-sequence.schema.json` 约束状态字段与选择，`scripts/check_shot_states.py` 校验显式接缝。
- MiniMax H3 可按官方指南制作多镜头有声时间线；Seedance 多镜头/视频编辑等能力应依实际用户所选版本确认；**本项目状态检查不保证模型真实出片无漂移**。
- P6 的视频画面 QC 才负责判断角色变脸、光照闪烁、效果在真实渲染里漂移等视觉问题。
