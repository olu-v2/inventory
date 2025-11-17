import os
import boto3
from botocore.exceptions import ProfileNotFound, NoCredentialsError, ClientError
import uuid

class S3Service:
 def __init__(self):
  self.region = os.getenv("AWS_REGION", "us-east-1")
  self.profile = os.getenv("AWS_PROFILE")

  self._session = self._create_session()
  self._dynamodb = self._session.resource("s3")
  self._client = self._session.client("s3")

 def _create_session(self):
  """Create a boto3 session using the AWS profile or default credentials."""
  try:
   if self.profile:
    return boto3.Session(profile_name=self.profile, region_name=self.region)
   return boto3.Session(region_name=self.region)
  except ProfileNotFound:
   raise RuntimeError(
    f"AWS profile '{self.profile}' not found. "
    "Check your ~/.aws/credentials file."
   )
  
 def upload_image(self, file_obj, bucket_name, folder="items"):
        """
        Upload an image to S3 and return the public URL.

        Args:
            file_obj (InMemoryUploadedFile): The file from request.FILES['image'].
            folder (str): Optional folder path prefix.

        Returns:
            str: The S3 public URL of the uploaded image.
        """

        # Generate a unique key for the image
        s3_key = f"{folder}/{uuid.uuid4()}_{file_obj.name}"

        try:
            self._client.upload_fileobj(
                file_obj,
                bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": file_obj.content_type,
                }
            )

            return f"https://{bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"

        except NoCredentialsError:
            raise RuntimeError("AWS credentials not found. Check your environment configuration.")
        except ClientError as e:
            raise RuntimeError(f"Failed to upload image: {e}")