from pdf2image import convert_from_path

def pdf_to_images(pdf_path):
    """
    Converte PDF (texto ou escaneado) em lista de imagens.
    """
    return convert_from_path(pdf_path, dpi=300)
