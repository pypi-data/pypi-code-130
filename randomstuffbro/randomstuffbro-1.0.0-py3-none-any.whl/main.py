import requests
import html_to_json
import time 
def get_data(website_url):
    base_url = 'https://nibbler.insites.com/en_US/reports/'
    website_url = website_url.replace('https://', '')
    website_url = website_url.replace('http://', '')
    full_url = base_url + website_url
    computed = False
    jned = ''
    while not computed:
        resp = requests.get(full_url).text
        length = len(resp)
        print(length)
        if length<15000:
            print('sleeping')
            time.sleep(5)
        else:
            print(length)
            jned = html_to_json.convert(resp)
            break

    returner = []
    for x in jned['html'][0]['body'][0]['div'][0]['div'][1]['div'][0]['div'][0]['div'][0]['div']:
        current = x['h3'][0]

        values ={
            'name' : current['_value'],
            'rating' : current['span'][0]['_attributes']['class'][1],
            'value': current ['span'][0]['_value']
        }
        returner.append(values)

    sudo = 0
    for x in jned ['html'][0]['body'][0]['div'][0]['div'][1]['div'][2]['div'][0]['div']:
        try:
            attribute = x['h2'][0]['_value']
            value = x['h2'][0]['span'][0]['_value']
            values ={
                'name' : attribute,
                'value': value
            }
            returner.append(values)
        except:
            pass
    print(returner)
    
get_data(input('enter website url: '))