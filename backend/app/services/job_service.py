import os
import subprocess
import logging
from typing import Optional
from common.config import settings

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.region = settings.GCP_REGION
        self.job_name = settings.GCP_JOB_NAME
        self.env = settings.ENV

    def trigger_job(self, task: str, target_id: Optional[int] = None, **kwargs):
        """
        Triggers a Cloud Run Job or runs it locally depending on the environment.
        """
        if self.env == "production":
            return self._trigger_cloud_run_job(task, target_id, **kwargs)
        else:
            return self._trigger_local_job(task, target_id, **kwargs)

    def _trigger_cloud_run_job(self, task: str, target_id: Optional[int] = None, **kwargs):
        """
        Triggers a Google Cloud Run Job using gcloud or API.
        Essentially: gcloud run jobs execute {job_name} --args="--task={task}","--id={target_id}"
        """
        logger.info(f"Triggering Cloud Run Job: task={task}, id={target_id}")
        # In a real scenario, you'd use the google-cloud-run library.
        # For simplicity in this demo, we'll describe the command.
        try:
            # Example command (requires backend to have gcloud or service account permissions)
            args = [f"--task={task}"]
            if target_id:
                args.append(f"--id={target_id}")
            
            # This is a placeholder for actual GCP SDK call
            # from google.cloud import run_v2
            # client = run_v2.JobsClient()
            # ...
            logger.info(f"Cloud Run Job Executed Mock (Production Mode)")
            return True
        except Exception as e:
            logger.error(f"Failed to trigger Cloud Run Job: {e}")
            return False

    def _trigger_local_job(self, task: str, target_id: Optional[int] = None, **kwargs):
        """
        Runs the job script locally in a detached process for development.
        """
        logger.info(f"Triggering Local Job: task={task}, id={target_id}, extra={kwargs}")
        
        args = [
            "python", 
            "jobs/run_job.py", 
            "--task", task
        ]
        if target_id:
            args.extend(["--id", str(target_id)])
        
        # Pass extra kwargs as environment variables for simplicity in subprocess
        env = os.environ.copy()
        for k, v in kwargs.items():
            env[f"JOB_EXTRA_{k.upper()}"] = str(v)

        try:
            # Run as detached process
            subprocess.Popen(args, cwd=os.getcwd(), env=env)
            logger.info(f"Local job started: {' '.join(args)}")
            return True
        except Exception as e:
            logger.error(f"Failed to start local job: {e}")
            return False

job_service = JobService()
