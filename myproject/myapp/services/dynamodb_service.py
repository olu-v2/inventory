import os
import boto3
from botocore.exceptions import ProfileNotFound

class DynamoDBService:
    """
    Handles the connection and all DynamoDB operations for this project.
    Reusable across multiple tables.
    """

    def __init__(self):
     self.region = os.getenv("AWS_REGION", "us-east-1")
     self.profile = os.getenv("AWS_PROFILE")

     self._session = self._create_session()
     self._dynamodb = self._session.resource("dynamodb")
     self._client = self._session.client("dynamodb")

     # optional cache for already accessed tables
     self._tables_cache = {}

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

    def get_table(self, table_name):
     """Return a table resource, caching it for future use."""
     if table_name not in self._tables_cache:
         self._tables_cache[table_name] = self._dynamodb.Table(table_name)
     return self._tables_cache[table_name]

    def list_tables(self):
     """Return all DynamoDB tables in the current region."""
     response = self._client.list_tables()
     return response.get("TableNames", [])

    def create_table(self, table_name, key_schema, attribute_definitions, provisioned_throughput):
     """Create a new DynamoDB table."""
     table = self._dynamodb.create_table(
         TableName=table_name,
         KeySchema=key_schema,
         AttributeDefinitions=attribute_definitions,
         ProvisionedThroughput=provisioned_throughput,
     )
     table.wait_until_exists()
     return table

    def put_item(self, table_name, item: dict):
     """Insert or update an item in the specified table."""
     table = self.get_table(table_name)
     table.put_item(Item=item)
     return {"status": "ok", "table": table_name, "item": item}

    def get_item(self, table_name, key: dict):
     """Retrieve an item by its key."""
     table = self.get_table(table_name)
     response = table.get_item(Key=key)
     return response.get("Item")

    def delete_item(self, table_name, key: dict):
     """Delete an item by its key."""
     table = self.get_table(table_name)
     table.delete_item(Key=key)
     return {"status": "deleted", "key": key}
