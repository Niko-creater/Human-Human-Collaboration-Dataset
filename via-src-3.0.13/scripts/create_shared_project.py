# Create a VIA3 shared project
#
# Author: Abhishek Dutta <adutta _AT_ robots.ox.ac.uk>
# 10 Oct. 2019

import http.client
import string
import os
import pickle
import json
import uuid
import time
import csv

def create_via3_shared_project(via_project_data):
	via_project_data_str = json.dumps(via_project_data)
	conn = http.client.HTTPConnection('zeus.robots.ox.ac.uk')
	conn.request('POST', '/via/store/3.x.y/', via_project_data_str)
	response = conn.getresponse()
	via_project_id = ''
	if response.status == 200:
	via_project_id = response.read().decode('utf-8')
	else:
	via_project_id = 'ERROR:' + response.reason
	conn.close()
	return via_project_id

def save_json(json_data, filename):
	with open(filename, 'w') as f:
		json.dump( json_data, f, indent=None, separators=(',',':') )

def init_via_project():
	d = {};
	d['project'] = {
		'pid': '__VIA_PROJECT_ID__',
		'rev': '__VIA_PROJECT_REV_ID__',
		'rev_timestamp': '__VIA_PROJECT_REV_TIMESTAMP__',
		'pname': '',
		'data_format_version': '3.1.1',
		'creator': 'VGG Image Annotator (http://www.robots.ox.ac.uk/~vgg/software/via)',
		'created': int(time.time()*1000),
		'vid_list': [],
	};
	d['config'] = {
		'file': {
			'loc_prefix': {
				'1':'',
				'2':'',
				'3':'',
				'4':'',
			},
		},
		'ui': {
			'file_content_align':'center',
			'file_metadata_editor_visible':True,
			'spatial_metadata_editor_visible':True,
			'spatial_region_label_attribute_id':'',
		},
	};
	d['attribute'] = {};
	d['file'] = {};
	d['view'] = {};
	d['metadata'] = {};
	return d


	d = init_via_project()
	## TODO: update "d" such that it contains the VIA3 project

	if False: ## Update this to "if True:" when you are ready to create shared project
		via_project_id = create_via3_shared_project(d)
		if via_project_id.startswith('ERROR'):
			print('Error creating shared project\n')
		else:
			print(via_project_id)
			save_json(d, 'copy-of-shared_project.json'))
