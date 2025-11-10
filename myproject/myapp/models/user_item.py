from dataclasses import dataclass
from datetime import datetime
from ..services.dynamodb_service import DynamoDBService

@dataclass
class UserItem:
 id: str
 first_name: str
 last_name: str
 staff_id: str
 password: str
 role: str
 created_at: str = datetime.utcnow().isoformat()
 updated_at: str = datetime.utcnow().isoformat()


 TABLE_NAME = "UserItems"

 def to_dict(self):
  return {
   "id": self.id,
   "first_name": self.first_name,
   "last_name": self.last_name,
   "staff_id": self.staff_id,
  "password": self.password,
  "role": self.role,
  "created_at": self.created_at,
  "updated_at": self.updated_at
  }

 def save(self):
  db = DynamoDBService()
  table = db.get_table(table_name = self.TABLE_NAME)
  table.put_item(Item=self.to_dict())
  return self
 
 @classmethod
 def get(cls, staff_id: str):
  """ Rettrieve item by Staff ID """
  db = DynamoDBService()
  table = db.get_table(table_name = cls.TABLE_NAME)
  response = table.get_item(Key={"staff_id": staff_id})
  item_data = response.get("Item")
  return cls(**item_data) if item_data else None
 
 @classmethod
 def all(cls):
  """ Return all Users """
  db = DynamoDBService()
  table = db.get_table(table_name = cls.TABLE_NAME)
  response = table.scan()
  return response.get("Items", [])
