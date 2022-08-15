import logging

import click
import treefiles as tf

from hpkerga.send_config import send_config, CONF_FNAME


@click.command()
@click.argument("name", type=str)
@click.option("--url", type=str, help="Url to link")
@click.option("--desc", type=str, help="Description of the entry (may be empty)")
@click.option("--image", type=str, help="Link to image logo")
@click.option("--group", type=str, help="Group")
def main(name, url, desc, image, group):
    if name != "send":

        group = tf.none(group, "New Group")
        data = dict(tf.load_yaml(CONF_FNAME))
        if group not in data:
            data[group] = {}

        key = name.lower().replace(" ", "_") + f"_{tf.get_string()}"
        data[group][key] = {
            "name": name,
            "url": url,
            "desc": desc,
            "photo": image,
        }

        tf.dump_yaml(CONF_FNAME, data)
    send_config(CONF_FNAME)
    log.info("Correct, visit https://hp.kerga.fr")


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    main()
