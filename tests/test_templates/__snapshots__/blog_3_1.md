# Blog API

**Version:** 2.3.0

A minimal blog API demonstrating OpenAPI 3.1 features.

## Posts

Blog post operations

### GET /posts

List posts

**Responses**

| Status | Description | Schema |
| --- | --- | --- |
| 200 | Posts | array of [Post](#post) |

## Other

### GET /health

Liveness probe

**Responses**

| Status | Description | Schema |
| --- | --- | --- |
| 200 | Service healthy | object |

**Example · 200**

```json
{
  "status": "ok"
}
```

## Schemas

### Post

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| id | integer | yes |  |
| title | string | yes |  |
| subtitle | string (nullable) | no | Optional subtitle |
| author | [Author](#author) | no |  |
| rating | integer or number | no |  |

### Author

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | no |  |
| email | string (email) | no |  |
