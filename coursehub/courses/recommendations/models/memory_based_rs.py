from courses.recommendations.models.recommender_system import RecommenderSystem

class MemoryBasedRecommenderSystem(RecommenderSystem):
    def __init__(self, ratings_df_path, neighborhood_size, precompute_rating_matrix_path=None, precompute_similarity_matrix_path=None, similarity_measure='adjusted_cosine'):
        super().__init__(ratings_df_path, precompute_rating_matrix_path)
        self.neighborhood_size = neighborhood_size
        self.similarity_measure = similarity_measure
        self.precompute_similarity_matrix_path = precompute_similarity_matrix_path