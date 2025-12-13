import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order


def run():
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    alice = Customer.objects.create(name='Alice', email='alice@example.com', phone='+1234567890')
    bob = Customer.objects.create(name='Bob', email='bob@example.com', phone='123-456-7890')
    carol = Customer.objects.create(name='Carol', email='carol@example.com')

    laptop = Product.objects.create(name='Laptop', price=Decimal('999.99'), stock=10)
    mouse = Product.objects.create(name='Mouse', price=Decimal('29.99'), stock=100)
    keyboard = Product.objects.create(name='Keyboard', price=Decimal('49.99'), stock=50)

    order1 = Order.objects.create(customer=alice)
    order1.products.set([laptop, mouse])
    order1.total_amount = laptop.price + mouse.price
    order1.save()

    order2 = Order.objects.create(customer=bob)
    order2.products.set([keyboard])
    order2.total_amount = keyboard.price
    order2.save()

    print('Seed complete')


if __name__ == '__main__':
    run()

