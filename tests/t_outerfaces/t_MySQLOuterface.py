# import libraries
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from unittest import TestCase
from zipfile import ZipFile
# import locals
from schemas.Event import Event
from schemas.ExportMode import ExportMode
from interfaces.outerfaces.MySQLOuterface import MySQLOuterface
from schemas.data_sources.DataHostConfig import DataHostConfig
from schemas.data_sources.MySQLHostConfig import MySQLSchema
from schemas.data_sources.GameSourceSchema import GameSourceSchema

class t_CSVInterface(TestCase):

    zipped_file = ZipFile(Path("tests/t_interfaces/BACTERIA_20210201_to_20210202_5c61198_events.zip"))

    @staticmethod
    def RunAll():
        mysql_schema_elems = {
            "DB_TYPE" : "MySQL",
            "DB_HOST" : "127.0.0.1",
            "DB_PORT" : 3306,
            "DB_USER" : "username",
            "DB_PW"   : "password",
            "SSH_HOST": "hostname",
            "SSH_USER": "WCER AD User",
            "SSH_PASS": "WCER AD Password"
        }
        data_sources : Dict[str, DataHostConfig] = {
            "MySQL" : MySQLSchema(name="MySQL", all_elements=mysql_schema_elems)
        }
        game_source_elems = {
            "source"   : "MySQL",
            "database" : "database_name",
            "table"    : "table_name",
            "schema"   : "OPENGAMEDATA_BIGQUERY"
        }
        config = GameSourceSchema(name="WAVES", all_elements=game_source_elems, data_sources=data_sources)

        export_modes = {ExportMode.POPULATION, ExportMode.PLAYER, ExportMode.SESSION}
        outerface = MySQLOuterface(game_id="WAVES", config=config, export_modes=export_modes)
        outerface.Open()
        # Load (or hardcode) the sample data, for now we've got session data
        sample_data : List[Event] = []
        mode        : ExportMode  = ExportMode.SESSION

        outerface.WriteLines(lines=sample_data, mode=mode)
        print("Ran all t_CSVInterface tests.")

if __name__ == '__main__':
    t_CSVInterface.RunAll()
