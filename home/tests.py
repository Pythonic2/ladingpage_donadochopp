from io import BytesIO
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from PIL import Image
from storages.backends.gcloud import GoogleCloudStorage

from .gcs_storage import CachedGoogleCloudStorage
from .storage_service import MediaStorageService, StorageServiceError


def image_upload(name="foto.png", size=(2, 2)):
    content = BytesIO()
    Image.new("RGB", size, color="red").save(content, format="PNG")
    return SimpleUploadedFile(name, content.getvalue(), content_type="image/png")


@override_settings(MEDIA_MAX_UPLOAD_SIZE=1024 * 1024, GCS_SIGNED_URL_TTL=900)
class MediaStorageServiceTests(SimpleTestCase):
    def setUp(self):
        self.storage = Mock()
        self.storage.save.side_effect = lambda name, content: name
        self.service = MediaStorageService(storage=self.storage)

    def test_upload_image_uses_category_and_unique_name(self):
        first = self.service.upload(image_upload(), "imagens", authorized=True)
        second = self.service.upload(image_upload(), "imagens", authorized=True)

        self.assertTrue(first.name.startswith("imagens/"))
        self.assertTrue(first.name.endswith(".png"))
        self.assertNotEqual(first.name, second.name)
        self.assertEqual(first.content_type, "image/png")

    def test_upload_pdf(self):
        upload = SimpleUploadedFile(
            "contrato.pdf",
            b"%PDF-1.7\nconteudo",
            content_type="application/pdf",
        )
        result = self.service.upload(upload, "documentos", authorized=True)
        self.assertTrue(result.name.startswith("documentos/"))

    def test_rejects_fake_image_content(self):
        upload = SimpleUploadedFile("foto.png", b"not-an-image", content_type="image/png")
        with self.assertRaises(ValidationError):
            self.service.upload(upload, "imagens", authorized=True)

    def test_rejects_disallowed_mime_type(self):
        upload = SimpleUploadedFile("script.exe", b"MZ", content_type="application/x-msdownload")
        with self.assertRaises(ValidationError):
            self.service.upload(upload, "documentos", authorized=True)

    def test_rejects_oversized_file(self):
        service = MediaStorageService(storage=self.storage, max_upload_size=4)
        upload = SimpleUploadedFile("arquivo.txt", b"12345", content_type="text/plain")
        with self.assertRaises(ValidationError):
            service.upload(upload, "documentos", authorized=True)

    def test_requires_explicit_authorization(self):
        with self.assertRaises(PermissionDenied):
            self.service.open("documentos/arquivo.pdf", authorized=False)

    def test_rejects_path_traversal_and_foreign_prefix(self):
        for name in ("../segredo.pdf", "crm/empresas/1/segredo.pdf"):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                self.service.open(name, authorized=True)

    def test_open_and_delete_authorized_file(self):
        expected = BytesIO(b"arquivo")
        self.storage.open.return_value = expected
        result = self.service.open("documentos/arquivo.pdf", authorized=True)
        self.assertIs(result, expected)
        self.service.delete("documentos/arquivo.pdf", authorized=True)
        self.storage.delete.assert_called_once_with("documentos/arquivo.pdf")

    def test_metadata(self):
        self.storage.size.return_value = 42
        self.storage.get_created_time.return_value = "created"
        result = self.service.metadata("documentos/arquivo.pdf", authorized=True)
        self.assertEqual(result.size, 42)
        self.assertEqual(result.content_type, "application/pdf")

    def test_wraps_provider_failure(self):
        self.storage.save.side_effect = OSError("provider unavailable")
        with self.assertRaises(StorageServiceError):
            self.service.upload(image_upload(), "imagens", authorized=True)

    def test_signed_url_for_gcs_blob(self):
        self.storage.url.return_value = "https://signed.example/file"

        url = self.service.signed_url("imagens/file.png", authorized=True)

        self.assertEqual(url, "https://signed.example/file")
        self.storage.url.assert_called_once()


@override_settings(GCS_SIGNED_URL_CACHE_TTL=3600)
class CachedGoogleCloudStorageTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.storage = CachedGoogleCloudStorage(
            bucket_name="test-bucket",
            project_id="test-project",
            location="landing-page-ddc/midias",
        )

    def tearDown(self):
        cache.clear()

    def test_reuses_signed_url_without_signing_again(self):
        with patch.object(
            GoogleCloudStorage,
            "url",
            return_value="https://storage.example/signed",
        ) as signer:
            first = self.storage.url("imagens/banner.png")
            second = self.storage.url("imagens/banner.png")

        self.assertEqual(first, second)
        signer.assert_called_once_with("imagens/banner.png", parameters=None)
