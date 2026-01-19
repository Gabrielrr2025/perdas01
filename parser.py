import re
import pdfplumber

# Regex principal:
# - Captura o nome do produto
# - A coluna UN vem depois e NÃO faz parte do nome
ITEM_RE = re.compile(
    r"""^\s*
    (?P<codigo>\d{4,6})\s*-\s*
    (?P<produto>.+?)\s+
    (?P<unidade>UN|KG)\s+
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

def br_float(valor: str) -> float:
    """Converte número brasileiro para float"""
    return float(valor.replace(".", "").replace(",", "."))

def remover_un_coluna(nome: str) -> str:
    """
    Remove APENAS o 'UN' da coluna de unidade.
    - Nunca remove KG
    - Nunca remove UN que faça parte do nome
    """
    nome = nome.strip()

    # remove somente UM ' UN' final (coluna)
    if nome.endswith(" UN"):
        return nome[:-3].strip()

    return nome

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

                match = ITEM_RE.match(line)
                if not match:
                    continue

                produto_raw = match.group("produto").strip()
                produto_final = remover_un_coluna(produto_raw)

                rows.append({
                    "Produto": produto_final,
                    "Quantidade": br_float(match.group("qtde")),
                    "Valor": br_float(match.group("venda")),
                })

    return rows
