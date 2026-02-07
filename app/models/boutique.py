"""Pydantic models for Boutique products."""

from pydantic import BaseModel


class Product(BaseModel):
    """Church merchandise product."""
    id: str
    name: str
    description: str | None = None
    short_description: str | None = None
    category: str | None = None
    price: str | None = None
    sale_price: str | None = None
    currency: str = "EUR"
    is_in_stock: str | None = None
    dimensions: str | None = None
    images: str | None = None
    tags: str | None = None
    status: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ProductListResponse(BaseModel):
    """Response for listing products."""
    products: list[Product]
    total: int
