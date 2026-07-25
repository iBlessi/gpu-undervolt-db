# GPU Undervolt Results — an open, crowdsourced dataset

Real GPU undervolt settings and the results people actually measured: voltage or offset, power
saved, temperature drop, FPS change, and how long it was tested. One row per tested configuration.

The dataset is rendered as a browsable table here:
**<https://techfuelhq.com/articles/gpu-undervolt-settings-database/>**

Published guides tell you the *method*. This tells you where other people's cards actually landed.

---

## Status: v1, seeded

This is version 1. The dataset currently holds **8 rows**, all seeded by TechFuelHQ to give the
table something real to stand on:

| Source type | Rows | What it means |
|---|---|---|
| `editorial-firstparty` | 1 | Measured by TechFuelHQ on our own hardware |
| `review-measured` | 1 | Taken from a published review's measurements |
| `community-verified` | 2 | A specific, sourced community result |
| `community-consensus` | 4 | The settings a card's community has converged on |

Cards covered so far: RTX 5090, RTX 5080, RTX 4090, RTX 4080 Super, RTX 5070 Ti (NVIDIA) and
RX 9070 XT, RX 9070, RX 7900 XTX (AMD).

**No third-party pull requests have been merged yet** — that is what this repo is for. Every row,
seeded or submitted, carries a `source_url`.

---

## How to contribute

1. Fork this repo.
2. Add **one** object to the `results` array in [`data/undervolt_results.json`](data/undervolt_results.json).
3. Open a pull request. The submission template fills in automatically — complete the field guide
   and checklist in it.

That is the whole process. **git is the moderation queue**: there is no backend, no account, and no
form. A maintainer reviews every PR, and an automated check runs on each one.

### What the automated check does

[`scripts/undervolt_outlier_flag.py`](scripts/undervolt_outlier_flag.py) runs on every PR that
touches the dataset ([workflow](.github/workflows/undervolt-check.yml)). It **blocks** on hard
problems — malformed schema, impossible values, a missing source — and **warns** on statistical
outliers. A warned row can still merge; it is marked `flagged` and held out of the on-site table
until a maintainer confirms it.

Run it yourself before opening the PR:

```bash
python scripts/undervolt_outlier_flag.py --self-test   # proves the checker works
python scripts/undervolt_outlier_flag.py --check       # validates the dataset
```

### The rules that get a row rejected

- **A number you did not measure.** Leave it `null`. Do not estimate, and do not copy a number from
  a review and present it as your own result.
- **No resolvable source.** `source_url` is required — a review, a forum or Reddit thread, or your
  own screenshot or log.
- **An untested "stable" claim.** Say how long you tested and in what. FurMark does not validate an
  NVIDIA curve undervolt; it needs a real load that holds the card at the locked clock.
- Setting `flagged` or `flag_reason` yourself. Those belong to the maintainer and the script.

---

## Schema

Top level is an object with two keys: `meta` (dataset metadata, including a field dictionary) and
`results` (the array of rows). Each row:

| Field | Type | Notes |
|---|---|---|
| `id` | string | Unique slug, `gpu-board-setting` |
| `gpu` | string | Canonical model, e.g. `RTX 5080`, `RX 9070 XT` |
| `vendor` | string | `NVIDIA` or `AMD` |
| `board` | string | AIB/board variant, or `""` if generic/consensus |
| `tbp_watts` | number | Stock total board power, watts |
| `method` | string | MSI Afterburner V/F curve (NVIDIA), or Adrenalin offset / max voltage (AMD) |
| `setting` | string | Human-readable summary of what was applied |
| `voltage_mv` | number\|null | NVIDIA curve target, or AMD RDNA3 absolute max voltage |
| `offset_mv` | number\|null | AMD negative voltage offset (RDNA4) |
| `clock_mhz` | number\|null | Target/held core clock |
| `power_limit_pct` | number\|null | Percent of stock (NVIDIA, e.g. `90`) or delta (AMD, e.g. `-10`); `null` if untouched |
| `power_saved_w` | number\|null | Measured reduction in board power |
| `temp_drop_c` | number\|null | Measured hotspot/junction drop, °C |
| `fps_delta_pct` | number\|null | `+` gain, `0` parity, `-` loss |
| `stability_hours` | number\|null | How long it was tested |
| `test_method` | string | What it was tested in |
| `source_type` | string | `editorial-firstparty`, `review-measured`, `community-verified`, `community-consensus`, or `community-submitted` |
| `source_url` | string | **Required.** Resolvable source for the numbers |
| `source_url_2` | string | Optional second source |
| `submitter` | string | Who submitted it |
| `date` | string | `YYYY-MM-DD` |
| `flagged` | boolean | Maintainer/script owned — leave `false` |
| `flag_reason` | string | Maintainer/script owned — leave `""` |

`meta.fields` in the JSON carries the same dictionary, so the file documents itself.

---

## License and attribution

The dataset is licensed **[CC BY 4.0](LICENSE)** (Creative Commons Attribution 4.0 International).
Use it, remix it, publish it commercially — just credit it:

> TechFuelHQ Community GPU Undervolt Results (CC BY 4.0).
> <https://techfuelhq.com/articles/gpu-undervolt-settings-database/>

Contributions are accepted under the same license.

The scripts and workflow in this repo exist to keep the data honest, and are provided as-is.
