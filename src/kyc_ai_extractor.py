import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

PROMPT = """
Você é um analista de KYC sênior no Brasil.

Leia o documento PDF fornecido (pode ser texto ou escaneado), incluindo corpo do texto, cabeçalhos e rodapés.

Extraia e retorne SOMENTE em JSON válido os campos abaixo.

=====================
DADOS DA PESSOA JURÍDICA
=====================
- razao_social
- nome_fantasia
- cnpj
- nire                      (somente números)
- data_constituicao
- endereco
- cep
- telefone                 (pode ter mais de um → separar por " / ")
- email

=====================
CNAE
=====================
- cnae_codigo     → somente números, exatamente 7 dígitos
- cnae_descricao  → descrição da atividade econômica

OBS:
- Nunca misturar CNAE com telefone, CPF, RG ou outros números

=====================
SÓCIOS / QUADRO SOCIETÁRIO
=====================
- socios → LISTA de objetos contendo:
    - nome
    - cpf_ou_cnpj
    - percentual_participacao

Exemplo:
[
  {
    "nome": "JOÃO SILVA",
    "cpf_ou_cnpj": "123.456.789-00",
    "percentual_participacao": "60%"
  },
  {
    "nome": "EMPRESA XYZ LTDA",
    "cpf_ou_cnpj": "12.345.678/0001-90",
    "percentual_participacao": "40%"
  }
]

Regras:
- CPF ou CNPJ é obrigatório se o sócio aparecer no documento
- Percentual deve ser extraído exatamente como no documento
- Se houver mais de um sócio, retornar todos

=====================
REPRESENTANTE LEGAL E DIRETORES
=====================
- nome_representante
- cpf_representante
- rg_representante
- data_nascimento_representante

- diretores → LISTA de objetos contendo:
    - nome
    - cargo

Exemplos válidos:
[
  {
    "nome": "CLEBER ADRIANO VIDAL",
    "cargo": "Administrador"
  },
  {
    "nome": "JOÃO PEREIRA",
    "cargo": "Diretor Financeiro"
  }
]

Regras:
- Se houver diretores sem cargo explícito, retornar cargo como ""
- Nunca retornar diretores como string; sempre como lista de objetos

=====================
REGRAS IMPORTANTES
=====================
- NIRE deve conter apenas números
- Telefone pode aparecer no rodapé ou misturado ao texto
- Aceitar formatos brasileiros:
    (xx) xxxx-xxxx
    (xx) xxxxx-xxxx
- Se houver vários telefones, separar por " / "
- Se o CEP estiver dentro do endereço, extrair para o campo 'cep'
- Se algum campo não existir, retornar ""
- NÃO escrever absolutamente nada fora do JSON
"""


def extract_kyc_from_pdf(pdf_path: str) -> dict:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    uploaded_file = client.files.create(
        file=pdf_path.open("rb"),
        purpose="assistants"
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": PROMPT},
                {"type": "input_file", "file_id": uploaded_file.id}
            ],
        }],
        temperature=0,
        max_output_tokens=2000
    )

    content = response.output_text.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"JSON inválido:\n{content}")

    # segurança
    data.setdefault("socios", [])
    data.setdefault("diretores", "")
    data["_raw_text"] = response.output_text

    return data
