import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP, Context
from pymongo import MongoClient
from pymongo.database import Database
from bson import json_util
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "mcp-server-demo")


@dataclass
class AppContext:
    """Application context with MongoDB client and database."""

    client: MongoClient
    db: Database


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage MongoDB connection lifecycle."""
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    try:
        yield AppContext(client=client, db=db)
    finally:
        client.close()
        # Force close all connections
        client._topology.close()


# Create MCP server with MongoDB integration
mcp = FastMCP(
    "MongoDB Tools",
    description="MCP server providing MongoDB query and management tools",
    lifespan=app_lifespan,
)


@mcp.tool()
def list_collections(ctx: Context) -> List[str]:
    """List all collections in the database."""
    db = ctx.request_context.lifespan_context.db
    return db.list_collection_names()


@mcp.tool()
def query_collection(
    ctx: Context,
    collection: str,
    query: Dict[str, Any],
    projection: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    skip: int = 0,
    sort: Optional[Dict[str, int]] = None,
) -> str:
    """
    Query documents from a MongoDB collection.

    Args:
        collection: Name of the collection to query
        query: MongoDB query filter
        projection: Fields to include/exclude in the results
        limit: Maximum number of documents to return
        skip: Number of documents to skip
        sort: Dictionary of field names and sort directions (1 for ascending, -1 for descending)
    """
    db = ctx.request_context.lifespan_context.db

    try:
        cursor = db[collection].find(
            filter=query,
            projection=projection,
        )

        if sort:
            cursor = cursor.sort(list(sort.items()))

        cursor = cursor.skip(skip).limit(limit)
        results = list(cursor)

        # Convert MongoDB objects to JSON-serializable format
        return json.dumps(results, default=json_util.default)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def count_documents(ctx: Context, collection: str, query: Dict[str, Any]) -> int:
    """
    Count documents in a collection that match the query.

    Args:
        collection: Name of the collection
        query: MongoDB query filter
    """
    db = ctx.request_context.lifespan_context.db
    return db[collection].count_documents(query)


@mcp.tool()
def get_collection_stats(ctx: Context, collection: str) -> str:
    """
    Get statistics about a collection.

    Args:
        collection: Name of the collection
    """
    db = ctx.request_context.lifespan_context.db
    try:
        stats = db.command("collStats", collection)
        return json.dumps(stats, default=json_util.default)
    except Exception as e:
        return json.dumps({"error": str(e)})


# @mcp.resource("collections://list")
# async def get_collections_resource(ctx: Context) -> str:
#     """Resource that lists all collections in the database."""
#     db = ctx.request_context.lifespan_context.db
#     collections = db.list_collection_names()
#     return json.dumps({"database": MONGODB_DATABASE, "collections": collections})


# @mcp.resource("collection://{name}/info")
# async def get_collection_info(ctx: Context, name: str) -> str:
#     """Resource that provides information about a specific collection."""
#     db = ctx.request_context.lifespan_context.db
#     try:
#         stats = db.command("collStats", name)
#         return json.dumps(stats, default=json_util.default)
#     except Exception as e:
#         return json.dumps({"error": str(e)})


def main():
    """Start the MCP server."""
    print(f"Starting MongoDB MCP server...")
    print(f"MongoDB URI: {MONGODB_URI}")
    print(f"Database: {MONGODB_DATABASE}")

    import uvicorn

    app = mcp.sse_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
