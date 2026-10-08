# Explainable EXIF Privacy Score

The score is a risk indicator, where a higher number means more recognized EXIF findings. It is not a probability or an independently calibrated cybersecurity metric.

`score = min(100, 50 * HIGH_count + 20 * MEDIUM_count + 5 * LOW_count)`

HIGH matches GPS-related names. MEDIUM matches make, model, artist, software, image unique ID and owner name. LOW matches timestamp, orientation and EXIF dimension names. Matching is case-insensitive and substring-based; HIGH wins over MEDIUM, which wins over LOW. Each key counts once in its winning tier. Related fields can accumulate independently and saturate the cap.

Example: GPSInfo + Make + Model + DateTime gives `min(100, 50 + 20 + 20 + 5) = 95`. The classifier's `high`, `medium`, `low` lists let a reader reconstruct the result. Unknown keys stay in details but do not contribute.

No EXIF gives zero for this heuristic. XMP, IPTC, visible personal information, PDF authorship and unrecognized camera tags can still expose private information. The UI shows an unassessed state for operations that do not calculate EXIF risk.

Before public release, inspect both the findings and the limits of inspection. Do not combine malware status and privacy score into one unsupported safety verdict.