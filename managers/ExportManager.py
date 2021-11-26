## @package DataToCSV.py
#  A package to handle processing of stuff from our database,
#  for export to CSV files.

## import standard libraries
from extractors.Extractor import Extractor
import logging
import math
import os
import subprocess
import traceback
from datetime import datetime
from typing import Dict, List, Type, Tuple, Union
## import local files
import utils
from config.config import settings as default_settings
from managers.FileManager import *
from managers.PopulationProcessor import PopulationProcessor
from managers.SessionProcessor import SessionProcessor
from managers.EventProcessor import EventProcessor
from managers.Request import Request
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema
from games.AQUALAB.AqualabExtractor import AqualabExtractor
from games.CRYSTAL.CrystalExtractor import CrystalExtractor
from games.JOWILDER.JowilderExtractor import JowilderExtractor
from games.LAKELAND.LakelandExtractor import LakelandExtractor
from games.MAGNET.MagnetExtractor import MagnetExtractor
from games.SHADOWSPECT.ShadowspectExtractor import ShadowspectExtractor
from games.WAVES.WaveExtractor import WaveExtractor

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
        self._extractor_class : Union[Type[Extractor],None]      = None
        self._pop_processor   : Union[PopulationProcessor, None] = None
        self._sess_processor  : Union[SessionProcessor, None]    = None
        self._evt_processor   : Union[EventProcessor, None]      = None

    def ExecuteRequest(self, request:Request, game_id:str, feature_overrides:Union[List[str],None]=None) -> Dict[str,Any]:
        ret_val      : Dict[str,Any] = {"success":False}
        game_schema  : GameSchema  = GameSchema(schema_name=game_id, schema_path=Path(f"./games/{game_id}"))
        table_name   : str
        if "GAME_SOURCE_MAP" in self._settings:
            table_name = self._settings["GAME_SOURCE_MAP"][game_id]["table"]
        else:
            table_name = default_settings["GAME_SOURCE_MAP"][game_id]["table"]
        table_schema : TableSchema = TableSchema(schema_name=f"{table_name}.json")

        start = datetime.now()
        try:
            _game_id = request.GetGameID()
            self._prepareExtractor(_game_id)
            self._prepareProcessors(request=request, game_schema=game_schema, feature_overrides=feature_overrides)
            if request._locs.files:
                ret_val['success'] = self._executeFileRequest(request=request, game_schema=game_schema, table_schema=table_schema)
            if request._locs.dict:
                result = self._executeDataRequest(request=request, table_schema=table_schema)
                ret_val.update(result) # merge event, session, and population data into the return value.
            utils.Logger.Log(f"Successfully completed request {str(request)}.", logging.INFO)
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.Log(f"Could not complete request {str(request)}, an error occurred:\n{msg}", logging.ERROR)
            traceback.print_tb(err.__traceback__)
        finally:
            time_delta = datetime.now() - start
            utils.Logger.Log(f"Total Data Request Execution Time: {time_delta}", logging.INFO)
            return ret_val

    def _executeDataRequest(self, request:Request, table_schema:TableSchema) -> Dict[str,Any]:
        ret_val : Dict[str,Any] = {"events":None, "sessions":None, "population":None}
        # If we have a schema, we can do feature extraction.
        if request._exports.events and self._evt_processor is not None:
            ret_val['events'] = {"cols":self._evt_processor.GetColumnNames(), "vals":[]}
        if request._exports.sessions and self._sess_processor is not None:
            ret_val['sessions'] = {"cols":self._sess_processor.GetSessionFeatureNames(), "vals":[]}
        if request._exports.population and self._pop_processor is not None:
            ret_val['population'] = {"cols":self._pop_processor.GetPopulationFeatureNames(), "vals":[]}
        # 4) Get the IDs of sessions to process
        _dummy = request.RetrieveSessionIDs()
        sess_ids = _dummy if _dummy is not None else []
        utils.Logger.toStdOut(f"Preparing to process {len(sess_ids)} sessions.", logging.INFO)
        # 5) Loop over and process the sessions, slice-by-slice (where each slice is a list of sessions).
        session_slices = self._genSlices(sess_ids)
        for i, next_slice in enumerate(session_slices):
            start      : datetime = datetime.now()
            next_data_set : Union[List[Tuple],None] = request._interface.RowsFromIDs(next_slice)
            if next_data_set is not None:
                time_delta = datetime.now() - start
                utils.Logger.Log(f"Retrieval time for slice [{i+1}/{len(session_slices)}]: {time_delta} to get {len(next_data_set)} events", logging.INFO)
                # 3a) If next slice yielded valid data from the interface, process row-by-row.
                self._processSlice(next_data_set=next_data_set, table_schema=table_schema, sess_ids=sess_ids, slice_num=i+1, slice_count=len(session_slices))
                # 3b) After processing all rows for each slice, write out the session data and reset for next slice.
                if request._exports.events and self._evt_processor is not None:
                    ret_val['events']['vals'] += self._evt_processor.GetLines()
                    self._evt_processor.ClearLines()
                if request._exports.sessions and self._sess_processor is not None:
                    self._sess_processor.CalculateAggregateFeatures()
                    ret_val['sessions']['vals'] += self._sess_processor.GetSessionFeatures()
                    self._sess_processor.ClearLines()
            else:
                utils.Logger.Log(f"Could not retrieve data set for slice [{i+1}/{len(session_slices)}].", logging.WARN)
        # 4) If we made it all the way to the end, write population data and return the number of sessions processed.
        if request._exports.population and self._pop_processor is not None:
            self._pop_processor.CalculateAggregateFeatures()
            ret_val['population']['vals'] = self._pop_processor.GetPopulationFeatures()
            self._pop_processor.ClearLines()
        return ret_val

    ## Private function containing most of the code to handle processing of db
    #  data, and export to files.
    #  @param request    A data structure carrying parameters for feature extraction
    #                    and export
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    def _executeFileRequest(self, request:Request, game_schema:GameSchema, table_schema:TableSchema) -> bool:
        ret_val  : bool = False
        num_sess : int  = -1
        _game_id = request.GetGameID()
        # 2) Prepare files for export.
        _data_dir : str = self._settings["DATA_DIR"] or default_settings["DATA_DIR"]
        file_manager = FileManager(exporter_files=request._exports, game_id=_game_id, \
                                    data_dir=_data_dir, date_range=request._range.GetDateRange(),
                                    extension="tsv")
        file_manager.OpenFiles()
        # 3) Loop over data, running extractors.
        if request._exports.events and self._evt_processor is not None:
            self._evt_processor.WriteEventsCSVHeader(file_mgr=file_manager, separator="\t")
        if request._exports.sessions and self._sess_processor is not None:
            self._sess_processor.WriteSessionFileHeader(file_mgr=file_manager, separator="\t")
        if request._exports.population and self._pop_processor is not None:
            self._pop_processor.WritePopulationFileHeader(file_mgr=file_manager, separator="\t")
        # 2) Get the IDs of sessions to process
        _dummy = request.RetrieveSessionIDs()
        sess_ids = _dummy if _dummy is not None else []
        num_sess = len(sess_ids)
        utils.Logger.toStdOut(f"Preparing to process {len(sess_ids)} sessions.", logging.INFO)
        # 3) Loop over and process the sessions, slice-by-slice (where each slice is a list of sessions).
        session_slices = self._genSlices(sess_ids)
        for i, next_slice in enumerate(session_slices):
            start      : datetime = datetime.now()
            next_data_set : Union[List[Tuple],None] = request._interface.RowsFromIDs(next_slice)
            if next_data_set is not None:
                time_delta = datetime.now() - start
                utils.Logger.Log(f"Retrieval time for slice [{i+1}/{len(session_slices)}]: {time_delta} to get {len(next_data_set)} events", logging.INFO)
                # 3a) If next slice yielded valid data from the interface, process row-by-row.
                self._processSlice(next_data_set=next_data_set, table_schema=table_schema, sess_ids=sess_ids, slice_num=i+1, slice_count=len(session_slices))
                # 3b) After processing all rows for each slice, write out the session data and reset for next slice.
                if request._exports.events and self._evt_processor is not None:
                    self._evt_processor.WriteEventsCSVLines(file_mgr=file_manager)
                    self._evt_processor.ClearLines()
                if request._exports.sessions and self._sess_processor is not None:
                    self._sess_processor.CalculateAggregateFeatures()
                    self._sess_processor.WriteSessionFileLines(file_mgr=file_manager, separator="\t")
                    self._sess_processor.ClearLines()
            else:
                utils.Logger.Log(f"Could not retrieve data set for slice [{i+1}/{len(session_slices)}].", logging.WARN)
        # 4) If we made it all the way to the end, write population data and return the number of sessions processed.
        if request._exports.population and self._pop_processor is not None:
            self._pop_processor.CalculateAggregateFeatures()
            self._pop_processor.WritePopulationFileLines(file_mgr=file_manager)
            self._pop_processor.ClearLines()
        # 4) Save and close files
        # If we have a schema, we can do feature extraction.
        if game_schema is not None:
            try:
                # before we zip stuff up, let's ensure the readme is in place:
                readme = open(file_manager._readme_path, mode='r')
            except FileNotFoundError:
                utils.Logger.toStdOut(f"Missing readme for {_game_id}, generating new readme...", logging.WARNING)
                readme_path = Path("./data") / _game_id
                utils.GenerateReadme(game_schema=game_schema, table_schema=table_schema, path=readme_path)
            else:
                readme.close()
        else:
            utils.Logger.toStdOut(f"Missing schema for {request.GetGameID()}", logging.WARNING)
        file_manager.CloseFiles()
        file_manager.ZipFiles()
        # 5) Finally, update the list of csv files.
        file_manager.WriteMetadataFile(num_sess=num_sess)
        file_manager.UpdateFileExportList(num_sess=num_sess)
        ret_val = True
        return ret_val

    def _processSlice(self, next_data_set:List[Tuple], table_schema:TableSchema, sess_ids:List[str], slice_num:int, slice_count:int):
        start      : datetime = datetime.now()
        num_events : int      = len(next_data_set)
        for row in next_data_set:
            try:
                next_event = table_schema.RowToEvent(row)
            except Exception as err:
                if default_settings.get("FAIL_FAST", None):
                    utils.Logger.Log(f"Error while converting row {row} to Event\nFull error: {err}", logging.ERROR)
                    raise err
                else:
                    utils.Logger.Log(f"Error while converting row to Event. This row will be skipped.\nFull error: {err}", logging.WARNING)
            else:
                if next_event.session_id in sess_ids:
                    try:
                        if self._pop_processor is not None:
                            self._pop_processor.ProcessEvent(next_event)
                        if self._sess_processor is not None:
                            self._sess_processor.ProcessEvent(next_event)
                        if self._evt_processor is not None:
                            self._evt_processor.ProcessEvent(next_event)
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

    def _prepareExtractor(self, game_id) -> None:
        game_extractor: Union[type,None] = None
        if game_id == "AQUALAB":
            game_extractor = AqualabExtractor
        elif game_id == "CRYSTAL":
            game_extractor = CrystalExtractor
        elif game_id == "JOWILDER":
            game_extractor = JowilderExtractor
        elif game_id == "LAKELAND":
            game_extractor = LakelandExtractor
        elif game_id == "MAGNET":
            game_extractor = MagnetExtractor
        elif game_id == "SHADOWSPECT":
            game_extractor = ShadowspectExtractor
        elif game_id == "WAVES":
            game_extractor = WaveExtractor
        elif game_id in ["BACTERIA", "BALLOON", "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE", "SHIPWRECKS", "STEMPORTS", "WIND"]:
            # all games with data but no extractor.
            pass
        else:
            raise Exception(f"Got an invalid game ID ({game_id})!")
        self._extractor_class = game_extractor

    def _prepareProcessors(self, request:Request, game_schema:GameSchema, feature_overrides:Union[List[str],None]):
        if request._exports.events:
            self._evt_processor = EventProcessor()
            # evt_processor.WriteEventsCSVHeader(file_mgr=file_manager, separator="\t")
        else:
            utils.Logger.toStdOut("Event log not requested, skipping events file.", logging.INFO)
        # If game doesn't have an extractor, make sure we don't try to export it.
        if self._extractor_class is None:
            request._exports.sessions = False
            request._exports.population = False
            utils.Logger.toStdOut("Could not export population/session data, no game extractor given!", logging.WARN)
        else:
            if request._exports.sessions:
                self._sess_processor = SessionProcessor(ExtractorClass=self._extractor_class, game_schema=game_schema, feature_overrides=feature_overrides)
            else:
                utils.Logger.toStdOut("Session features not requested, skipping session_features file.", logging.INFO)
            if request._exports.population:
                self._pop_processor = PopulationProcessor(ExtractorClass=self._extractor_class, game_schema=game_schema, feature_overrides=feature_overrides)
            else:
                utils.Logger.toStdOut("Population features not requested, skipping population_features file.", logging.INFO)

    def _genSlices(self, sess_ids):
        _sess_ct = len(sess_ids)
        _slice_size = self._settings["BATCH_SIZE"] or default_settings["BATCH_SIZE"]
        return [[sess_ids[i] for i in range( j*_slice_size, min((j+1)*_slice_size, _sess_ct) )]
                                       for j in range( 0, math.ceil(_sess_ct / _slice_size) )]
