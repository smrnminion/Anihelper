from dataclasses import dataclass
import pickle
from pathlib import Path
import pandas as pd
from difflib import get_close_matches
from typing import Generator
import numpy as np
from sklearn import preprocessing
from loguru import logger
import enum
from Levenshtein import distance


class Algoritms(str, enum.Enum):
    KNN = "KNN"
    COS_SIM = "COS_SIM"


@dataclass
class PredictValue:
    v: str
    conf: float


@dataclass
class Predict:
    def __post_init__(self) -> None:
        self.data = "data"
        dataset_path = self.data + "/anime.csv"

        with open(self.data + "/cos_sim.pkl", "rb") as f:
            self.cos_sim = pickle.load(f)

        with open(self.data + "/knn.pkl", "rb") as f:
            self.knn = pickle.load(f)

        df = pd.read_csv(dataset_path)
        #print(df[:10])
        df = df.dropna()
        #print(df[:10])
        self.df = df
        df['rating'] = df['rating']*df['members']/(df['members']+10)
        self.df_processed = self.df_preprocess(df)
        self._names: list[str] = list(df["name"].unique())
        self.algoritm = Algoritms.KNN


    def df_preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df_processed = pd.get_dummies(df, columns=['genre', 'type'])
        df_processed = df_processed.drop(columns=['name', 'anime_id', 'episodes'])

        x = df_processed.values
        min_max_scaler = preprocessing.MinMaxScaler()
        x_scaled = min_max_scaler.fit_transform(x)
        df_processed = pd.DataFrame(x_scaled)

        return df_processed

    def recomend_cos(self, target_name: str, top: int = 10) -> Generator[PredictValue, None, None]:
        idx = self.df[self.df["name"] == target_name].index[0]
        score_series = pd.Series(self.cos_sim[idx]).sort_values(ascending=False)

        top = top + 1
        top_indexes = list(score_series.iloc[1:top].index)

        for i in top_indexes:
            yield PredictValue(v=self.df["name"].iloc[i], conf=score_series[i])

    def recomend_knn(self, target_name: str, top: int = 10) -> Generator[PredictValue, None, None]:
        target_idx = self.df[self.df["name"] == target_name].index[0]
        row = self.df_processed.iloc[target_idx]

        distances, idxs = self.knn.kneighbors([row], top + 1, return_distance=True)
        distances, idxs = distances[0], idxs[0]

        for i, idx in enumerate(idxs):
            yield PredictValue(v=self.df["name"].iloc[idx], conf=distances[i])

    def recommend(self, target_name: str, count: int = 10):
        if self.algoritm == Algoritms.COS_SIM:
            result = self.recomend_cos(target_name, count)
        else:
            result = self.recomend_knn(target_name, count)
        result = list(result)

        logger.debug(
            "recommendation done: target_name: {}, count: {}, algoritm: {}\nresult: {}",
            target_name,
            count,
            self.algoritm,
            result,
        )
        return result
    
    def find_names(self, name: str, count: int):
        names = get_close_matches(name, self._names, n=count * 3)
        self.df['distance'] = self.df['name'].apply(lambda x: distance(x, name))
        rows = self.df[self.df['name'].isin(names)].sort_values("distance", ascending=True)["name"].unique()
        names = list(rows)[:count]
        logger.debug("names found: name: {}, count: {}, found_names: {}", name, count, names)
        return names

    def best_from(self, count: int, field: str, name: str):
        best = list(self.df[self.df[field].str.contains(name)].sort_values(by="rating", ascending=False).name[:count])
        
        logger.debug("found best from: field: {}, name: {}, best: {}", field, name, best)
        return best

    def find_name(self, name: str) -> str:
        found_names = self.find_names(name, count=1)
        if len(found_names) == 0:
            raise KeyError(f"Name not found: {name}")
        return found_names[0]
    
    def recommend_best_anime(self, watched_anime_list: list, recommendation_count: int = 10):
        # Collect all recommendations for each anime in the watched list
        all_recommendations = []
        for anime in watched_anime_list:
            try:
                # Ensure the anime name exists in the dataset
                anime_name = self.find_name(anime)
                # Get recommendations based on the current algorithm setting
                recommendations = self.recommend(anime_name, recommendation_count)
                all_recommendations.extend(recommendations)
            except KeyError:
                logger.warning(f"Anime '{anime}' not found in the database. Skipping.")
        
        # Aggregating and scoring recommendations
        recommendation_scores = {}
        for rec in all_recommendations:
            if rec.v not in watched_anime_list:
                if rec.v in recommendation_scores:
                    recommendation_scores[rec.v] += rec.conf
                else:
                    recommendation_scores[rec.v] = rec.conf

        # Sort recommendations based on aggregate confidence scores
        sorted_recommendations = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)

        # Returning the top recommendations
        return [rec[0] for rec in sorted_recommendations[:recommendation_count]]