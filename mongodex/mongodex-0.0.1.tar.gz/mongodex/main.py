import sys

import pymongo
from loguru import logger
from pymongo.read_preferences import ReadPreference

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSSS}</green> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)


@logger.catch
def migrate(uri: str, collections: dict, verbose: bool = False):
    logger.remove()
    logger.add(sys.stdout, format=LOG_FORMAT, level=max(20 - (verbose * 10), 0))
    logger.add(sys.stderr, format=LOG_FORMAT, level="WARNING")

    dba = pymongo.MongoClient(uri, uuidRepresentation="standard")
    db = dba.get_default_database(read_preference=ReadPreference.PRIMARY)

    logger.info(f"Processing {len(collections)} collections")
    total_changes = 0
    for collection, indexes in collections.items():
        logger.info(f"Processing {collection}")

        index_data = {index.name: index for index in indexes}
        dbcol = db.get_collection(collection)
        dbindexes = {
            dbindex["name"]: dbindex
            for dbindex in dbcol.list_indexes()
            if not dbindex["name"].startswith("_id")
        }
        index_names = " | ".join(sorted(index_data))
        dbindex_names = " | ".join(sorted(dbindexes))

        logger.debug(f"  # of indexes for {collection}: {len(indexes)}")
        logger.debug(f"  Indexes for {collection}: {index_names}")
        logger.debug(f"  # of indexes found on db collection: {len(dbindexes)}")
        logger.debug(f"  Indexes found on db collection: {dbindex_names}")
        chchchchanges = False

        # Remove unused indexes
        for dbindex in sorted(set(dbindexes).difference(set(index_data))):
            chchchchanges = True
            total_changes += 1
            logger.info(f"    Removing unused index {dbindex}")
            dbcol.drop_index(dbindex)

        # Adding missing indexes
        for index in sorted(set(index_data).difference(set(dbindexes))):
            chchchchanges = True
            total_changes += 1
            logger.info(f"    Adding missing index {index}")
            dbcol.create_index(name=index, **index_data[index].creation_query)

        # Updating existing indexes
        for index in sorted(set(index_data).intersection(set(dbindexes))):
            logger.debug(f"    Checking if index {index} needs updating")
            if index_data[index] == dbindexes[index]:
                logger.trace(f"    Index {index} is up to date")
                continue

            chchchchanges = True
            total_changes += 1
            logger.info(f"    Updating index {index}")
            dbcol.drop_index(index)
            dbcol.create_index(name=index, **index_data[index].creation_query)

        if not chchchchanges:
            logger.info(f"  No changes to indexes for {collection}")
        logger.debug("")

    if total_changes:
        logger.info(f"{total_changes} changes made to indexes")
    else:
        logger.info("No changes made to any indexes")
