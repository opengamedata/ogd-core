import http
import json
import logging
import math
import mysql.connector
import typing
import datetime

def loadJSONFile(filename: str, path:str = "./"):
    if not filename.endswith(".json"):
        filename = filename + ".json"
    ret_val = None
    try:
        json_file = open(path+filename, "r")
        ret_val = json.loads(json_file.read())
        json_file.close()
    except Exception as err:
        logging.error("Could not read file at {}{}".format(path, filename))
    return ret_val

def dateToFileSafeString(date: datetime.datetime):
    return "{}-{}-{}".format(date.month, date.day, date.year)

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
               distinct: bool = False) -> typing.List[typing.Tuple]:
        d = "DISTINCT " if distinct else ""
        cols = ",".join(columns) if columns is not None and len(columns) > 0 else "*"
        table_path = db_name + "." + str(table)

        sel_clause   = "SELECT " + d + cols + " FROM " + table_path
        where_clause = "" if filter is None else " WHERE " + filter
        lim_clause   = "" if limit < 0     else " LIMIT " + str(limit)

        query = sel_clause + where_clause +  lim_clause + ";"
        logging.debug("Running query: " + query)
        cursor.execute(query)
        return cursor.fetchall()

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