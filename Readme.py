import logging
import os
import traceback
from pathlib import Path

# import local files
from ogd.common.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.common.schemas.events.LoggingSpecificationSchema import LoggingSpecificationSchema
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.utils.Logger import Logger

class Readme:
    def __init__(self, event_collection:LoggingSpecificationSchema,
                 generator_collection:GeneratorCollectionConfig,
                 table_schema:TableSchema):
        self._event_collection     : LoggingSpecificationSchema = event_collection
        self._generator_collection : GeneratorCollectionConfig  = generator_collection
        self._table_schema         : TableSchema                = table_schema
        self._custom_src           : str                        = self._getCustomSrc()
        self._dataset_meta         : str                        = self._getDatasetMetadata()
        self._changelog            : str                        = self._getDatabaseChangelog()

    @property
    def GameName(self):
        return self._event_collection.GameName

    @property
    def CustomReadmeSource(self) -> str:
        return self._custom_src

    @property
    def DatasetMetadata(self) -> str:
        return self._dataset_meta

    @property
    def DatasetChangelog(self) -> str:
        return self._changelog

    def ToFile(self, path:Path = Path("./")):
        try:
            os.makedirs(name=path, exist_ok=True)
            with open(path / "README.md", "w") as readme:
                # 1. Open files with game-specific readme data, and global db changelog.
                # 2. Use schema to write feature & column descriptions to the readme.
                readme.write("\n\n".join([
                    f"# Game: {self.GameName}",
                    self.CustomReadmeSource,
                    self.DatasetMetadata,
                    self._table_schema.AsMarkdown,
                    self._event_collection.AsMarkdown,
                    self._generator_collection.AsMarkdown,
                    self.DatasetChangelog,
                    ""
                ]))
                # 3. Append any important data from the data changelog.
        except FileNotFoundError as err:
            Logger.Log("Could not open README.md for writing.", logging.ERROR)
            traceback.print_tb(err.__traceback__)
        else:
            Logger.Log(f"Wrote readme file to {path}/README.md", logging.INFO)

    def _getCustomSrc(self) -> str:
        ret_val = "No game-specific readme content prepared"

        game_schema_dir = Path(f"./games/{self.GameName}/schemas")
        try:
            with open(game_schema_dir / f"{self.GameName}_readme_src.md", "r") as readme_src:
                ret_val = readme_src.read()
        except FileNotFoundError:
            Logger.Log(f"Could not find {self._event_collection.GameName}_readme_src", logging.WARNING)
        finally:
            return ret_val

    def _getDatasetMetadata(self) -> str:
        """Function to generate markdown-formatted metadata for a given game.
        Gives a summary of the data licensing and suggested citation,
        then adds the markdown-formatted information from game and table schemas.

        :param game_schema: [description]
        :type game_schema: GameSchema
        :param table_schema: [description]
        :type table_schema: TableConfig
        :return: A string containing metadata for the given game.
        :rtype: str
        """
        return "\n\n".join([
            "## Field Day Open Game Data",
            "\n".join([
                "Retrieved from https://fielddaylab.wisc.edu/opengamedata",
                "These anonymous data are provided in service of future educational data mining research.",
                "They are made available under the Creative Commons CCO 1.0 Universal license.",
                "See https://creativecommons.org/publicdomain/zero/1.0/",
            ]),
            "### Suggested citation",
            "#### Field Day. (2019). Open Educational Game Play Logs - [dataset ID]. Retrieved [today's date] from https://opengamedata.fielddaylab.wisc.edu/"
        ])

    def _getDatabaseChangelog(self) -> str:
        ret_val = "No changelog prepared"

        changelog_dir = Path("./schemas/")
        try:
            with open(changelog_dir / "database_changelog_src.md", "r") as changelog_src:
                ret_val = changelog_src.read()
        except FileNotFoundError:
            Logger.Log("Could not find database_changelog_src", logging.WARNING)
        finally:
            return ret_val
