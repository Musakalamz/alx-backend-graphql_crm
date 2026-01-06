import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Log file path
LOG_FILE = '/tmp/order_reminders_log.txt'

def main():
    # Setup GraphQL client
    # Assuming the server is running on localhost:8000
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        verify=False,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Calculate date 7 days ago for filtering
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

    # Define the query with filter
    query = gql("""
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
    """)

    # Filter for orders in the last 7 days (pending orders)
    params = {
        "filter": {
            "orderDateGte": seven_days_ago
        }
    }

    try:
        # Execute query
        result = client.execute(query, variable_values=params)
        edges = result.get('allOrders', {}).get('edges', [])
        
        # Log reminders
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