# import standard libraries
import logging
import traceback
from typing import Any, List, Dict, IO, Type, Union
# import local files
import utils
from extractors.Extractor import Extractor
from extractors.FeatureLoader import FeatureLoader
from extractors.FeatureRegistry import FeatureRegistry
from features.FeatureData import FeatureData
from games.LAKELAND.LakelandLoader import LakelandLoader
from managers.Request import ExporterTypes
from schemas.Event import Event
from schemas.GameSchema import GameSchema

## @class SessionProcessor
#  Class to extract and manage features for a processed csv file.
class SessionExtractor(Extractor):
    ## Constructor for the SessionProcessor class.
    #  Simply stores some data for use later, including the type of extractor to
    #  use.
    #
    #  @param ExtractorClass The type of data extractor to use for input data.
    #         This should correspond to whatever game_id is in the TableSchema.
    #  @param game_table    A data structure containing information on how the db
    #                       table assiciated with the given game is structured. 
    #  @param game_schema   A dictionary that defines how the game data itself
    #                       is structured.
    #  @param sessions_csv_file The output file, to which we'll write the processed
    #                       feature data.
    def __init__(self, LoaderClass:Type[FeatureLoader], game_schema: GameSchema, player_id:str, session_id:str,
                 feature_overrides:Union[List[str],None]=None, session_file:Union[IO[str],None]=None):
        ## Define instance vars
        self._session_file : Union[IO[str],None] = session_file
        self._session_id   : str = session_id
        self._player_id    : str = player_id
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)

    def _prepareLoader(self) -> FeatureLoader:
        ret_val : FeatureLoader
        if self._LoaderClass is LakelandLoader:
            ret_val = LakelandLoader(player_id=self._player_id, session_id=self._session_id, game_schema=self._game_schema, feature_overrides=self._overrides, output_file=self._session_file)
        else:
            ret_val = self._LoaderClass(player_id=self._player_id, session_id=self._session_id, game_schema=self._game_schema, feature_overrides=self._overrides)
        return ret_val

    ## Function to handle processing of a single row of data.
    #  Basically just responsible for ensuring an extractor for the session
    #  corresponding to the row already exists, then delegating the processing
    #  to that extractor.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessEvent(self, event: Event):
        self._registry.ExtractFromEvent(event)

    def ProcessFeatureData(self, feature: FeatureData):
        self._registry.ExtractFromFeatureData(feature=feature)

    def GetFeatureNames(self) -> List[str]:
        return self._registry.GetFeatureNames()

    def GetFeatureValues(self, export_types:ExporterTypes, as_str:bool=False) -> Dict[str,List[Any]]:
        # 1) First, we get Session's first-order feature data:
        _first_order_data : Dict[str, List[FeatureData]] = self.GetFeatureData(order=FeatureRegistry.FeatureOrders.FIRST_ORDER.value)
        # 2) Then we can side-propogate the values to second-order features, and down-propogate to other extractors:
        for feature in _first_order_data['session']:
            self.ProcessFeatureData(feature=feature)
        # 3) Finally, we assume higher-ups have already sent down their first-order features, so we are ready to return all feature values.
        if export_types.sessions:
            if as_str:
                return {"session" : self._registry.GetFeatureStringValues()}
            else:
                return {"session" : self._registry.GetFeatureValues()}
        else:
            return {}

    def GetFeatureData(self, order:int) -> Dict[str, List[FeatureData]]:
        ret_val : Dict[str, List[FeatureData]] = {}
        ret_val["session"] = self._registry.GetFeatureData(order=order, player_id=self._player_id, sess_id=self._session_id)
        return ret_val

    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing features from SessionExtractor.", logging.DEBUG)
        self._registry = FeatureRegistry()