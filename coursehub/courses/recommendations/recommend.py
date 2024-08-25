from courses.recommendations.models.item_regression_rs import ItemBasedRegressionRecommenderSystem1, ItemRegressionModel
from courses.recommendations.models.non_personalized_rs import NonPersonalizedRecommenderSystem

NON_PER_PATH = 'courses/recommendations/trained_models/non_per.pkl'
ITEM_REG_PATH = 'courses/recommendations/trained_models/item_reg.pkl'

# Ensure classes are available in the global namespace
import sys
sys.modules['__main__'].NonPersonalizedRecommenderSystem = NonPersonalizedRecommenderSystem
sys.modules['__main__'].ItemBasedRegressionRecommenderSystem1 = ItemBasedRegressionRecommenderSystem1
sys.modules['__main__'].ItemRegressionModel = ItemRegressionModel

print('Loading models...')
non_per_model = NonPersonalizedRecommenderSystem.load_model(NON_PER_PATH)
item_reg_model = ItemBasedRegressionRecommenderSystem1.load_model(ITEM_REG_PATH)
print('Models loaded')

def get_user_recommendations(model_type, user_id):
    if model_type == 'non personalized':
        recommended_courses_id = non_per_model.recommend_items(user_id=0, top_n=10)
    elif model_type == 'item regression':
        recommended_courses_id = item_reg_model.recommend_items(user_id=user_id, top_n=10)
    else:
        raise ValueError('Invalid model type')
    return recommended_courses_id

def retrain_non_personalized_model(save=False):
    print('Retraining non personalized model...')
    non_per_model.fit(retrain=True)
    if save:
        non_per_model.save_model(NON_PER_PATH)

def retrain_item_regression_model(save=False):
    print('Retraining item regression model...')
    item_reg_model.fit(retrain=True)
    if save:
        item_reg_model.save_model(ITEM_REG_PATH)