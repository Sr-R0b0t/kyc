# src/rules.py

def build_kyc_payload(cnpj: dict, rep: dict) -> dict:
    """
    Monta um dicionário com tudo que precisamos para preencher a Ficha KYC.
    """
    # Cadastro PJ
    cadastro = {
        "tipo": "Pessoa Jurídica",
        "razao_social": cnpj.get("razao_social", ""),
        "nome_fantasia": cnpj.get("nome_fantasia", ""),
        "cnpj": cnpj.get("cnpj", ""),
        "data_constituicao": cnpj.get("data_abertura", ""),
        "nacionalidade": "Brasileira",
        "endereco": cnpj.get("endereco_completo", ""),
        "cep": cnpj.get("cep", ""),
        "cnae": cnpj.get("cnae_principal", ""),
        "telefone": cnpj.get("telefone", ""),
        "email": cnpj.get("email", ""),
        "representante_nome": rep.get("nome", ""),
        "representante_cpf": rep.get("cpf", ""),
        "representante_rg": rep.get("rg", ""),
        "representante_data_nascimento": rep.get("data_nascimento", ""),
        "representante_endereco": rep.get("endereco", ""),
        "representante_nacionalidade": rep.get("nacionalidade", "Brasileira"),
    }

    # Questionário PJ – DEFAULT = NÃO
    questionario_pj = {
        "programa_compliance": "Não",
        "socios": f'{cadastro["representante_nome"]} - 100%',
        "subsidiarias": "Não",
        "numero_empregados": "0",  # você pode sobrescrever manualmente depois
        "diretores": f'{cadastro["representante_nome"]} - Empresário',
        # tudo default NÃO
        "relacao_kof": "Não",
        "empregado_kof": "Não",
        "vinculo_autoridade": "Não",
        "investigacoes": "Não",
        "condenacoes": "Não",
        "falencia": "Não",
        "listas_restritivas": "Não",
    }

    return {
        "cadastro": cadastro,
        "questionario_pj": questionario_pj,
    }
