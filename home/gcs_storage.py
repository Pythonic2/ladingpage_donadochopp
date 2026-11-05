"""Google Cloud Storage backend optimized for stable, private landing media."""

import hashlib
import json

from django.conf import settings
from django.core.cache import cache
from storages.backends.gcloud import GoogleCloudStorage


class CachedGoogleCloudStorage(GoogleCloudStorage):
    """Cache expensive IAM-signed URLs while keeping the bucket private."""

    def _url_cache_key(self, name, parameters=None):
        payload = json.dumps(
            {"name": self._normalize_name(name), "parameters": parameters or {}},
            sort_keys=True,
            default=str,
        ).encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        return f"gcs-signed-url:{digest}"

    def url(self, name, parameters=None):
        key = self._url_cache_key(name, parameters)
        cached_url = cache.get(key)
        if cached_url:
            return cached_url

        signed_url = super().url(name, parameters=parameters)
        cache.set(key, signed_url, timeout=settings.GCS_SIGNED_URL_CACHE_TTL)
        return signed_url

    def save(self, name, content, max_length=None):
        stored_name = super().save(name, content, max_length=max_length)
        cache.delete(self._url_cache_key(stored_name))
        return stored_name

    def delete(self, name):
        cache.delete(self._url_cache_key(name))
        return super().delete(name)
