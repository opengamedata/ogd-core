## import standard libraries
from datetime import datetime
import re
from typing import Any, Callable, Dict, List, Optional
## import local files
from . import features
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.games.JOWILDER.features import *
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.Logger import Logger

class JowilderLoader(GeneratorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return features

    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Optional[Feature]:
        ret_val : Optional[Feature] = None
        match feature_type:
            case "QuestionAnswers":
                ret_val = QuestionAnswers.QuestionAnswers(params=extractor_params)
            case "SurveyItem":
                ret_val = SurveyItem.SurveyItem(params=extractor_params)
            case "Interaction":
                ret_val = Interaction.Interaction(params=extractor_params)
            case "SurveyTime":
                ret_val = SurveyTime.SurveyTime(params=extractor_params)
            case "Clicks":
                ret_val = Clicks.Clicks(params=extractor_params)
            case "Hovers":
                ret_val = Hovers.Hovers(params=extractor_params)
            case "SessionDuration":
                ret_val = SessionDuration.SessionDuration(params=extractor_params)
            case "InteractionName":
                ret_val = InteractionName.InteractionName(params=extractor_params)
            case "NotebookUses":
                ret_val = NotebookUses.NotebookUses(params=extractor_params)
            case "EventCount":
                ret_val = EventCount.EventCount(params=extractor_params)
            case "UserEnabled":
                ret_val = UserEnabled.UserEnabled(params=extractor_params)
            case "GameVersion":
                ret_val = GameVersion.GameVersion(params=extractor_params)
            case "UsedSaveCode":
                ret_val = UsedSaveCode.UsedSaveCode(params=extractor_params)
            case "GameScript":
                ret_val = GameScript.GameScript(params=extractor_params)
            case "SessionStart":
                ret_val = SessionStart.SessionStart(params=extractor_params)
            case "IdleState":
                ret_val = IdleState.IdleState(params=extractor_params, threshold=schema_args.get("IDLE_THRESH_SECONDS", IdleState.IdleState.IDLE_TIME_THRESHOLD))
            case "ActiveStateTime":
                ret_val = ActiveStateTime.ActiveStateTime(params=extractor_params, threshold=schema_args.get('ACTIVE_THRESH_SECONDS', ActiveStateTime.ActiveStateTime.ACTIVE_TIME_THRESHOLD))
            case "MeaningfulActions":
                ret_val = MeaningfulActions.MeaningfulActions(params=extractor_params)
            case "FirstInteraction":
                ret_val = FirstInteraction.FirstInteraction(params=extractor_params)
            case "LastInteraction":
                ret_val = LastInteraction.LastInteraction(params=extractor_params)
            case "UsedContinue":
                ret_val = UsedContinue.UsedContinue(params=extractor_params)
            case "InteractionWordsPerSecond":
                ret_val = InteractionWordsPerSecond.InteractionWordsPerSecond(params=extractor_params)
            case "InteractionTextBoxesPerSecond":
                ret_val = InteractionTextBoxesPerSecond.InteractionTextBoxesPerSecond(params=extractor_params)
            case _:
                Logger.Log(f"'{feature_type}' is not a valid feature for Jowilder.")
        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Optional[Detector]:
        Logger.Log(f"'{detector_type}' is not a valid feature for Lakeland.")
        return None

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the JoWilderExtractor class.
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Constructor for the CrystalLoader class.

        :param player_id: _description_
        :type player_id: str
        :param session_id: The id number for the session whose data is being processed by this instance
        :type session_id: str
        :param game_schema: A data structure containing information on how the game events and other data are structured
        :type game_schema: GameSchema
        :param feature_overrides: A list of features to export, overriding the default of exporting all enabled features.
        :type feature_overrides: Optional[List[str]]
        """
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, mode=mode, feature_overrides=feature_overrides)
