import subprocess
from app.utils.pdf_reader import parse_pdf_tables

def doc_to_pdf(docpath) -> str:
    arr = docpath.split('/')
    dirname = "/".join(arr[:-1])
    filename = arr[-1].replace('.docx', '.pdf')
    filename = filename.replace('.doc', '.pdf')
    # print(docpath, dirname, filename)
    # subprocess.run(["soffice", "--headless", "--convert-to", "pdf", docpath, "--outdir", dirname])
    return dirname + '/' + filename


def read_file(path: str):
    if path.endswith(".doc") or path.endswith('.docx'):
        path = doc_to_pdf(path)
    print(path)
    parse_pdf_tables(path)
    with open(path + '.decrypt', 'r') as file:
        return file.read()