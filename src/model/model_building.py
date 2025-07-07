import numpy as np
import pandas as pd
import os
import pickle
import yaml
import logging
import lightgbm as lgb
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger('model_building')
logger.setLevel('DEBUG')

console_handler = logging.StreamHandler()
console_handler.setLevel('DEBUG')

file_handler = logging.FileHandler('model_building_errors.log')
file_handler.setLevel('ERROR')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

def load_params(params_path: str) -> dict:
    try:
        with open(params_path, 'r') as file:
            params = yaml.safe_load(file)
        logger.debug('Parameters retrieved from %s', params_path)
        return params
    except FileNotFoundError:
        logger.error('File not found: %s', params_path)
        raise
    except yaml.YAMLError as e:
        logger.error('YAML error: %s', e)
        raise
    except Exception as e:
        logger.error('Unexpected error: %s', e)
        raise

def load_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        df.fillna('', inplace=True)
        logger.debug('Data loaded and NaNs filled from file: %s', file_path)
        return df
    except pd.errors.ParserError as e:
        logger.error('Failed to parse the CSV file: %s', e)
        raise
    except Exception as e:
        logger.error('Unexpected error occurred while loading the data: %s', e)
        raise

def get_root_directory() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, '../../'))


def apply_tfidf(train_data: pd.DataFrame, max_features: int, ngram_range: tuple) -> tuple:
    try:
        vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=ngram_range)

        X_train = train_data['clean_comment'].values
        y_train = train_data['category'].values

        X_train_tfidf = vectorizer.fit_transform(X_train)

        logger.debug(f"TF-IDF transformation complete. Train shape: {X_train_tfidf.shape}")

        with open(os.path.join(get_root_directory(), 'tfidf_vectorizer.pkl'), 'wb') as f:
            pickle.dump(vectorizer, f)
        
        logger.debug('TF-IDF applied with trigrams and data transformed')
        return X_train_tfidf, y_train
    except Exception as e:
        logger.error('Unexpected error occurred during TF-IDF transformation: %s', e)
        raise


def train_light_bm(X_train: np.ndarray, y_train: np.ndarray, learning_rate: float, max_depth: int, n_estimators: int) -> lgb.LGBMClassifier:
    try:
        best_model = lgb.LGBMClassifier(
            objective = 'multiclass',
            num_class = 3,
            metric = 'multi_logloss',
            is_unbalance = True,
            class_weight = 'balanced',
            reg_alpha = 0.1,
            reg_lambda = 0.1,
            learning_rate = learning_rate,
            max_depth = max_depth,
            n_estimators = n_estimators
        )

        best_model.fit(X_train, y_train)
        logger.debug('LightBM model trainin compelte')
        return best_model
    except Exception as e:
        logger.error('Unexpected error occurred while training LightBM model: %s', e)
        raise

