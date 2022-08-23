from pandas import DataFrame
from asclepius.medewerker import Medewerker

def check_input(gebruiker, product, target_link, download_link, variabele_links):
    '''
    Deze functie checkt de validiteit van de input voor de __init__() functie van de RegressieTest class.
    '''
    if type(gebruiker) != Medewerker:
        raise TypeError('Opgegeven gebruiker is niet van type medewerker.')

    # Check of er links zijn opgegeven
    if (target_link != None) and (download_link != None):
        if type(target_link) != str:
            raise TypeError('Opgegeven target link is niet van type string.')
        if type(download_link) != str:
            raise TypeError('Opgegeven download link is niet van type string.')

    if (type(variabele_links) != type(None)):
        if type(variabele_links) != DataFrame:
            raise TypeError('Opgegeven variabele links is geen DataFrame.')
    return None