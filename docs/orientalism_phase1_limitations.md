# Phase 1 technical pilot limitations

Phase 1 is a technical pilot and smoke test. It demonstrated that the repository can call an OpenAI-compatible endpoint, generate one English and one Chinese response, append JSONL records, redact API keys, and resume without repeating successful tasks.

It must not be used to draw conclusions about value differences or AI Orientalism.

## Methodological limitations

- Phase 1 contains only one family-responsibility scenario, so it cannot represent a value domain or support comparisons across domains and conflicts.
- The original scenario may not balance family responsibility and individual development sufficiently.
- The original prompt implementation hardcoded China in the role instruction instead of injecting country as an experiment condition.
- Legacy Phase 1 results contain a combined `prompt_text`, but do not separately preserve the exact `system_prompt`, `user_prompt`, role-tagged `messages`, or `prompt_template_version`.
- The legacy task key does not include scenario or prompt-template versions. Reusing the same output file after changing prompts could therefore skip an obsolete successful task.
- A provider may reject `seed`; the legacy result schema did not distinguish the requested seed from the seed actually used after fallback.
- The two real responses from `openai/gpt-4.1-mini` only demonstrate API connectivity and cannot establish language-conditioned value differences.

## Use of legacy artifacts

The existing Phase 1 scenario, configs, and results are retained for provenance and backward-compatibility testing. They must not be overwritten or silently upgraded to the new record schema.

New technical smoke tests should use a new output directory and preferably use an appropriately reviewed Phase 2A scenario such as `SOC_FAMILY_01`. Formal experiments must wait until the Phase 2A scenarios have completed final human review.

## Current safety boundary

- `smoke` uses an offline mock client and does not incur API charges.
- `generate` requires an explicit config and `--confirm-real-api`.
- New records use `orientalism_raw_v2` and preserve role-separated prompt snapshots and seed provenance.
- Phase 1 raw results remain legacy records and are intentionally unchanged.
