from IPython import embed
from suppl import options
from time import sleep
import sys,csv,json,requests,argparse
import pandas as pd

#USAGE: $ python3 venue_create_edit.py e template.csv
# OR    $ python3 venue_create_edit.py c template.csv

def push_data(venues,cookies,job_type):
    job = 'Creating' if job_type.lower() == 'c' else 'Editing'
    
    for v in venues:
        if 'tab_panel_id' in v.keys():
            if v['tab_panel_id'] == '':
                v.pop('tab_panel_id')

        print('\n{0} venue {1}...\n'.format(job,v['name']))

        r = requests.post(options['url']+'/venue/',cookies=cookies,data=json.dumps([v],separators=(',', ':'))) \
            if job_type.lower() == 'c' else requests.put(options['url']+'/venue/',\
                cookies=cookies,data=json.dumps([v]))

        if r.status_code == 200:
            print('Successful! HTTP response: {0}\n'.format(r.status_code)) 
        else:
            embed()
            print('Error occurred for venue {0}, HTTP response {1}\n'.format(v['name'],r.status_code))

def job_check(venues):
    for venue in venues:
        print(venue['name'],'\n')

    print('\nTo proceed, type "y". To exit, type anything else.')
    response = input().lower()

    if response == 'y':
        pass
    else:
        sys.exit()

def create_unfound_venues(venues,system_venues):
    unfound = []

    for venue,item in zip(venues,system_venues):
        if type(item) == int:
            system_venues.remove(item)
            unfound.append(venues.pop(venues.index(venue)))

    if unfound != []:
        for v in unfound:
            print('Venue with partner ID {0} not found in system; adding '
                    'to list of uneditable venues.'.format(v['partner_venue_id']))

        with open('unfound_venues.csv','w',newline='') as csvfile:
            new_file = csv.writer(csvfile, delimiter=',')
            for p_v_i in [f['partner_venue_id'] for f in unfound]:
                new_file.writerow([p_v_i])
    
    return venues,system_venues

def get_vals_fr_vistar(venues,system_venues):
    venues,system_venues = create_unfound_venues(venues,system_venues)

    for venue,sys_venue in zip(venues,system_venues):
        for key in sys_venue.keys():
            try:
                if venue[key] == '':
                    venue[key] = sys_venue[key]
            except:
                venue[key] = sys_venue[key]

    for venue,sys_venue in zip(venues,system_venues):
        for key in sys_venue['address'].keys():
            try:
                if venue['address'][key] == '':
                    venue['address'][key] = sys_venue['address'][key]
            except:
                venue['address'][key] = sys_venue['address'][key]
    
    return venues

def get_system_venues(venues,cookies):
    all_venues = requests.get(options['url']+'/venue',cookies=cookies).json()
    system_venues = []
    
    for i,venue in enumerate(venues):
        for v in all_venues:
            if venue['network_id'] == v['network_id'] and \
                str(venue['partner_venue_id']) == str(v['partner_venue_id']):
                system_venues.append(v)
        if len(system_venues) < i+1:
            system_venues.append(i) #Creates int. placeholder for unfound venues

    return system_venues

def add_creation_properties(venues):
    for venue in venues:
        venue['targetings'] = {}
        venue['activation_date'] = None
        
        if venue['address']['city'] == '':
            venue['address']['city'] = None

        if venue['address']['street_address'] == '':
            venue['address']['street_address'] = None

        venue['address']['state'] = None
        venue['address']['zip_code'] = None

    return venues

def create_venues(list_template,job_type):
    venues = []
    for i in list_template.index:
        venue = {}
        row = list_template[list_template.index == i]
        for key,val in zip(row.columns,row.values.tolist()[0]):
            venue[key] = val
        venues.append(venue)
    
    for venue in venues:
        venue['address'] = {'street_address':venue.pop('street_address'),
                            'city':venue.pop('city')}

    if job_type.lower() == 'c':
        venues = add_creation_properties(venues)

    return venues

def read(bulk_template):
    list_template = pd.read_csv(bulk_template).fillna('')
    list_template = list_template.rename(columns={'venue name':'name'})
    list_template['partner_venue_id'].apply(str) ### in case these are
    list_template['tab_panel_id'].apply(str) ####### numeric only; must b string

    return list_template

def authenticate():
    r = requests.post(options['url']+'/session/',data=json.dumps(options['cred']))
    if r.status_code == 200:
        cookies = r.cookies
    else:
        print('Problems with log-in. Please review suppl.py and try again.')
        sys.exit()

    return cookies

def cli():
    parser = argparse.ArgumentParser(description="This script creates or edits venues in bulk.")
    parser.add_argument('job',choices=['c','C','e','E'],type=str,default=None)
    parser.add_argument('doc',type=str,default=None)
    args = parser.parse_args()

    return args.job,args.doc

def main():
    job_type,bulk_template = cli()
    cookies = authenticate()
    list_template = read(bulk_template)
    venues = create_venues(list_template,job_type)
    if job_type.lower() == 'e':
        system_venues = get_system_venues(venues,cookies)
        venues = get_vals_fr_vistar(venues,system_venues)
    job_check(venues)
    push_data(venues,cookies,job_type)

if __name__ == "__main__":
    main()