from typing import List
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
import logging

from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.models.PopulationModel import PopulationModel
from ogd.common.utils.Logger import Logger
from pathlib import Path

class NeuralNetModel(PopulationModel):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        print("\n\nInitializing Neural Network Model (BLOOM)\n\n")

        self._economy_view_count = []
        self._alert_review_count = []
        self._policy_change_count = []
        self._game_win = []

        self._model = None
        self._accuracy = None
        self._params = params.extra_params if hasattr(params, "extra_params") else {}

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

        if feature.Name == "EconomyViewCount":
            self._economy_view_count.append(value)
        elif feature.Name == "AlertReviewCount":
            self._alert_review_count.append(value)
        elif feature.Name == "TotalPolicyChangeCount":
            self._policy_change_count.append(value)
        elif feature.Name == "GameCompletionStatus":
            self._game_win.append(1 if feature.FeatureValues[0] == "WIN" else 0)

    def _updateFromEvent(self, event):
        pass

    def _train(self):
        print("\n\nTraining Neural Network Model (BLOOM)\n\n")

        min_length = min(
            len(self._economy_view_count),
            len(self._alert_review_count),
            len(self._policy_change_count),
            len(self._game_win)
        )

        if min_length == 0:
            Logger.Log("No sufficient data for Neural Network training.", logging.WARN)
            return

        X = pd.DataFrame({
            'EconomyViewCount': self._economy_view_count[:min_length],
            'AlertReviewCount': self._alert_review_count[:min_length],
            'TotalPolicyChangeCount': self._policy_change_count[:min_length],
        })
        y = self._game_win[:min_length]

        self._model = MLPClassifier(
            hidden_layer_sizes=(8,),  
            activation='relu',       
            solver='adam',           
            max_iter=500,
            random_state=42
        )

        self._model.fit(X, y)
        y_pred = self._model.predict(X)
        self._accuracy = accuracy_score(y, y_pred)

        Logger.Log(f"Neural Network training completed. Accuracy: {self._accuracy:.2f}", logging.INFO)

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
            Logger.Log("Neural Network Model Info:", logging.INFO)
            Logger.Log(f"Number of layers: {self._model.n_layers_}", logging.INFO)
            Logger.Log(f"Hidden layer sizes: {self._model.hidden_layer_sizes}", logging.INFO)

    def _modelInfo(self):
        if self._model:
            Logger.Log(f"Neural Network Model Accuracy: {self._accuracy:.2f}", logging.INFO)
