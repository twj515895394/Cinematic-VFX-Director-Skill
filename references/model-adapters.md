# P5 · 仅 MiniMax H3 / Seedance 的视频模型特效适配

**模型选择硬规则**：仅两个目标 `minimax-h3` 与 `seedance`。用户没有明确说使用哪个时，**默认 MiniMax H3**。用户明确选 Seedance 时不自动改回 H3。无需添加 Kling、Veo、Wan、通用第三模型、其他虚构模型控制接口。

## 1. 先选特效，再适配模型
上游 `skill-movie` 负责 VFX 导演与构建，原始566原子提供参考，P4四轴指导实现类型/风格映射。用户没有指定特效时，先走 [新手方案选择](choice-first-workflow.md)：分析场景/图片 → 3–5方案 → 等用户选择 → 才生成 Effect Card → 再适配这两个模型。

`scripts/adapt_prompt.py` 是**确定性 VFX 插入片段编译**：只读已审核的 Effect Card，保持原 `source_prompt` 完全一致；不自动理解图片、不自行生成剧情、不创建新摄影/声音/剪辑命令，也不对模型质量做无依据保证。

## 2. MiniMax H3（默认）

**直接复用 MiniMax 官方 Skill**：
- [官方 SKILL.md](../third_party/minimax-h3/skills/h3-prompt-writing/SKILL.md)
- [T2VA/I2VA/FL2VA/L2VA 原始规范](../third_party/minimax-h3/skills/h3-prompt-writing/references/base-en.txt)
- [Ref2VA 原始规范](../third_party/minimax-h3/skills/h3-prompt-writing/references/ref-en.txt)

文件来自 `MiniMax-AI/MiniMax-H3` commit `199b7d0e1fd95e7b3eafa8c15eca692534142427`，在 `third_party/` 原样保存。**不是我们自行发明提示词规范**。

| 输入实际具备 | H3 模式 | 特效写法 |
|---|---|---|
| 纯文字场景 | T2VA | 以原镜头可见行动为框架，特效只写入正确的镜头 `integrated_multimodal_description` |
| 真实首帧图片 | I2VA | 第一帧原始人物/场景是锚点；只描述后续准许的 VFX，不杜撰图像外未来动作 |
| 首、尾两张参考图 | FL2VA | 保持两端已知状态，特效沿现有动作连续演进 |
| 真实尾帧 | L2VA | 特效收束到已知尾帧，不把尾帧误当首帧 |
| 实际图片/视频/音频多参考 | Ref2VA | 参考标签与 `subject_definitions/retention_analysis/detailed_description` 依官方规范，切勿虚构 `<Picture N>` |

官方基本模式完整视频提示词采用 `integrated_multimodal_description`、`overall_soundscape`、`non_diegetic_music` 三个字段；全参考有六部分。Agent **只有在用户授权完整输出且有必要信息时** 才按照官方原版格式编排完整稿；默认给**VFX-only 插入**，不擅自改动镜头或音频。H3 官方规范倾向英文改写，原语种对白/画面文字保留；`scripts/adapt_prompt.py` 不执行机器翻译，Agent 如整理英文稿应保留原文和对照。

### CLI
```bash
python scripts/adapt_prompt.py --card sample.sword-activation
python scripts/adapt_prompt.py --card sample.sword-activation --json
python scripts/adapt_prompt.py --card sample.sword-activation --input-mode first-frame --references-provided
```
**注意**：`--references-provided` 只允许在用户**实际提供对应参考图片/媒体**时使用；它不是自动读取附件、不是自动识别附件类型，也不应在无媒体时填入虚构的参考标签。

## 3. Seedance（仅另一个选项）
- 字节跳动官方：[Seedance 2.0 发布与多模态参考说明](https://seed.bytedance.com/en/blog/seedance-2-0-official-launch)、[Seedance 2.5 发布与能力区别](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)。
- 用户只说 `Seedance` 而未指明版本时，采用通用家族安全的**自然语言特效因果描述**。不自行猜测2.0还是2.5，也不随意赋予帧数、时长、分辨率、隐藏API参数。
- 用户实际提供的图像、视频、音频才允许作为参考；引用占位符（如 `@Image 1`）应与真实附件及所在平台实际语法对应。没有真实参考资源就不写 `@image1` / `@video1`。
- 有已有视频要求定向添加特效时，锁定原镜头/人物/声音/剪辑，在指定可见时间段和接触点描述**只增加的VFX**；视频编辑、延长片段、首尾帧能力因实际版本/渠道而异，不能凭资料一概承诺可用。

### CLI
```bash
python scripts/adapt_prompt.py --card sample.rainy-street --model seedance
python scripts/adapt_prompt.py --card sample.rainy-street --model seedance --json
```

## 4. 非侵入式与输出级别
- **默认**：原文（逐字保留）+ 适合选定模型的特效补充文字。脚本的 `model_vfx_insert` 只是**供已有镜头插入的增量**，不是完整视频模型提示词。
- **用户明确要求完整版本**：在保留原始文本和说明改动的前提下，由 Agent 按官方 H3/Seedance 语法整理新增示例。P3 编译器脚本的 `--integrated --approved` 仍需卡片 `editable_scope=explicitly-approved-integration`，仅追加，不自动替换原镜头内容。
- **用户要多个镜头**：按 [shot-state](multishot-states.md) 判断镜头是否延续，不能把不同情节强行串成单镜头。
- **模型没有强制默认时长**：以用户提供的镜头长度和真实使用渠道支持的选项为准。不要虚构采样、LoRA、Context Windows 或隐藏参数保证效果。

## 5. 最小调用链
```text
用户原稿/图片
   ↓ Agent查阅事实与上游 VFX 资料
3–5个方案（仅在需求模糊时） → 用户确认
   ↓
已确认的 Effect Card（镜头因果+不可改项）
   ↓
P3 compile_prompt.py + P5 adapt_prompt.py
   ↓
默认 MiniMax H3 的 VFX-only 增量 / 明确指定时 Seedance 增量
   ↓
如用户明确授权完整稿，再按官方原版格式制作整合稿
```
