from django_filters import FilterSet, CharFilter, NumberFilter, IsoDateTimeFilter
from .models import Customer, Product, Order


class CustomerFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    email = CharFilter(field_name='email', lookup_expr='icontains')
    created_at__gte = IsoDateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = IsoDateTimeFilter(field_name='created_at', lookup_expr='lte')
    phone_pattern = CharFilter(method='filter_phone_pattern')

    def filter_phone_pattern(self, queryset, name, value):
        return queryset.filter(phone__istartswith=value)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at', 'phone']


class ProductFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    price__gte = NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = NumberFilter(field_name='price', lookup_expr='lte')
    stock__gte = NumberFilter(field_name='stock', lookup_expr='gte')
    stock__lte = NumberFilter(field_name='stock', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']


class OrderFilter(FilterSet):
    total_amount__gte = NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount__lte = NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date__gte = IsoDateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date__lte = IsoDateTimeFilter(field_name='order_date', lookup_expr='lte')
    customer_name = CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = CharFilter(field_name='products__name', lookup_expr='icontains')
    product_id = NumberFilter(method='filter_product_id')

    def filter_product_id(self, queryset, name, value):
        return queryset.filter(products__id=value)

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date', 'customer', 'products']
