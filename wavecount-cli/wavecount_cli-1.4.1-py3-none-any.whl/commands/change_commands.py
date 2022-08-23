import click
import pydash as _
import PyInquirer as inq
from examples import custom_style_1
from wavecount_cli.services.backend_services import Backend


@click.group(name='change', add_help_option=False, short_help='Subcommands: [contract]', help='Change commands managements')
def change():
    pass


@click.command(name='contract', help='Change the contract of customers.')
@click.pass_context
def contract(ctx):
    try:
        backend_service = Backend(context=ctx)
        result = backend_service.sync_cache()
        customers = _.map_(result['companies'], 'company')
        contracts_list = result['contracts']
        answer = inq.prompt(
            questions=[
                {
                    'type': 'list',
                    'name': 'customer',
                    'message': 'Which customer you want to change the contract?',
                    'choices': customers
                },
                {
                    'type': 'list',
                    'name': 'contract',
                    'message': 'Wich "contract"',
                    'choices': _.map_(contracts_list, 'title'),
                }
            ],
            style=custom_style_1
        )
        contractID = _.find(contracts_list, {'title': answer['contract']})['contractID']
        backend_service.update_contract(answer['customer'], contractID)
        click.secho("")
    except Exception as e:
        exit(1)


change.add_command(contract)
