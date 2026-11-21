# P4 · 动态视觉案例索引：数据、查询、来源及局限

## 1. Copy-First 数据结构
- 上游：`kanaworksai-hue/kanaworks-sakuga-vfx`，固定 commit `7cfc9e6bd6ecc0239f3c141e9c5c42cbdc8bb365`。
- 原样复制的文件：`third_party/kanaworks-sakuga-vfx/catalog.json` 和 `LICENSE.md`。
- 原目录 **90条、9元素 × 每元素10案例**，带有 `form`、`fps`、`frames`、`loop`、`contact_frame`、`anchor`、`orientation`、`pairs`、`tags`、`use_cases` 和多层 VFX 参数。
- 本项目用 [adapters/sakuga_catalog.py](../adapters/sakuga_catalog.py) 进行**薄结构转换**，生成 `data/catalog/cases.json` 的90条 Case 记录。源数据不动；重新运行可校验版本未漂移。
- 每条记录附有源项目具体目录链接、原始预览 WebP 文件链接、源帧率/循环属性/特效组合 ID、许可证署名与审核状态。未把动图、图片或序列帧素材打包成我们的独立资源包。
- 所有90条的 `curation_status=metadata-only`：**仅核对了上游元数据，不声称人工逐帧审查、视频模型可用或真人人物特效适用**。原数据中部分 `use_cases` 有重复标签，保持原样以便和上游同步。

## 2. 案例查询
```bash
python scripts/search_cases.py --element water --limit 20
python scripts/search_cases.py --element fire --form projectile --json
python scripts/search_cases.py --family impact --tag splash
python scripts/search_cases.py --paired-with water_charge_01
python scripts/search_cases.py --use-case "water pillar"
python scripts/search_cases.py --loop yes
python scripts/search_cases.py --medium anime-2d --style anime-sakuga
```

`--element`、`--form`、`--tag`、`--use-case`、`--paired-with`、`--loop` 是上游真实元数据过滤；`--family` 是公开明确的源 form→本项目映射；`--medium`、`--style` 检索的是**本案例索引已记录的媒体属性**，而不是对 566 原子做伪精确过滤。所有90条源案例都属于动漫风格二维游戏动画。由于源目录没有可证实的剧情题材标注，`genres=[]`，因此 `--genre xianxia` 返回空，不意味着特效无法用在仙侠，只表示未被这一来源证实。

## 3. 如何预览
- 官方 **<https://kanaworksai-hue.github.io/kanaworks-sakuga-vfx/>**：查看动态特效预览与资源说明。
- 单条 Case 的 `source_url` 指向固定 commit 的资产目录，`static_preview_url` 指向上游已有的 `preview.webp`；该 WebP 可能包含动图，脚本没有做动画类型的逐文件验证，因此 `motion_preview_url` 暂设为 `null`。
- `time_markers` 只从真实 `contact_frame/fps` 计算，不杜撰其他“命中/峰值”帧。
- `atom_ids=[]`：sakuga 与 skill-movie 的 566词原子分属不同体系，目前没有审核过的可靠逐条对应，因此不虚构关联 ID。

## 4. 组合关系、元素属性与影视适配
源目录的 `pairs.cast/projectile/impact` 和 `fx.flash/ring/sparks/debris/smoke/decal/light/trail/shake/sfx` 提供特效分层、辅助件与节奏的结构参考。本项目保存的是 `paired_source_ids` 和 `fx_components`，真实数值仍直接阅读原 `catalog.json`。

这批案例适合**二维动漫游戏类**特效组合与时序参考，不能证明适用于真人电影 CGI、MJ 梦境柔光、Pixar式动画电影、自然灾害/非战斗写实。那些场景以独立的 [四轴指导](../references/cinematic-profile-routing.md)、`skill-movie` 原始导演规范及 `rng-vfx` 物理/风格资料为主。

## 5. 数据版本维护与质量验证
```bash
python adapters/sakuga_catalog.py --check
python scripts/search_cases.py --element water
python scripts/lookup_profile.py --axis family --id spatial
python -m pip install -r requirements-dev.txt
python scripts/validate_data.py
python -m unittest discover -s tests -v
```
**改上游版本的流程**：先更新 `third_party/kanaworks-sakuga-vfx/catalog.json`、对应 LICENSE 和 `adapters/sakuga_catalog.py` 中的 `UPSTREAM_COMMIT`，再执行 `--write`，审查生成 diff，最后更新 `data/sources.json` 来源记录和所有引用。

**P4 仍未具备的真实影视案例**：真人好莱坞电影 CG、日系半写实 CG、非战斗写实灾害、MJ柔光及 3D动画电影需要另外引入有授权和可访问预览的专业素材。当前90条属于独立可检索的动漫案例，不是这些其他媒介的真实例证。
