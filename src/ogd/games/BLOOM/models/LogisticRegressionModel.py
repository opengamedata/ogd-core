from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import logging

from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.models.PopulationModel import PopulationModel
from ogd.common.utils.Logger import Logger
from pathlib import Path
import time

class LogisticRegressionModel(PopulationModel):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        print("\n\nInitializing Logistic Regression Model (BLOOM)\n\n")

        self._economy_view_count = []
        self._alert_review_count = []
        self._policy_change_count = []
        self._game_win = []

        self._scaler = None
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

    def _updateFromFeature(self, feature: Feature):
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
        print("\n\nTraining Logistic Regression Model (BLOOM)\n\n")

        print(self._game_win)

        min_length = min(
            len(self._economy_view_count),
            len(self._alert_review_count),
            len(self._policy_change_count),
            len(self._game_win)
        )

        if min_length == 0:
            Logger.Log("No sufficient data for Logistic Regression model training.", logging.WARN)
            return

        X = pd.DataFrame({
            'EconomyViewCount': self._economy_view_count[:min_length],
            'AlertReviewCount': self._alert_review_count[:min_length],
            'TotalPolicyChangeCount': self._policy_change_count[:min_length],
        })

        y = self._game_win[:min_length]

        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        self._model = LogisticRegression()
        self._model.fit(X_scaled, y)

        y_pred = self._model.predict(X_scaled)
        self._accuracy = accuracy_score(y, y_pred)
        Logger.Log(f"Logistic Regression training completed. Accuracy: {self._accuracy:.2f}", logging.INFO)

    def _apply(self, apply_to: List[Feature]) -> Feature:
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
        input_scaled = self._scaler.transform(input_df[required_features])
        pred = self._model.predict(input_scaled)[0]
        prob = self._model.predict_proba(input_scaled)[0][1]

        result_feature = apply_to[0] if apply_to else None
        if result_feature:
            result_feature.FeatureValues = [bool(pred)]
            result_feature.Name = "PredictedGameWin"

        return result_feature

    def _render(self, save_path: Path = None):
        if self._model:
            Logger.Log("Logistic Regression Coefficients:", logging.INFO)
            features = ['EconomyViewCount', 'AlertReviewCount', 'TotalPolicyChangeCount']
            for name, coef in zip(features, self._model.coef_[0]):
                Logger.Log(f"{name}: {coef:.4f}", logging.INFO)

    def _modelInfo(self):
        if self._model:
            Logger.Log(f"Logistic Regression Model Accuracy: {self._accuracy:.2f}", logging.INFO)