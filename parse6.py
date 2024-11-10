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
prev_item_id = None
table_wid = 0

for table in tables:
    df = table.df
    specs = ["" for i in range(table_wid)]

    if (start_id is None and df.shape[1] > 4 or start_id is not None and df.shape[1] >= table_wid) and not df.isnull().any().any():
        print('READING TABLE')
        for i in range(df.shape[0]):
            print(list(df.iloc[i]))
            if prev_item_id == None:
                sid = validator.find_start_id(df)
                if sid > -1:
                    prev_item_id = 0

                    specs = list(df.iloc[prev_item_id])
                    table_wid = len(specs)              
                    all_doc_specs.append(["" for i in range(table_wid)])
      
                    print("POBEDA READ ALL FILE TO END", specs, table_wid, prev_item_id)

            else:
                # ширина равна шир табл
                # print(len(specs), table_wid, len(list(df.iloc[i])), table_wid == len(list(df.iloc[i])))
                if table_wid == len(list(df.iloc[i])):
                    if list(df.iloc[i])[0] != '' and list(df.iloc[i])[0].isdigit():
                        # print("wanna new prev id [", list(df.iloc[i])[0], "]")
                        # print(df.iloc[i])
                        try:
                            print("wanna new prev id [", list(df.iloc[i])[0], "]")
                            # print(df.iloc(i))
                            prev_item_id = int(list(df.iloc[i])[0]) - 1
                            for i in range(len(all_doc_specs), prev_item_id + 1):
                                all_doc_specs.append(["" for i in range(table_wid)])


                        except:
                            print("error parsing table col 0 for item id")
                            # print("wanna new prev id [", list(df.iloc(i))[0], "]")
                            # print(df.iloc(i))
                    for col_id in range (table_wid):
                        all_doc_specs[prev_item_id][col_id] += " " + list(df.iloc[i])[col_id]
    if len(specs) == table_wid and specs != ["" for i in range(table_wid)]:
        all_doc_specs.append(specs)

for item in all_doc_specs:
    print(item)
# print(all_doc_specs)
            #col_name_mapper: dict = validator.map_pdf_columns(reference_col_name, table.df.iloc[0])
            #print("col mapa", col_name_mapper)