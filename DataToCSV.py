## import standard libraries
import json
import logging
import math
import typing
## import local files
import utils
from BatchData import BatchData
from Request import Request
from game_features.WaveFeature import WaveFeature

def exportDataToCSV(request: Request, db, settings):
    db_settings = settings["db_config"]
    if request.game_id is not None:
        batch_data: BatchData = _getBatchData(request, db, db_settings)

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

        parse_result: str = _getAndParseData(request, batch_data, db, settings)
        
        # output results
        if parse_result is not None:
            try:
                print(json.dumps(parse_result))
            except Exception as err:
                utils.SQL.server500Error(err)
    else:
        logging.error("Game ID was not given!")

def _getBatchData(request: Request, db, settings) -> BatchData:
    db_cursor = db.cursor(buffered=True)
    ## grab the min and max levels from the database, for later use.
    max_min_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                    columns=["MAX(level)", "MIN(level)"], filter="app_id=\"{}\"".format(request.game_id),
                                    distinct=True)
    max_level = max_min_raw[0][0]
    min_level = max_min_raw[0][1]
    # logging.debug("max_level: " + str(max_level))

    # We grab the ids for all sessions that have 0th move in the proper date range.
    session_ids_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                    columns=["session_id"], filter="app_id=\"{}\" AND session_n=0 AND (server_time BETWEEN '{}' AND '{}')".format( \
                                                                    request.game_id, request.start_date.isoformat(), request.end_date.isoformat()),
                                    sort_columns=["session_id"], sort_direction="ASC", distinct=True, limit=request.max_sessions)
    session_ids = [sess[0] for sess in session_ids_raw]
    # logging.debug("session_ids: " + str(session_ids))

    db_cursor.execute("SHOW COLUMNS from {}.{}".format(db.database, settings["table"]))
    col_names = [col[0] for col in db_cursor.fetchall()]

    return BatchData(col_names, max_level, min_level, session_ids)

def _getAndParseData(request: Request, batch_data: BatchData, db, settings):
    db_cursor = db.cursor(buffered=True)
    data_directory = settings["DATA_DIR"] + request.game_id
    db_settings = settings["db_config"]
    
    # logging.debug("complex_data_index: {}".format(complex_data_index))
    ## NOTE: Some code that could be useful to refer to if we ever decide to do something to unwrap
    ## the event_data_complex column.
    # parsed_columns = db_cursor.column_names[0:complex_data_index]                 \
    #                + tuple(json.loads(single_elem[0][complex_data_index]).keys()) \
    #                + db_cursor.column_names[complex_data_index+1:-1]

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
    raw_csv_file.write(",".join(batch_data.column_names) + "\n")
    all_sessions = []
    num_sess = len(batch_data.session_ids)
    slice_size = settings["BATCH_SIZE"]
    session_slices = [[batch_data.session_ids[i] for i in \
                     range( j*slice_size, min((j+1)*slice_size - 1, num_sess) )] for j in \
                     range( 0, math.ceil(num_sess / slice_size) )]
    for next_slice in session_slices:
        # grab data for the given session range. Sort by event time, so 
        filt = "app_id=\"WAVES\" AND session_id BETWEEN {} AND {}".format(next_slice[0], next_slice[-1])
        next_data_set = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=db_settings["table"],
                                        filter= filt, sort_columns=["client_time"], sort_direction = "ASC",
                                        distinct=False)
        # initialize vars for session data.
        # each data variable maps level numbers to values for the given level.
        slice_features = {sess_id:WaveFeature(sess_id, batch_data.max_level, batch_data.min_level) for sess_id in next_slice}
        raw_csv_lines = []


        # now, we process each row.
        for row in next_data_set:
            session_id = row[batch_data.session_id_index]
            if session_id in batch_data.session_ids:
                raw_csv_lines.append(",".join([str(elem) for elem in row]))
                complex_data_json = row[batch_data.complex_data_index]
                complex_data_parsed = json.loads(complex_data_json) if (complex_data_json is not None) else {"event_custom":row[batch_data.event_index]}
                # use function in the "features" var to pull features from each row
                slice_features[session_id].extractFromRow(row[batch_data.level_index], complex_data_parsed, row[batch_data.client_time_index])
            else:
                logging.warn("Found a session which was in the slice but not in the list of sessions for processing.")
        for session_features in slice_features.values():
            session_features.calculateAggregateFeatures()
            all_sessions.append(session_features)
        
        # after processing all rows, write out the session data.
        raw_csv_file.write("\n".join(raw_csv_lines))
        raw_csv_file.write("\n")

    # Use functions from the feature class to write actual data
    all_sessions[0].writeCSVHeader(proc_csv_file)
    for session in all_sessions:
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