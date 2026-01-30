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
        self.job_name = settings.CLOUD_RUN_JOB_NAME
        self.env = settings.ENV

    def trigger_job(self, task: str, target_id: Optional[int] = None, **kwargs):
        """
        Triggers a Cloud Run Job or runs it locally depending on the environment.
        """
        if self.env in ["production", "preview"]:
            return self._trigger_cloud_run_job(task, target_id, **kwargs)
        else:
            return self._trigger_local_job(task, target_id, **kwargs)

    def _trigger_cloud_run_job(self, task: str, target_id: Optional[int] = None, **kwargs):
        """
        Triggers a Google Cloud Run Job using the official SDK.
        """
        logger.info(f"Triggering Cloud Run Job '{self.job_name}': task={task}, id={target_id}")
        
        if not self.project_id:
            logger.error("GCP_PROJECT_ID is not set. Cannot trigger Cloud Run Job.")
            return False

        try:
            from google.cloud import run_v2
            
            client = run_v2.JobsClient()
            
            # Prepare arguments for the container
            args = [f"--task={task}"]
            if target_id:
                args.append(f"--id={target_id}")
            
            # Formatting job path: projects/{project}/locations/{location}/jobs/{job}
            job_path = f"projects/{self.project_id}/locations/{self.region}/jobs/{self.job_name}"
            
            request = run_v2.RunJobRequest(
                name=job_path,
                overrides={
                    "container_overrides": [
                        {
                            "args": args
                        }
                    ]
                }
            )
            
            operation = client.run_job(request=request)
            logger.info(f"Cloud Run Job triggered. Operation: {operation.operation.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger Cloud Run Job via SDK: {e}")
            # Fallback or just fail
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
