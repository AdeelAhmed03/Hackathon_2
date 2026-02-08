# API Contract: GET /api/tasks

## Query Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `q` | `string` | No | - | Case-insensitive search on title/description. |
| `priority` | `string[]` | No | - | Filter by one or more: `low`, `medium`, `high`. |
| `tags` | `string[]` | No | - | Filter by one or more tag names (AND logic). |
| `status` | `string` | No | - | `completed` or `pending`. |
| `sort_by` | `string` | No | `created_at` | `created_at`, `due_date`, `priority`, `title`. |
| `order` | `string` | No | `desc` | `asc` or `desc`. |

## Response

Returns the same standard task objects, filtered and ordered according to the query.

### Example Request
`GET /api/tasks?q=grocery&priority=high&sort_by=due_date&order=asc`

### Example Response
```json
[
  {
    "id": "uuid-1",
    "title": "Buy grocery items",
    "description": "Milk, Eggs, Bread",
    "priority": "high",
    "status": false,
    "due_date": "2026-01-20T10:00:00Z",
    "tags": ["personal", "urgent"],
    "created_at": "2026-01-14T12:00:00Z"
  }
]
```
