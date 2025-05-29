from django.urls import path
from .views import CreateOrderView, OrderListView

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('add/<int:file_id>/', CreateOrderView.as_view(), name='order-add'),
]
