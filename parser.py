import re
import pdfplumber

ITEM_RE = re.compile(
    r"""^\s*
    (?P<codigo>\d{4,6})\s*-\s*
    (?P<produto>.+?)\s+
    (?P<qtde>\d+(?:,\d+)?)\s+
    (?P<preco>\d+,\d+)\s+
    (?P<venda>\d+,\d+)
    \s*$""",
    re.VERBOSE
)

IGNORE_PREFIXES = (
    "SHOPPING",
    "Perdas por",
    "Período:",
    "Sub Departamento",
    "Setor:",
    "UN Qtde",
    "Total do",
    "Total Geral",
    "Pag.",
    "www.",
    "Lince"
)

def br_float(x: str) -> float:
    return float(x.replace(".", "").replace(",", "."))

def parse_pdf_items(pdf_path: str):
    rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():

                line = line.strip()
                if not line:
                    continue

                if line.startswith(IGNORE_PREFIXES):
                    continue

                m = ITEM_RE.match(line)
                if not m:
                    continue

                rows.append({
                    "Produto": m.group("produto").strip(),
                    "Quantidade": br_float(m.group("qtde")),
                    "Valor": br_float(m.group("venda")),
                })

    return rows
