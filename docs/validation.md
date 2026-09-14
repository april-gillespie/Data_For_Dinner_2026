# Final publication validation

Publication date: September 13, 2026.

## Completed checks

- Reviewed all 27 rendered pages of the final presentation and used them for the active project summary, credits, source links, and reported values.
- Preserved all seven supplied files byte for byte. The [artifact manifest](artifact_manifest.json) records sizes, SHA-256 hashes, and Git blob hashes.
- Checked the four supporting Office files read-only. The statistics workbook has 10 worksheets and 215 formula cells with cached results. Independent formula evaluation matched those cached results; this was not native Excel recalculation or validation of the underlying statistical methods.
- Decoded both supplied QR images and the final slide QR codes. Their short links agree. Checked their redirect destinations for the GitHub repository and Tableau dashboard.
- Independently reviewed the authored summaries against the presentation. Documented source differences in [reconciliation notes](source_priority.md), including the differing Midwest values within slide 15.

## Repository checks

Run the standard-library verifier from the repository root with Python 3.9 or later:

```sh
python tools/verify_final_package.py
```

It checks original-file sizes and hashes, the archived file hashes, and final Markdown local file targets. It excludes historical Markdown from current-link checks because that content is preserved as a snapshot. External URLs and Markdown anchor fragments are not validated by the script.

Before remote publication, the packaging check uses `--staged` because the existing Git subtree is attached directly without downloading and reuploading historical binaries. The published tree is checked against the [archive manifest](archive_manifest.json), preserving all 54 historical files plus the prior main README.

## Remaining limitations

- The final video has not been supplied. Playback, audio, and duration await the final recording. See the [video home](../video/README.md).
- The supplied presentation and workbooks have not been rewritten to resolve inconsistencies. The presentation remains authoritative for the published narrative, with internal differences disclosed.
- Original data acquisition and all slide calculations were not rerun. Reported figures should be read with their slide labels and the documented definition and denominator limits.
- The Tableau destination was obtained from the supplied QR link. Live dashboard values were not audited or substituted for the final presentation.
- Repository visibility and sharing permissions are unchanged. Reviewers still need the access required by the repository settings.
