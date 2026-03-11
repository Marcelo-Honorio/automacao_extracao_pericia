from pathlib import Path
from docxtpl import DocxTemplate

def gerar_laudo_docx(template_path, out_dir, contexto):
    """
    Preenche um template .docx com o contexto e salva o arquivo final.
    """
    template_path = Path(template_path)
    output_path = out_dir / "laudo_pericial.docx"
    output_path = Path(output_path)

    doc = DocxTemplate(template_path)
    doc.render(contexto)
    doc.save(output_path)

    return output_path