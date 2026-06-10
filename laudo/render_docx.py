from pathlib import Path
from docxtpl import DocxTemplate
from docx import Document
from jinja2 import Environment
import re

## bibliotecas para a função processar_blocos_docx
from docx.document import Document as _Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl


# TAG de block e end_block
TAG_BLOCK = re.compile(r"\[\[\s*BLOCK\s+([a-zA-Z0-9_]+)\s*\]\]", re.IGNORECASE)
TAG_END_BLOCK = re.compile(r"\[\[\s*END\s*_?\s*BLOCK\s*\]\]", re.IGNORECASE)

def texto_xml(el) -> str:
    textos = []
    for node in el.iter():
        if node.tag.endswith("}t") and node.text:
            textos.append(node.text)

    return (
        "".join(textos)
        .replace("\u200b", "")
        .replace("\ufeff", "")
        .replace("\xa0", " ")
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )

def remover_xml(el):
    parent = el.getparent()
    if parent is not None:
        parent.remove(el)


# Frases com a primeira palavra maiuscula
def frase_maiuscula(texto):
    if not texto:
        return texto
    return texto[0].upper() + texto[1:]

# Função para remover o paragrafo
def remover_paragrafo(paragraph):
    p = paragraph._element
    p.getparent().remove(p)
    paragraph._p = paragraph._element = None

##########################################################################################
# Funções para montar os blocos de textos e eliminar as tabelas
##########################################################################################
def iter_elementos_documento(parent):
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    else:
        parent_elm = parent._element

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def remover_tabela(table):
    tbl = table._element
    tbl.getparent().remove(tbl)


def limpar_texto_tag(texto: str) -> str:
    return (
        texto.strip()
        .replace("\u200b", "")
        .replace("\xa0", " ")
    )

def processar_blocos_docx(path_docx: Path, contexto: dict):
    doc = Document(path_docx)
    body = doc.element.body

    pilha = []

    for el in list(body.iterchildren()):
        if not isinstance(el, (CT_P, CT_Tbl)):
            continue

        texto = texto_xml(el)

        match_block = TAG_BLOCK.search(texto)
        match_end = TAG_END_BLOCK.search(texto)

        if match_block:
            nome_bloco = match_block.group(1)
            ativo = bool(contexto.get(nome_bloco, False))

            print(f"BLOCK encontrado: {nome_bloco} | ativo={ativo}")

            pilha.append({
                "nome": nome_bloco,
                "ativo": ativo,
            })

            remover_xml(el)
            continue

        if match_end:
            print("END_BLOCK encontrado")

            if not pilha:
                raise ValueError("Encontrado [[END_BLOCK]] sem [[BLOCK]] correspondente.")

            pilha.pop()
            remover_xml(el)
            continue

        if pilha and not all(item["ativo"] for item in pilha):
            remover_xml(el)

    if pilha:
        raise ValueError(f"Existe [[BLOCK]] sem [[END_BLOCK]] correspondente: {pilha}")

    doc.save(path_docx)

# Gerar laudo Docx
def gerar_laudo_docx(out_dir, contexto, decisoes_irregularidades):
    """
    Preenche o template .docx com o contexto, aplica blocos condicionais
    e salva o laudo final.
    """
    BASE_DIR = Path(__file__).resolve().parent
    template_path = BASE_DIR / "templates" / "laudo_completo.docx"

    output_path = Path(out_dir) / "laudo_pericial.docx"

    contexto_final = {
        **contexto,
        **decisoes_irregularidades,
    }

    # Ambiente Jinja com filtro personalizado
    jinja_env = Environment()
    jinja_env.filters["frase_maiuscula"] = frase_maiuscula

    doc = DocxTemplate(template_path)
    # Primeira palavra maiúscula
    doc.render(contexto_final, jinja_env=jinja_env)
    doc.save(output_path)
    #doc.render(contexto_final)
    #doc.save(output_path)

    processar_blocos_docx(output_path, contexto_final)

    return output_path


