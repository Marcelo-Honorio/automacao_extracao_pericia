from pathlib import Path
from docxtpl import DocxTemplate
from docx import Document
import re

# TAG de block e end_block
TAG_BLOCK = re.compile(r"\[\[BLOCK\s+([a-zA-Z0-9_]+)\]\]")
TAG_END_BLOCK = re.compile(r"\[\[END_BLOCK\]\]")

# Função para remover o paragrafo
def remover_paragrafo(paragraph):
    p = paragraph._element
    p.getparent().remove(p)
    paragraph._p = paragraph._element = None

# Função processar blocos de texto
def processar_blocos_docx(path_docx: Path, contexto: dict):
    doc = Document(path_docx)

    pilha = []

    for par in list(doc.paragraphs):
        texto = par.text.strip()

        match_block = TAG_BLOCK.fullmatch(texto)
        match_end = TAG_END_BLOCK.fullmatch(texto)

        if match_block:
            nome_bloco = match_block.group(1)
            ativo = bool(contexto.get(nome_bloco, False))
            pilha.append(ativo)
            remover_paragrafo(par)
            continue

        if match_end:
            if not pilha:
                raise ValueError("Encontrado [[END_BLOCK]] sem [[BLOCK]] correspondente.")
            pilha.pop()
            remover_paragrafo(par)
            continue

        if pilha and not all(pilha):
            remover_paragrafo(par)

    if pilha:
        raise ValueError("Existe [[BLOCK]] sem [[END_BLOCK]] correspondente.")

    doc.save(path_docx)




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