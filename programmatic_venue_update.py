# from IPython import embed
from suppl import options
from time import sleep
import sys,csv,json,requests

def main(bulk_template):
	list_b = read(bulk_template)
	list_b,all_venues,cookies = get_ids(list_b)
	venue_edits_to_submit = create_venue_dicts(list_b,all_venues)
	for d in venue_edits_to_submit:
		r = requests.put(options['url']+'/venue/',cookies=cookies,data=json.dumps([d],separators=(',', ':')))
		# if r.status_code != 200: #FOR TROUBLESHOOTING
		# 	embed()
		print('\nEditing venue {0}...\n'.format(d['partner_venue_id']))
		print('HTTP response: {0}\n'.format(r.status_code)) 

def is_a_number(value):
	if value.isdigit() == True:
		return [True,int(value)]
	else:
		try:
			float(value)
			return [True,float(value)]
		except:
			return [False]

def unstringify_ints(dict_v,list_b,all_venues): #turn str'd integers into ints
	for k in list(dict_v.keys()): 
		if k == 'tab_panel_id' or k == 'partner_venue_id': 
			#if these values consist of str'd ints only, they should remain strings
			continue
		if type(dict_v[k]) == str:
			if is_a_number(dict_v[k])[0] == True:
				dict_v[k] = is_a_number(dict_v[k])[1]
	return dict_v
		
def create_venue_dicts(list_b,all_venues):
	list_of_dicts = []
	for row in list_b[1:]: #populate non-template values with values in system
		dict_v = {'targetings':None,'impressions_30_sec': None,'action': None,
			'address': {},'dma':None}
		for key in list(dict_v.keys()): 
			if key == 'address' or key == 'action':
				continue
			else:
				dict_v[key] = all_venues[row[-1]][key]
		for i,n in enumerate(list_b[0][1:17]): #populate dict with values in template
			if i+1 > 8 and i+1 < 13:
				continue
			else:
				dict_v[n] = row[i+1]
		for i,n in enumerate(list_b[0][9:13]):
			dict_v['address'][n] = row[i+9]
		dict_v = unstringify_ints(dict_v,list_b,all_venues)
		list_of_dicts.append(dict_v)
	return list_of_dicts

def get_editable_values(list_b,all_venues):
	for row in list_b[1:]: #fill blank values (non-address) in template with values in system
		for i,cell in enumerate(row[2:15]):
			if i+2 > 8 and i+2 < 13:
				continue
			else:
				if cell == '' or cell == ' ': #(2nd condition is in case a space is accidentally entered in template)
					if i+2 == 14: #skips tab panel ID since not every venue has this
						continue
					row.pop(i+2)
					row.insert(i+2,all_venues[row[-1]][list_b[0][i+2]])
		for i,cell in enumerate(row[9:13]): #now fill in blank values for address with values in system
			if cell == '' or cell == ' ':
				row.pop(i+9)
				row.insert(i+9,all_venues[row[-1]]['address'][list_b[0][i+9]])
	return list_b,all_venues

def user_prompt(list_b,all_venues):
	print('You will be editing the following venues:\n')
	sleep(0.5)
	for row in list_b[1:]:
		for venue in all_venues:  
			if venue['network_id'] == row[15] and venue['id'] == row[16]:
				print(venue['name'])
	print('\nTo proceed, type "y". To exit, type anything else.')
	response = input().lower()
	if response == 'y':
		pass
	else:
		sys.exit()

def get_ids(list_b):
	r = requests.post(options['url']+'/session/',data=json.dumps(options['cred']))
	cookies = r.cookies
	all_venues = requests.get(options['url']+'/venue',cookies=r.cookies).json()
	all_networks = requests.get(options['url']+'/network',cookies=r.cookies).json()
	for row in list_b[1:]: #get network id from network name
		for n in all_networks:
			if n['name'].lower().replace(' ','') == row[0].lower().replace(' ',''):
				row.append(n['id'])
	for row in list_b[1:]: #get venue id from venue name and network
		for i,v in enumerate(all_venues): 
			if v['network_id'] == row[15] and v['partner_venue_id'].lower().replace(' ','') == row[1].lower().replace(' ',''):
				row.append(v['id'])
				row.append(i)
	user_prompt(list_b,all_venues)
	list_b,all_venues = get_editable_values(list_b,all_venues)
	return list_b,all_venues,cookies

def read(bulk_template):
	list_b = []
	readable_b = csv.reader(open(bulk_template,'r'),delimiter = ',',quotechar='"')
	for row in readable_b:
		list_b.append(row)
	list_b[0].pop(2)
	list_b[0].insert(2,'name')
	list_b[0].extend(['network_id','id','venue index'])
	return list_b

if __name__ == "__main__":
	main(sys.argv[1])