from pathlib import Path

import utils
from tests.t_interfaces.t_CSVInterface import t_CSVInterface
from tests.t_utils import t_utils

test_utils = t_utils()
test_utils.RunAll()
test_config = utils.loadJSONFile(filename="t_config.json", path=Path("./tests"))
if test_config.get("interfaces", False):
    test_CSVInterface = t_CSVInterface()
    test_CSVInterface.RunAll()