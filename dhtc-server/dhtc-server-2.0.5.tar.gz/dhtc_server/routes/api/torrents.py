from beanie import WriteRules
from beanie.operators import Text
from fastapi import APIRouter, Body
from datetime import datetime, timedelta

from dhtc_server.models.Torrent import Torrent, TorrentTag

from dhtc_server.models.requests.AddTorrentRequest import AddTorrentRequest
from dhtc_server.models.requests.SearchTorrentRequest import SearchTorrentRequest

from dhtc_server.models.responses.AddTorrentResponse import AddTorrentResponse
from dhtc_server.models.responses.SearchTorrentResponse import SearchTorrentResponse

router = APIRouter()


async def get_count(end: datetime, begin: datetime):
    """
    :param end: eg. datetime.now()
    :param begin: eg. datetime.now() - timedelta(days=1)
    :return: count of items in that range
    """
    return await Torrent.find(Torrent.DiscoveredOn <= end, Torrent.DiscoveredOn >= begin, fetch_links=False).count()


async def get_metrics(i_delta: timedelta, i_range: int, i_format: str) -> dict:
    end = datetime.now()
    start = end - i_delta
    step = i_delta / i_range

    data = {
        "labels": [],
        "values": []
    }

    for i in range(0, i_range):
        x = start + (step * i)
        if i_format is None:
            data["labels"].append(str((x + step)))
        else:
            data["labels"].append((x + step).strftime(i_format))
        data["values"].append(await get_count(x + step, x))

    return data


@router.post("/add", response_model=AddTorrentResponse)
async def torrent_add(torrent: AddTorrentRequest = Body(...)):
    exists = await Torrent.find_one(Torrent.InfoHash == torrent.InfoHash)

    if not exists:
        exists = Torrent(
            InfoHash=torrent.InfoHash,
            Name=torrent.Name,
            Files=torrent.Files,
            DiscoveredOn=datetime.fromtimestamp(torrent.DiscoveredOn),
            TotalSize=torrent.TotalSize,
            Tags=[],
            SeenCounter=0
        )

    exists.SeenCounter += 1
    await exists.save(link_rule=WriteRules.WRITE)

    return {
        "InfoHash": exists.InfoHash,
        "SeenCount": exists.SeenCounter
    }


@router.post("/search/name", response_model=SearchTorrentResponse)
async def torrent_search_name(request: SearchTorrentRequest = Body(...)):
    return {"Torrents": await Torrent.find(Text(request.Text)).to_list()}


@router.post("/search/file", response_model=SearchTorrentResponse)
async def torrent_search_file(request: SearchTorrentRequest = Body(...)):
    return {"Torrents": await Torrent.find(Text(request.Text)).to_list()}


@router.get("/random", response_model=SearchTorrentResponse)
async def torrent_random():
    return {"Torrents": await Torrent.aggregate([{"$sample": {"size": 1}}]).to_list()}


@router.get("/metrics")
async def torrent_count(Count: int, SecondsFromNow: int, TimeAxisFormat: str = None):
    return await get_metrics(timedelta(seconds=SecondsFromNow), Count, TimeAxisFormat)


@router.get("/count")
async def torrent_count():
    return {"count": await Torrent.count()}


@router.get("/categories")
async def torrent_categories():
    return {
        "labels": TorrentTag.get_tags(),
        "values": [(await TorrentTag.find_one(TorrentTag.Name == tag)).Seen for tag in TorrentTag.get_tags()]
    }


@router.get("/all", response_model=SearchTorrentResponse)
async def torrent_all():
    return {"Torrents": await Torrent.all().to_list()}
