<!--
  Contribute a GPU undervolt result to this open dataset.
  You are adding ONE object to the "results" array in data/undervolt_results.json.
  git is the moderation queue: a maintainer reviews every PR. An automated outlier check
  (scripts/undervolt_outlier_flag.py) runs on your PR; implausible or unsourced rows are
  flagged and held out of the on-site table until a human confirms them.
-->

## Undervolt result submission

**Card:** <!-- e.g. RTX 4070 Ti Super / RX 9070 XT -->
**Your setting in one line:** <!-- e.g. "900 mV @ 2650 MHz" (NVIDIA) or "-90 mV offset, -10% power limit" (AMD) -->

### The row I added to `data/undervolt_results.json`

```json
{
  "id": "rtx-4070-ti-super-900mv-2650mhz",
  "gpu": "RTX 4070 Ti Super",
  "vendor": "NVIDIA",
  "board": "",
  "tbp_watts": 285,
  "method": "MSI Afterburner V/F curve",
  "setting": "900 mV @ 2650 MHz",
  "voltage_mv": 900,
  "offset_mv": null,
  "clock_mhz": 2650,
  "power_limit_pct": null,
  "power_saved_w": 45,
  "temp_drop_c": 7,
  "fps_delta_pct": 0,
  "stability_hours": 6,
  "stock_result": "285 W, 74 C, 92 FPS average; Cyberpunk 2077 1440p RT Ultra, 30-minute loop",
  "tuned_result": "240 W, 67 C, 92 FPS average in the same loop",
  "test_method": "My own card. 6 h across Cyberpunk 2077 + Superposition loop, no crashes/artifacts",
  "source_type": "community-submitted",
  "source_url": "https://your-source-or-screenshot",
  "source_url_2": "",
  "source_publisher": "where the source is published, e.g. your Imgur album or forum",
  "source_author": "your-handle",
  "source_title": "title of the source page or post",
  "source_date": "2026-10-01",
  "source_quote": "a short verbatim line from the source with the result",
  "source_read": "2026-10-01",
  "submitter": "your-handle",
  "date": "2026-10-01",
  "flagged": false,
  "flag_reason": ""
}
```

### Field guide
- **method / setting** — NVIDIA: the MSI Afterburner V/F-curve target (`voltage_mv` @ `clock_mhz`). AMD RDNA4: a negative `offset_mv` (+ `power_limit_pct` as a delta, e.g. `-10`). AMD RDNA3: the Adrenalin absolute `voltage_mv` max.
- **Results** — `stock_result` and `tuned_result` carry the stock and tuned figures from the same workload. Fill the numeric fields only from those: `power_saved_w` (stock minus tuned), `temp_drop_c`, `fps_delta_pct` (+gain / 0 parity / -loss). Leave a field `null` if you did not measure it. **Do not guess.** A setting nobody measured is not a row.
- **Methodology** — `stability_hours` and `test_method`: how long, in what (a real demanding game and/or a loop that holds the card at the locked clock — FurMark does not validate an NVIDIA curve undervolt).
- **source fields** — `source_publisher`, `source_author`, `source_title`, `source_date` and a short verbatim `source_quote` from the page or post the numbers come from.
- **source_url** — REQUIRED. Every numeric value must trace to something resolvable: a review, a forum/Reddit thread, or your own screenshot/log. Rows without a real source are flagged.

### Checklist
- [ ] I added exactly **one** object to the `results` array (valid JSON — no trailing comma).
- [ ] `id` is unique and descriptive (`gpu-board-setting`).
- [ ] Every number I filled in is real and measured; unmeasured fields are `null`.
- [ ] `source_url` points to a resolvable source (or my own evidence).
- [ ] I set `flagged: false` and left `flag_reason` empty (the maintainer/script owns those).
- [ ] `python scripts/undervolt_outlier_flag.py --check` passes locally (optional but appreciated).
