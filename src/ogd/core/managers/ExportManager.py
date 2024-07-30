## @package DataToCSV.py
#  A package to handle processing of stuff from our database,
#  for export to CSV files.

## import standard libraries
import logging
import math
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type, Optional

## import local files
from ogd import games
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.managers.EventManager import EventManager
from ogd.core.managers.FeatureManager import FeatureManager
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExportMode import ExportMode
from ogd.core.models.enums.IDMode import IDMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.schemas.configs.ConfigSchema import ConfigSchema
from ogd.core.requests.Request import Request
from ogd.core.requests.RequestResult import RequestResult
from ogd.core.utils.Logger import Logger

Slice = List[str]

## @class ExportManager
#  A class to export features and raw data, given a Request object.
class ExportManager:
    """ExportManager class.
    Use this class to carry out a request for a data export, by passing along an instance of the `Request` class to the ExecuteRequest function.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:ConfigSchema):
        """Constructor for an ExportManager object.
        Simply sets the config for the manager. All other data comes from a request given to the manager.

        :param settings: [description]
        :type settings: [type]
        """
        self._config      : ConfigSchema = config
        self._event_mgr   : Optional[EventManager]   = None
        self._feat_mgr    : Optional[FeatureManager] = None
        self._debug_count : int                      = 0

    def __str__(self):
        return f"ExportManager"

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ExecuteRequest(self, request:Request) -> RequestResult:
        """Carry out the export given by a request.
        Each request has a game id, an interface for getting the data, a data range, the output type(s),
        the locations for output (to file or return value),
        and an optional list of features to override the configured features for a game.

        :param request: [description]
        :type request: Request
        :return: [description]
        :rtype: Dict[str,Any]
        """
        ret_val : RequestResult = RequestResult(msg="No Export")

        Logger.Log(f"Executing request: {str(request)}", logging.INFO)
        start = datetime.now()
        try:
        # 1. Pre-processing
            Logger.Log(f"Setting up file, event, and feature managers as pre-processing...", logging.INFO)
            self._preProcess(request=request)
            Logger.Log(f"Done", logging.INFO)
            Logger.Log(f"Executing...", logging.INFO)
            _sess_ids : List[str] = request.RetrieveIDs() or []
            for outerface in request.Outerfaces:
                outerface.SessionCount = len(_sess_ids)

        # 2. Process slices
            Logger.Log(f"Preparing to process {len(_sess_ids)} sessions...", logging.INFO, depth=1)
            self._processSlices(request=request, ids=_sess_ids)
            Logger.Log(f"Done", logging.INFO, depth=1)

        # 3. Output population/player features as post-slicing data.
            Logger.Log(f"Outputting post-process data...", logging.INFO, depth=2)
            self._postProcess(request=request)
            Logger.Log(f"Done", logging.INFO)

            ret_val.SessionCount = len(_sess_ids)
            ret_val.RequestSucceeded(msg=f"Successfully executed data request {request}.")
        except ValueError as err:
            msg = f"Failed to execute data request {str(request)}, an invalid value was found:\n{str(err)}\n{traceback.format_exc()}"
            ret_val.RequestErrored(msg=msg)
        except Exception as err:
            msg = f"Failed to execute data request {str(request)}, an unexpected error occurred:\n{type(err)} {str(err)}\n{traceback.format_exc()}"
            ret_val.RequestErrored(msg=msg)
        finally:
            time_delta = datetime.now() - start
            ret_val.Duration = time_delta
            return ret_val

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _receiveEventTrigger(self, event:Event) -> None:
        # TODO: consider how to put a limit on times this runs, based on how big export is.
        if self._debug_count < 5:
            Logger.Log(f"{self} received an event trigger.", logging.DEBUG)
            self._debug_count += 1
        self._processEvent(next_event=event)

    def _preProcess(self, request:Request) -> None:
        """
        Pre-processing of request, setting up required components before we retrieve session data.

        In particular, this function:
        1. Sets up loader class
        2. Sets up event manager
        3. Sets up feature manager
        4. Opens request outerfaces
        :param request: The export request being processed
        :type request: Request
        """
        _games_path  = Path(games.__file__) if Path(games.__file__).is_dir() else Path(games.__file__).parent
        _game_schema  : GameSchema  = GameSchema.FromFile(game_id=request.GameID, schema_path=_games_path / request.GameID / "schemas")
    # 1. Get LoaderClass
        load_class = ExportManager._loadLoaderClass(request.GameID)
        if load_class is None:
            # If game doesn't have an extractor, make sure we don't try to export it.
            request.RemoveExportMode(ExportMode.DETECTORS)
            request.RemoveExportMode(ExportMode.SESSION)
            request.RemoveExportMode(ExportMode.PLAYER)
            request.RemoveExportMode(ExportMode.POPULATION)

    # 2. Set up EventManager, assuming it was requested.
        if request.ExportRawEvents or request.ExportProcessedEvents:
            self._event_mgr = EventManager(game_schema=_game_schema, LoaderClass=load_class,
                                           trigger_callback=self._receiveEventTrigger, feature_overrides=request._feat_overrides)
        else:
            Logger.Log("Event data not requested, skipping event manager.", logging.INFO, depth=1)
    # 3. Set up FeatureManager, assuming it was requested.
        if request.ExportSessions or request.ExportPlayers or request.ExportPopulation:
            self._feat_mgr = FeatureManager(game_schema=_game_schema, LoaderClass=load_class, feature_overrides=request._feat_overrides)
        else:
            Logger.Log("Feature data not requested, or extractor loader unavailable, skipping feature manager.", logging.INFO, depth=1)
    # 4. Open the outerfaces
        for outerface in request.Outerfaces:
            outerface.Open()
        self._outputHeaders(request=request)

    def _processSlices(self, request:Request, ids:List[str]) -> None:
        start  : datetime
        slices : List[Slice] = self._generateSlices(sess_ids=ids)

        _next_slice_data : Optional[List[Event]] = None
        for i, next_slice_ids in enumerate(slices):
            _next_slice_data = self._loadSlice(request=request, next_slice_ids=next_slice_ids, slice_num=i+1, slice_count=len(slices))
            if _next_slice_data is not None:
            # 1. Process the slice.
                start = datetime.now()
                Logger.Log(f"Processing slice [{i+1}/{len(slices)}]...", logging.INFO, depth=2)
                self._processSlice(next_slice_data=_next_slice_data, request=request, ids=ids)
                time_delta = datetime.now() - start
                Logger.Log(f"Processing time for slice [{i+1}/{len(slices)}]: {time_delta} to handle {len(_next_slice_data)} events", logging.INFO, depth=2)

            # 2. Write out the session data and reset for next slice.
                start = datetime.now()
                Logger.Log(f"Outputting slice [{i+1}/{len(slices)}]...", logging.INFO, depth=2)
                self._outputSlice(request=request, slice_num=i+1, slice_count=len(slices))
                time_delta = datetime.now() - start
                Logger.Log(f"Output time for slice [{i+1}/{len(slices)}]: {time_delta} to handle {len(_next_slice_data)} events", logging.INFO, depth=2)

    def _postProcess(self, request:Request):
        start = datetime.now()
        if self._feat_mgr is not None:
            if request.ExportPopulation:
                _pop_feats = self._feat_mgr.GetPopulationFeatures(as_str=True)
                for outerface in request.Outerfaces:
                    outerface.WriteLines(lines=_pop_feats, mode=ExportMode.POPULATION)
                self._feat_mgr.ClearPopulationLines()
            if request.ExportPlayers:
                _player_feats = self._feat_mgr.GetPlayerFeatures(as_str=True)
                for outerface in request.Outerfaces:
                    outerface.WriteLines(lines=_player_feats, mode=ExportMode.PLAYER)
                self._feat_mgr.ClearPlayerLines()
        else:
            Logger.Log(f"Skipping feature output for post-process, no FeatureManager exists!", logging.DEBUG, depth=3)
        time_delta = datetime.now() - start
        Logger.Log(f"Output time for population: {time_delta}", logging.INFO, depth=2)

    @staticmethod
    def _loadLoaderClass(game_id:str) -> Optional[Type[GeneratorLoader]]:
        _loader_class: Optional[Type[GeneratorLoader]] = None
        match game_id:
            case "AQUALAB":
                from ogd.games.AQUALAB.AqualabLoader import AqualabLoader
                _loader_class = AqualabLoader
            case "CRYSTAL":
                from ogd.games.CRYSTAL.CrystalLoader import CrystalLoader
                _loader_class = CrystalLoader
            case "ICECUBE":
                from ogd.games.ICECUBE.IcecubeLoader import IcecubeLoader
                _loader_class = IcecubeLoader
            case "JOURNALISM":
                from ogd.games.JOURNALISM.JournalismLoader import JournalismLoader
                _loader_class = JournalismLoader
            case "JOWILDER":
                from ogd.games.JOWILDER.JowilderLoader import JowilderLoader
                _loader_class = JowilderLoader
            case "LAKELAND":
                from ogd.games.LAKELAND.LakelandLoader import LakelandLoader
                _loader_class = LakelandLoader
            case "MAGNET":
                from ogd.games.MAGNET.MagnetLoader import MagnetLoader
                _loader_class = MagnetLoader
            case "SHADOWSPECT":
                from ogd.games.SHADOWSPECT.ShadowspectLoader import ShadowspectLoader
                _loader_class = ShadowspectLoader
            case "SHIPWRECKS":
                from ogd.games.SHIPWRECKS.ShipwrecksLoader import ShipwrecksLoader
                _loader_class = ShipwrecksLoader
            case "THERMOVR":
                from ogd.games.THERMOVR.ThermoVRLoader import ThermoVRLoader
                _loader_class = ThermoVRLoader
            case "WAVES":
                from ogd.games.WAVES.WaveLoader import WaveLoader
                _loader_class = WaveLoader
            case "PENGUINS":
                from ogd.games.PENGUINS.PenguinsLoader import PenguinsLoader
                _loader_class = PenguinsLoader
            case "BLOOM":
                from ogd.games.BLOOM.BloomLoader import BloomLoader
                _loader_class = BloomLoader
            case _:
                if game_id in {"BACTERIA", "BALLOON", "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE", "MASHOPOLIS", "WEATHER_STATION", "WIND"}:
                    # all games with data but no extractor.
                    pass
                else:
                    raise ValueError(f"Got an unrecognized game ID ({game_id})!")
        return _loader_class

    def _generateSlices(self, sess_ids:List[str]) -> List[Slice]:
        """
        Convert session ID list into slices of size `self._config.BatchSize.`

        Each slice is just a list of session IDs.
        :param sess_ids: The list of all session IDs in the request.
        :type sess_ids: List[str]
        :return: A list of ID blocks (slices).
        :rtype: List[Slice]
        """
        _num_sess = len(sess_ids)
        _slice_size = self._config.BatchSize
        Logger.Log(f"With slice size = {_slice_size}, there are {math.ceil(_num_sess / _slice_size)} slices", logging.INFO, depth=1)
        return [[sess_ids[i] for i in range( j*_slice_size, min((j+1)*_slice_size, _num_sess) )]
                             for j in range( 0, math.ceil(_num_sess / _slice_size) )]

    def _loadSlice(self, request:Request, next_slice_ids:List[str], slice_num:int, slice_count:int) -> Optional[List[Event]]:
        ret_val : Optional[List[Event]]

        Logger.Log(f"Retrieving slice [{slice_num}/{slice_count}]...", logging.INFO, depth=2)
        start : datetime = datetime.now()
        # TODO : Add a way to configure what to exclude at higher level, here. So we can easily choose to leave out certain events.
        _exclude_rows = None
        # HACK : setting to skip algae events here directly
        if request.GameID == 'BLOOM':
            _exclude_rows = ['algae_growth_end', 'algae_growth_begin']
        ret_val = request.Interface.EventsFromIDs(id_list=next_slice_ids, id_mode=request.Range.IDMode, exclude_rows=_exclude_rows)
        time_delta = datetime.now() - start
        if ret_val is not None:
            Logger.Log(f"Retrieval time for slice [{slice_num}/{slice_count}]: {time_delta} to get {len(ret_val)} events", logging.INFO, depth=2)
        else:
            Logger.Log(f"Could not retrieve data set for slice [{slice_num}/{slice_count}].", logging.WARN, depth=2)
        return ret_val

    def _processSlice(self, next_slice_data:List[Event], request: Request, ids:List[str]):
        _unsessioned_event_count : int = 0
        _sampled_an_event = False
        # 3a) If next slice yielded valid data from the interface, process row-by-row.
        # TODO: instead of separating everything out into one call per event, turn this into a list comprehension using a validation function, so we can pass whole list down a level.
        for event in next_slice_data:
            if not _sampled_an_event:
                Logger.Log(f"First event of slice is:\n{event}", logging.DEBUG, depth=2)
                _sampled_an_event = True
            if (request._range._id_mode==IDMode.SESSION and event.SessionID in ids) \
            or (request._range._id_mode==IDMode.USER    and event.UserID    in ids):
                self._processEvent(next_event=event)
            elif event.SessionID is not None and event.SessionID.upper() != "NONE":
                Logger.Log(f"Found a session ({event.SessionID}, type {type(event.SessionID)}) which was in the slice but not in the list of sessions for processing ({ids[:5]}..., type {type(ids[0])}).", logging.WARNING, depth=2)
            elif event.UserID is not None and event.UserID.upper() != "NONE":
                Logger.Log(f"Found a user ({event.UserID}) which was in the slice but not in the list of players for processing.", logging.WARNING, depth=2)
            else:
                _unsessioned_event_count += 1
                if _unsessioned_event_count < 10:
                    Logger.Log(f"Found an event with no session/player ID, event is: {event}", logging.WARNING, depth=2)
        if _unsessioned_event_count > 0:
            Logger.Log(f"Found {_unsessioned_event_count} events without session IDs.", logging.WARNING, depth=2)

    def _processEvent(self, next_event:Event):
        try:
            if self._event_mgr is not None:
                self._event_mgr.ProcessEvent(event=next_event)
            if self._feat_mgr is not None:
                self._feat_mgr.ProcessEvent(event=next_event)
        except Exception as err:
            if self._config.FailFast:
                Logger.Log(f"Error while processing event {next_event.EventName}:\n{next_event}", logging.ERROR, depth=2)
                raise err
            else:
                Logger.Log(f"Error while processing event {next_event.EventName}. This event will be skipped. \nFull error: {traceback.format_exc()}", logging.WARNING, depth=2)

    def _outputHeaders(self, request:Request):
        if self._event_mgr is not None:
            if request.ExportRawEvents:
                cols = self._event_mgr.GetColumnNames()
                for outerface in request.Outerfaces:
                    outerface.WriteHeader(header=cols, mode=ExportMode.EVENTS)
            else:
                Logger.Log("Event log not requested, skipping events output.", logging.INFO, depth=1)
            if request.ExportProcessedEvents:
                cols = self._event_mgr.GetColumnNames()
                for outerface in request.Outerfaces:
                    outerface.WriteHeader(header=cols, mode=ExportMode.DETECTORS)
            else:
                Logger.Log("Event log not requested, skipping events output.", logging.INFO, depth=1)
        if self._feat_mgr is not None:
            if request.ExportSessions:
                cols = self._feat_mgr.GetSessionFeatureNames()
                for outerface in request.Outerfaces:
                    outerface.WriteHeader(header=cols, mode=ExportMode.SESSION)
            else:
                Logger.Log("Session features not requested, skipping session_features file.", logging.INFO, depth=1)
            if request.ExportPlayers:
                cols = self._feat_mgr.GetPlayerFeatureNames()
                for outerface in request.Outerfaces:
                    outerface.WriteHeader(header=cols, mode=ExportMode.PLAYER)
            else:
                Logger.Log("Player features not requested, skipping player_features file.", logging.INFO, depth=1)
            if request.ExportPopulation:
                cols = self._feat_mgr.GetPopulationFeatureNames()
                for outerface in request.Outerfaces:
                    outerface.WriteHeader(header=cols, mode=ExportMode.POPULATION)
            else:
                Logger.Log("Population features not requested, skipping population_features file.", logging.INFO, depth=1)

    def _outputSlice(self, request:Request, slice_num:int, slice_count:int):
        """
        Output all genearted data for a slice's-worth of raw data

        TODO : Find better solution that does not involve discarding session features, which likely messes up some second-order features.
        :param request: _description_
        :type request: Request
        :param slice_num: _description_
        :type slice_num: int
        :param slice_count: _description_
        :type slice_count: int
        """
        if self._event_mgr is not None:
        # 1. Output raw events, if requested
            if request.ExportRawEvents:
                _events = self._event_mgr.GetRawLines(slice_num=slice_num, slice_count=slice_count)
                for outerface in request.Outerfaces:
                    outerface.WriteLines(lines=_events, mode=ExportMode.EVENTS)
        # 2. Output combined raw & detected events, if requested
            if request.ExportProcessedEvents:
                _events = self._event_mgr.GetAllLines(slice_num=slice_num, slice_count=slice_count)
                for outerface in request.Outerfaces:
                    outerface.WriteLines(lines=_events, mode=ExportMode.DETECTORS)
            self._event_mgr.ClearLines()
        else:
            Logger.Log(f"Skipping event output for slice [{slice_num}/{slice_count}], no EventManager exists!", logging.DEBUG, depth=3)
        if self._feat_mgr is not None:
        # 3. Output session features, if requested
            if request.ExportSessions:
                _sess_feats = self._feat_mgr.GetSessionFeatures(slice_num=slice_num, slice_count=slice_count, as_str=True)
                for outerface in request.Outerfaces:
                    outerface.WriteLines(lines=_sess_feats, mode=ExportMode.SESSION)
                self._feat_mgr.ClearSessionLines()
        else:
            Logger.Log(f"Skipping feature output for slice [{slice_num}/{slice_count}], no FeatureManager exists!", logging.DEBUG, depth=3)
