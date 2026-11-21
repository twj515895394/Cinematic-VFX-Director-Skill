# 四维 VFX 分类与路由规范（P1）

**四个互相独立的字段**：`medium`（画面呈现媒介）、`genre`（故事类型）、`style_profiles[]`（美术/镜头审美修饰）、`family`（特效家族）。既有素材和用户约束优先，切勿从某个轴臆造另外一个轴。

## Medium（单选）
| ID | 中文 | 视觉与合成原则 |
|---|---|---|
| photoreal-live-action | 真人写实实拍 | 真实材质、接触阴影、镜头曝光和环境反射 |
| premium-cg | 高规格电影 CG | 物理体积、几何深度、精细光传输 |
| semi-realistic-japanese-cg | 日系半写实 CG | 角色审美化，能量效果精致，保留空间真实感 |
| anime-2d | 二维动漫 | 图形化轮廓、关键帧力度、少量高可读形变 |
| stylized-3d | 风格化三维 | 夸张形状和材质，物理逻辑可风格化 |
| toon-3d | 卡通动画电影三维 | 柔和体积、清晰轮廓、适当夸张而不过曝 |
| npr-2.5d | 非真实感/2.5D | 线条/网点/水墨等媒介混合，边界优先 |
| mixed-media | 混合媒介 | 规定特效属于何层，混合后风格统一 |
| unknown | 尚未确认 | 采用中性表述，保持用户已有画风 |

## Genre（可多选，主题材明确）
`modern-action`（现代动作）、`wuxia`（武侠）、`xianxia`（仙侠）、`mythology`（神话）、`science-fiction`（科幻）、`mecha`（机甲）、`cyberpunk`（赛博朋克）、`superpower`（超能力）、`high-fantasy`（高奇幻）、`dark-fantasy`（暗黑奇幻）、`natural-disaster`（自然灾害）、`environmental`（环境叙事）、`transformation`（形态变化）、`slice-of-life-fantasy`（日常奇幻）。不等于视觉风格，也不等于效果类型。

## Style profiles（零到多个，可自定义）
| ID | 定义 | 避免误判 |
|---|---|---|
| natural-cinematic | 现实主义电影层次和真实光影 | 不等于强烈镜头光斑 |
| soft-diffused | 低对比柔光，节制高光晕散 | 不能柔到丢失形状 |
| mj-dreamlike | 梦境艺术电影/柔和体积光/诗意氛围 | 不是一种模型能力或特效形状 |
| pixar-like-animation | 通用高完成度卡通电影语言 | 不仿制特定受保护角色 |
| anime-sakuga | 动漫作画强化、速度/冲击帧 | 不等于每帧加速度线 |
| graphic-ink | 水墨/线条/版画等平面构成 | 避免无依据乱加墨迹 |
| dark-gritty | 粗粝、暗部层次与有限可见性 | 不等于黑屏 |
| high-energy-game-cg | 图形化鲜明技能表现 | 不能影响动作可读性 |
| user-defined | 用户明确描述的新风格 | 保留原词与可验证约束 |

## Family（单项原子的主要家族）
`weapon`（武器附着/启动）、`character`（人物状态/发力）、`motion`（速度/拖尾）、`impact`（碰撞命中）、`elemental`（火水冰风雷等元素）、`energy`（通用能量体系）、`ritual`（法阵/符文/召唤）、`spatial`（空间变化）、`technology`（全息/机械/科技装置）、`environment-weather`（雨雪风雾/灾害天气）、`destruction-material`（碎裂/磨损/材质变化）、`transformation`（形态变化）、`optical-compositing`（交互光照/折射/合成）、`atmospheric`（尘埃/薄雾/漂浮物）。

## 决策示例
1. `semi-realistic-japanese-cg + slice-of-life-fantasy + [soft-diffused,mj-dreamlike] + weapon` → 握剑激活的紫色微光、少量粒子、手部光照，禁止自动远程剑气。
2. `photoreal-live-action + environmental + [natural-cinematic] + environment-weather` → 暴雨流速、风向、湿材质反射，禁止未经要求的魔法。
3. `anime-2d + wuxia + [anime-sakuga] + motion` → 清晰刀光/速度残影，接触后才产生冲击帧。
4. `premium-cg + mecha + [dark-gritty] + technology` → 金属构件变形、锁定、机械火花，不能变为无来源光球。
5. `stylized-3d + high-fantasy + [mj-dreamlike] + spatial` → 空间边界折射与周围光照，控制空间锚点。

## 中文/英文别名与非等价词
| 用户常用描述 | 归一化目标 | 解释与边界 |
|---|---|---|
| 真人电影 / 真实摄影 / live action | medium=photoreal-live-action | 不自动添加魔法粒子 |
| 日系 3D 动漫电影 / 半写实 CG | medium=semi-realistic-japanese-cg | 明确三维与真实深度 |
| Pixar感 / 欧美卡通电影 | medium=toon-3d + style=pixar-like-animation | 审美标签不改变剧情题材 |
| MJ风格 / 梦幻柔光 / 朦胧艺术电影 | style=mj-dreamlike 或 soft-diffused | 用户只说“MJ”时保留不确定性 |
| 国风武侠 / 武打 | genre=wuxia | 不默认仙术 |
| 修仙 / 东方仙侠 | genre=xianxia | 有法力的世界观，但不强制当前镜头施法 |
| 机甲 / mecha | genre=mecha | 不自动新增机械武器 |
| 剑气 / sword projectile | 原子 family=weapon-motion，使用前区分贴身拖尾与离体投射 | 不等同普通 weapon trail |
| 刀光 / slash arc | family=weapon/motion 候选 | 贴合真实武器运动路径 |
| 护盾 / barrier / shield | 原子 system=technology/ritual 候选 | 必须先判断科技或超自然来源 |
| 特效呼吸 / energy pulse | family=energy | 允许仅在武器表面，不必爆炸 |
| 随手抹除、凭空闪现 | transformation/spatial 候选 | 需剧情授权且不能遮盖身份连续性 |

别名仅用于**理解和检索扩展**，绝不将近义词机械视为视觉效果等价。上游 [566条原子词库](../third_party/skill-movie/vfx-effect-construction-engine/references/vfx-atom-index.md) 原样保留；词库中英文名交给原始检索脚本处理。

## 路由顺序
用户明确声明（硬约束） > 已有参考/输入中的明确线索 > 类型默认 > unknown。若只输入「MJ风格」，优先返回少量风格方向而不是杜撰精确效果；用户目的明确且画面已充分描述时可采用保守默认并声明假设。

**后续 P2**：将本表可机读化并在搜索时接受四轴过滤；**P4**：为每一类建立完整艺术指导资料与参考案例。
