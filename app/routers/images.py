"""Image proxy API endpoints."""

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

router = APIRouter()

# Cache pour les images (en mémoire, simple)
_image_cache: dict[str, tuple[bytes, str]] = {}


@router.get("/google-drive/{file_id}")
async def proxy_google_drive_image(file_id: str, size: int = 1000):
    """
    Proxy Google Drive images to avoid CORS issues.

    Args:
        file_id: Google Drive file ID
        size: Image width (default: 1000)
    """
    cache_key = f"{file_id}_{size}"

    # Check cache
    if cache_key in _image_cache:
        image_data, content_type = _image_cache[cache_key]
        return Response(
            content=image_data,
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=86400"}
        )

    # Fetch from Google
    url = f"https://lh3.googleusercontent.com/d/{file_id}=w{size}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=15.0, follow_redirects=True)

            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Image not found")

            image_data = response.content
            content_type = response.headers.get("content-type", "image/jpeg")

            # Cache the result
            _image_cache[cache_key] = (image_data, content_type)

            return Response(
                content=image_data,
                media_type=content_type,
                headers={"Cache-Control": "public, max-age=86400"}
            )

    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch image: {str(e)}")