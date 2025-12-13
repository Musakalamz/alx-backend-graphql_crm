# ALX Backend GraphQL CRM

## Overview

ALX Backend GraphQL CRM is a Django-based backend that introduces GraphQL fundamentals through a practical, production-style setup. It demonstrates how to design a clean GraphQL schema, expose a single `/graphql` endpoint, and integrate Django models and resolvers using `graphene-django`. The project emphasizes correctness, security, and performance, making it a strong foundation for real-world GraphQL APIs.

## Learning Objectives

- Explain GraphQL and how it differs from REST.
- Describe core schema elements: types, queries, and mutations.
- Set up GraphQL in Django using `graphene-django`.
- Build queries and mutations to fetch and manipulate data.
- Use GraphiQL or API clients (Insomnia/Postman) against the GraphQL endpoint.
- Apply best practices for scalable and secure GraphQL APIs.

## Key Concepts

- **GraphQL vs REST**: One flexible endpoint vs multiple fixed endpoints.
- **Schema**: Formal contract with Types, Queries, Mutations.
- **Resolvers**: Functions that resolve fields from data sources.
- **Graphene-Django**: Bridges Django ORM and GraphQL.

## Best Practices

- **Schema Design**: Keep types modular, naming clear, and fields purposeful.
- **Security**: Enforce authZ/authN in resolvers; avoid overexposing data.
- **Error Handling**: Surface actionable, friendly errors.
- **Pagination**: Use cursor/offset pagination for large lists.
- **N+1 Problem**: Optimize with `select_related`, `prefetch_related`, or `graphene-django-optimizer`.
- **Testing**: Unit test queries/mutations for reliability.
- **Documentation**: Enable GraphiQL for discoverability during development.

## Repository Structure

After initialization, the repository will contain:

- `manage.py` – Django management entrypoint
- `alx_backend_graphql_crm/` – Django project package (`settings.py`, `urls.py`)
- `crm/` – Main Django app (future models, schema integrations)
- `README.md` – Project documentation

## Setup

1) Create and activate a Python environment (optional but recommended).

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies.

```bash
pip install django graphene-django django-filter
```

3) Initialize the Django project and app.

```bash
# From the repository root
python -m django startproject alx_backend_graphql_crm .
python manage.py startapp crm
```

4) Configure GraphQL.

- Add `graphene_django` and `crm` to `INSTALLED_APPS` in `alx_backend_graphql_crm/settings.py`.
- Create `alx_backend_graphql_crm/schema.py` with a basic `Query` and `schema`.
- Add the GraphQL endpoint to `alx_backend_graphql_crm/urls.py`.

## Hello Query (Checkpoint)

With the initial schema, visiting `http://localhost:8000/graphql` and running:

```graphql
{
  hello
}
```

Returns:

```json
{
  "data": {
    "hello": "Hello, GraphQL!"
  }
}
```

## Running Locally

```bash
python manage.py runserver
# Open http://localhost:8000/graphql (GraphiQL enabled)
```

To test programmatically:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"{ hello }"}' \
  http://localhost:8000/graphql
```

## Next Steps

- Add Django models and expose them via GraphQL types.
- Implement mutations for create/update/delete flows.
- Add authentication/authorization to resolvers.
- Optimize data access and add pagination.
- Write unit tests for queries and mutations.

## License

This repository is intended for educational use within the ALX ecosystem. Adapt and extend for your own projects as needed.

