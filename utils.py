import http
import json
import logging
import math
import mysql.connector
import typing
import datetime

import os

def loadJSONFile(filename: str, path:str = "./"):
    if not filename.endswith(".json"):
        filename = filename + ".json"
    ret_val = None
    try:
        json_file = open(path+filename, "r")
        ret_val = json.loads(json_file.read())
        json_file.close()
    except Exception as err:
        logging.error("Could not read file at {}\nFull error message: {}\nCurrent directory: {}".format(path+filename, str(err), os.getcwd()))
    return ret_val

def dateToFileSafeString(date: datetime.datetime):
    return "{}-{}-{}".format(date.month, date.day, date.year)

def csvMetadata(game_name: str, begin_date: datetime.datetime, end_date: datetime.datetime,
                      field_list: dict) -> str:
    template_str = \
    "## Field Day Open Game Data \n\
# Retrieved from https://fielddaylab.wisc.edu/opengamedata \n\
# These anonymous data are provided in service of future educational data mining research. \n\
# They are made available under the Creative Commons CCO 1.0 Universal license. \n\
# See https://creativecommons.org/publicdomain/zero/1.0/ \n\
\n\
## Suggested citation: \n\
# Field Day. (2019). Open Educational Game Play Logs - [dataset ID]. Retrieved [today's date] from https://fielddaylab.wisc.edu/opengamedata \n\
\n\
## Game: {0} \n\
# Begin Date: {1} \n\
# End Date: {2} \n\
\n\
## Field Descriptions: \n".format(game_name, begin_date, end_date)
    field_descriptions = ["# {0} - {1}".format(key, field_list[key]) for key in field_list.keys()]
    template_str += "\n".join(field_descriptions)
    template_str += "\n"
    return template_str

# class Numeric:
#     @staticmethod
#     def replaceNans(arr: typing.Dict) -> typing.Dict:
#         ret_val = arr
#         for key in ret_val.keys():
#             if type(ret_val[key]) is dict:
#                  ret_val[key] = Numeric.replaceNans(ret_val[key])
#             elif type(ret_val[key]) is not str and math.isnan(ret_val[key]):
#                 ret_val[key] = 'NaN'
#             elif type(ret_val[key]) is not str and math.isinf(ret_val[key]):
#                 ret_val[key] = 'Inf'
#         return ret_val

class SQL:
    @staticmethod
    def connectToMySQL(host: str, port: int, user: str, pword: str, db_name: str):
        try:
            return mysql.connector.connect(host = host, port = port, user = user, password = pword, database = db_name)
        except mysql.connector.Error as err:
            print("Error connecting to MySql database: " + str(err))

    @staticmethod
    def SELECT(cursor: mysql.connector.cursor.MySQLCursor, db_name: str, table: str,
               columns: typing.List[str] = None, filter: str = None, limit: int = -1,
               sort_columns: typing.List[str] = None, sort_direction = "ASC", grouping: str = None,
               distinct: bool = False, fetch_results: bool = True) -> typing.List[typing.Tuple]:
        d = "DISTINCT " if distinct else ""
        cols      = ",".join(columns)      if columns is not None      and len(columns) > 0      else "*"
        sort_cols = ",".join(sort_columns) if sort_columns is not None and len(sort_columns) > 0 else None
        table_path = db_name + "." + str(table)

        sel_clause   = "SELECT " + d + cols + " FROM " + table_path
        where_clause = "" if filter    is None else " WHERE {}".format(filter)
        group_clause = "" if grouping  is None else " GROUP BY {}".format(grouping)
        sort_clause  = "" if sort_cols is None else " ORDER BY {} {} ".format(sort_cols, sort_direction)
        lim_clause   = "" if limit < 0         else " LIMIT {}".format(str(limit))

        query = sel_clause + where_clause + group_clause + sort_clause + lim_clause + ";"
        logging.debug("Running query: " + query)
        cursor.execute(query)
        return cursor.fetchall() if fetch_results else None

    @staticmethod
    def server500Error(error: Exception):
        logging.error("HTTP Response: " + http.HTTPStatus.INTERNAL_SERVER_ERROR.value \
                                + http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase )
        print(str(error))

# def run_tests():
#     fails = []
#     test_data = {}
#     # add test data below as follows:
#     # create list of tuples, where each tuple has function args as first input, and expected output as second.
#     # Finally, map function name as string to the list, and everything else goes automatically.