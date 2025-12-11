from openpyxl import Workbook
from pathlib import Path
import re


# ==================================================
# NORMALIZAÇÕES
# ==================================================

def normalize_cnae(cnae: str) -> str:
    digits = re.sub(r"\D", "", cnae or "")
    return digits if len(digits) == 7 else ""


def format_cnae(code: str, desc: str) -> str:
    if not code:
        return ""
    formatted = f"{code[:2]}.{code[2:4]}-{code[4]}-{code[5:]}"
    return f"{formatted} - {desc}" if desc else formatted


def normalize_phone(phone: str, raw_text: str = "") -> str:
    if phone:
        if re.search(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}", phone):
            return phone.replace(",", " / ").replace(";", " / ")

    matches = re.findall(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}", raw_text)
    return " / ".join(dict.fromkeys(matches))


# ==================================================
# SÓCIOS / PERCENTUAL
# ==================================================

def parse_percentual(socio: dict) -> str:
    """
    Prioridade:
    1) percentual explícito (ex: 60%)
    2) cálculo via valor_participacao / capital_total
    """

    perc = socio.get("percentual_participacao", "")
    if perc and "%" in perc:
        return perc.strip()

    valor = socio.get("valor_participacao")
    total = socio.get("capital_total")

    if valor and total:
        try:
            valor = float(valor.replace(".", "").replace(",", "."))
            total = float(total.replace(".", "").replace(",", "."))
            pct = round((valor / total) * 100, 2)
            return f"{pct:.0f}%"
        except Exception:
            return ""

    return ""


def format_socios(data: dict) -> str:
    socios = data.get("socios", [])
    if not isinstance(socios, list) or not socios:
        return ""

    resultado = []

    for s in socios:
        nome = s.get("nome", "").strip()
        doc = s.get("cpf_ou_cnpj", "").strip()
        percentual = parse_percentual(s)

        partes = []

        if nome:
            partes.append(nome)
        if doc:
            partes.append(f"({doc})")
        if percentual:
            partes.append(f"- {percentual}")

        if partes:
            resultado.append(" ".join(partes))

    return " / ".join(resultado)


# ==================================================
# DIRETORES / ADMINISTRADORES
# ==================================================

def format_diretores(data: dict) -> str:
    """
    Ex:
    JOÃO SILVA (Diretor Financeiro) / MARIA OLIVEIRA (Administradora)
    """

    diretores = data.get("diretores", [])

    if not isinstance(diretores, list) or not diretores:
        return data.get("nome_representante", "")

    resultado = []

    for d in diretores:
        nome = d.get("nome", "").strip()
        cargo = d.get("cargo", "").strip()

        if nome and cargo:
            resultado.append(f"{nome} ({cargo})")
        elif nome:
            resultado.append(nome)

    return " / ".join(resultado)


# ==================================================
# EXCEL
# ==================================================

def generate_xlsx(data: dict, output_path: str):
    wb = Workbook()

    # =========================
    # ABA CADASTRO
    # =========================
    ws_cad = wb.active
    ws_cad.title = "Cadastro"

    cnae_code = normalize_cnae(data.get("cnae_codigo", ""))
    cnae_desc = data.get("cnae_descricao", "")

    cadastro_rows = [
        ("Tipo", "Pessoa Jurídica"),
        ("Razão Social", data.get("razao_social", "")),
        ("Nome Fantasia", data.get("nome_fantasia", "")),
        ("CNPJ", data.get("cnpj", "")),
        ("NIRE", data.get("nire", "")),
        ("Data de Constituição", data.get("data_constituicao", "")),
        ("Nacionalidade", "Brasileira"),
        ("Endereço", data.get("endereco", "")),
        ("CEP", data.get("cep", "")),
        ("CNAE", format_cnae(cnae_code, cnae_desc)),
        ("Telefone", normalize_phone(data.get("telefone", ""), data.get("_raw_text", ""))),
        ("E-mail", data.get("email", "")),
        ("Representante Legal", data.get("nome_representante", "")),
        ("CPF Representante", data.get("cpf_representante", "")),
        ("RG Representante", data.get("rg_representante", "")),
        ("Data Nascimento", data.get("data_nascimento_representante", "")),
    ]

    for r in cadastro_rows:
        ws_cad.append(r)

    # =========================
    # ABA QUESTIONÁRIO PJ
    # =========================
    ws_pj = wb.create_sheet("Questionário PJ")

    questionario_rows = [
        ("Razão Social", data.get("razao_social", "")),
        ("Nome Comercial", data.get("nome_fantasia", "")),
        ("CNPJ", data.get("cnpj", "")),
        ("Endereço", data.get("endereco", "")),
        ("Telefone", normalize_phone(data.get("telefone", ""), data.get("_raw_text", ""))),
        ("Página Web", data.get("pagina_web", "")),
        ("Sócios / Percentual", format_socios(data)),
        ("Subsidiárias", "Não"),
        ("Número de Empregados", "0"),
        ("Diretores / Administradores", format_diretores(data)),
    ]

    for r in questionario_rows:
        ws_pj.append(r)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return output_path
