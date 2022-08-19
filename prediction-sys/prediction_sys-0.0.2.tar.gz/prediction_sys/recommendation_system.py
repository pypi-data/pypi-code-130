from enum import Enum
from typing import Union
from sklearn.metrics.pairwise import linear_kernel


class SysRecommenadtionException(Exception):
    pass


class SysRecMethode(str, Enum):
    KNN = "KNN"
    TFIDF = "TFIDf"


class SysRecommenadtion:
    _output_model: any
    _method: any
    indices: any = None
    features: any = None
    threshold: Union[int, None] = None

    def __init__(self, source):
        self.source = source

    def build(self, model, method: SysRecMethode = SysRecMethode.KNN):
        self._method = method
        if method == SysRecMethode.KNN:
            if self.features is None:
                raise SysRecommenadtionException(
                    "You must provide features, e.g: SysRecommenadtion.features = [...]")
            model.fit(self.features)
            dist, idlist = model.kneighbors(self.features)
            self._output_model = idlist

        elif method == SysRecMethode.TFIDF:
            self._output_model = linear_kernel(model, model)

    def predict(self, value: str, key: any = '', keys: any = ['']):

        if not key and not keys:
            raise SysRecommenadtionException("You must provide key or keys")
       
        if self._method == SysRecMethode.TFIDF:
            if self.indices is None:
                raise SysRecommenadtionException(
                    "You must provide an indices, e.g: SysRecommenadtion.indices = [...]")

            idx = self.indices[value]

            sim_scores = list(enumerate(self._output_model[idx]))

            # Get the scores of the 10 most similar movies
            if self.threshold is not None:
                sim_scores = sim_scores[1:self.threshold]

            # Get the movie indices
            movie_indices = [i[0] for i in sim_scores]

            # Return the top 10 most similar movies
            if key:
                return self.source[key].iloc[movie_indices]
            elif keys:
                return self.source[keys].iloc[movie_indices]

        elif self._method == SysRecMethode.KNN:
            predictions = []
            id = self.source[self.source[key] == value].index
            id = id[0]
            for newid in self._output_model[id]:
                predictions.append(self.source.loc[newid].title)
            return predictions
