import git
import json
import logging
import os
import re
import shutil
import sys
import traceback
import zipfile
from datetime import datetime
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from pathlib import Path
from typing import Any, Dict, IO, List, Optional, Set

# import local files
import utils
from interfaces.outerfaces.DataOuterface import DataOuterface
from schemas.ExtractionMode import ExtractionMode
from schemas.ExportMode import ExportMode
from schemas.configs.GameSourceMapSchema import GameSourceSchema
from schemas.games.GameSchema import GameSchema
from schemas.tables.TableSchema import TableSchema
from schemas.configs.IndexingSchema import FileIndexingSchema
from utils.Logger import Logger, ExportRow

def GenerateReadme(game_schema:GameSchema, table_schema:TableSchema, path:Path = Path("./")):
    try:
        os.makedirs(name=path, exist_ok=True)
        with open(path / "readme.md", "w") as readme:
            # 1. Open files with game-specific readme data, and global db changelog.
            game_schema_dir = Path(f"./games/{game_schema.GameName}/schemas")
            try:
                with open(game_schema_dir / f"{game_schema.GameName}_readme_src.md", "r") as readme_src:
                    readme.write(readme_src.read())
            except FileNotFoundError as err:
                readme.write("No game readme prepared")
                Logger.Log(f"Could not find {game_schema.GameName}_readme_src", logging.WARNING)
            finally:
                readme.write("\n\n")
            # 2. Use schema to write feature & column descriptions to the readme.
            meta = TSVOuterface.GenCSVMetadata(game_schema=game_schema, table_schema=table_schema)
            readme.write(meta)
            # 3. Append any important data from the data changelog.
            changelog_dir = Path(f"./schemas/")
            try:
                with open(changelog_dir / "database_changelog_src.md", "r") as changelog_src:
                    readme.write(changelog_src.read())
            except FileNotFoundError as err:
                readme.write("No changelog prepared")
                Logger.Log(f"Could not find database_changelog_src", logging.WARNING)
    except FileNotFoundError as err:
        Logger.Log(f"Could not open readme.md for writing.", logging.ERROR)
        traceback.print_tb(err.__traceback__)
    else:
        Logger.Log(f"Wrote readme file to {path}/readme.md", logging.INFO)

def GenCSVMetadata(game_schema: GameSchema, table_schema: TableSchema) -> str:
    """Function to generate markdown-formatted metadata for a given game.
    Gives a summary of the data licensing and suggested citation,
    then adds the markdown-formatted information from game and table schemas.

    :param game_schema: [description]
    :type game_schema: GameSchema
    :param table_schema: [description]
    :type table_schema: TableSchema
    :return: A string containing metadata for the given game.
    :rtype: str
    """
    template_str =\
    "\n".join(["## Field Day Open Game Data  ",
    "### Retrieved from https://fielddaylab.wisc.edu/opengamedata  ",
    "### These anonymous data are provided in service of future educational data mining research.  ",
    "### They are made available under the Creative Commons CCO 1.0 Universal license.  ",
    "### See https://creativecommons.org/publicdomain/zero/1.0/  ",
    "",
    "## Suggested citation:  ",
    "### Field Day. (2019). Open Educational Game Play Logs - [dataset ID]. Retrieved [today's date] from https://fielddaylab.wisc.edu/opengamedata  ",
    "",
    f"# Game: {game_schema._game_name}  ",
    "",
    "## Field Descriptions:  \n",
    f"{table_schema.AsMarkdown}",
    "",
    f"{game_schema.AsMarkdown}",
    ""])
    return template_str
