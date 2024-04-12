# import standard libraries
import logging
from calendar import monthrange
from datetime import datetime
from typing import Set

# import 3rd-party libraries

# import local files
from ogd.core.interfaces.DataInterface import DataInterface
from ogd.core.interfaces.MySQLInterface import MySQLInterface
from ogd.core.interfaces.BigQueryInterface import BigQueryInterface
from ogd.core.interfaces.BQFirebaseInterface import BQFirebaseInterface
from ogd.core.requests.Request import ExporterRange
from ogd.core.schemas.configs.ConfigSchema import ConfigSchema
from ogd.core.schemas.ExportMode import ExportMode
from ogd.core.utils.Logger import Logger

class OGDGenerators:
    @staticmethod
    def genDBInterface(config:ConfigSchema, game:str) -> DataInterface:
        ret_val : DataInterface
        _game_cfg = config.GameSourceMap.get(game)
        if _game_cfg is not None and _game_cfg.Source is not None:
            match (_game_cfg.Source.Type):
                case "Firebase" | "FIREBASE":
                    ret_val = BQFirebaseInterface(game_id=game, config=_game_cfg, fail_fast=config.FailFast)
                case "BigQuery" | "BIGQUERY":
                    ret_val = BigQueryInterface(game_id=game, config=_game_cfg, fail_fast=config.FailFast)
                case "MySQL" | "MYSQL":
                    ret_val = MySQLInterface(game_id=game, config=_game_cfg, fail_fast=config.FailFast)
                case _:
                    raise Exception(f"{_game_cfg.Source.Type} is not a valid DataInterface type!")
            return ret_val
        else:
            raise ValueError(f"Config for {game} was invalid or not found!")

    @staticmethod
    def genModes(with_events:bool, with_features:bool, no_session_file:bool, no_player_file:bool, no_pop_file:bool) -> Set[ExportMode]:
        ret_val = set()

        if with_events:
            ret_val.add(ExportMode.EVENTS)
            ret_val.add(ExportMode.DETECTORS)
        if with_features:
            if not no_session_file:
                ret_val.add(ExportMode.SESSION)
            if not no_player_file:
                ret_val.add(ExportMode.PLAYER)
            if not no_pop_file:
                ret_val.add(ExportMode.POPULATION)

        return ret_val
        
    # retrieve/calculate date range.
    @staticmethod
    def genDateRange(game:str, interface, monthly:bool, start_date:str, end_date:str) -> ExporterRange:
        _from: datetime
        _to  : datetime
        today     : datetime = datetime.now()
        # If we want to export all data for a given month, calculate a date range.
        if monthly:
            month: int = today.month
            year:  int = today.year
            month_year = start_date.split("/")
            month = int(month_year[0])
            year  = int(month_year[1])
            month_range = monthrange(year, month)
            days_in_month = month_range[1]
            _from = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)
            _to   = datetime(year=year, month=month, day=days_in_month, hour=23, minute=59, second=59)
            Logger.Log(f"Exporting {month}/{year} data for {game}...", logging.DEBUG)
        # Otherwise, create date range from given pair of dates.
        else:
            _from = datetime.strptime(start_date, "%m/%d/%Y") if start_date is not None else today
            _from = _from.replace(hour=0, minute=0, second=0)
            _to   = datetime.strptime(end_date, "%m/%d/%Y") if end_date is not None else _from
            _to = _to.replace(hour=23, minute=59, second=59)
            Logger.Log(f"Exporting from {str(_from)} to {str(_to)} of data for {game}...", logging.INFO)
        return ExporterRange.FromDateRange(source=interface, date_min=_from, date_max=_to)