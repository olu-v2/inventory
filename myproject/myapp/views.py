from django.http import JsonResponse, HttpResponse
from .services.dynamodb_service import DynamoDBService
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

def index(request):
    return HttpResponse("You are at index.")

def list_tables(request):
    dynamo = DynamoDBService()
    tables = dynamo.list_tables()
    return JsonResponse({"tables": tables})

@csrf_exempt
def create_table(request):
    if request.method != "POST":
     return JsonResponse({"error": "Method not allowed"}, status=405)
    print(request.body)
    try:
        body = json.loads(request.body)
        table_name = body.get("table_name")
        key_schema = body.get("key_schema")
        attribute_definitions = body.get("attribute_definitions")
        provisioned_throughput = body.get("provisioned_throughput", {
          "ReadCapacityUnits": 5,
          "WriteCapacityUnits": 5
        })

        if not all([table_name, key_schema, attribute_definitions]):
            return JsonResponse(
                { "error" : "Midding required fields: table_name, key_schema, attribute_definitions"},
                status=400
            )
        dynamodb = DynamoDBService()
        table = dynamodb.create_table(
            table_name=table_name,
            key_schema=key_schema,
            attribute_definitions=attribute_definitions,
            provisioned_throughput=provisioned_throughput
        )
        return JsonResponse({
            "status" : "success",
            "table_name" : table_name,
            "table_status": table.table_status,
            "table_arn": table.table_arn,
        }, status=200)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
         return JsonResponse({"error": str(e)}, status=500)

