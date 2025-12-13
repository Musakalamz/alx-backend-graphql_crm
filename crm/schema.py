import re
import decimal
import graphene
from django.db import transaction
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from .models import Customer, Product, Order


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


class CRMQuery(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    all_customers = graphene.List(CustomerType)

    @staticmethod
    def resolve_all_customers(root, info):
        return Customer.objects.all()


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


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# Backward alias to satisfy imports expecting CRMQuery
CRMQuery = Query
