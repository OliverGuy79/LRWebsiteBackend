"""Boutique API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.models.boutique import Product, ProductListResponse
from app.services import sheets_service


router = APIRouter()


@router.get("", response_model=ProductListResponse)
async def list_products(
    category: str | None = Query(None, description="Filter by category"),
    in_stock: bool | None = Query(None, description="Filter by stock status"),
):
    """List all products."""
    data = await sheets_service.get_boutique()
    
    # Filter by category if provided
    if category:
        data = [p for p in data if p.get("category", "").lower() == category.lower()]
    
    # Filter by stock status if provided
    if in_stock is not None:
        stock_value = "TRUE" if in_stock else "FALSE"
        data = [p for p in data if p.get("is_in_stock", "").upper() == stock_value]
    
    # Filter to only show active products
    data = [p for p in data if p.get("status", "").lower() == "active"]
    
    products = [Product(**product) for product in data]
    return ProductListResponse(products=products, total=len(products))


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a single product by ID."""
    data = await sheets_service.get_boutique()
    
    product_data = next((p for p in data if p.get("id") == product_id), None)
    
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(**product_data)
