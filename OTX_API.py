from OTXv2 import OTXv2
from OTXv2 import IndicatorTypes
from collections import Counter
from matplotlib import pyplot as plt
import numpy
import pandas as pd
import itertools
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
    response = otx.getsince(timestamp, limit=50, max_page=mp)
    return response

"Function creates a bar chart showing the number of different industries targeted by the different pulses"
"Not an official metric this is more a test/reminder for myself of how data visualization in python works."
def industries_Bar(response):
    d = []
    for r in response:
        ind = r['industries']
        if len(ind) == 0:
            continue
        for i in ind:
            d.append(i.lower())
    l = Counter(d)
    l = dict(l)
    print(l)

    x = list(l.keys())
    y = list(l.values())
    plt.barh(x, y)

    for index, value in enumerate(y):
        plt.text(value, index, str(value))
    plt.show()


def Convert(tup, di):
    for a, b in tup:
        di[a] = b
    return di


def barh(dict, label, title):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    sampledata = {'key': list(dict.keys()),
                  'value': list(dict.values())}
    test = pd.DataFrame(sampledata, index=sampledata['key'])
    test.sort_values(by="value").plot(kind="barh", color="steelblue", legend=False, grid=False, ax=ax)
    plt.xlim(0, 100)

    for i, v in enumerate(sorted(test.value)):
        plt.text(v + 0.2, i, str(round(v, 2)) + "%", color='black', va="center")

    plt.xlabel(label)
    plt.title(title)

    plt.show()


def industries(response):
    count = len(response)
    d = []
    for r in response:
        ind = r['industries']
        if len(ind) == 0:
            count = count - 1
            continue
        for i in ind:
            if i.lower() == 'energy':
               d.append(r)
    print("total amount of responses that have a non empty industry")
    print(count)
    print("total amount of pulses that have energy")
    print(len(d))

    return d


def indicator_type_freq(pulses):
    tc = 0
    data = dict()
    for p in pulses:
        indicators = p['indicators']
        tc += len(indicators)
        for i in indicators:
            typ = i['type']
            if typ in data:
                data[typ] += 1
            else:
                data[typ] = 1

    for k in list(data):
        data[k] = round(((data[k] / tc) * 100), 2)
        if data[k] < 5.0:
            data.pop(k)

    data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    dictionary = dict()
    Convert(data, dictionary)
    return dictionary


def tag_filter(tags):
    filtered_tags = []
    for t in tags:
        t = t.lower()
        if t == 'malware' or t == 'valak':
            filtered_tags.append('malware')
        elif t == 'malspam':
            filtered_tags.append('malspam')
            filtered_tags.append('malware')
        elif t == 'phishing':
            filtered_tags.append('phishing')
        elif t == 'ransomware' or t == 'wastedlocker':
            filtered_tags.append('ransomware')
            filtered_tags.append('malware')
        elif t == 'backdoor':
            filtered_tags.append('backdoor')
        elif t == 'spearphishing' or t == 'spear phishing' or t == 'spear-phishing':
            filtered_tags.append('spearphishing')
            filtered_tags.append('phishing')

    filtered_tags = list(dict.fromkeys(filtered_tags))
    return filtered_tags


def tag_freq(pulses):
    tc = 0
    data = dict()
    for p in pulses:
       tags = p['tags']
       tags = tag_filter(tags)
       nioc = len(p['indicators'])
       tc += nioc
       for t in tags:
           t = t.lower()
           if t in data:
               data[t] += nioc
           else:
               data[t] = nioc

    for k in list(data):
        data[k] = round(((data[k] / tc) * 100), 2)
        if data[k] < 5.0:
           data.pop(k)

    data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    dictionary = dict()
    Convert(data, dictionary)

    return dictionary


def targeted_country_freq(pulses):
    tc = 0
    data = dict()
    for p in pulses:
        targ = p['targeted_countries']
        nioc = len(p['indicators'])
        tc += nioc
        for t in targ:

            if t in data:
               data[t] += nioc
            else:
               data[t] = nioc

    for k in list(data):
        data[k] = round(((data[k] / tc) * 100), 2)
        if data[k] < 0.5:
           data.pop(k)
           
    data['United States'] += data['United States of America']
    data.pop('United States of America')
        #data['Russia'] = data.pop('Russian Federation')
        #data['Vietnam'] = data.pop('Viet Nam')
        #data['Iran'] = data.pop('Iran, Islamic Republic of')

        
    data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    dictionary = dict()
    Convert(data, dictionary)

    return dictionary

def normalised_targeted_country_freq(pulses):
    tc = 0
    data = dict()
    data2 = dict()
    data3 = dict()
    for p in pulses:
        targ = p['targeted_countries']
        nioc = len(p['indicators'])
        tc += nioc
        for t in targ:

            if t in data:
               data[t] += nioc
            else:
               data[t] = nioc

    data['United States'] += data['United States of America']
    data.pop('United States of America')            
        
    for k in list(data):
       if data[k] < 100:
           data.pop(k)
   
    print(data)
    for k in list(data):
        print(k)
        query = "targeted_countries:" +str(k)+"*"
        responseCountry = search_by_query(query ,9000)
        if responseCountry:
            if k == "United States":
                query = "targeted_countries:" +str('United States of America')
                responseCountry += search_by_query(query ,9000)
                print("United States of America")           
            for p in responseCountry:
                try:
                    targ = p['targeted_countries']
                    nioc = len(p['indicators'])
                    tc += nioc
                    for t in targ:
                        if str(t) == str(k):
                            if t in data2:
                                data2[t] += nioc
                            else:
                                data2[t] = nioc
                except:
                    pass
        else:
            data.pop(k)
    try:
        data2['United States'] += data2['United States of America']
        data2.pop('United States of America')
    except:
        pass
    
    data = dict(data)
    data2 = dict(data2)
    for k in data:
            if data2[k]:        
                data3[k] = float(data[k]) / float(data2[k]) * 100


        
    data3 = sorted(data3.items(), key=lambda x: x[1], reverse=True)
    dictionary = dict()
    Convert(data3, dictionary)

    return dictionary

def tag_dispersion(pulses):
    dict_malware = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0,
                 '12': 0}
    dict_phishing = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0,
                 '12': 0}
    dict_malspam = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0,
                 '12': 0}
    dict_ransomware = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0,
                 '12': 0}
    dict_spearphishing = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0,
                 '12': 0}
    dict_backdoor = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0,
                          '11': 0,
                          '12': 0}
    for p in pulses:
        nioc = len(p['indicators'])
        modified = p['created']
        modified = modified[5:7]
        tags = p['tags']
        tags = [x.lower() for x in tags]
        if 'malspam' in tags:
            dict_malspam[modified] += nioc
            dict_malware[modified] += nioc
        elif 'backdoor' in tags:
            dict_backdoor[modified] += nioc
        elif 'ransomware' in tags or 'wastedlocker' in tags:
            dict_ransomware[modified] += nioc
            dict_malware[modified] += nioc
        elif 'malware' in tags or 'valak' in tags:
            dict_malware[modified] += nioc
        elif 'spearphishing' in tags or 'spear phishing' in tags or 'spear-phishing' in tags:
            dict_spearphishing[modified] += nioc
            dict_phishing[modified] += nioc
        elif 'phishing' in tags:
            dict_phishing[modified] += nioc
        else:
            print('Nothing corresponds')

    dates = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ioc_malware = dict_malware.values()
    ioc_malspam = dict_malspam.values()
    ioc_ransomware = dict_ransomware.values()
    ioc_spearphishing = dict_spearphishing.values()
    ioc_backdoor = dict_backdoor.values()
    ioc_phishing = dict_phishing.values()

    axes = plt.gca()
    axes.set_ylim([0, 1501])

    plt.plot(dates, ioc_malware, '-b', label="malware")
    plt.plot(dates, ioc_malspam, '-g', label="malspam")
    plt.plot(dates, ioc_ransomware, '-r', label="ransomware")
    plt.plot(dates, ioc_spearphishing, '-c', label="spearphishing")
    plt.plot(dates, ioc_phishing, '-m', label="phishing")
    plt.plot(dates, ioc_backdoor, '-y', label='backdoor')

    plt.xlabel("IOCs related to threat type detected per month")
    plt.title("IOCs related to threat type detected in a specific month of a year")

    plt.legend()
    plt.show()


def threat_dispersion(pulses):
    timestamps = dict()
    for p in pulses:
        nioc = len(p['indicators'])
        modified = p['modified']
        modified = modified[0 : 7]
        if modified in timestamps:
            timestamps[modified] += nioc
        else:
            timestamps[modified] = nioc
    return timestamps


def dispersion_plot(dictionary):
    dict_2016 = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}
    dict_2017 = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}
    dict_2018 = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}
    dict_2019 = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}
    dict_2020 = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}

    for i in dictionary.keys():
        if i[0 : 4] == "2016":
            dict_2016[i[5:7]] += dictionary[i]
        elif i[0 : 4] == "2017":
            dict_2017[i[5:7]] += dictionary[i]
        elif i[0 : 4] == "2018":
            dict_2018[i[5:7]] += dictionary[i]
        elif i[0 : 4] == "2019":
            dict_2019[i[5:7]] += dictionary[i]
        elif i[0 : 4] == "2020":
            dict_2020[i[5:7]] += dictionary[i]

    dates = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ioc_2016 = dict_2016.values()
    ioc_2017 = dict_2017.values()
    ioc_2018 = dict_2018.values()
    ioc_2019 = dict_2019.values()
    ioc_2020 = dict_2020.values()

    axes = plt.gca()
    axes.set_ylim([0, 2000])

    plt.plot(dates, ioc_2016, '-b', label="2016")
    plt.plot(dates, ioc_2017, '-g', label="2017")
    plt.plot(dates, ioc_2018, '-r', label="2018")
    plt.plot(dates, ioc_2019, '-c', label="2019")
    plt.plot(dates, ioc_2020, '-m', label="2020")

    plt.xlabel("IOCs detected per month")
    plt.title("Number of IOCs detected in a specific month of a year")

    plt.legend()
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
    #Make a list of all energy pulses
    response = search_by_query("industries: Energy", 9000)

    #creates time series of tags of IOC's across months.
    #not used in the final deliverable
    #tag_dispersion(response)

    #creates time series of IOC's for different years across different months.
    #not used in final version.
    #dict = threat_dispersion(response)
    #dispersion_plot(dict)

    #frequency of selected tags in IOCs
    #used for graph 2
    dicto = tag_freq(response)
    barh(dicto, "Frequency of IOC's tagged with a threat type", "Frequency of threat types across IOC's in the energy industry")

    #frequency of the different indicator typse amongst IOCs.
    #used for graph 3
    dicto = indicator_type_freq(response)
    barh(dicto, "Frequency of the indicator types amongst all IOC's", "Most common indicator types in the energy industry")

    #frequency of the different countries targeted by IOCs.
    #used for graph 1.
    dicto = targeted_country_freq(response)
    barh(dicto, "frequency of IOC's targeting a specific country (above 1.5%)", "Frequency of country's targeted by energy industry IOC's")

    dicto = normalised_targeted_country_freq(response)
    #barh(dicto, "frequency of IOC's targeting a specific country (above 1.5%)", "Frequency of country's targeted by energy industry IOC's")
    print(dicto)

if __name__ == "__main__" :
        main()
