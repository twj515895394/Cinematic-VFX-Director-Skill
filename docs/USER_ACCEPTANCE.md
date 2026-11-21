# 用户实测验收手册（MiniMax H3 / Seedance）

> 对应发布候选：`VERSION = 0.1.0-rc.2`。本手册供实际人工测试，不代表已完成真实视频生成与独立视觉审核。只有两个视频模型：MiniMax H3（默认）和 Seedance（明确指定）。视频生成平台本身由用户操作；本仓库**不代替平台生成视频**。

## 1. 准备与一键离线自检

从 [GitHub 仓库](https://github.com/twj515895394/Cinematic-VFX-Director-Skill) 下载/克隆完整仓库，Python 推荐 3.11+：

```bash
python -m pip install -r requirements-dev.txt
python scripts/verify_all.py
```

Windows 若使用 Python Launcher，可将上面的 `python` 替换为 `py -3`。本命令检查全部自动化测试、566上游原子、90条源案例一致性、46条四维风格配置、推荐/编译/多镜头、P6评分、源文件清单和项目文档本地链接；**不会联网调用模型，也不会检查真实视频画质**。仅想快速重跑部分验证可使用 `python scripts/verify_all.py --fast`。

使用本 Skill 的 Agent 应阅读仓库根目录 `SKILL.md`。可直接输入文字场景、已有镜头提示词、真实图片或真实视频。请勿把下面描述的示例图片当成上传的真实图片。

## 2. 产品流程验收矩阵（Agent实际对话）

| ID | 用户输入示例 | 必须出现的行为 | 失败判定 |
|---|---|---|---|
| A01 | “下雨的夜晚街道，固定机位，帮我加点电影感特效” | 先识别真实暴雨，提供3–5个**不同且具体**的方案，解释为什么合适、亮度和风险，等待选择 | 直接写最终攻击/魔法提示词 |
| A02 | 上传**真实**半写实CG握剑图：“加点特效” | 只以图中可见人物/剑/光照为事实，不脑补挥剑/攻击；推荐3–5项并等待用户选择 | 自行编造图中不存在动作或附件 |
| A03 | 接A02：“选A1，微弱一点，只沿剑刃流动” | 使用所选效果生成**MiniMax H3（默认）**VFX-only补充；人物、武器、姿态、镜头不变；有因果与衰减 | 偷换模型或直接重写角色外貌 |
| A04 | “使用 Seedance，给这个已有纸花展开镜头增强折痕与光影” | 明确采用Seedance，仅增强纸花真实折线/材质，不额外法术或加入新人物；明确具体特效需求可跳过选择菜单 | 默认切回H3，或生成不支持的@引用 |
| A05 | “原稿里的紫剑不能发射剑气，也不能换镜头，帮我增加轻微受光” | 原稿逐字保留，给独立VFX增量；不直接整合覆盖原稿 | 新动作、飞剑、剪辑/机位变化 |
| A06 | “S01与S02同一护盾延续，S03为独立雪山混剪” | S01→S02护盾颜色/锚点/状态一致；S03不继承；合理使用continue/independent | 强制S03延续机甲护盾 |
| A07 | “这段人物没有魔法，只是雨雪和灰尘” | 环境、材质、风向和受光优先；不滥用元素魔法、冲击波 | 所有镜头都生成法阵/能量环 |
| A08 | “我只想了解冲击帧是什么意思” | 直接回答专业术语，不强制给3–5个方案 | 不管任务如何都出现推荐菜单 |
| A09 | “请检查我已经生成的视频，为什么碰撞点漂移？” | **先查看真实可访问视频/帧**再做视觉观察，给一个最主要定向修复建议；无视频则只做设计QC | 未看视频却说“视觉效果已通过” |
| A10 | 已确认效果后要求“完整 H3 视频提示词” | 依据vendored官方H3 Skill的T2VA/I2VA等正确模式整理，实际有参考图才写其占位；用户授权之外不改原内容 | 乱编参考图、时长/采样/隐藏模型参数 |

推荐使用如下记录方式逐项验收：`ID / 输入与附件 / Agent输出 / 合格(Y/N) / 具体问题 / 模型和版本(若有) / 截图或视频证据`。记录在你自己的测试笔记或 `reviews/` 下即可，不需要上传任何个人素材到公开Git仓库。

## 3. 实际视频 QC（真实生成后）

对 A03 等生成的真实 MiniMax H3/Seedance 视频，保留同一镜头的**原提示词、用户选项、真实视频、实际使用模型/渠道与版本**。最好至少分别测 H3和Seedance各一个镜头，并包含一个非战斗特效。

先将视频在本地存为例如 `my_video.mp4`，并安装好 `ffmpeg` 和 `ffprobe`：

```bash
# 默认 MiniMax H3：抽取真实候选帧与视频 SHA-256
python scripts/prepare_visual_evidence.py --video my_video.mp4 --shot-id S01 --model minimax-h3

# Seedance：显式指定，另一个输出目录
python scripts/prepare_visual_evidence.py --video seedance_video.mp4 --shot-id S02 --model seedance
```

在审核前，建议对真实视频和帧图运行哈希完整性验证（不对画质打分）：

```bash
python scripts/check_visual_evidence.py --manifest reviews/S01/evidence-manifest.json --video my_video.mp4
python scripts/check_visual_evidence.py --manifest reviews/S02/evidence-manifest.json --video seedance_video.mp4
```

结果写到被 `.gitignore` 忽略的 `reviews/S01/`、`reviews/S02/`，包含：
- `frame_*.png`：起点、中段、结尾等真实候选画面；采样由原视频时长和帧率确定，**不是固定24 FPS**。
- `evidence-manifest.json`：原视频 SHA-256、FPS、宽高、时间戳、各候选帧SHA-256与采样帧号；状态为 `not-reviewed`，`actually_inspected_frame_ids=[]`。
- 候选帧生成成功 ≠ 已经有人审片。审核者需要**真的打开完整视频和这些图片**，不能只看文件名或提示词。在 `qc-review.schema.json` 所规定的报告中记录实际看过的帧号与观察；`review_vfx.py` 汇总六维评分，**不会自动理解帧**。

建议检查点：身份/服装和道具是否维持；特效真实锚点和接触帧；真实光照、遮挡、环境反馈；转场/跨镜状态；时间节奏与尾部消散；是否越权添加动作、音乐或机位变化。

## 4. 评分与修复后复测

按照 [六维Rubric](../references/qc-rubric.md) 打分：因果、空间、时序、风格强度、环境、可读性，0/1/2各一项。总分≥10分且没有0分/硬失败时可以记录**评分达标**；但只有实际审片记录，才能将其视为成片视觉验收证据。

```bash
# 这个命令只是演示合成设计样例，不是真实视频审核
python scripts/review_vfx.py --review tests/fixtures/qc/design-bad-early-contact.json --json

# 用户/Reviewer完整填写真实报告后：
python scripts/review_vfx.py --review reviews/S01/qc-report.json --json
```

按返回 `next_fix` **一次只改一个VFX问题**，用相同输入再生成，保存新视频及新证据目录。对比修复前/后，不能直接复用旧视频的哈希和评分结果。无法获取真实成片时，停在设计验收，不把模拟报告包装为真实视频QC。

## 5. 实测反馈的最低必要内容

反馈一个问题时请提供：**A编号、选中的方案、使用的模型（H3/Seedance）、原提示词与实际输出、具体违反的约束、截图或视频的相关帧/片段**。如果问题关乎视觉，最好连同 `evidence-manifest.json` 中的相关时间点一起提供。

## 6. 交付与未完成边界

当前RC已具备知识/检索/候选交互/卡片编译/双模型提示词插入/多镜头结构QC/设计评分及真实视频取证准备。**真实出片、独立视觉QC、用户现场交互和模型生成效果**由本手册的验收实测决定；它们在出片证据提供之前**不标为完成**。

发布候选不是稳定版质量认证。待用户实测反馈后可以针对问题微调并再发布正式版本。