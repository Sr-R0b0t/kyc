import os
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from main import main as run_kyc

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "output"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/processar", methods=["POST"])
def processar():
    try:
        cnpj_file = request.files.get("cnpj_pdf")
        contrato_file = request.files.get("contrato_pdf")

        if not cnpj_file or not contrato_file:
            return jsonify({"error": "Envie os dois PDFs (CNPJ e Contrato)."}), 400

        # Nomes fixos esperados pelo seu main.py
        cnpj_path = os.path.join(app.config["UPLOAD_FOLDER"], "cnpj.pdf")
        contrato_path = os.path.join(app.config["UPLOAD_FOLDER"], "contrato.pdf")

        cnpj_file.save(cnpj_path)
        contrato_file.save(contrato_path)

        # Executa a geração do arquivo XLSX
        run_kyc()

        output_file = os.path.join(app.config["OUTPUT_FOLDER"], "Ficha_KYC_Preenchida.xlsx")
        if not os.path.exists(output_file):
            return jsonify({"error": "Falha ao gerar o arquivo XLSX."}), 500

        return send_file(
            output_file,
            as_attachment=True,
            download_name="Ficha_KYC_Preenchida.xlsx"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🚀 CONFIGURAÇÃO OBRIGATÓRIA PARA O RENDER
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 3000)),
        debug=False  # nunca ON no Render!
    )
