import mlflow
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import subprocess
import time
import requests
from typing import Dict, Any, Optional
import yaml
import os
from pyngrok import ngrok
import logging

logger = logging.getLogger(__name__)

class MLflowManager:
    """Manages MLflow tracking with local/remote server support"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mlflow_config = config.get('mlflow', {})
        self.client = None
        self.run = None
        
    def setup_tracking(self):
        """Setup MLflow tracking URI with ngrok if needed"""
        # Priority: env var > config file > default
        tracking_uri = os.environ.get('MLFLOW_TRACKING_URI') or \
                       self.mlflow_config.get('tracking_uri', 'http://localhost:5000')

        # Setup ngrok for Colab
        if self.mlflow_config.get('use_ngrok', False):
            tracking_uri = self._setup_ngrok()

        # Setup SSH tunnel for Lambda (alternative to ngrok)
        elif self.mlflow_config.get('ssh_tunnel', {}).get('enabled', False):
            tracking_uri = self._setup_ssh_tunnel()
        
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient(tracking_uri)
        
        # Create or get experiment
        experiment_name = self.mlflow_config.get('experiment_name', 'whisper-training')
        try:
            experiment = mlflow.create_experiment(experiment_name)
        except:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment:
                experiment = experiment.experiment_id
        
        mlflow.set_experiment(experiment_name)
        logger.info(f"MLflow tracking URI: {tracking_uri}")
        logger.info(f"Experiment: {experiment_name}")
        
        return tracking_uri
    
    def _setup_ngrok(self):
        """Setup ngrok tunnel for Colab"""
        ngrok_token = os.environ.get('NGROK_TOKEN', 
                                     self.mlflow_config.get('ngrok_token'))
        if not ngrok_token:
            raise ValueError("NGROK_TOKEN not found in environment or config")
        
        # Authenticate ngrok
        ngrok.set_auth_token(ngrok_token)
        
        # Start tunnel to local MLflow server
        local_port = 5000
        public_url = ngrok.connect(local_port)
        
        logger.info(f"Ngrok tunnel established: {public_url}")
        
        # Wait for tunnel to be ready
        time.sleep(2)
        
        # Test connection
        try:
            response = requests.get(f"{public_url}/health")
            if response.status_code == 200:
                logger.info("Successfully connected to MLflow through ngrok")
        except Exception as e:
            logger.warning(f"Could not verify MLflow connection: {e}")
        
        return public_url
    
    def _setup_ssh_tunnel(self):
        """Setup SSH tunnel for Lambda/cloud instances"""
        ssh_config = self.mlflow_config.get('ssh_tunnel', {})
        local_port = ssh_config.get('local_port', 5000)
        remote_port = ssh_config.get('remote_port', 5001)
        
        # SSH tunnel command (you'll need to set this up)
        # ssh -L remote_port:localhost:local_port your_local_machine
        
        return f"http://localhost:{remote_port}"
    
    def start_run(self, run_name: Optional[str] = None):
        """Start MLflow run with parameters"""
        if not run_name:
            from datetime import datetime
            run_name = f"whisper_sw_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.run = mlflow.start_run(run_name=run_name)
        
        # Log parameters
        self._log_params()
        
        # Log tags
        tags = self.mlflow_config.get('tags', {})
        for key, value in tags.items():
            mlflow.set_tag(key, value)
        
        logger.info(f"Started MLflow run: {run_name}")
        return self.run
    
    def _log_params(self):
        """Log all configuration parameters"""
        # Log model params
        model_config = self.config.get('model', {})
        for key, value in model_config.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    mlflow.log_param(f"model.{key}.{sub_key}", sub_value)
            else:
                mlflow.log_param(f"model.{key}", value)
        
        # Log training params
        training_config = self.config.get('training', {})
        for key, value in training_config.items():
            if not isinstance(value, dict):
                mlflow.log_param(f"training.{key}", value)
        
        # Log dataset params
        dataset_config = self.config.get('dataset', {})
        for key, value in dataset_config.items():
            if not isinstance(value, dict):
                mlflow.log_param(f"dataset.{key}", value)
    
    def log_metrics(self, metrics: Dict[str, float], step: int):
        """Log metrics to MLflow"""
        for key, value in metrics.items():
            mlflow.log_metric(key, value, step=step)
    
    def log_model(self, model, processor, artifact_path="model"):
        """Log model to MLflow"""
        mlflow.pytorch.log_model(
            model, 
            artifact_path,
            registered_model_name="whisper-large-v2-sw"
        )
        
        # Also save processor
        processor.save_pretrained("temp_processor")
        mlflow.log_artifacts("temp_processor", "processor")
    
    def log_artifacts(self, local_path: str, artifact_path: Optional[str] = None):
        """Log artifacts like tensorboard files"""
        mlflow.log_artifacts(local_path, artifact_path)
    
    def end_run(self):
        """End MLflow run"""
        if self.run:
            mlflow.end_run()
            logger.info("Ended MLflow run")