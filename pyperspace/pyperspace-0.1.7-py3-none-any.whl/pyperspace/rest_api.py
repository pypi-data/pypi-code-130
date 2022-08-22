from pyperspace import Daemon, Config
from pyperspace.data import Entry
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union, List
from datetime import datetime
import logging

LOG = logging.getLogger(__name__)

def _to_nanoseconds(value: Union[datetime, int]) -> int:
    try:
        # Assume it's an int
        return int(value)
    except:
        # Otherwise it's a datetime...
        return int(value.timestamp() * 1000000000)

def datetime_from_nanoseconds(ns: int) -> datetime:
    return datetime.fromtimestamp(ns / 1000000000)

class DataEntry(BaseModel):
    time: Union[int, datetime]
    data: bytes

def generate_api(cfg: Config) -> FastAPI:
    app = FastAPI(title="Pyperspace Frontend", version="0.1.7", docs_url="/")
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
    async def get_dataset_stats(name: str, nanoseconds: bool = True):
        ds = db.open_lsm_dataset(name)
        try:
            begin_time, end_time, num_entries = ds.stats
            if not nanoseconds:
                begin_time, end_time = datetime_from_nanoseconds(begin_time), datetime_from_nanoseconds(end_time)
            return {"ok": True, "dataset": name, "begin_time": begin_time, "end_time": end_time, "num_entries": num_entries}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            ds.close()

    @app.post("/api/v1/dataset/{name}/insert")
    async def insert_rows(name: str, rows: List[DataEntry]):
        try:
            db.send_insert_many(name, (Entry(_to_nanoseconds(e.time), e.data) for e in rows))
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @app.post("/api/v1/dataset/{name}/delete")
    async def delete_range(name: str, begin: Union[int, datetime], end: Union[int, datetime]):
        ds = db.open_lsm_dataset(name)
        try:
            data = ds.delete(_to_nanoseconds(begin), _to_nanoseconds(end))
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            ds.close()

    @app.get("/api/v1/dataset/{name}/select")
    async def select_range(name: str, begin: Union[int, datetime], end: Union[int, datetime], nanoseconds: bool = True):
        ds = db.open_lsm_dataset(name)
        try:
            data = ds.find_range(_to_nanoseconds(begin), _to_nanoseconds(end))
            if nanoseconds:
                return {"ok": True, "data": [{"time": e.time, "data": e.data.tobytes()} for e in data]}
            else:
                return {"ok": True, "data": [{"time": datetime_from_nanoseconds(e.time), "data": e.data.tobytes()} for e in data]}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            ds.close()

    @app.get("/api/v1/dataset/{name}/select-all")
    async def select_all(name: str, nanoseconds: bool = True):
        ds = db.open_lsm_dataset(name)
        try:
            data = ds.find_all()
            if nanoseconds:
                return {"ok": True, "data": [{"time": e.time, "data": e.data.tobytes()} for e in data]}
            else:
                return {"ok": True, "data": [{"time": datetime_from_nanoseconds(e.time), "data": e.data.tobytes()} for e in data]}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            ds.close()

    return app
