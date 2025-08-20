# import standard libraries
from typing import Dict, Final, List, LiteralString, Optional, Self
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.schemas.locations.DatabaseLocationSchema import DatabaseLocationSchema
from ogd.common.utils.typing import Map
from ogd.common.utils.typing import conversions

class GameStoreConfig(Schema):
    """A simple Schema structure containing configuration information for a particular game's data.
    
    When given to an interface, this schema is treated as the location from which to retrieve data.
    When given to an outerface, this schema is treated as the location in which to store data.
    (note that some interfaces/outerfaces, such as debugging i/o-faces, may ignore the configuration)
    Key properties of this schema are:
    - `Name` : Typically, the name of the Game whose source configuration is indicated by this schema
    - `Source` : A data source where game data is stored
    - `DatabaseName` : The name of the specific database within the source that contains this game's data
    - `TableName` : The neame of the specific table within the database holding the given game's data
    - `TableConfig` : A schema indicating the structure of the table containing the given game's data.

    TODO : use a TableConfig for the table_schema instead of just the name of the schema, like we do with source_schema.
    TODO : Implement and use a smart Load(...) function of TableConfig to load schema from given name, rather than FromFile.
    """

    _DEFAULT_GAME_ID     : Final[LiteralString] = "UNKNOWN GAME"
    _DEFAULT_EVENTS_FROM : Final[List[DataTableConfig]] = [DataTableConfig(
        name="DefaultEventSource",
        store_name="DefaultStore",
        schema_name="DefaultTable",
        table_location=DatabaseLocationSchema.Default(),
        store_config=BigQueryConfig.Default(),
        table_schema=EventTableSchema.FromFile(schema_name="OPENGAMEDATA_BQ")
    )]
    _DEFAULT_EVENTS_TO   : Final[List[DataTableConfig]] = [DataTableConfig(
        name="DefaultEventDest",
        store_name="DefaultStore",
        schema_name="DefaultTable",
        table_location=None,
        store_config=FileStoreConfig.Default(),
        table_schema=EventTableSchema.FromFile(schema_name="OGD_EVENTS_FILE")
    )]
    _DEFAULT_FEATS_FROM  : Final[List[DataTableConfig]] = [DataTableConfig(
        name="DefaultFeatSource",
        store_name="DefaultStore",
        schema_name="DefaultTable",
        table_location=DatabaseLocationSchema.Default(),
        store_config=BigQueryConfig.Default(),
        table_schema=FeatureTableSchema.FromFile(schema_name="OPENGAMEDATA_BQ")
    )]
    _DEFAULT_FEATS_TO    : Final[List[DataTableConfig]] = [DataTableConfig(
        name="DefaultFeatDest",
        store_name="DefaultStore",
        schema_name="DefaultTable",
        table_location=None,
        store_config=DatasetRepositoryConfig.Default(),
        table_schema=FeatureTableSchema.FromFile(schema_name="OGD_EVENTS_FILE")
    )]

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_id:Optional[str],
                 events_from : Optional[List[DataTableConfig]],
                 events_to   : Optional[List[DataTableConfig]],
                 feats_from  : Optional[List[DataTableConfig]],
                 feats_to    : Optional[List[DataTableConfig]],
                 other_elements:Optional[Map]=None):
        """Constructor for the `DataTableConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "source" : "DATA_SOURCE_NAME",
            "database": "db_name",
            "schema" : "TABLE_SCHEMA_NAME",
            "table" : "table_name"
        },
        ```

        :param name: _description_
        :type name: str
        :param game_id: _description_
        :type game_id: Optional[str]
        :param source_name: _description_
        :type source_name: Optional[str]
        :param schema_name: _description_
        :type schema_name: Optional[str]
        :param table_location: _description_
        :type table_location: Optional[DatabaseLocationSchema]
        :param other_elements: _description_
        :type other_elements: Optional[Map]
        """
        unparsed_elements : Map = other_elements or {}

        self._game_id     : str             = game_id     or name
        self._events_from : List[DataTableConfig] = events_from or self._parseEventsFrom(unparsed_elements=unparsed_elements)
        self._events_to   : List[DataTableConfig] = events_to   or self._parseEventsTo(unparsed_elements=unparsed_elements) # TODO : in addition to parsing, fall back on default dest being the standard output to repo at ./data/
        self._feats_from  : List[DataTableConfig] = feats_from  or self._parseFeatsFrom(unparsed_elements=unparsed_elements) # TODO : in addition to parsing, fall back on default source being same store as events, just a different table schema
        self._feats_to    : List[DataTableConfig] = feats_to    or self._parseFeatsTo(unparsed_elements=unparsed_elements) # TODO : in addition to parsing, fall back on default dest being the standard output to repo at ./data/

        super().__init__(name=name, other_elements=other_elements)

    @property
    def GameID(self) -> str:
        """Property to get the Game ID (also called App ID) associated with the given game source

        By convention, this is a human-readable simplification of the games name, in CONSTANT_CASE format

        :return: _description_
        :rtype: str
        """
        return self._game_id

    @property
    def EventsFrom(self) -> List[DataTableConfig]:
        return self._events_from
    @EventsFrom.setter
    def EventsFrom(self, new_list: List[DataTableConfig]) -> None:
        self._events_from = new_list

    @property
    def EventsTo(self) -> List[DataTableConfig]:
        return self._events_to
    @EventsTo.setter
    def EventsTo(self, new_list: List[DataTableConfig]) -> None:
        self._events_to = new_list

    @property
    def FeaturesFrom(self) -> List[DataTableConfig]:
        return self._feats_from
    @FeaturesFrom.setter
    def FeaturesFrom(self, new_list: List[DataTableConfig]) -> None:
        self._feats_from = new_list

    @property
    def FeaturesTo(self) -> List[DataTableConfig]:
        return self._feats_to
    @FeaturesTo.setter
    def FeaturesTo(self, new_list: List[DataTableConfig]) -> None:
        self._feats_to = new_list

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {len(self.EventsFrom)} event sources, {len(self.EventsTo)} event destinations, {len(self.FeaturesFrom)} feature sources, {len(self.FeaturesTo)} feature destinations"
        return ret_val

    @classmethod
    def Default(cls) -> "GameStoreConfig":
        return GameStoreConfig(
            name="DefaultGameStoreConfig",
            game_id=cls._DEFAULT_GAME_ID,
            events_from=cls._DEFAULT_EVENTS_FROM,
            events_to=cls._DEFAULT_EVENTS_TO,
            feats_from=cls._DEFAULT_FEATS_FROM,
            feats_to=cls._DEFAULT_FEATS_TO,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map,
                  key_overrides:Optional[Dict[str, str]]=None,
                  default_override:Optional[Self]=None) -> "GameStoreConfig":
        """Create a DataTableConfig from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.
        TODO : data_sources shouldn't really be a param here. Better to have e.g. a way to register the list into DataTableConfig class, or something.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataStoreConfig]
        :return: _description_
        :rtype: DataTableConfig
        """
        return GameStoreConfig(name=name, game_id=None, events_from=None, events_to=None, feats_from=None, feats_to=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def UpdateStores(self, data_sources:Dict[str, DataStoreConfig]):
        for table_cfg in self.EventsFrom + self.EventsTo + self.FeaturesFrom + self.FeaturesTo:
            _existing_store = data_sources.get(table_cfg.StoreName)
            if _existing_store:
                table_cfg.StoreConfig = _existing_store

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseEventsFrom(unparsed_elements:Map) -> List[DataTableConfig]:
        ret_val : List[DataTableConfig]

        raw_elems = GameStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["events_from"],
            to_type=[list, dict],
            default_value=None,
            remove_target=True
        )
        if isinstance(raw_elems, list):
            ret_val = []
            for config in raw_elems:
                as_dict = conversions.ConvertToType(config, to_type=dict)
                ret_val.append(DataTableConfig.FromDict(name="EventSource", unparsed_elements=as_dict))
        elif isinstance(raw_elems, dict):
            ret_val = [DataTableConfig.FromDict(name="EventSource", unparsed_elements=raw_elems)]
        elif set(unparsed_elements.keys()) == {"source", "database", "table", "schema"}:
            ret_val = [DataTableConfig.FromDict(name="EventSource", unparsed_elements=unparsed_elements)]
        else:
            ret_val = GameStoreConfig._DEFAULT_EVENTS_FROM

        return ret_val

    @staticmethod
    def _parseEventsTo(unparsed_elements:Map) -> List[DataTableConfig]:
        ret_val : List[DataTableConfig] = []

        raw_elems = GameStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["events_to"],
            to_type=list,
            default_value=None,
            remove_target=True
        )
        if isinstance(raw_elems, list):
            for config in raw_elems:
                as_dict = conversions.ConvertToType(config, to_type=dict)
                ret_val.append(DataTableConfig.FromDict(name="EventDestination", unparsed_elements=as_dict))
        elif isinstance(raw_elems, dict):
            ret_val = [DataTableConfig.FromDict(name="EventDestination", unparsed_elements=raw_elems)]
        else:
            ret_val = GameStoreConfig._DEFAULT_EVENTS_TO

        return ret_val

    @staticmethod
    def _parseFeatsFrom(unparsed_elements:Map) -> List[DataTableConfig]:
        ret_val : List[DataTableConfig] = []

        raw_elems = GameStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["feats_from"],
            to_type=list,
            default_value=None,
            remove_target=True
        )
        if isinstance(raw_elems, list):
            for config in raw_elems:
                as_dict = conversions.ConvertToType(config, to_type=dict)
                ret_val.append(DataTableConfig.FromDict(name="FeatureSource", unparsed_elements=as_dict))
        elif isinstance(raw_elems, dict):
            ret_val = [DataTableConfig.FromDict(name="FeatureSource", unparsed_elements=raw_elems)]
        else:
            ret_val = GameStoreConfig._DEFAULT_FEATS_FROM

        return ret_val

    @staticmethod
    def _parseFeatsTo(unparsed_elements:Map) -> List[DataTableConfig]:
        ret_val : List[DataTableConfig] = []

        raw_elems = GameStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["feats_to"],
            to_type=list,
            default_value=None,
            remove_target=True
        )
        if isinstance(raw_elems, list):
            for config in raw_elems:
                as_dict = conversions.ConvertToType(config, to_type=dict)
                ret_val.append(DataTableConfig.FromDict(name="FeatureDestination", unparsed_elements=as_dict))
        elif isinstance(raw_elems, dict):
            ret_val = [DataTableConfig.FromDict(name="FeatureDestination", unparsed_elements=raw_elems)]
        else:
            ret_val = GameStoreConfig._DEFAULT_FEATS_TO

        return ret_val


    # *** PRIVATE METHODS ***
