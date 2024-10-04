# import standard libraries
import cProfile
import pstats
#import datetime
import argparse
import os
import sys
from argparse import Namespace
from pathlib import Path

# import 3rd-party libraries

# import local files
from config.config import settings
import_path = Path(".") / "src"
sys.path.insert(0, str(import_path))
from ogd.common.utils.Logger import Logger
from src.ogd import games
from src.ogd.core.exec.Commands import OGDCommands
from src.ogd.core.exec.Parsers import OGDParsers
from src.ogd.core.schemas.configs.ConfigSchema import ConfigSchema


## This section of code is what runs main itself. Just need something to get it
#  started.
config = ConfigSchema(name="config.py", all_elements=settings)
Logger.InitializeLogger(level=config.DebugLevel, use_logfile=config.UseLogFile)
# Logger.Log(f"Running {sys.argv[0]}...", logging.INFO)
# set up parent parsers with arguments for each class of command
games_folder : Path = Path(games.__file__) if Path(games.__file__).is_dir() else Path(games.__file__).parent
games_list = [name.upper() for name in os.listdir(games_folder) if (os.path.isdir(games_folder / name) and name != "__pycache__")]
# set up main parser, with one sub-parser per-command.
parser = OGDParsers.CommandParser(games_list=games_list)

args : Namespace = parser.parse_args()


success : bool
if config.WithProfiling:
    profiler = cProfile.Profile()
    profiler.enable()
if args is not None:
    cmd = (args.command or "help").lower()
    dest = Path(args.destination if args.destination != "" else "./") if 'destination' in args else config.DataDirectory
    match cmd:
        case "export":
            success = OGDCommands.RunExport(args=args, config=config, destination=dest, with_events=True, with_features=True)
        case "export-events":
            success = OGDCommands.RunExport(args=args, config=config, destination=dest, with_events=True)
        case "export-features":
            success = OGDCommands.RunExport(args=args, config=config, destination=dest, with_features=True)
        case "info":
            success = OGDCommands.ShowGameInfo(config=config, game=args.game)
        case "readme":
            success = OGDCommands.WriteReadme(config=config, game=args.game, destination=dest)
        case "list-games":
            success = OGDCommands.ListGames(games_list=games_list)
        # case "help":
        #     success = ShowHelp()
        case _:
            print(f"Invalid Command {cmd}!")
            success = False
else:
    print(f"Need to enter a command!")
    success = False
if config.WithProfiling:
    profiler.disable()
    profile = pstats.Stats(profiler)
    profile.sort_stats(pstats.SortKey.CUMULATIVE).print_stats('ogd', .1)

if not success:
    sys.exit(1)
