from generic_crawler.core import GenericCrawler, ActionReader
from generic_crawler.config import Config

config = Config(token="auth_token", endpoint_url="service_endpoint_url")

reader = ActionReader(path_to_yaml="tests/actions/test_ddgo.yml")
crawler = GenericCrawler(config=config)

#reader.action["steps"][0]["duration"] = 20

data, _ = crawler.retrieve(reader.action)

print("ok")

