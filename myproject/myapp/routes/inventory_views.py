from django.http import JsonResponse
import uuid
from datetime import datetime
from schemas.inventory import CreateItemRequest, CreateItemResponse
from models.inventory_item import InventoryItem

def list_or_add_items(request):
    """ This calls the all method defined in the models/inventory_item method file to get all the items in stock """
    if request.method == "GET":
        items = InventoryItem.all()
        return JsonResponse(items, safe=False)
    elif request.method == "POST":
        # Use the validated data from the middleware
        data = request.validated_data._raw
        item = InventoryItem(
            id=str(uuid.uuid4()),
            name=data["name"],
            quantity=data["quantity"],
            tag=data["tag"],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )
        item.save()
        response_data = CreateItemResponse(
            id = item.id,
            name = item.name,
            quantity = item.quantity,
            tag = item.tag,
            created_at = item.created_at,
            updated_at = item.updated_at
        ).to_dict()
        return JsonResponse(response_data, status=201)
 
def item_detail(request, item_id):
 """Handles GET, PATCH, and DELETE operations for a specific inventory item."""
 if request.method == "GET":
     item = InventoryItem.get(item_id)
     if not item:
         return  JsonResponse({"error": "Item not found"}, status=404)
     return JsonResponse(item.to_dict(), status=200)
 elif request.method == "PATCH":
     data = getattr(request, "validated_data", None)
     if not data:
         return JsonResponse({"error": "Missing or invalid data"}, status=400)
     item = InventoryItem.get(item_id)
     if not item:
         return JsonResponse({"error": "Item not found"}, status=404)
     updated_fields = {}
     for key, value in data._raw.items():
         if hasattr(item, key):
             setattr(item, key, value)
             updated_fields[key] = value
     item.updated_at = datetime.utcnow().isoformat()
     item.save()
     return JsonResponse({
          "status": "ok",
          "updated_fields": updated_fields
      }, status=200)
 elif request.method == "DELETE":
        success = InventoryItem.delete(item_id)
        if not success:
            return JsonResponse({"error": "Item not found"}, status=404)
        return JsonResponse({"status": "deleted"}, status=204)
 return JsonResponse({"error": "Method not allowed"}, status=405)

list_or_add_items.request_schema = CreateItemRequest
list_or_add_items.response_schema = CreateItemResponse