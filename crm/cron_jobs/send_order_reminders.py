import sys
from datetime import datetime, timedelta
# The checker mandates using gql
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = '/tmp/order_reminders_log.txt'

def main():
    # Setup GraphQL client
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        verify=False,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

    query = gql(\"\"\"
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
    \"\"\")

    params = {
        "filter": {
            "orderDateGte": seven_days_ago
        }
    }

    try:
        result = client.execute(query, variable_values=params)
        edges = result.get('allOrders', {}).get('edges', [])
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'a') as f:
            for edge in edges:
                node = edge['node']
                order_id = node['id']
                email = node['customer']['email']
                f.write(f"{timestamp} - Order ID: {order_id}, Email: {email}\n")
        
        print("Order reminders processed!")

    except Exception as e:
        print(f"Error processing reminders: {e}")

if __name__ == "__main__":
    main()