# P6 · 影视 VFX 六维 QC Rubric（0–2 × 6）

> **来源复用**：`third_party/effekseer-vfx-skill/skills/vfx-review/SKILL.md` 的**独立视觉审核、逐帧证据、最弱问题单次修复**流程；`third_party/effekseer-vfx-skill/skills/effekseer-vfx/references/review.md` 的亮度/时序/脱锚/尾部问题；`third_party/rng-vfx/skills/rng-vfx/references/physics.md` 的材质、风向与粒子物理；`third_party/skill-movie/cinematic-vfx-director/SKILL.md` 的因果、锚点、清晰阅读重点和媒介路由。
>
> 原上游 `vfx-review` **自身是 9维 × 0–3 的游戏特效 filmstrip 评分**，不能宣称它原本就有本项目的“六维 × 0–2”。下面是针对 AI 影视的**本地适配规则**，上游原件保持不动。

## 1. 六维评分

每项只有整数 `0 / 1 / 2`：

| 维度 | 0（严重失败） | 1（可解释但问题明显） | 2（成立且清楚） |
|---|---|---|---|
| **causality 因果** | 力量/接触/形变缺乏来源，擅加动作 | 有来源但触发/受体不够清楚 | 来源→触发→作用对象闭合，且遵守原动作 |
| **space 空间** | 贴片飘离、尺度/遮挡严重不符 | 锚点基本正确但透视/遮挡有瑕疵 | 真实锚点、景深、尺度及接触位置稳定 |
| **timing 时序** | 命中早于接触、阶段无缘由跳变 | 出现/峰值/衰减有轻微节奏问题 | 按事件发生；重要节拍清楚、余韵自然 |
| **style_intensity 风格强度** | 视觉语言不兼容、强度失控 | 基本适配但主次或强度偏差 | 媒介/题材/审美匹配，主次明确、不过载 |
| **environment 环境交互** | 光照/风向/材料/受体明显矛盾 | 环境反馈不足或略显脱节 | 正确而克制的受光、物理与材质反馈 |
| **readability 可读性** | 爆闪/粒子严重遮住主体/接触点 | 关键信息略被抢占 | 主视觉清晰，人物表情/重要动作仍可见 |

**判定门槛**：总分 `>=10/12`，**全部六维分数都非0**，并且**没有任何硬性失败**。总分12也不能抵消一个硬性失败。该门槛用于确定设计或报告评分是否达标，不等于自动“渲染视觉已验证”。

## 2. 硬性失败（任何一项直接阻断）

`scripts/review_vfx.py` 支持14类明确问题码：
- **SCOPE/IDENTITY**：`SOURCE_PROMPT_CHANGED`、`UNAUTHORIZED_ACTION`、`IDENTITY_DRIFT`；
- **时序与空间**：`EARLY_CONTACT`、`DETACHED_ANCHOR`、`STATE_JUMP`；
- **画面和物理**：`MISSING_ENV_RESPONSE`、`OCCLUSION`、`OVEREXPOSURE`、`UNJUSTIFIED_INTENSITY`、`PHYSICS_MISMATCH`；
- **工作流与模型**：`UNSUPPORTED_MODEL_CONTROL`、`UNCONFIRMED_CHOICE`、`FABRICATED_REFERENCE`。

具体发现必须记录**观察到的问题**、有据可查的引用，以及**局部修复内容**。硬失败例如未接触先火星、人物变脸、无镜头授权却增加攻击、用户没选特效便擅自定稿；无论整体评分看起来多优秀都必须拦截。

未被明确允许的“模型参数”（如任意隐藏采样参数）不能混入 MiniMax H3 / Seedance 正式提示词。H3 官方标准应直接读取 `third_party/minimax-h3/skills/h3-prompt-writing/` 原件。视频模型只有 MiniMax H3（默认）和 Seedance。

## 3. 不同效果的例外处理
- 治愈、护盾、轻微受光、环境雾、气象特效**不需要强行设置攻击闪白、命中冲击波或高速击中帧**。
- 真实暴雨、光照、雪、纸花展开等非战斗镜头，重点是材质、持续态、风向/光路和变形前沿；没有明确接触的“contact”维度不能凭空要求出现火花。
- 二维动画可出现更强的图形节拍，但真实接触依然要对齐；写实摄影、日系半写实CG、梦境柔光按媒介单独判断，不用游戏效果的绝对阈值。
- 0–2 的每维评分依据**具体画面与用户目标**，不可把 `effekseer` 的60 FPS帧号、亮度阈值、游戏引擎 recipe 直接套用于 MiniMax H3 或 Seedance 视频。

## 4. 两种 QC 的证据边界（不可混淆）
1. **设计/提示词 QC**：读取真实用户需求、原提示词、选定方案和 Effect Card，审核可推断的因果/空间/时序/冲突；标记 `evidence.kind=design-only`。满足门槛后只返回 **`design-pass-pending-rendered-review`**。**不得声称视频视觉通过或已看过画面**。
2. **已生成视频/画面 QC**：需要实际视频或抽帧、可访问资源、观察帧编号、独立审核（优先），`rendered-frames` / `rendered-video`。每个评分必须引用实际检查帧/资产；不能根据“设计很合理”冒充观看帧画面。结构化脚本只能核对元数据与帧引用的**格式**，无法证明帧资源真的存在或被打开。因此即使分数达标也只返回 `reviewer-reported-visual-pass`，`rendered_video_independently_verified_by_tool=false`；真正的发布审核仍需独立视觉检查与素材版本/证据核验。

## 5. 一轮只修一个主要问题
优先修**硬性失败**；没有硬失败但评分不过，则修最弱维度。一次只建议更改一个视觉环节（锚点、亮度、时间、环境或最小特效分层），下一轮必须重新检查。

如果脚本返回 `SOURCE_PROMPT_CHANGED` 或 `UNAUTHORIZED_ACTION`：只让 Agent 修改新增的 VFX delta，不替用户改写剧情、打斗动作、镜头运动、剪辑、时长、声音或人物身份。

详细审核和运行契约见 [qc-review-workflow.md](qc-review-workflow.md)。
