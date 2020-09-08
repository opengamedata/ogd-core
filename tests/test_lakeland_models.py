import unittest
from tests import helpers

# run as python -m unittest tests.test_models from the opengamedata dir


test_zip_path = lambda kind: f'tests/test_data/LAKELAND_20200501_to_20200530_5c141b6_{kind}.zip'
test_v18_zip_paths = lambda kind: f'tests/test_data/sample_v18_{kind}.zip'
kind_to_sep = {
    "dump": '\t',
    "proc": ',',
    "raw": '\t'
}

def get_df(kind, kind_to_path_func):
    df, _ = helpers.getLogDFbyPaths([kind_to_path_func(kind)],
                            index_cols=False,
                            sep=kind_to_sep[kind])
    return df

test_dfs = helpers.LazyDict(get_df, kind_to_path_func=test_zip_path)
test_v18_dfs = helpers.LazyDict(get_df, kind_to_path_func=test_v18_zip_paths)

test_proc_sessions = test_dfs['proc'].to_dict('records')
test_v18_dumps = [groupdf.to_dict('records') for _, groupdf in test_v18_dfs['dump'].groupby('sess_id')]

feature_models = []

sequence_models = []

def test_feature_models():
    for m in feature_models:
        print(m, m.Eval(test_proc_sessions), sep='\n')

def test_sequence_models():
    for session_dump in test_v18_dumps:
        for m in sequence_models:
            print(m, m.Eval(session_dump), sep='\n')







if __name__ == '__main__':
    pass
