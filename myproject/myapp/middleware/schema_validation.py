import json
from django.http import JsonResponse

class SchemaValidationMiddleware:
  """ 
  This automatically vaidates request and response payloads
  using the classes defined in the view function
  """

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    if not request.path.startswith('inventory/items'):
      return self.get_response(request)
    
    response = self.process_view(request)
    if response:
      return response
    
    response = self.get_response(request)
    return response

  def process_view(self, request, view_func, view_args, view_kwargs):
    if request.method in ("POST", "PUT", "PATCH"):
      try:
        data = json.loads(request.body or "{}")
        request.validated_data = type("Obj", (object,), {"_raw": data})
      except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    return None
