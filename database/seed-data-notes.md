# Seed data notes

Seed files live in `data/` and are produced by:

```bash
python src/data_generation/generate_sample_data.py
```

| File | Rows | Role |
| --- | --- | --- |
| `data/customers.csv` | 10,010 | Customer dimension extract |
| `data/orders.csv` | 100,020 | Fact extract |
| `data/products.csv` | 500 | Product dimension extract |

These are **synthetic**. They include blank emails, duplicate keys, null FKs, and orphan FKs as specified in `src/data_generation/DATA_GENERATION_NOTES.md`.

Do not replace them with production extracts. If you regenerate, keep seed `42` so tests stay valid.
