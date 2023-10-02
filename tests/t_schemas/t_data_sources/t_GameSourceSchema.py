# import libraries
from pathlib import Path
from typing import Dict, List
from unittest import TestCase
# import locals
from schemas.ExportMode import ExportMode
from schemas.data_sources.DataHostConfig import DataHostConfig
from schemas.data_sources.GameSourceSchema import GameSourceSchema
from schemas.data_sources.MySQLHostConfig import MySQLSchema

class t_GameSourceSchema(TestCase):


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
        source_element = {
            "AQUALAB":        { "source":"OPENGAMEDATA_BQ",    "database":"aqualab",             "table":"aqualab_daily",        "schema":"OPENGAMEDATA_BIGQUERY" },
        }
        dest_element   = {
            "AQUALAB":        { "destination":"OPENGAMEDATA_MYSQL_FEATURES", "database":"opengamedata", "table":"aqualab",        "schema":"OPENGAMEDATA_BIGQUERY" },
        }
        app_id = "AQUALAB"
        source_schema = GameSourceSchema(name=app_id, all_elements=source_element[app_id], data_sources=data_sources)
        dest_schema   = GameSourceSchema(name=app_id, all_elements=dest_element[app_id],   data_sources=data_sources)

        print("Ran all t_GameSourceSchema tests.")

if __name__ == '__main__':
    t_GameSourceSchema.RunAll()
