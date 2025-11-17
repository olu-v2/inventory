from django.http import JsonResponse
from datetime import datetime
from myapp.models.user_item import UserItem
import json

def login(request):
 if request.method != "POST":
   return JsonResponse({"error": "Method not allowed"}, status=405)
 try:
   body = json.loads(request.body)
   staff_id = body.get("staff_id")
   password = body.get("password")
   user = UserItem.get(staff_id)
   if user.password == password:
     return JsonResponse({
       "status": "ok",
       "message": "Login successful"
     }, status = 200)
   else:
     return JsonResponse({
       "status": "failed",
       "message": "Username or password is incorrect"
     }, status = 401)
 except Exception as e:
   return JsonResponse({"error": str(e)}, status=500)