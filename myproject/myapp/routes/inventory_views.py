from django.http import JsonResponse
import uuid
from datetime import datetime
from schemas.inventory import CreateItemRequest, CreateItemResponse
from models.inventory_item import InventoryItem
import json
import boto3
import os

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

def checkout(request, item_id):
    """ 
        This is a checkout function that is going to run when an inventory item is taken out of stock.
        And when the stock quantity is below 5, a lambda function is triggered that publishes a message to an sns topic.
        An email address is subscribed to the SNS topic, to notify whoever is in charge that that item is low on stock.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        if not isinstance(data, list) or len(data) == 0:
            return JsonResponse({"error": "Expected a non-empty list of items"}, status=400)
        
        lambda_client = boto3.client(
                "lambda",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                profile_name=os.getenv("AWS_PROFILE")
            )
        LOW_STOCK_THRESHOLD = 5
        results = []

        for entry in data:
            item_id = entry.get("item_id")
            quantity_to_deduct = entry.get("quantity")
            if not item_id or quantity_to_deduct is None or quantity_to_deduct <= 0:
                results.append({
                    "item_id" : item_id,
                    "status": "failed",
                    "error": "Invalid item_id or quantity"
                })
                continue

            try:
                item = InventoryItem.get(item_id=item_id)
            except Exception as e:
                results.append({
                    "item_id": item_id,
                    "status": "failed",
                    "error": f"Item not found: {str(e)}"
                })
                continue
        
            if item.quantity < quantity_to_deduct:
                results.append({
                    "item_id": item_id,
                    "name": item.name,
                    "status": "failed",
                    "error": "Not enough stock"
                })
                continue

            item.quantity -= quantity_to_deduct
            item.save()

            if item.quantity <= LOW_STOCK_THRESHOLD:
                

                payload = {
                    "item_id": item.id,
                    "item_name": item.name,
                    "quantity": item.quantity,
                    "message": f"Low stock alert for {item.name}: {item.quantity} left."
                }

                lambda_client.invoke(
                    FunctionName="low_stock_alert_handler",
                    InvocationType="Event",  # async
                    Payload=json.dumps(payload)
                )
            results.append({
                "item_id": item.id,
                "name": item.name,
                "remaining_quantity": item.quantity,
                "status": "success"
            })

        return JsonResponse({
            "message": "Checkout successful",
            "item": {
                "id": item.id,
                "name": item.name,
                "remaining_quantity": item.quantity
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
def restock(request, item_id):
    """ 
        This is a function that updates the quantity of an inventory item. 
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        quantity_to_restock = int(data.get("quantity", 0))

        if quantity_to_restock is None or quantity_to_restock <= 0:
            return JsonResponse({"error": "Invalid quantity"}, status=400)

        try:
            item = InventoryItem.get(item_id=item_id)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        item.quantity += quantity_to_restock
        item.save()

        return JsonResponse({
            "message": "Checkout successful",
            "item": {
                "id": item.id,
                "name": item.name,
                "remaining_quantity": item.quantity
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    

list_or_add_items.request_schema = CreateItemRequest
list_or_add_items.response_schema = CreateItemResponse