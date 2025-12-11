
# webapp.py (versão corrigida e mais robusta)
import os
import traceback
from flask import Flask, render_template, request, send_file, abort, jsonify
from werkzeug.utils import secure_filename
from main import main as run_kyc  # sua função que gera o XLSX

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "output"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

ALLOWED_EXT = {".pdf"}

def _allowed_filename(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT

@app.route("/")
def index():
    # Certifique-se de ter templates/index.html na pasta templates/
    return render_template("index.html")

@app.route("/processar", methods=["POST"])
def processar():
    try:
        cnpj_file = request.files.get("cnpj_pdf")
        contrato_file = request.files.get("contrato_pdf")

        if not cnpj_file or not contrato_file:
            return jsonify({"error": "Envie os dois PDFs (cnpj_pdf e contrato_pdf)."}), 400

        # valida extensões (segurança)
        if not _allowed_filename(cnpj_file.filename) or not _allowed_filename(contrato_file.filename):
            return jsonify({"error": "Apenas arquivos .pdf são permitidos."}), 400

        # salvar com nomes previsíveis (seu main.py espera uploads/cnpj.pdf e uploads/contrato.pdf)
        # mas ainda usamos secure_filename para segurança caso queira manter nome original
        cnpj_path = os.path.join(app.config["UPLOAD_FOLDER"], "cnpj.pdf")
        contrato_path = os.path.join(app.config["UPLOAD_FOLDER"], "contrato.pdf")

        cnpj_file.save(cnpj_path)
        contrato_file.save(contrato_path)

        # Opcional: checar se os arquivos foram escritos
        if not (os.path.exists(cnpj_path) and os.path.exists(contrato_path)):
            return jsonify({"error": "Falha ao salvar os arquivos no servidor."}), 500

        # Executa seu fluxo atual (pode lançar exceções — vamos capturar)
        try:
            run_kyc()
        except Exception as e:
            tb = traceback.format_exc()
            # retorna o trace para facilitar debug (remova em produção)
            return jsonify({"error": "Erro ao executar a extração KYC.", "details": str(e), "traceback": tb}), 500

        # Resultado esperado
        output_file = os.path.join(app.config["OUTPUT_FOLDER"], "Ficha_KYC_Preenchida.xlsx")
        if not os.path.exists(output_file):
            return jsonify({"error": "Arquivo de saída não encontrado.", "expected_path": output_file}), 500

        # Compatibilidade Flask: download_name (>=2.0) / attachment_filename (antigos)
        try:
            return send_file(output_file, as_attachment=True, download_name="Ficha_KYC_Preenchida.xlsx")
        except TypeError:
            # fallback para versões antigas do Flask
            return send_file(output_file, as_attachment=True, attachment_filename="Ficha_KYC_Preenchida.xlsx")
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"error": "Erro inesperado no servidor.", "details": str(e), "traceback": tb}), 500

if __name__ == "__main__":
    # debug True para facilitar durante desenvolvimento; desligue em produção
    app.run(debug=True, port=3000, host="0.0.0.0")
