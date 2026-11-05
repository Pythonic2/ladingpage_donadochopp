from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Copia mídias locais ausentes para o storage configurado, sem sobrescrever objetos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Executa os uploads. Sem esta opção, apenas mostra o plano.",
        )

    def handle(self, *args, **options):
        if not settings.GCS_ENABLED:
            raise CommandError("GCS_ENABLED precisa ser true para usar este comando.")

        media_root = Path(settings.MEDIA_ROOT).resolve()
        if not media_root.is_dir():
            raise CommandError(f"MEDIA_ROOT não encontrado: {media_root}")

        execute = options["execute"]
        pending = uploaded = existing = 0
        for local_path in sorted(path for path in media_root.rglob("*") if path.is_file()):
            relative = local_path.relative_to(media_root).as_posix()
            pure = PurePosixPath(relative)
            if pure.is_absolute() or ".." in pure.parts:
                raise CommandError(f"Caminho local inseguro: {relative}")

            if default_storage.exists(relative):
                existing += 1
                continue

            pending += 1
            if not execute:
                self.stdout.write(f"UPLOAD {relative}")
                continue

            with local_path.open("rb") as stream:
                stored_name = default_storage.save(relative, File(stream, name=relative))
            if stored_name != relative:
                raise CommandError(
                    f"O storage alterou o nome de {relative} para {stored_name}; "
                    "nenhum objeto existente foi sobrescrito."
                )
            uploaded += 1
            self.stdout.write(self.style.SUCCESS(f"OK {relative}"))

        action = "enviados" if execute else "planejados"
        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: {uploaded if execute else pending} {action}; "
                f"{existing} já existentes."
            )
        )
