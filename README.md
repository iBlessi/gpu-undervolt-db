# GPU Undervolt Settings and Reported Results

An open dataset of community setting references and attributed external reports. Each row
identifies its source and evidence category. A setting reference is not a completed experiment.

The dataset is rendered as a browsable table here:
**<https://techfuelhq.com/articles/gpu-undervolt-settings-database/>**

Use the method notes to understand what a source reports before borrowing any settings.

---

## Status: eight entries; corrected September 8, 2026

The dataset contains **8 rows** compiled by TechFuelHQ:

| Source type | Rows | What it means |
|---|---|---|
| `editorial-firstparty` | 0 | No logged TechFuelHQ before/after test is present |
| `review-measured` | 1 | Alva Jonathan's RX 9070 result as reported by Notebookcheck |
| `community-verified` | 2 | Attributed XDA and Esports Tales reports; not independently reproduced here |
| `community-consensus` | 5 | Setting references with unestablished outcome fields set to `null` |

The category names are retained for schema compatibility. In this dataset, “verified” in a
category name does not mean that TechFuelHQ reproduced the test. Read each row's method and source.

`null` means no configuration-specific outcome is established; zero would mean a reported zero
change. The RTX 5070 Ti's 50 W saving belongs to the source's Steel Nomad test. The RX 9070's
rounded -7% records a loss. Different workloads make these reports unsuitable for claiming a
typical saving or guaranteed stability across cards.

Cards covered so far: RTX 5090, RTX 5080, RTX 4090, RTX 4080 Super, RTX 5070 Ti (NVIDIA) and
RX 9070 XT, RX 9070, RX 7900 XTX (AMD).

Every row carries a `source_url`. Contributions should add a traceable stock-versus-tuned report,
with unmeasured fields left null.

---

## How to contribute

1. Fork this repo.
2. Add **one** object to the `results` array in [`data/undervolt_results.json`](data/undervolt_results.json).
3. Open a pull request. The submission template fills in automatically — complete the field guide
   and checklist in it.

Opening a pull request requires a GitHub account. Email hello@techfuelhq.com with the same
information if you prefer not to use GitHub. Maintainers review submissions through pull requests.

### What the automated check does

[`scripts/undervolt_outlier_flag.py`](scripts/undervolt_outlier_flag.py) runs on pull requests
touching the dataset or checker ([workflow](.github/workflows/undervolt-check.yml)). It checks
schema, numeric bounds and required source fields, and warns about statistical outliers.
These checks cannot establish that an experiment happened, authenticate a measurement, or prove
stability. The site table excludes rows marked `flagged`; maintainers must review the evidence.

Run it yourself before opening the PR:

```bash
python scripts/undervolt_outlier_flag.py --self-test   # proves the checker works
python scripts/undervolt_outlier_flag.py --check       # validates the dataset
```

### The rules that get a row rejected

- **An outcome without an attributable measurement.** Leave it `null`. Do not estimate. A value
  from a published report must name that source and workload; never present it as your own test.
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
| `test_method` | string | Workload, attribution and limits; reference instructions for untested rows |
| `source_type` | string | `editorial-firstparty`, `review-measured`, `community-verified`, `community-consensus`, or `community-submitted` |
| `source_url` | string | **Required.** Source for the setting reference or reported outcome |
| `source_url_2` | string | Optional second source |
| `submitter` | string | Who submitted it |
| `date` | string | `YYYY-MM-DD` added/corrected date, not necessarily a test date |
| `flagged` | boolean | Maintainer/script owned — leave `false` |
| `flag_reason` | string | Maintainer/script owned — leave `""` |

`meta.fields` in the JSON carries the same dictionary, so the file documents itself.

## Correction history

September 8, 2026: removed outcome estimates from five consensus references and synchronized
the public download with the website. The original public RTX 5080 row incorrectly claimed
first-party provenance; a July local correction had not reached the public repository. No
first-party before/after result is established for that row. The README's former “eight tested
configurations” framing and “no account” contribution instruction were also corrected.

---

## License and attribution

The dataset is licensed **[CC BY 4.0](LICENSE)** (Creative Commons Attribution 4.0 International).
Use it, remix it, publish it commercially — just credit it:

> TechFuelHQ Community GPU Undervolt Results (CC BY 4.0).
> <https://techfuelhq.com/articles/gpu-undervolt-settings-database/>

Contributions are accepted under the same license.

The scripts and workflow in this repo exist to keep the data honest, and are provided as-is.
