from datetime import datetime
from crm.schema import UpdateLowStockProducts
from alx_backend_graphql_crm.schema import schema

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"
    
    try:
        result = schema.execute('{ hello }')
        if not result.errors:
            message = f"{timestamp} CRM is alive (GraphQL Responsive)\n"
    except:
        pass

    try:
        with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
            f.write(message)
    except:
        pass

def update_low_stock():
    mutation = """
    mutation {
        updateLowStockProducts {
            products {
                name
                stock
            }
            message
        }
    }
    ""
    
    try:
        result = schema.execute(mutation)
        
        if result.errors:
            return

        data = result.data.get('updateLowStockProducts', {})
        products = data.get('products', [])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            if products:
                for product in products:
                    log_entry = f"{timestamp} - Updated {product['name']} to stock {product['stock']}\n"
                    f.write(log_entry)
            else:
                pass
    except:
        pass