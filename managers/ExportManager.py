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
from pprint import pformat
from typing import Any, Dict, List, Tuple, Union

from matplotlib.pyplot import table
from managers.ExtractorManager import ExtractorManager
## import local files
from utils import Logger
from config.config import settings as default_settings
from managers.FileManager import FileManager
from managers.EventManager import EventManager
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema
from schemas.Request import Request

## @class ExportManager
#  A class to export features and raw data, given a Request object.
class ExportManager:
    """ExportManager class.
    Use this class to carry out a request for a data export, by passing along an instance of the `Request` class to the ExecuteRequest function.
    """

    # *** PUBLIC BUILT-INS ***

    def __init__(self, settings):
        """Constructor for an ExportManager object.
        Simply sets the settings for the manager. All other data comes from a request given to the manager.

        :param settings: [description]
        :type settings: [type]
        """
        self._settings = settings
        self._event_mgr   : Union[EventManager, None]     = None
        self._extract_mgr : Union[ExtractorManager, None] = None
        self._file_mgr    : Union[FileManager, None]      = None

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ExecuteRequest(self, request:Request) -> Dict[str,Any]:
        """Carry out the export given by a request.
        Each request has a game id, an interface for getting the data, a data range, the output type(s),
        the locations for output (to file or return value),
        and an optional list of features to override the configured features for a game.

        :param request: [description]
        :type request: Request
        :return: [description]
        :rtype: Dict[str,Any]
        """
        ret_val : Dict[str,Any] = {"success":False}

        _game_id      : str         = request.GetGameID()
        _game_schema  : GameSchema  = GameSchema(schema_name=_game_id, schema_path=Path(f"./games/{_game_id}"))
        _table_schema : TableSchema = self._loadTableSchema(_game_id)

        Logger.Log(f"Executing request: {str(request)}", logging.INFO)
        start = datetime.now()
        try:
            Logger.Log(f"Preparing managers...", logging.DEBUG)
            self._prepareManagers(request=request, game_schema=_game_schema, feature_overrides=request._feat_overrides)
            Logger.Log(f"Done", logging.DEBUG)

            if request.ToFile():
                Logger.Log(f"File output requested, setting up file manager...", logging.DEBUG)
                self._prepareFileManager(request=request)
                Logger.Log(f"Done", logging.DEBUG)

            Logger.Log(f"Executing...", logging.DEBUG)
            _result = self._executeDataRequest(request=request, table_schema=_table_schema, file_manager=self._file_manager)
            Logger.Log(f"Done", logging.DEBUG)
            num_sess : int = _result.get("sessions_ct", 0)

            Logger.Log(f"Saving output...", logging.DEBUG)
            if request.ToFile() and self._file_manager is not None:
                # 4) Save and close files
                self._closeFiles(game_schema=_game_schema, table_schema=_table_schema, num_sess=num_sess)
            if request.ToDict():
                ret_val.update(_result) # merge event, session, player, and population data into the return value.
            Logger.Log(f"Done", logging.DEBUG)
            Logger.Log(f"Successfully executed data request {str(request)}.", logging.INFO)
            ret_val['success'] = True # if we made it to end, we were successful.
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            Logger.Log(f"Failed to execute data request {str(request)}, an error occurred:\n{msg}", logging.ERROR)
            traceback.print_tb(err.__traceback__)
        finally:
            time_delta = datetime.now() - start
            Logger.Log(f"Total data request execution time: {time_delta}", logging.INFO)
            return ret_val

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _loadTableSchema(self, _game_id:str):
        if "GAME_SOURCE_MAP" in self._settings:
            _table_name = self._settings["GAME_SOURCE_MAP"][_game_id]["table"]
        else:
            _table_name = default_settings["GAME_SOURCE_MAP"][_game_id]["table"]
        return TableSchema(schema_name=f"{_table_name}.json")

    def _prepareManagers(self, request:Request, game_schema:GameSchema, feature_overrides:Union[List[str],None]):
        if request.ExportEvents():
            self._event_mgr = EventManager()
        # If game doesn't have an extractor, make sure we don't try to export it.
        if request.ExportSessions() or request.ExportPlayers() or request.ExportPopulation():
            self._extract_mgr = ExtractorManager(game_id=request.GetGameID(), exp_types=request._exports,
                                                       game_schema=game_schema, feature_overrides=feature_overrides)
            if not self._extract_mgr.HasLoader():
                request._exports.sessions   = False
                request._exports.players    = False
                request._exports.population = False
                Logger.Log("Could not extract feature data, no game extractor given!", logging.WARNING, depth=1)

    def _prepareFileManager(self, request:Request):
        _data_dir : str = self._settings["DATA_DIR"] or default_settings["DATA_DIR"]
        self._file_manager = FileManager(request=request, data_dir=_data_dir, extension="tsv")
        self._file_manager.OpenFiles()
        if self._event_mgr is not None:
            if request.ExportEvents():
                cols = self._event_mgr.GetColumnNames()
                self._file_manager.WriteEventsFile("\t".join(cols) + "\n")
            else:
                Logger.Log("Event log not requested, skipping events file.", logging.INFO, depth=1)
        if self._extract_mgr is not None:
            if request.ExportPopulation():
                cols = self._extract_mgr.GetPopulationFeatureNames()
                self._file_manager.WritePopulationFile("\t".join(cols) + "\n")
            else:
                Logger.Log("Population features not requested, skipping population_features file.", logging.INFO, depth=1)
            if request.ExportPlayers():
                cols = self._extract_mgr.GetPlayerFeatureNames()
                self._file_manager.WritePlayersFile("\t".join(cols) + "\n")
            else:
                Logger.Log("Player features not requested, skipping player_features file.", logging.INFO, depth=1)
            if request.ExportSessions():
                cols = self._extract_mgr.GetSessionFeatureNames()
                self._file_manager.WriteSessionsFile("\t".join(cols) + "\n")
            else:
                Logger.Log("Session features not requested, skipping session_features file.", logging.INFO, depth=1)

    def _executeDataRequest(self, request:Request, table_schema:TableSchema, file_manager:Union[FileManager, None]=None) -> Dict[str,Any]:
        ret_val       : Dict[str,Any]           = {"events":None, "sessions":None, "players":None, "population":None, "sessions_ct":0}
        next_data_set : Union[List[Tuple],None] = None

        if request.ToDict():
            if request.ExportEvents() and self._event_mgr is not None:
                ret_val['events'] = {"cols":self._event_mgr.GetColumnNames(), "vals":[]}
            if self._extract_mgr is not None:
                if request.ExportSessions():
                    ret_val['sessions'] = {"cols":self._extract_mgr.GetSessionFeatureNames(), "vals":[]}
                if request.ExportPlayers():
                    ret_val['players'] = {"cols":self._extract_mgr.GetPlayerFeatureNames(), "vals":[]}
                if request.ExportPopulation():
                    ret_val['population'] = {"cols":self._extract_mgr.GetPopulationFeatureNames(), "vals":[]}
        # 1) Get the IDs of sessions to process
        sess_ids = request.RetrieveIDs() or []
        ret_val["sessions_ct"] = len(sess_ids)
        Logger.Log(f"Preparing to process {len(sess_ids)} sessions.", logging.INFO, depth=1)
        _session_slices : List[List[str]] = self._generateSlices(sess_ids=sess_ids)
        # 2) Loop over and process the sessions, slice-by-slice (where each slice is a list of sessions).
        for i, next_slice in enumerate(_session_slices):
            next_data_set = self._getSlice(request=request, next_slice=next_slice, slice_num=i+1, slice_count=len(_session_slices))
            if next_data_set is not None:
                self._processSlice(next_data_set=next_data_set, table_schema=table_schema, sess_ids=sess_ids, slice_num=i+1, slice_count=len(_session_slices))
                # 2b) After processing all rows for each slice, write out the session data and reset for next slice.
                if request.ExportEvents() and self._event_mgr is not None:
                    _events = self._event_mgr.GetLines()
                    if request.ToDict():
                        ret_val['events']['vals'] += _events
                    if request.ToFile() and file_manager is not None:
                        file_manager.GetEventsFile().writelines(_events)
                    self._event_mgr.ClearLines()
                if self._extract_mgr is not None:
                    if request.ExportSessions():
                        _sess_feats = self._extract_mgr.GetSessionFeatures(as_str=True)
                        if request.ToDict():
                            ret_val['sessions']['vals'] += _sess_feats
                        if request.ToFile() and file_manager is not None:
                            file_manager.GetSessionsFile().writelines(["\t".join(sess) + "\n" for sess in _sess_feats])
                        self._extract_mgr.ClearSessionLines()
                    if request.ExportPlayers():
                        _player_feats = self._extract_mgr.GetPlayerFeatures(as_str=True)
                        if request.ToDict():
                            ret_val['players']['vals'] += _player_feats
                        if request.ToFile() and file_manager is not None:
                            file_manager.GetPlayersFile().writelines(["\t".join(player) + "\n" for player in _player_feats])
                        self._extract_mgr.ClearPlayerLines()
        # 3) If we made it all the way to the end, write population data and return the number of sessions processed.
        if self._extract_mgr is not None:
            if request.ExportPopulation():
                _pop_feats = self._extract_mgr.GetPopulationFeatures(as_str=True)
                if request.ToDict():
                    ret_val['population']['vals'] = _pop_feats
                if request.ToFile() and file_manager is not None:
                    file_manager.WritePopulationFile("\t".join(_pop_feats) + "\n")
            self._extract_mgr.ClearPopulationLines()
        return ret_val

    def _generateSlices(self, sess_ids:List[str]) -> List[List[str]]:
        _num_sess = len(sess_ids)
        #TODO: rewrite this to slice across players, instead of sessions.
        _slice_size = self._settings["BATCH_SIZE"] or default_settings["BATCH_SIZE"]
        Logger.Log(f"With slice size = {_slice_size}, there are {math.ceil(_num_sess / _slice_size)} slices", logging.INFO)
        return [[sess_ids[i] for i in range( j*_slice_size, min((j+1)*_slice_size, _num_sess) )]
                             for j in range( 0, math.ceil(_num_sess / _slice_size) )]

    def _getSlice(self, request:Request, next_slice:List[str], slice_num:int, slice_count:int) -> Union[List[Tuple], None]:
        start : datetime = datetime.now()

        ret_val = request.GetInterface().RowsFromIDs(id_list=next_slice, id_mode=request.GetRange().GetIDMode())
        time_delta = datetime.now() - start
        if ret_val is not None:
            Logger.Log(f"Retrieval time for slice [{slice_num}/{slice_count}]: {time_delta} to get {len(ret_val)} events", logging.INFO, depth=2)
        else:
            Logger.Log(f"Could not retrieve data set for slice [{slice_num}/{slice_count}].", logging.WARN)
        return ret_val

    def _processSlice(self, next_data_set:List[Tuple], table_schema:TableSchema, sess_ids:List[str], slice_num:int, slice_count:int):
        start      : datetime = datetime.now()
        num_events : int      = len(next_data_set)
        _unsessioned_event_count : int = 0
        # 3a) If next slice yielded valid data from the interface, process row-by-row.
        for row in next_data_set:
            try:
                next_event = table_schema.RowToEvent(row)
            except Exception as err:
                if default_settings.get("FAIL_FAST", None):
                    Logger.Log(f"Error while converting row to Event\nFull error: {err}\nRow data: {pformat(row)}", logging.ERROR)
                    raise err
                else:
                    Logger.Log(f"Error while converting row to Event. This row will be skipped.\nFull error: {err}", logging.WARNING)
            else:
                if next_event.session_id in sess_ids:
                    try:
                        if self._event_mgr is not None:
                            self._event_mgr.ProcessEvent(event=next_event)
                        if self._extract_mgr is not None:
                            self._extract_mgr.ProcessEvent(event=next_event)
                    except Exception as err:
                        if default_settings.get("FAIL_FAST", None):
                            Logger.Log(f"Error while processing event {next_event}.", logging.ERROR)
                            raise err
                        else:
                            Logger.Log(f"Error while processing event {next_event}. This event will be skipped. \nFull error: {err}", logging.WARNING)
                elif next_event.session_id is not None and next_event.session_id.upper() != "NONE":
                    Logger.Log(f"Found a session ({next_event.session_id}) which was in the slice but not in the list of sessions for processing.", logging.WARNING)
                else:
                    _unsessioned_event_count += 1
                    if _unsessioned_event_count < 10:
                        Logger.Log(f"Original data for an 'unsessioned' row: {row}", logging.WARNING)
        if _unsessioned_event_count > 0:
            Logger.Log(f"Found {_unsessioned_event_count} events with no session IDs.", logging.WARNING)
        time_delta = datetime.now() - start
        Logger.Log(f"Processing time for slice [{slice_num}/{slice_count}]: {time_delta} to handle {num_events} events", logging.INFO)

    def _closeFiles(self, game_schema:GameSchema, table_schema:TableSchema, num_sess:int):
        _game_id = game_schema._game_name
        try:
            # before we zip stuff up, let's ensure the readme is in place:
            readme = open(self._file_manager._readme_path, mode='r')
        except FileNotFoundError:
            Logger.Log(f"Missing readme for {_game_id}, generating new readme...", logging.WARNING)
            readme_path = Path("./data") / _game_id
            FileManager.GenerateReadme(game_schema=game_schema, table_schema=table_schema, path=readme_path)
        else:
            readme.close()
        self._file_manager.CloseFiles()
        self._file_manager.ZipFiles()
        self._file_manager.WriteMetadataFile(num_sess=num_sess)
        self._file_manager.UpdateFileExportList(num_sess=num_sess)