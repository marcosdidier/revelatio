#!/usr/bin/env python3
"""Brief-shaped OOD test PDF generator for Project Revelatio.

Mirrors the exact structure of 00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf
— including the §3+§4 prose blocks on page 1, the "(ficticio)" CPF suffix in the
CPF cell, the combined "Agencia: X | Conta: Y" page-2 line, and the running
footer with page number — but with completely different fictitious client data
(Salvador/BA, financiamento de veículo) that the pipeline has never seen.

Purpose: out-of-distribution holdout to validate that the literal-extraction
prompt change generalizes to a brief-faithful layout it has not been tuned on.

Output:
    05_synthetic_data/pdfs/F09_brief_shape.pdf
    05_synthetic_data/gold/F09_brief_shape.json
"""
from io import BytesIO
import json
from pathlib import Path

from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).parent
OUT_PDF = HERE / "pdfs" / "F09_brief_shape.pdf"
OUT_GOLD = HERE / "gold" / "F09_brief_shape.json"
OUT_PDF.parent.mkdir(exist_ok=True, parents=True)
OUT_GOLD.parent.mkdir(exist_ok=True, parents=True)


CLIENT_ANA = {
    "client_name": "Ana Beatriz Souza Carvalho",
    "cpf_raw": "567.890.123-45",
    "cpf_display": "567.890.123-45 (ficticio)",
    "birth_date": "28/03/1991",
    "phone": "(71) 99654-2287",
    "email": "ana.carvalho.exemplo@emailficticio.com",
    "address": "Rua Chile, 478, Casa 02 - Centro - Salvador/BA",
    "postal_code": "40020-000",
    "contract_number": "BX-2025-0098432",
    "product": "Financiamento de veiculo",
    "contract_date": "03/09/2025",
    "original_amount": "R$ 32.700,00",
    "updated_balance": "R$ 38.940,15",
    "days_overdue": "89 dias",
    "status": "Aguardando proposta",
    "last_contact_attempt": "18/03/2026",
    "internal_owner": "Equipe Cobranca - Nucleo 02",
    "p2_holder": "Ana Beatriz Souza Carvalho",
    "p2_address": "Rua Chile, 478, Casa 02",
    "p2_neighborhood": "Centro - Salvador/BA",
    "p2_postal": "40020-000",
    "p2_reference": "Conta de gas - Distribuidora Ficticia de Gas",
    "p2_period": "02/2026",
    "p2_value": "R$ 96,38",
    "p2_barcode": "81790.00000 49638.000000 10524.050006 7 99990000009638",
    "p2_bank_name": "Banco Exemplo S.A.",
    "p2_branch": "5678",
    "p2_account": "00045123-7",
    "p2_tx_date": "05/03/2026",
    "p2_tx_type": "Pagamento integral",
    "p2_payer": "Ana Beatriz Souza Carvalho",
    "p2_payee": "Banco X - Carteira de Cobranca",
    "p2_amount_paid": "R$ 2.800,00",
    "p2_auth": "BX26.03.05.00098.43210.FICT",
}


# ---------- Page 1 (digital text + tables + prose) ----------

def page1_tables(d):
    labels = {
        "client_name": "Nome completo",
        "cpf_display": "CPF",
        "birth_date": "Data de nascimento",
        "phone": "Telefone",
        "email": "E-mail",
        "address": "Endereco",
        "postal_code": "CEP",
        "contract_number": "Contrato",
        "product": "Produto",
        "contract_date": "Data de contratacao",
        "original_amount": "Valor original",
        "updated_balance": "Saldo atualizado",
        "days_overdue": "Dias em atraso",
        "status": "Status interno",
        "last_contact_attempt": "Ultima tentativa de contato",
        "internal_owner": "Responsavel interno",
    }
    ident_keys = ["client_name", "cpf_display", "birth_date", "phone", "email", "address", "postal_code"]
    debt_keys = [
        "contract_number", "product", "contract_date", "original_amount",
        "updated_balance", "days_overdue", "status", "last_contact_attempt", "internal_owner",
    ]
    ident = [["Campo", "Informacao"]] + [[labels[k], d[k]] for k in ident_keys]
    debt = [["Campo", "Informacao"]] + [[labels[k], d[k]] for k in debt_keys]
    return ident, debt


def build_page1_story(d):
    styles = getSampleStyleSheet()
    h_style = ParagraphStyle("H", parent=styles["Heading1"], fontSize=16, spaceAfter=8, alignment=1)
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=9, textColor=colors.grey, spaceAfter=14)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, spaceAfter=6, leading=14)

    story = [
        Paragraph("BANCO X - DOSSIÊ DE CLIENTE DEVEDOR", h_style),
        Paragraph("Documento ficticio para desafio tecnico de extracao de dados", sub_style),
    ]

    ident_rows, debt_rows = page1_tables(d)
    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6eef7")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bdbdbd")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])

    story.append(Paragraph("1. Identificacao do Cliente", h2_style))
    t1 = Table(ident_rows, colWidths=[5*cm, 11*cm])
    t1.setStyle(table_style)
    story.append(t1)

    story.append(Paragraph("2. Informacoes da Divida", h2_style))
    t2 = Table(debt_rows, colWidths=[5*cm, 11*cm])
    t2.setStyle(table_style)
    story.append(t2)

    story.append(Paragraph("3. Dados a serem extraidos para planilha", h2_style))
    story.append(Paragraph(
        "Campos esperados: nome, CPF, telefone, e-mail, endereco, contrato, produto, valor original, "
        "saldo atualizado, dias em atraso, status, ultima tentativa de contato e responsavel interno.",
        body_style,
    ))

    story.append(Paragraph("4. Observacoes", h2_style))
    story.append(Paragraph(
        "Este documento foi gerado apenas para simular um PDF operacional com estrutura repetitiva. "
        "A segunda pagina contem imagem simulada de comprovantes anexados, exigindo que a solucao "
        "avalie tambem documentos com informacoes dentro de imagens.",
        body_style,
    ))
    story.append(PageBreak())
    return story


# ---------- Page 2 (rasterized comprovantes — brief-faithful layout) ----------

def _font(size):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_page2_image(d):
    W, H = 1200, 1500
    img = PILImage.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    font_h1 = _font(28)
    font_h2 = _font(22)
    font_body = _font(18)
    font_small = _font(14)

    draw.text((50, 30), "Anexos do Cliente", fill="black", font=font_h1)
    draw.text((50, 75),
              "A pagina abaixo simula comprovantes inseridos como imagem dentro do PDF.",
              fill="gray", font=font_small)
    draw.text((50, 105), "COMPROVANTES ANEXADOS - DOCUMENTO FICTICIO",
              fill="black", font=font_h2)
    draw.text((50, 135), "Uso exclusivo para teste tecnico - dados simulados",
              fill="gray", font=font_small)

    # Comprovante de Endereço
    y = 180
    draw.rectangle([(40, y), (W - 40, y + 360)], outline=(190, 190, 190), width=2)
    draw.text((60, y + 12), "Comprovante de Endereco", fill="black", font=font_h2)
    y += 55
    for label, value in [
        ("Titular:", d["p2_holder"]),
        ("Endereco:", d["p2_address"]),
        ("Bairro:", d["p2_neighborhood"]),
        ("CEP:", d["p2_postal"]),
        ("Referencia:", d["p2_reference"]),
        ("Mes/Ano:", d["p2_period"]),
        ("Valor:", d["p2_value"]),
        ("Codigo de barras:", d["p2_barcode"]),
    ]:
        draw.text((60, y), f"{label} {value}", fill="black", font=font_body)
        y += 32

    # Comprovante Bancário — note: Agencia + Conta on the SAME LINE (brief-faithful)
    y = 580
    draw.rectangle([(40, y), (W - 40, y + 420)], outline=(190, 190, 190), width=2)
    draw.text((60, y + 12), "Comprovante Bancario", fill="black", font=font_h2)
    y += 55
    bank_lines = [
        f"Banco: {d['p2_bank_name']}",
        f"Agencia: {d['p2_branch']} | Conta: {d['p2_account']}",
        f"Data da transacao: {d['p2_tx_date']}",
        f"Tipo: {d['p2_tx_type']}",
        f"Pagador: {d['p2_payer']}",
        f"Recebedor: {d['p2_payee']}",
        f"Valor pago: {d['p2_amount_paid']}",
        f"Autenticacao: {d['p2_auth']}",
    ]
    for line in bank_lines:
        draw.text((60, y), line, fill="black", font=font_body)
        y += 32

    # PAGO stamp (green circle)
    cx, cy, r = W - 200, 770, 60
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(0, 130, 70), width=4)
    draw.text((cx - 30, cy - 20), "PAGO", fill=(0, 130, 70), font=font_h2)

    # Footer block
    draw.text((50, 1040), "Observacoes do Anexo", fill="black", font=font_h2)
    draw.text((50, 1080), "Imagem simulada para parecer com comprovante digitalizado.",
              fill="black", font=font_small)
    draw.text((50, 1105), "Nao contem dados reais de pessoas, bancos ou operacoes.",
              fill="black", font=font_small)
    draw.text((50, 1130), "Finalidade: testar extracao de dados em PDF com texto + imagem.",
              fill="black", font=font_small)

    return img


def build_page2_story(d):
    img = make_page2_image(d)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return [RLImage(buf, width=17 * cm, height=21 * cm)]


# ---------- Brief-faithful running footer ----------

def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(
        2 * cm, 1 * cm,
        "Documento ficticio para teste tecnico - nao utilizar como documento real",
    )
    canvas.drawRightString(19 * cm, 1 * cm, f"Pagina {canvas.getPageNumber()}")
    canvas.restoreState()


# ---------- Gold JSON ----------

def _digits(s):
    return "".join(c for c in s if c.isdigit())


def _normalize_currency(brl):
    if not brl:
        return ""
    s = brl.replace("R$", "").strip().replace(".", "").replace(",", ".")
    return s


def _normalize_date(brl):
    if not brl or "/" not in brl:
        return None
    parts = brl.split("/")
    if len(parts) == 3:
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    if len(parts) == 2:
        return f"{parts[1]}-{parts[0]}"
    return None


def _days_int(s):
    digits = _digits(s)
    return int(digits) if digits else None


def make_gold(d):
    return {
        "$meta": {
            "fixture_id": "F09_brief_shape",
            "p1_variation": "brief_faithful",
            "p2_variation": "brief_faithful",
            "generator": "05_synthetic_data/generate_brief_shaped_ood.py",
            "purpose": "OOD holdout: brief-faithful structure, fresh client data",
        },
        "page1": {
            "client_name": d["client_name"],
            "cpf": d["cpf_raw"],
            "cpf_digits_only": _digits(d["cpf_raw"]),
            "birth_date": _normalize_date(d["birth_date"]),
            "phone": d["phone"],
            "email": d["email"],
            "address": d["address"],
            "postal_code": d["postal_code"],
            "contract_number": d["contract_number"],
            "product": d["product"],
            "contract_date": _normalize_date(d["contract_date"]),
            "original_amount": _normalize_currency(d["original_amount"]),
            "updated_balance": _normalize_currency(d["updated_balance"]),
            "days_overdue": _days_int(d["days_overdue"]),
            "status": d["status"],
            "last_contact_attempt": _normalize_date(d["last_contact_attempt"]),
            "internal_owner": d["internal_owner"],
        },
        "page2": {
            "comprovante_endereco": {
                "proof_address_holder": d["p2_holder"],
                "proof_address_line": d["p2_address"],
                "proof_address_neighborhood": d["p2_neighborhood"],
                "proof_address_postal": d["p2_postal"],
                "proof_reference": d["p2_reference"],
                "proof_period": _normalize_date(d["p2_period"]),
                "proof_value": _normalize_currency(d["p2_value"]),
                "proof_barcode": _digits(d["p2_barcode"]),
            },
            "comprovante_bancario": {
                "bank_name": d["p2_bank_name"],
                "bank_branch": d["p2_branch"],
                "bank_account": d["p2_account"],
                "transaction_date": _normalize_date(d["p2_tx_date"]),
                "transaction_type": d["p2_tx_type"],
                "payer": d["p2_payer"],
                "payee": d["p2_payee"],
                "amount_paid": _normalize_currency(d["p2_amount_paid"]),
                "authentication_code": d["p2_auth"],
                "paid_stamp_present": True,
            },
        },
    }


# ---------- Build ----------

def build_pdf(d):
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
        title="Banco X - Dossiê de Cliente Devedor",
        author="Project Revelatio — OOD holdout generator",
    )
    story = build_page1_story(d)
    story.extend(build_page2_story(d))
    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)


def main():
    print(f"Generating brief-shaped OOD PDF: {OUT_PDF}")
    build_pdf(CLIENT_ANA)
    gold = make_gold(CLIENT_ANA)
    OUT_GOLD.write_text(json.dumps(gold, ensure_ascii=False, indent=2))
    print(f"  ✓ {OUT_PDF.name}")
    print(f"  ✓ {OUT_GOLD.name}")


if __name__ == "__main__":
    main()
