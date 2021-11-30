"""
filename : utils.py

This script holds the common functions used in project.
"""

from modzy import ApiClient
import streamlit as st
import json
import re
import lxml.html as LH
from pyquery import PyQuery
import base64
import uuid
import re

colors = ['#7aecec', '#aa9cfc', '#feca74', '#bfe1d9', '#c887fb', '#e4e7d2', 
			'#905829', '#dfcd62', '#e8d53d', '#f0c88b', '#b68282', '#799fb2', 
			'#c3b489', '#bf9a81', '#a592ae', '#e5aef9', '#f69419', '#a36b42', 
			'#e5c3a6', '#4fc6b4', '#d9e69a', '#f76b6b', '#e8d53d', '#61c861', 
			'#65a4d9', '#b8ff57', '#779987', '#f69419']

def header():
	"""
	Header to display in all page.
	"""
	st.markdown("""<h1 style='text-align: center; color: black;'><a id="top">Seshat</a></h1>""", unsafe_allow_html=True)

def load_config():
	"""
	Function to load configurations
	"""
	with open('config.json') as f:
		return json.load(f)

@st.cache(allow_output_mutation=True)
def get_client():
	"""
	Function to get modzy client
	"""

	config = load_config()

	if not config["API_URL"] and config["API_KEY"]:
		st.error("Please update config.json file with valid credentials...")
	else:
		try:
			client = ApiClient(base_url= config["API_URL"], api_key= config["API_KEY"])
		except:
			st.error("Coudn't connect to Modzy server, please verify credentials...")

	return client

@st.cache
def get_model(client, model_name):
	"""
	Function to load model based on name
	Args:
		client: modzy client object
		model_name: model name to load
	"""

	model = client.models.get_by_name(model_name)
	modelVersion = client.models.get_version(model, model.latest_version)

	return model, modelVersion.version

@st.cache
def get_model_output(client, model_identifier, model_version, data_sources, explain=False):
	"""
	Args:
		client: modzy client object
		model_identifier: model identifier (string)
		model_version: model version (string)
		data_sources: dictionary with the appropriate filename --> local file key-value pairs
		explain: boolean variable, defaults to False. If true, model will return explainable result
	"""
	client = get_client()
	job = client.jobs.submit_text(model_identifier, model_version, data_sources, explain)
	result = client.results.block_until_complete(job, timeout=None)
	model_output = result.get_first_outputs()['results.json']

	return model_output

@st.cache
def beautify_tags(tags):
	"""
	Function to beautify tags result
	
	Args:
		tags: list of tags
	"""

	div = '<div class="entities" style="line-height: 2.5; direction: ltr">'
	mark = '<mark class="entity" style="background:{}; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">{}\n<span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; text-transform: uppercase; vertical-align: middle; margin-left: 0.5rem"></span></mark>'
	
	html = ""+div

	for i in range(len(tags[:5])):
		html += mark.format("#F63366", tags[i])
	html += '</div>'

	html += div

	for i in range(5, len(tags)):
		html += mark.format("#F63366", tags[i])
	html += '</div>'
	
	return html

@st.cache
def beautify_html(html: str, title=False, title_string=""):
	"""
	Function to display border around corpus and result in visualisations. 
	Args:
		html: html string to beautify
		title: bool
		title_string: string that appears as header
	"""
    
	if title:
		WRAPPER = """<div style="border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem"><header><h3 style="text-decoration: underline;">{}<h3></header>{}</div>"""
		html = html.replace("\n", " ")
		return WRAPPER.format(title_string,html)
	else:
		WRAPPER = """<div style="border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""
		html = html.replace("\n", " ")
		return WRAPPER.format(html)


@st.cache
def beautify_entities(response):
	"""
	Function to beautify entities result
	Args:
		response: entity response from Modzy
	"""

	unique_entities = list(set([tag[1] for tag in response]))

	entity_color = dict()
 
	for i in range(len(unique_entities)):
		entity_color[unique_entities[i]] = colors[i]

	div1 = '<div class="entities" style="line-height: 2.5; direction: ltr">'
	mark1 = '<mark class="entity" style="background:' 
	mark2 = '; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">'
	sp1 = '<span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; text-transform: uppercase; vertical-align: middle; margin-left: 0.5rem">'
	e1 = '</span></mark>'
		
	html = ""
	html += div1

	for i in range(len(response)):
		if response[i][1] == "O":
			html += response[i][0]+" "
		else:
			html += mark1 + entity_color[response[i][1]] + mark2+ response[i][0]+ sp1 + response[i][1] + e1
			
	html += '</div>'

	return html

def show_corpus(corpus):
	"""
	Function to display corpus
	Args:
		corpus: corpus para
	"""

	div = '<div class="entities" style="line-height: 2.5; font-weight: bold; direction: ltr">'+corpus+'</div>'
	style = "<style>mark.entity { display: inline-block }</style>"
	st.write(f"{style}{beautify_html(div)}", unsafe_allow_html=True)

	return div

@st.cache
def mask_entities(response, entities_html, unique_entities):
	"""
	Function to mask entities.
	Args:
		response: entity respose from modzy
		entities_html: html string of entity
		unique_entities: list of unique entities
	"""

	unique_entities = list(set([tag[1] for tag in response]))

	entity_color = dict()
 
	for i in range(len(unique_entities)):
		entity_color[unique_entities[i]] = colors[i]

	root = LH.fromstring(entities_html)
	for entity in unique_entities:
		elements = root.xpath('//{}'.format('mark'))
		for e in elements:
			pq = PyQuery(e)
			entity2 = pq('span')
			if entity2.text() == entity:
				e.attrib['color'] = entity_color[entity]

	for entity in unique_entities:
		for i in range(len(response)):
			if response[i][1] != "O":
				replace_with = response[i][0]+"_"+response[i][0]
				try:
					root = LH.tostring(root).decode("utf-8").replace(replace_with,entity_color[entity]+'"')
				except:
					root = root.replace(replace_with,entity_color[entity]+'"')

		try:
			root = LH.tostring(root).decode("utf-8").replace(';" color='+'"'+entity_color[entity]+'"','; color:'+entity_color[entity]+'"')
		except:
			root = root.replace(';" color='+'"'+entity_color[entity]+'"','; color:'+entity_color[entity]+'"')
	
	return root

def download_file(object_to_download,name):
	"""
	Function to download visualized result to as a .pdf file.
	Args:
		object_to_download: object/var to download
		name: name to give to downloaded file
	"""
	try:
		b64 = base64.b64encode(object_to_download.encode()).decode()

	except AttributeError as e:
		b64 = base64.b64encode(object_to_download).decode()

	button_text = 'Save Result'
	button_uuid = str(uuid.uuid4()).replace('-', '')
	button_id = re.sub('\d+', '', button_uuid)

	custom_css = f""" 
		<style>
			#{button_id} {{
				background-color: rgb(255, 255, 255);
				color: rgb(38, 39, 48);
				padding: 0.25em 0.38em;
				position: relative;
				text-decoration: none;
				border-radius: 4px;
				border-width: 1px;
				border-style: solid;
				border-color: rgb(230, 234, 241);
				border-image: initial;
			}} 
			#{button_id}:hover {{
				border-color: rgb(246, 51, 102);
				color: rgb(246, 51, 102);
			}}
			#{button_id}:active {{
				box-shadow: none;
				background-color: rgb(246, 51, 102);
				color: white;
				}}
		</style> """

	dl_link = custom_css + f'<a download="{name}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

	return dl_link
