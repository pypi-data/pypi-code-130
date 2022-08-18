from ..response import ok, error


def _format(response: dict) -> dict:
    return {
        'email': response['email'],
        'first_name': response['first_name'],
        'last_name': response['last_name'],
        'id': response['id']
    }


def validate_client(client: dict) -> dict:
    fields = ['nombre', 'apellido', 'documento', 'email', 'domicilio']
    for f in fields:
        if f not in client:
            return error('{} field is missing'.format(f))

    for f in ['calle', 'altura']:
        if f not in client['domicilio']:
            return error('domicilio.{} field is missing'.format(f))

    return ok(client)


class Customer:
    def __init__(self, sdk):
        self.sdk = sdk

    def create(self, client: dict) -> dict:
        """

        :param client: Diccionario del cliente
        nombre, apellido, documento, email, domicilio son obligatorios
        :return:
        """
        # Check para el client y evitar errores
        r = validate_client(client)
        if r['status'] == 'error':
            return r

        customer_response = self.sdk.customer().search(filters={'email': client['email']})
        if len(customer_response['response']['results']) > 0:
            return ok(_format(customer_response['response']['results'][0]))

        try:
            street_number = int(client['domicilio']['altura'])
        except:
            street_number = 1

        mp_customer_data = {
            'email': client['email'],
            'first_name': client['nombre'],
            'last_name': client['apellido'],
            'phone': {
                'area_code': None,
                'number': client['celular']
            },
            'identification': {
                'type': 'DNI',
                'number': client['documento']
            },  # ! Tipo de identificacion hardcodeado
            'address': {
                'street_name': client['domicilio']['calle'],
                'street_number': street_number,
            }
        }
        mp_response = self.sdk.customer().create(mp_customer_data)
        if mp_response['status'] < 400:
            return ok(_format(mp_response['response']), mp_response['status'])

        return error(mp_response['response'], mp_response['status'])

    def get(self, customer_id: str):
        mp_response = self.sdk.customer().get(customer_id)
        if mp_response['status'] < 400:
            customer = mp_response['response']
            return ok(_format(customer), mp_response['status'])

        return error(mp_response['response']['message'], mp_response['status'])

    def search(self, filters: dict):
        mp_response = self.sdk.customer().search(filters)
        if mp_response['status'] < 400:
            return ok(mp_response['response'], mp_response['status'])

        return error(mp_response['response'], mp_response['status'])
