import unittest
from tests import helpers
from models import Lakeland_featseq_velocity as mymodels

# run as python -m unittest tests.test_models from the opengamedata dir


test_zip_paths = {kind: f'tests/test_data/LAKELAND_20200501_to_20200530_5c141b6_{kind}.zip'
                  for kind in "dump proc".split()}
kind_to_sep = {
    "dump": '\t',
    "proc": ',',
    "raw": '\t'
}

test_dfs = {kind: helpers.getLogDFbyPaths([path],
            index_cols=False,
            sep=kind_to_sep[kind])[0]
            for kind, path in test_zip_paths.items()}

for sess





if __name__ == '__main__':
    pass
