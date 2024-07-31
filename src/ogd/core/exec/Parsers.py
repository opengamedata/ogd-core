"""Module for setting up parsers for the OGD CLI"""
# import standard libraries
from argparse import ArgumentParser, SUPPRESS
from typing import List

# import 3rd-party libraries

# import OGD files

class OGDParsers:
    """Utility class to collect functions for setting up each of the parsers that are used by the various commands."""

    # *** BUILT-INS & PROPERTIES ***

    # *** PUBLIC STATICS ***

    @staticmethod
    def CommandParser(games_list:List[str]) -> ArgumentParser:
        """Create an arg parser for getting top-level command.

        Available commands are:
        * export
        * export-events
        * export-features
        * info
        * readme
        * list-games

        :param games_list: List of games available for export.
        :type games_list: List[str]
        :return: A parser that recognizes the available top-level commands
        :rtype: ArgumentParser
        """
        game_parser = OGDParsers.GameParser(games_list=games_list) 
        export_parser = OGDParsers.ExportParser(parents=[game_parser])
        destination_parser = OGDParsers.DestinationParser()

        parser = ArgumentParser(description="Simple command-line utility to execute OpenGameData export requests.")
        sub_parsers = parser.add_subparsers(help="Chosen command to run", dest="command")
        sub_parsers.add_parser("export", parents=[export_parser, destination_parser],
                                help="Export data in a given date range.")
        sub_parsers.add_parser("export-events", parents=[export_parser, destination_parser],
                                help="Export event data in a given date range.")
        sub_parsers.add_parser("export-features", parents=[export_parser, destination_parser],
                                help="Export session feature data in a given date range.")
        sub_parsers.add_parser("info", parents=[game_parser],
                                help="Display info about the given game.")
        sub_parsers.add_parser("readme", parents=[game_parser, destination_parser],
                                help="Generate a readme for the given game.")
        sub_parsers.add_parser("list-games",
                                help="Display a list of games available for parsing.")
        # sub_parsers.add_parser("help",
        #                         help="Display a list of games available for parsing.")
        return parser

    @staticmethod
    def ExportParser(parents:List[ArgumentParser]) -> ArgumentParser:
        """Create an arg parser for getting parameters specific to export commands.

        Available parameters are:
        * start_date
        * end_date
        * --player
        * --session
        * --player_id_file
        * --session_id_file
        * --file
        * --monthly
        * --no_session_file
        * --no_player_file
        * --no_pop_file

        :param parents: The parent parser(s) that the export parsers contributes to.
        :type parents: List[ArgumentParser]
        :return: A parser that recognizes the available export parameters.
        :rtype: ArgumentParser
        """
        export_parser = ArgumentParser(add_help=False, parents=parents)
        export_parser.add_argument("start_date", nargs="?", default=None,
                            help="The starting date of an export range in MM/DD/YYYY format (defaults to today).")
        export_parser.add_argument("end_date", nargs="?", default=None,
                            help="The ending date of an export range in MM/DD/YYYY format (defaults to today).")
        export_parser.add_argument("-p", "--player", default="",
                            help="Tell the program to output data for a player with given ID, instead of using a date range.")
        export_parser.add_argument("-s", "--session", default="",
                            help="Tell the program to output data for a session with given ID, instead of using a date range.")
        export_parser.add_argument("--player_id_file", default="",
                            help="Tell the program to output data for a collection of players with IDs in given file, instead of using a date range.")
        export_parser.add_argument("--session_id_file", default="",
                            help="Tell the program to output data for a collection of sessions with IDs in given file, instead of using a date range.")
        export_parser.add_argument("-f", "--file", default="",
                            help="Tell the program to use a file as input, instead of looking up a database.")
        export_parser.add_argument("-m", "--monthly", default=False, action="store_true",
                            help="Set the program to export a month's-worth of data, instead of using a date range. Replace the start_date argument with a month in MM/YYYY format.")
        # allow individual feature files to be skipped.
        export_parser.add_argument("--no_session_file", default=False, action="store_true",
                            help="Tell the program to skip outputting a per-session file.")
        export_parser.add_argument("--no_player_file", default=False, action="store_true",
                            help="Tell the program to skip outputting a per-player file.")
        export_parser.add_argument("--no_pop_file", default=False, action="store_true",
                            help="Tell the program to skip outputting a population file.")
        return export_parser

    @staticmethod
    def DestinationParser() -> ArgumentParser:
        """Create an arg parser for getting a destination parameter for various commands.

        Available parameters are:

        * --destination

        :return: A parser that recognizes the available `destination` parameter.
        :rtype: ArgumentParser
        """
        destination_parser = ArgumentParser(add_help=False)
        destination_parser.add_argument("-d", "--destination", default=SUPPRESS, type=str,
                            help="The destination folder for the readme.")
        return destination_parser

    @staticmethod
    def GameParser(games_list:List[str]) -> ArgumentParser:
        """Create an arg parser for getting a game parameter for various commands

        Available parameters are:
        
        * game

        :param games_list: List of games available for export.
        :type games_list: List[str]
        :return: A parser that recognizes the available `game` parameter.
        :rtype: ArgumentParser
        """
        game_parser = ArgumentParser(add_help=False)
        game_parser.add_argument("game", type=str.upper, choices=games_list,
                            help="The game to use with the given command.")
        return game_parser

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
