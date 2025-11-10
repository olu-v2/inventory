from datetime import datetime
from .base import BaseSchema

class CreateItemRequest(BaseSchema):
 def validate(self, data: dict):
  if "name" not in data or not isinstance(data["name"], str):
   raise ValueError("Field 'name' is required and must be a string.")
  if "quantity" not in data or not isinstance(data["quantity"], int):
   raise ValueError("Field 'quantity' is required and must be an integer.")
  if "image" not in data or not isinstance(data["image"], str):
   raise ValueError("An image is required.")
  if "tag" not in data or not isinstance(data["tag"], str):
   raise ValueError("Field 'tag' is required anf must be a string")
  
class CreateItemResponse(BaseSchema):
 def validate(self, data: dict):
  required = ["id", "name", "quantity", "image", "tag", "created_at", "updated_at"]
  for field in required:
   if field not in data:
    raise ValueError(f"Missing required field '{field}'")