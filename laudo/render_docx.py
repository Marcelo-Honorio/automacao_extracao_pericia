from pathlib import Path
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

def gerar_laudo_docx(template_path, output_path, contexto):
    template_path = Path(template_path)
    output_path = Path(output_path)

    doc = DocxTemplate(template_path)

    contexto_final = dict(contexto)

    # imagem
    if contexto.get("grafico_saldo"):
        contexto_final["grafico_saldo"] = InlineImage(
            doc,
            str(contexto["grafico_saldo"]),
            width=Mm(140)
        )

    doc.render(contexto_final)
    doc.save(output_path)
    return output_path