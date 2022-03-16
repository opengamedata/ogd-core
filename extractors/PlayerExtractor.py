# import standard libraries
import logging
import traceback
from typing import Any, List, Dict, IO, Type, Union
# import local files
import utils
from extractors.Extractor import Extractor
from extractors.FeatureLoader import FeatureLoader
from extractors.FeatureLoader import FeatureLoader
from extractors.FeatureRegistry import FeatureRegistry
from extractors.SessionExtractor import SessionExtractor
from features.FeatureData import FeatureData
from games.LAKELAND.LakelandLoader import LakelandLoader
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.Request import ExporterTypes

## @class PlayerProcessor
#  Class to extract and manage features for a processed csv file.
class PlayerExtractor(Extractor):
    ## Constructor for the PlayerProcessor class.
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
    def __init__(self, LoaderClass: Type[FeatureLoader], game_schema: GameSchema, player_id:str,
                 feature_overrides:Union[List[str],None]=None, player_file:Union[IO[str],None]=None):
        self._player_file : Union[IO[str],None] = player_file
        self._player_id   : str                 = player_id
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        ## Define instance vars
        self._session_extractors : Dict[str,SessionExtractor] = {
            "null" : SessionExtractor(LoaderClass=LoaderClass, game_schema=game_schema,
                                      player_id=self._player_id, session_id="null",
                                      feature_overrides=feature_overrides, session_file=player_file)
        }

    def _prepareLoader(self) -> FeatureLoader:
        ret_val : FeatureLoader
        if self._LoaderClass is LakelandLoader:
            ret_val = LakelandLoader(player_id=self._player_id, session_id="player", game_schema=self._game_schema, feature_overrides=self._overrides, output_file=self._player_file)
        else:
            ret_val = self._LoaderClass(player_id=self._player_id, session_id="player", game_schema=self._game_schema, feature_overrides=self._overrides)
        return ret_val

    ## Function to handle processing of a single row of data.
    #  Basically just responsible for ensuring an extractor for the session
    #  corresponding to the row already exists, then delegating the processing
    #  to that extractor.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessEvent(self, event:Event):
        self._registry.ExtractFromEvent(event=event)
        # ensure we have an extractor for the given session:
        if event.session_id not in self._session_extractors.keys():
            self._session_extractors[event.session_id] = SessionExtractor(LoaderClass=self._LoaderClass, game_schema=self._game_schema,
                                                                          player_id=self._player_id, session_id=event.session_id,
                                                                          feature_overrides=self._overrides, session_file=self._player_file)

        self._session_extractors[event.session_id].ProcessEvent(event=event)

    def ProcessFeatureData(self, feature: FeatureData):
        self._registry.ExtractFromFeatureData(feature=feature)
        # Down-propogate values to player (and, by extension, session) features:
        for session in self._session_extractors.values():
            session.ProcessFeatureData(feature=feature)

    def SessionCount(self):
        return len(self._session_extractors.keys()) - 1 # don't count null player

    def GetFeatureNames(self) -> List[str]:
        return self._registry.GetFeatureNames() + ["SessionCount"]
    def GetSessionFeatureNames(self) -> List[str]:
        return self._session_extractors["null"].GetFeatureNames()

    def GetFeatureValues(self, export_types:ExporterTypes, as_str:bool=False) -> Dict[str, List[Any]]:
        ret_val : Dict[str, List[Any]] = {}
        if export_types.players:
            _sess_ct = self.SessionCount()
            if as_str:
                ret_val["player"] = self._registry.GetFeatureStringValues() + [str(_sess_ct)]
            else:
                ret_val["player"] = self._registry.GetFeatureValues() + [_sess_ct]
        if export_types.sessions:
            # _results gives us a list of dicts, each with a "session" element
            _results = [sess_extractor.GetFeatureValues(export_types=export_types, as_str=as_str) for sess_extractor in self._session_extractors.values()]
            ret_val["sessions"] = []
            # so we loop over list, and pull each "session" element into a master list of all sessions.
            for session in _results:
                ret_val["sessions"].append(session["session"])
            # finally, what we return is a dict with a "sessions" element, containing list of lists.
        return ret_val

    def GetFeatureData(self, order:int) -> Dict[str, List[FeatureData]]:
        ret_val : Dict[str, List[FeatureData]] = {}
        ret_val["player"] = self._registry.GetFeatureData(order=order)
        _result = [session_extractor.GetFeatureData(order=order) for session_extractor in self._session_extractors.values()]
        ret_val["sessions"] = []
        for session in _result:
            ret_val["sessions"] += session['session']
        return ret_val

    ##  Function to empty the list of lines stored by the PlayerProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def ClearLines(self):
        utils.Logger.Log(f"Clearing features from PlayerExtractor.", logging.DEBUG)
        self._registry = FeatureRegistry()

    def ClearSessionsLines(self):
        utils.Logger.Log(f"Clearing {len(self._session_extractors)} sessions from PlayerProcessor.", logging.DEBUG)
        self._session_extractors = {}