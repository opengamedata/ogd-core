## @package DataToCSV.py
#  A package to handle processing of stuff from our database,
#  for export to CSV files.

## import standard libraries
import logging
import math
from msilib import Table
import subprocess
import traceback
from datetime import datetime
from pprint import pformat
from typing import Dict, List, Type, Tuple, Union
from managers.ExtractorManager import ExtractorManager
## import local files
import utils
from config.config import settings as default_settings
from managers.FileManager import *
from managers.EventManager import EventManager
from managers.Request import Request
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema

## @class ExportManager
#  A class to export features and raw data, given a Request object.
class ExportManager:
    ## Constructor for the ExportManager class.
    #  Fairly simple, just saves some data for later use during export.
    #  @param game_id Initial id of game to export
    #                 (this can be changed, if a TableSchema with a different id is
    #                  given, but will generate a warning)
    #  @param db      An active database connection
    #  @param settings A dictionary of program settings, some of which are needed for export.
    def __init__(self, settings):
        self._settings = settings
        self._event_processor   : Union[EventManager, None]     = None
        self._extract_processor : Union[ExtractorManager, None] = None

    def ExecuteRequest(self, request:Request, feature_overrides:Union[List[str],None]=None) -> Dict[str,Any]:
        ret_val       : Dict[str,Any] = {"success":False}
        _game_id      : str         = request.GetGameID()
        _game_schema  : GameSchema  = GameSchema(schema_name=_game_id, schema_path=Path(f"./games/{_game_id}"))
        _table_schema : TableSchema = self._prepareTableSchema(_game_id)

        start = datetime.now()
        try:
            self._prepareProcessors(request=request, game_schema=_game_schema, feature_overrides=feature_overrides)
            _result = self._executeDataRequest(request=request, table_schema=_table_schema)
            if request.ToFile():
                ret_val['success'] = self._executeFileRequest(request=request,      feature_data=_result,
                                                          game_schema=_game_schema, table_schema=_table_schema)
            if request.ToDict():
                ret_val.update(_result) # merge event, session, player, and population data into the return value.
            utils.Logger.Log(f"Successfully executed data request {str(request)}.", logging.INFO)
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.Log(f"Failed to execute data request {str(request)}, an error occurred:\n{msg}", logging.ERROR)
            traceback.print_tb(err.__traceback__)
        finally:
            time_delta = datetime.now() - start
            utils.Logger.Log(f"Total data request execution time: {time_delta}", logging.INFO)
            return ret_val

    def _prepareTableSchema(self, _game_id:str):
        if "GAME_SOURCE_MAP" in self._settings:
            _table_name = self._settings["GAME_SOURCE_MAP"][_game_id]["table"]
        else:
            _table_name = default_settings["GAME_SOURCE_MAP"][_game_id]["table"]
        return TableSchema(schema_name=f"{_table_name}.json")

    def _prepareProcessors(self, request:Request, game_schema:GameSchema, feature_overrides:Union[List[str],None]):
        if request.ExportEvents():
            self._event_processor = EventManager()
            # evt_processor.WriteEventsCSVHeader(file_mgr=file_manager, separator="\t")
        else:
            utils.Logger.toStdOut("Event log not requested, skipping events file.", logging.INFO)
        # If game doesn't have an extractor, make sure we don't try to export it.
        if request.ExportSessions() or request.ExportPlayers() or request.ExportPopulation():
            self._extract_processor = ExtractorManager(game_id=request.GetGameID(), exp_types=request._exports,
                                                       game_schema=game_schema, feature_overrides=feature_overrides)
            if not self._extract_processor.HasExtractor():
                request._exports.sessions   = False
                request._exports.players    = False
                request._exports.population = False
                utils.Logger.toStdOut("Could not extract feature data, no game extractor given!", logging.WARN)

    def _executeDataRequest(self, request:Request, table_schema:TableSchema) -> Dict[str,Any]:
        ret_val       : Dict[str,Any]           = {"events":None, "sessions":None, "players":None, "population":None}
        next_data_set : Union[List[Tuple],None] = None

        if request.ExportEvents() and self._event_processor is not None:
            ret_val['events'] = {"cols":self._event_processor.GetColumnNames(), "vals":[]}
        if request.ExportSessions() and self._extract_processor is not None:
            ret_val['sessions'] = {"cols":self._extract_processor.GetSessionFeatureNames(), "vals":[]}
        if request.ExportPlayers() and self._extract_processor is not None:
            ret_val['players'] = {"cols":self._extract_processor.GetPlayerFeatureNames(), "vals":[]}
        if request.ExportPopulation() and self._extract_processor is not None:
            ret_val['population'] = {"cols":self._extract_processor.GetPopulationFeatureNames(), "vals":[]}
        # 4) Get the IDs of sessions to process
        sess_ids = request.RetrieveSessionIDs() or []
        utils.Logger.toStdOut(f"Preparing to process {len(sess_ids)} sessions.", logging.INFO)
        # 5) Loop over and process the sessions, slice-by-slice (where each slice is a list of sessions).
        _session_slices = self._prepareSlices(sess_ids=sess_ids)
        for i, next_slice in enumerate(_session_slices):
            start         : datetime = datetime.now()
            next_data_set = request._interface.RowsFromIDs(next_slice)
            if next_data_set is not None:
                time_delta = datetime.now() - start
                utils.Logger.Log(f"Retrieval time for slice [{i+1}/{len(_session_slices)}]: {time_delta} to get {len(next_data_set)} events", logging.INFO)
                # 3a) If next slice yielded valid data from the interface, process row-by-row.
                self._processSlice(next_data_set=next_data_set, table_schema=table_schema, sess_ids=sess_ids, slice_num=i+1, slice_count=len(_session_slices))
                # 3b) After processing all rows for each slice, write out the session data and reset for next slice.
                if request.ExportEvents() and self._event_processor is not None:
                    ret_val['events']['vals'] += self._event_processor.GetLines()
                    self._event_processor.ClearLines()
                if request.ExportSessions() and self._extract_processor is not None:
                    self._extract_processor.CalculateAggregateSessionFeatures()
                    ret_val['sessions']['vals'] += self._extract_processor.GetSessionFeatures()
                    self._extract_processor.ClearSessionLines()
                if request.ExportPlayers() and self._extract_processor is not None:
                    self._extract_processor.CalculateAggregatePlayerFeatures()
                    ret_val['players']['vals'] += self._extract_processor.GetPlayerFeatures()
                    self._extract_processor.ClearPlayerLines()
            else:
                utils.Logger.Log(f"Could not retrieve data set for slice [{i+1}/{len(_session_slices)}].", logging.WARN)
        # 4) If we made it all the way to the end, write population data and return the number of sessions processed.
        if request.ExportPopulation() and self._extract_processor is not None:
            self._extract_processor.CalculateAggregatePopulationFeatures()
            ret_val['population']['vals'] = self._extract_processor.GetPopulationFeatures()
            self._extract_processor.ClearPopulationLines()
        return ret_val

    def _prepareSlices(self, sess_ids:List[str]):
        _num_sess = len(sess_ids)
        #TODO: rewrite this to slice across players, instead of sessions.
        _slice_size = self._settings["BATCH_SIZE"] or default_settings["BATCH_SIZE"]
        utils.Logger.toStdOut(f"Using slice size = {_slice_size}, should result in {math.ceil(_num_sess / _slice_size)} slices", logging.INFO)
        return [[sess_ids[i] for i in range( j*_slice_size, min((j+1)*_slice_size, _num_sess) )]
                                       for j in range( 0, math.ceil(_num_sess / _slice_size) )]

    def _processSlice(self, next_data_set:List[Tuple], table_schema:TableSchema, sess_ids:List[str], slice_num:int, slice_count:int):
        start      : datetime = datetime.now()
        num_events : int      = len(next_data_set)
        for row in next_data_set:
            try:
                next_event = table_schema.RowToEvent(row)
            except Exception as err:
                if default_settings.get("FAIL_FAST", None):
                    utils.Logger.Log(f"Error while converting row to Event\nFull error: {err}\nRow data: {pformat(row)}", logging.ERROR)
                    raise err
                else:
                    utils.Logger.Log(f"Error while converting row to Event. This row will be skipped.\nFull error: {err}", logging.WARNING)
            else:
                if next_event.session_id in sess_ids:
                    try:
                        if self._extract_processor is not None:
                            self._extract_processor.ProcessEvent(event=next_event)
                        if self._event_processor is not None:
                            self._event_processor.ProcessEvent(event=next_event)
                    except Exception as err:
                        if default_settings.get("FAIL_FAST", None):
                            utils.Logger.Log(f"Error while processing event {next_event}.", logging.ERROR)
                            raise err
                        else:
                            utils.Logger.Log(f"Error while processing event {next_event}. This event will be skipped", logging.WARNING)
                else:
                    utils.Logger.toStdOut(f"Found a session ({next_event.session_id}) which was in the slice but not in the list of sessions for processing.", logging.WARNING)
        time_delta = datetime.now() - start
        utils.Logger.Log(f"Processing time for slice [{slice_num}/{slice_count}]: {time_delta} to handle {num_events} events", logging.INFO)

    ## Private function containing most of the code to handle processing of db
    #  data, and export to files.
    #  @param request    A data structure carrying parameters for feature extraction
    #                    and export
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    def _executeFileRequest(self, request:Request, feature_data:Dict[str,Any], game_schema:GameSchema, table_schema:TableSchema) -> bool:
        ret_val  : bool = False
        num_sess : int  = len(feature_data['sessions'].get('vals', []))
        # 2) Prepare files for export.
        _data_dir : str = self._settings["DATA_DIR"] or default_settings["DATA_DIR"]
        file_manager = FileManager(request=request, data_dir=_data_dir, extension="tsv")
        file_manager.OpenFiles()
        self._setupFileHeaders(request=request, file_manager=file_manager)
        num_sess = len(feature_data['sessions'].get('vals', -1))
        # 3) Loop over and process the sessions, slice-by-slice (where each slice is a list of sessions).
        if request.ExportEvents() and self._event_processor is not None:
            _events = feature_data['events'].get('vals', [])
            file_manager.GetEventsFile().writelines(_events)
        if request.ExportSessions() and self._extract_processor is not None:
            _sess_feats = self._extract_processor.GetSessionFeatures()
            for sess in _sess_feats:
                file_manager.WriteSessionsFile("\t".join(sess) + "\n")
            self._extract_processor.ClearSessionLines()
        if request.ExportPlayers() and self._extract_processor is not None:
            _player_feats = self._extract_processor.GetPlayerFeatures()
            for player in _player_feats:
                file_manager.WritePlayersFile("\t".join(player) + "\n")
            self._extract_processor.ClearPlayerLines()
        if request.ExportPopulation() and self._extract_processor is not None:
            _pop_feats = self._extract_processor.GetPopulationFeatures()
            file_manager.WritePopulationFile("\t".join(_pop_feats))
            self._extract_processor.ClearPopulationLines()
        # 5) Finally, update the list of csv files.
        file_manager.WriteMetadataFile(num_sess=num_sess)
        file_manager.UpdateFileExportList(num_sess=num_sess)
        self._setupReadme(file_manager=file_manager, game_schema=game_schema, table_schema=table_schema)
        # 4) Save and close files
        file_manager.CloseFiles()
        file_manager.ZipFiles()
        ret_val = True
        return ret_val

    def _setupFileHeaders(self, request:Request, file_manager:FileManager):
        if request.ExportEvents() and self._event_processor is not None:
            cols = self._event_processor.GetColumnNames()
            file_manager.WriteEventsFile("\t".join(cols) + "\n")
        if request.ExportSessions() and self._extract_processor is not None:
            cols = self._extract_processor.GetSessionFeatureNames()
            file_manager.WriteSessionsFile("\t".join(cols) + "\n")
        if request.ExportPlayers() and self._extract_processor is not None:
            cols = self._extract_processor.GetPlayerFeatureNames()
            file_manager.WritePlayersFile("\t".join(cols) + "\n")
        if request.ExportPopulation() and self._extract_processor is not None:
            cols = self._extract_processor.GetPopulationFeatureNames()
            file_manager.WritePopulationFile("\t".join(cols) + "\n")

    def _setupReadme(self, file_manager:FileManager, game_schema:GameSchema, table_schema:TableSchema):
        _game_id = game_schema._game_name
        try:
            # before we zip stuff up, let's ensure the readme is in place:
            readme = open(file_manager._readme_path, mode='r')
        except FileNotFoundError:
            utils.Logger.toStdOut(f"Missing readme for {_game_id}, generating new readme...", logging.WARNING)
            readme_path = Path("./data") / _game_id
            utils.GenerateReadme(game_schema=game_schema, table_schema=table_schema, path=readme_path)
        else:
            readme.close()