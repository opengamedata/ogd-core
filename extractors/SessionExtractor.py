# import standard libraries
import logging
import traceback
from typing import Any, List, Dict, IO, Type, Union
# import local files
from utils import Logger
from extractors.Extractor import Extractor
from features.FeatureData import FeatureData
from features.FeatureLoader import FeatureLoader
from features.FeatureRegistry import FeatureRegistry
from games.LAKELAND.LakelandLoader import LakelandLoader
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.Request import ExporterTypes

## @class SessionProcessor
#  Class to extract and manage features for a processed csv file.
class SessionExtractor(Extractor):
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getFeatureNames(self) -> List[str]:
        return self._registry.GetFeatureNames()

    def _getFeatureValues(self, export_types:ExporterTypes, as_str:bool=False) -> Dict[str,List[Any]]:
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

    def _getFeatureData(self, order:int) -> Dict[str, List[FeatureData]]:
        ret_val : Dict[str, List[FeatureData]] = {}
        ret_val["session"] = self._registry.GetFeatureData(order=order, player_id=self._player_id, sess_id=self._session_id)
        return ret_val

    ## Function to handle processing of a single row of data.
    def _processEvent(self, event: Event):
        """Function to handle processing of a single row of data.
        Basically just responsible for ensuring an extractor for the session corresponding
        to the row already exists, then delegating the processing to that extractor.

        :param event: Object with the data for the game event data to be processed.
        :type event: Event
        """
        self._registry.ExtractFromEvent(event)

    def _processFeatureData(self, feature: FeatureData):
        self._registry.ExtractFromFeatureData(feature=feature)

    def _prepareLoader(self) -> FeatureLoader:
        ret_val : FeatureLoader
        if self._LoaderClass is LakelandLoader:
            ret_val = LakelandLoader(player_id=self._player_id, session_id=self._session_id, game_schema=self._game_schema, feature_overrides=self._overrides, output_file=self._session_file)
        else:
            ret_val = self._LoaderClass(player_id=self._player_id, session_id=self._session_id, game_schema=self._game_schema, feature_overrides=self._overrides)
        return ret_val

    # *** PUBLIC BUILT-INS ***

    ## Constructor for the SessionProcessor class.
    def __init__(self, LoaderClass:Type[FeatureLoader], game_schema: GameSchema, player_id:str, session_id:str,
                 feature_overrides:Union[List[str],None]=None, session_file:Union[IO[str],None]=None):
        """Constructor for the SessionProcessor class.
        Simply stores some data for use later, including the type of extractor to
        use.

        :param LoaderClass: The type of data extractor to use for input data.
                            This should correspond to whatever game_id is in the TableSchema.
        :type LoaderClass: Type[FeatureLoader]
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        :param player_id: _description_
        :type player_id: str
        :param session_id: _description_
        :type session_id: str
        :param feature_overrides: _description_, defaults to None
        :type feature_overrides: Union[List[str],None], optional
        :param session_file: _description_, defaults to None
        :type session_file: Union[IO[str],None], optional
        """
        ## Define instance vars
        self._session_file : Union[IO[str],None] = session_file
        self._session_id   : str = session_id
        self._player_id    : str = player_id
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ClearLines(self):
        Logger.Log(f"Clearing features from SessionExtractor.", logging.DEBUG)
        self._registry = FeatureRegistry()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
