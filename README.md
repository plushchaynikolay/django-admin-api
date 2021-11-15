# Django admin api

Most important thing in this repository - [AbstractQueryset](django_admin_api/query/base.py#L60). Provides two default API approaches: JSON and REST.

## JSON API

Sending JSON body in POST request, with `action` property.

Example:
<details>

1. Count

Request
```json
{
    "action": "count",
    "filters": {
        "id": {
            "in": [1, 2]
        },
        "name": {
            "e": "test"
        }
    },
    "order_by": ["id"]
}
```

Response:
```json
{
    "count": 1
}
```
2 List

Request:
```json
{
    "action": "list",
    "filters": {
        "id": {
            "in": [1, 2]
        },
        "name": {
            "exact": "test"
        }
    },
    "order_by": ["id"],
    "limit": 1,
    "offset": 0
}
```

Response:
```json
{
    "data": [
        {
            "id": 1,
            "name": "test",
            "volume": 5.0
        }
    ]
}
```

1. Create

Request:
```json
{
    "action": "create",
    "data": [
        {
            "name": "test 2",
            "volume": 15.0
        }
    ]
}
```

Response:
```json
{
    "data": [
        {
            "id": 2,
            "name": "test 2",
            "volume": 15.0
        }
    ]
}
```

1. Update

Request:
```json
{
    "action": "update",
    "filters": {
        "id": {
            "in": [1, 2]
        },
        "name": {
            "e": "test"
        }
    },
    "update": {
        "volume": 0.0
    }
}
```

Response:
```json
{
    "count": 2
}
```

1. Delete
```json
{
    "action": "delete",
    "filters": {
        "id": {
            "in": [1, 2]
        },
        "name": {
            "e": "test"
        }
    }
}
```

Response:
```json
{
    "count": 1
}
```
</details>

## REST API


Example:
<details>

1. Count

Request:
```
GET /products/count/?id__in=1,2&name=test&order_by=id
```

Response:
```json
{
    "count": 1
}
```
2. List

Request:
```
GET /products/?id__in=1&id__in=2&name=test&order_by=id&limit=1&offset=0
```

Response:
```json
{
    "data": [
        {
            "id": 1,
            "name": "test",
            "volume": 5.0
        }
    ]
}
```

3. Create

Request:
```
POST /products/

{
    "data": [
        {
            "name": "test 2",
            "volume": 15.0
        }
    ]
}
```

Response:
```json
{
    "data": [
        {
            "id": 2,
            "name": "test 2",
            "volume": 15.0
        }
    ]
}
```

4. Update

Request:
```
PATCH /products/?id__in=1&id__in=2&name=test

{
    "data": {
        "volume": 0.0
    }
}
```

Response:
```json
{
    "count": 2
}
```

5. Delete

```
DELETE /products/?id__in=1&id__in=2&name=test
```

Response:
```json
{
    "count": 1
}
```
</details>

## TODO

- [ ] Swagger generation.
- [ ] One-to-Many relation support.
- [ ] Many-to-Many relation support.

Dev
- [ ] Configure development environment to enable example project running.
- [ ] Configure building and deploying to PyPI.
- [ ] Tests.
