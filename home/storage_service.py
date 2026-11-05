"""Private media operations shared by the landing page backend.

The configured Django storage owns the application prefix. Callers only choose
an allowed media category and never provide a bucket prefix.
"""

from __future__ import annotations

import mimetypes
import re
import uuid
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.text import get_valid_filename
from PIL import Image, UnidentifiedImageError


ALLOWED_CATEGORIES = {
    "imagens": {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    },
    "videos": {
        "video/mp4",
        "video/webm",
        "video/quicktime",
    },
    "audios": {
        "audio/mpeg",
        "audio/ogg",
        "audio/wav",
        "audio/mp4",
    },
    "documentos": {
        "application/pdf",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
}


class StorageServiceError(RuntimeError):
    """A storage provider operation failed without exposing provider details."""


@dataclass(frozen=True)
class StoredFileMetadata:
    name: str
    original_name: str
    content_type: str
    size: int
    created_at: object | None = None


def _safe_original_name(filename: str) -> str:
    basename = PurePosixPath(filename.replace("\\", "/")).name
    cleaned = get_valid_filename(basename)
    if not cleaned or cleaned in {".", ".."}:
        raise ValidationError("Nome de arquivo inválido.")
    return cleaned


def _validate_image_content(uploaded_file) -> None:
    position = uploaded_file.tell() if hasattr(uploaded_file, "tell") else 0
    try:
        image = Image.open(uploaded_file)
        image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError("O conteúdo enviado não é uma imagem válida.") from exc
    finally:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(position)


def _validate_pdf_content(uploaded_file) -> None:
    position = uploaded_file.tell() if hasattr(uploaded_file, "tell") else 0
    try:
        header = uploaded_file.read(5)
    finally:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(position)
    if header != b"%PDF-":
        raise ValidationError("O conteúdo enviado não é um PDF válido.")


class MediaStorageService:
    """Validated access to the application's private media storage.

    Authorization is deliberately explicit. Views must decide whether the
    current authenticated principal can access the business object before
    passing ``authorized=True``.
    """

    def __init__(self, storage=None, max_upload_size=None):
        self.storage = storage or default_storage
        self.max_upload_size = max_upload_size or settings.MEDIA_MAX_UPLOAD_SIZE

    def _require_authorized(self, authorized: bool) -> None:
        if not authorized:
            raise PermissionDenied("Acesso ao arquivo não autorizado.")

    def _validate_storage_name(self, name: str) -> str:
        normalized = str(PurePosixPath(name.replace("\\", "/")))
        path = PurePosixPath(normalized)
        if path.is_absolute() or ".." in path.parts:
            raise ValidationError("Caminho de arquivo inválido.")
        if not path.parts or path.parts[0] not in ALLOWED_CATEGORIES:
            raise ValidationError("Categoria de arquivo inválida.")
        return normalized

    def validate_upload(self, uploaded_file, category: str) -> tuple[str, str]:
        if category not in ALLOWED_CATEGORIES:
            raise ValidationError("Categoria de arquivo inválida.")
        if uploaded_file.size <= 0:
            raise ValidationError("O arquivo está vazio.")
        if uploaded_file.size > self.max_upload_size:
            raise ValidationError("O arquivo excede o tamanho máximo permitido.")

        original_name = _safe_original_name(uploaded_file.name)
        content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
        guessed_type, _ = mimetypes.guess_type(original_name)
        if content_type not in ALLOWED_CATEGORIES[category]:
            raise ValidationError("Tipo MIME não permitido para esta categoria.")
        if guessed_type and guessed_type != content_type:
            aliases = {"image/jpg": "image/jpeg", "audio/x-wav": "audio/wav"}
            if aliases.get(guessed_type, guessed_type) != aliases.get(content_type, content_type):
                raise ValidationError("Extensão e tipo MIME do arquivo não correspondem.")

        if content_type.startswith("image/"):
            _validate_image_content(uploaded_file)
        elif content_type == "application/pdf":
            _validate_pdf_content(uploaded_file)
        return original_name, content_type

    def generate_name(self, original_name: str, category: str) -> str:
        safe_name = _safe_original_name(original_name)
        suffix = Path(safe_name).suffix.lower()
        stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", Path(safe_name).stem).strip("-")
        stem = stem[:60] or "arquivo"
        date_path = timezone.now().strftime("%Y/%m/%d")
        return f"{category}/{date_path}/{stem}-{uuid.uuid4().hex}{suffix}"

    def upload(self, uploaded_file, category: str, *, authorized: bool) -> StoredFileMetadata:
        self._require_authorized(authorized)
        original_name, content_type = self.validate_upload(uploaded_file, category)
        name = self.generate_name(original_name, category)
        try:
            stored_name = self.storage.save(name, uploaded_file)
        except Exception as exc:
            raise StorageServiceError("Não foi possível armazenar o arquivo.") from exc
        return StoredFileMetadata(
            name=stored_name,
            original_name=original_name,
            content_type=content_type,
            size=uploaded_file.size,
            created_at=timezone.now(),
        )

    def open(self, name: str, *, authorized: bool):
        self._require_authorized(authorized)
        name = self._validate_storage_name(name)
        try:
            return self.storage.open(name, "rb")
        except Exception as exc:
            raise StorageServiceError("Não foi possível recuperar o arquivo.") from exc

    def metadata(self, name: str, *, authorized: bool) -> StoredFileMetadata:
        self._require_authorized(authorized)
        name = self._validate_storage_name(name)
        try:
            size = self.storage.size(name)
            created_at = self.storage.get_created_time(name)
        except Exception as exc:
            raise StorageServiceError("Não foi possível consultar o arquivo.") from exc
        content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        return StoredFileMetadata(name, PurePosixPath(name).name, content_type, size, created_at)

    def delete(self, name: str, *, authorized: bool) -> None:
        self._require_authorized(authorized)
        name = self._validate_storage_name(name)
        try:
            self.storage.delete(name)
        except Exception as exc:
            raise StorageServiceError("Não foi possível excluir o arquivo.") from exc

    def signed_url(self, name: str, *, authorized: bool, expires_in=None) -> str:
        self._require_authorized(authorized)
        name = self._validate_storage_name(name)
        expires_in = expires_in or settings.GCS_SIGNED_URL_TTL
        try:
            try:
                return self.storage.url(
                    name,
                    parameters={
                        "expiration": timedelta(seconds=expires_in),
                        "method": "GET",
                        "version": "v4",
                    },
                )
            except TypeError:
                # FileSystemStorage does not accept provider parameters.
                return self.storage.url(name)
        except Exception as exc:
            raise StorageServiceError("Não foi possível gerar a URL temporária.") from exc
