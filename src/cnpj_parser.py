# src/cnpj_parser.py
import re

def _get_after(label: str, text: str, end_chars=("\n",)):
    idx = text.find(label)
    if idx == -1:
        return ""
    start = idx + len(label)
    # pega até o próximo \n
    end = len(text)
    for ch in end_chars:
        tmp = text.find(ch, start)
        if tmp != -1:
            end = min(end, tmp)
    return text[start:end].strip(" :\t")

def parse_cnpj_text(text: str) -> dict:
    data = {}

    data["razao_social"] = _get_after("NOME EMPRESARIAL", text)
    if not data["razao_social"]:
        data["razao_social"] = _get_after("Nome Empresarial:", text)

    data["nome_fantasia"] = _get_after("TÍTULO DO ESTABELECIMENTO (NOME DE FANTASIA)", text)
    if not data["nome_fantasia"]:
        data["nome_fantasia"] = _get_after("Título do Estabelecimento (Nome de Fantasia):", text)

    cnpj_match = re.search(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", text)
    data["cnpj"] = cnpj_match.group(0) if cnpj_match else ""

    data["data_abertura"] = _get_after("DATA DE ABERTURA", text)
    if not data["data_abertura"]:
        data["data_abertura"] = _get_after("Data de Abertura:", text)

    # CNAE principal
    cnae_principal = _get_after(
        "CÓDIGO E DESCRIÇÃO DA ATIVIDADE ECONÔMICA PRINCIPAL", text
    )
    data["cnae_principal"] = cnae_principal

    # Endereço (bem simplificado; você pode ajustar com regex mais fino depois)
    endereco_label = "ENDEREÇO"
    endereco_bloco = text[text.find(endereco_label):]
    linhas_end = endereco_bloco.splitlines()
    # geralmente a linha 1 é "ENDEREÇO ..." e na 2 já vem logradouro
    if len(linhas_end) >= 2:
        data["endereco_completo"] = linhas_end[1].strip()
    else:
        data["endereco_completo"] = ""

    # Município / UF / CEP
    cep_match = re.search(r"\b\d{5}-\d{3}\b", text)
    data["cep"] = cep_match.group(0) if cep_match else ""

    # aqui você pode refinar trazendo MUNICÍPIO e UF via regex
    data.setdefault("municipio_uf", "")

    # Telefones / e-mail – no seu exemplo tem no rodapé; dá para melhorar com regex
    data["telefone"] = ""
    data["email"] = ""

    # Natureza jurídica
    data["natureza_juridica"] = _get_after("NATUREZA JURÍDICA", text)

    return data
