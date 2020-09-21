from OTXv2 import OTXv2
from OTXv2 import IndicatorTypes
from collections import Counter
from matplotlib import pyplot as plt

# API key
API_KEY = '00ae9112982b83069f9566b026a8f3db4279ba4c8483930197ecd41f91230f76'
OTX_SERVER = 'https://otx.alienvault.com/'
# Create OTX object to interect with API.
otx = OTXv2(API_KEY, server=OTX_SERVER)

"the OTX api is defined at: https://github.com/AlienVault-OTX/OTX-Python-SDK/blob/master/OTXv2.py"

"Get a number of pulses from all pulses that the user is subscribed too."
def getall(mp):
    response = otx.getall(modified_since=None, author_name=None, limit=50, max_page=mp, max_items=None, iter=False)
    return response

"get a number of pulses modified since a certain timestamp"
def getsince(timestamp, mp):
    response = otx.getsince(timestamp, limit=40, max_page=mp)
    return response

"Function creates a bar chart showing the number of different industries targeted by the different pulses"
"Not an official metric this is more a test/reminder for myself of how data visualization in python works."
def Industries_Bar(response):
    d = []
    for r in response:
        ind = r['industries']
        if len(ind) == 0:
            continue
        for i in ind:
            d.append(i.lower())
    l = Counter(d)
    l = dict(l)

    x = list(l.keys())
    y = list(l.values())
    plt.barh(x, y)

    for index, value in enumerate(y):
        plt.text(value, index, str(value))
    plt.show()

"instead of searching within all pulses provide a string query and only return pulses matching" \
"said query."
def search_by_query(query, mr):
    query_response = otx.search_pulses(query, mr)
    query_response = query_response['results']
    return query_response

"Instead of searching for pulses this function will help you search for users of OTX."
def search_users(query, mr):
    query_response = otx.search_users(query, mr)
    query_response = query_response['results']
    return query_response

"If a pulse id is provided it will return the full pulse details."
def pulse_details(pulse_id):
    pulse_detail = otx.get_pulse_details(pulse_id)
    return pulse_detail

"Instead of returning the entire pulse this function will only return the indicators of the pulse."
def pulse_indicators(pulse_id):
    pulse_indicator = otx.get_all_indicators(pulse_id)
    return pulse_indicator

"return all information OTX has on a certain indicator for example a domain like google.com"
def indicator_details(indicator_type, indicator_id):
    indicator = otx.get_indicator_details_full(indicator_type, indicator_id)
    return indicator

def main():
    response = getall(5)
    Industries_Bar(response)


if __name__ == "__main__" :
        main()