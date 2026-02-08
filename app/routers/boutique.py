"""Boutique API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.models.boutique import Product, ProductListResponse
from app.services import sheets_service


router = APIRouter()


@router.get("", response_model=ProductListResponse)
async def list_products(
    category: str | None = Query(None, description="Filter by category"),
    in_stock: bool | None = Query(None, description="Filter by stock status"),
    preview: bool = Query(False, description="Include draft content for preview"),
):
    """List all published products."""
    data = await sheets_service.get_boutique()
    
    # Filter by status
    if preview:
        # Show published and draft (not archived)
        data = [p for p in data if p.get("status", "").lower() in ("published", "draft")]
    else:
        # Only show published
        data = [p for p in data if p.get("status", "").lower() == "published"]
    
    # Filter by category if provided
    if category:
        data = [p for p in data if p.get("category", "").lower() == category.lower()]
    
    # Filter by stock status if provided
    if in_stock is not None:
        stock_value = "TRUE" if in_stock else "FALSE"
        data = [p for p in data if p.get("is_in_stock", "").upper() == stock_value]
    
    products = [Product(**product) for product in data]
    return ProductListResponse(products=products, total=len(products))


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    preview: bool = Query(False, description="Allow viewing draft products"),
):
    """Get a single product by ID."""
    data = await sheets_service.get_boutique()
    
    product_data = next((p for p in data if p.get("id") == product_id), None)
    
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check status - only allow published unless preview mode
    status = product_data.get("status", "").lower()
    if not preview and status != "published":
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(**product_data)
