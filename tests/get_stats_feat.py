import json
from datetime import datetime as dt
import math
import pandas as pd
from pathlib import Path
from ogd.core.schemas.tables.TableSchema import TableSchema
from ogd.games.LAKELAND.LakelandExtractor import LakelandExtractor
from realtime.ModelManager import ModelManager
from ogd.core.schemas.games.GameSchema import GameSchema

dump = pd.read_csv(
    "tests/test_data/LAKELAND_20200828_to_20200828 2/LAKELAND_20200828_to_20200828_d45ae97_dump.tsv", sep='\t')
dump = dump.rename(
    columns={'sess_id':'session_id', 'client_secs_ms':'client_time_ms', 'persistent_sess_id':'persistent_session_id'})
proc = pd.read_csv("tests/test_data/LAKELAND_20200828_to_20200828/LAKELAND_20200828_to_20200828_d45ae97_proc.csv")
# print(df.columns)
model_name = 'PopAchVelocityModel'
file_version = 'v18'
schema = GameSchema.FromFile("LAKELAND", Path("games/LAKELAND/schemas"))
model_mgr = ModelManager(game_name="LAKELAND")
col_names = list(dump.columns)
game_id = dump['app_id'][0]
min_level = dump['level'].min()
max_level = dump['level'].max()
table = TableSchema(game_id=game_id, column_names=col_names, max_level=max_level, min_level=min_level)
#table = TableSchema.FromCSV(dump)
session_id_list = dump.session_id.unique()
model = model_mgr.LoadModel(model_name)
test_outfile = open('test_outfile.csv', 'w+')
next_session_result = []
ids = []

session_result_list = []
def isfloat(x):
    try:
        a = float(x)
    except (TypeError, ValueError):
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except (TypeError, ValueError, OverflowError):
        return False
    else:
        return a == b

def parse_nums(x):
    for k, v in x.items():
        neg, p = False, ""
        if len(v.split('-')) == 2:
            neg = True
        if neg:
            p = v.split("-")[1]
        else:
            p = v
        if isint(p):
            x[k] = int(float(p)) if not neg else -1 * int(float(p))
        elif isfloat(p):
            x[k] = float(p) if not neg else -1 * float(p)
    return x

def get_time(x):
    return dt.strptime(x, '%Y-%m-%d %H:%M:%S')

session_result_list = []
for session in session_id_list:
    slice = 300
    next_session_result = []
    dump_session_data = dump.loc[dump['session_id'] == session].to_dict('records')
    extractor = LakelandExtractor(session, table, schema, test_outfile)
    for i in range(0, len(dump_session_data), slice):
        next_slice = dump_session_data[(i-slice):i]
        # print(i, len(next_slice))
        print(len(dump_session_data), i)
        for row in next_slice:
            row = list(row.values())
            col = row[table.complex_data_index]
            complex_data_parsed = json.loads(col) if (col is not None) else {"event_custom": row[table.event_custom_index]}
            if "event_custom" not in complex_data_parsed.keys():
                complex_data_parsed["event_custom"] = row[table.event_custom_index]
            row[table.client_time_index] = dt.strptime(row[table.client_time_index], '%Y-%m-%d %H:%M:%S')
            row[table.complex_data_index] = complex_data_parsed
            extractor.extractFromRow(row_with_complex_parsed=row, game_table=table)
        extractor.CalculateAggregateFeatures()
        all_features = dict(zip(extractor.getFeatureNames(game_table=table, game_schema=schema),
                                extractor.GetFeatureValues()))
        all_features = parse_nums(all_features)
        result = model.Eval([all_features])[0]
        if result is None:
            break
        next_session_result.append(model.Eval([all_features])[0])
        print("next_sess_result", next_session_result)
    next_session_result.insert(0, session)
    session_result_list.append(next_session_result)

out_df = pd.DataFrame(session_result_list)
out_df.to_csv(f'{model_name}_{file_version}.csv')