from schema_val_pkg.base import BaseSchema
from schema_val_pkg.fields import Field

class CreateItemRequest(BaseSchema):
   name = Field(str)
   quantity = Field(int)
   image_url = Field(str)
   tag = Field(str)

class CreateItemResponse(BaseSchema):
   id = Field(str)
   name = Field(str)
   quantity = Field(int)
   image_url = Field(str)
   tag = Field(str)
   created_at = Field(str)
   updated_at = Field(str)