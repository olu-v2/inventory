from dataclasses import dataclass
from datetime import datetime
from ..services.dynamodb_service import DynamoDBService

@dataclass
class InventoryItem:
 id: str
 name: str
 quantity: int
 tag: str
 image_url: str
 created_at: str = datetime.utcnow().isoformat()
 updated_at: str = datetime.utcnow().isoformat()
 
 TABLE_NAME = "InventoryItems"

 def to_dict(self):
  return {
   "id": self.id,
   "name": self.name,
   "quantity": self.quantity,
   "tag": self.tag,
   "image_url": self.image_url,
   "created_at": self.created_at,
   "updated_at": self.updated_at,
  }

 def save(self):
  """ Save to DynamoDB """
  db = DynamoDBService()
  table = db.get_table(table_name = self.TABLE_NAME)
  table.put_item(Item=self.to_dict())
  return self
 
 @classmethod
 def get(cls, item_id: str):
  """ Rettrieve item by ID """
  db = DynamoDBService()
  table = db.get_table(table_name = cls.TABLE_NAME)
  response = table.get_item(Key={"id": item_id})
  item_data = response.get("Item")
  return cls(**item_data) if item_data else None
 
 @classmethod
 def delete(cls, item_id: str):
  db = DynamoDBService()
  table = db.get_table(table_name=cls.TABLE_NAME)
  response = table.delete_item(Key={"id": item_id})
  return response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200

 
 @classmethod
 def all(cls):
  """ Return all inventory """
  db = DynamoDBService()
  table = db.get_table(table_name = cls.TABLE_NAME)
  response = table.scan()
  return response.get("Items", [])