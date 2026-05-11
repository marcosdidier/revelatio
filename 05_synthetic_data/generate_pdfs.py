#!/usr/bin/env python3
"""
Synthetic PDF generator for Project Revelatio.

Generates a small corpus of fictitious "Banco X — Dossiê de Cliente Devedor"
PDFs that mimic the structure of the original example PDF at
00_brief/exemplo_pdf_cliente_devedor_ficticio.pdf.

For each fixture, produces:
    pdfs/{fixture_id}.pdf   — 2-page PDF (page 1 digital text tables, page 2 rasterized image)
    gold/{fixture_id}.json  — gold-truth extraction for that PDF, schema matching 01_field_map/gold_truth.json

Usage:
    cd 05_synthetic_data && python3 generate_pdfs.py
"""
from pathlib import Path
import json
import random
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image as RLImage, PageBreak,
)
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).parent
OUT_PDFS = HERE / "pdfs"
OUT_GOLDS = HERE / "gold"
OUT_PDFS.mkdir(exist_ok=True)
OUT_GOLDS.mkdir(exist_ok=True)


# Two distinct fictitious clients
CLIENT_MARIA = {
    "client_name": "Maria Almeida Costa",
    "cpf": "123.456.789-09",
    "birth_date": "14/08/1983",
    "phone": "(81) 98888-1122",
    "email": "maria.costa.exemplo@emailficticio.com",
    "address": "Rua das Laranjeiras, 145, Apto 302 - Boa Vista - Recife/PE",
    "postal_code": "50050-120",
    "contract_number": "BX-2024-0004587",
    "product": "Empréstimo pessoal",
    "contract_date": "12/02/2024",
    "original_amount": "R$ 18.450,00",
    "updated_balance": "R$ 22.780,35",
    "days_overdue": "147 dias",
    "status": "Em negociação",
    "last_contact_attempt": "25/04/2026",
    "internal_owner": "Equipe Cobrança - Núcleo 03",
    "p2_holder": "Maria Almeida Costa",
    "p2_address": "Rua das Laranjeiras, 145, Apto 302",
    "p2_neighborhood": "Boa Vista - Recife/PE",
    "p2_postal": "50050-120",
    "p2_reference": "Conta de energia - Companhia Fictícia de Energia",
    "p2_period": "03/2026",
    "p2_value": "R$ 184,72",
    "p2_barcode": "34191.79001 01043.510047 91020.150008 1 99990000018472",
    "p2_bank_name": "Banco Exemplo S.A.",
    "p2_branch": "1234",
    "p2_account": "00098765-4",
    "p2_tx_date": "18/03/2026",
    "p2_tx_type": "Pagamento parcial de acordo",
    "p2_payer": "Maria Almeida Costa",
    "p2_payee": "Banco X - Carteira de Cobrança",
    "p2_amount_paid": "R$ 750,00",
    "p2_auth": "BX26.03.18.00045.99871.FICT",
}

CLIENT_JOAO = {
    "client_name": "João Silva Pereira",
    "cpf": "987.654.321-00",
    "birth_date": "22/11/1976",
    "phone": "(11) 97777-3344",
    "email": "joao.pereira.exemplo@emailficticio.com",
    "address": "Av. Paulista, 1000, Sala 405 - Bela Vista - São Paulo/SP",
    "postal_code": "01310-100",
    "contract_number": "BX-2025-0001234",
    "product": "Cartão de crédito",
    "contract_date": "05/06/2025",
    "original_amount": "R$ 5.200,00",
    "updated_balance": "R$ 6.847,13",
    "days_overdue": "92 dias",
    "status": "Sem contato",
    "last_contact_attempt": "10/03/2026",
    "internal_owner": "Equipe Cobrança - Núcleo 01",
    "p2_holder": "João Silva Pereira",
    "p2_address": "Av. Paulista, 1000, Sala 405",
    "p2_neighborhood": "Bela Vista - São Paulo/SP",
    "p2_postal": "01310-100",
    "p2_reference": "Conta de telefone - Operadora Fictícia Telecom",
    "p2_period": "02/2026",
    "p2_value": "R$ 247,90",
    "p2_barcode": "84610000012 6 47900000010 4 12300011110 0 99990000024790",
    "p2_bank_name": "Banco Exemplo S.A.",
    "p2_branch": "0987",
    "p2_account": "00012345-6",
    "p2_tx_date": "20/02/2026",
    "p2_tx_type": "Pagamento integral",
    "p2_payer": "João Silva Pereira",
    "p2_payee": "Banco X - Carteira de Cobrança",
    "p2_amount_paid": "R$ 1.500,00",
    "p2_auth": "BX26.02.20.00012.34567.FICT",
}


FIXTURES = [
    {"id": "F01_perfect",                "data": CLIENT_MARIA, "p1_variation": None,        "p2_variation": None},
    {"id": "F02_missing_email",          "data": {**CLIENT_MARIA, "email": ""}, "p1_variation": None, "p2_variation": None},
    {"id": "F03_missing_phone",          "data": {**CLIENT_MARIA, "phone": ""}, "p1_variation": None, "p2_variation": None},
    {"id": "F04_low_quality_page2",      "data": CLIENT_MARIA, "p1_variation": None,        "p2_variation": "noise"},
    {"id": "F05_cpf_no_separators",      "data": {**CLIENT_MARIA, "cpf": "12345678909"}, "p1_variation": None, "p2_variation": None},
    {"id": "F06_alternate_labels",       "data": CLIENT_JOAO,  "p1_variation": "alt_labels", "p2_variation": None},
    {"id": "F07_skewed_page2",           "data": CLIENT_MARIA, "p1_variation": None,        "p2_variation": "skew"},
    {"id": "F08_partial_obscure_page2",  "data": CLIENT_MARIA, "p1_variation": None,        "p2_variation": "obscure"},
]


# --------- PAGE 1 (digital text tables) ---------

def page1_table_data(d, alt_labels=False):
    if alt_labels:
        labels = {"client_name": "Nome:", "cpf": "CPF:", "birth_date": "Nasc.:",
                  "phone": "Tel:", "email": "Email:", "address": "End.:", "postal_code": "CEP:",
                  "contract_number": "Contrato:", "product": "Produto:", "contract_date": "Data contr.:",
                  "original_amount": "Valor orig.:", "updated_balance": "Saldo atual.:",
                  "days_overdue": "Atraso:", "status": "Status:",
                  "last_contact_attempt": "Últ. contato:", "internal_owner": "Resp. interno:"}
    else:
        labels = {"client_name": "Nome completo", "cpf": "CPF", "birth_date": "Data de nascimento",
                  "phone": "Telefone", "email": "E-mail", "address": "Endereço", "postal_code": "CEP",
                  "contract_number": "Contrato", "product": "Produto", "contract_date": "Data de contratação",
                  "original_amount": "Valor original", "updated_balance": "Saldo atualizado",
                  "days_overdue": "Dias em atraso", "status": "Status interno",
                  "last_contact_attempt": "Última tentativa de contato", "internal_owner": "Responsável interno"}

    ident = [["Campo", "Informação"]]
    for k in ["client_name", "cpf", "birth_date", "phone", "email", "address", "postal_code"]:
        ident.append([labels[k], d[k]])

    debt = [["Campo", "Informação"]]
    for k in ["contract_number", "product", "contract_date", "original_amount",
              "updated_balance", "days_overdue", "status", "last_contact_attempt", "internal_owner"]:
        debt.append([labels[k], d[k]])

    return ident, debt


def build_page1_story(d, p1_variation):
    styles = getSampleStyleSheet()
    h_style = ParagraphStyle("H", parent=styles["Heading1"], fontSize=16, spaceAfter=8)
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=9, textColor=colors.grey, spaceAfter=14)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=6)

    story = []
    story.append(Paragraph("BANCO X - DOSSIÊ DE CLIENTE DEVEDOR", h_style))
    story.append(Paragraph("Documento ficticio para desafio tecnico de extracao de dados", sub_style))

    alt_labels = (p1_variation == "alt_labels")
    ident_rows, debt_rows = page1_table_data(d, alt_labels=alt_labels)

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

    story.append(Paragraph("1. Identificação do Cliente", h2_style))
    t1 = Table(ident_rows, colWidths=[5*cm, 11*cm])
    t1.setStyle(table_style)
    story.append(t1)

    story.append(Paragraph("2. Informações da Dívida", h2_style))
    t2 = Table(debt_rows, colWidths=[5*cm, 11*cm])
    t2.setStyle(table_style)
    story.append(t2)

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Documento ficticio gerado para teste tecnico. Estrutura simulada.",
        ParagraphStyle("Foot", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    ))
    story.append(PageBreak())
    return story


# --------- PAGE 2 (rasterized image of comprovantes) ---------

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


def make_page2_image(d, variation=None):
    W, H = 1200, 1500
    img = PILImage.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    font_h1 = _font(28)
    font_h2 = _font(22)
    font_body = _font(18)
    font_small = _font(14)

    draw.text((50, 30), "Anexos do Cliente", fill="black", font=font_h1)
    draw.text((50, 75), "A página abaixo simula comprovantes inseridos como imagem dentro do PDF.",
              fill="gray", font=font_small)
    draw.text((50, 105), "COMPROVANTES ANEXADOS - DOCUMENTO FICTICIO", fill="black", font=font_h2)
    draw.text((50, 135), "Uso exclusivo para teste tecnico - dados simulados", fill="gray", font=font_small)

    # Comprovante de Endereço box
    y = 180
    draw.rectangle([(40, y), (W-40, y+360)], outline=(190, 190, 190), width=2)
    draw.text((60, y+12), "Comprovante de Endereço", fill="black", font=font_h2)
    y += 55
    addr_rows = [
        ("Titular:", d["p2_holder"]),
        ("Endereço:", d["p2_address"]),
        ("Bairro:", d["p2_neighborhood"]),
        ("CEP:", d["p2_postal"]),
        ("Referência:", d["p2_reference"]),
        ("Mês/Ano:", d["p2_period"]),
        ("Valor:", d["p2_value"]),
        ("Código de barras:", d["p2_barcode"]),
    ]
    for label, value in addr_rows:
        draw.text((60, y), f"{label} {value}", fill="black", font=font_body)
        y += 32

    # Comprovante Bancário box
    y = 580
    draw.rectangle([(40, y), (W-40, y+420)], outline=(190, 190, 190), width=2)
    draw.text((60, y+12), "Comprovante Bancário", fill="black", font=font_h2)
    y += 55
    bank_rows = [
        ("Banco:", d["p2_bank_name"]),
        ("Agência:", d["p2_branch"]),
        ("Conta:", d["p2_account"]),
        ("Data da transação:", d["p2_tx_date"]),
        ("Tipo:", d["p2_tx_type"]),
        ("Pagador:", d["p2_payer"]),
        ("Recebedor:", d["p2_payee"]),
        ("Valor pago:", d["p2_amount_paid"]),
        ("Autenticação:", d["p2_auth"]),
    ]
    for label, value in bank_rows:
        draw.text((60, y), f"{label} {value}", fill="black", font=font_body)
        y += 32

    # PAGO stamp
    cx, cy, r = W-200, 770, 60
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline=(0, 130, 70), width=4)
    draw.text((cx-30, cy-20), "PAGO", fill=(0, 130, 70), font=font_h2)

    # Footer
    draw.text((50, 1040), "Observações do Anexo", fill="black", font=font_h2)
    draw.text((50, 1080), "Imagem simulada para parecer com comprovante digitalizado.", fill="black", font=font_small)
    draw.text((50, 1105), "Não contem dados reais de pessoas, bancos ou operações.", fill="black", font=font_small)
    draw.text((50, 1130), "Finalidade: testar extração de dados em PDF com texto + imagem.", fill="black", font=font_small)

    # Variations
    if variation == "noise":
        img = img.filter(ImageFilter.GaussianBlur(radius=2.0))
        random.seed(42)
        px = img.load()
        for _ in range(8000):
            x = random.randint(0, W-1)
            yy = random.randint(0, H-1)
            shade = random.randint(140, 220)
            px[x, yy] = (shade, shade, shade)
    elif variation == "skew":
        img = img.rotate(-3, expand=False, fillcolor=(255, 255, 255), resample=PILImage.BICUBIC)
    elif variation == "obscure":
        d2 = ImageDraw.Draw(img)
        d2.rectangle([(0, 720), (W, 770)], fill=(20, 20, 20))

    return img


def build_page2_story(d, p2_variation):
    img = make_page2_image(d, variation=p2_variation)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    rl_img = RLImage(buf, width=17*cm, height=21*cm)
    return [rl_img]


# --------- GOLD JSON GENERATION ---------

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


def make_gold(fixture):
    d = fixture["data"]
    return {
        "$meta": {
            "fixture_id": fixture["id"],
            "p1_variation": fixture["p1_variation"],
            "p2_variation": fixture["p2_variation"],
            "generator": "05_synthetic_data/generate_pdfs.py",
        },
        "page1": {
            "client_name": d["client_name"],
            "cpf": d["cpf"],
            "cpf_digits_only": _digits(d["cpf"]),
            "birth_date": _normalize_date(d["birth_date"]),
            "phone": d["phone"] or None,
            "email": d["email"] or None,
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


# --------- PDF BUILD ---------

def build_pdf(fixture):
    pdf_path = OUT_PDFS / f"{fixture['id']}.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
        title=f"Banco X - Dossiê (sintético: {fixture['id']})",
    )
    story = build_page1_story(fixture["data"], fixture["p1_variation"])
    story.extend(build_page2_story(fixture["data"], fixture["p2_variation"]))
    doc.build(story)
    return pdf_path


def main():
    print(f"Generating {len(FIXTURES)} synthetic PDFs into {OUT_PDFS}/ ...")
    for fx in FIXTURES:
        pdf_path = build_pdf(fx)
        gold = make_gold(fx)
        gold_path = OUT_GOLDS / f"{fx['id']}.json"
        gold_path.write_text(json.dumps(gold, ensure_ascii=False, indent=2))
        print(f"  ✓ {fx['id']}: {pdf_path.name} + {gold_path.name}")
    print(f"Done. {len(FIXTURES)} PDFs + golds.")


if __name__ == "__main__":
    main()
