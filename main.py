# main.py
from fastapi import FastAPI

# Create a FastAPI instance - this is the core of your application
app = FastAPI(
    title="My First FastAPI App",
    description="A simple API built with FastAPI",
    version="0.1.0"
)

# Define a route using a decorator
# The @app.get("/") decorator tells FastAPI that the function below handles GET requests to the root path "/"
@app.get("/")
async def root():
    """
    Root endpoint that returns a simple greeting message
    Returns a JSON object with a welcome message
    """
    return {"message": "Hello World from FastAPI!"}

# Define another route with a path parameter
# Path parameters are variables in the path that are captured and passed to the function
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """
    Endpoint that returns information about a specific item

    Args:
        item_id (int): The ID of the item to retrieve

    Returns:
        JSON object with the item ID and a message
    """
    return {"item_id": item_id, "message": f"You requested item {item_id}"}

# Define a route with query parameters
# Query parameters are optional and are specified after the ? in the URL
@app.get("/search/")
async def search_items(q: str = None, skip: int = 0, limit: int = 10):
    """
    Endpoint that searches for items based on query parameters

    Args:
        q (str, optional): Search query
        skip (int, optional): Number of items to skip
        limit (int, optional): Maximum number of items to return

    Returns:
        JSON object with the search parameters and results
    """
    return {
        "query": q,
        "skip": skip,
        "limit": limit,
        "message": f"Searching for '{q}' (skipping {skip}, limiting to {limit})"
    }

# To run this app, use the command:
# uvicorn main:app --reload
#
# Then you can access:
# - http://127.0.0.1:8000/ for the root endpoint
# - http://127.0.0.1:8000/items/42 to get information about item 42
# - http://127.0.0.1:8000/search?q=test to search for "test"
# - http://127.0.0.1:8000/docs for the automatic interactive API documentation

# Project structure
#
# my_fastapi_app/
# ├── app/
# │   ├── __init__.py
# │   ├── main.py          # FastAPI application creation and configuration
# │   ├── models/          # Pydantic models for request/response
# │   │   ├── __init__.py
# │   │   └── item.py      # Item data models
# │   ├── routes/          # API route handlers
# │   │   ├── __init__.py
# │   │   └── items.py     # Item-related endpoints
# │   └── utils/           # Utility functions and helpers
# │       ├── __init__.py
# │       └── exceptions.py # Custom exception handlers
# └── requirements.txt     # Project dependencies

# app/models/item.py
from pydantic import BaseModel, Field
from typing import Optional, List

class ItemBase(BaseModel):
    """Base model for item data"""
    name: str = Field(..., min_length=1, max_length=100, description="The name of the item")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    price: float = Field(..., gt=0, description="Price must be greater than zero")
    tags: List[str] = Field(default=[], description="List of tags for the item")

class ItemCreate(ItemBase):
    """Model for creating a new item"""
    pass

class ItemResponse(ItemBase):
    """Model for item responses that includes the ID"""
    id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Laptop",
                "description": "Powerful development machine",
                "price": 1299.99,
                "tags": ["electronics", "computers"]
            }
        }

# app/utils/exceptions.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class ItemNotFoundError(Exception):
    """Raised when an item is not found"""
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.message = f"Item with ID {item_id} not found"
        super().__init__(self.message)

def add_exception_handlers(app: FastAPI) -> None:
    """Add custom exception handlers to the FastAPI application"""

    @app.exception_handler(ItemNotFoundError)
    async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error in request data",
                "errors": exc.errors()
            }
        )

# app/routes/items.py
from fastapi import APIRouter, Path, Query, HTTPException, status
from typing import List, Optional

from ..models.item import ItemCreate, ItemResponse
from ..utils.exceptions import ItemNotFoundError

router = APIRouter(prefix="/items", tags=["items"])

# Mock database (in a real app, this would be a database)
fake_items_db = {}
item_counter = 0

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item"""
    global item_counter
    item_counter += 1

    # Create new item with ID
    item_dict = item.dict()
    new_item = {**item_dict, "id": item_counter}

    # Store in our fake database
    fake_items_db[item_counter] = new_item

    return new_item

@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int = Path(..., gt=0, description="The ID of the item to retrieve")
):
    """Get a specific item by ID"""
    if item_id not in fake_items_db:
        raise ItemNotFoundError(item_id)

    return fake_items_db[item_id]

@router.get("/", response_model=List[ItemResponse])
async def list_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items to return"),
    tag: Optional[str] = Query(None, description="Filter items by tag")
):
    """List items with optional filtering and pagination"""
    items = list(fake_items_db.values())

    # Filter by tag if provided
    if tag:
        items = [item for item in items if tag in item.get("tags", [])]

    # Apply pagination
    return items[skip:skip+limit]

# app/main.py
from fastapi import FastAPI
from .routes import items
from .utils.exceptions import add_exception_handlers

# Create FastAPI application
app = FastAPI(
    title="Enhanced FastAPI Example",
    description="A more structured FastAPI application with proper models and error handling",
    version="0.2.0"
)

# Add routes
app.include_router(items.router)

# Configure exception handlers
add_exception_handlers(app)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to the enhanced FastAPI example",
        "docs": "/docs",
        "endpoints": {
            "items": "/items"
        }
    }

# To run: uvicorn app.main:app --reload