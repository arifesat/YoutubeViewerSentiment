import json
import os
from dotenv import load_dotenv
import logging
import mlflow
import mlflow.tracing
import mlflow.tracking
import time
from mlflow.exceptions import MlflowException, RestException

load_dotenv()
aws_mlflow_uri = os.getenv('AWS-MLFLOW')
mlflow.set_tracking_uri(aws_mlflow_uri)

logger = logging.getLogger('model_registration')
logger.setLevel('DEBUG')

console_handler = logging.StreamHandler()
console_handler.setLevel('DEBUG')

file_handler = logging.FileHandler('model_registration_errors.log')
file_handler.setLevel('ERROR')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def load_model_info(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            model_info = json.load(file)
        logger.debug('Model info loaded from %s', file_path)
        return model_info
    except FileNotFoundError:
        logger.error('File not found: %s', file_path)
        raise
    except Exception as e:
        logger.error('Unexpected error occurred while loading model info: %s', e)
        raise

def register_model(model_name: str, model_info: dict):
    try:
        # Check if model_path is already a registered model URI
        if model_info['model_path'].startswith('models:/'):
            model_uri = model_info['model_path']
            logger.info(f"Model path is already a registered model URI: {model_uri}")
            # Skip registration since model is already registered
            logger.info(f"Model {model_name} is already registered. Skipping registration step.")
            return
        else:
            model_uri = f"runs:/{model_info['run_id']}/{model_info['model_path']}"
        
        logger.info(f"Attempting to register model with URI: {model_uri}")
        
        # Verify the model exists before attempting registration
        try:
            client = mlflow.tracking.MlflowClient()
            run = client.get_run(model_info['run_id'])
            logger.info(f"Found run: {run.info.run_id}")
            
            # List artifacts to verify model path exists
            artifacts = client.list_artifacts(model_info['run_id'])
            logger.info(f"Available artifacts: {[art.path for art in artifacts]}")
            
        except Exception as e:
            logger.error(f"Failed to verify run or artifacts: {e}")
            raise
        
        # Register the model with retries
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Registration attempt {attempt + 1}/{max_retries}")
                model_version = mlflow.register_model(model_uri, model_name)
                logger.info(f"Model registered successfully. Version: {model_version.version}")
                break
            except (RestException, MlflowException) as e:
                if "500" in str(e) or "connection" in str(e).lower():
                    if attempt < max_retries - 1:
                        logger.warning(f"Registration attempt {attempt + 1} failed with server error. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error(f"All registration attempts failed: {e}")
                        raise
                else:
                    logger.error(f"Registration failed with non-retryable error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error during registration: {e}")
                raise
        
        # Check if we should skip stage transition
        skip_staging = os.getenv('SKIP_MODEL_STAGING', 'false').lower() == 'true'
        if skip_staging:
            logger.info(f"Skipping stage transition for model {model_name} version {model_version.version} due to SKIP_MODEL_STAGING=true")
            return
        
        # Transition to staging with retries
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Stage transition attempt {attempt + 1}/{max_retries}")
                client.transition_model_version_stage(
                    name=model_name,
                    version=model_version.version,
                    stage='Staging'
                )
                logger.info(f"Model {model_name} version {model_version.version} successfully transitioned to Staging.")
                return
            except (RestException, MlflowException) as e:
                if "500" in str(e) or "connection" in str(e).lower() or "max retries exceeded" in str(e).lower():
                    if attempt < max_retries - 1:
                        logger.warning(f"Stage transition attempt {attempt + 1} failed with server error. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error(f"All stage transition attempts failed: {e}")
                        # Don't raise here - model registration succeeded, just stage transition failed
                        logger.warning(f"Model {model_name} version {model_version.version} was registered but could not be transitioned to Staging due to server issues.")
                        return
                else:
                    logger.error(f"Stage transition failed with non-retryable error: {e}")
                    # Don't raise here - model registration succeeded
                    logger.warning(f"Model {model_name} version {model_version.version} was registered but could not be transitioned to Staging.")
                    return
            except Exception as e:
                logger.error(f"Unexpected error during stage transition: {e}")
                # Don't raise here - model registration succeeded
                logger.warning(f"Model {model_name} version {model_version.version} was registered but could not be transitioned to Staging.")
                return
        
    except Exception as e:
        logger.error('Unexpected error occurred while model registration: %s', e)
        raise

def main():
    try:
        model_info_path = 'experiment_info.json'
        model_info = load_model_info(model_info_path)

        model_name = 'yt_chrome_plugin_model'

        register_model(model_name, model_info)
        
        logger.info("Model registration process completed successfully.")
        
    except Exception as e:
        logger.error('Failed to complete the model registration process: %s', e)
        raise

if __name__ == '__main__':
    main()