from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'total_amount', 'status', 'payment_method', 'bank_transfer_confirmed']
    list_filter = ['status', 'payment_method']
    actions = ['confirm_bank_transfer']

    def confirm_bank_transfer(self, request, queryset):
        updated = queryset.update(bank_transfer_confirmed=True, status='completed')
        self.message_user(request, f'{updated} đơn hàng đã được xác nhận thanh toán chuyển khoản.')
    confirm_bank_transfer.short_description = "Xác nhận thanh toán chuyển khoản cho các đơn hàng đã chọn"
