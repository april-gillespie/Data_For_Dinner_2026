# Publication review

Review date: September 14, 2026.

## Video

- The supplied recording is 1920 x 1080 at 30 frames per second, with stereo AAC audio, and runs 00:07:48,045.
- A full decode of the supplied recording completed without errors. Audio measurement found a peak of -0.8 dBFS and a mean of -22.3 dBFS. Audio falls silent at approximately 00:06:39,234.
- The closing QR-code slide remains visible until 00:06:41,900. A black interval follows until 00:07:43,000, after which a silent future-work title card appears. The published copy ends after the closing QR slide.
- The published copy retains the presentation at 1080p and 30 frames per second. It uses H.264 at CRF 26 and AAC audio at 128 kb/s because the GitHub upload API rejected the larger copy. Fast-start metadata supports progressive playback.
- A full decode of the published copy completed without errors, with 12,057 video frames. No black interval lasting at least one second was detected. Its measured audio peak is -0.8 dBFS, with a mean of -21.7 dBFS.
- Representative frames across the presentation and the closing sequence were visually reviewed. The supplied original was not modified, and its hash from source inspection is included in the [artifact manifest](artifact_manifest.json).
- Original SRT captions and a mechanical transcript accompany the video. The 106 caption blocks have sequential numbers, positive durations, and no overlaps. The caption endpoint is 00:06:38,500. Word-by-word audio alignment and caption corrections were not performed.

## Repository and supporting files

- The current presentation has 27 pages and retains its original SHA-256 hash.
- The research workbook ZIP package passes its integrity check. Its 215 formula cells contain no cached Excel error values. The workbook retains its original SHA-256 hash. This was a read-only check, not a fresh Excel recalculation or a rerun of source acquisition.
- The front page links to the video, captions, transcript, presentation, research workbook, and dashboard. Local file targets and HTML image targets are checked by the repository verifier.
- The Tableau link opened the public dashboard titled Data for Dinner Team | WiD Datathon 2026 by Toni Randell. Dashboard values were not substituted for the final slide figures.
- The supplied presentation and workbook are preserved unchanged. Clear wording issues are qualified in the README and documented below.

## Data and presentation notes

| Location | Finding and treatment |
| --- | --- |
| Slide 12, global charts | The charts show percentages. They do not establish a ranking by number of affected people. The README now describes the displayed percentages and retains the slide category labels. The precise indicator definition and observation period should accompany reuse of these figures. |
| Slide 15, Midwest | Body text says 12.3%, while the map legend says 12.2%. The public Tableau dashboard displays 12.1% at this review. These differences are disclosed. |
| Research workbook, US Regions G5 and H5 | The Midwest text lists 12 states, but its formula includes 15 values, also using Maryland, Virginia, and West Virginia. This needs reconciliation before treating the presentation value as a validated regional estimate. |
| Slide 17 and research workbook, US B59 | The workbook formula is `AVERAGE(B2:B52)`, with a cached value of 0.12858823529411764. Rounded to one decimal percentage point, this is 12.9%. It is an unweighted mean of 50 states plus the District of Columbia. The README identifies this basis. |
| Research workbook, Southeast A6 | Supporting prose says Alabama at 12.1% and North Carolina at 11.8% exceed 12.9%. Both are numerically below 12.9%. This sentence is not repeated in the README. |
| Slides 19 and 20, Alabama | Low income, low access, and food insecurity describe different measures. The README preserves the Low-Income Low-Access county label and does not describe that ranking as a food insecurity rate. |
| Slide 22, proposed solutions | The suggestions were not evaluated through an implementation study. The README identifies them as proposed actions. |
| Slide 24, future work | Allergy impacts remain a research direction. A completed allergy-impact analysis is not claimed. |

This sweep checks publication usability and documents the observed source differences. It does not certify every slide calculation or estimate causal effects. The original slides, workbook, captions, and recorded wording remain source material, including their unresolved differences.

## Reproduce the file checks

From the repository root, use Python 3.9 or later:

```sh
python tools/verify_publication.py
```

The verifier checks the manifest hashes, MP4 structure, caption sequence and duration bounds, transcript extraction, and local Markdown and HTML image paths. It does not fetch external links or validate every caption word against audio.
