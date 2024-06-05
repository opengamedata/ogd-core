# standard imports
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Optional

# ogd imports
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

class DatasetKey:
    """Simple little class to make logic with dataset keys easier
    """
    def __init__(self, key:str, game_id:str):
    # 1. Get Game ID from key
        if key[:len(game_id)] != game_id:
            Logger.Log(f"Got a mismatch between expected game ID and ID in the dataset key: {key[:len(game_id)]} != {game_id}. Defaulting to {game_id}")
        self._game_id = game_id
    # 2. Get Dates from key
        _date_range = key[len(game_id):]
        _date_range_parts = _date_range.split("_")
        # If this _dataset_key matches the expected format,
        # i.e. spit is: ["", "YYYYMMDD", "to", "YYYYMMDD"]
        if len(_date_range_parts) == 4:
            self._from_year  = int(_date_range_parts[1][0:4])
            self._from_month = int(_date_range_parts[1][4:6])
            self._to_year    = int(_date_range_parts[3][0:4])
            self._to_month   = int(_date_range_parts[3][4:6])
        else:
            self._from_year  = None
            self._from_month = None
            self._to_year    = None
            self._to_month   = None
        self._original_key = key

    def __str__(self):
        return self._original_key
    
    @property
    def IsValid(self) -> bool:
        return  self._from_year  is not None \
            and self._from_month is not None \
            and self._to_year    is not None \
            and self._to_month   is not None
    @property
    def GameID(self) -> str:
        return self._game_id
    @property
    def FromYear(self) -> int:
        return self._from_year or -1
    @property
    def FromMonth(self) -> int:
        return self._from_month or -1
    @property
    def ToYear(self) -> int:
        return self._to_year or -1
    @property
    def ToMonth(self) -> int:
        return self._to_month or -1

class DatasetSchema(Schema):
    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._key                 : DatasetKey
        self._date_modified       : date | str
        self._start_date          : date | str
        self._end_date            : date | str
        self._ogd_revision        : str
        self._session_ct          : Optional[int]
        self._player_ct           : Optional[int]
        self._raw_file            : Optional[Path]
        self._events_file         : Optional[Path]
        self._events_template     : Optional[Path]
        self._sessions_file       : Optional[Path]
        self._sessions_template   : Optional[Path]
        self._players_file        : Optional[Path]
        self._players_template    : Optional[Path]
        self._population_file     : Optional[Path]
        self._population_template : Optional[Path]

        if not isinstance(all_elements, dict):
            all_elements = {}
        _game_id = DatasetSchema._parseGameID(name)
        self._key = DatasetKey(key=name, game_id=_game_id)
    # 1. Parse dates
        if "date_modified" in all_elements.keys():
            self._date_modified = DatasetSchema._parseDateModified(all_elements["date_modified"])
        else:
            self._date_modified = "UNKNOWN"
        if "start_date" in all_elements.keys():
            self._start_date = DatasetSchema._parseStartDate(all_elements["start_date"])
        else:
            self._start_date = "UNKNOWN"
        if "end_date" in all_elements.keys():
            self._end_date = DatasetSchema._parseEndDate(all_elements["end_date"])
        else:
            self._end_date = "UNKNOWN"
    # 2. Parse metadata
        if "ogd_revision" in all_elements.keys():
            self._ogd_revision = DatasetSchema._parseOGDRevision(all_elements["ogd_revision"])
        else:
            self._ogd_revision = "UNKNOWN"
        if "sessions" in all_elements.keys():
            self._session_ct = DatasetSchema._parseSessionCount(all_elements["sessions"])
        else:
            self._session_ct = None
        if "players" in all_elements.keys():
            self._players = DatasetSchema._parsePlayerCount(all_elements["players"])
        else:
            self._player_ct = None
    # 3. Parse file/template paths
        if "raw_file" in all_elements.keys():
            self._raw_file = DatasetSchema._parseRawFile(all_elements["raw_file"])
        else:
            self._raw_file = None
        if "events_file" in all_elements.keys():
            self._events_file = DatasetSchema._parseEventsFile(all_elements["events_file"])
        else:
            self._events_file = None
        if "events_template" in all_elements.keys():
            self._events_template = DatasetSchema._parseEventsTemplate(all_elements["events_template"])
        else:
            self._events_template = None
        if "sessions_file" in all_elements.keys():
            self._sessions_file = DatasetSchema._parseSessionsFile(all_elements["sessions_file"])
        else:
            self._sessions_file = None
        if "sessions_template" in all_elements.keys():
            self._sessions_template = DatasetSchema._parseSessionsTemplate(all_elements["sessions_template"])
        else:
            self._sessions_template = None
        if "players_file" in all_elements.keys():
            self._players_file = DatasetSchema._parsePlayersFile(all_elements["players_file"])
        else:
            self._players_file = None
        if "players_template" in all_elements.keys():
            self._players_template = DatasetSchema._parsePlayersTemplate(all_elements["players_template"])
        else:
            self._players_template = None
        if "population_file" in all_elements.keys():
            self._population_file = DatasetSchema._parsePopulationFile(all_elements["population_file"])
        else:
            self._population_file = None
        if "population_template" in all_elements.keys():
            self._population_template = DatasetSchema._parsePopulationTemplate(all_elements["population_template"])
        else:
            self._population_template = None

        _used = {"date_modified", "start_date", "end_date", "ogd_revision", "sessions", "players",
                 "raw_file", "events_file", "events_template",
                 "sessions_file", "sessions_template", "players_file", "players_template",
                 "population_file", "population_template"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    def __str__(self) -> str:
        return str(self.Key)

    # *** Properties ***

    @property
    def Key(self) -> DatasetKey:
        return self._key
    @property
    def DateModified(self) -> date | str:
        return self._date_modified
    @property
    def DateModifiedStr(self) -> str:
        ret_val : str
        if isinstance(self._date_modified, date):
            ret_val = self._date_modified.strftime("%m/%d/%Y")
        else:
            ret_val = self._date_modified
        return ret_val
    @property
    def StartDate(self) -> date | str:
        return self._start_date
    @property
    def EndDate(self) -> date | str:
        return self._end_date
    @property
    def OGDRevision(self) -> str:
        return self._ogd_revision
    @property
    def SessionCount(self) -> Optional[int]:
        return self._session_ct
    @property
    def PlayerCount(self) -> Optional[int]:
        return self._player_ct
    @property
    def RawFile(self) -> Optional[Path]:
        return self._raw_file
    @property
    def EventsFile(self) -> Optional[Path]:
        return self._events_file
    @property
    def EventsTemplate(self) -> Optional[Path]:
        return self._events_template
    @property
    def SessionsFile(self) -> Optional[Path]:
        return self._sessions_file
    @property
    def SessionsTemplate(self) -> Optional[Path]:
        return self._sessions_template
    @property
    def PlayersFile(self) -> Optional[Path]:
        return self._players_file
    @property
    def PlayersTemplate(self) -> Optional[Path]:
        return self._players_template
    @property
    def PopulationFile(self) -> Optional[Path]:
        return self._population_file
    @property
    def PopulationTemplate(self) -> Optional[Path]:
        return self._population_template

    @property
    def FileSet(self) -> str:
        """
        The list of data files associated with the dataset.

        r -> Raw events file (no generated events)
        e -> All events file (with generated events)
        s -> Session features file
        p -> Player features file
        P -> Popoulation features file

        :return: The list of data files associated with the dataset.
        :rtype: str
        """
        _fset = [
           "r" if self.RawFile is not None else "",
           "e" if self.EventsFile is not None else "",
           "s" if self.SessionsFile is not None else "",
           "p" if self.PlayersFile is not None else "",
           "P" if self.PopulationFile is not None else ""
        ]
        return "".join(_fset)

    @property
    def TemplateSet(self) -> str:
        """
        The list of template files associated with the dataset.

        e -> Events template
        s -> Session features template
        p -> Player features template
        P -> Popoulation features template

        :return: The list of template files associated with the dataset.
        :rtype: str
        """
        _tset = [
           "e" if self.EventsTemplate is not None else "",
           "s" if self.SessionsTemplate is not None else "",
           "p" if self.PlayersTemplate is not None else "",
           "P" if self.PopulationTemplate is not None else ""
        ]
        return "".join(_tset)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = \
f"""{self.Name}: {self.PlayerCount} players across {self.SessionCount} sessions.  
Last modified {self.DateModified.strftime('%m/%d/%Y') if type(self.DateModified) == date else self.DateModified} with OGD v.{self.OGDRevision or 'UNKNOWN'}  
- Files: [{self.FileSet}]  
- Templates: [{self.TemplateSet}]"""
        return ret_val

    @staticmethod
    def EmptySchema() -> "DatasetSchema":
        return DatasetSchema(name="NOT FOUND", all_elements={})

    # TODO : once we have official minimum Python up to 3.11, import Self and set other:Optional[Self]
    def IsNewerThan(self, other) -> bool | None:
        """
        Check if `self` has a more recent "modified on" date than `other`.

        If `other` is None, returns True by default.  
        If both `self` and `other` are DatasetSchemas, but one (or both) is missing a "modified" date, returns None, because it is indeterminate. 

        :param other: The DatasetSchema to be compared with `self`.
        :type other: Optional[Self]
        :return: True if `self` has a more recent "modified" date than `other`, otherwise False. If one (or both) are missing "modified" date, then None. If `other` is None, True by default.
        :rtype: bool | None
        """
        if other == None:
            return True
        if isinstance(self.DateModified, date) and isinstance(other.DateModified, date):
            return self.DateModified > other.DateModified
        else:
            return None

    # *** Private Functions ***

    # NOTE: Yes, most of these parse functions are redundant, but that's fine,
    # we just want to have one bit of code to parse each piece of the schema, even if most do the same thing.

    @staticmethod
    def _parseGameID(dataset_name) -> str:
        ret_val : str
        if isinstance(dataset_name, str):
            ret_val = dataset_name.split('_')[0]
        else:
            ret_val = str(dataset_name).split('_')[0]
            Logger.Log(f"Dataset name was unexpected type {type(dataset_name)}, defaulting to str(dataset_name).split('_')[0]={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDateModified(date_modified) -> date:
        ret_val : date
        if isinstance(date_modified, date):
            ret_val = date_modified
        elif isinstance(date_modified, str):
            ret_val = datetime.strptime(date_modified, "%m/%d/%Y").date()
        else:
            ret_val = datetime.strptime(str(date_modified), "%m/%d/%Y").date()
            Logger.Log(f"Dataset modified date was unexpected type {type(date_modified)}, defaulting to strptime(str(date_modified))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseStartDate(start_date) -> date:
        ret_val : date
        if isinstance(start_date, date):
            ret_val = start_date
        elif isinstance(start_date, str):
            ret_val = datetime.strptime(start_date, "%m/%d/%Y").date()
        else:
            ret_val = datetime.strptime(str(start_date), "%m/%d/%Y").date()
            Logger.Log(f"Dataset start date was unexpected type {type(start_date)}, defaulting to strptime(str(start_date))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseEndDate(end_date) -> date:
        ret_val : date
        if isinstance(end_date, date):
            ret_val = end_date
        elif isinstance(end_date, str):
            ret_val = datetime.strptime(end_date, "%m/%d/%Y").date()
        else:
            ret_val = datetime.strptime(str(end_date), "%m/%d/%Y").date()
            Logger.Log(f"Dataset end date was unexpected type {type(end_date)}, defaulting to strptime(str(end_date))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseOGDRevision(revision) -> str:
        ret_val : str
        if isinstance(revision, str):
            ret_val = revision
        else:
            ret_val = str(revision)
            Logger.Log(f"Dataset OGD revision was unexpected type {type(revision)}, defaulting to str(revision)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSessionCount(sess_ct) -> Optional[int]:
        ret_val : Optional[int]
        if isinstance(sess_ct, int):
            ret_val = sess_ct
        elif sess_ct == None:
            ret_val = None
        else:
            ret_val = int(sess_ct)
            Logger.Log(f"Dataset session count was unexpected type {type(sess_ct)}, defaulting to int(sess_ct)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePlayerCount(player_ct) -> Optional[int]:
        ret_val : Optional[int]
        if isinstance(player_ct, int):
            ret_val = player_ct
        elif player_ct == None:
            ret_val = None
        else:
            ret_val = int(player_ct)
            Logger.Log(f"Dataset player count was unexpected type {type(player_ct)}, defaulting to int(player_ct)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseRawFile(raw_file:Optional[Path | str]) -> Optional[Path]:
        ret_val : Optional[Path]
        if raw_file == None:
            ret_val = None
        elif isinstance(raw_file, Path):
            ret_val = raw_file
        elif isinstance(raw_file, str):
            ret_val = Path(raw_file) if raw_file != "" else None
        else:
            ret_val = Path(str(raw_file))
            Logger.Log(f"Dataset raw event file was unexpected type {type(raw_file)}, defaulting to Path(str(raw_file))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseEventsFile(events_file:Optional[Path | str]) -> Optional[Path]:
        ret_val : Optional[Path]
        if events_file == None:
            ret_val = None
        elif isinstance(events_file, Path):
            ret_val = events_file
        elif isinstance(events_file, str):
            ret_val = Path(events_file) if events_file != "" else None
        else:
            ret_val = Path(str(events_file))
            Logger.Log(f"Dataset all event file was unexpected type {type(events_file)}, defaulting to Path(str(events_file))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSessionsFile(sessions_file:Optional[Path | str]) -> Optional[Path]:
        ret_val : Optional[Path]
        if sessions_file == None:
            ret_val = None
        elif isinstance(sessions_file, Path):
            ret_val = sessions_file
        elif isinstance(sessions_file, str):
            ret_val = Path(sessions_file) if sessions_file != "" else None
        else:
            ret_val = Path(str(sessions_file))
            Logger.Log(f"Dataset session feature file was unexpected type {type(sessions_file)}, defaulting to Path(str(sessions_file))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePlayersFile(players_file:Optional[Path | str]) -> Optional[Path]:
        ret_val : Optional[Path]
        if players_file == None:
            ret_val = None
        elif isinstance(players_file, Path):
            ret_val = players_file
        elif isinstance(players_file, str):
            ret_val = Path(players_file) if players_file != "" else None
        else:
            ret_val = Path(str(players_file))
            Logger.Log(f"Dataset player feature file was unexpected type {type(players_file)}, defaulting to Path(str(players_file))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePopulationFile(pop_file:Optional[Path | str]) -> Optional[Path]:
        ret_val : Optional[Path]
        if pop_file == None:
            ret_val = None
        elif isinstance(pop_file, Path):
            ret_val = pop_file
        elif isinstance(pop_file, str):
            ret_val = Path(pop_file) if pop_file != "" else None
        else:
            ret_val = Path(str(pop_file))
            Logger.Log(f"Dataset population feature file was unexpected type {type(pop_file)}, defaulting to Path(str(pop_file))={ret_val}.", logging.WARN)
        return ret_val


    @staticmethod
    def _parseEventsTemplate(events_tplate:Optional[Path | str]) -> Optional[Path]:
        ret_val : Optional[Path]
        if events_tplate == None:
            ret_val = None
        elif isinstance(events_tplate, Path):
            ret_val = events_tplate
        elif isinstance(events_tplate, str):
            ret_val = Path(events_tplate) if events_tplate != "" else None
        else:
            ret_val = Path(str(events_tplate))
            Logger.Log(f"Dataset events template was unexpected type {type(events_tplate)}, defaulting to Path(str(events_tplate))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSessionsTemplate(sessions_tplate:Optional[Path | str]) -> Optional[Path]:
        ret_val : Optional[Path]
        if sessions_tplate == None:
            ret_val = None
        elif isinstance(sessions_tplate, Path):
            ret_val = sessions_tplate
        elif isinstance(sessions_tplate, str):
            ret_val = Path(sessions_tplate) if sessions_tplate != "" else None
        else:
            ret_val = Path(str(sessions_tplate))
            Logger.Log(f"Dataset session template file was unexpected type {type(sessions_tplate)}, defaulting to Path(str(sessions_tplate))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePlayersTemplate(players_tplate:Optional[Path | str]) -> Optional[Path]:
        ret_val : Optional[Path]
        if players_tplate == None:
            ret_val = None
        elif isinstance(players_tplate, Path):
            ret_val = players_tplate
        elif isinstance(players_tplate, str):
            ret_val = Path(players_tplate) if players_tplate != "" else None
        else:
            ret_val = Path(str(players_tplate))
            Logger.Log(f"Dataset players template file was unexpected type {type(players_tplate)}, defaulting to Path(str(players_tplate))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePopulationTemplate(pop_tplate:Optional[Path | str]) -> Optional[Path]:
        ret_val : Optional[Path]
        if pop_tplate == None:
            ret_val = None
        elif isinstance(pop_tplate, Path):
            ret_val = pop_tplate
        elif isinstance(pop_tplate, str):
            ret_val = Path(pop_tplate) if pop_tplate != "" else None
        else:
            ret_val = Path(str(pop_tplate))
            Logger.Log(f"Dataset population template file was unexpected type {type(pop_tplate)}, defaulting to Path(str(pop_tplate))={ret_val}.", logging.WARN)
        return ret_val
