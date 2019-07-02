# library imports
import bisect
import logging
import json
# local file imports
import utils

class WaveFeature:
    _feature_list = [
        "totalSliderMoves",     # slider moves across a given level
        "totalLevelTime",       # time spent on a level
        "totalKnobStdDevs",     # sum of stdev_val for all slider moves in a level
        "totalMoveTypeChanges", # number of times "slider" changes across a level
        "totalKnobAvgMaxMin",   # difference between max and min values of a slider move
        "totalOffsetMoves",     # number of times the offset is adjusted
        "totalWavelengthMoves", # number of times the wavelength is adjusted
        "totalAmplitudeMoves",  # number of times the amplitude is adjusted
        "totalFails",           # number of "Fail" events
        "avgSliderMoves",
        "avgLevelTime",
        "avgKnobStdDevs",
        "avgMoveTypeChanges",
        "avgKnobAvgMaxMin",
        "avgOffsetMoves",
        "avgWavelengthMoves",
        "avgAmplitudeMoves",
        "avgFails",
        "avgPercentOffset",
        "avgPercentAmplitude",
        "avgPercentWavelength"
    ]

    _db_columns = [
        "id",
        "app_id",
        "app_id_fast",
        "app_version",
        "session_id",
        "persistent_session_id",
        "level",
        "event",
        "event_custom",
        "event_data_simple",
        "event_data_complex",
        "client_time",
        "client_time_ms",
        "server_time",
        "req_id",
        "session_n",
        "http_user_agent",
    ]

    _event_data_complex_types = None
    _event_data_complex_schemas = None

    @staticmethod
    def initializeClass(schema_path:str = "./schemas/", schema_name:str = "WAVES.json"):
        schema = utils.loadJSONFile(schema_name, schema_path)
        if schema is None:
            logging.error("Could not find wave event_data_complex schemas at {}".format(schema_path))
        else:
            _event_data_complex_types = schema["schemas"].keys()
            _event_data_complex_schemas = schema["schemas"]

    def __init__(self):
        self.levels = []
        self.start_times = {}
        self.end_times = {}
        self.features = { f:{} for f in WaveFeature._feature_list }

    def extractFromRow(self, level:int, event_data_complex_parsed, event_client_time):
        if "event_custom" not in event_data_complex_parsed.keys():
            logging.error("Invalid event_data_complex, does not contain event_custom field!")
        else:
            if not level in self.levels:
                i = bisect.insort(self.levels, level)
            # handle cases for each type of event
            if event_data_complex_parsed["event_custom"] == "BEGIN":
                self.start_times[level] = event_client_time
            if event_data_complex_parsed["event_custom"] == "COMPLETE":
                self.end_times[level] = event_client_time
            elif event_data_complex_parsed["event_custom"] == "SUCCEED":
                pass
            elif event_data_complex_parsed["event_custom"] == "FAIL":
                self.features["totalFails"] += 1
            elif event_data_complex_parsed["event_custom"] == "SLIDER_MOVE_RELEASE":
                self.features["totalSliderMoves"] += 1
            elif event_data_complex_parsed["event_custom"] == "ARROW_MOVE_RELEASE":
