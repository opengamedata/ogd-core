# import standard libraries
import logging
import traceback
from typing import Any, List, Dict, IO, Type, Optional
# import local files
from utils import Logger
from extractors.ExtractorRegistry import ExtractorRegistry
from extractors.ExtractorLoader import ExtractorLoader
from features.FeatureRegistry import FeatureRegistry
from processors.FeatureProcessor import FeatureProcessor
from processors.SessionProcessor import SessionProcessor
from schemas.FeatureData import FeatureData
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.Request import ExporterTypes

## @class PlayerProcessor
#  Class to extract and manage features for a processed csv file.
class PlayerProcessor(FeatureProcessor):

    # *** PUBLIC BUILT-INS ***

    ## Constructor for the PlayerProcessor class.
    def __init__(self, LoaderClass: Type[ExtractorLoader], game_schema: GameSchema, player_id:str,
                 feature_overrides:Optional[List[str]]=None):
        """Constructor for the PlayerProcessor class.
           Simply stores some data for use later, including the type of extractor to use.

        :param LoaderClass: The type of data extractor to use for input data.
                            This should correspond to whatever game_id is in the TableSchema.
        :type LoaderClass: Type[ExtractorLoader]
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        :param player_id: _description_
        :type player_id: str
        :param feature_overrides: _description_, defaults to None
        :type feature_overrides: Union[List[str],None], optional
        :param player_file: _description_, defaults to None
        :type player_file: Optional[IO[str]], optional
        """
        Logger.Log(f"Setting up PlayerProcessor for {player_id}...", logging.DEBUG, depth=2)
        self._player_id   : str                 = player_id
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        ## Define instance vars
        self._session_processors : Dict[str,SessionProcessor] = {
            "null" : SessionProcessor(LoaderClass=LoaderClass, game_schema=game_schema,
                                      player_id=self._player_id, session_id="null",
                                      feature_overrides=feature_overrides)
        }
        Logger.Log(f"Done", logging.DEBUG, depth=2)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _prepareLoader(self) -> ExtractorLoader:
        return self._LoaderClass(player_id=self._player_id, session_id="player",
                                 game_schema=self._game_schema, feature_overrides=self._overrides)

    def _getExtractorNames(self) -> List[str]:
        if isinstance(self._registry, FeatureRegistry):
            return self._registry.GetExtractorNames() + ["SessionCount"]
        else:
            raise TypeError()

    ## Function to handle processing of a single row of data.
    def _processEvent(self, event:Event):
        """Function to handle processing of a single row of data.
        Basically just responsible for ensuring an extractor for the session corresponding
        to the row already exists, then delegating the processing to that extractor.
        :param event: An object with the data for the event to be processed.
        :type event: Event
        """
        self._registry.ExtractFromEvent(event=event)
        # ensure we have an extractor for the given session:
        if event.session_id not in self._session_processors.keys():
            self._session_processors[event.session_id] = SessionProcessor(LoaderClass=self._LoaderClass, game_schema=self._game_schema,
                                                                          player_id=self._player_id, session_id=event.session_id,
                                                                          feature_overrides=self._overrides)

        self._session_processors[event.session_id].ProcessEvent(event=event)

    def _processFeatureData(self, feature: FeatureData):
        self._registry.ExtractFromFeatureData(feature=feature)
        # Down-propogate values to player (and, by extension, session) features:
        for session in self._session_processors.values():
            session.ProcessFeatureData(feature=feature)

    def _getFeatureValues(self, export_types:ExporterTypes, as_str:bool=False) -> Dict[str, List[Any]]:
        ret_val : Dict[str, List[Any]] = {}
        if export_types.players and isinstance(self._registry, FeatureRegistry):
            _sess_ct = self.SessionCount()
            if as_str:
                ret_val["players"] = self._registry.GetFeatureStringValues() + [str(_sess_ct)]
            else:
                ret_val["players"] = self._registry.GetFeatureValues() + [_sess_ct]
        if export_types.sessions:
            # _results gives us a list of dicts, each with a "session" element
            _results = [sess_extractor.GetFeatureValues(export_types=export_types, as_str=as_str) for sess_extractor in self._session_processors.values()]
            ret_val["sessions"] = []
            # so we loop over list, and pull each "session" element into a master list of all sessions.
            for session in _results:
                ret_val["sessions"].append(session["sessions"])
            # finally, what we return is a dict with a "sessions" element, containing list of lists.
        return ret_val

    def _getFeatureData(self, order:int) -> Dict[str, List[FeatureData]]:
        ret_val : Dict[str, List[FeatureData]] = { "players":[] }
        if isinstance(self._registry, FeatureRegistry):
            ret_val["players"] = self._registry.GetFeatureData(order=order)
        _result = [session_extractor.GetFeatureData(order=order) for session_extractor in self._session_processors.values()]
        ret_val["sessions"] = []
        for session in _result:
            ret_val["sessions"] += session['sessions']
        return ret_val

    ##  Function to empty the list of lines stored by the PlayerProcessor.
    def _clearLines(self) -> None:
        """Function to empty the list of lines stored by the PlayerProcessor.
        This is helpful if we're processing a lot of data and want to avoid eating too much memory.
        """
        Logger.Log(f"Clearing features from PlayerProcessor for {self._player_id}.", logging.DEBUG, depth=2)
        self._registry = FeatureRegistry()

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def SessionCount(self):
        return len(self._session_processors.keys()) - 1 # don't count null player

    def GetSessionFeatureNames(self) -> List[str]:
        return self._session_processors["null"].GetExtractorNames()

    def ClearSessionsLines(self):
        Logger.Log(f"Clearing {len(self._session_processors)} sessions from PlayerProcessor for {self._player_id}.", logging.DEBUG, depth=2)
        self._session_processors = {}

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
