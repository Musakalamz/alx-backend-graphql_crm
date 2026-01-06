from celery import shared_task
import requests
from datetime import datetime

@shared_task
def generate_crm_report():
    url = 'http://localhost:8000/graphql'
    query = """
    query {
        allCustomers {
            edges {
                node {
                    id
                }
            }
        }
        allOrders {
            edges {
                node {
                    totalAmount
                }
            }
        }
    }
    ""
    
    try:
        response = requests.post(url, json={'query': query})
        result = response.json()
        
        if 'errors' in result:
            return
            
        data = result.get('data', {})
        customers = data.get('allCustomers', {}).get('edges', [])
        orders = data.get('allOrders', {}).get('edges', [])
        
        customer_count = len(customers)
        order_count = len(orders)
        total_revenue = sum(float(edge['node']['totalAmount']) for edge in orders if edge['node']['totalAmount'])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - Report: {customer_count} customers, {order_count} orders, {total_revenue} revenue\n"
        
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(log_message)
            
    except Exception:
        pass