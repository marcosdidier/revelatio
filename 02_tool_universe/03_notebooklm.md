# Dossier — NotebookLM

> Brief-listed tool · Will test **briefly** in **Epic 5.7** to demonstrate the misfit (1 screenshot is stronger evidence than prose).

## What it is
Google's research assistant over user-uploaded documents (Workspace product). Lets you upload sources, then ask questions, generate summaries, and get answers grounded in the corpus with citations. Now also generates audio overviews ("podcast" mode) and can produce study guides.

## Where it fits in our pipeline
- **Extractor candidate**: ❌ wrong layer. NotebookLM is designed for *conversational research over content*, not bulk structured extraction. There's no "give me a JSON for every doc in this folder" mode. Asking it for structured output works for 1 doc but doesn't scale.
- **Orchestrator**: no.
- **Downstream consumer**: ✅ **excellent fit here**. Once the spreadsheet exists, the legal team can upload it as a Notebook source and ask Portuguese-language questions: *"Quais devedores estão em negociação há mais de 90 dias?"*, *"Liste os 10 maiores saldos atualizados"*. Strong UX for non-technical lawyers.

## Hands-on plan (Epic 5.7)
- Upload `exemplo_pdf_cliente_devedor_ficticio.pdf` as a source.
- Prompt: *"Extract the following fields as a table with one row per source: nome, CPF, ..."*
- Capture screenshot of the response. Likely conversational, not strictly structured. The screenshot is the evidence.
- Then upload a hypothetical resulting spreadsheet (or a small CSV) and demonstrate downstream Q&A — that's the **positive** half of the verdict.

## LGPD / data-residency
- Workspace Business / Enterprise: data not used for training; Google's standard data protection controls. Brazil-region availability via Google Cloud regions.
- Workspace Education / personal: less strict — would not recommend for debtor data.

## Cost class
- Free with Google account (rate-limited)
- Workspace seat already covered if firm has Google Workspace
- 💲 (existing seat) — effectively free at the margin if the firm is already on Workspace

## Fit verdict
**❌ for the extraction job** (wrong tool category). **✅ as a post-extraction layer** to give the legal team a Q&A interface over the resulting spreadsheet. We propose it in the architecture as *"NotebookLM as the corpus search/Q&A companion after the pipeline writes the spreadsheet"* — turning a "doesn't fit" into a "fits somewhere else useful."

## Risks specific to this tool
- Mentioning it without explaining the mismatch would look like we ran the wrong test. The 1-screenshot demonstration in 5.7 + the downstream-consumer pivot is the cleanest way to handle this.
- Google has shipped frequent UX changes to NotebookLM; describe our test with a date stamp.
