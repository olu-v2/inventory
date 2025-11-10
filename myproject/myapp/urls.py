from django.urls import path
from . import views
from .routes import inventory_views, user_views
urlpatterns = [
path('', views.index, name='index'),
path('items/', inventory_views.list_or_add_items, name="items"),
path("items/<str:item_id>/",inventory_views.item_detail, name="item_detail"),
path("tables/", views.list_tables, name="list_tables"),
path("table/", views.create_table, name="create_table"),
path("login/", user_views.login, name="login")
]