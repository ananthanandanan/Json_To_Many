# Library API

**Version:** 0.9.0

Books and authors, with circular references between them.

## Authentication

| Scheme | Type | Details |
| --- | --- | --- |
| oauth2 | oauth2 | flows: authorizationCode |
| bearerAuth | http | bearer (JWT) |

## Books

### GET /books/{isbn}

Get a book

**Security:** oauth2, bearerAuth

**Parameters**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| isbn | path | string | yes |  |

**Responses**

| Status | Description | Schema |
| --- | --- | --- |
| 200 | A book | [Book](#book) |

## Schemas

### Book

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| isbn | string | yes |  |
| title | string | yes |  |
| author | [Author](#author) | no |  |

### Author

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | no |  |
| books | array of [Book](#book) | no |  |
