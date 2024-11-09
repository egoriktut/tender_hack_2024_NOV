from typing import List, Optional, TypedDict

import camelot
import pandas as pd


class PageData(TypedDict, total=False):
    text: Optional[str]
    table: Optional[List[List[List[str]]]]
    inversed_text: Optional[str]
    inversed_table: Optional[List[List[List[str]]]]


pd.set_option("display.max_colwidth", None)

import os


def parse_pdf_tables(pdf_path):
    output_dir = os.path.join(os.path.dirname(pdf_path))
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, os.path.basename(pdf_path) + ".decrypt")

    tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")

    horizontal_tables = []
    vertical_tables = []

    with open(output_file_path, "w") as answer:
        for i, table in enumerate(tables):
            df = table.df
            if df.shape[1] > df.shape[0]:
                horizontal_tables.append(df)
                answer.write(
                    df.to_string(index=False, header=False)
                    .replace("\n", " ")
                    .replace("  ", " ")
                    + "\n"
                )
            else:
                vertical_df = df.transpose()
                vertical_tables.append(vertical_df)
                answer.write(
                    vertical_df.to_string(index=False, header=False)
                    .replace("\n", " ")
                    .replace("  ", " ")
                    + "\n"
                )

    return horizontal_tables, vertical_tables
