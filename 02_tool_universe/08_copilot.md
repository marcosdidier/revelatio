# Dossier — Microsoft Copilot

> Brief-listed tool · **Not testing hands-on** (per user direction — different layer than the extractor; we build the case analytically).

## What it is
Microsoft's chat-mode AI assistant, exposed in three forms relevant here:

1. **Copilot for M365** — embedded inside Word, Excel, Outlook, Teams. Acts on the user's M365 documents; respects sensitivity labels and tenant policies.
2. **Copilot Studio** — low-code platform for building custom copilots over org data (could surface debtor info from the resulting spreadsheet via natural language).
3. **copilot.microsoft.com** — standalone web chatbot (free + paid tiers). Not appropriate for debtor data.

Backed by the GPT-4o / GPT-5 family with Microsoft's commercial data protection and tenant-region controls.

## Where it fits in our pipeline

- **Extractor for the bulk job**: ❌ wrong tool. Copilot is interactive chat, not a programmatic batch extractor. There's no "process 10k PDFs and append rows" mode that's better than Power Automate + AI Builder doing exactly that.
- **Orchestrator**: ❌ Copilot Studio could in principle drive a flow, but Power Automate is the right product for that — Copilot Studio sits on top of Power Automate.
- **Downstream consumer of the resulting Excel**: ✅ ✅ — once the pipeline produces the spreadsheet, **Copilot in Excel** turns it into a natural-language analytics layer for the legal team. Examples:
  - *"Mostre os 50 maiores saldos com mais de 90 dias de atraso, agrupados por responsável interno."*
  - *"Quais devedores tiveram a última tentativa de contato há mais de 60 dias?"*
  - *"Crie um gráfico de barras dos 10 produtos com maior valor original em atraso."*

This positions Copilot as the **value-multiplier on top of the Power Automate pipeline** — the legal team gets natural-language access to the cleaned data without learning Excel pivots.

## Why we don't test hands-on
- Per user direction: justify, don't implement. Copilot's role is post-pipeline (consumer), not extraction — a hands-on test would mostly demonstrate that "yes, you can ask the spreadsheet questions in natural language", which is well-documented Microsoft functionality.
- The narrative position is what matters: Copilot complements Power Automate, it doesn't compete with it.

## LGPD / data-residency
- Copilot for M365: covered by M365 Commercial Data Protection; tenant region settings apply; Brazilian residency configurable; same posture as Power Automate (D-005).
- copilot.microsoft.com (consumer): **inappropriate for debtor data** — no enterprise data protection.
- **Posture rating: 4/5** when used as Copilot for M365 inside firm's tenant.

## Cost class
- Copilot for M365: ~$30/user/mo on top of M365 license
- Typically licensed for select power-users on the legal-ops team (5–10 seats), not everyone
- 💲💲

## Fit verdict
**❌ Not the extractor** for the 10k-batch problem. **✅ Recommended as a downstream consumer/analyst layer on top of the Power Automate pipeline output**, especially for non-technical lawyers who want to query the resulting spreadsheet conversationally.

## How it shows up in the relatório

In §5 ("Como essa ferramenta seria utilizada no fluxo da equipe"):
> *"O Copilot para M365 não compõe o fluxo de extração — esse papel é do Power Automate + AI Builder. Mas, uma vez que a planilha consolidada esteja em SharePoint/OneDrive, Copilot in Excel transforma esses dados em uma interface de consulta em linguagem natural para a equipe jurídica, sem necessidade de planilhas avançadas. Recomendamos seat licensing apenas para os usuários power do núcleo de cobrança."*

## Position in the comparison matrix
**Rank: not ranked as extractor; listed in "Downstream consumers" group with NotebookLM as alternatives within the same role.**
