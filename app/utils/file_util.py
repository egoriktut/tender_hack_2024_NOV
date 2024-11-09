import subprocess

from app.utils.pdf_reader import parse_pdf_tables
import os
import pdfplumber

def read_plain_text(path: str) -> str:
    read_text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text().replace("\n", " ").strip()
            read_text += text
    return read_text


def doc_to_pdf(docpath) -> str:
    arr = docpath.split("/")
    dirname = "/".join(arr[:-1])
    filename = arr[-1].replace(".docx", ".pdf")
    filename = filename.replace(".doc", ".pdf")
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", docpath, "--outdir", dirname]
    )
    return dirname + "/" + filename


def read_file(path: str):
    if path.endswith(".doc") or path.endswith(".docx"):
        path_docx = path
        path = doc_to_pdf(path)
        # os.remove(path_docx)
    try:
        parsed_plaint_text = read_plain_text(path)
        tables = parse_pdf_tables(path)
        parsed_data = {}
        with open(path + ".decrypt", "r") as file:
            parsed_data = file.read()
        # os.remove(path + ".decrypt")
        return parsed_data, parsed_plaint_text, tables
    except Exception as e:
        return None, None, None
