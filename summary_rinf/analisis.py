from datetime import datetime
import time
import numpy as np
from pyoxigraph import Store
import json
import pprint
from test_rinf import Tester
from urllib.parse import unquote
import pandas as pd


def divide_columns(row):
    if row["Totales"] != 0:
        return float(row["Aciertos"]) / float(row["Totales"])
    else:
        return np.nan


def divide_columns_qt(row):
    if row["Totales_QT"] != 0:
        return float(row["Aciertos_QT"]) / float(row["Totales_QT"])
    else:
        return np.nan


dataf = pd.DataFrame(columns=['question', 'solution', 'entity_type', 'question_type', 'property',
                              'answer', 'confidence', 'correct', 'log', 'resources'])
entity_types = ["Track", "Platform", "Siding", "ContactLineSystem",
                "TrainDetectionSystem", "ETCSLevel", "LineReference"]
labeled_types = ["OperationalPoint", "SectionOfLine"]

report_name = "20230702_220827"
df = pd.read_excel(f'./qa_reports/qa_report_{report_name}.xlsx', engine='openpyxl')

answers = df['correct'].values
properties = df['property'].values
question_types = df['question_type'].values

unique_prop = list(set(properties))
unique_qtype = list(set(question_types))
df_res = pd.DataFrame({"Properties": unique_prop})
df_res = df_res.drop(0)
df_res["Aciertos"] = 0
df_res["Totales"] = 0
df_res["Porcentaje"] = 0

df_res["Question_Types"] = pd.Series(unique_qtype).reindex(df_res.index)
df_res["Aciertos_QT"] = 0
df_res["Totales_QT"] = 0
df_res["Porcentaje_QT"] = 0

for ans, prop, qtype in zip(answers, properties, question_types):
    df_res.loc[df_res["Properties"] == prop, "Totales"] = df_res.loc[df_res["Properties"] == prop, "Totales"] + 1
    df_res.loc[df_res["Question_Types"] == qtype, "Totales_QT"] = df_res.loc[df_res["Question_Types"] == qtype, "Totales_QT"] + 1
    if "YES" in str(ans):
        df_res.loc[df_res["Properties"] == prop, "Aciertos"] = df_res.loc[df_res["Properties"] == prop, "Aciertos"] + 1
        df_res.loc[df_res["Question_Types"] == qtype, "Aciertos_QT"] = df_res.loc[df_res["Question_Types"] == qtype, "Aciertos_QT"] + 1

df_res['Porcentaje'] = df_res.apply(divide_columns, axis=1)
df_res['Porcentaje_QT'] = df_res.apply(divide_columns_qt, axis=1)

df_res = df_res.sort_values("Porcentaje")
subset = ["Question_Types", "Aciertos_QT", "Totales_QT", "Porcentaje_QT"]
df_res_sort = df_res[subset].sort_values(by="Porcentaje_QT")
df_res[subset] = df_res_sort
# print(df_res)

file_name = f"./qa_analysis/qa_analysis_{report_name}.xlsx"
df_res.to_excel(excel_writer=file_name)
