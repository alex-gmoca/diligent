# Diligent Corporation Test

**Question 1: Zip File Generation Service**

This solution utilizes AWS CloudFormation to deploy a serverless architecture for generating and downloading zip files.

* **Components:**
    * **3 Lambda Functions:**
        * **`request_zip`:** 
            * Triggered by an API Gateway endpoint (`/request_download`).
            * Receives a target folder path as input.
            * Generates a unique `job_id`.
            * Enqueues the job to an SQS queue.
            * Stores job details (including `job_id`) in a database.
            * Returns the `job_id` to the API caller.
        * **`generate_zip`:**
            * Triggered by messages from the SQS queue.
            * Creates the zip file of the specified folder's contents.
            * Uploads the zip file to an S3 bucket.
            * Updates the job status and S3 location in the database.
        * **`download_zip`:**
            * Triggered by an API Gateway endpoint (`/download/{job_id}`).
            * Retrieves job status from the database.
            * If the job is complete, initiates the download of the zip file from S3.
            * If the job is still in progress, returns a message indicating the incomplete status.

**Question 2: Script Execution Service**

This solution leverages Terraform and AWS services to execute user-provided scripts.

* **Components:**
    * **API Gateway:**
        * Endpoint for uploading scripts (`/code/create`):
            * Receives the script (e.g., Python) as input.
            * Stores the script in an S3 bucket.
            * Creates a record in the database with the script_id.
            * Returns the script_id to the user.
        * Endpoint for triggering script execution  (`/code/{script_id}`):
            * Initiates an AWS Step Function execution.
    * **Step Function:**
        * Triggers an AWS Fargate task.
    * **Fargate Task:**
        * Downloads the script from S3 based on the provided script_id.
        * Executes the script within the container.
        * Stores the script output in a new S3 location.
        * Updates the database record with the output location and execution status.

**Question 3: Security scan tool**

This solution utilizes Terraform, Docker, and AWS Fargate to orchestrate a security scan tool.

* **Components:**
    * **Fargate Cluster:** Hosts the crawler and controller tasks.
    * **Task Definitions:**
        * **Controller:** 
            * Runs a Java application, assumed that it uses Maven to manage controller tasks.
        * **Crawler:** 
            * Based on a generic Ubuntu image.
            * It assumes that the crawler will download necessary libraries and dependencies.
            * It will run a bash script that reloads Chromium with specified flags.
    * **Orchestrator Container:**
            * Runs a Python script within a Fargate task.
            * Monitors the database for available job slots.
            * Spawns new Fargate tasks for crawler instances when slots are available.
            * Monitors running jobs for idle jobs (e.g., 5 minutes).
            * Kills timed-out tasks and updates their status in the database.

**Note:**

* Only essential files have been included, and the hierarchy of the files may not be the exact nested structure needed for a real deployment.

