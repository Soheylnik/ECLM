from django.views import View
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from files.models import UploadedFile
from .models import Order

class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request, file_id):
        file = get_object_or_404(UploadedFile, pk=file_id)
        order, created = Order.objects.get_or_create(user=request.user, file=file)
        return redirect('orders:order-list')

class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).select_related('file')
        return render(request, 'orders/order_list.html', {'orders': orders})
