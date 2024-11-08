from typing import AnyStr, List
from typing import TypedDict, List, Optional
import camelot
import pandas as pd


class PageData(TypedDict, total=False):
    text: Optional[str] 
    table: Optional[List[List[List[str]]]] 
    inversed_text: Optional[str] 
    inversed_table: Optional[List[List[List[str]]]]  

pd.set_option('display.max_colwidth', None) 

def parse_pdf_tables(pdf_path):
    tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")

    horizontal_tables = []
    vertical_tables = []
    with open(pdf_path + '.decrypt', 'w') as answer:
      for i, table in enumerate(tables):
          df = table.df 
          if df.shape[1] > df.shape[0]:
              horizontal_tables.append(df)
              answer.write(df.to_string(index=False, header=False).replace('\n', ' ').replace('  ', ' ') + '\n')

          else:
              vertical_df = df.transpose()
              vertical_tables.append(vertical_df)
              answer.write(df.transpose().to_string(index=False, header=False).replace('\n', ' ').replace('  ', ' ') + '\n')

      return horizontal_tables, vertical_tables



