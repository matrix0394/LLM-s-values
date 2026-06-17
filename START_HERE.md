# LLM Values 2026-06 Handoff

这是给师弟接手“大模型价值观”后续工作的第一入口。先看这一页，再看 `PACKAGE_README.md` 和 `docs/code_data_handoff_2026-06.md`。

## GitHub 地址

目标仓库：

```bash
https://github.com/matrix0394/LLM-s-values.git
```

交接分支名：

```bash
codex/llm_values_2026_06
```

如果分支已经推到 GitHub，师弟可以这样拿代码：

```bash
git clone -b codex/llm_values_2026_06 https://github.com/matrix0394/LLM-s-values.git llm_values_2026_06
cd llm_values_2026_06
```

如果 GitHub 上还看不到这个分支，说明本地已经整理和提交，但还没有成功 push。可从本机整理好的副本推送：

```bash
cd /private/tmp/llm_values_github_branch_2026_06_local
git push -u github codex/llm_values_2026_06
```

## 先跑这几个命令

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/run/run_paper_analysis.py --help
python3 src/run/run_paper_analysis.py --study 2
python3 external_runners/hk_local_hf_interview_upload.py --help
```

Study 2 的正式样本口径应为：

```text
Models: 20
Total model×country×language observations: 920
Overall English Advantage: +3.6%
```

## 这个包包含什么

- 可运行代码：`src/`、`analysis/`、`config/`、`external_runners/`
- 主入口：`src/run/run_paper_analysis.py`
- 香港本地 Hugging Face runner：`external_runners/hk_local_hf_interview_upload.py`
- 核心 PCA 和轻量结果：`data/country_values/`、`data/llm_pca/`、`results/analysis/`、`results/paper_data/`
- BLOOM/PolyLM 旧 pilot 的少量 raw 记录，用来说明旧结果为什么只能作调试参考

## 这个包不包含什么

- WVS/EVS 官方原始 `.sav`
- `ivs_df.pkl`、`valid_data.pkl` 这类几 GB 的派生缓存
- 全量 API/raw interview
- `.env`、zip、本机临时文件、Python cache

WVS/EVS 原始数据是官方可获得的数据，不应放进 GitHub。需要从头重建人类基准时，让师弟从 WVS 官网下载 `Integrated_values_surveys_1981-2022.sav`，再放到项目约定路径。

## 正式样本和探索样本不要混

当前 PCA 文件里保留了后续探索模型：

```text
qwen3-1.7b
glm-4.6
qwq-32b
```

它们可以留给后续扩展分析，但正式 Study 1-4 和 model imitation 使用 20-model paper sample，`src/run/run_paper_analysis.py` 已排除这三个探索模型。不要把它们混进正式论文统计，否则 Study 2 的 English Advantage 会被拉偏。

## 师兄说的后续工作怎么接

后续不是只看旧 PCA，也不是从一堆原始 API 回答开始瞎跑。正确顺序是：

```text
新模型回答 WVS/IVS 题
  -> 解析/adjudication 成 10 个题目的数值回答
  -> 用固定 PCA 模型投影到同一文化空间
  -> 跟人类国家坐标算距离
  -> 纳入 Study 1-4 / model imitation / 新优化实验比较
```

三类后续任务：

- 旧模型补测：BLOOM、PolyLM 等。旧 pilot 只作调试参考，正式结果要重新用稳定 runner 跑。
- 最新模型更新：把新 API 模型或新开源模型接到同一套问卷、解析、PCA、分析流程。
- 多语言模型优化：比较 prompt、本地化语言、解析策略、adjudication、微调或后处理方法是否能减少语言偏差。

## 下一步读什么

- `PACKAGE_README.md`：这个包里有哪些文件、哪些没放、验证过哪些命令。
- `docs/code_data_handoff_2026-06.md`：完整交接说明。
- `docs/data_flow_traceability.md`：数据从原始回答到 PCA/统计的链路。
- `docs/REPRODUCIBILITY.md`：复现说明。

---

下面保留完整交接说明原文，供需要细节时继续往下读。

# Code And Data Handoff Guide

交接时间建议：2026-06-17 周三  
项目路径：`/Users/yxy/code/LLM's values`  
当前本地分支：`codex-hk-local-hf-roleplay`

这份文档给接手同学快速理解三件事：

1. 论文主线代码如何复现已有结果。
2. 数据和结果文件哪些是核心、哪些是可选或不要公开。
3. 后续旧模型、最新模型、本地 Hugging Face 模型和多语言优化实验应该从哪些固定入口继续。

## 一、先讲清楚项目在做什么

项目研究 LLM 在不同语言和国家角色扮演条件下表达出的文化价值观。核心方法是让模型回答 10 道 WVS/IVS 价值观问卷题，再把回答投影到固定的 Inglehart-Welzel 二维文化空间，与 66 个国家/地区的人类基准坐标比较。

当前主论文线索可以概括为：

- Study 1：LLM 内在价值观的世俗理性偏差，以及不同语言 baseline 的差异。
- Study 2：非英语国家中，英语角色扮演是否比母语角色扮演更接近真实国家坐标。
- Study 3：非西方国家的英语优势更强，形成数字东方主义现象。
- Study 4：东亚、港澳、拉美、非洲等殖民/语言历史相关分析。
- Model imitation：模型用英语角色扮演 66 国时的整体模仿准确度排名。

接手顺序建议：先用已经生成好的 PCA 坐标和 `run_paper_analysis.py` 弄清楚“10 道题回答 -> PCA 坐标 -> 与人类国家坐标算距离 -> English Advantage/Model imitation”这条评价链；然后再开始跑旧模型、最新模型、本地 HF 模型或多语言优化实验。不是不跑新模型，而是新实验也要接到同一条 raw answer -> adjudication/解析 -> PCA 投影 -> 统计分析链条上，避免只收了一堆原始回答却无法和主线结果比较。

师兄安排的后续工作可以分成三类：

- 旧模型补测：例如 BLOOM/PolyLM 这类本地或开源多语言模型，重点是验证它们是否能稳定回答 WVS 题，而不是直接信旧 pilot 的解析结果。
- 最新模型更新：把新 API 模型或新开源模型接到现有问卷和 PCA 评价流程里，和 20-model paper sample 保持可比。
- 多语言模型优化：围绕语言提示、回答解析、adjudication、翻译/本地化 prompt、模型微调或后处理方法做毕业论文可能需要的扩展实验。

## 二、推荐交接方式

建议交给师弟三包材料。

### 1. 代码包

代码仓库在：

```bash
/Users/yxy/code/LLM's values
```

当前远端是：

```bash
https://github.com/matrix0394/LLM-s-values.git
```

不要把当前整个本地目录直接复制给师弟。整体可以按下面三包讲，但实际交付时要先把代码仓库和数据实体分开：

1. 代码层：让师弟从 GitHub 干净 clone，或者在一个明确命名的交接分支上接手。
2. 数据层：用网盘/移动硬盘单独给“轻量复现包”和必要的大数据，不把几 G 的 WVS/EVS 原始数据、缓存和 zip 混进 Git。

我检查过当前本地工作区，里面混着四类东西：

| 类别 | 当前代表内容 | 怎么处理 |
|------|--------------|----------|
| 可进入交接版的代码/文档 | `README.md`、`docs/REPRODUCIBILITY.md`、`docs/data_flow_traceability.md`、`docs/code_data_handoff_2026-06.md`、`src/run/`、`src/base/`、`src/roleplay_multilingual/` | 最终应在干净分支里 review 后提交，作为师弟接手的代码基线 |
| 需要单独交的数据 | `data/llm_pca/`、`data/country_values/country_scores_pca.json`、`data/country_values/pca_model_fixed.pkl`、`data/external/regression_covariates.csv`、`results/analysis/`、`results/paper_data/`、`Supplementary Materials/data/` | 不走 GitHub；单独打包或网盘交接 |
| 本机保留但不要交 | `.env`、`.cursor/`、`.mplconfig/`、根目录 zip、历史解压副本、临时/异常文件名 | 不发给师弟，不提交 Git；确认无用后再移到废纸篓 |
| 待确认再清理 | `SI/` 中大量新版/旧版图表、旧中文汇报目录、旧 references、旧 results dashboard、历史 zip/副本 | 先不要直接删；确认“论文提交版是否还需要”后再清 |

当前根目录尤其要注意这些不建议交付的东西：

```text
.env
.cursor/
.mplconfig/
LLM's values.zip
The Value Atlas of AI.zip
The Value Atlas of AI/
LLM's values/
```

另外，当前 Git 状态里有大量 tracked 文件被删除、也有大量 untracked 文件。如果直接 `git clean` 或直接把本地状态当最终版，很容易把仍然有用的 `data/`、`Supplementary Materials/`、`analysis/`、`config/` 一起误判成垃圾。因此，交接时请按本节分层给材料，而不是把“当前脏工作区”原样交出去。

#### 本次整理版的验证边界

本次整理出的 clean/ready 版是“轻量复现和继续开发包”，不是“从官方原始数据和全量 API raw response 重新生成一切的完整大包”。

已验证可以跑：

```bash
python3 src/run/run_paper_analysis.py --help
python3 src/run/run_paper_analysis.py
python3 src/run/run_paper_analysis.py --regression-only
python3 external_runners/hk_local_hf_interview_upload.py --help
```

因此，ready 版能支持师弟先复现 Study 1-4、model imitation、回归数据生成，并理解香港本地 HF runner 的参数。

重要：当前 PCA 文件里包含后续/探索性多语言模型：`qwen3-1.7b`、`glm-4.6`、`qwq-32b`。正式论文/交接分析用 20-model paper sample，`src/run/run_paper_analysis.py` 会排除这三个模型。它们不要删，留给后续扩展分析；但不要混进 Study 1-4 或 model imitation 的正式统计。尤其 `qwen3-1.7b` 如果混进 Study 2，overall English Advantage 会被拉到约 `-0.215%`，这不是正式样本结果。

ready 版刻意不包含，所以不能直接跑的内容：

```text
python3 src/run/run_paper_analysis.py --rebuild-from-raw
python3 src/run/run_country_values_analysis.py
```

原因是 ready 版没有放全量原始大数据：

```text
WVS/EVS 官方原始 .sav
data/country_values/ivs_df.pkl
data/country_values/valid_data.pkl
data/llm_interviews/*/interview_raw/ 全量 API/raw 访谈
```

例外：ready 版保留了香港本地 HF 旧 pilot 的两组小 raw 记录，供师弟理解 BLOOM/PolyLM 为什么不能直接当正式结果：

```text
data/llm_interviews/multilingual/interview_raw/bloom-1b7/
data/llm_interviews/multilingual/interview_raw/polylm-1.7b/
```

如果师弟要从头重建，需要按下面“官方原始数据”和“LLM 原始访谈”两节补齐这些大文件。

### 2. 数据包

数据不要简单分成“能不能给”。更准确的分法是：哪些是论文复现必须文件，哪些是 WVS/EVS 官方可重新下载的原始数据，哪些只是本项目生成的中间缓存。WVS/IVS 那几个大文件不是“拿不到”或“不能用”，而是没有必要放进 GitHub；实验室内部交接时可以直接传，或者让师弟按官方来源重新下载。

先用这张表判断每类数据的身份：

| 路径/文件 | 数据身份 | 来源 | 主要用途 | 交接建议 |
|-----------|----------|------|----------|----------|
| `Integrated_values_surveys_1981-2022.sav` | 官方原始调查数据 | WVS/EVS 官方下载 | 从头重建人类文化基准 | 可以传；也可以让师弟从 WVS 官网重新下载。不要放 Git/GitHub |
| `data/country_values/ivs_df.pkl` | 本地派生缓存 | 由 `.sav` 读入后保存 | 省去重新解析 SPSS 文件的时间 | 可以传给师弟省时间；不是唯一来源，可重建 |
| `data/country_values/valid_data.pkl` | 本地派生中间表 | 由 `DataProcessor.get_filtered_data()` 生成 | 2005 年后、至少 6 题有效的 IVS 子集 | 可重建，只有从头跑 Stage 0 时才需要 |
| `data/country_values/country_scores_pca.json` | 核心人类基准坐标 | 由 Stage 0 PCA 生成 | 66/112 国家 WVS/IVS 坐标，供距离计算 | 必须给，轻量且关键 |
| `data/country_values/pca_model_fixed.pkl` | 冻结 PCA 模型 | 由 Stage 0 PCA 生成 | 把 LLM 回答投影到同一文化空间 | 必须给，缺它无法投影新 LLM 回答 |
| `data/llm_interviews/*/interview_raw/` | LLM API 原始回答 | 本项目采集/API 生成 | debug 单题、重做 parser、审计模型回答 | 按需传；体积大，不是复现统计的第一入口 |
| `data/llm_interviews/*/processed/` | LLM 回答转 IVS 格式 | 本项目处理生成 | 从 processed 重新做 PCA | 要重跑 PCA 或修正解析时传 |
| `data/llm_pca/intrinsic/` | Study 1 坐标 | 本项目处理生成 | baseline/intrinsic 价值观分析 | 必须给 |
| `data/llm_pca/multilingual/` | Study 2-4 坐标 | 本项目处理生成 | 角色扮演、英语优势、东方主义、殖民分析 | 必须给 |
| `data/external/` | 回归协变量 | World Bank、HDI、EF EPI、殖民历史等外部表 | 回归和补充分析 | 建议给，尤其是 `regression_covariates.csv` |
| `results/analysis/` | 已跑出的统计结果 | `run_paper_analysis.py` 等脚本生成 | 快速核对论文数字 | 建议给 |
| `results/paper_data/` | 论文图表源数据 | `regenerate_paper_data.py` 等脚本生成 | 画 Figure 1-4、回归表 | 建议给 |
| `Supplementary Materials/data/` | publication-ready 数据表 | 从项目结果整理而来 | 给审稿/读者查看的公开数据 | 建议给 |

#### A. 轻量复现包：建议必须给

这组文件不大，能让师弟先复现主论文统计和图表数据：

```text
data/country_values/country_scores_pca.json
data/country_values/pca_model_fixed.pkl
data/country_values/Table_S5_IVS_PCA_coordinates.csv
data/llm_pca/intrinsic/
data/llm_pca/multilingual/
data/external/regression_covariates.csv
results/analysis/study*.json
results/paper_data/
Supplementary Materials/data/
```

其中最关键的是：

- `country_scores_pca.json`：人类国家/地区的 PCA 坐标。
- `pca_model_fixed.pkl`：冻结的 PCA 投影模型，所有 LLM 回答都靠它投到同一坐标空间。
- `data/llm_pca/intrinsic/`：Study 1 baseline 坐标。
- `data/llm_pca/multilingual/`：多语言角色扮演坐标，Study 2-4 主要依赖它。
- `Supplementary Materials/data/`：publication-ready 数据表，适合给不想跑全 pipeline 的人快速查看。

#### B. 官方原始数据：WVS/EVS 可获得，建议说明来源

这些文件很大，但来源是官方数据。它们不是项目私有数据；如果师弟需要从头重建人类基准，可以从官方源获取。

```text
Integrated_values_surveys_1981-2022.sav
```

获取方式：

1. 访问 World Values Survey 官方网站：`https://www.worldvaluessurvey.org/`
2. 在 Data Download / WVS-EVS integrated 或 trend data 页面下载 `Integrated_values_surveys_1981-2022.sav`。
3. 下载后按本项目 runner 的默认路径放到：

```text
data/raw/Integrated_values_surveys_1981-2022.sav
```

注意：你本地当前有一份在：

```text
data/country_values/Integrated_values_surveys_1981-2022.sav
```

但 `src/run/run_country_values_analysis.py` 默认检查的是 `data/raw/Integrated_values_surveys_1981-2022.sav`。如果师弟要重建 Stage 0，需要把官方 `.sav` 放到 `data/raw/`，或者相应调整 runner 路径。

#### C. 本地派生缓存：能传但可重建

```text
data/country_values/ivs_df.pkl
data/country_values/valid_data.pkl
data/country_values/variable_view.pkl
data/country_values/country_scores_pca.pkl
```

这些不是 WVS 官方原始文件，而是本项目从 `.sav` 读入、过滤、保存出来的缓存。`ivs_df.pkl` 约 4.2G，传给师弟可以省时间，但不是唯一来源。要从官方 `.sav` 重建这些文件，运行：

```bash
python3 src/run/run_country_values_analysis.py
```

该脚本会做三步：

```text
data/raw/Integrated_values_surveys_1981-2022.sav
  -> data/country_values/ivs_df.pkl
  -> data/country_values/valid_data.pkl
  -> data/country_values/country_scores_pca.json / .pkl
  -> data/country_values/pca_model_fixed.pkl
  -> results/country_values/
```

#### D. LLM 原始访谈：按需求传

```text
data/llm_interviews/*/interview_raw/
data/llm_interviews/*/processed/
```

这些是本项目/API 生成的数据，不是 WVS 官方数据。是否传取决于师弟接手目标：

- 只复现论文统计：优先给 `data/llm_pca/` 和 `results/analysis/`，不一定需要全量 raw。
- 要 debug 某个模型为什么偏：给对应模型/国家/语言的 raw JSON。
- 要重跑 PCA 或修正 parser：给 processed 和 raw 都更稳。

交接时可以把数据讲成两种路线：

- 快速复现路线：给轻量复现包，先跑 `run_paper_analysis.py`。
- 从头重建路线：师弟从 WVS 官方下载 `.sav`，再跑 `run_country_values_analysis.py` 和后续 LLM pipeline。

### 3. 近期香港本地 HF 实验包

近期真正要接手的扩展实验不是主论文复现，而是香港本地 Hugging Face / Colab 模型访谈。

固定入口优先使用：

```bash
/Users/yxy/Downloads/hk_local_hf_interview_upload.py
```

这个文件是单文件 runner，适合上传到 Colab 或 AutoDL。它能做：

- 跑 Hugging Face 本地模型访谈。
- 输出 raw JSON。
- 生成 `adjudication.csv` 供人工判定。
- 可选用 DeepSeek 自动把文本回答映射回原始选项编号。
- 根据 `pca_model_fixed.pkl` 生成 PCA 坐标。
- 生成 English advantage 汇总。

仓库里的简版入口：

```bash
src/run/run_local_hf_hk_pilot.py
```

只适合作 smoke test。它只跑香港 `en-native` 和 `zh-hk`，主要保存 raw answer 和简单有效率，不是完整正式 pipeline。

## 三、核心目录怎么读

```text
config/
  country/                 国家编码、文化区域
  models/                  LLM 模型注册表
  questions/               IVS/WVS 10 道题和多语言题干

src/
  base/                    通用基础设施：API 调用、问卷校验、PCA 投影
  country_values/          Stage 0，人类 WVS/IVS 基准构建
  llm_values/              Stage 1，LLM 内在价值观 baseline
  roleplay_multilingual/   Stage 3，多语言国家角色扮演
  analysis/                距离、图表数据、比较分析
  run/                     固定运行入口

analysis/
  si/                      SI 图表生成
  core/                    stage0 vs stage3 距离分析
  language/                东方主义、殖民历史等扩展分析
  figures/                 正文图表脚本
  outputs/                 之前生成的 audit 输出

data/
  country_values/          人类基准坐标和固定 PCA 模型
  external/                回归协变量
  llm_interviews/          LLM 原始访谈和处理结果
  llm_pca/                 LLM PCA 坐标

results/
  analysis/                Study 结果 JSON、距离表、中间分析
  paper_data/              论文图表数据和回归表

Supplementary Materials/
  data/                    publication-ready 数据表
  figures/                 附录图表
```

## 四、主论文复现入口

先确认参数：

```bash
python3 src/run/run_paper_analysis.py --help
```

常用命令：

```bash
# 跑 Study 1-4 和 model imitation 相关分析
python3 src/run/run_paper_analysis.py

# 只跑某些 Study
python3 src/run/run_paper_analysis.py --study 1
python3 src/run/run_paper_analysis.py --study 2 3

# 只生成回归 CSV
python3 src/run/run_paper_analysis.py --regression-only

# 从原始访谈 JSON 重建 PCA 后再分析
python3 src/run/run_paper_analysis.py --rebuild-from-raw
```

输出主要在：

```text
results/analysis/study1_intrinsic_bias.json
results/analysis/study2_english_advantage.json
results/analysis/study3_digital_orientalism.json
results/analysis/study4_colonial_legacies.json
results/analysis/model_imitation_accuracy.json
results/analysis/paper_statistics_all.json
results/paper_data/regression_data.csv
```

注意：`--help` 里 Study 只支持 `1,2,3,4`。Model imitation 是补充分析，主入口参数不是 `--study 5`；当前交接版完整重跑后以 `model_imitation_accuracy.json` 为准，旧的 `study5_model_imitation.json` 可能是历史结果。

## 五、PCA 和距离计算要点

全项目最关键的文件：

```text
data/country_values/pca_model_fixed.pkl
```

作用：把 LLM 的 10 道题回答投影到和 WVS/IVS 人类数据同一个二维文化空间。

核心流程：

```text
原始访谈 JSON
  -> 提取 10 道题答案
  -> 转为 IVS 编码
  -> 用 pca_model_fixed.pkl 投影
  -> 得到 PC1 / PC2 坐标
  -> 与 country_scores_pca.json 中的人类国家坐标算距离
```

English Advantage 公式：

```text
EA = (d_native - d_english) / d_native * 100%
```

解释：

- EA > 0：英语 prompt 比母语 prompt 更接近人类基准。
- EA < 0：母语 prompt 更接近人类基准。

香港在主论文分析中不是英语母语国家，母语条件应看 `zh-hk`，不是把香港归入 English-native。

## 六、已有关键结果状态

下面数字来自我在交接 ready 版中运行 `python3 src/run/run_paper_analysis.py` 的输出，时间为 2026-06-15。用于交接时快速解释，不需要死背；如果之后数据或模型列表变化，以当次重跑生成的 `results/analysis/*.json` 为准。

### Study 1

文件：

```text
results/analysis/study1_intrinsic_bias.json
```

当前样本：20 个模型，6 种语言，共 120 个 model-language 组合。  
PC1 语言差异显著：`F = 3.349, p = 0.0074`。  
英语和阿拉伯语在 secular-rational 方向差异明显，`en_ar_divergence = 1.60`。

### Study 2

文件：

```text
results/analysis/study2_english_advantage.json
```

当前结果：20 个模型、40 个非英语国家，共 920 条 model-country-language 观测。  
overall English advantage 约 `3.594%`。  
country-level paired t-test：`t = 2.343, p = 0.024307`，当前正式样本显著。  
香港 `ea_from_means` 约 `20.56%`。

### Study 3

文件：

```text
results/analysis/study3_digital_orientalism.json
```

非西方国家英语优势高于西方国家：

```text
western_vs_nonwestern_d = 2.30
t = 6.08
p = 0.0
```

文化距离与英语优势在 country-level 上相关很强：`pearson_r = 0.792`。

### Study 4

文件：

```text
results/analysis/study4_colonial_legacies.json
```

东亚/儒家实体分层里：

```text
China       EA = 0.1
Japan       EA = 3.3
Hong Kong   EA = 20.6
Macao       EA = -5.3
```

可以用来解释香港和澳门的语言历史差异，但注意一些子分析样本量很小，要避免讲得过满。

### Model Imitation

文件：

```text
results/analysis/model_imitation_accuracy.json
```

英语角色扮演 66 国的平均距离排名里，当前前几名包括：

```text
gpt-4o
deepseek-chat
qwen3-max
deepseek-chat-v3.1
llama-3.3-70b-instruct
```

这个结果适合讲“模型整体模仿准确度”，不要和语言优势指标混淆。

## 七、香港本地 HF / Colab 实验怎么接

### 1. 推荐入口

上传或使用：

```bash
/Users/yxy/Downloads/hk_local_hf_interview_upload.py
```

查看参数：

```bash
python3 /Users/yxy/Downloads/hk_local_hf_interview_upload.py --help
```

### 2. Colab / AutoDL 依赖

典型安装：

```bash
pip install -U transformers accelerate sentencepiece safetensors huggingface_hub bitsandbytes
pip install "numpy<2.1" "pandas==2.2.2"
```

如果需要 DeepSeek 自动判定：

```bash
export DEEPSEEK_API_KEY=...
```

不要把 key 写进代码或上传到 GitHub。

### 3. 最小 smoke test

先跑一个模型、一个国家、两个语言：

```bash
python hk_local_hf_interview_upload.py \
  --models bloomz_mt \
  --country "Hong Kong" \
  --languages en zh-hk \
  --consensus-count 1 \
  --max-new-tokens 64 \
  --output-dir ./hk_local_hf_interviews
```

### 4. 正式香港实验

正式跑香港时建议保持 5 次 consensus：

```bash
python hk_local_hf_interview_upload.py \
  --models bloomz_mt polylm_chat_13b \
  --country "Hong Kong" \
  --languages en zh-hk \
  --consensus-count 5 \
  --pca-model-path ./pca_model_fixed.pkl \
  --country-coordinates-path ./country_scores_pca.json \
  --output-dir ./hk_local_hf_interviews
```

如果模型输出不是纯数字，不要直接信 legacy digit extraction。先看：

```text
models/<model_alias>/raw/
models/<model_alias>/adjudication/adjudication.csv
```

可用 DeepSeek 自动判定：

```bash
python hk_local_hf_interview_upload.py \
  --skip-interview \
  --auto-adjudicate deepseek \
  --judge-confidence-threshold 0.8 \
  --pca-model-path ./pca_model_fixed.pkl \
  --country-coordinates-path ./country_scores_pca.json \
  --output-dir ./hk_local_hf_interviews
```

最终看：

```text
models/<model_alias>/final/final_answers_long.csv
models/<model_alias>/final/final_answers_wide.csv
models/<model_alias>/coordinates/coordinates.csv
models/<model_alias>/coordinates/english_advantage.csv
summaries/all_final_answers_long.csv
summaries/all_final_answers_wide.csv
summaries/all_coordinates.csv
summaries/all_english_advantage.csv
```

### 5. 旧 pilot 记录怎么解释

旧 pilot 在：

```text
results/analysis/local_hf_hk_pilot_20260428_*.csv
data/llm_interviews/multilingual/interview_raw/bloom-1b7/
data/llm_interviews/multilingual/interview_raw/polylm-1.7b/
```

这两组已经放进 ready 交接版。它们不是主论文 20-model 多语言 PCA 样本，也不是正式香港结论；它们是“为什么后续要换成 `hk_local_hf_interview_upload.py` + adjudication”的证据。

这些只能当 smoke test / 失败记录，不能当正式结论。原因：

- 早期很多记录只跑了 1 道题。
- BLOOM / PolyLM 小模型经常复读 prompt 或 format hint。
- 旧 legacy parser 会从文本里抽数字，比如把“第3次嘗試”里的 `3` 当答案。

后续如果继续跑 BLOOM/PolyLM，不要沿用旧 `bloom-1b7` / `polylm-1.7b` pilot 的解析结果。应使用 ready 版里的：

```text
external_runners/hk_local_hf_interview_upload.py
```

当前 runner 里相关 alias 包括：

```text
bloom_7b1
bloomz_7b1
bloomz_mt
polylm_base_13b
polylm_instruct_13b
polylm_chat_13b
```

建议正式香港扩展先用 `bloomz_mt` 和 `polylm_chat_13b` 做小样本 smoke test，再用 raw answer + adjudication 生成最终坐标。

已有 audit 结果：

```text
analysis/outputs/hk_legacy_parsing_audit_summary.csv
analysis/outputs/hk_legacy_parsing_audit_rows.csv
```

其中 `polylm-1.7b zh-hk` 有较高 legacy-like extraction 风险；这正是后续要用人工/DeepSeek adjudication 的原因。

## 八、Qwen 交接草稿需要修正的点

Qwen 写的总体框架可用，但要改这些：

1. 当前远端仓库是 `matrix0394/LLM-s-values.git`，不是草稿里的另一个仓库名。
2. 当前 `run_paper_analysis.py --study` 只支持 1-4；Study 5/model imitation 是补充分析，不是 `--study 5`。
3. 数据不是“全部都应该打包给师弟”。WVS/EVS 原始 `.sav` 是官方可获得数据，实验室内部可以传或让师弟重下；`ivs_df.pkl` 是本项目派生缓存，可重建。真正要区分的是“轻量复现必需、从头重建才需要、debug 才需要”。
4. 香港本地 HF 实验不应该继续用早期 smoke test 结果作为正式数据。
5. `Downloads/hk_local_hf_interview_upload.py` 是当前最完整的 Colab/AutoDL 接手入口；仓库内 `run_local_hf_hk_pilot.py` 是窄版 smoke test。

## 九、周三会议流程建议

### 0-10 分钟：研究问题

讲清楚一张图：

```text
LLM 回答 10 道 WVS/IVS 题
  -> 投影到二维文化地图
  -> 与 66 国人类坐标比较
  -> 看语言、国家、模型来源带来的偏差
```

### 10-25 分钟：代码结构

打开：

```text
README.md
docs/REPRODUCIBILITY.md
docs/data_flow_traceability.md
src/run/run_paper_analysis.py
```

重点讲 `src/run/` 是固定入口，不要到处找临时脚本。

### 25-40 分钟：现场复现

建议现场跑：

```bash
python3 src/run/run_paper_analysis.py --help
python3 src/run/run_paper_analysis.py --study 2
```

然后打开：

```text
results/analysis/study2_english_advantage.json
results/paper_data/figure3_digital_orientalism.csv
```

### 40-55 分钟：后续模型实验任务

讲：

- 后续不是只复现论文，还要测旧模型、最新模型和多语言优化方法。
- API 新模型继续接主项目的问卷/PCA/analysis 流程。
- 本地或开源 HF 模型优先用 `external_runners/hk_local_hf_interview_upload.py` 或 `/Users/yxy/Downloads/hk_local_hf_interview_upload.py`。
- 为什么旧 BLOOM/PolyLM pilot 不能直接当正式结果。
- 为什么所有新实验都要保留 raw answer + adjudication + PCA coordinates。

### 55-60 分钟：权限和注意事项

确认：

- OpenRouter key 谁管理。
- DeepSeek adjudication key 谁管理。
- 原始 IVS 数据是否能给。
- 师弟是否从干净分支接手。
- 未来新实验入口固定放哪里，不要再散落到多个目录。

## 十、接手后的第一周任务建议

1. 用干净环境跑通 `python3 src/run/run_paper_analysis.py --study 2`，确认能复现正式样本的 English Advantage。
2. 读懂 `data/country_values/pca_model_fixed.pkl` 和 `data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.*` 的作用。
3. 挑一个后续任务做最小闭环：旧模型补测、最新模型更新、本地 HF 模型、或多语言 prompt/adjudication 优化。
4. 如果跑本地 HF 模型，用 `hk_local_hf_interview_upload.py` 在 Colab/AutoDL 先跑一个最小 smoke test。
5. 手动检查 20 条 raw response，确认模型是输出真实答案还是复读 prompt。
6. 再决定是否启用 `--auto-adjudicate deepseek` 批量判定。
7. 正式跑前先定好输出目录、模型列表、语言列表和 adjudication 规则，不要把新结果散落到 `analysis/colab`、`src/run`、`Downloads` 多处。

## 十一、最容易踩的坑

- 不要把 `.env` 或 API key 发进群。
- WVS/EVS 原始 `.sav` 官方可下载，但不要放进 Git/GitHub；实验室内部交接可以传，或者让师弟从 WVS 官网重新下载。
- `ivs_df.pkl` 是本地派生缓存，不是官方原始文件；体积大，可以传给师弟省时间，也可以从 `.sav` 重建。
- 不要把旧 `local_hf_hk_pilot_20260428` 当正式实验。
- 不要只看 success_rate，raw response 可能是复读 prompt。
- 不要新建一堆一次性脚本，优先扩展固定入口。
- 不要在主分支直接做实验性改动。
- 不要把香港当 English-native；香港母语条件是 `zh-hk`。
- 不要混淆 `en` 和 `en-native`：主线数据里香港历史上有 `en-native` 命名，但分析语义上是英语提示条件，不代表香港是英语母语国家。

## 十二、一句话交接版

先让师弟跑通 `run_paper_analysis.py`，理解 `pca_model_fixed.pkl -> llm_pca -> results/analysis` 这条主线；后续无论是测旧模型、最新模型、本地 HF 模型，还是做多语言优化，都要把新回答接回 raw answer -> adjudication/解析 -> PCA coordinates -> analysis 的固定链条，不要直接继承旧 smoke test 的解析结果。
