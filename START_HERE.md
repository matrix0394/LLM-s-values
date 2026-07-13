# LLM Values 2026-06 Handoff

这个目录就是给师弟接手“大模型价值观”后续工作的最终轻量项目包，不是建议稿。GitHub 包只放能跑主线和继续开发所需的代码、配置、轻量 PCA 坐标、统计结果和必要文档；旧图表、PPT、重复发布材料、几 GB 的缓存和官方原始数据不放进来。

## GitHub

仓库地址：

```bash
https://github.com/matrix0394/LLM-s-values.git
```

交接分支：

```bash
codex/llm_values_2026_06
```

分支推上 GitHub 后，师弟直接 clone：

```bash
git clone -b codex/llm_values_2026_06 https://github.com/matrix0394/LLM-s-values.git llm_values_2026_06
cd llm_values_2026_06
```

当前本机已经整理并提交好这个分支。如果 GitHub 上还看不到分支，从本机推送：

```bash
cd /private/tmp/llm_values_github_branch_2026_06_local
git push -u github codex/llm_values_2026_06
```

## 包里保留的内容

```text
src/                 固定代码入口和核心模块
config/              国家、模型、WVS/IVS 题目 JSON 配置
external_runners/    本地 HF / Colab / AutoDL runner
             
 data/country_values/ 人类 PCA 坐标和固定 PCA 模型
 data/llm_pca/        主线分析所需 LLM PCA 坐标表和 entity_scores
 data/external/       回归协变量
 data/llm_interviews/ BLOOM/PolyLM 香港旧 pilot 的少量 raw 记录
results/analysis/    Study JSON、CSV/XLSX 统计结果
results/paper_data/  论文图表/表格源数据 CSV
docs/                复现、数据流、交接说明
```

已从包里移走：根目录旧 `analysis/` 脚本堆、PPT、PNG/PDF/DOCX/HTML/TEX 图表文档、`Supplementary Materials/`、`dryad/`、backup 文件、完整 PCA 中间对象、嵌套 `.git`。

## 第一次运行

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python src/run/run_paper_analysis.py --help
python src/run/run_paper_analysis.py --study 2
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 src/run/run_paper_analysis.py --help
python3 src/run/run_paper_analysis.py --study 2
python3 external_runners/hk_local_hf_interview_upload.py --help
```

Study 2 正式口径应看到：

```text
Models: 20
Total model×country×language observations: 920
Overall English Advantage: +3.6%
```

## 不放 GitHub、由你网盘/微信发给师弟的数据

这些是本项目自己跑出来的 raw/intermediate 数据。不是 GitHub 包必需，但如果师弟要从头 debug、重做 parser 或完全重建中间结果，可以单独发。

```text
/Users/yxy/code/LLM's values/data/country_values/ivs_df.pkl
  约 4.2G，WVS .sav 读入后的派生缓存。可重建，但发给师弟能省时间。

/Users/yxy/code/LLM's values/data/country_values/valid_data.pkl
  约 31M，过滤后的 IVS 有效样本缓存。可重建。

/Users/yxy/code/LLM's values/data/llm_interviews/multilingual/interview_raw/
  约 176M，全量多语言角色扮演 API/raw 回答。要重做解析或审计模型回答时发。

/Users/yxy/code/LLM's values/data/llm_interviews/intrinsic/interview_raw/
  约 4.5M，baseline/intrinsic raw 回答。要重做 baseline 解析时发。

/Users/yxy/code/LLM's values/data/llm_pca/intrinsic/llm_pca_results.pkl
  约 32M，完整 baseline PCA 中间对象。GitHub 包已移走；需要深度 debug PCA 时发。

/Users/yxy/code/LLM's values/data/llm_pca/multilingual/roleplay_ml_pca_results_latest.pkl
  约 47M，完整 roleplay PCA 中间对象。GitHub 包已移走；需要深度 debug PCA 时发。
```

不用发：`.venv/`、`LLM's values.zip`、旧 PPT/图表、`Supplementary Materials/`、`dryad/`。这些不是师弟接手开发和复现主线的必要输入。

## WVS/EVS 官方数据让师弟官网下载

不要把官方原始 `.sav` 放进 GitHub。师弟如果要从头重建人类国家 PCA 基准，去 WVS 官网下载：

```text
Integrated_values_surveys_1981-2022.sav
https://www.worldvaluessurvey.org/
```

注意：`WVS Time Series 1981-2022` 只包含 WVS，不等于论文使用的
`WVS + EVS Integrated Values Survey`。不要仅重命名 WVS Time Series 文件后重建
正式 PCA。正式轻量基准应满足：

```text
data/country_values/country_scores_pca.json  -> 112 个国家/地区
data/country_values/pca_model_fixed.pkl      -> 固定 PPCA + Varimax 模型
```

新模型接入和可视化只需要上述两个正式轻量文件，不需要重新生成几 GB 的
`ivs_df.pkl`。只有确实需要完全重建 Stage0 时，才下载完整 Integrated Values
Survey，或向交接人索取原始 `ivs_df.pkl`。

下载后放到项目约定路径：

```text
data/raw/Integrated_values_surveys_1981-2022.sav
```

然后运行：

```bash
python3 src/run/run_country_values_analysis.py
```

## 后续模型怎么接

后续测旧模型、最新模型或多语言优化方法，都要接回同一条链：

```text
新模型回答 WVS/IVS 题
  -> 解析/adjudication 成 10 个题目的数值回答
  -> 用 data/country_values/pca_model_fixed.pkl 投影到固定 PCA 空间
  -> 和 data/country_values/country_scores_pca.json 的人类国家坐标算距离
  -> 进入 Study 1-4 / model imitation / 新优化实验比较
```

单模型六语言 smoke test：

```powershell
python src/run/run_llm_multilingual_analysis.py --models google/gemma-3-4b-it --languages en zh-cn fr es ru ar --consensus-count 1 --step all --skip-existing
```

这条命令只用于验证自动化流程。论文 Study 1 正式口径是 20 个模型、6 种语言、
每个模型-语言组合 5 次独立推理。正式模型、探索模型和 smoke-test 模型不能混入
同一份统计结果。

运行产生的 `data/llm_interviews/intrinsic/`、完整 PCA 中间对象和
`results/llm_values/` 图表默认不提交 GitHub；只提交代码、配置和经过确认的轻量
论文结果。

BLOOM/PolyLM 正式补测从这个入口跑：

```bash
python3 external_runners/hk_local_hf_interview_upload.py --help
```

优先跑的 alias：`bloomz_mt`、`polylm_chat_13b`。包里保留的 `bloom-1b7` 和 `polylm-1.7b` 旧 raw 只是 pilot/smoke test，不当正式结果。

## 正式样本边界

正式 Study 1-4 和 model imitation 使用 20-model paper sample。`qwen3-1.7b`、`glm-4.6`、`qwq-32b` 是后续探索模型，数据可以保留给扩展分析，但 `src/run/run_paper_analysis.py` 已把它们排除在正式统计外。
