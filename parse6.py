from app.validation import KSValidator
from app.utils.file_util import read_file
import camelot
import pandas as pd



validator = KSValidator()

tz_name = "tz.pdf"
pk_name = "pk.doc"
reference_col_name = {
    "name": ["Наименование", "Название"],
    "quantity": ["Кол.", "Кол-", "Кол-во", "Количество"],
    "date": ["сроки", "срок", "Дата"],
    "cost": ["Стоимость", "Цена", "Стоим"],
}

#validator.download_file("https://zakupki.mos.ru/newapi/api/FileStorage/Download?id=233468189", pk_name, 1)
# validator.download_file("https://zakupki.mos.ru/newapi/api/FileStorage/Download?id=233468193", tz_name, 1)


print("done bro")

tables = camelot.read_pdf("./resources/_1_pk.pdf", pages="all", flavor="stream")

print(tables)
if tables is None:
    print("NULL PAGES")

all_doc_specs = []
start_id = None
table_wid = 0

for table in tables:
    df = table.df
    specs = []

    if df.shape[1] > 4 and not df.isnull().any().any():
        print('READING TABLE')
        for i in range(df.shape[0]):
            # print(list(df.iloc[i]))
            if start_id == None:
                sid = validator.find_start_id(df)
                if sid > -1:
                    start_id = sid
                    specs = list(df.iloc[start_id])
                    table_wid = len(specs)                    
                    print("POBEDA READ ALL FILE TO END", specs, table_wid, start_id)

            else:
                # ширина равна шир табл
                if table_wid == len(df.iloc[i]):
                    for col_id in range (table_wid):
                        specs[col_id] += list(df.iloc[i])[col_id]
    all_doc_specs.append(specs)

print(all_doc_specs)
            #col_name_mapper: dict = validator.map_pdf_columns(reference_col_name, table.df.iloc[0])
            #print("col mapa", col_name_mapper)