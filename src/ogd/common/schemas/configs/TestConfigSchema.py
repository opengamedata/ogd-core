"""
TestConfigSchema

Contains a Schema class for managing config data for testing configurations.
In particular, base testing config files always have a `"VERBOSE"` setting,
and a listing of `"ENABLED"` tests.
"""

# import standard libraries
import logging
from typing import Any, Dict, Optional

# import 3rd-party libraries

# import OGD libraries
from ogd.core.schemas.Schema import Schema

# import local files

class TestConfigSchema(Schema):
    @staticmethod
    def DEFAULT():
        return TestConfigSchema(
            name            = "DefaultTestConfig",
            verbose         = False,
            enabled_tests   = {
            }
        )

    def __init__(self, name:str, verbose:bool, enabled_tests:Dict[str, bool], other_elements:Dict[str, Any]={}):
        self._verbose       : bool            = verbose
        self._enabled_tests : Dict[str, bool] = enabled_tests
        super().__init__(name=name, other_elements=other_elements)

    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]):
        _verbose         : bool
        _enabled_tests   : Dict[str, bool]
        if "VERBOSE" in all_elements.keys():
            _verbose = TestConfigSchema._parseVerbose(all_elements["VERBOSE"], logger=logger)
        else:
            _verbose = TestConfigSchema.DEFAULT().Verbose
            _msg = f"{name} config does not have an 'VERBOSE' element; defaulting to verbose={_verbose}"
            if logger:
                logger.warn(_msg, logging.WARN)
            else:
                print(_msg)
        if "ENABLED" in all_elements.keys():
            _enabled_tests = TestConfigSchema._parseEnabledTests(all_elements["ENABLED"], logger=logger)
        else:
            _enabled_tests = TestConfigSchema.DEFAULT().EnabledTests
            _msg = f"{name} config does not have an 'ENABLED' element; defaulting to enabled={_enabled_tests}"
            if logger:
                logger.warn(_msg, logging.WARN)
            else:
                print(_msg)

        _used = {"VERBOSE", "ENABLED"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return TestConfigSchema(name=name, verbose=_verbose, enabled_tests=_enabled_tests, other_elements=_leftovers)

    @property
    def Verbose(self) -> bool:
        return self._verbose

    @property
    def EnabledTests(self) -> Dict[str, bool]:
        return self._enabled_tests

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}"
        return ret_val

    @staticmethod
    def _parseVerbose(verbose, logger:Optional[logging.Logger]) -> bool:
        ret_val : bool
        if isinstance(verbose, bool):
            ret_val = verbose
        elif isinstance(verbose, int):
            ret_val = bool(verbose)
        elif isinstance(verbose, str):
            ret_val = False if verbose.upper()=="FALSE" else bool(verbose)
        else:
            ret_val = bool(verbose)
            _msg = f"Config 'verbose' setting was unexpected type {type(verbose)}, defaulting to bool(verbose)={ret_val}."
            if logger:
                logger.warn(_msg, logging.WARN)
            else:
                print(_msg)
        return ret_val

    @staticmethod
    def _parseEnabledTests(enabled, logger:Optional[logging.Logger]) -> Dict[str, bool]:
        ret_val : Dict[str, bool]
        if isinstance(enabled, dict):
            ret_val = { str(key) : bool(val) for key, val in enabled.items() }
        else:
            ret_val = TestConfigSchema.DEFAULT().EnabledTests
            _msg = f"Config 'enabled tests' setting was unexpected type {type(enabled)}, defaulting to class default = {ret_val}."
            if logger:
                logger.warn(_msg, logging.WARN)
            else:
                print(_msg)
        return ret_val
