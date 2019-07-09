# library imports
import bisect
import datetime
import json
import logging
import typing
# local file imports
import utils

class WaveFeature:
    _feature_list:               typing.Dict      = None
    db_columns:                 typing.Dict = None
    _event_data_complex_types:   typing.List[str] = None
    _event_data_complex_schemas: typing.Dict      = None
    schema:                     typing.Dict      = {}
    _initialized:                bool             = False

    @staticmethod
    def initializeClass(schema_path:str = "./schemas/", schema_name:str = "WAVES.json"):
        logging.basicConfig(level=logging.DEBUG)
        logging.info("called initializeClass")
        WaveFeature.schema = utils.loadJSONFile(schema_name, schema_path)
        if WaveFeature.schema is None:
            logging.error("Could not find wave event_data_complex schemas at {}".format(schema_path))
        else:
            _event_data_complex_types = WaveFeature.schema["schemas"].keys()
            _event_data_complex_schemas = WaveFeature.schema["schemas"]
            _feature_list = list(WaveFeature.schema["features"]["perlevel"].keys()) + list(WaveFeature.schema["features"]["aggregate"].keys())
            db_columns = WaveFeature.schema["db_columns"]
        WaveFeature._initialized = True

    def __init__(self, max_level:int, min_level:int):
        if not WaveFeature._initialized:
            WaveFeature.initializeClass()
        self.last_adjust_type: str          = None
        self.max_level:   int               = max_level
        self.min_level:   int               = min_level
        self.levels:      typing.List[int]  = []
        self.start_times: typing.Dict       = {}
        self.end_times:   typing.Dict       = {}
        # construct features as a dictionary that maps each per-level feature to a sub-dictionary,
        # which maps each level to a value.
        logging.info("schema keys: " + str(WaveFeature.schema.keys()))
        self.features:    typing.Dict       = { f:{lvl:0 for lvl in range(self.min_level,self.max_level+1)} for f in WaveFeature.schema["features"]["perlevel"] }
        # then, add in aggregate-only features.
        self.features.update({f:0 for f in WaveFeature.schema["features"]["aggregate"]})

    def extractFromRow(self, level:int, event_data_complex_parsed, event_client_time: datetime.datetime):
        if "event_custom" not in event_data_complex_parsed.keys():
            logging.error("Invalid event_data_complex, does not contain event_custom field!")
        else:
            if not level in self.levels:
                bisect.insort(self.levels, level)
            # handle cases for each type of event
            # NOTE: for BEGIN and COMPLETE, we assume only one event of each type happens.
            # If there are somehow multiples, the previous times are overwritten by the newer ones.
            if event_data_complex_parsed["event_custom"] == "BEGIN":
                self.start_times[level] = event_client_time
            if event_data_complex_parsed["event_custom"] == "COMPLETE":
                self.end_times[level] = event_client_time
                self.features["completed"][level] = 1
            elif event_data_complex_parsed["event_custom"] == "SUCCEED":
                pass
            elif event_data_complex_parsed["event_custom"] == "FAIL":
                self.features["totalFails"][level] += 1
            elif event_data_complex_parsed["event_custom"] in ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"] :
                # first, log the type of move.
                if event_data_complex_parsed["slider"] is not self.last_adjust_type:
                    self.last_adjust_type = event_data_complex_parsed["slider"]
                    # NOTE: We assume data are processed in order of event time.
                    # If events are not sorted by time, the "move type changes" may be inaccurate.
                    self.features["totalMoveTypeChanges"][level] += 1
                if event_data_complex_parsed["slider"] == "AMPLITUDE":
                    self.features["totalAmplitudeMoves"][level] += 1
                elif event_data_complex_parsed["slider"] == "OFFSET":
                    self.features["totalOffsetMoves"][level] += 1
                if event_data_complex_parsed["slider"] == "WAVELENGTH":
                    self.features["totalWavelengthMoves"][level] += 1
                # then, log things specific to slider move:
                if event_data_complex_parsed["event_custom"] == "SLIDER_MOVE_RELEASE":
                    self.features["totalSliderMoves"][level] += 1
                    self.features["totalKnobStdDevs"][level] += event_data_complex_parsed["stdev_val"]
                    self.features["totalKnobAvgMaxMin"][level] += event_data_complex_parsed["max_val"] - event_data_complex_parsed["min_val"]
                else: # log things specific to arrow move:
                    self.features["totalArrowMoves"][level] += 1

    def _calcPercentMoves(self, key:str, level:int) -> int:
        num = sum(self.features[key].values())
        if num == 0:
            return 0
        else:
            denom = sum(self.features["totalSliderMoves"].values()) \
                  + sum(self.features["totalArrowMoves"].values())
            return num/denom

    def _calcLevelTime(self, lvl:int) -> int:
        # use 0 if not played, -1 if not completed
        if lvl in self.levels:
            if lvl in self.start_times and lvl in self.end_times:
                return (self.end_times[lvl] - self.start_times[lvl]).total_seconds()
            else:
                return -1
        else:
            return 0
                                               

    def calculateAggregateFeatures(self):
        if len(self.levels) > 0:
            # the percent____Moves features are per-level, but can't be calculated until the end.
            self.features["percentAmplitudeMoves"] = {lvl: self._calcPercentMoves("totalAmplitudeMoves", lvl) \
                                                       if lvl in self.levels else 0
                                                       for lvl in range(self.min_level, self.max_level+1)}
            self.features["percentOffsetMoves"] = {lvl: self._calcPercentMoves("totalOffsetMoves", lvl) \
                                                       if lvl in self.levels else 0
                                                       for lvl in range(self.min_level, self.max_level+1)}
            self.features["percentWavelengthMoves"] = {lvl: self._calcPercentMoves("totalWavelengthMoves", lvl) \
                                                       if lvl in self.levels else 0
                                                       for lvl in range(self.min_level, self.max_level+1)}
            self.features["avgSliderMoves"] = sum(self.features["totalSliderMoves"].values()) / len(self.levels)
            self.features["totalLevelTime"] = {lvl:self._calcLevelTime(lvl) for lvl in range(self.min_level, self.max_level+1)}
            self.features["avgLevelTime"] = sum(self.features["totalLevelTime"].values()) / len(self.levels)
            self.features["avgKnobStdDevs"] = sum(self.features["totalKnobStdDevs"].values()) / len(self.levels)
            self.features["avgMoveTypeChanges"] = sum(self.features["totalMoveTypeChanges"].values()) / len(self.levels)
            self.features["avgKnobAvgMaxMin"] = sum(self.features["totalKnobAvgMaxMin"].values()) / len(self.levels)
            self.features["avgAmplitudeMoves"] = sum(self.features["totalAmplitudeMoves"].values()) / len(self.levels)
            self.features["avgOffsetMoves"] = sum(self.features["totalOffsetMoves"].values()) / len(self.levels)
            self.features["avgWavelengthMoves"] = sum(self.features["totalWavelengthMoves"].values()) / len(self.levels)

    def writeCSVHeader(self, file: typing.IO.writable):
        columns = []
        for key in self.features.keys():
            if type(self.features[key]) is type({}):
                # if it's a dictionary, expand.
                columns.extend(["lvl{}_{}".format(lvl, key) for lvl in range(self.min_level,self.max_level+1)])
            else:
                columns.append(key)
        file.write(",".join(columns))
        file.write("\n")

    # TODO: write out per-level vals once for each level
    def writeCurrentFeatures(self, file: typing.IO.writable):
        column_vals = []
        for key in self.features.keys():
            if type(self.features[key]) is type({}):
                # if it's a dictionary, expand.
                column_vals.extend([str(self.features[key][lvl]) for lvl in range(self.min_level,self.max_level+1)])
            else:
                column_vals.append(str(self.features[key]))
        file.write(",".join(column_vals))
        file.write("\n")