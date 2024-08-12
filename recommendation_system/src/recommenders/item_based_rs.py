import numpy as np
import torch


from utils.similarity_measure import pure_cosine_similarity, pearson_correlation
from recommenders.memory_based_rs import MemoryBasedRecommenderSystem

class ItemBasedRecommenderSystem(MemoryBasedRecommenderSystem):
    def __init__(self, ratings_df, neighborhood_size, precompute_rating_matrix_path=None, precompute_similarity_matrix_path=None, similarity_measure='adjusted_cosine'):
        super().__init__(ratings_df, neighborhood_size, precompute_rating_matrix_path, precompute_similarity_matrix_path, similarity_measure)

    def calculate_similarity_matrix(self):
        """
        Calculate similarity matrix between items and store it in self.similarity_matrix
        """
        movies_count = len(self.unique_movies)
        self.similarity_matrix = np.zeros((movies_count, movies_count))

        for movie_i in self.unique_movies:
            movie_i_index = self.movie_to_index[movie_i]
            for movie_j in self.unique_movies:
                movie_j_index = self.movie_to_index[movie_j]
                if movie_i > movie_j:
                    self.similarity_matrix[movie_i_index, movie_j_index] = self.similarity_matrix[movie_j_index, movie_i_index]
                    continue
                elif movie_i == movie_j:
                    continue
                else:
                    users_rated_both = np.nonzero(~np.isnan(self.rating_matrix[:, movie_i_index]) & ~np.isnan(self.rating_matrix[:, movie_j_index]))[0]
                    movie_i_vec = self.rating_matrix[users_rated_both, movie_i_index]
                    movie_j_vec = self.rating_matrix[users_rated_both, movie_j_index]

                    similarity = 0
                    if self.similarity_measure == 'pearson_correlation':
                        similarity = pearson_correlation(movie_i_vec, movie_j_vec)
                    elif self.similarity_measure == 'pure_cosine':
                        similarity = pure_cosine_similarity(movie_i_vec, movie_j_vec)
                    elif self.similarity_measure == 'adjusted_cosine':
                        movie_i_vec = movie_i_vec - np.nanmean(self.rating_matrix[users_rated_both, :], axis=1)
                        movie_j_vec = movie_j_vec - np.nanmean(self.rating_matrix[users_rated_both, :], axis=1)
                        similarity = pure_cosine_similarity(movie_i_vec, movie_j_vec)

                    self.similarity_matrix[movie_i_index, movie_j_index] = similarity

        self.similarity_matrix = torch.from_numpy(self.similarity_matrix).float()

    def fit(self):
        """
        If does not use precomputed similarity matrix, calculate similarity matrix between items and store it in self.similarity_matrix
        """
        if self.similarity_matrix is None:
            self.calculate_similarity_matrix()

    def predict_rating(self, user_id, movie_id):
        """
        Predict rating of user_id for movie_id
        """
        user_index = self.user_to_index.get(user_id)
        movie_index = self.movie_to_index.get(movie_id)

        if user_index is None and movie_index is None:
            return torch.nanmean(self.rating_matrix)
        elif movie_index is None:
            return torch.nanmean(self.rating_matrix[user_index, :])
        elif user_index is None:
            return torch.nanmean(self.rating_matrix[:, movie_index])
        elif not torch.isnan(self.rating_matrix[user_index, movie_index]):
            return self.rating_matrix[user_index, movie_index]

        user_ratings = self.rating_matrix[user_index, :]
        movies_rated_by_user_index = torch.nonzero(~torch.isnan(user_ratings)).squeeze()
        movie_similarities = self.similarity_matrix[movie_index, movies_rated_by_user_index]

        top_k_similar_indexes = torch.argsort(movie_similarities)[-self.neighborhood_size:]
        top_k_similarities = movie_similarities[top_k_similar_indexes]
        top_k_user_ratings = user_ratings[movies_rated_by_user_index[top_k_similar_indexes]]

        denominator = torch.norm(top_k_similarities, p=1)
        rating_prediction = torch.dot(top_k_similarities, top_k_user_ratings) / denominator if denominator != 0 else torch.nanmean(self.rating_matrix[:, movie_index])

        return rating_prediction