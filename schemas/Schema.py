import abc
import typing

# Abstract base class for game schemas
class Schema(abc.ABC):
    _schema:                      typing.Dict      = {}
    _db_columns:                  typing.Dict      = None
    _feature_list:               typing.Dict      = None
    _event_data_complex_types:   typing.List[str] = None
    _event_data_complex_schemas: typing.Dict      = None
    _initialized:                bool             = False

    @staticmethod
    @abc.abstractmethod
    def initializeClass(schema_path:str, schema_name:str):
        pass

    @staticmethod
    @abc.abstractmethod
    def schema():
        pass

    @staticmethod
    @abc.abstractmethod
    def events():
        pass

    @staticmethod
    @abc.abstractmethod
    def event_types():
        pass

    @staticmethod
    @abc.abstractmethod
    def features():
        pass

    @staticmethod
    @abc.abstractmethod
    def perlevel_features():
        pass

    @staticmethod
    @abc.abstractmethod
    def aggregate_features():
        pass

    @staticmethod
    @abc.abstractmethod
    def feature_list():
        pass

    @staticmethod
    @abc.abstractmethod
    def db_columns():
        pass