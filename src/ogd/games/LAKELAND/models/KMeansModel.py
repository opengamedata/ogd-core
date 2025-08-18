from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import logging

from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.models.PopulationModel import PopulationModel
from ogd.common.utils.Logger import Logger
from pathlib import Path

class KMeansModel(PopulationModel):

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        print("\n\nInitializing KMeans Model (BLOOM)\n\n")
        # Feature data accumulators
        self._build_count = []
        self._city_inspection_count = []
        self._dairy_inspection_count = []
        self._grain_inspection_count = []
        self._phosphorus_view_count = []
        self._economy_view_count = []
        self._activity = []
        # Trained model components
        self._scaler = None
        self._pca = None
        self._kmeans = None
        self._processed_data = None
        self._cluster_summary = None
        self._silhouette_score = None

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return [
            'BuildCount',
            'CityInspectionCount',
            'DairyInspectionCount',
            'GrainInspectionCount',
            'PhosphorusViewTime',
            'EconomyViewTime'
        ]

    def _updateFromFeature(self, feature: Feature):
        if feature.ExportMode == self.ExtractMode:
            try:
                value_as_string = str(feature.Values[0])
                numeric_value = int(value_as_string.split()[-1])
            except (ValueError, IndexError):
                numeric_value = 0

            if feature.Name == "BuildCount":
                # print("  -> NAME CHECK: PASSED. Appending to _build_count.")
                self._build_count.append(numeric_value)
                # print(self._build_count)
                # self._build_count.append(numeric_value)
            elif feature.Name == "CityInspectionCount":
                # print("  -> NAME CHECK: PASSED. Appending to _city_inspection_count.")
                # print(self._city_inspection_count)
                self._city_inspection_count.append(numeric_value)
            elif feature.Name == "DairyInspectionCount":
                self._dairy_inspection_count.append(numeric_value)
                # print("  -> NAME CHECK: PASSED. Appending to _dairy_inspection_count.")
                # print(self._dairy_inspection_count)
            elif feature.Name == "GrainInspectionCount":
                self._grain_inspection_count.append(numeric_value)
                # print("  -> NAME CHECK: PASSED. Appending to _grain_inspection_count.")
                # print(self._grain_inspection_count)
            # elif feature.Name == "PhosphorusViewCount":
            elif feature.Name == "PhosphorusViewTime":
                # print(feature.Values)
                self._phosphorus_view_count.append(feature.FeatureValues[1] if feature.FeatureValues[1] else 0)
                # print("  -> NAME CHECK: PASSED. Appending to _phosphorus_view_count.")
            # elif feature.Name == "EconomyViewCount":
            elif feature.Name == "EconomyViewTime":
                # print("  -> NAME CHECK: PASSED. Appending to _economy_view_count.")
                self._economy_view_count.append(feature.FeatureValues[1] if feature.FeatureValues[1] else 0)

    def _updateFromEvent(self, event):
        pass

    def _train(self):

        data_dict = {
            'BuildCount': self._build_count,
            'CityInspectionCount': self._city_inspection_count,
            'DairyInspectionCount': self._dairy_inspection_count,
            'GrainInspectionCount': self._grain_inspection_count,
            'PhosphorusViewCount': self._phosphorus_view_count,
            'EconomyViewCount': self._economy_view_count,
        }


        print(data_dict)


        print("--- KMEANSMODEL: INSPECTING DATA AT START OF _train ---")
        print(f"Total entries for BuildCount: {len(self._build_count), len(data_dict['BuildCount'])}")
        print(f"Total entries for CityInspectionCount: {len(self._city_inspection_count), len(data_dict['CityInspectionCount'])}")
        print(f"Total entries for DairyInspectionCount: {len(self._dairy_inspection_count), len(data_dict['DairyInspectionCount'])}")
        print(f"Total entries for GrainInspectionCount: {len(self._grain_inspection_count), len(data_dict['GrainInspectionCount'])}")
        print(f"Total entries for PhosphorusViewCount: {len(self._phosphorus_view_count), len(data_dict['PhosphorusViewCount'])}")
        print(f"Total entries for EconomyViewCount: {len(self._economy_view_count), len(data_dict['EconomyViewCount'])}")

        min_length = min(
            len(self._build_count),
            len(self._city_inspection_count),
            len(self._dairy_inspection_count),
            len(self._grain_inspection_count),
            len(self._phosphorus_view_count),
            len(self._economy_view_count)
        )

        if min_length == 0:
            Logger.Log("No feature data available for KMeansModel training, skipping.", logging.WARN)
            return

        data_dict = {
            'BuildCount': self._build_count,
            'CityInspectionCount': self._city_inspection_count,
            'DairyInspectionCount': self._dairy_inspection_count,
            'GrainInspectionCount': self._grain_inspection_count,
            'PhosphorusViewCount': self._phosphorus_view_count,
            'EconomyViewCount': self._economy_view_count,
        }

        print("Data dictionary keys:", data_dict)
        self._processed_data = pd.DataFrame(data_dict)
        features = list(data_dict.keys())

        for col in ['PhosphorusViewCount', 'EconomyViewCount']:
            if col in self._processed_data.columns:
                self._processed_data[col] = self._processed_data[col].apply(lambda x: np.log1p(x) if x is not None else 0)

        self._scaler = StandardScaler()
        self._processed_data[features] = self._scaler.fit_transform(self._processed_data[features])

        self._pca = PCA(n_components=2)
        pca_data = self._pca.fit_transform(self._processed_data[features])

        self._kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
        cluster_labels = self._kmeans.fit_predict(pca_data)

        self._processed_data['Cluster'] = cluster_labels
        self._silhouette_score = silhouette_score(pca_data, cluster_labels)
        self._cluster_summary = self._processed_data.groupby('Cluster')[features].mean()

        Logger.Log(f"KMeansModel training completed. Silhouette Score: {self._silhouette_score}", logging.INFO)



    def _apply(self, apply_to:List[Feature]) -> Feature:
        if self._kmeans is None:
            raise ValueError("Model must be trained before applying")

        input_features = {}
        for feature_data in apply_to:
            print("feature_data:", feature_data)
            if feature_data.ExportMode == self.ExtractMode:
                input_features[feature_data.Name] = feature_data.FeatureValues[0]

        required_features = self._featureFilter(self.ExtractMode)
        if len(input_features) != len(required_features):
            raise ValueError(f"Missing required features. Got {list(input_features.keys())}, need {required_features}")

        input_df = pd.DataFrame([input_features])
        for col in ['PhosphorusViewCount', 'EconomyViewCount']:
            if col in input_df.columns:
                input_df[col] = input_df[col].apply(lambda x: np.log1p(x))

        input_scaled = self._scaler.transform(input_df[required_features])
        input_pca = self._pca.transform(input_scaled)
        cluster_assignment = self._kmeans.predict(input_pca)[0]

        result_feature = apply_to[0] if apply_to else None
        if result_feature:
            result_feature.Values = [cluster_assignment]
            result_feature.Name = "PredictedCluster"

        return result_feature

    def _render(self, save_path: Path = None):
        if not self._kmeans:
            Logger.Log("KMeansModel has not been trained yet. No centroids to render.", logging.INFO)
            return

        Logger.Log("KMeans Cluster Centroids (in PCA-reduced space):", logging.INFO)
        for idx, centroid in enumerate(self._kmeans.cluster_centers_):
            Logger.Log(f"Cluster {idx}: {centroid}", logging.INFO)

    def _modelInfo(self):
        if not self._cluster_summary is not None:
            Logger.Log("KMeansModel has not been trained yet. No info to display.", logging.INFO)
            return

        Logger.Log(f"KMeansModel - Average Silhouette Score: {self._silhouette_score:.4f}", logging.INFO)
        Logger.Log("KMeansModel - Cluster Summary (Feature Averages):", logging.INFO)
        Logger.Log(str(self._cluster_summary), logging.INFO)

        labels = list(self._cluster_summary.columns)
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist() + [0]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        for idx, row in self._cluster_summary.iterrows():
            values = row.tolist() + row.tolist()[:1]
            ax.plot(angles, values, label=f'Cluster {idx}')
            ax.fill(angles, values, alpha=0.1)

        ax.set_title("Cluster Feature Radar Plot", size=15)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), labels)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        plt.tight_layout()
        plt.savefig("cluster_radar_plot.png")
        Logger.Log("Radar plot saved as 'cluster_radar_plot.png'", logging.INFO)
