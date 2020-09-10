'''
In the commandline, run "py.test -s tests\" from the project directory.
'''

import unittest
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
v18_dumps = [groupdf.to_dict('records') for _, groupdf in v18_dfs['dump'].groupby('sess_id')]

model_mgr = ModelManager(game_name="LAKELAND")
all_models = [model_mgr.LoadModel(model_name) for model_name in model_mgr.ListModels()]
# print(*list(zip(model_mgr.ListModels(), all_models)), sep='\n')
feature_models = [model for model in all_models if model and model.GetInputType() == ModelInputType.FEATURE]
sequence_models = [model for model in all_models if model and model.GetInputType() == ModelInputType.SEQUENCE]

@pytest.mark.parametrize("model", feature_models)
def test_feature_model(model):
    print(f'\nRunning {model}:', model.Eval(proc_sessions), sep='\n')

@pytest.mark.parametrize("model", sequence_models)
def test_sequence_model(model):
    print(f'\nRunning {model}:')
    for session_dump in v18_dumps:
        print(model.Eval(session_dump), end=', ')
    print()


if __name__ == '__main__':
    pass
