"""Art Institute of Chicago API client with caching."""

import logging

import httpx
from cachetools import TTLCache

from app.config import settings
from app.exceptions import BadRequestException, ExternalAPIException

logger = logging.getLogger(__name__)

# In-memory cache for artwork lookups
_artwork_cache: TTLCache = TTLCache(
    maxsize=settings.CACHE_MAX_SIZE,
    ttl=settings.CACHE_TTL,
)


class ArticAPIClient:
    """Client for the Art Institute of Chicago API.

    Provides methods to fetch and validate artworks.
    Includes in-memory TTL caching to reduce external API calls.
    """

    BASE_URL = settings.ARTIC_API_BASE_URL
    TIMEOUT = settings.ARTIC_API_TIMEOUT

    @classmethod
    def _get_client(cls) -> httpx.Client:
        """Create a new httpx client."""
        return httpx.Client(timeout=cls.TIMEOUT)

    @classmethod
    def get_artwork(cls, artwork_id: int) -> dict:
        """Fetch artwork details from the Art Institute of Chicago API.

        Args:
            artwork_id: The artwork's external ID.

        Returns:
            Dictionary with artwork data (id, title, artist_display).

        Raises:
            BadRequestException: If the artwork does not exist.
            ExternalAPIException: If the external API is unavailable.
        """
        # Check cache first
        cached = _artwork_cache.get(artwork_id)
        if cached is not None:
            logger.debug(f"Cache hit for artwork {artwork_id}")
            return cached

        url = f"{cls.BASE_URL}/artworks/{artwork_id}"
        params = {"fields": "id,title,artist_display"}

        try:
            with cls._get_client() as client:
                response = client.get(url, params=params)

            if response.status_code == 404:
                raise BadRequestException(
                    f"Artwork with external_id {artwork_id} does not exist "
                    f"in the Art Institute of Chicago API"
                )

            response.raise_for_status()
            data = response.json().get("data", {})

            artwork_data = {
                "id": data.get("id"),
                "title": data.get("title", "Unknown"),
                "artist_display": data.get("artist_display"),
            }

            # Cache the result
            _artwork_cache[artwork_id] = artwork_data
            logger.debug(f"Cached artwork {artwork_id}")

            return artwork_data

        except BadRequestException:
            raise
        except httpx.TimeoutException:
            raise ExternalAPIException(
                "Art Institute of Chicago API request timed out"
            )
        except httpx.HTTPError as e:
            raise ExternalAPIException(
                f"Error communicating with Art Institute of Chicago API: {str(e)}"
            )

    @classmethod
    def validate_artwork_exists(cls, artwork_id: int) -> dict:
        """Validate that an artwork exists in the Art Institute API.

        This is a convenience wrapper around get_artwork that makes
        the intent clearer in business logic code.

        Args:
            artwork_id: The artwork's external ID.

        Returns:
            Dictionary with artwork data.

        Raises:
            BadRequestException: If the artwork does not exist.
        """
        return cls.get_artwork(artwork_id)

    @classmethod
    def search_artworks(cls, query: str, limit: int = 10) -> list[dict]:
        """Search artworks in the Art Institute of Chicago API.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            List of artwork dictionaries.
        """
        url = f"{cls.BASE_URL}/artworks/search"
        params = {
            "q": query,
            "limit": limit,
            "fields": "id,title,artist_display",
        }

        try:
            with cls._get_client() as client:
                response = client.get(url, params=params)

            response.raise_for_status()
            data = response.json().get("data", [])

            return [
                {
                    "id": item.get("id"),
                    "title": item.get("title", "Unknown"),
                    "artist_display": item.get("artist_display"),
                }
                for item in data
            ]

        except httpx.HTTPError as e:
            raise ExternalAPIException(
                f"Error searching Art Institute of Chicago API: {str(e)}"
            )
