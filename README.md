# GPU Undervolt Settings and Attributed Results

GPU undervolt and power-limit results, one row per setting a source measured: the stock and tuned
figures, the source's author and publication date, and the passage the numbers come from. One row is
TechFuelHQ's own RTX 5080 stock baseline. Workloads differ between rows, so no row predicts another card.

The dataset is rendered as a browsable table here:
**<https://techfuelhq.com/articles/gpu-undervolt-settings-database/>**

The website serves the same file at <https://techfuelhq.com/data/undervolt_results.json>.

Read a row's `test_method` and its source before borrowing any setting.

---

## Status: nine rows; synchronized October 1, 2026

The dataset contains **9 rows** compiled by TechFuelHQ:

| Source type | Rows | What it means |
|---|---|---|
| `editorial-firstparty` | 1 | TechFuelHQ's own bench: the RTX 5080 stock baseline (ASUS ROG Astral OC, June 8 to 11, 2026) |
| `review-measured` | 4 | A publication's or reviewer's test: Der8auer's RX 9070 XT, Alva Jonathan's two RX 9070 tunes, Quasar Zone's RTX 4090 power limit |
| `community-verified` | 4 | An owner's report on their own card: RTX 5070 Ti, RX 9070 XT, RX 7900 XTX, RTX 4090 |

TechFuelHQ reproduced none of the external rows. Each row's `source_read` gives the date TechFuelHQ
last read its figures in the source, and `source_quote` the passage they come from.

`null` means the source gives no matched measurement; zero would mean a reported zero change.
`power_saved_w` is also `null` where the tune drew more power than stock, as the two RDNA 4
performance tunes did; their watts are in `stock_result` and `tuned_result`.

Cards covered: RTX 5080, RTX 5070 Ti, RTX 4090 (NVIDIA) and RX 9070 XT, RX 9070, RX 7900 XTX (AMD).

Every row carries a `source_url`. A `source_url` that starts with `/` is a path on
`https://techfuelhq.com`.

---

## How to contribute

1. Fork this repo.
2. Add **one** object to the `results` array in [`data/undervolt_results.json`](data/undervolt_results.json),
   with stock and tuned measurements from the same workload and a source.
3. Open a pull request. The submission template fills in automatically; complete the field guide
   and checklist in it.

Opening a pull request requires a GitHub account. Email contact@techfuelhq.com with the same
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

- **A setting nobody measured.** A recommended or "typical" setting is not a row.
- **An outcome without an attributable measurement.** Leave it `null`. Do not estimate. A value
  from a published report must name that source and workload; never present it as your own test.
- **No resolvable source.** `source_url` is required: a review, a forum or Reddit thread, or your
  own screenshot or log.
- **An untested "stable" claim.** Say how long you tested and in what. FurMark does not validate an
  NVIDIA curve undervolt; it needs a real load that holds the card at the locked clock.
- Setting `flagged` or `flag_reason` yourself. Those belong to the maintainer and the script.

---

## Schema

Top level is an object with two keys: `meta` (dataset metadata, including a field dictionary) and
`results` (the array of rows). `meta.schema_version` is 2. Each row:

| Field | Type | Notes |
|---|---|---|
| `id` | string | Unique slug, `gpu-board-setting` |
| `gpu` | string | Canonical model, e.g. `RTX 5080`, `RX 9070 XT` |
| `vendor` | string | `NVIDIA` or `AMD` |
| `board` | string | Board the source tested, or `""` if the source does not name it |
| `tbp_watts` | number\|null | Reference total board power for the card as tested; `null` for a partner board whose own rating the source does not state |
| `method` | string | MSI Afterburner V/F curve, AMD Adrenalin voltage offset or maximum voltage, or a power limit alone |
| `setting` | string | Settings as the source states them; not a stability guarantee |
| `voltage_mv` | number\|null | NVIDIA curve target, or AMD RDNA3 absolute max voltage |
| `offset_mv` | number\|null | AMD negative voltage offset (RDNA4) |
| `clock_mhz` | number\|null | Target/held core clock |
| `power_limit_pct` | number\|null | Percent of stock (NVIDIA, e.g. `90`) or delta (AMD, e.g. `-10`); `null` if untouched |
| `power_saved_w` | number\|null | Stock minus tuned board power in the stated workload; `null` without a matched pair or when the tune drew more |
| `temp_drop_c` | number\|null | Stock minus tuned temperature in the stated workload, °C |
| `fps_delta_pct` | number\|null | `+` gain, `0` parity, `-` loss; rounded from the source's stock and tuned figures where both are given |
| `stability_hours` | number\|null | Reported stable test duration; `null` means no duration established |
| `stock_result` | string | The stock figures the source measured, with the workload |
| `tuned_result` | string | The tuned figures the source measured in the same workload |
| `test_method` | string | Workload, whose card it was, and the limits of the measurement |
| `source_type` | string | `editorial-firstparty`, `review-measured`, `community-verified`, or `community-submitted` |
| `source_url` | string | **Required.** Where the figures were published |
| `source_url_2` | string | A second source for the same test, or `""` |
| `source_publisher` | string | Publication or forum that carries the source |
| `source_author` | string | Author, poster or tester the source names |
| `source_title` | string | Title of the source page or thread |
| `source_date` | string | `YYYY-MM-DD` the source was published or posted |
| `source_quote` | string | A short verbatim passage from the source |
| `source_read` | string | `YYYY-MM-DD` TechFuelHQ last read the source |
| `submitter` | string | Who compiled or submitted the row, with original attribution |
| `date` | string | `YYYY-MM-DD` the row was added or corrected; not the experiment date |
| `flagged` | boolean | Maintainer/script owned; leave `false` |
| `flag_reason` | string | Maintainer/script owned; leave `""` |

`meta.fields` in the JSON carries the same dictionary, so the file documents itself.

## Correction history

October 1, 2026: synchronized with the website's corrections of September 26 and 28;
`data/undervolt_results.json` is now the same file the website serves (schema version 2, nine rows).
Removed three settings that could not be traced to a measurement in their cited sources:
`rtx-4080-super-950mv-2760mhz`, `rtx-5090-900mv-2800mhz` and `rtx-4090-940mv-2700mhz`. Replaced the
RTX 5080 setting of 950 mV at 2,750 MHz (`rtx-5080-rog-astral-oc-950mv-2750mhz`) with TechFuelHQ's
RTX 5080 stock baseline from LK Wood IV's June 8 to 11, 2026 runs (`rtx-5080-rog-astral-oc-stock-baseline`).
Added `rtx-4090-60pct-power-limit` (Quasar Zone's 60% power limit as TechPowerUp reports it),
`rtx-4090-985mv-2800mhz` (Level1Techs forum), `rx-9070-xt-red-devil-neg170mv-110pt` (Der8auer, as
Tom's Hardware tabulates it) and `rx-9070-neg125mv-plus10pl-performance` (Alva Jonathan, as Tom's
Hardware and Club386 report it). Re-based `rx-7900-xtx-1100mv-max` on the Topaz forum report and
re-sourced `rx-9070-neg100mv-30pl-efficiency` to Club386 with Notebookcheck second. Every row now gives
the source's stock and tuned figures from one workload, its author and date, and a verbatim passage.
The contact address is now contact@techfuelhq.com.

September 8, 2026: removed outcome estimates from five setting rows and clarified the RTX 5070 Ti
benchmark and the RX 9070 loss. The README's former "eight tested configurations" framing and
"no account" contribution instruction were also corrected.

---

## License and attribution

The dataset is licensed **[CC BY 4.0](LICENSE)** (Creative Commons Attribution 4.0 International).
Use it, remix it, publish it commercially; just credit it:

> TechFuelHQ GPU Undervolt Settings and Attributed Results (CC BY 4.0).
> <https://techfuelhq.com/articles/gpu-undervolt-settings-database/>

Contributions are accepted under the same license.

The scripts and workflow in this repo exist to keep the data honest, and are provided as-is.
