import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.contrib.staticfiles.storage import ManifestFilesMixin, StaticFilesStorage
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

MANIFEST_PATH = "staticfiles.json"


class PicselliaManifestFilesMixin(ManifestFilesMixin):
    def hashed_name(self, name, content=None, filename=None):
        if name.startswith("dist/"):
            return name
        return super(PicselliaManifestFilesMixin, self).hashed_name(
            name, content, filename
        )


class PicselliaManifestStaticFilesStorage(
    PicselliaManifestFilesMixin, StaticFilesStorage
):
    pass


class Command(BaseCommand):
    def log(self, msg):
        """
        Small log helper
        """
        self.stdout.write(msg)

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Force the reupload of files",
        )

    def handle(self, *args, **options):
        self.force = options["force"]
        self.verbosity = options["verbosity"]

        with TemporaryDirectory() as tmpdirname:
            # Save custom settings
            # STATIC_ROOT=BASE_DIR/static

            # STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
            # or
            # STATICFILES_STORAGE = 'picsell_os.storage_backends.CustomManifestStaticStorage'
            #
            saved_static_root = settings.STATIC_ROOT
            saved_storage = settings.STATICFILES_STORAGE

            try:
                max_workers = settings.MAX_WORKERS_S3_COLLECT_STATIC
            except Exception:
                max_workers = 10

            # 1. Collect static with ManifestStaticFiles => Generate hashed filenames
            # 2 differents hashes => 2 different content files
            settings.STATIC_ROOT = tmpdirname
            settings.STATICFILES_STORAGE = "picsellia_collectstatic.management.commands.picsellia_collectstatic.PicselliaManifestStaticFilesStorage"

            call_command("collectstatic")

            # 2. Read all hashed files
            # All files need to be upload
            manifest = Path(tmpdirname) / MANIFEST_PATH
            with manifest.open("rb") as f:
                to_upload = set(json.load(f)["paths"].values())

            settings.STATIC_ROOT = saved_static_root
            settings.STATICFILES_STORAGE = saved_storage
            storage = import_string(saved_storage)()

            if storage.exists(MANIFEST_PATH):
                with storage.open(MANIFEST_PATH) as f:
                    # 3. Read distant storage manifest
                    already_uploaded = set(json.load(f)["paths"].values())

                    # Intersection files don't need to be upload
                    intersection = to_upload.intersection(already_uploaded)
                    self.log(f"{len(intersection)} files were already uploaded")

                    # 4. Compute difference between distant files and tmp files
                    if self.force:
                        self.log("Forcing the reupload of files")
                    else:
                        to_upload.difference_update(already_uploaded)

            def _save_asset(path):
                path_obj = Path(tmpdirname) / path
                with path_obj.open("rb") as f:
                    storage.save(path, f)
                return path

            # 5. Upload difference
            still_error = False
            self.log(f"Start the upload of {len(to_upload)} files")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(_save_asset, path): path for path in to_upload
                }
                to_retry = []
                for future in as_completed(futures):
                    path = futures[future]
                    try:
                        uploaded = future.result()
                        self.log(f"{uploaded} was uploaded")
                    except Exception as e:
                        self.log(
                            "Something went wrong ({}) with file {}. Will retry".format(
                                str(e), path
                            )
                        )
                        to_retry.append(path)

                retries = {
                    executor.submit(_save_asset, path): path for path in to_retry
                }
                for future in as_completed(retries):
                    path = retries[future]
                    try:
                        retried = future.result()
                        self.log(f"{retried} was finally uploaded")
                    except Exception as e:
                        self.log(
                            "Something went wrong ({}) with file {} a second time. No retry".format(
                                str(e), path
                            )
                        )
                        still_error = True

            # 6. Save manifest in the end when everything succeeded
            if not still_error:
                self.log("Uploading the manifest")
                _save_asset(MANIFEST_PATH)
            else:
                self.log(
                    "Did not upload the manifest because at least one error occured"
                )
