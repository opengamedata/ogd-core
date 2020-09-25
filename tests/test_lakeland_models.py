'''
Example commands to be run in the commandline from the project directory:
py.test tests -s
pytest  tests/test_lakeland_models.py -s -k PopulationModel
pytest tests/test_lakeland_models.py::test_sequence_model[20070509155287116-PopulationModel] -vsl
pytest  tests/test_lakeland_models.py::test_sequence_model[20070513431426580-PopulationModel] --log-level=DEBUG
    --log-file=tests/logs/pop_negative_20070513431426580-PopulationModel.log -vl
    (logging is only helpful if there are logging.debug("") etc. statements in the model/test)

-v: verbose
-s: show print statements
-l: show local variables on error
-x: stop at first error
'''

import unittest
import logging
import pytest
import json
from tests import helpers
from realtime.ModelManager import ModelManager
from models.Model import ModelInputType


zip_path = lambda kind: f'tests/test_data/LAKELAND_20200501_to_20200530_5c141b6_{kind}.zip'
v18_zip_paths = lambda kind: f'tests/test_data/sample_v18_{kind}.zip'
kind_to_sep = {
    "dump": '\t',
    "proc": ',',
    "raw": '\t'
}

def get_df(kind, kind_to_path_func):
    df, _ = helpers.getLogDFbyPaths([kind_to_path_func(kind)],
                            index_cols=False,
                            sep=kind_to_sep[kind])
    if kind=="dump":
        df["event_data_complex"] = df["event_data_complex"].apply(lambda s: json.loads(s))
    return df

dfs = helpers.LazyDict(get_df, kind_to_path_func=zip_path)
v18_dfs = helpers.LazyDict(get_df, kind_to_path_func=v18_zip_paths)

proc_sessions = v18_dfs['proc'].to_dict('records')
proc_session_names = [f'{x["sessID"]}.{x["num_play"]}' for x in proc_sessions]
v18_dumps = [groupdf.to_dict('records') for _, groupdf in v18_dfs['dump'].groupby('sess_id')]
v18_dump_ids = [str(d[0]["sess_id"]) for d in v18_dumps]

model_mgr = ModelManager(game_name="LAKELAND")
model_names = model_mgr.ListModels()
all_models = [model_mgr.LoadModel(model_name) for model_name in model_names]
# print(*list(zip(model_mgr.ListModels(), all_models)), sep='\n')
feature_models, feature_model_names = zip(*[(model,model_name) for model,model_name in zip(all_models, model_names)
                  if model and model.GetInputType() == ModelInputType.FEATURE])
sequence_models, sequence_model_names = zip(*[(model,model_name) for model,model_name in zip(all_models, model_names)
                   if model and model.GetInputType() == ModelInputType.SEQUENCE])


@pytest.mark.parametrize("model", feature_models, ids=feature_model_names)
@pytest.mark.parametrize("proc_sessions", proc_sessions, ids=proc_session_names)
def test_feature_model(model,proc_sessions):
    if type(proc_sessions) is not list:
        proc_sessions = [proc_sessions]
    print(model.Eval(proc_sessions), end=', ')


@pytest.mark.parametrize("model", sequence_models, ids=sequence_model_names)
@pytest.mark.parametrize("session_dump", v18_dumps, ids=v18_dump_ids)
def test_sequence_model(model, session_dump):
    try:
        print(model.Eval(session_dump), end=', ')
    except AssertionError:
        logging.exception("Caught exception")
        raise


if __name__ == '__main__':
    pass
