# DEPLOY.md — Revelatio demo no Streamlit Community Cloud

Este runbook cobre apenas o que **só um humano pode fazer**: criar projeto Google Cloud, baixar a chave JSON da service account, criar a planilha, fazer push do repositório e configurar o app no Streamlit Cloud. Toda a parte de código já está pronta — `06_reference_script/app.py`, `06_reference_script/sheets_writer.py` e `requirements.txt` na raiz.

**Pré-requisitos:**
- Conta Google (qualquer Gmail funciona) — para Google Cloud e Google Sheets.
- Conta GitHub `marcosdidier` (já existente).
- `gh` CLI autenticado localmente (`gh auth status` deve retornar OK). Se não estiver, rode `gh auth login`.
- `git status` limpo o suficiente para um commit final do Epic 8.5.

**Tempo total estimado:** ~30 minutos somando os 5 blocos, mais ~10 minutos de buffer para o típico round-trip de permissão da service account.

---

## Bloco 1 — Google Cloud + service account (~10 min)

1. Abra `https://console.cloud.google.com`.
2. Barra superior → seletor de projeto → **Novo projeto** → nome `revelatio-demo` → **Criar**. Aguarde o projeto ficar selecionado.
3. Barra de busca do topo → digite `Google Sheets API` → clique no resultado → **Ativar**.
4. Menu lateral → **IAM e administrador** → **Contas de serviço** → **Criar conta de serviço**.
   - Nome: `revelatio-demo` (o ID é preenchido automaticamente).
   - **Criar e continuar**.
   - Função (etapa 2 opcional): pode pular — a permissão será concedida via compartilhamento da planilha (princípio do menor privilégio). Clique **Continuar** → **Concluído**.
5. Na lista de contas de serviço, clique no email recém-criado (algo como `revelatio-demo@revelatio-demo-XXXXXX.iam.gserviceaccount.com`).
6. Aba **Chaves** → **Adicionar chave** → **Criar nova chave** → **JSON** → **Criar**. O download da chave começa automaticamente. **Esta chave concede acesso de escrita à planilha — trate como segredo, não comite.**
7. **Anote** o email da service account (você vai colar no Bloco 2) e **mova** o arquivo JSON para fora do diretório do repositório (ex.: `~/Downloads/`).

**Resultado esperado:** um arquivo `*.json` na sua pasta de Downloads e um email de service account anotado.

---

## Bloco 2 — Planilha Google + compartilhamento (~2 min)

1. Abra `https://drive.google.com` → **Novo** → **Planilhas Google** → **Planilha em branco**.
2. Renomeie a planilha para `Revelatio — Dossiês extraídos` (canto superior esquerdo, clique no nome).
3. (Opcional) Renomeie a aba `Página1` para `Dossiers`. Se não renomear, o writer cria automaticamente uma aba `Dossiers` na primeira escrita.
4. Botão **Compartilhar** (canto superior direito) → cole o email da service account (Bloco 1, passo 7) → permissão **Editor** → **Notificar pessoas** **desmarcado** → **Compartilhar**.
5. Na URL da planilha (`https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`), **copie o `<SHEET_ID>`** — é a string longa entre `/d/` e `/edit`.

**Resultado esperado:** planilha criada, compartilhada com a service account como Editor, `SHEET_ID` copiado.

---

## Bloco 3 — Push do repositório para GitHub (~5 min)

A partir do diretório do projeto (`/Users/marcosdidier/testeRevelatio/`):

1. **Sanity-check pré-push** — confirme que nenhum segredo está rastreado:
   ```bash
   git status
   git ls-files | grep -E "\.env$|service.*\.json|credentials\.json" && echo "ALERTA — segredo rastreado" || echo "OK — nenhum segredo rastreado"
   ```
   O segundo comando deve imprimir `OK`. Se imprimir `ALERTA`, **pare** e remova o arquivo do índice antes de continuar.
2. Comite o trabalho do Epic 8.5:
   ```bash
   git add 06_reference_script/app.py 06_reference_script/sheets_writer.py \
           requirements.txt .env.example .gitignore DEPLOY.md
   git commit -m "Epic 8.5: Streamlit Cloud deploy + Google Sheets write-back"
   ```
3. Crie o repositório público e faça o push:
   ```bash
   gh repo create marcosdidier/revelatio --public --source=. --remote=origin --push
   ```
   Alternativa via UI: crie em `github.com/new` (nome `revelatio`, público), depois `git remote add origin https://github.com/marcosdidier/revelatio.git && git push -u origin main`.

**Resultado esperado:** o repositório aparece em `https://github.com/marcosdidier/revelatio` com todos os commits do projeto.

---

## Bloco 4 — Deploy no Streamlit Community Cloud (~5 min)

1. Abra `https://share.streamlit.io` → **Sign in with GitHub** (autorize o app se for o primeiro acesso).
2. Botão **New app** (canto superior direito) → tipo **From existing repo**.
3. Preencha:
   - **Repository**: `marcosdidier/revelatio`
   - **Branch**: `main`
   - **Main file path**: `06_reference_script/app.py`
   - **App URL** (opcional): `revelatio-demo` → resultado: `https://revelatio-demo.streamlit.app`
4. Expanda **Advanced settings** → **Secrets** → cole o TOML abaixo, substituindo cada `...` pelos valores reais:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   AZURE_DI_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
   AZURE_DI_KEY = "..."
   GOOGLE_SHEET_ID = "..."
   GOOGLE_SERVICE_ACCOUNT_JSON = """
   {
     "type": "service_account",
     "project_id": "revelatio-demo-XXXXXX",
     ...
   }
   """
   ```
   **Atenção ao formato do JSON**: cole o conteúdo *inteiro* do arquivo `.json` do Bloco 1 entre as três aspas duplas. Mantenha as quebras de linha originais — o TOML aceita strings multilinha entre `"""..."""`.
5. **Save** os secrets → **Deploy**. O build leva 1–3 minutos (instalação de `requirements.txt`).

**Resultado esperado:** a URL do app responde com o título "Revelatio — Extração de Dossiês". Logs do Streamlit Cloud (ícone "Manage app" → "Logs") não devem mostrar `ModuleNotFoundError` nem `KeyError`.

---

## Bloco 5 — Smoke test end-to-end (~5 min)

1. Abra a URL pública do app no navegador.
2. Arraste `05_synthetic_data/pdfs/F09_brief_shape.pdf` para o uploader (use Drive/AirDrop/SCP para enviar do laptop se necessário — o app espera o arquivo via upload de browser).
3. Clique **▶ Extrair 1 dossiê(s)**. Aguarde ~30–60 segundos (latência típica do pipeline).
4. **Verifique no resultado**: a linha exibida deve ter `client_name`, `cpf`, todos os campos da página 2 preenchidos, e `needs_review = FALSE`.
5. Clique **📤 Enviar para Planilha Google**. Aguarde a mensagem `1 linha(s) enviada(s) com sucesso.` + link `[Abrir planilha]`.
6. Abra a planilha pelo link. A primeira linha é o cabeçalho (`pdf_filename, client_name, ...., extracted_at`). A segunda linha contém os dados extraídos, com `extracted_at` em ISO-8601 UTC.

**Resultado esperado:** todos os 6 passos sem erro. A planilha agora tem uma linha de dados de teste.

---

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `ModuleNotFoundError: gspread` nos logs do Streamlit | `requirements.txt` não está na raiz, ou commit não foi pushed | Confirme `git ls-files \| grep requirements.txt` e re-push se necessário. |
| `Planilha <id> não encontrada` no app | Sheet ID errado **ou** sheet não compartilhada com a service account | Reveja Bloco 2 passo 4. O email da service account precisa estar em "Pessoas com acesso" da planilha como Editor. |
| `JSON da service account inválido` | `GOOGLE_SERVICE_ACCOUNT_JSON` truncado nos secrets do Streamlit (faltou uma chave `}`) | Re-cole o conteúdo do JSON original entre `"""..."""`. |
| App carrega mas botão "📤 Enviar" está desabilitado | `GOOGLE_SHEET_ID` ausente nos secrets | Adicione a chave nos secrets do Streamlit Cloud → app reinicia automaticamente. |
| Build falha com `azure-ai-documentintelligence` | versão removida do PyPI (raro) | Atualize `requirements.txt` para uma versão `>=1.0,<2` e re-push. |
| Smoke test passa mas planilha não recebe linha | `GOOGLE_SHEET_ID` aponta para outra planilha | Confirme que o ID nos secrets bate com o ID da URL da planilha compartilhada. |

---

## Após o smoke test passar

Os documentos do Epic 7 e o relatório PT-BR só são atualizados **depois** que o gate do Bloco 5 passa em produção. A lista de arquivos a atualizar está em `08_5_kickoff_prompt.md` na seção "After Epic 8.5 ships". É um batch pequeno (~15 min): adicionar a URL viva no `SESSION_RESUME.md`, atualizar `§5` do relatório, anexar a URL ao roteiro do vídeo (Epic 9) e simplificar a caveat "CLI usado no PoC" no diagrama 2.

Se algum bloco falhar e não for resolvível em tempo hábil, o enquadramento atual do relatório ("construímos o motor; n8n é uma opção entre várias") permanece intacto e é a posição metodologicamente limpa de fallback. Não retro-atribua sucesso de deploy ao Epic 8.
