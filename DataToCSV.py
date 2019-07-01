# import standard libraries
import json
import logging
import typing
# import local files
import utils
from Request import Request

def dataToCSV(request: Request, db, settings):
    DATA_DIR = settings["DATA_DIR"] + request.game_id
    db_settings = settings["db_config"]
    if request.game_id is not None:
        # TODO: Should we get model file still? Not sure what it's used for.
        model = utils.loadJSONFile("../model.json")
        # TODO: figure out if these are even needed.
        SQL_QUESTION_CUSTOM = model[request.game_id]['sqlEventCustoms']['question']
        SQL_MOVE_CUSTOM = model[request.game_id]['sqlEventCustoms']['move']
        SQL_OTHER_CUSTOMS = model[request.game_id]['sqlEventCustoms']['other']

        parse_result = getAndParseData(request, model, db, db_settings, DATA_DIR)
        
        # output results
        if parse_result is not None:
            try:
                print(json.dumps(parse_result))
            except Exception as err:
                utils.SQL.server500Error(err)
    else:
        logging.error("Game ID was not given!")

def getAndParseData(request: Request, model, db, settings, data_directory):
    db_cursor = db.cursor(buffered=True)

    ## NOTE: I've left the bit of cache code ported from the old logger,
    ## on the off chance we ever decide to use caching again.
    # if request.read_cache:
    #     cache_query = "SELECT output FROM cache WHERE filter=%s ORDER BY time DESC LIMIT 1"
    #     cache_params = [request]
    #     try:
    #         db_cursor.execute(cache_query, cache_params)
    #         cache_result = db_cursor.fetchall()
    #         if cache_result is not []:
    #             logger.debug("cache_result: " + str(cache_result))
    #             quit()
    #     except Exception as err:
    #         utils.SQL.server500Error(err)
    
    max_level = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                 columns=["MAX(level)"], filter="app_id=\"WAVES\"", distinct=True)
    # logging.debug("max_level: " + str(max_level))

    session_ids = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                   columns=["session_id"],
                                   filter="app_id=\"WAVES\"", limit=4, distinct=True)
    # logging.debug("session_ids: " + str(session_ids))

    db_cursor.execute("SHOW COLUMNS from {}.{}".format(db.database, settings["table"]))
    col_names = [col[0] for col in db_cursor.fetchall()]

    complex_data_index = col_names.index("event_data_complex")
    logging.debug("complex_data_index: {}".format(complex_data_index))

    ## NOTE: Some code that could be useful to refer to if we ever decide to do something to unwrap
    ## the event_data_complex column.
    # parsed_columns = db_cursor.column_names[0:complex_data_index]                 \
    #                + tuple(json.loads(single_elem[0][complex_data_index]).keys()) \
    #                + db_cursor.column_names[complex_data_index+1:-1]

    raw_csv_file = open("{}/{}_{}_raw.csv".format(data_directory, utils.dateToFileSafeString(request.start_date),
                                               utils.dateToFileSafeString(request.end_date)), "w")
    proc_csv_file = open("{}/{}_{}_proc.csv".format(data_directory, utils.dateToFileSafeString(request.start_date),
                                                 utils.dateToFileSafeString(request.end_date)), "w")

    raw_csv_file.write(",".join(col_names))
    for elem in session_ids:
        next_data_set = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                   filter="app_id=\"WAVES\" AND session_id={}".format(elem[0]),
                                   limit=3, distinct=True)
        # logging.debug("next_data_set: " + str(next_data_set))
        logging.debug("number of rows expected: " + str(len(next_data_set)))
        csv_lines = []
        for row in next_data_set:
            csv_lines.append(",".join([str(elem) for elem in row]))
        logging.debug("actual number of rows: " + str(len(csv_lines)))
        raw_csv_file.write("\n".join(csv_lines))
        raw_csv_file.write("\n")
        # logging.debug("formatted data: " + "\n".join(csv_lines))

        ## NOTE: Some code that could be useful to refer to if we ever decide to do something to unwrap
        ## the event_data_complex column.
        # parsed_data = []
        # for row in next_data_set:
            # complex_data = row[complex_data_index]
        #     if (complex_data is not None):
        #         complex_data_parsed = json.loads(complex_data)
        #         parsed_data.append( row[0:complex_data_index] \
        #                         + tuple(complex_data_parsed.values()) \
        #                         + row[complex_data_index+1:-1] )
        # stringified_rows = [str(elem) for elem in row]
        # csv_lines = [",".join(stringified_rows) for row in parsed_data]
    
    ## NOTE: I've left the bit of cache code ported from the old logger,
    ## on the off chance we ever decide to use caching again.
    # if request.write_cache:
    #     cache_query = "INSERT INTO cache (filter, output) VALUES (%s, %s)"
    #     cache_params = [request, ret_val]
    #     try:
    #         db_cursor.execute(cache_query, cache_params)
    #     except Exception as err:
    #         utils.SQL.server500Error(logger, err)

    return "Successfully completed."