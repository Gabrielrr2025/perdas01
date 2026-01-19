import re
import pdfplumber
from typing import List, Dict

# Linha típica (exemplos nos PDFs):
# 000619 - TORTA FLORESTA NEGRA KG KG 1,94 69,90 135,47
# 004003 - CIGARRETE UN UN 2,00 10,90 21,80
ITEM_RE = re.compile(
    r"""^\s*
    (?P<codigo>\d{4,6})\s*-\s*
    (?P<produto>.+?)\s+
    (?P<un1>KG|UN)\s+
    (?P<un2>KG|UN)\s+
    (?P<qtde>\d+,\d+|\d+)\s+
    (?P<preco>\d+,\d+)\s+
    (?P<venda>\d+,\d+)
    \s*$""",
    re.VERBOSE
)

def _to_float_br(x: str) -> float:
    # converte "1.234,56" ou "135,47" para float
    x = x.replace(".", "").replace(",", ".")
    return float(x)

def parse_pdf_items(pdf_path: str) -> List[Dict]:
    rows: List[Dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                m = ITEM_RE.match(line)
                if not m:
                    continue

                codigo = m.group("codigo").strip()
                produto = m.group("produto").strip()

                qtde = _to_float_br(m.group("qtde"))
                preco = _to_float_br(m.group("preco"))
                venda = _to_float_br(m.group("venda"))

                rows.append({
                    "Produto": f"{codigo} - {produto}",
                    "Quantidade": qtde,
                    "Valor": venda,   # aqui é a coluna "Venda" (total)
                    # Se quiser Valor=preço unitário: troque para preco
                })

    return rows
