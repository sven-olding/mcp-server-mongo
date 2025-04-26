# MCP Server with MongoDB Integration

This is an MCP server that provides tools for querying MongoDB data.

## Setup

1. Install dependencies using uv:
```bash
uv pip install -e .
```

2. Configure MongoDB connection:
   - The server will connect to MongoDB at `mongodb://localhost:27017` by default
   - You can change the connection details by setting environment variables:
     - `MONGODB_URI`: MongoDB connection string
     - `MONGODB_DATABASE`: Database name

## Running the Server

```bash
python main.py
```

## Available Tools

### 1. query_mongodb
Query a MongoDB collection with a filter.

Parameters:
- `collection` (string): Name of the collection to query
- `query` (object): MongoDB query filter
- `limit` (integer, optional): Maximum number of results to return (default: 10)

Example:
```python
{
    "collection": "users",
    "query": {"age": {"$gt": 18}},
    "limit": 5
}
```

### 2. list_collections
List all collections in the database.

No parameters required.

## Development

To add new dependencies:
```bash
uv pip install <package-name>
```

To update dependencies:
```bash
uv pip install --upgrade <package-name>
```
