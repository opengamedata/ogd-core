import pandas as pd
from realtime.ModelManager import ModelManager
import json
import numpy as np
from models.Model import ModelInputType

# df = pd.read_csv('tests/test_data/LAKELAND_20200501_to_20200530/LAKELAND_20200501_to_20200530_5c141b6_dump.tsv', header=0, sep='\t')
df = pd.read_csv('tests/test_data/LAKELAND_20200828_to_20200828/LAKELAND_20200828_to_20200828_d45ae97_dump.tsv', header=0, sep='\t')

unique_ids = df.sess_id.unique()

session_results_list = []
ids = []

model_mgr = ModelManager(game_name="LAKELAND")
model = model_mgr.LoadModel('DiagonalFarmDetectorModel')

#for session in unique_ids:
#    next_session = df.loc[df['sess_id'] == session]
#    next_session_dict = next_session.to_dict('records')
#    for i in range(0, len(next_session_dict)):
#        next_session_dict[i]["event_data_complex"] = json.loads(next_session_dict[i]["event_data_complex"])
#    #print(next_session_dict)
#    next_session_result = model.Eval(next_session_dict)
#    session_results_list.append(next_session_result)
#    ids.append(session)

for session in unique_ids:
    next_session = df.loc[df['sess_id'] == session]
    next_session_dict = next_session.to_dict('records')
    for i in range(0, len(next_session_dict)):
        next_session_dict[i]["event_data_complex"] = json.loads(next_session_dict[i]["event_data_complex"])
    split_values = []
    for i in range(25, len(next_session_dict), 25):
        next_session_result = model.Eval(next_session_dict[0:i])
        next_session_result = str(next_session_result)
        ":".join(next_session_result)
        #split_values.append(next_session_result[0] + next_session_result[1] + next_session_result[2])
        split_values.append(next_session_result)
    session_results_list.append(split_values)
    ids.append(session)

rows = []
for i in range(0,len(ids)):
    ith_row = []
    ith_row.append(ids[i])
    for j in range(0, len(session_results_list[i])):
        ith_row.append(session_results_list[i][j])
    rows.append(ith_row)

print(rows)

out_df = pd.DataFrame(rows)
out_df.to_csv("diagonal_farm_detector_stats_v18.csv")