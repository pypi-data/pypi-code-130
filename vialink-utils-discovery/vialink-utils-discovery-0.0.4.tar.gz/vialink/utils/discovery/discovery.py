from dns.resolver import resolve

from .settings import settings


def resolve_srv(url):
    answers = resolve(url, 'SRV')
    record = answers[0]
    host = record.target.to_text().rstrip('.')
    port = record.port
    a_url = f'http://{host}:{port}'
    return a_url


class Record:
    def __init__(self, name: str, type_: str = 'srv'):
        self.name: str = name
        self.type_: str = type_

    def __get__(self, instance: 'Discovery', owner=None):
        if instance.environment == 'local':
            service_name = self.name.split('-')[0]
            return settings.DEV_API_GATEWAY_ENDPOINT + f'/api/{service_name}'

        if self.type_ == 'srv':
            return resolve_srv(f'{self.name}.lc-{instance.environment}')
        raise NotImplementedError()


class Discovery:
    def __init__(self, environment):
        self.environment = environment

    matching = Record('matching-service', 'srv')
    tms = Record('tms-service', 'srv')
    location = Record('location-service', 'srv')
    pricing = Record('pricing-service', 'srv')
    ai = Record('litto-service', 'srv')
    bidding = Record('bidding-service', 'srv')
    notification = Record('notification-service', 'srv')
    account = Record('account-service', 'srv')
    openapi = Record('openapi-service', 'srv')
    fulfillment = Record('fulfillment-service', 'srv')
    finance = Record('finance-service', 'srv')


discovery = Discovery(settings.ENVIRONMENT)
