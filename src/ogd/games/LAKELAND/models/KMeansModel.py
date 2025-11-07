
# from typing import List, Dict, Any
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.preprocessing import StandardScaler
# from sklearn.decomposition import PCA
# from sklearn.cluster import KMeans
# from sklearn.metrics import silhouette_score

# from typing import List
# from ogd.common.models.enums.ExtractionMode import ExtractionMode
# from ogd.common.models.Feature import Feature
# from ogd.core.generators.Generator import GeneratorParameters
# from ogd.core.generators.models.PopulationModel import PopulationModel
# from ogd.common.utils.Logger import Logger

# class KMeansModel(PopulationModel):

#     def __init__(self, params:GeneratorParameters):
#         super().__init__(params=params)
#         self._crop_build_count = []
#         self._dairy_build_count = []
#         self._house_build_count = []
#         self._hovers_before_crop_placement = []
#         self._total_build_count = []

#     @classmethod
#     def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
#         return [
#             'CropBuildCount', 
#             'DairyBuildCount', 
#             'HouseBuildCount',
#             'HoversBeforeCropPlacement', 
#             'TotalBuildCount'
#         ]
    
#     def _updateFromFeature(self, feature:Feature):
#         print("\n\n\nInside _updateFromFeature of KMeansModel")
#         if hasattr(feature, 'ExtractionMode') and feature.ExtractionMode == ExtractionMode.SESSION:
#             if feature.Name == "CropBuildCount":
#                 self._crop_build_count.append(feature.Values[0])
#             elif feature.Name == "DairyBuildCount":
#                 self._dairy_build_count.append(feature.Values[0])
#             elif feature.Name == "HouseBuildCount":
#                 self._house_build_count.append(feature.Values[0])
#             elif feature.Name == "HoversBeforeCropPlacement":
#                 self._hovers_before_crop_placement.append(feature.Values[0])
#             elif feature.Name == "TotalBuildCount":
#                 self._total_build_count.append(feature.Values[0])

#             Logger.Log(f"[KMeansModel] Received feature: {feature.Name} = {feature.Values[0]}", logging.DEBUG)


#     def _updateFromEvent(self, event):
#         pass
    
#     def _train(self):
#         print("\n\n\nInside _train of KMeansModel")
#         # self._updateFromFeature(feature)
#         min_length = min(
#             len(self._crop_build_count),
#             len(self._dairy_build_count), 
#             len(self._house_build_count),
#             len(self._hovers_before_crop_placement),
#             len(self._total_build_count)
#         )
        
#         if min_length == 0:
#             raise ValueError("No feature data available for training")
        
#         data_dict = {
#             'CropBuildCount': self._crop_build_count[:min_length],
#             'DairyBuildCount': self._dairy_build_count[:min_length],
#             'HouseBuildCount': self._house_build_count[:min_length],
#             'HoversBeforeCropPlacement': self._hovers_before_crop_placement[:min_length],
#             'TotalBuildCount': self._total_build_count[:min_length]
#         }
        
#         self._processed_data = pd.DataFrame(data_dict)
        
#         n_clusters = 6
#         n_components = 2
#         features = ['CropBuildCount', 'DairyBuildCount', 'HouseBuildCount',
#                     'HoversBeforeCropPlacement', 'TotalBuildCount']
        
#         processed_data = pd.DataFrame(data_dict)
        
#         for col in ['HoversBeforeCropPlacement', 'TotalBuildCount']:
#             if col in processed_data.columns:
#                 processed_data[col] = processed_data[col].apply(lambda x: np.log1p(x))
        
#         self._scaler = StandardScaler()
#         available_features = [f for f in features if f in processed_data.columns]
#         processed_data[available_features] = self._scaler.fit_transform(
#             processed_data[available_features]
#         )
        
#         self._pca = PCA(n_components=n_components)
#         self._pca_data = self._pca.fit_transform(processed_data[available_features])
        
#         self._kmeans = KMeans(n_clusters=n_clusters, random_state=42)
#         self._cluster_labels = self._kmeans.fit_predict(self._pca_data)
        
#         processed_data['Cluster'] = self._cluster_labels
#         self._processed_data = processed_data
        
#         self._silhouette_score = silhouette_score(self._pca_data, self._cluster_labels)
        
#         self._cluster_summary = processed_data.groupby('Cluster')[available_features].mean()
        
#         print(f"Training completed. Silhouette Score: {self._silhouette_score}")


#     def _apply(self, apply_to:List[Feature]) -> Feature:
#         if self._kmeans is None:
#             raise ValueError("Model must be trained before applying")
        
#         input_features = {}
        
#         for feature_data in apply_to:
#             if feature_data.ExportMode == self.ExtractMode:
#                 if feature_data.Name == "CropBuildCount":
#                     input_features["CropBuildCount"] = feature_data.FeatureValues[0]
#                 elif feature_data.Name == "DairyBuildCount":
#                     input_features["DairyBuildCount"] = feature_data.FeatureValues[0]
#                 elif feature_data.Name == "HouseBuildCount":
#                     input_features["HouseBuildCount"] = feature_data.FeatureValues[0]
#                 elif feature_data.Name == "HoversBeforeCropPlacement":
#                     input_features["HoversBeforeCropPlacement"] = feature_data.FeatureValues[0]
#                 elif feature_data.Name == "TotalBuildCount":
#                     input_features["TotalBuildCount"] = feature_data.FeatureValues[0]
    
#         required_features = self._featureFilter(self.ExtractMode)
#         if len(input_features) != len(required_features):
#             raise ValueError(f"Missing required features. Got {list(input_features.keys())}, need {required_features}")
        
#         input_df = pd.DataFrame([input_features])
        
#         for col in ['HoversBeforeCropPlacement', 'TotalBuildCount']:
#             if col in input_df.columns:
#                 input_df[col] = input_df[col].apply(lambda x: np.log1p(x))
        
#         features = ['CropBuildCount', 'DairyBuildCount', 'HouseBuildCount',
#                    'HoversBeforeCropPlacement', 'TotalBuildCount']
#         input_scaled = self._scaler.transform(input_df[features])
        
#         input_pca = self._pca.transform(input_scaled)
        
#         cluster_assignment = self._kmeans.predict(input_pca)[0]
        
#         print(f"Predicted cluster: {cluster_assignment}")
        
#         result_feature = apply_to[0] if apply_to else None
#         if result_feature:
#             result_feature.Values = [cluster_assignment]
#             result_feature.Name = "PredictedCluster"
        
#         return result_feature


#     def _render(self):
#         if not hasattr(self, "_kmeans") or self._kmeans is None:
#             print("Model has not been trained yet. No centroids to render.")
#             return

#         print("Cluster Centroids in PCA-reduced space:")
#         for idx, centroid in enumerate(self._kmeans.cluster_centers_):
#             print(f"Cluster {idx}: {centroid}")


#     def _modelInfo(self):
#         if not hasattr(self, "_cluster_summary") or self._cluster_summary is None:
#             print("Model has not been trained yet. No info to display.")
#             return

#         print(f"Average Silhouette Score: {self._silhouette_score:.4f}")
#         print("Cluster Summary (Feature Averages):")
#         print(self._cluster_summary)

#         labels = list(self._cluster_summary.columns)
#         num_vars = len(labels)

#         angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
#         angles += angles[:1]  


#         fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

#         for idx, row in self._cluster_summary.iterrows():
#             values = row.tolist()
#             values += values[:1]  
#             ax.plot(angles, values, label=f'Cluster {idx}')
#             ax.fill(angles, values, alpha=0.1)

#         ax.set_title("Cluster Feature Radar Plot", size=15)
#         ax.set_theta_offset(np.pi / 2)
#         ax.set_theta_direction(-1)
#         ax.set_thetagrids(np.degrees(angles[:-1]), labels)
#         ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

#         plt.tight_layout()
#         plt.savefig("cluster_radar_plot.png")
#         print("Radar plot saved as 'cluster_radar_plot.png'")



# File: src/ogd/games/LAKELAND/models/KMeansModel.py

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

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        # Feature data accumulators
        self._crop_build_count = []
        self._dairy_build_count = []
        self._house_build_count = []
        self._hovers_before_crop_placement = []
        self._total_build_count = []
        # Trained model components
        self._scaler = None
        self._pca = None
        self._kmeans = None
        self._processed_data = None
        self._cluster_summary = None
        self._silhouette_score = None

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        # This is correct as is.
        return [
            'CropBuildCount', 
            'DairyBuildCount', 
            'HouseBuildCount',
            'HoversBeforeCropPlacement', 
            'TotalBuildCount'
        ]
    
# In KMeansModel.py, replace your _updateFromFeature with this detailed version:

    def _updateFromFeature(self, feature: Feature):
        # --- ADD THIS DETAILED DEBUGGING BLOCK ---
        print(" DEBUGGING: CHECKPOINT 2 (KMeansModel) ")
        print(f"Received feature: {feature.Name} with value {feature.Values[0]}")
        mode_check_passed = False
        if hasattr(feature, 'ExtractionMode') and feature.ExtractionMode == ExtractionMode.SESSION:
            mode_check_passed = True
            print("  -> EXTRACTION MODE CHECK: PASSED (Mode is SESSION)")
        else:
            mode = getattr(feature, 'ExtractionMode', '!!! ATTRIBUTE NOT FOUND !!!')
            print(f"  -> EXTRACTION MODE CHECK: FAILED (Mode is '{mode}', expected SESSION)")

        # 2. If the mode was correct, check the Name condition
        if mode_check_passed:
            try:
                value_as_string = str(feature.Values[0])
                numeric_value = int(value_as_string.split()[-1])
            except (ValueError, IndexError):
                numeric_value = 0

            if feature.Name == "CropBuildCount":
                print("  -> NAME CHECK: PASSED. Appending to _crop_build_count.")
                self._crop_build_count.append(numeric_value)
            elif feature.Name == "DairyBuildCount":
                print("  -> NAME CHECK: PASSED. Appending to _dairy_build_count.")
                self._dairy_build_count.append(numeric_value)
            elif feature.Name == "HouseBuildCount":
                print("  -> NAME CHECK: PASSED. Appending to _house_build_count.")
                self._house_build_count.append(numeric_value)
            elif feature.Name == "HoversBeforeCropPlacement":
                print("  -> NAME CHECK: PASSED. Appending to _hovers_before_crop_placement.")
                self._hovers_before_crop_placement.append(numeric_value)
            elif feature.Name == "TotalBuildCount":
                print("  -> NAME CHECK: PASSED. Appending to _total_build_count.")
                self._total_build_count.append(numeric_value)
            else:
                print(f"  -> NAME CHECK: FAILED (Name '{feature.Name}' did not match any list)")
            
            print("lenght for checking append", len(self._crop_build_count))
        # --- END OF DETAILED DEBUGGING BLOCK ---

    def _updateFromEvent(self, event):
        # This is correct as is.
        pass
    
    def _train(self):

        print("--- KMEANSMODEL: INSPECTING DATA AT START OF _train ---")
        print(f"Total entries for CropBuildCount:      {len(self._crop_build_count)}")
        print(f"  -> First 5 values: {self._crop_build_count[:5]}")
        # This logic is correct and will be called by the registry at the right time.
        min_length = min(
            len(self._crop_build_count), len(self._dairy_build_count), 
            len(self._house_build_count), len(self._hovers_before_crop_placement),
            len(self._total_build_count)
        )
        
        if min_length == 0:
            Logger.Log("No feature data available for KMeansModel training, skipping.", logging.WARN)
            return
        
        data_dict = {
            'CropBuildCount': self._crop_build_count[:min_length],
            'DairyBuildCount': self._dairy_build_count[:min_length],
            'HouseBuildCount': self._house_build_count[:min_length],
            'HoversBeforeCropPlacement': self._hovers_before_crop_placement[:min_length],
            'TotalBuildCount': self._total_build_count[:min_length]
        }
        
        self._processed_data = pd.DataFrame(data_dict)
        
        n_clusters = 6
        n_components = 2
        features = list(data_dict.keys())
        
        processed_data_copy = self._processed_data.copy()
        
        for col in ['HoversBeforeCropPlacement', 'TotalBuildCount']:
            if col in processed_data_copy.columns:
                processed_data_copy[col] = processed_data_copy[col].apply(lambda x: np.log1p(x) if x is not None else 0)
        
        self._scaler = StandardScaler()
        processed_data_copy[features] = self._scaler.fit_transform(processed_data_copy[features])
        
        self._pca = PCA(n_components=n_components)
        pca_data = self._pca.fit_transform(processed_data_copy[features])
        
        self._kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
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
            if feature_data.ExportMode == self.ExtractMode:
                if feature_data.Name == "CropBuildCount":
                    input_features["CropBuildCount"] = feature_data.FeatureValues[0]
                elif feature_data.Name == "DairyBuildCount":
                    input_features["DairyBuildCount"] = feature_data.FeatureValues[0]
                elif feature_data.Name == "HouseBuildCount":
                    input_features["HouseBuildCount"] = feature_data.FeatureValues[0]
                elif feature_data.Name == "HoversBeforeCropPlacement":
                    input_features["HoversBeforeCropPlacement"] = feature_data.FeatureValues[0]
                elif feature_data.Name == "TotalBuildCount":
                    input_features["TotalBuildCount"] = feature_data.FeatureValues[0]
    
        required_features = self._featureFilter(self.ExtractMode)
        if len(input_features) != len(required_features):
            raise ValueError(f"Missing required features. Got {list(input_features.keys())}, need {required_features}")
        
        input_df = pd.DataFrame([input_features])
        
        for col in ['HoversBeforeCropPlacement', 'TotalBuildCount']:
            if col in input_df.columns:
                input_df[col] = input_df[col].apply(lambda x: np.log1p(x))
        
        features = ['CropBuildCount', 'DairyBuildCount', 'HouseBuildCount',
                   'HoversBeforeCropPlacement', 'TotalBuildCount']
        input_scaled = self._scaler.transform(input_df[features])
        
        input_pca = self._pca.transform(input_scaled)
        
        cluster_assignment = self._kmeans.predict(input_pca)[0]
        
        print(f"Predicted cluster: {cluster_assignment}")
        
        result_feature = apply_to[0] if apply_to else None
        if result_feature:
            result_feature.Values = [cluster_assignment]
            result_feature.Name = "PredictedCluster"
        
        return result_feature

    def _render(self, save_path:Path = None):
        # This logic is correct.
        if not hasattr(self, "_kmeans") or self._kmeans is None:
            Logger.Log("KMeansModel has not been trained yet. No centroids to render.", logging.INFO)
            return

        Logger.Log("KMeans Cluster Centroids (in PCA-reduced space):", logging.INFO)
        for idx, centroid in enumerate(self._kmeans.cluster_centers_):
            Logger.Log(f"Cluster {idx}: {centroid}", logging.INFO)

    def _modelInfo(self):
        # This logic is correct.
        if not hasattr(self, "_cluster_summary") or self._cluster_summary is None:
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