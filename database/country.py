from textwrap import wrap
import pandas as pd 
import os, requests


dir = os.path.dirname(__file__)

def country_data(country_code):
    datafile = pd.read_csv(os.path.join(dir, 'data.csv'), index_col='Code')
    result = datafile.loc[country_code]
    #print(result)
    return result.to_dict()




def get_country_code(ipaddr):
    try:
        #url = 'https://stat.ripe.net/data/whois/data.json?resource={}'.format(ipaddr)
        url = 'https://stat.ripe.net/data/maxmind-geo-lite/data.json?resource={}'.format(ipaddr)
        #response = requests.get(url).json()['data']['records']
        response = requests.get(url).json()['data']['located_resources'][0]['locations']
        #print(response)
        #len(response)
        #return response
    except:
        country_code = 'private'
        return country_code

    try:
        for el in response:
            country_code = el['country']
            '''
            for dct in el:
                if dct['key'].lower() == 'country':
                    country_code = dct['value']
                    #print(country_code)
                    return country_code

                else:
                    country_code = 'private'
            '''
        return country_code            
        
    except:
        country_code = 'private'
        return country_code