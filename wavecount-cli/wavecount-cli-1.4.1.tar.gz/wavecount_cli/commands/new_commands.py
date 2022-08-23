import click
import pydash as _
import PyInquirer as inq
from examples import custom_style_1
from wavecount_cli.services.backend_services import Backend
from wavecount_cli.utils import (IntValidate, PartNumberValidate,
                                 SerialNumberValidate, StringValidate)


@click.command(name='new', help='Register a new device.')
@click.pass_context
def new(ctx):
    try:
        request_payload = {}
        roles: str = ctx.obj['roles']
        backend_service = Backend(context=ctx)
        result = backend_service.sync_cache()
        companies = result['companies']
        company_choices = ['new', *_.map_(companies, 'company')]
        part_numbers = result['partNumbers']
        part_numbers_choices = []
        contracts_list = result['contracts']
        if roles == 'admin':
            part_numbers_choices.extend(['new'])
        part_numbers_choices.extend(part_numbers)
        answer = inq.prompt(
            questions=[
                {
                    'type': 'input',
                    'name': 'serial_number',
                    'message': 'Enter device "serial number"',
                    'validate': SerialNumberValidate,
                },
                {
                    'type': 'list',
                    'name': 'part_number',
                    'message': 'Wich "part number"',
                    'choices': part_numbers_choices,
                    'validate': PartNumberValidate,
                }
            ],
            style=custom_style_1
        )
        serial_number: str = answer['serial_number']
        request_payload['serialNumber'] = serial_number
        part_number: str = answer['part_number']
        request_payload['partNumber'] = part_number
        if part_number == 'new':
            answer = inq.prompt(
                style=custom_style_1,
                questions=[
                    {
                        'type': 'input',
                        'name': 'part_number',
                        'message': 'Enter device "part number"',
                        'validate': PartNumberValidate,
                    }
                ],
            )
            part_number: str = answer['part_number']
            request_payload['partNumber'] = part_number
        answer = inq.prompt(
            questions=[
                {
                    'type': 'list',
                    'name': 'company',
                    'message': 'Wich "company"',
                    'choices': company_choices,
                    'validate': StringValidate,
                }
            ],
            style=custom_style_1
        )
        company: str = answer['company']
        request_payload['company'] = company
        if company == 'new':
            answers = inq.prompt(
                style=custom_style_1,
                questions=[
                    {
                        'type': 'input',
                        'name': 'company',
                        'message': 'Enter "company"',
                        'validate': StringValidate,
                    },
                    {
                        'type': 'list',
                        'name': 'contract',
                        'message': 'Wich "contract"',
                        'choices': _.map_(contracts_list, 'title'),
                    },
                    {
                        'type': 'input',
                        'name': 'store',
                        'message': 'Enter "store"',
                        'validate': StringValidate,
                    },
                    {
                        'type': 'input',
                        'name': 'store_number',
                        'message': 'Enter "store number"',
                        'validate': IntValidate,
                    },
                ],
            )
            company: str = answers['company']
            request_payload['company'] = company
            contract: str = answers['contract']
            contractId = _.find(contracts_list, {'title': contract})['contractID']
            request_payload['contractID'] = contractId
            store: str = answers['store']
            request_payload['store'] = store
            store_number: int = int(answers['store_number'])
            request_payload['storeNumber'] = store_number
        else:
            store_choices = ['new']
            company_item = _.find(companies, {'company': company})
            stores_items = company_item['stores']
            stores = _.uniq(_.map_(stores_items, 'store'))
            store_choices.extend(stores)
            answer = inq.prompt(
                style=custom_style_1,
                questions=[
                    {
                        'type': 'list',
                        'name': 'store',
                        'message': 'Enter "store"',
                        'choices': store_choices,
                        'validate': StringValidate,
                    },
                ],
            )
            store: str = answer['store']
            request_payload['store'] = store
            if store == 'new':
                answer = inq.prompt(
                    style=custom_style_1,
                    questions=[
                        {
                            'type': 'input',
                            'name': 'store',
                            'message': 'Enter "store"',
                            'validate': StringValidate,
                        },
                        {
                            'type': 'input',
                            'name': 'store_number',
                            'message': 'Enter "store number"',
                            'validate': IntValidate,
                        },
                    ],
                )
                store: str = answer['store']
                store_number: int = int(answer['store_number'])
                request_payload['store'] = store
                request_payload['storeNumber'] = store_number
            else:
                store_item = _.find(stores_items, {'store': store})
                store_number: int = store_item['storeNumber']
                request_payload['storeNumber'] = store_number
        device = backend_service.register_device(request_payload)
        dev_id = device['deviceId']
        prim_key = device['symmetricKey']['primaryKey']
        comp = device['company']
        store = device['store']
        store_num = device['storeNumber']
        sn = device['serialNumber']
        pn = device['partNumber']
        click.secho(' Part Number:    {}'.format(pn), fg='green')
        click.secho(' Serial Number:  {}'.format(sn), fg='green')
        click.secho(' Device Id:      {}'.format(dev_id), fg='green')
        click.secho(' Primary Key:    {}'.format(prim_key), fg='green')
        click.secho(' Company:        {}'.format(comp), fg='green')
        click.secho(' Store:          {}'.format(store), fg='green')
        click.secho(' Store Number:   {}'.format(store_num), fg='green')
        click.secho()
    except Exception as e:
        exit(1)
