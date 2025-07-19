import boto3


class S3Client:
    def __init__(self):
        self.client = boto3.client("s3")

    def upload_file(self, file, bucket_name, file_key):
        self.client.upload_fileobj(file, bucket_name, file_key)


s3_client = S3Client()
