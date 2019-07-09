# import standard libraries
import json
import logging
import typing
# import local files
import utils
from game_features.WaveFeature import WaveFeature
from Request import Request

def exportDataToCSV(request: Request, db, settings):
    DATA_DIR = settings["DATA_DIR"] + request.game_id
    db_settings = settings["db_config"]
    if request.game_id is not None:

        parse_result = getAndParseData(request, db, db_settings, DATA_DIR)
        
        # output results
        if parse_result is not None:
            try:
                print(json.dumps(parse_result))
            except Exception as err:
                utils.SQL.server500Error(err)
    else:
        logging.error("Game ID was not given!")

def getAndParseData(request: Request, db, settings, data_directory):
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
    
    max_level_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                     columns=["MAX(level)"], filter="app_id=\"{}\"".format(request.game_id),
                                     distinct=True)
    max_level = max_level_raw[0][0]
    min_level_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                     columns=["MIN(level)"], filter="app_id=\"{}\"".format(request.game_id),
                                     distinct=True)
    min_level = min_level_raw[0][0]
    # logging.debug("max_level: " + str(max_level))

    # event_counts_by_session = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                    #    columns=["session_id", "COUNT(*) as event_count"], filter="app_id=\"{}\"".format(request.game_id),
                                    #    grouping="session_id", distinct=False)
    # logging.debug("event counts by session ID: " + str(event_counts_by_session))
    # logging.debug("Number of sessions: " + str(len(event_counts_by_session)))
    # sliced_by_session = [event_counts_by_session[i*1000:min((i+1)*1000, len(event_counts_by_session)-1)] for i in range(0,16)]
    # counts_by_slice = [[elem[1] for elem in next_slice] for next_slice in sliced_by_session]
    # logging.debug("events by 1000 ids" + str([sum(next_slice) for next_slice in counts_by_slice]))

    session_ids_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                       columns=["session_id"], filter="app_id=\"{}\"".format(request.game_id),
                                       distinct=True, limit=1)
    session_ids = [sess[0] for sess in session_ids_raw]
    logging.debug("session_ids: " + str(session_ids))

    db_cursor.execute("SHOW COLUMNS from {}.{}".format(db.database, settings["table"]))
    col_names = [col[0] for col in db_cursor.fetchall()]

    complex_data_index = col_names.index("event_data_complex")
    logging.debug("complex_data_index: {}".format(complex_data_index))
    ## NOTE: Some code that could be useful to refer to if we ever decide to do something to unwrap
    ## the event_data_complex column.
    # parsed_columns = db_cursor.column_names[0:complex_data_index]                 \
    #                + tuple(json.loads(single_elem[0][complex_data_index]).keys()) \
    #                + db_cursor.column_names[complex_data_index+1:-1]

    WaveFeature.initializeClass("./game_features/schemas/", "WAVES.json")

    raw_csv_file = open("{}/{}_{}_raw.csv".format(data_directory, utils.dateToFileSafeString(request.start_date),
                                               utils.dateToFileSafeString(request.end_date)), "w")
    proc_csv_file = open("{}/{}_{}_proc.csv".format(data_directory, utils.dateToFileSafeString(request.start_date),
                                                 utils.dateToFileSafeString(request.end_date)), "w")
    raw_metadata = utils.csvMetadata(game_name=request.game_id, begin_date=request.start_date, end_date=request.end_date,
                                      field_list=WaveFeature.schema["db_columns"])
    feature_descriptions = {**WaveFeature.schema["features"]["perlevel"], **WaveFeature.schema["features"]["aggregate"]}
    proc_metadata = utils.csvMetadata(game_name=request.game_id, begin_date=request.start_date, end_date=request.end_date,
                                      field_list=feature_descriptions)

    # after generating the metadata, write to each file
    raw_csv_file.write(raw_metadata)
    proc_csv_file.write(proc_metadata)
    # then write the column headers for the raw csv. We'll get the processed csv later.
    raw_csv_file.write(",".join(col_names) + "\n")
    session_features = []
    for sess_id in session_ids:
        # initialize vars for session data.
        # each data variable maps level numbers to values for the given level.
        features = WaveFeature(max_level, min_level)
        raw_csv_lines = []

        # grab data for the given session.
        next_data_set = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                         filter="app_id=\"WAVES\" AND session_id={}".format(sess_id),
                                         sort_columns=["client_time"], sort_direction = "ASC",
                                         distinct=False)

        # now, we process each row.
        for row in next_data_set:
            raw_csv_lines.append(",".join([str(elem) for elem in row]))
            complex_data = row[complex_data_index]
            complex_data_parsed = json.loads(complex_data) if (complex_data is not None) else {"event_custom":row[col_names.index("event")]}
            # use function in the "features" var to pull features from each row
            features.extractFromRow(row[col_names.index("level")], complex_data_parsed, row[col_names.index("client_time")])
        features.calculateAggregateFeatures()
        session_features.append(features)
        
        # after processing all rows, write out the session data.
        raw_csv_file.write("\n".join(raw_csv_lines))
        raw_csv_file.write("\n")

    # Use functions from the feature class to write actual data
    session_features[0].writeCSVHeader(proc_csv_file)
    for session in session_features:
        session.writeCurrentFeatures(proc_csv_file)

        ## NOTE: Some code that could be useful to refer to if we ever decide to do something to unwrap
        ## the event_data_complex column.
        # parsed_data = []
        # for row in next_data_set:
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