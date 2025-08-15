from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import logging

from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.models.PopulationModel import PopulationModel
from ogd.common.utils.Logger import Logger
from pathlib import Path
import time

class RandomForestModel(PopulationModel):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        print("\n\nInitializing Random Forest Model (BLOOM)\n\n")

        self._economy_view_count = []
        self._alert_review_count = []
        self._policy_change_count = []
        self._game_win = []

        self._model = None
        self._processed_data = None
        self._accuracy = None

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return [
            'EconomyViewCount',
            'AlertReviewCount',
            'TotalPolicyChangeCount',
            'GameCompletionStatus'
        ]

    def _updateFromFeatureData(self, feature: FeatureData):
        if feature.ExportMode != self.ExtractionMode:
            return

        try:
            value = float(feature.FeatureValues[0]) if feature.FeatureValues[0] else 0
        except Exception:
            value = 0

        name = feature.Name

        if name == "EconomyViewCount":
            self._economy_view_count.append(value)
        elif name == "AlertReviewCount":
            self._alert_review_count.append(value)
        elif name == "TotalPolicyChangeCount":
            self._policy_change_count.append(value)
        elif name == "GameCompletionStatus":
            if feature.FeatureValues[0] == "WIN":
                self._game_win.append(1)
            else:
                self._game_win.append(0)

    def _updateFromEvent(self, event):
        pass

    def _train(self):
        print("\n\nTraining Random Forest Model (BLOOM)\n\n")

        min_length = min(
            len(self._economy_view_count),
            len(self._alert_review_count),
            len(self._policy_change_count),
            len(self._game_win)
        )

        if min_length == 0:
            Logger.Log("No sufficient data for Random Forest model training.", logging.WARN)
            return

        # Trim to same length
        X = pd.DataFrame({
            'EconomyViewCount': self._economy_view_count[:min_length],
            'AlertReviewCount': self._alert_review_count[:min_length],
            'TotalPolicyChangeCount': self._policy_change_count[:min_length],
        })

        y = self._game_win[:min_length]

        self._model = RandomForestClassifier(
            n_estimators=100, 
            random_state=42
        )
        self._model.fit(X, y)

        y_pred = self._model.predict(X)
        self._accuracy = accuracy_score(y, y_pred)
        Logger.Log(f"Random Forest training completed. Accuracy: {self._accuracy:.2f}", logging.INFO)

    def _apply(self, apply_to: List[FeatureData]) -> FeatureData:
        if self._model is None:
            raise ValueError("Model must be trained before applying.")

        input_features = {}
        for feature_data in apply_to:
            if feature_data.ExportMode == self.ExtractionMode:
                input_features[feature_data.Name] = float(feature_data.FeatureValues[0]) if feature_data.FeatureValues[0] else 0

        required_features = ['EconomyViewCount', 'AlertReviewCount', 'TotalPolicyChangeCount']
        for key in required_features:
            if key not in input_features:
                raise ValueError(f"Missing required feature: {key}")

        input_df = pd.DataFrame([input_features])
        pred = self._model.predict(input_df)[0]
        prob = self._model.predict_proba(input_df)[0][1]

        result_feature = apply_to[0] if apply_to else None
        if result_feature:
            result_feature.FeatureValues = [bool(pred)]
            result_feature.Name = "PredictedGameWin"

        return result_feature

    def _render(self, save_path: Path = None):
        if self._model:
            Logger.Log("Random Forest Feature Importances:", logging.INFO)
            features = ['EconomyViewCount', 'AlertReviewCount', 'TotalPolicyChangeCount']
            for name, importance in zip(features, self._model.feature_importances_):
                Logger.Log(f"{name}: {importance:.4f}", logging.INFO)

    def _modelInfo(self):
        if self._model:
            Logger.Log(f"Random Forest Model Accuracy: {self._accuracy:.2f}", logging.INFO)
