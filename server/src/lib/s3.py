import boto3
from botocore.exceptions import ClientError
from src.core.config import settings
from src.lib.logger import logger
from fastapi import HTTPException


class S3Client:
    def __init__(
        self, bucket_name: str = settings.s3_bucket_name, region_name: str = "us-east-1"
    ):
        client = boto3.resource("s3")
        self.bucket = client.Bucket(bucket_name)
        self.bucket_name = settings.s3_bucket_name

    def upload_file(self, path_to_file: str, file_key: str):
        try:
            self.bucket.upload_file(path_to_file, file_key)
            logger.info(f"File {file_key} uploaded successfully to {self.bucket_name}")
            return f"https://{settings.cloudfront_domain}/{file_key}"
        except ClientError as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail=f"Error uploading file {e}")

    def get_file_size(self, file_key: str):
        try:
            response = self.bucket.head_object(Key=file_key)
            return response["ContentLength"]
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return None
            raise

    def delete_file(self, file_key: str):
        try:
            self.bucket.delete_object(Key=file_key)
            logger.info(f"Deleted file {file_key}")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return None
            raise

    def download_file(self, file_key: str, path_to_download_to: str):
        try:
            self.bucket.download_file(file_key, path_to_download_to)
            logger.info(
                f"File {file_key} downloaded successfully to {path_to_download_to}"
            )
        except ClientError as e:
            logger.error(f"Error downloading file: {e}")
            raise HTTPException(status_code=500, detail=f"Error downloading file {e}")

    def delete_directory(self, path: str):
        # make sure the prefix ends with '/' if it's meant to be a directory
        if not path.endswith("/"):
            path += "/"

        # list all objects with the directory prefix
        paginator = self.bucket.get_paginator("list_objects_v2")
        pages = paginator.paginate(Prefix=path)

        # collect all object keys to delete
        objects_to_delete = []
        for page in pages:
            if "Contents" in page:
                for obj in page["Contents"]:
                    objects_to_delete.append({"Key": obj["Key"]})

        # delete objects in batches (max 1000 per batch)
        if objects_to_delete:
            for i in range(0, len(objects_to_delete), 1000):
                batch = objects_to_delete[i : i + 1000]
                self.bucket.delete_objects(Delete={"Objects": batch})
            logger.info(f"Deleted {len(objects_to_delete)} objects from {path}")
        else:
            logger.info(f"No objects found with prefix {path}")

        return True


s3_client = S3Client()
