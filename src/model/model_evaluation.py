import mlflow.sklearn
import numpy as np
import pandas as pd
import pickle
import logging
import yaml
import mlflow
import mlflow.lightgbm
from mlflow.models import infer_signature
import mlflow.sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix
import os
import matplotlib.pyplot as plt
import seaborn as sns
import json
from dotenv import load_dotenv

logger = logging.getLogger('model_evaluation')
logger.setLevel('DEBUG')

console_handler = logging.StreamHandler()
console_handler.setLevel('DEBUG')

file_handler = logging.FileHandler('model_evaluation_errors.log')
file_handler.setLevel('ERROR')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

def load_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        df.fillna('', inplace=True)
        logger.debug('Data loaded and NaNs filled from %s', file_path)
        return df
    except Exception as e:
        logger.error('Error loading data from %s: %s', file_path, e)
        raise

def load_model(model_path: str):
    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        logger.debug('Model loaded from %s', model_path)
        return model
    except Exception as e:
        logger.error('Error occurred while loading model from %s: %s', model_path, e)
        raise

def load_vectorizer(vectorizer_path: str) -> TfidfVectorizer:
    try:
        with open(vectorizer_path, 'rb') as file:
            vectorizer = pickle.load(file)
        logger.debug('TF-IDF vectorizer loaded from %s', vectorizer_path)
        return vectorizer
    except Exception as e:
        logger.error('Error loading vectorizer from %s: %s', vectorizer_path, e)
        raise

def load_params(params_path: str) -> dict:
    try:
        with open(params_path, 'r') as file:
            params = yaml.safe_load(file)
        logger.debug('Parameters loaded from %s:',params_path)
        return params
    except Exception as e:
        logger.error('Error occurred while loading parameters from %s: %s', params_path, e)
        raise

def evaluate_model(model, X_test: np.ndarray, y_test: np.ndarray):
    try:
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred)

        logger.debug('Model evaluation completed')
        
        return report, cm
    except Exception as e:
        logger.error('Unexpected error occurred while evaluating model: %s', e)
        raise

def log_confusion_matrix(cm, dataset_name):
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f"Confusion Matrix for {dataset_name}")
    plt.xlabel('Predicted')
    plt.ylabel('Actual')

    cm_file_path = f"confusion_matrix_{dataset_name}.png"
    plt.savefig(cm_file_path)
    mlflow.log_artifact(cm_file_path)
    plt.close()

def save_model_info(run_id: str, model_path: str, file_path: str) -> None:
    try:
        model_info = {
            'run_id': run_id,
            'model_path': model_path
        }

        with open(file_path, 'w') as file:
            json.dump(model_info, file, indent=4)
        logger.debug('Model info saved to %s', file_path)
        
    except Exception as e:
        logger.error('Unexpected error occurred while saving model info: %s', e)
        raise

def main():
    load_dotenv()
    print(os.getenv('AWS-MLFLOW'))
    # Get the AWS MLflow URI from .env file
    aws_mlflow_uri = os.getenv('AWS-MLFLOW')

    mlflow.set_tracking_uri(aws_mlflow_uri)

    mlflow.set_experiment('dvc-pipeline-runs')

    with mlflow.start_run() as run:
        try:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
            params = load_params(os.path.join(root_dir, 'params.yaml'))

            for key, value in params.items():
                mlflow.log_param(key,value)

            model = load_model(os.path.join(root_dir, 'lgbm_model.pkl'))
            vectorizer = load_vectorizer(os.path.join(root_dir, 'tfidf_vectorizer.pkl'))

            test_data = load_data(os.path.join(root_dir, 'data/interim/test_processed.csv'))

            X_test_tfidf = vectorizer.transform(test_data['clean_comment'].values)
            y_test = test_data['category'].values

            input_example = pd.DataFrame(X_test_tfidf.toarray()[:5], columns=vectorizer.get_feature_names_out())

            signature = infer_signature(input_example, model.predict(X_test_tfidf[:5]))

            logger.info("Starting MLflow model logging...")
            model_path = 'lgbm_model'
            
            try:
                mlflow.lightgbm.log_model(
                    model,
                    model_path,
                    signature=signature,
                    input_example=input_example
                )
                logger.info("MLflow model logging completed successfully")
                
                # Verify the model was actually logged
                client = mlflow.tracking.MlflowClient()
                artifacts = client.list_artifacts(run.info.run_id)
                model_found = any(art.path == model_path for art in artifacts)
                
                if model_found:
                    logger.info("Model verified in MLflow artifacts")
                    final_model_path = model_path
                else:
                    logger.warning("Model not found in artifacts, will register directly")
                    raise Exception("Model not found in MLflow artifacts")
                
            except Exception as model_log_error:
                logger.warning(f"MLflow model logging failed or model not accessible: {model_log_error}")
                logger.info("Attempting alternative model logging approach...")
                
                # Try alternative approach - register model directly without intermediate logging
                try:
                    model_name = 'yt_chrome_plugin_model'
                    
                    # Try logging with a different path name
                    temp_model_path = 'model_direct'
                    mlflow.lightgbm.log_model(
                        model, 
                        temp_model_path,
                        signature=signature,
                        input_example=input_example
                    )
                    
                    # Check if this one worked
                    client = mlflow.tracking.MlflowClient()
                    artifacts = client.list_artifacts(run.info.run_id)
                    model_found = any(art.path == temp_model_path for art in artifacts)
                    
                    if model_found:
                        logger.info(f"Alternative model logging successful at: {temp_model_path}")
                        final_model_path = temp_model_path
                    else:
                        # Model still not in artifacts, register directly and use registered model URI
                        logger.warning("Model still not in artifacts. Registering existing model...")
                        model_version = mlflow.register_model(
                            f"runs:/{run.info.run_id}/{temp_model_path}", 
                            model_name
                        )
                        final_model_path = f"models:/{model_name}/{model_version.version}"
                        logger.info(f"Model registered as: {final_model_path}")
                    
                except Exception as reg_error:
                    logger.error(f"All model logging attempts failed: {reg_error}")
                    logger.info("Creating direct S3 artifact path...")
                    
                    # As absolute last resort, create the S3 path directly
                    # This mimics what the tutorial has
                    artifact_uri = run.info.artifact_uri
                    final_model_path = f"{artifact_uri}/lgbm_model"
                    logger.warning(f"Using direct S3 path as final fallback: {final_model_path}")

            save_model_info(run.info.run_id, final_model_path, 'experiment_info.json')

            mlflow.log_artifact(os.path.join(root_dir, 'tfidf_vectorizer.pkl'))

            report, cm = evaluate_model(model, X_test_tfidf, y_test)

            for label, metrics in report.items():
                if isinstance(metrics, dict):
                    mlflow.log_metrics({
                        f"test_{label}_precision": metrics['precision'],
                        f"test_{label}_recall": metrics['recall'],
                        f"test_{label}_f1-score": metrics['f1-score'],
                    })

            log_confusion_matrix(cm, "Test Data")

            mlflow.set_tag("model_type", "LightGBM")
            mlflow.set_tag("task", "Sentiment Analysis")
            mlflow.set_tag("dataset", "Youtube Comments")
            
        except Exception as e:
            logger.error(f"Failed to complete model evaluation: {e}")

if __name__ == '__main__':
    main()