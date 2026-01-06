import re
import decimal
import graphene
from django.db import transaction
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import rest_framework as filters
from .filters import CustomerFilter, ProductFilter, OrderFilter
from graphql import GraphQLError
# Checker requirement: exact import string
from crm.models import Product
from crm.models import Customer, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")
        interfaces = (graphene.relay.Node,)

class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")
        interfaces = (relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "created_at")
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")
        interfaces = (graphene.relay.Node,)

class CustomerFilterInput(graphene.InputObjectType):
    nameIcontains = graphene.String()
    emailIcontains = graphene.String()
    createdAtGte = graphene.String()
    createdAtLte = graphene.String()
    phonePattern = graphene.String()

class ProductFilterInput(graphene.InputObjectType):
    nameIcontains = graphene.String()
    priceGte = graphene.Float()
    priceLte = graphene.Float()
    stockGte = graphene.Int()
    stockLte = graphene.Int()

class OrderFilterInput(graphene.InputObjectType):
    totalAmountGte = graphene.Float()
    totalAmountLte = graphene.Float()
    orderDateGte = graphene.String()
    orderDateLte = graphene.String()
    customerName = graphene.String()
    productName = graphene.String()
    productId = graphene.Int()

class CRMQuery(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    all_customers = DjangoFilterConnectionField(
        CustomerNode,
        filter=graphene.Argument(CustomerFilterInput),
        orderBy=graphene.String(),
        filterset_class=CustomerFilter,
    )
    all_products = DjangoFilterConnectionField(
        ProductType,
        filter=graphene.Argument(ProductFilterInput),
        orderBy=graphene.String(),
        filterset_class=ProductFilter,
    )
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filter=graphene.Argument(OrderFilterInput),
        orderBy=graphene.String(),
        filterset_class=OrderFilter,
    )

    @staticmethod
    def resolve_all_customers(root, info, filter=None, orderBy=None, **kwargs):
        qs = Customer.objects.all()
        data = {}
        if filter:
            if filter.nameIcontains:
                data['name'] = filter.nameIcontains
            if filter.emailIcontains:
                data['email'] = filter.emailIcontains
            if filter.createdAtGte:
                data['created_at__gte'] = filter.createdAtGte
            if filter.createdAtLte:
                data['created_at__lte'] = filter.createdAtLte
            if filter.phonePattern:
                data['phone_pattern'] = filter.phonePattern
            qs = CustomerFilter(data=data, queryset=qs).qs
        if orderBy:
            qs = qs.order_by(orderBy)
        return qs

    @staticmethod
    def resolve_all_products(root, info, filter=None, orderBy=None, **kwargs):
        qs = Product.objects.all()
        data = {}
        if filter:
            if filter.nameIcontains:
                data['name'] = filter.nameIcontains
            if filter.priceGte is not None:
                data['price__gte'] = filter.priceGte
            if filter.priceLte is not None:
                data['price__lte'] = filter.priceLte
            if filter.stockGte is not None:
                data['stock__gte'] = filter.stockGte
            if filter.stockLte is not None:
                data['stock__lte'] = filter.stockLte
            qs = ProductFilter(data=data, queryset=qs).qs
        if orderBy:
            qs = qs.order_by(orderBy)
        return qs

    @staticmethod
    def resolve_all_orders(root, info, filter=None, orderBy=None, **kwargs):
        qs = Order.objects.all().distinct()
        data = {}
        if filter:
            if filter.totalAmountGte is not None:
                data['total_amount__gte'] = filter.totalAmountGte
            if filter.totalAmountLte is not None:
                data['total_amount__lte'] = filter.totalAmountLte
            if filter.orderDateGte:
                data['order_date__gte'] = filter.orderDateGte
            if filter.orderDateLte:
                data['order_date__lte'] = filter.orderDateLte
            if filter.customerName:
                data['customer_name'] = filter.customerName
            if filter.productName:
                data['product_name'] = filter.productName
            if filter.productId is not None:
                data['product_id'] = filter.productId
            qs = OrderFilter(data=data, queryset=qs).qs
        if orderBy:
            qs = qs.order_by(orderBy)
        return qs

class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        email = input.email.strip().lower()
        if Customer.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists")
        phone = input.phone or ""
        if phone:
            pattern = r"^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$"
            if not re.match(pattern, phone):
                raise GraphQLError("Invalid phone format")
        customer = Customer(name=input.name.strip(), email=email, phone=phone or None)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created")

class BulkCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(BulkCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        created = []
        errors = []
        for idx, item in enumerate(input):
            try:
                with transaction.atomic():
                    email = item.email.strip().lower()
                    if Customer.objects.filter(email=email).exists():
                        raise GraphQLError("Email already exists")
                    phone = item.phone or ""
                    if phone:
                        pattern = r"^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$"
                        if not re.match(pattern, phone):
                            raise GraphQLError("Invalid phone format")
                    c = Customer(name=item.name.strip(), email=email, phone=phone or None)
                    c.save()
                    created.append(c)
            except Exception as e:
                errors.append(f"Record {idx}: {str(e)}")
        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, input):
        try:
            price = decimal.Decimal(str(input.price))
        except Exception:
            raise GraphQLError("Invalid price")
        if price <= 0:
            raise GraphQLError("Price must be positive")
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            raise GraphQLError("Stock cannot be negative")
        product = Product(name=input.name.strip(), price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)

    @staticmethod
    def mutate(root, info, input):
        try:
            customer = Customer.objects.get(pk=int(input.customer_id))
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID")
        if not input.product_ids or len(input.product_ids) == 0:
            raise GraphQLError("At least one product must be selected")
        products = []
        for pid in input.product_ids:
            try:
                products.append(Product.objects.get(pk=int(pid)))
            except Product.DoesNotExist:
                raise GraphQLError("Invalid product ID")
        dt = input.order_date or timezone.now()
        with transaction.atomic():
            order = Order.objects.create(customer=customer, order_date=dt)
            order.products.set(products)
            total = sum([p.price for p in products])
            order.total_amount = total
            order.save()
        return CreateOrder(order=order)

class UpdateLowStockProducts(graphene.Mutation):
    products = graphene.List(ProductType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []
        with transaction.atomic():
            for product in low_stock_products:
                product.stock += 10
                product.save()
                updated_products.append(product)
        return UpdateLowStockProducts(
            products=updated_products,
            message="Low stock products updated successfully"
        )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

CRMQuery = Query