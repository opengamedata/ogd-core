## import standard libraries
import logging
import typing
## import local files
import utils
from schemas.Schema import Schema

class WaveSchema(Schema):
    _schema:                     typing.Dict      = {}
    _feature_list:               typing.Dict      = None
    _initialized:                bool             = False

    @staticmethod
    def initializeClass(schema_path:str = "./schemas/JSON", schema_name:str = "WAVES.json"):
        WaveSchema.schema = utils.loadJSONFile(schema_name, schema_path)
        if WaveSchema.schema is None:
            logging.error("Could not find wave event_data_complex schemas at {}".format(schema_path))
        else:
            WaveSchema._feature_list = list(WaveSchema._schema["features"]["perlevel"].keys()) + list(WaveSchema._schema["features"]["aggregate"].keys())
        WaveSchema._initialized = True

    @staticmethod
    def schema():
        return WaveSchema._schema

    @staticmethod
    def events():
        return WaveSchema._schema["events"]

    @staticmethod
    def event_types():
        return WaveSchema._schema["events"].keys()

    @staticmethod
    def features():
        return WaveSchema._schema["features"]

    @staticmethod
    def perlevel_features():
        return WaveSchema._schema["features"]["perlevel"]

    @staticmethod
    def aggregate_features():
        return WaveSchema._schema["features"]["aggregate"]

    @staticmethod
    def feature_list():
        return WaveSchema._feature_list

    @staticmethod
    def db_columns():
        return WaveSchema._schema["db_columns"]