# NT6094 midterm (UTS) 2026-1 — Pradigta Hisyam Ramadhan (28726019)

Answer sheet for the 2026-1 midterm of **NT6094 Teknik Penulisan Jurnal Ilmiah** (lecturer: Sparisoma Viridi),
Nanotechnology Study Program, The Graduate School of Multidisciplinary Science and Technology, Institut Teknologi
Bandung. Assignment page: https://endap.github.io/26j76/ (seed 28726019 → datasets g40s1, g42s3, g44s3, g46s4,
g48s2, g50s3, g52s3, g54s4, g56s3, g58s1).

## Answer sheet

| File | Description |
|---|---|
| [`UTS-NT6094-PradigtaHR-28726019-JMS.pdf`](UTS-NT6094-PradigtaHR-28726019-JMS.pdf) | Manuscript in *Journal of Materials Science* submission format (with Online Resource 1) |
| [`UTS-NT6094-PradigtaHR-28726019.pdf`](UTS-NT6094-PradigtaHR-28726019.pdf) | Same work as a free-format report |
| `*.docx` | Word sources of both PDFs |

## AI chat

[`ai-chat/claude-code-chat-log.md`](ai-chat/claude-code-chat-log.md) — relevant export of the Claude Code
(Claude Opus 5.5, Anthropic) session used for this midterm: prompts, visible replies, clarifying answers, and
the list of actions per turn (hidden reasoning and raw tool output omitted).

## Contents

| Folder | Content |
|---|---|
| `data/results.json` | Extracted features per dataset: ids, peak, last point, *m*, *b*, *R*², *x*₀ |
| `figures/` | App screenshots (`app_*.png`), flowchart (`flowchart.mmd` / `.png`), charts |
| `scripts/` | Processing and document scripts (see below) |

The raw datasets are not copied here; they are published by the lecturer at the endap posts
26j34, 26j40, 26j44, 26j49, 26j51, 26j56, 26j60, 26j65, 26j68, 26j70.

## Reproduce

```sh
# 1. download the ten posts into web/ (e.g. curl -s https://endap.github.io/26j34/ -o web/26j34.html ...)
py scripts/extract.py web data/datasets.json     # parse raw data, app sampling step per page
py scripts/analyze.py data/datasets.json data/results.json   # peak, last, 25–75 % regression
py scripts/plot_results.py                         # charts for the free-format report
py scripts/plot_jms.py                             # charts for the JMS manuscript
py scripts/build_docx.py                           # free-format DOCX
py scripts/build_jms_docx.py                       # JMS-format DOCX
powershell -File scripts/to_pdf.ps1 -In <docx> -Out <pdf>   # PDF via Microsoft Word
```

Requires Python 3 with matplotlib, numpy, python-docx; the flowchart was rendered with
`@mermaid-js/mermaid-cli`.
