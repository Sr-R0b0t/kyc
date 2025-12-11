from src.kyc_ai_extractor import extract_kyc_from_pdf
from src.kyc_writer import generate_xlsx


def main():
    print("🧠 Lendo CNPJ...")
    cnpj_data = extract_kyc_from_pdf("uploads/cnpj.pdf")

    print("🧠 Lendo contrato / representante...")
    contrato_data = extract_kyc_from_pdf("uploads/contrato.pdf")

    final_data = cnpj_data.copy()

    # NIRE
    if not final_data.get("nire"):
        final_data["nire"] = contrato_data.get("nire", "")

    # Representante
    for k in [
        "nome_representante",
        "cpf_representante",
        "rg_representante",
        "data_nascimento_representante",
    ]:
        if contrato_data.get(k):
            final_data[k] = contrato_data[k]

    # Email
    if not final_data.get("email"):
        final_data["email"] = contrato_data.get("email", "")

    # Sócios (preferência contrato)
    if contrato_data.get("socios"):
        final_data["socios"] = contrato_data["socios"]

    # Diretores
    if contrato_data.get("diretores"):
        final_data["diretores"] = contrato_data["diretores"]

    # Texto bruto
    final_data["_raw_text"] = (
        cnpj_data.get("_raw_text", "") + "\n" +
        contrato_data.get("_raw_text", "")
    )

    generate_xlsx(final_data, "output/Ficha_KYC_Preenchida.xlsx")
    print("✅ KYC gerado com sucesso!")


if __name__ == "__main__":
    main()
