import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

LOG_FILE = '/tmp/order_reminders_log.txt'
GRAPHQL_URL = 'http://localhost:8000/graphql'

def main():
    query = """
    query GetPendingOrders($filter: OrderFilterInput) {
        allOrders(filter: $filter) {
            edges {
                node {
                    id
                    orderDate
                    customer {
                        email
                    }
                }
            }
        }
    }
    ""

    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')

    variables = {
        "filter": {
            "orderDateGte": seven_days_ago
        }
    }

    payload = json.dumps({"query": query, "variables": variables}).encode('utf-8')
    req = urllib.request.Request(
        GRAPHQL_URL, 
        data=payload, 
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            result = json.loads(response_body)

            if 'errors' in result:
                print(f"GraphQL Errors: {result['errors']}")
                return

            orders = result.get('data', {}).get('allOrders', {}).get('edges', [])
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                with open(LOG_FILE, 'a') as f:
                    for edge in orders:
                        node = edge['node']
                        order_id = node['id']
                        customer = node.get('customer') or {}
                        email = customer.get('email', 'Unknown Email')
                        f.write(f"{timestamp} - Order ID: {order_id}, Email: {email}\n")
            except:
                pass
            
            print("Order reminders processed!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()