"""Module containing all the commands available through the OGD CLI"""
# import standard libraries
import csv
import logging
import traceback
from argparse import Namespace
from itertools import chain
from pathlib import Path
from typing import List, Optional, Set

# import 3rd-party libraries
from dateutil.parser import parse

# import OGD files
# from ogd.core.exec.Generators import OGDGenerators
from ogd import games
from ogd.core.managers.ExportManager import ExportManager
from ogd.core.requests.Request import Request
from ogd.core.requests.RequestResult import RequestResult, ResultStatus
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.core.configs.CoreConfig import CoreConfig
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.filters.SetFilter import SetFilter
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.schemas.events.LoggingSpecificationSchema import LoggingSpecificationSchema
from ogd.common.utils.Logger import Logger
from ogd.games.Readme import Readme
from .Generators import OGDGenerators


class OGDCommands:
    """Utility class to collect functions for each of the commands that can be run when executing ogd-core as a module."""

    # *** BUILT-INS & PROPERTIES ***

    # *** PUBLIC STATICS ***

    @staticmethod
    def ListGames(games_list:List[str]) -> bool:
        """Command to list out the games available for export.

        :param games_list: The list of available games, which the command should display.
        :type games_list: List[str]
        :return: True if the list was successfully displayed, else False.
        :rtype: bool
        """
        print(f"The games available for export are:\n{games_list}")
        return True

    @staticmethod
    def ShowGameInfo(config:CoreConfig, game:str) -> bool:
        """Function to print out info on a game from the game's schema.

        This does a similar function to writeReadme, but is limited to the CSV metadata part
        (basically what was in the schema, at one time written into the csv's themselves).
        Further, the output is printed rather than written to file.

        :return: True if game metadata was successfully loaded and printed, or False if an error occurred
        :rtype: bool
        """
        try:
            event_schema  = LoggingSpecificationSchema.Load(schema_name=game)
            generator_cfg = GeneratorCollectionConfig.Load( schema_name=game)
            table_schema = config.GameSourceMap[game].EventsFrom[0].TableSchema or EventTableSchema.Default()
            readme = Readme(event_collection=event_schema, generator_collection=generator_cfg, table_schema=table_schema)
            print(readme.CustomReadmeSource)
        except Exception as err: # pylint: disable=broad-exception-caught
            msg = f"Could not print information for {game}: {type(err)} {str(err)}"
            Logger.Log(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            return False
        else:
            return True

    @staticmethod
    def WriteReadme(config:CoreConfig, game:str, destination:Path) -> bool:
        """Function to write out the readme file for a given game.

        This includes the CSV metadata (data from the schema, originally written into
        the CSV files themselves), custom readme source, and the global changelog.
        The readme is placed in the game's data folder.

        :return: _description_
        :rtype: bool
        """
        path = destination / game
        try:
            event_schema  = LoggingSpecificationSchema.Load(schema_name=game)
            generator_cfg = GeneratorCollectionConfig.Load(schema_name=game)
            table_schema = EventTableSchema.Load(schema_name=f"{config.GameSourceMap[game].EventsFrom[0].TableName}.json")
            readme = Readme(event_collection=event_schema, generator_collection=generator_cfg, table_schema=table_schema)
            readme.ToFile(path=path)
        except Exception as err: # pylint: disable=broad-exception-caught
            msg = f"Could not create a readme for {game}: {type(err)} {str(err)}"
            Logger.Log(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            return False
        else:
            Logger.Log(f"Successfully generated a readme for {game}.", logging.INFO)
            return True

    @staticmethod
    def RunExport(args:Namespace, config:CoreConfig, destination:Path, with_events:bool = False, with_features:bool = False) -> bool:
        """Function to handle execution of export code.

        This is the main intended use of the program.

        .. TODO:: Refactor "step 2" logic into smaller functions, probably a "get case", then pass in to a "get range" and "get dataset ID"
        .. TODO:: Use DatasetKey here for the dataset name.

        :param events: _description_, defaults to False
        :type events: bool, optional
        :param features: _description_, defaults to False
        :type features: bool, optional
        :return: _description_
        :rtype: bool
        """
        success : bool = False

        # pull vars from args, for autocomplete and type-hinting purposes
        game_id         : str            = args.game
        from_source     : Optional[str]  = args.from_source           if args.from_source     else None
        session_id      : Optional[str]  = args.session               if args.session         else None
        session_id_file : Optional[Path] = Path(args.session_id_file) if args.session_id_file else None
        player_id       : Optional[str]  = args.player                if args.session_id_file else None
        player_id_file  : Optional[Path] = Path(args.player_id_file)  if args.player_id_file  else None

        filters      : DatasetFilterCollection = DatasetFilterCollection()
        export_modes : Set[ExportMode] = OGDGenerators.GenModes(
            with_events=with_events, with_features=with_features,
            no_session_file=args.no_session_file,
            no_player_file=args.no_player_file,
            no_pop_file=args.no_pop_file
        )
        game_source_mapping = config.GameSourceMap
        repository : DatasetRepositoryConfig = DatasetRepositoryConfig.Default()
        dataset_id : Optional[DatasetKey] = None

        _games_path  = Path(games.__file__) if Path(games.__file__).is_dir() else Path(games.__file__).parent
        generator_config  : GeneratorCollectionConfig  = GeneratorCollectionConfig.Load(schema_name=f"{game_id}.json")

        # TODO : Add a way to configure what to exclude, rather than just hardcoding. So we can easily choose to leave out certain events.
        exclude_rows : Optional[Set[str]]
        match game_id:
            case 'BLOOM':
                exclude_rows = {'algae_growth_end', 'algae_growth_begin'}
            case 'THERMOLAB' | 'THERMOVR':
                exclude_rows = {'nudge_hint_displayed', 'nudge_hint_hidden'}
            case 'LAKELAND':
                exclude_rows = {'CUSTOM.24'}
            case _:
                exclude_rows = None
        filters.Events.EventNames = SetFilter(mode=FilterMode.EXCLUDE, set_elements=exclude_rows)

    # 2. figure out the interface and range
        if from_source is not None and from_source != "":
            # raise NotImplementedError("Sorry, exports with file inputs are currently broken.")
            game_source_mapping[game_id].EventsFrom = [
                DataTableConfig(name="FILE SOURCE",
                    store_name=None,
                    schema_name=None,
                    table_location=None,
                    store_config=FileStoreConfig(name="SourceFile", location=from_source, file_credential=None),
                    table_schema=EventTableSchema.Load(schema_name="OGD_EVENT_FILE") )
            ]
            dataset_id = DatasetKey(game_id=game_id, full_file=from_source)
    # 3. Whether we use a file for source or not, we then consider any specification of a player ID, session ID, or date range.
        # a. Case where specific player ID was given
        elif player_id is not None and player_id != "":
            filters.IDFilters.Players = SetFilter(mode=FilterMode.INCLUDE, set_elements={player_id})
            dataset_id = DatasetKey(game_id=game_id, player_id=player_id)
        # b. Case where player ID file was given
        elif player_id_file is not None and player_id_file != "":
            file_path = Path(player_id_file)
            with open(file_path, encoding="UTF-8") as player_file:
                reader = csv.reader(player_file)
                file_contents = list(reader) # this gives list of lines, each line a list
                names = set(chain.from_iterable(file_contents)) # so, convert to single list
                print(f"list of names: {list(names)}")
                filters.IDFilters.Players = SetFilter(mode=FilterMode.INCLUDE, set_elements=names)
            dataset_id = DatasetKey(game_id=game_id, player_id_file=file_path)
        # c. Case where specific session ID was given
        elif session_id is not None and session_id != "":
            filters.IDFilters.Sessions = SetFilter(mode=FilterMode.INCLUDE, set_elements={session_id})
            dataset_id = DatasetKey(game_id=game_id, session_id=session_id)
        # d. Case where session ID file was given
        elif session_id_file is not None and session_id_file != "":
            file_path = Path(session_id_file)
            with open(file_path, encoding="UTF-8") as session_file:
                reader = csv.reader(session_file)
                file_contents = list(reader) # this gives list of lines, each line a list
                names = set(chain.from_iterable(file_contents)) # so, convert to single list
                print(f"list of sessions: {list(names)}")
                filters.IDFilters.Sessions = SetFilter(mode=FilterMode.INCLUDE, set_elements=names)
            dataset_id = DatasetKey(game_id=game_id, session_id_file=session_id_file)
        # e. Default case where we use date range
        else:
            start_date = parse(timestr=args.start_date, dayfirst=False).date()
            end_date   = parse(timestr=args.end_date, dayfirst=False).date()
            filters.Sequences.Timestamps = OGDGenerators.GenDateFilter(game=game_id, monthly=args.monthly, start_date=start_date, end_date=end_date)
            dataset_id = DatasetKey(game_id=game_id, from_date=start_date, to_date=end_date)
    # 3. set up the outerface, based on the range and dataset_id.
        game_source_mapping[game_id].EventsTo = [
            DataTableConfig(name="EventDestination",
                                store_name=None,
                                schema_name=None,
                                table_location=None,
                                store_config=FileStoreConfig(name="OutputFile", location=destination / game_id / f"{dataset_id}.tsv", file_credential=None),
                                table_schema=EventTableSchema.Load(schema_name="OGD_EVENT_FILE")
            )
        ]
        game_source_mapping[game_id].FeaturesTo = [
            DataTableConfig(name="FeatDestination",
                                store_name=None,
                                schema_name=None,
                                table_location=None,
                                store_config=FileStoreConfig(name="OutputFile", location=destination / game_id / f"{dataset_id}_features.tsv", file_credential=None),
                                table_schema=FeatureTableSchema.Load(schema_name="OGD_FEATURE_FILE")
            )
        ]
        # If we're in debug level of output, include a debug outerface, so we know what is *supposed* to go through the outerfaces.
        if config.DebugLevel == "DEBUG":
            cfg = DataTableConfig(name="DEBUG", store_name="Debug", schema_name=None, table_location=None)
            game_source_mapping[game_id].EventsTo.append(cfg)
            game_source_mapping[game_id].FeaturesTo.append(cfg)

    # 4. Once we have the parameters parsed out, construct the request.
        req = Request(
            exporter_modes=export_modes,
            filters=filters,
            global_cfg=config,
            game_cfg=generator_config,
            custom_dataset_key=dataset_id,
            custom_game_stores=game_source_mapping[game_id],
            custom_data_directory=repository)
        # HACK : another place where we're just hardcoded to only use the first interface in the Interfaces collection
        if list(req.Interfaces.values())[0].Connector.IsOpen:
            export_manager : ExportManager = ExportManager(config=config)
            result         : RequestResult = export_manager.ExecuteRequest(request=req)
            success = result.Status == ResultStatus.SUCCESS
            level = logging.INFO if success else logging.ERROR
            Logger.Log(message=result.Message, level=level)
            Logger.Log(f"Total data request execution time: {result.Duration}", logging.INFO)
            # cProfile.runctx("feature_exporter.ExportFromSQL(request=req)",
                            # {'req':req, 'feature_exporter':feature_exporter}, {})
        return success

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
