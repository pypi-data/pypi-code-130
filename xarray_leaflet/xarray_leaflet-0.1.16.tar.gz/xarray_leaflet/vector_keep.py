import json
from functools import partial
from pathlib import Path
from typing import Optional

import mercantile
import numpy as np
import pyproj
import xarray as xr
import dask.array
from geocube.api.core import make_geocube
from geocube.rasterize import rasterize_image
from geopandas import GeoDataFrame
from rasterio.enums import MergeAlg
from shapely.geometry import box, mapping
from shapely.ops import transform

from .utils import debug  # noqa


class Zvect:
    def __init__(
        self,
        df: GeoDataFrame,
        measurement: str,
        width: int,
        height: int,
        root_path: str = "",
    ):
        # reproject to Web Mercator
        self.df = df.to_crs(epsg=3857)
        self.measurement = measurement
        self.width = width
        self.height = height
        self.zzarr = Zzarr(root_path, width, height)
        self.tiles = []

    def get_da_tile(self, tile: mercantile.Tile) -> Optional[xr.DataArray]:
        xy_bounds = mercantile.xy_bounds(tile)
        dx = (xy_bounds.right - xy_bounds.left) / self.width
        dy = (xy_bounds.top - xy_bounds.bottom) / self.height
        # take one more pixel to avoid glitches
        bbox = box(
            xy_bounds.left - dx,
            xy_bounds.bottom - dy,
            xy_bounds.right + dx,
            xy_bounds.top + dy,
        )
        geom = json.dumps(
            {**mapping(bbox), "crs": {"properties": {"name": "EPSG:3857"}}}
        )
        df_tile = self.df.clip(bbox.bounds)
        if df_tile.empty:
            return None
        ds_tile = make_geocube(
            vector_data=df_tile,
            resolution=(-dy, dx),
            measurements=[self.measurement],
            rasterize_function=partial(
                rasterize_image, merge_alg=MergeAlg.add, all_touched=True
            ),
            fill=0,
            geom=geom,
        )
        # remove added pixels
        da_tile = ds_tile[self.measurement][1:-1, 1:-1]
        return da_tile

    def get_da_llbbox(
        self, bbox: mercantile.LngLatBbox, z: int
    ) -> Optional[xr.DataArray]:
        tiles = mercantile.tiles(*bbox, z)
        all_none = True
        for tile in tiles:
            if tile in self.tiles:
                all_none = False
            else:
                da_tile = self.get_da_tile(tile)
                if da_tile is not None:
                    all_none = False
                    self.zzarr.write_to_zarr(tile, da_tile.values)
                self.tiles.append(tile)
        if all_none:
            return None
        project = pyproj.Transformer.from_crs(
            pyproj.CRS("EPSG:4326"), pyproj.CRS("EPSG:3857"), always_xy=True
        ).transform
        b = box(*bbox)
        polygon = transform(project, b)
        left, bottom, right, top = polygon.bounds
        return self.zzarr.ds(z)["da"].sel(
            x=slice(left, right), y=slice(top, bottom)
        )

    def get_da(self, z: int) -> xr.DataArray:
        return self.zzarr.ds(z)["da"]


class Zzarr:
    def __init__(self, root_path: str, width: int, height: int):
        self.root_path = Path(root_path)
        self.width = width
        self.height = height
        self.ds = {}

    def write_to_zarr(self, tile: mercantile.Tile, tile_data: np.ndarray):
        x, y, z = tile
        path = self.root_path / str(z)
        lazy_data = dask.array.zeros((2**z * self.height, 2**z * self.width), chunks=(self.height, self.width))
        debug(f"{(2**z * self.height, 2**z * self.width)=}")
        debug(f"{(self.height, self.width)=}")
        if not path.exists():
            # write Dataset to zarr
            mi, ma = mercantile.minmax(z)
            ul = mercantile.xy_bounds(mi, mi, z)
            lr = mercantile.xy_bounds(ma, ma, z)
            bbox = mercantile.Bbox(ul.left, lr.bottom, lr.right, ul.top)
            x_coord = np.linspace(bbox.left, bbox.right, 2**z * self.width)
            y_coord = np.linspace(bbox.top, bbox.bottom, 2**z * self.height)
            #da = xr.DataArray(lazy_data, coords=dict(y=y_coord, x=x_coord), dims=["y", "x"])
            da = xr.DataArray(lazy_data)
            ds = xr.Dataset({"da": da})
            debug("to_zarr")
            import time
            t0 = time.time()
            ds.to_zarr(path, compute=False)
            debug("to_zarr done")
            t1 = time.time()
            debug(f"{t1 - t0}")
        y0 = y * self.height
        y1 = (y + 1) * self.height
        x0 = x * self.width
        x1 = (x + 1) * self.width
        lazy_data[y0:y1, x0:x1] = tile_data
        da = xr.DataArray(lazy_data, coords=dict(y=y_coord, x=x_coord), dims=["y", "x"])
        self.ds[z] = xr.Dataset({"da": da})
        region = dict(
            y=slice(y0, y1),
            x=slice(x0, x1)
        )
        ds_tile = self.ds[z].isel(region)
        ds_tile.to_zarr(
            path,
            mode="a",
            region=region
        )
