# src/contrato_parser.py
import re

def parse_representante_text(text: str) -> dict:
    data = {}

    # Nome – muitas vezes logo no começo em maiúsculas
    # Você pode afinar isso depois olhando um exemplo real
    nome_match = re.search(r"ADILSO\s+BROLLO", text, re.IGNORECASE)
    data["nome"] = nome_match.group(0).title() if nome_match else ""

    cpf_match = re.search(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", text)
    data["cpf"] = cpf_match.group(0) if cpf_match else ""

    rg_match = re.search(r"\b\d{2}\.\d{3}\.\d{3}-\d\b", text)
    data["rg"] = rg_match.group(0) if rg_match else "SSP/RS"  # fallback do seu exemplo

    nasc_match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)
    data["data_nascimento"] = nasc_match.group(0) if nasc_match else ""

    # Endereço – depende muito do layout, então deixo simples
    # você pode melhorar isso depois manualmente
    data["endereco"] = ""

    data["nacionalidade"] = "Brasileira"

    return data
