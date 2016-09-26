# from IPython import embed
from suppl import options
from time import sleep
import sys,csv,json,requests,argparse,collections

#USAGE:$ python3 programmatic_venue_update.py e template.csv

def push_data(venues_to_push,cookies,job_type):
	'''
	Takes list of venue dictionaries and iterates thru each one, 
	pushing edits or creations into the system via API.
	'''
	def status(r,venue):
		if r.status_code == 200:
			print('Successful! HTTP response: {0}\n'.format(r.status_code)) 
		else:
			print('Error occurred for venue {0}, HTTP response {1}\n'.format(venue['name'],r.status_code))

	if job_type == 'c':
		for v in venues_to_push:
			print('\nCreating venue {0}...\n'.format(v['name']))
			r = requests.post(options['url']+'/venue/',cookies=cookies,data=json.dumps([v],separators=(',', ':')))
			status(r,v)
	elif job_type == 'e':
		for v in venues_to_push:		
			print('\nEditing venue {0}...\n'.format(v['name']))
			r = requests.put(options['url']+'/venue/',cookies=cookies,data=json.dumps([v],separators=(',', ':')))
			status(r,v)

def unstringify_ints(venue):
	'''
	Numerical values in venue dictionary have to be correctly formatted
	into integers in order for data to push.
	'''
	def _is_a_number(value):
		if value.isdigit() == True:
			return [True,int(value)]
		else:
			try:
				float(value)
				return [True,float(value)]
			except:
				return [False]

	for k in list(venue.keys()): 
		if k == 'tab_panel_id' or k == 'partner_venue_id' or k == 'name': 
			continue
		if type(venue[k]) == str:
			if _is_a_number(venue[k])[0] == True:
				venue[k] = _is_a_number(venue[k])[1]
				
	return venue

def create_unfound_venues(unfound):
	with open('unfound_venues.csv','w',newline='') as csvfile:
	    new_file = csv.writer(csvfile, delimiter=',')
	    for f in unfound:
		    new_file.writerow(f)

def edit_check(list_v,all_venues):
	'''
	For editing: if a venue did not have a venue ID saved from get_ids, 
	it gets flagged, is removed from list, and is saved in a csv output of 
	"unfound" venues. Remaining venues are printed on screen.

	all_venues is then altered so that it only contains the venues being
	edited.
	'''
	unfound = []

	for row in list_v[1:]:
		try:
			row[14]
		except:
			print('Venue with partner ID {0} not found in system; '
				'adding to list of uneditable venues.'.format(row[1]))
			unfound.append(row)
			list_v.remove(row)

	create_unfound_venues(unfound)
	venues_to_edit = []
	counter = 0	

	for row in list_v[1:]: 
		for venue in all_venues:  
			if venue['network_id'] == row[0] and venue['id'] == row[14]:
				print('{0} You will be editing {1}'.format(counter+1,venue['name']))
				venues_to_edit.append(venue) 
				row.pop(15) #replace all_venues idx w/ venues_to_edit idx
				row.append(counter)
				counter += 1

	print('\nTo proceed, type "y". To exit, type anything else.')
	response = input().lower()

	if response == 'y':
		return list_v,venues_to_edit
	else:
		sys.exit()

def get_vals_fr_vistar(venue,idx,all_venues):
	'''
	For editing: runs through each value in the venue dictionary and
	looks for blanks. If blank, retrieve the value that is stored in 
	the system.
	'''
	if venue['tab_panel_id'] == '':
		venue.pop('tab_panel_id')

	for k in list(venue.keys()):
		if venue[k] == '':
			venue[k] = all_venues[idx][k]
	
	for k in list(venue['address'].keys()):
		if venue['address'][k] == '':
			venue['address'][k] = all_venues[idx]['address'][k]

	venue['action'] = None
	venue['impressions_30_sec'] = all_venues[idx]['impressions_30_sec']
	venue['targetings'] = all_venues[idx]['targetings']

	return venue

def get_ids(list_v,cookies,job_type):
	'''
	For editing: gets venue IDs from Vistar and appends them to the 
	end of each row in the template, along with the venue index in
	all_venues list. 
	'''
	all_venues = requests.get(options['url']+'/venue',cookies=cookies).json()
	for row in list_v[1:]: 
		for i,v in enumerate(all_venues): 
			if v['network_id'] == row[0] and v['partner_venue_id'].lower().replace(' ','') == row[1].lower().replace(' ',''):
				row.append(v['id']) # venue ID --> cell 14
				row.append(i) # index of venue in all_venues --> cell 15

	return list_v,all_venues

def create_venues(list_v,cookies,job_type): 
	'''
	Creates a list of dictionaries, via zipping of header and rows. 
	Each dict is a venue that will be created or edited.
	'''
	if job_type == 'e':
		list_v,all_venues = get_ids(list_v,cookies,job_type)
		list_v,all_venues = edit_check(list_v,all_venues)

	headers = list_v[0]
	list_of_dicts = []

	for row in list_v[1:]:
		pairs = dict(zip(headers[0:11],row[0:11]))
		address = dict(zip(headers[11:14],row[11:14]))
		pairs['address'] = address
		pairs['targetings'] = {}
		try:
			pairs['id'] = row[14]
			list_of_dicts.append([pairs,row[15]])
		except:
			list_of_dicts.append(pairs)

	if job_type == 'e':
		for i,d in enumerate(list_of_dicts):
			venue = get_vals_fr_vistar(d[0],d[1],all_venues)
			list_of_dicts.pop(i)
			list_of_dicts.insert(i,venue) #removes stored all_venue index,
										#  since it's no longer needed	
	else:
		for d in list_of_dicts:
			if d['tab_panel_id'] == '':
				d.pop('tab_panel_id')
		
	for d in list_of_dicts:
		d = unstringify_ints(d)

	return list_of_dicts

def read(bulk_template):
	'''
	Turns csv into list
	'''
	list_v = []
	readable_b = csv.reader(open(bulk_template,'r'),delimiter = ',',quotechar='"')	
	for row in readable_b:
		list_v.append(row)
	list_v[0].pop(2)
	list_v[0].insert(2,'name') # edit user-friendly header to system-friendly header 
	list_v[0].extend(['id','venue index']) # add more headers

	return list_v

def cli():
	'''
	USAGE:$ python3 programmatic_venue_update.py e template.csv
	'''
	parser = argparse.ArgumentParser(description="This script creates or edits venues in bulk.")
	parser.add_argument('job',choices=['c','C','e','E'],type=str,default=None)
	parser.add_argument('doc',type=str,default=None)
	args = parser.parse_args()

	return args.job,args.doc

def main():
	job_type,bulk_template = cli()
	r = requests.post(options['url']+'/session/',data=json.dumps(options['cred']))
	if r.status_code == 200:
		cookies = r.cookies
	else:
		print('Problems with log-in. Please review credentials and/or URL '
				' and try again.')
		sys.exit()
	list_v = read(bulk_template)
	venues_to_push = create_venues(list_v,cookies,job_type)
	push_data(venues_to_push,cookies,job_type)

if __name__ == "__main__":
	main()