# Petstore API

**Version:** 1.0.0

A sample API for managing pets in a store.

**Servers**

- `https://api.petstore.example.com/v1` — Production

## Authentication

| Scheme | Type | Details |
| --- | --- | --- |
| apiKey | apiKey | header: X-API-Key |

## Pets

Everything about pets

### GET /pets

List pets

**Parameters**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| limit | query | integer (int32) | no | Maximum number of pets to return |

**Responses**

| Status | Description | Schema |
| --- | --- | --- |
| 200 | A list of pets | array of [Pet](#pet) |

### POST /pets

Create a pet

**Security:** apiKey

**Request body** (`application/json`) (required): [NewPet](#newpet)

Pet to add to the store

**Example**

```json
{
  "name": "Rex",
  "tag": "dog"
}
```

**Responses**

| Status | Description | Schema |
| --- | --- | --- |
| 201 | Pet created | [Pet](#pet) |
| 400 | Invalid input | — |

### GET /pets/{petId}

Get a pet by id

**Parameters**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| petId | path | integer (int64) | yes | The id of the pet |

**Responses**

| Status | Description | Schema |
| --- | --- | --- |
| 200 | A single pet | [Pet](#pet) |
| 404 | Pet not found | [Error](#error) |

**Example · 200**

```json
{
  "id": 42,
  "name": "Rex",
  "tag": "dog",
  "status": "available"
}
```

## Store

Store inventory operations

### GET /store/inventory

Inventory by status

**Responses**

| Status | Description | Schema |
| --- | --- | --- |
| 200 | A map of status to quantity | object |

## Schemas

### Error

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| code | integer (int32) | yes |  |
| message | string | yes |  |

### NewPet

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | yes |  |
| tag | string | no |  |

### Pet

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| id | integer (int64) | yes | Unique id |
| name | string | yes | The pet's name |
| tag | string | no |  |
| status | string | no | Pet status \| lifecycle |
