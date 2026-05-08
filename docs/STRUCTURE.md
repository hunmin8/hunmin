# Hunmin Folder Structure

`hunmin_pkg` is the official package that is pushed to GitHub and Hugging Face.
`hunmin_v1` is the earlier research/experiment repository; useful pieces can be
promoted into `hunmin_pkg`, but new product code should not be added there.

## Official package

```text
hunmin_pkg/
  hunmin/
    api.py                 # public transcription API
    cli.py                 # `hunmin ...` CLI
    core/                  # language-specific transcription rules
      cjk.py               # Japanese/Chinese/Korean transcription
    entity.py              # phonetic entity resolver
    data/
      cmudict.dict
      entities/
        sample_entities.jsonl
  scripts/
    eval_heldout_1000.py
    wikidata_dump_to_entities.py
    phonetic_entity_cli.py
  tests/
  docs/
    STRUCTURE.md
```

## Experimental repository

```text
hunmin_v1/
  factory/                 # synthetic/search data factories
  scripts/                 # training/eval utilities
  configs/                 # model training configs
  eval/                    # heldout retrieval sets
  output/                  # generated artifacts
```

## Rule

- Transcription changes go to `hunmin_pkg/hunmin/core/`.
- Public API additions go to `hunmin_pkg/hunmin/`.
- Entity alias search belongs in `hunmin_pkg/hunmin/entity.py`.
- Model training, embedding experiments, and generated corpora stay in `hunmin_v1`.
- GitHub/Hugging Face release files should come from `hunmin_pkg`, not `hunmin_v1`.
