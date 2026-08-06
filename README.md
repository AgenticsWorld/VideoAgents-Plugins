# VideoAgents-Plugins

[中文](#中文) | [English](#english)

---

## 中文

VideoAgents 官方插件仓库。VideoAgents 内置 83 个 Agent 覆盖「小说 → 视频」主流程；主流程之外的业务（衍生小说、双书融合、音频配画……）以**插件**形式发布在本仓库，下载 zip 包上传即可安装，不改内核。

### 插件列表

| 插件 | 一句话定位 | 下载 |
|---|---|---|
| **derivative-fiction** 衍生创作 | 基于项目既有的世界圣经、角色、场景资产，创作衍生小说（前传/番外/支线/if 线） | [derivative-fiction.zip](plugins/derivative-fiction.zip) |
| **fusion-fiction** 双书融合 | 把两本书融合成一部新剧本：甲本出故事与人物灵魂，乙本覆盖世界观与人物形象壳 | [fusion-fiction.zip](plugins/fusion-fiction.zip) |
| **audio-to-video** 音频配画 | 给一段讲述音频（MP3 + 文本）配上精确贴合的视频画面，声轨就是用户原始母带 | [audio-to-video.zip](plugins/audio-to-video.zip) |
| **mashup** 混剪配画 | 给讲述音频配**现成素材**画面：不生成一帧视频，检索 YouTube/CC0 素材站下载切片混剪，零公差零漂移 | [mashup.zip](plugins/mashup.zip) |

### 功能说明

#### derivative-fiction — 衍生小说创作

主流程是「小说 → 视频」的**解析方向**；本插件补上**生成方向**的文本工位：复用项目中已完成的剧情、世界设定、人物、环境等 metadata（正史只读），产出风格可定制的长篇小说。

- **团队**：8 个 Agent —— 衍生企划、小说架构、文风圣经、章节规划、章节写作（每章扇出）、润色定稿、文本质量审核、发布排版；并复用内置的剧情逻辑 / 设定一致性 / 人设一致性 QA。
- **流程**：衍生立项 → 大纲 + 文风圣经 → 章节规划 → 逐章写作与润色（首章试读签字）→ 全书终审 → 发布排版（EPUB/TXT）。
- **产物**：写入独立命名空间 `data/projects/<slug>/derivative/`，严禁触碰正史 `bible/`。

#### fusion-fiction — 双书融合创作

把两本书融合成一部新剧本：**甲本**出故事、人物灵魂（可含美术风格）；**乙本**覆盖世界观（地理/政治/经济/宗教/文化等，按维度分配矩阵逐项确认）与人物形象壳。乙本若是世界名著/公版作品，可零文本输入，凭模型知识考据（名著模式）。

- **三个核心产物**：维度分配矩阵 `fusion_plan.json`、人物映射表 `character_map.json`（用户锁定 + 系统推荐）、概念转换字典 `dictionary.json`。
- **团队**：6 个新工位（融合企划、乙本考据、人物映射、世界融合、剧本移植、双源保真审核）+ 大量复用内置 Agent。
- **⚠️ 直改正史**：融合产物直接写回 `bible/`、`story/`，控制台既有预览页零改动即可呈现融合结果。分支与回滚由用户自行管理，**建议开工前先留 git 分支备份**。

#### audio-to-video — 音频配画

用户提供 MP3（如一个人讲历史故事）与对应文本，流程产出一条画面精确贴合音频的成片，**声轨就是用户原来那个 MP3，零重编码**。与主流程方向正好相反：主流程画面先定、旁白适配；本插件音频母带不可动，画面按 ffprobe 实测时长切分适配。

- **前置要求**：VideoAgents 版本需自带 `modules/avsync.py` 与 `code/check_av_sync.py`；本机 `ffmpeg / ffprobe` 可用；至少一个已登录的 agent 引擎；图像/视频生成渠道的 API Key。
- **注意**：旧版宿主上安装不会报错，真正的拦截点在流程第一个节点 `av0-ingest` 的自检——**装上没报错 ≠ 能用，以第一个节点的结论为准**。

#### mashup — 混剪配画

audio-to-video 的近亲，但**不生成一帧视频**：用户同样提供 MP3 讲述音频与文稿，画面改为检索 YouTube（主通道）与 Pexels/Pixabay（CC0 兜底）的**现成素材**，下载切片、拼接封装——生成成本变为检索与带宽成本。母带纪律与 audio-to-video 相同：声轨就是用户原始 MP3（`-c:a copy` 零重编码），ffprobe 实测为唯一时长事实源，累计漂移恒 0；且现成素材想切多准切多准，**交付零公差**。

- **拍/镜两层节奏（v2 方法论）**：拍 = 语义句（transcript-aligner 按句切、吸附停顿，时长事实）；镜由 shot-designer 逐拍找**信息焦点**、定对应模式——**literal（一致，画面直给，可长镜）** 或 **render（相辅相成，群像多镜快切渲染，0.8–2.5s/镜）**——后在拍内细分，镜长无上限、硬下限 0.5s，节奏感来源于此。保留主流程 p0–p2 世界观作画面/检索参考，**检索语言按文化圈定**（中文语境搜中文、日本文化搜日文、CC0 素材站恒英文）。
- **团队**：新增 6 个 Agent（音频摄入、拍轨对齐、分镜设计、素材侦察、选片核验（须视觉引擎）、下载切片）+ 1 个混剪 QA；复用内置剪辑/字幕/封面与各 QA 工位。分镜写标准 `shot_list.json`，**分镜预览页零改动呈现**，组注释即可调整检索意图。
- **成本阶梯**：元数据检索（零流量）→ 360p 预览抽帧（几 MB）→ 确认后才 1080p 区间下载（几十 MB）；同源视频整簇复用。**水印一票否决**（摸底约 1/3 候选因此被毙）。
- **版权口径**：不过滤 license，责任由用户 **MH1 签字自担**；流程强制登记来源台账 `sources.json`，unknown license 清单在 MH3 终签时呈给用户。
- **前置要求**：宿主自带 `modules/footage.py` + `code/check_footage.py`（v2 拍/镜口径）；本机 `yt-dlp`（2025.11+ 另需 node）与 `ffmpeg/ffprobe` 可用；选片工位须派给带视觉能力的引擎。装完先跑 `python3 modules/footage.py doctor`。同样**以第一个节点 `mx0-ingest` 的自检结论为准**。

### 如何安装

1. **下载 zip 包**：从本仓库的 [`plugins/`](plugins/) 目录下载所需插件的 zip 包（或 Clone 本仓库后取用）。
2. **上传安装**：打开 VideoAgents Web 控制台 → ⚙️ 设置 → 高级 → **插件** → 「安装插件包」→ 上传 zip，约 30 秒内被发现。
3. **手动启用**：安装后**默认停用**，须在「插件」页点击**启用**才生效。确认插件卡片显示的 agent 数量、workflow 路径正确，且 errors 为空。

命令行等价方式（请求体即 zip 原始字节，非 multipart）：

```bash
curl -X POST --data-binary @audio-to-video.zip http://127.0.0.1:8630/api/v1/plugins
```

**升级与卸载**：没有原地升级，同名安装一律 409。升级须先在「插件」页删除旧版，再上传新版 zip，然后**重新启用**（启用状态会丢失）。卸载只移除插件目录，项目内已生成的产物全部保留。

> 🔐 **安全提醒**：插件的 SOUL.md 会逐字注入模型系统提示词。安装第三方插件前请人工审阅全部内容，警惕越权指令（改正史/越命名空间写入/伪造回执）。有疑虑就不装。

### 使用提示词参考

安装并启用插件后，在项目对话中向总制片（orchestrator）发送类似下面的指令即可启动对应流程。

**derivative-fiction 衍生创作：**

```text
我要基于现在的项目进行衍生创作（使用衍生创作插件工作流），具体要求如下：
基于桐华的甄嬛传和东宫的写作风格，和当前的故事和人物把这个故事输出成一本小说。
人物的名字、性格、身份，故事和场景都保留，所以在小说创作时基于项目中已经完成的：
剧情、世界设定、人物、环境和建筑等 metadata，从而保证一致性。
小说在写作风格上需要使用桐华的风格（参考她写的甄嬛传和东宫两本书），去掉目前原始剧本的"登味"。
字数你根据故事需要和桐华的写作风格来确定，我不硬性要求。
目标读者以女性为主。
```

**fusion-fiction 双书融合：**

```text
启动 fusion-fiction 融合流程：甲本就是本项目，出故事、人物灵魂；
乙本《西游记》（名著模式），覆盖人物形象、地理、政治、经济、宗教。
人物映射我先指定：
福瓦德=孙悟空
巴沙拉特=土地公公
哈桑=唐僧
拉妮娅=女儿国国王
阿吉布=猪八戒
塔希娜=嫦娥
纳吉娅=紫霞仙子
麦姆娜=哪吒
其余你们推荐后给我确认。
```

**audio-to-video 音频配画：**

```text
启动 audio-to-video 流程：音频 refs/xxx.mp3，文本 refs/xxx.txt。
设计风格已在设计构想里选好。先跑 av0 摄入与对齐，出时间轴基线给我签 AVH1。
```

**mashup 混剪配画：**

```text
启动 mashup 混剪流程：音频 refs/audio/qingxing.mp3，文稿 refs/qingxing.txt。
先跑 p0–p2 出世界观参考，并行 mx0 摄入对齐，
再逐拍分镜设计，出时间轴与节奏基线给我签 MH1。
```

---

## English

The official plugin repository for VideoAgents. VideoAgents ships with 83 built-in agents covering the main "novel → video" pipeline; everything beyond that (derivative novels, two-book fusion, audio-to-video…) is published here as **plugins** — download a zip, upload it, done. No core changes required.

### Plugin Catalog

| Plugin | One-liner | Download |
|---|---|---|
| **derivative-fiction** | Write derivative novels (prequels/side stories/what-if lines) on top of the project's existing world bible, characters, and scene assets | [derivative-fiction.zip](plugins/derivative-fiction.zip) |
| **fusion-fiction** | Fuse two books into one new screenplay: Book A supplies the story and character souls, Book B supplies the worldview and character appearance shells | [fusion-fiction.zip](plugins/fusion-fiction.zip) |
| **audio-to-video** | Generate a video whose visuals precisely follow a narrated audio track (MP3 + transcript) — the soundtrack is the user's original master, untouched | [audio-to-video.zip](plugins/audio-to-video.zip) |
| **mashup** | Pair a narrated audio track with **found footage**: no video generation at all — search YouTube/CC0 stock sites, download and cut existing clips, zero tolerance and zero drift | [mashup.zip](plugins/mashup.zip) |

### What Each Plugin Does

#### derivative-fiction — Derivative Novel Writing

The main pipeline goes in the **parsing** direction (novel → video); this plugin adds the **generative** direction: it reuses the project's finished metadata — plot, world settings, characters, environments and architecture (canon is read-only) — to produce a full-length novel in a customizable prose style.

- **Team**: 8 agents — derivative planner, novel outline, prose-style bible, chapter planner, chapter writer (fanned out per chapter), line editor, prose QA, and release/packaging; plus reuse of the built-in logic / world-consistency / character-consistency QA agents.
- **Flow**: premise → outline + prose-style bible → chapter planning → per-chapter writing and editing (first-chapter sign-off) → full-book review → packaging (EPUB/TXT).
- **Outputs**: written to the dedicated namespace `data/projects/<slug>/derivative/`; the canonical `bible/` is never modified.

#### fusion-fiction — Two-Book Fusion

Fuses two books into one new screenplay: **Book A** supplies the story and character souls (optionally the art style); **Book B** supplies the worldview (geography/politics/economy/religion/culture — confirmed dimension by dimension via an allocation matrix) and the character appearance shells. If Book B is a public-domain classic, no text input is needed — the model's own knowledge is used ("classic mode").

- **Three core artifacts**: the dimension allocation matrix `fusion_plan.json`, the character map `character_map.json` (user-locked pairs + system recommendations), and the concept-conversion dictionary `dictionary.json`.
- **Team**: 6 new agents (fusion planner, classic scholar, character mapper, world merger, script transposer, fusion-fidelity QA) plus heavy reuse of built-in agents.
- **⚠️ Writes to canon directly**: fusion outputs are written straight back to `bible/` and `story/`, so the console's existing preview pages show the fused result with zero changes. Branching and rollback are the user's responsibility — **create a git branch backup before starting**.

#### audio-to-video — Audio-Driven Video

You provide an MP3 (e.g. someone narrating a history story) and its transcript; the pipeline produces a finished video whose visuals precisely match the audio — **the soundtrack is your original MP3, zero re-encoding**. It is the exact inverse of the main pipeline: there, visuals are fixed and narration adapts; here, the audio master is immutable and visuals are cut to the ffprobe-measured timeline.

- **Prerequisites**: a VideoAgents version that ships `modules/avsync.py` and `code/check_av_sync.py`; `ffmpeg / ffprobe` available locally; at least one logged-in agent engine; API keys for your image/video generation channels.
- **Note**: installing on an older host will NOT raise an error. The real gate is the self-check in the flow's first node, `av0-ingest` — **"installed without errors" ≠ "usable"; trust the first node's verdict**.

#### mashup — Found-Footage Mashup

A close cousin of audio-to-video, except **not a single frame is generated**: you provide the same MP3 narration and transcript, but the visuals come from searching **existing footage** on YouTube (primary channel) and Pexels/Pixabay (CC0 fallback), then downloading, cutting, and assembling the clips — generation cost becomes search and bandwidth cost. The master-track discipline is identical: the soundtrack is your original MP3 (`-c:a copy`, zero re-encoding), ffprobe measurements are the only source of duration truth, and cumulative drift is always 0. Since found footage can be cut to any precision, delivery is **zero-tolerance**.

- **Beat/shot two-layer rhythm (v2 methodology)**: a beat = one semantic sentence (cut by the transcript-aligner, snapped to pauses — the duration ground truth); shots are designed per beat by the shot-designer, which finds the **information focus**, picks a mapping mode — **literal** (text and picture say the same thing; one shot, can run long) or **render** (picture conveys complementary information via human states; 2–6 rapid-cut shots at 0.8–2.5s each) — then subdivides within the beat. Shots have no upper length limit and a hard 0.5s floor; this is where the rhythm comes from. The main pipeline's p0–p2 worldview runs as reference data, and **search language follows the cultural context** (Chinese topics searched in Chinese, Japanese culture in Japanese, CC0 stock sites always in English).
- **Team**: 6 new agents (audio ingest, transcript aligner, shot designer, footage scout, footage curator — requires a vision-capable engine — and clip cutter) plus one mashup QA; built-in editing/subtitle/thumbnail and QA agents are reused. Storyboards are written as standard `shot_list.json`, so the **existing storyboard preview page works with zero changes** — edit group annotations to adjust search intent.
- **Cost ladder**: metadata search (zero traffic) → 360p previews with frame grids (a few MB) → 1080p range downloads only after confirmation (tens of MB); one source video serves a whole cluster. **Watermarks are an instant veto** (~1/3 of candidates were killed for this in field testing).
- **Copyright stance**: licenses are not filtered — responsibility rests with the user via the **MH1 sign-off**; the pipeline enforces honest bookkeeping in a `sources.json` ledger, and the unknown-license list is presented at the final MH3 sign-off.
- **Prerequisites**: a host that ships `modules/footage.py` + `code/check_footage.py` (v2 beat/shot semantics); `yt-dlp` (2025.11+ also needs node) and `ffmpeg/ffprobe` available locally; the curator must run on a vision-capable engine. Run `python3 modules/footage.py doctor` after installing. As with audio-to-video, **trust the verdict of the first node, `mx0-ingest`**.

### Installation

1. **Download the zip** for the plugin you want from this repo's [`plugins/`](plugins/) directory (or clone the repo).
2. **Upload it**: open the VideoAgents web console → ⚙️ Settings → Advanced → **Plugins** → "Install plugin package" → upload the zip. It is discovered within ~30 seconds.
3. **Enable it manually**: plugins are **disabled by default** after installation — click **Enable** on the Plugins page. Verify the plugin card shows the expected agent count and workflow path, with no errors.

Command-line equivalent (request body is the raw zip bytes, not multipart):

```bash
curl -X POST --data-binary @audio-to-video.zip http://127.0.0.1:8630/api/v1/plugins
```

**Upgrade & uninstall**: there is no in-place upgrade — installing under the same name returns 409. To upgrade, delete the old version on the Plugins page first, upload the new zip, then **re-enable** (the enabled state is lost). Uninstalling only removes the plugin directory; all artifacts already generated inside your projects are preserved.

> 🔐 **Security note**: a plugin's SOUL.md files are injected verbatim into model system prompts. Manually review the full contents of any third-party plugin before installing — watch for privilege-escalating instructions (modifying canon, writing outside its namespace, forging receipts). When in doubt, don't install.

### Prompt Examples

After installing and enabling a plugin, send the orchestrator a message like the following in your project conversation to kick off the corresponding workflow.

**derivative-fiction:**

```text
I want to create a derivative work based on the current project (using the
derivative-fiction plugin workflow). Requirements:
Turn this story into a novel in the writing style of Tong Hua ("Empresses in
the Palace" and "Goodbye My Princess").
Keep all character names, personalities, identities, story and scenes — base the
writing on the project's finished metadata (plot, world settings, characters,
environments and architecture) to guarantee consistency.
Word count is up to you, based on the story's needs and Tong Hua's style.
Target audience is primarily female readers.
```

**fusion-fiction:**

```text
Start the fusion-fiction workflow: Book A is this project, supplying the story
and character souls; Book B is "Journey to the West" (classic mode), covering
character appearances, geography, politics, economy, and religion.
Character mappings I'm locking in first:
Fuwad = Sun Wukong
Basharat = the Earth God (Tudi Gong)
Hasan = Tang Sanzang
Rania = the Queen of the Women's Kingdom
Ajib = Zhu Bajie
Tahina = Chang'e
Najia = Fairy Zixia
Maimuna = Nezha
Recommend mappings for the rest and let me confirm.
```

**audio-to-video:**

```text
Start the audio-to-video workflow: audio refs/xxx.mp3, transcript refs/xxx.txt.
The design style has already been chosen in the design concept. Run av0 ingest
and alignment first, and give me the timeline baseline for the AVH1 sign-off.
```

**mashup:**

```text
Start the mashup workflow: audio refs/audio/qingxing.mp3, transcript
refs/qingxing.txt. Run p0–p2 first for the worldview reference, with mx0 ingest
and alignment in parallel, then design the storyboard beat by beat and give me
the timeline and rhythm baseline for the MH1 sign-off.
```
