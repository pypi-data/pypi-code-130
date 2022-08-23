from pathlib import Path
from typing import Union
from zipfile import ZipFile

from lnschema_core import id
from sqlmodel import Session, select  # noqa

import lnbfx.schema as schema  # noqa


def parse_bfx_file_type(filepath: Union[str, Path]):
    """Returns bioinformatics file type by parsing its path.

    Args:
        filepath (Union[str,Path]): Path to the file to be parsed.

    Returns:
        str: String with the identified file type.
    """
    filepath = Path(filepath)
    if any(i in {".gz"} for i in filepath.suffixes):
        return filepath.suffixes[0]
    else:
        return filepath.suffix


def get_bfx_files_from_dir(dirpath: Union[str, Path]) -> list:
    """Parses dir and returns files that can be mapped to a bioinformatics file type.

    Args:
        dirpath (Union[str,Path]): Path to dir.

    Returns:
        list: List with bioinformatics file paths.
    """
    dirpath = Path(dirpath)

    if dirpath.suffix == ".zip":
        with ZipFile(dirpath, "r") as zipObj:
            filelist = zipObj.namelist()
            return [file for file in filelist if not file.endswith("/")]
    bfx_files_in_dir = [
        file.as_posix() for file in dirpath.rglob("*") if file.is_file()
    ]

    return bfx_files_in_dir


class BfxRun:
    def __init__(
        self,
        *,
        pipeline_id: str = None,
        pipeline_v: str = "3.8.1",
        pipeline_name: str = "nf-core/rnaseq",
        pipeline_source: str = "https://github.com/nf-core/rnaseq",
        run_id: str = None,
        run_name: str = None
    ):
        self._bfx_pipeline_id = pipeline_id
        self._bfx_pipeline_v = pipeline_v
        self._bfx_pipeline_name = pipeline_name
        self._bfx_pipeline_source = pipeline_source
        self._bfx_run_id = run_id
        self._bfx_run_name = run_name
        self._ingested = False
        self._run_dir = "./"
        self._db_engine = None

    @property
    def db_engine(self):
        """Database engine."""
        return self._db_engine

    @db_engine.setter
    def db_engine(self, engine):
        self._db_engine = engine

    @property
    def run_dir(self):
        """BFX pipeline run dir."""
        return self._run_dir

    @run_dir.setter
    def run_dir(self, dirpath):
        if isinstance(dirpath, str):
            dirpath = Path(dirpath)
        self._run_dir = dirpath

    def get_pipeline_pk(self):
        """Queries pipeline and returns private key.

        Args:
            None.

        Returns:
            Tuple with the pipeline id and version.

        Raises:
            RuntimeError: If the pipeline has not been ingested yet.
        """
        pipeline = self._query_bfx_pipeline()
        if pipeline is None:
            raise RuntimeError(
                "Unable to get pipeline private key. Pipeline not yet ingested."
            )
        return (pipeline.id, pipeline.v)

    def get_run_pk(self) -> str:
        """Queries pipeline run and returns private key.

        Args:
            None.

        Returns:
            str: Pipeline run id.

        Raises:
            RuntimeError: If the pipeline run has not been ingested yet.
        """
        pipeline_run = self._query_bfx_run()
        if pipeline_run is None:
            raise RuntimeError(
                "Unable to get pipeline run private key. Pipeline run not yet ingested."
            )
        return pipeline_run.id

    def check_and_ingest(self, pipeline_run_id: str):
        """Ingests bionformatics pipeline and pipeline run if that hasn't been done yet.

        Args:
            pipeline_run_id: An a primary key id for the
            `lnschema_core.pipeline_run` table.

        Returns:
            None.
        """
        bfx_pipeline_entry = self._query_bfx_pipeline()
        bfx_run_entry = self._query_bfx_run()
        if bfx_pipeline_entry is None:
            if self._bfx_pipeline_id is None:
                self._bfx_pipeline_id = id.id_base62(4)
            bfx_pipeline_entry = self._insert_bfx_pipeline()
        if bfx_run_entry is None:
            if self._bfx_run_id is None:
                self._bfx_run_id = pipeline_run_id
            bfx_run_entry = self._insert_bfx_run(
                bfx_pipeline_entry.id, bfx_pipeline_entry.v
            )

    def link_dobject(self, dobject_id: str, dobject_filepath: Union[str, Path]):
        """Ingest bfxmeta and add link between dobject and bfx file type.

        Args:
            dobject_id (str): dobject's ID.
            dobject_filepath (Union[str, Path]): dobject's filepath.

        Returns:
            None.
        """
        file_type = parse_bfx_file_type(dobject_filepath)
        dobject_dirpath = str(Path(dobject_filepath).parent.resolve())
        bfxmeta_id = self._insert_bfxmeta(file_type, dobject_dirpath).id
        self._insert_dobject_bfxmeta(dobject_id, bfxmeta_id)

    def _insert_bfx_run(self, bfx_pipeline_id: str, bfx_pipeline_v: str):
        """Inserts entry in the bfx_run table."""
        with Session(self._db_engine) as session:
            bfx_run_entry = schema.bfx_run(
                id=self._bfx_run_id,
                name=self._bfx_run_name,
                dir=self.run_dir,
                bfx_pipeline_id=bfx_pipeline_id,
                bfx_pipeline_v=bfx_pipeline_v,
            )
            session.add(bfx_run_entry)
            session.commit()
            session.refresh(bfx_run_entry)
            return bfx_run_entry

    def _insert_bfx_pipeline(self):
        """Inserts entry in the bfx_pipeline table."""
        with Session(self._db_engine) as session:
            bfx_pipeline_entry = session.exec(
                select(schema.bfx_pipeline).where(
                    schema.bfx_pipeline.id == self._bfx_pipeline_id,
                    schema.bfx_pipeline.v == self._bfx_pipeline_v,
                )
            ).first()
            if bfx_pipeline_entry is None:
                bfx_pipeline_entry = schema.bfx_pipeline(
                    id=self._bfx_pipeline_id,
                    v=self._bfx_pipeline_v,
                    name=self._bfx_pipeline_name,
                    source=self._bfx_pipeline_source,
                )
                session.add(bfx_pipeline_entry)
                session.commit()
                session.refresh(bfx_pipeline_entry)
            return bfx_pipeline_entry

    def _insert_bfxmeta(self, file_type: str, dirpath: str):
        """Inserts entry in the bfxmeta table."""
        with Session(self._db_engine) as session:
            bfxmeta_entry = session.exec(
                select(schema.bfxmeta).where(
                    schema.bfxmeta.file_type == file_type,
                    schema.bfxmeta.dir == dirpath,
                )
            ).first()
            if bfxmeta_entry is None:
                bfxmeta_entry = schema.bfxmeta(file_type=file_type, dir=dirpath)
                session.add(bfxmeta_entry)
                session.commit()
                session.refresh(bfxmeta_entry)
            return bfxmeta_entry

    def _insert_dobject_bfxmeta(self, dobject_id: str, bfxmeta_id: int):
        """Inserts entry in the dobject_bfxmeta table."""
        dobject_bfxmeta_entry = schema.dobject_bfxmeta(
            dobject_id=dobject_id, bfxmeta_id=bfxmeta_id
        )
        with Session(self._db_engine) as session:
            session.add(dobject_bfxmeta_entry)
            session.commit()
            session.refresh(dobject_bfxmeta_entry)
        return dobject_bfxmeta_entry

    def _query_bfx_pipeline(self):
        """Queries bfx pipeline."""
        with Session(self._db_engine) as session:
            bfx_pipeline_entry = session.exec(
                select(schema.bfx_pipeline).where(
                    schema.bfx_pipeline.id == self._bfx_pipeline_id,
                    schema.bfx_pipeline.v == self._bfx_pipeline_v,
                )
            ).first()
        return bfx_pipeline_entry

    def _query_bfx_run(self):
        """Queries bfx pipeline run."""
        with Session(self._db_engine) as session:
            bfx_run_entry = session.exec(
                select(schema.bfx_run).where(
                    schema.bfx_run.id == self._bfx_run_id,
                )
            ).first()
        return bfx_run_entry
