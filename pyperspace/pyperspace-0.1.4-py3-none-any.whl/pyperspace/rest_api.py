from pyperspace import Daemon, Config
from pyperspace.data import Entry
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import logging

LOG = logging.getLogger(__name__)

class DataEntry(BaseModel):
    time: int
    data: bytes

def generate_api(cfg: Config) -> FastAPI:
    app = FastAPI(title="Pyperspace Frontend", version="0.1.4", docs_url="/")
    db = Daemon(cfg.data_dir, cfg.datasets, cfg.storage)

    @app.on_event("startup")
    async def startup():
        LOG.info("starting daemon...")
        db.start()

    @app.on_event("shutdown")
    async def shutdown():
        LOG.info("shutting down daemon...")
        db.stop()
        db.close()

    @app.post("/api/v1/dataset/{name}/create")
    async def create_dataset(name: str):
        try:
            db.send_create(name)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True}

    @app.post("/api/v1/dataset/{name}/drop")
    async def drop_dataset(name: str):
        try:
            db.drop(name)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @app.get("/api/v1/datasets")
    async def list_datasets():
        try:
            return {"ok": True, "datasets": list(db.datasets)}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    @app.get("/api/v1/dataset/{name}/stats")
    async def get_dataset_stats(name: str):
        ds = db.open_lsm_dataset(name)
        try:
            begin_time, end_time, num_entries = ds.stats
            return {"ok": True, "dataset": name, "begin_time": begin_time, "end_time": end_time, "num_entries": num_entries}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            ds.close()

    @app.post("/api/v1/dataset/{name}/insert")
    async def insert_rows(name: str, rows: List[DataEntry]):
        try:
            db.send_insert_many(name, (Entry(e.time, e.data) for e in rows))
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @app.post("/api/v1/dataset/{name}/delete")
    async def delete_range(name: str, begin: int, end: int):
        ds = db.open_lsm_dataset(name)
        try:
            data = ds.delete(begin, end)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            ds.close()

    @app.get("/api/v1/dataset/{name}/select")
    async def select_range(name: str, begin: int, end: int):
        ds = db.open_lsm_dataset(name)
        try:
            data = ds.find_range(begin, end)
            return {"ok": True, "data": [{"time": e.time, "data": e.data.tobytes()} for e in data]}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            ds.close()

    @app.get("/api/v1/dataset/{name}/select-all")
    async def select_all(name: str):
        ds = db.open_lsm_dataset(name)
        try:
            data = ds.find_all()
            return {"ok": True, "data": [{"time": e.time, "data": e.data.tobytes()} for e in data]}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            ds.close()

    return app
