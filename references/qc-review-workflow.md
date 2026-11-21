# P6 · VFX 审核—定向修复的实际工作流

本层不是像素识别器；以已经导入的 [原始独立审片 Skill](../third_party/effekseer-vfx-skill/skills/vfx-review/SKILL.md) 和 [上游审核资料](../third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/review.md) 为基线。其**先看实际图、后下评分、不凭代码猜效果**的原则适用于 AI 视频，但原 Godot/60FPS 和游戏引擎构建脚本不能直接用来验证生成的 H3/Seedance 成片。

## 流程 A：用户尚无生成视频（设计 QC）

1. 已按 [P5 方案选择流程](choice-first-workflow.md) 获用户明确选择；如仍未选，硬失败 `UNCONFIRMED_CHOICE`，应暂停最终视频提示词而不是自行替用户决定。
2. 读取用户原稿（逐字保留）、参考图片（有则实际看图）、已选 Effect Card、动作顺序、媒介、原有构图、不可改项。只对已有事实和效果逻辑做文本/设计评估。
3. 使用 [六维 rubric](qc-rubric.md) 逐项记录 `0/1/2`、观察文字和证据，例如“原稿 S01 第2行，未出现挥剑”，不得凭空声称看过未来生成的片段。
4. 硬失败直接拦截；分数 `>=10/12` 且每维 `>=1` 且无硬失败才算**设计检查通过**。
5. 最弱问题给一个局部修改建议，改 VFX delta 或与用户澄清；不要直接改原人物/机位/剪辑。再次进行设计 QC。
6. 通过后可输出 MiniMax H3（默认）或 Seedance（显式选择）的 VFX-only 插入。视频视觉是否达标需要真实生成后另审。

## 流程 B：已有 H3/Seedance 成片（视觉 QC）

1. 核对这是用户实际生成的视频/抽帧，记录资源路径或URL、版本/生成批次、帧或时间点及审查时使用的视图。**必须查看真实画面**；一张静图只能支持静态空间/遮挡的部分结论，不能证明整条片的时间节奏或最后衰减。
2. 对照用户原始镜头与选择的方案，重点检查：人物是否变脸、剑是否变形、能量附着是否漂移、碰撞是否对准、环境是否受光、声音/镜头是否保留，以及所有消散和跨镜头状态。
3. 优先让不同于生成者的 Reviewer 独立读帧，不向其提供可诱导结论的自评说明。依上游 effekseer-vfx-review 方法做证据记录和一轮只修一个问题。
4. 创建 `qc-review.schema.json` 报告，六维每维包含观察文字 + 实际帧引用；提到的 `frame:N` 必须属于 `observed_frame_ids`。对缺少真实截图或视频的情况，**不可填造报告来宣称已通过**。
5. 调用 `scripts/review_vfx.py` 汇总评分与发现；分数和硬失败决定是否**报告合格**，即使 reported-pass 也不意味着工具自己看过帧。发布前仍需独立核查帧及素材版本是否就是评审所见；视频重新生成后旧报告失效。
6. 如果失败，只修最关键的一个VFX问题并重新生成/剪辑**允许变动的部分**，不默默添加新剧情/新动作，不用整个视频重写代替局部修复。

## 可执行命令

```bash
python -m pip install -r requirements-dev.txt

# 合格的合成文字/设计检查：只是设计可交付，不代表成片视觉通过
python scripts/review_vfx.py --review tests/fixtures/qc/design-good-sword.json --json

# 故意有问题的回归示例：返回一次定向修复指令
python scripts/review_vfx.py --review tests/fixtures/qc/design-bad-early-contact.json

# 如需在流水线里让失败报告退出状态为1
python scripts/review_vfx.py --review tests/fixtures/qc/design-good-rain.json --fail-on-blocked
python -m unittest discover -s tests -v
python scripts/validate_data.py
```

脚本没有视频下载、帧提取、图像理解、真实模型调用或外部证据的自动验证功能。**任何基于实际视频的 QC 结论必须由能够查看真实画面的 Agent/Reviewer 写出观察事实**，再交给脚本校验评分与输出最小修复建议。

## 记录格式

`data/schemas/qc-review.schema.json`：

- `review_id` / `shot_id` / `model`（仅 H3/Seedance）/ `medium` / `source_prompt` / `immutable_constraints`。
- `reviewer.id`、`reviewer.role`（`author` / `independent`）。
- `evidence.kind`（设计 / 已渲染帧 / 已渲染视频），`asset_refs`、`observed_frame_ids`、可选 `asset_version`；渲染报告必须带媒体来源与观察帧。
- `scores` 六个各含 `score`、`observation`、`evidence_refs`；`hard_failures`、`findings` 记录错误和局部修复目标。

**警告**：`reviewer.role=independent` 只是报告字段，不能凭这个自填值证明审核者真的独立。独立性由实际审片工作流程保证。P7 可再建立真实视频回归基线及视觉审核任务交接。
