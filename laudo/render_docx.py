from pathlib import Path
from docxtpl import DocxTemplate


# template_path,
def gerar_laudo_docx(out_dir, contexto):
    """
    Preenche um template .docx com o contexto e salva o arquivo final.
    """
    BASE_DIR = Path(__file__).resolve().parent
    template_path = BASE_DIR / "templates" / "laudo_modelo.docx"

    output_path = out_dir / "laudo_pericial.docx"
    output_path = Path(output_path)

    doc = DocxTemplate(template_path)
    doc.render(contexto)
    doc.save(output_path)

    return output_path