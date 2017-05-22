from IPython import embed
from suppl import options
from time import sleep
from datetime import timedelta,timezone
import sys,csv,json,requests,argparse
import dateutil.parser as parser
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
            print('Error occurred for venue {0}, HTTP response {1}\n'.format(v['name'],r.status_code))
            embed()

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
        
        if venue['activation_date'] != '':
            parsed_date = parser.parse(venue['activation_date'])
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            venue['activation_date'] = parsed_date.isoformat()            
        else:
            venue['activation_date'] = None
        
        if venue['address']['city'] == '':
            venue['address']['city'] = None

        if venue['address']['street_address'] == '':
            venue['address']['street_address'] = None

        if venue['address']['state'] == '':
            venue['address']['state'] = None

        venue['address']['zip_code'] = None

    return venues

def create_venues(list_template,job_type):
    venues = []
    for i in list_template.index:
        venue = {}
        row = list_template[list_template.index == i]
        for key,val in zip(row.columns,row.values.tolist()[0]):
            if key == 'exclude_direct':
                if val.strip():
                    venue['excluded_buy_types'].append('direct')
            elif key == 'exclude_audience':
                if val.strip():
                    venue['excluded_buy_types'].append('audience')
            else:
                venue[key] = val
        venues.append(venue)
    
    for venue in venues:
        venue['address'] = {'street_address':venue.pop('street_address'),
                            'city':venue.pop('city'),'state':venue.pop('state')}

    if job_type.lower() == 'c':
        venues = add_creation_properties(venues)

    return venues

def save_deletions_to_csv(system_venues):
    for venue in system_venues:
        for k,v in venue['address'].items():
            venue[k] = v
        venue.pop('address')

    deleted_output = [[f for f in set(system_venues[0].keys())]]
    
    for venue in system_venues:
        write_row = []
        for key in set(venue.keys()):
            write_row.append(venue[key])
        deleted_output.append(write_row)

    with open('deletions.csv','w',newline='') as csvfile:
        new_file = csv.writer(csvfile,delimiter=',')
        for f in deleted_output:
            new_file.writerow(f)

    print('Venues set for deletion have been saved to a .csv for backup purposes.')

def delete_venues(list_template,cookies):
    venues = []
    
    for row in list_template.itertuples():
        venues.append({'partner_venue_id':row[2],'network_id':row[1]})
    
    system_venues = get_system_venues(venues,cookies)
    save_deletions_to_csv(system_venues)

    for venue in venues:
        print('Deleting venue {0}'.format())
        r = requests.delete('{0}/selling/venues/{1}'.format(options['url'],
            venue['partner_venue_id']),cookies=cookies)

        if r.status_code == 200:
            print('Successful! HTTP response: {0}\n'.format(r.status_code)) 
        else:
            print('Error occurred for venue {0}, HTTP response {1}\n'.format(v['name'],r.status_code))
            embed()

    sys.exit()

def read(bulk_template):
    list_template = pd.read_csv(bulk_template).fillna('')
    list_template = list_template.rename(columns={'venue name':'name'})
    list_template['partner_venue_id'] = list_template['partner_venue_id'].astype(str) ### in case these are
    list_template['tab_panel_id'] = list_template['tab_panel_id'].astype(str) ####### numeric only; must b string

    return list_template

def authenticate():
    r = requests.post(options['url']+'/session/',data=json.dumps(options['cred']))
    if r.status_code == 200:
        admin_cookies = r.cookies
    else:
        print('Problems with log-in. Please review suppl.py and try again.')
        sys.exit()
    
    while True:
        print('Please type in the email login of the partner: '\
            '(Example: dooh-partner@vistarmedia.com)')
        options['partner']['username'] = str(input())
        p = requests.post(options['url']+'/assume_user',cookies=r.cookies,
            data=json.dumps(options['partner']))

        if p.status_code == 200:
            partner_cookies = p.cookies
            break
        else:
            print('Partner not found. Please try again or exit.')
    
    return admin_cookies,partner_cookies

def cli():
    parser = argparse.ArgumentParser(description="This script creates, edits, or deletes venues in bulk.")
    parser.add_argument('job',choices=['c','C','e','E','d','D'],type=str,default=None)
    parser.add_argument('doc',type=str,default=None)
    args = parser.parse_args()

    return args.job,args.doc

def main():
    job_type,bulk_template = cli()
    admin_cookies,partner_cookies = authenticate()
    list_template = read(bulk_template)
    if job_type.lower() == 'd':
        delete_venues(list_template,partner_cookies)
    venues = create_venues(list_template,job_type)
    if job_type.lower() == 'e':
        system_venues = get_system_venues(venues,partner_cookies)
        venues = get_vals_fr_vistar(venues,system_venues)
    job_check(venues)
    push_data(venues,partner_cookies,job_type)

if __name__ == "__main__":
    main()