from datetime import date
import os
import requests
import sys
import json
from html_to_json import convert, convert_tables
from urllib import parse as urlparse
__all__=('tseclient','Persona')

def sanitizar_resultado(lista):
    """En pocas palabras le quita los breaklines, espacios y demas de 
    su contenido y lo compone dentro de un diccionario"""

    def sanitizar_string(s): return str(s).strip()
    resultado = dict()
    keys = []

    skeys = 0
    idc = 1
    for sublistas in lista:
        for index, item in enumerate(sublistas):
            if item == "":
                continue
            if index in [0, 2]:  # Es una key
                _item = sanitizar_string(item).replace(
                    ":", "").replace(' ', "_")
                if _item == 'Identificación':
                    _item += str(idc)
                    idc += 1
                resultado[_item] = None

                keys.append(_item)
            if index in [1, 3]:  # Es un valor
                resultado[keys[skeys]] = sanitizar_string(item)
                skeys += 1

    return resultado


def edad(birthdate: date):
    today = date.today()
    age = today.year - birthdate.year - \
        ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


def delctype(dictionary: dict) -> dict:
    dictionarya = dictionary.copy()
    del dictionarya['Content-Type']
    return dictionarya


class Persona(object):

    def __init__(self, data) -> None:
    
        self.fecha_de_nacimiento_str = str(data['Fecha_de_Nacimiento'])
        
        dia, mes, anyo = [int(val)
                          for val in self.fecha_de_nacimiento_str.split('/')]
        self.fecha_de_nacimiento = date(anyo, month=mes, day=dia)
        self.edad = edad(self.fecha_de_nacimiento)
        self.edad_str = str(self.edad)+(b' a\xc3\xb1os').decode('utf-8')
        self.nombre = str(' '.join([sname.capitalize() for sname in data['Nombre'].split(' ')]))

        self.apellido = str(data['Primer_Apellido']).capitalize()
                       
  
        self.segundo_apellido = str(data.get('Segundo_Apellido', '')).capitalize(

        )  # Personas sin segundo apellido como estadounidenses
        self.nombre_completo = f'{self.nombre} {self.apellido} {self.segundo_apellido}'.strip(
        )

        self.cedula = str(data['Número_de_Cédula'])
        self.padres_rawdata = dict({"padre": {
            "nombre": (' '.join([subname.capitalize() for subname in data['Hijo/a_de'].split(' ') ])), "cedula": data['Identificación1']
        }, "madre": {
            "nombre": (' '.join([subname.capitalize() for subname in data['Y'].split(' ') ])), "cedula": data['Identificación2']
        }})
        self.madre.nombre_completo =  str(self.padres_rawdata['madre']['nombre'])
        self.padre.nombre_completo =  str(self.padres_rawdata['padre']['nombre'])
        self.madre.cedula =  str(self.padres_rawdata['madre']['cedula'])
        self.padre.cedula =  str(self.padres_rawdata['padre']['cedula'])
        self.cc = str(data['Conocido/a_Como']) if '' != data['Conocido/a_Como'] else None
        self.sexo = str(data.get('Sexo', 'N/A')).lower()
        # En el sitio web del tribunal si haces una consulta,
        # no aparece el campo de sexo, probablemente lo cambien
        # por "Genero" a largo plazo
        # debido a la ley de ideologia de genero, o alguna vara asi :p
        self.ha_muerto = bool(data['Fallecido/a'] == 'SI')
        self.marginal = bool(data['Marginal'] == 'SI')
        self.empadronado = bool(data['Empadronado/a'] == 'SI')
        self.fallecio = bool(self.ha_muerto)
        self.lugar_de_nacimiento = str(data['Lugar_de_Nacimiento'])
        self.nacionalidad = str(data['Nacionalidad']).capitalize()
        self.conocido_como = self.cc
        self.json = self.datos_raw = dict(vars(self))
        
        pass

    def __repr__(self) -> str:
        # type(self).__name__+'('+str({"nombre_completo":self.nombre_completo, "id":self.id,
        return '<Persona [nombre_completo="{}"]>'.format(self.nombre_completo)
        # "cedula":self.cedula})+')'

    
        
    class madre(object):
            def __repr__(self) -> str:
                       return '<Persona.madre [nombre_completo="{}"]>'.format(self.nombre_completo)

            nombre_completo:str
            cedula:str
    class padre(object):
            def __repr__(self) -> str:
                       return '<Persona.padre [nombre_completo="{}"]>'.format(self.nombre_completo)
            
            nombre:str
            cedula:str


class tseclient:
    """Esta clase se encarga de preservar las cookies para poder hacer las requests,
     y brinda los metodos para las peticiones web.
     Argumentos: 
     • (Opcional) url_base: Es la url principal del TSE (Tribunal supremo de elecciones ) por defecto es https://servicioselectorales.tse.go.cr/chc"""

    def __init__(self, url_base=None, proxylist={}) -> None:
        self.sesion = requests.Session()
        self.sesion.proxies.update(proxylist)
        self.tseurl = url_base if url_base is not None else "https://servicioselectorales.tse.go.cr/chc/"
        self.default_headers = {"Sec-Fetch-Dest": "empty",  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",

                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "same-origin", "Accept": "*/*",
                                "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
                                "X-Requested-With": "XMLHttpRequest",
                                "X-MicrosoftAjax": "Delta=true",
                                "Cache-Control": "no-cache", }

        pass

    def refrescarCookies(self) -> None:
        '''En caso de que la peticion arroje un error,
        se puede llamar a este metodo para cambiar el "Jarro" de cookies '''
        self.sesion = requests.Session()
        return

    def consulta_cedula(self, numero_de_cedula):
        """Informacion detallada sobre alguien
        Argumentos:
        . (Requerido) numero_de_cedula (Puede ser un numero o una string)"""
        if type(numero_de_cedula) is int:
            numero_de_cedula = str(numero_de_cedula)

        if type(numero_de_cedula) not in (int, str, float):
            raise TypeError(
                'El tipo de argumento de numero_de_cedula debe ser una string, o un int (numero)')
        if len(numero_de_cedula) != 9:
            raise TypeError('La longitud del numero de cedula es {} que nueve (9)'.format(
                'mayor' if len(numero_de_cedula) > 9 else 'menor'))
        headers = self.default_headers.copy()
        self.sesion.get(url=urlparse.urljoin(

            self.tseurl, 'consulta_cedula.aspx'))  # Cargar las cookies para la peticion POST
        headers['Content-Type'] = "application/x-www-form-urlencoded; charset=utf-8"
        headers['Referer'] = urlparse.urljoin(  # Enviar los datos de busqueda.
            self.tseurl, 'consulta_cedula.aspx')
        body = {
            "ScriptManager1": "UpdatePanel1|btnConsultaCedula",
            "__VIEWSTATE": "/wEPDwULLTE1OTIyMjMwMDVkZGf0hlOpAN/BhOLq3iF0Kb+QcNbXnKtj9cz9G/QSHoS3",
            "__VIEWSTATEGENERATOR": "88BF6952",
            "__EVENTVALIDATION": "/wEdAAlhsepm4eRCbhEZmiY4Hi6/tTfNpOz0CH4vKngBfzxDIS2hNtLCXCKq92TKMjYS4CX24YOX6Ab2AoRRJXYcN6RPZrHMfDaOuX2c5DuODJSeiypYaPycT+v9uchEvEhJB0tWvoSmUD9cccAzkkmmOR9zkJ/OtIbU04qfUHmBu0NaRFCfQQ61frM+tUgerGfangYS2N04UlIFa4rVghzY4oGplT9A52lAlbeWWbDkW1aVjw==",
            "txtcedula": numero_de_cedula,
            "__ASYNCPOST": "true",
            "btnConsultaCedula": "Consultar"
        }
        self.sesion.post(url=urlparse.urljoin(  # Enviar los datos de busqueda.
            self.tseurl, 'consulta_cedula.aspx'), headers=headers, data=urlparse.urlencode(body)
        )

        self.sesion.get(url=urlparse.urljoin(self.tseurl,
                        'resultado_persona.aspx'), headers=delctype(headers))

        headers['Referer'] = urlparse.urljoin(  # Enviar los datos de busqueda.
            self.tseurl, 'resultado_persona.aspx')
        self.sesion.post(url=urlparse.urljoin(self.tseurl, 'resultado_persona.aspx'),
                         data="ScriptManager1=UpdatePanel4%7CLinkButton11&__LASTFOCUS=&__EVENTTARGET=LinkButton11&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwULLTIwNDExMTE1NjkPZBYCAgUPZBYKAg0PZBYCZg9kFiYCAw8PFgQeBFRleHQFJ1NPTElDSVRBUiBDRVJUSUZJQ0FDSU9OIERFIEVTVEFETyBDSVZJTB4HVG9vbFRpcAUnU09MSUNJVEFSIENFUlRJRklDQUNJT04gREUgRVNUQURPIENJVklMZGQCCQ8PFgIeB1Zpc2libGVoZGQCDQ8PFgIfAmhkZAITDw8WAh8ABQkxMTAyNTA1MzlkZAIXDw8WAh8ABQoyMy8wMS8xOTc5ZGQCGw8PFgIfAAUcS0FUVElBIFZBTkVTU0EgU09MQU5PIEFDVcORQWRkAh8PDxYCHwAFDUNPU1RBUlJJQ0VOU0VkZAIjDw8WAh8ABQEgZGQCJw8PFgIfAAUINDMgQcORT1NkZAIrDw8WAh8ABRdSVVBFUlRPIFNPTEFOTyBDSVNORVJPU2RkAi8PDxYCHwAFAk5PZGQCMw8PFgIfAAUBMGRkAjsPDxYCHwAFGkNMQVJBIExVWiBBQ1XDkUEgUk9EUklHVUVaZGQCQQ8PFgIfAAUBMGRkAkMPDxYCHwAFDERJVk9SQ0lBRE8vQWRkAkUPDxYCHwAFATRkZAJJDw8WAh8AZWRkAk0PDxYCHwAFCEZFTUVOSU5PZGQCTw8PFgIfAGVkZAIfDw8WAh8AZWRkAicPZBYCZg9kFgICAw88KwARAgEQFgAWABYADBQrAABkAikPZBYCZg9kFgICAw88KwARAgEQFgAWABYADBQrAABkAisPZBYCZg9kFgICAw88KwARAgEQFgAWABYADBQrAABkGAQFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYEBQtJbWFnZUluaWNpbwUTSW1hZ2VDb25zdWx0YUNlZHVsYQUTSW1hZ2VDb25zdWx0YU5vbWJyZQUKSW1hZ2VTYWxpcgUMR3JpZHZvdGFjaW9uD2dkBQ9HcmlkbWF0cmltb25pb3MPZ2QFCUdyaWRoaWpvcw9nZO%2BH%2FtJgq8NjpaMLYHcTKiEXuWkknOfTChH%2FctqQHTZI&__VIEWSTATEGENERATOR=9B2EA161&__EVENTVALIDATION=%2FwEdABFAJ9AOECCD6yPGNivK4dt3iqbymbVNf9U%2B%2BjDqKpBZeKfpigIS2tjkEVbbLpJMXRKuK%2Bc1zGEqN0QiOtSVIjbTo8XTvMemOeiTsiCv52YIemVikE%2B%2ByEdoHTLugZV7sMg9MKWwyYnyGaRupuuiPjUTpRd%2Bw%2Bp8QgmIF%2Fxj83k64%2Fwe9%2BBwVz5Ihp%2BbC78EPFMCfHJxCCGkqx0cEcFZIWbctTfNpOz0CH4vKngBfzxDIS2hNtLCXCKq92TKMjYS4CX24YOX6Ab2AoRRJXYcN6RPb%2F5cgUWoPLK9FRe9Wehz9MYrrw85uciTs0i4KdeN%2FlBd3VPD6Wym8us3eHD1WYbKZrHMfDaOuX2c5DuODJSei%2BH1hWXvxR5U2ZnFMHxc2WVhU1TPbODZ9xWO%2BvSy9SkP&hdnCodigoAccionMarginal=1&hdnFechaSucesoMatrimonio=&__ASYNCPOST=true&",
                         headers=headers)
        response = self.sesion.get(url=urlparse.urljoin(
            self.tseurl, 'detalle_nacimiento.aspx'), headers=delctype(headers))
        persona = convert(response.content.decode(
            'utf-8'))['html'][0]['body'][0]['form'][0]['table'][1]

        return Persona(sanitizar_resultado(
            convert_tables(response.content.decode('utf-8'))[3]))

    def consulta_nombres(self, nombre: str, apellido: str, segundo_apellido="", limite=50) -> list[dict]:
        '''Peticion hacia consulta_nombres.aspx que devuelve como resultado una lista de objetos "Persona"
        Argumentos:
        · (Requerido) nombre
        · (Requerido) apellido
        · (Opcional) segundo_apellido'''

        headers = self.default_headers.copy()
        headers['Content-Type'] = "application/x-www-form-urlencoded; charset=utf-8"
        headers["Referer"] = urlparse.urljoin(  # Enviar los datos de busqueda.
            self.tseurl, 'consulta_nombres.aspx')

        body = {'ScriptManager1': 'UpdatePanel1|btnConsultarNombre',
                '__VIEWSTATE': '/wEPDwUKMTE5MDA1NjkyMGRkDLOKATPznmx9I9lbIMFKv03MaOOc0w1bamfOxJBoC0o=',
                '__VIEWSTATEGENERATOR': '6D9EFD0A',
                '__EVENTVALIDATION':
                '/wEdAAs/42GmxfoIA1Ax2hbYG924tTfNpOz0CH4vKngBfzxDIS2hNtLCXCKq92TKMjYS4CX24YOX6Ab2AoRRJXYcN6RPZrHMfDaOuX2c5DuODJSei2DFl2PkTbOZC6CPafAYm8pRl9ScBPfOFka6q0phNEL8twmUZ6F4j9mDkTAUvEdpjI9xyi8lOqgWkn57Bww75NShJ9OpgLV2di8vwMcGnnPAKp+hSpqDPVCqS6ldDro7ssek8vFqyuKhgnei+/PG4dmCycVW2TeTxF7bADBOc5Oj',
                "referencia": "", "observacion": "",
                'txtnombre': nombre, 'txtapellido1': apellido, '__ASYNCPOST': 'true', 'btnConsultarNombre': 'Consultar'}
        # Los datos de arriba estan precargados con el apellido y el nombre, mas unos datos extra (No se ni para que sirven :p)
        if not segundo_apellido == "":
            body['txtapellido2'] = segundo_apellido

        self.sesion.post(url=urlparse.urljoin(  # Enviar los datos de busqueda.
            self.tseurl, 'consulta_nombres.aspx'), headers=headers, data=urlparse.urlencode(body)
        )
        del headers['Content-Type']
        response = self.sesion.get(url=urlparse.urljoin(
            self.tseurl, 'muestra_nombres.aspx'
        ), headers=headers)

        personas = convert(response.content.decode(
            'utf-8'))['html'][0]['body'][0]['form'][0]['table'][2]['tr'][2]['td'][1]['table'][0]['tr']
        collected_personas = list()
        for indice, persona in enumerate(personas):
            if indice >= limite:
                break
            persona_ = persona['td'][0]['span'][0]
            persona_nyc = persona_['label'][0]['_value'].split('   ')
            persona_nombre = persona_nyc[1]

            persona_cedula = persona_nyc[0].split(' ')[1]
            collected_personas.append(
                {"nombre_completo": persona_nombre, "cedula": persona_cedula})

        return collected_personas
