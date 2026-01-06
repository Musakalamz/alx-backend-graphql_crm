#!/bin/bash
cd "$(dirname "$0")/../../"
python3 manage.py shell <<EOF
from crm.models import Customer, Order
from django.utils import timezone
from datetime import timedelta
import sys

# Calculate the threshold date (1 year ago)
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers who have placed orders in the last year
active_customer_ids = Order.objects.filter(order_date__gt=one_year_ago).values_list('customer_id', flat=True).distinct()

# Identify inactive customers
inactive_customers = Customer.objects.exclude(id__in=active_customer_ids)

count = inactive_customers.count()
if count > 0:
    inactive_customers.delete()

# Log the result
timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
log_message = f"{timestamp} - Deleted {count} inactive customers\n"

try:
    with open('/tmp/customer_cleanup_log.txt', 'a') as f:
        f.write(log_message)
except:
    pass
EOF