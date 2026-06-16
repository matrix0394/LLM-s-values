# Colab Smoke Test For Hong Kong

This folder contains a minimal Hugging Face smoke test for the Hong Kong
language-condition comparison.

## What it does

The script [hk_hf_smoke_test.py](/Users/yxy/code/LLM's values/analysis/colab/hk_hf_smoke_test.py):

- tests `BLOOM-zh`, `BLOOMZ`, and `PolyLM`
- uses the project's Hong Kong `en`, `zh-hk`, and `zh-cn` prompt setup
- runs the 10 IVS questions used in the paper
- saves raw outputs and a simple validity summary to CSV

## Recommended first Colab run

1. Open [Google Colab](https://colab.google/).
2. Switch runtime to `GPU`.
3. Install packages:

```python
!pip -q install -U transformers accelerate sentencepiece safetensors huggingface_hub "pandas==2.2.2"
```

4. Upload the local file [hk_hf_smoke_test.py](/Users/yxy/code/LLM's values/analysis/colab/hk_hf_smoke_test.py) to Colab.

You can use:

```python
from google.colab import files
files.upload()
```

The script contains fallback prompts and questions, so it can run even without
the full repo.

5. Optional but recommended: mount Google Drive before running so CSV files are
saved outside the runtime.

```python
from google.colab import drive
drive.mount('/content/drive')
```

6. Run a single model first:

```python
!python analysis/colab/hk_hf_smoke_test.py \
  --models bloom_zh \
  --languages en zh-hk zh-cn \
  --output-dir "/content/drive/MyDrive/hk_smoke_test/bloom_zh"
```

7. After that works, run all three:

```python
!python analysis/colab/hk_hf_smoke_test.py \
  --models bloom_zh bloomz polylm \
  --languages en zh-hk zh-cn \
  --output-dir "/content/drive/MyDrive/hk_smoke_test/all_models"
```

If you uploaded the script directly into `/content`, use:

```python
!python /content/hk_hf_smoke_test.py \
  --models bloom_zh \
  --languages en zh-hk zh-cn \
  --output-dir "/content/drive/MyDrive/hk_smoke_test/bloom_zh"
```

## Output files

- `hk_smoke_test_raw.csv`
- `hk_smoke_test_summary.csv`

The summary file gives:

- `question_count`
- `valid_count`
- `valid_rate`

This is enough for a first-pass check of:

- whether each model loads
- whether `zh-hk` outputs stay numeric
- whether `zh-hk` behaves differently from `en` and `zh-cn`

## Notes

- `PolyLM` needs `trust_remote_code=True`; the script already handles that.
- Free Colab GPUs vary across sessions, so start with one model at a time.
- This is a smoke test, not the full paper pipeline.
