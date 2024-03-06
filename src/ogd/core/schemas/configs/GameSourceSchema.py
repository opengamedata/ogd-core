# import standard libraries
import logging
from typing import Any, Dict, List, Optional, Union
# import local files
from ogd.core.schemas.configs.data_sources.DataSourceSchema import DataSourceSchema
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

class GameSourceSchema(Schema):
    """A simple Schema structure containing configuration information for a particular game's data.
    
    When given to an interface, this schema is treated as the location from which to retrieve data.
    When given to an outerface, this schema is treated as the location in which to store data.
    (note that some interfaces/outerfaces, such as debugging i/o-faces, may ignore the configuration)
    Key properties of this schema are:
    - `Name` : Typically, the name of the Game whose source configuration is indicated by this schema
    - `Source` : A data source where game data is stored
    - `DatabaseName` : The name of the specific database within the source that contains this game's data
    - `TableName` : The neame of the specific table within the database holding the given game's data
    - `TableSchema` : A schema indicating the structure of the table containing the given game's data.

    :param Schema: _description_
    :type Schema: _type_
    """
    def __init__(self, name:str, all_elements:Dict[str, Any], data_sources:Dict[str, DataSourceSchema]):
        self._source_name   : str
        self._source_schema : Optional[DataSourceSchema]
        self._db_name       : str
        self._table_schema  : str
        self._table_name    : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Game Source config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "source" in all_elements.keys():
            self._source_name = GameSourceSchema._parseSource(all_elements["source"])
        else:
            self._source_name = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'source' element; defaulting to source_name={self._source_name}", logging.WARN)
        if self._source_name in data_sources.keys():
            self._source_schema = data_sources[self._source_name]
        else:
            self._source_schema = None
            Logger.Log(f"{name} config's 'source' name ({self._source_name}) was not found in available source schemas; defaulting to source_schema={self._source_schema}", logging.WARN)
        if "database" in all_elements.keys():
            self._db_name = GameSourceSchema._parseDBName(all_elements["database"])
        else:
            self._db_name = name
            Logger.Log(f"{name} config does not have a 'database' element; defaulting to db_name={self._db_name}", logging.WARN)
        if "table" in all_elements.keys():
            self._table_name = GameSourceSchema._parseTableName(all_elements["table"])
        else:
            self._table_name = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'table' element; defaulting to table={self._table_name}", logging.WARN)
        if "schema" in all_elements.keys():
            self._schema = GameSourceSchema._parseSchema(all_elements["schema"])
        else:
            self._schema = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'schema' element; defaulting to schema={self._schema}", logging.WARN)

        _used = {"source", "database", "table", "schema"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def SourceName(self) -> str:
        return self._source_name

    @property
    def Source(self) -> Optional[DataSourceSchema]:
        return self._source_schema

    @property
    def DatabaseName(self) -> str:
        return self._db_name

    @property
    def TableName(self) -> str:
        return self._table_name

    @property
    def TableSchema(self) -> str:
        return self._schema

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: _{self.TableSchema}_ format, source {self.Source.Name if self.Source else 'None'} : {self.DatabaseName}.{self.TableName}"
        return ret_val

    @staticmethod
    def EmptySchema() -> "GameSourceSchema":
        return GameSourceSchema(name="NOT FOUND", all_elements={}, data_sources={})

    @staticmethod
    def _parseSchema(schema) -> str:
        ret_val : str
        if isinstance(schema, str):
            ret_val = schema
        else:
            ret_val = str(schema)
            Logger.Log(f"Game Source schema type was unexpected type {type(schema)}, defaulting to str(schema)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSource(source) -> str:
        ret_val : str
        if isinstance(source, str):
            ret_val = source
        else:
            ret_val = str(source)
            Logger.Log(f"Game Source source name was unexpected type {type(source)}, defaulting to str(source)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDBName(db_name) -> str:
        ret_val : str
        if isinstance(db_name, str):
            ret_val = db_name
        else:
            ret_val = str(db_name)
            Logger.Log(f"MySQL Data Source DB name was unexpected type {type(db_name)}, defaulting to str(db_name)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseTableName(table) -> str:
        ret_val : str
        if isinstance(table, str):
            ret_val = table
        else:
            ret_val = str(table)
            Logger.Log(f"Game Source table name was unexpected type {type(table)}, defaulting to str(table)={ret_val}.", logging.WARN)
        return ret_val
