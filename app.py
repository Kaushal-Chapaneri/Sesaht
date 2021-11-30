"""
filename : app.py

This script holds the code of input processing, generating results and displaying past results.
"""

import streamlit as st
from weasyprint import HTML
import uuid
from datetime import datetime

from utils import *

from db_operations import *

def generate_text_results(client):
    """
	Function takes user input and generate different analysis

    Args:
		client: modzy client object
    """
        
    input_text = st.text_area('Enter corpus',height=150)

    data = dict()
    key = str(uuid.uuid1())

    data["key"] = key
    data["timestamp"] = str(datetime.now())

    if input_text:

        data["corpus"] = input_text

        st.write("")

        st.markdown("""<h3 style='text-align: left; color: black;'><a id="top">Corpus</a></h3>""", unsafe_allow_html=True)

        # displaying input corpus
        corpus = show_corpus(input_text)

        corpus = beautify_html(corpus, title=True, title_string="Corpus")

        # running topic modelling on input corpus
        model, model_vesrion = get_model(client, "Text Topic Modeling")

        sources = {"source-key": {"input.txt": input_text}}

        response = get_model_output(client, model.modelId,model_vesrion, sources, explain=False)

        data["tag_response"] = response

        html_tags = beautify_html(beautify_tags(response), title=True, title_string="Tags")

        st.write("")

        st.markdown(html_tags, unsafe_allow_html=True)

        # running text summarization on input corpus
        model, model_vesrion = get_model(client, "Text Summarization")

        response = get_model_output(client, model.modelId,model_vesrion, sources, explain=False)

        data["summary_response"] = response["summary"]

        html_summary = beautify_html(response["summary"], title=True, title_string="Summary")

        st.write("")
        
        st.markdown(html_summary, unsafe_allow_html=True)

        # running NER on input corpus
        model, model_vesrion = get_model(client, "Named Entity Recognition")

        response = get_model_output(client, "a92fc413b5", "0.0.12", sources, explain=False)

        data["entity_response"] = response

        unique_entities = list(set([tag[1] for tag in response]))

        st.write("")

        entities_html =  beautify_entities(response)

        st.markdown(beautify_html(entities_html, title=True, title_string="Entities"), unsafe_allow_html=True)

        pdfile = HTML(string=corpus+html_tags+html_summary+beautify_html(entities_html, title=True, title_string="Entities")).write_pdf()
        download_button_str = download_file(pdfile, 'corpus_tags_summary_entities.pdf')
        st.markdown(download_button_str, unsafe_allow_html=True)

        st.write("")

        # generating masked entities 
        hidden_entities_html = beautify_html(mask_entities(response, entities_html, unique_entities), title=True, title_string="Hidden Entities")

        st.write("")

        st.markdown(hidden_entities_html, unsafe_allow_html=True)

        pdfile = HTML(string=hidden_entities_html).write_pdf()
        download_button_str = download_file(pdfile, 'corpus_hidden_entities.pdf')
        st.markdown(download_button_str, unsafe_allow_html=True)

        # storing all API results in db
        store_in_db(data)


def display_stored_results():
    """
	Function fetches all the past results generated from mongodb
    """

    records = list(fetch_from_db())

    records_time = ["Result of "+record["timestamp"] for record in records]

    record_list = st.selectbox("Select a record",
                            records_time)

    record_time = record_list.split("Result of ")[1]

    data = [record for record in records if record["timestamp"]==record_time][0]

    # displaying corpus
    st.write("")
    st.markdown("""<h3 style='text-align: left; color: black;'><a id="top">Corpus</a></h3>""", unsafe_allow_html=True)
    corpus = show_corpus(data["corpus"])
    corpus = beautify_html(corpus, title=True, title_string="Corpus")

    # displaying tag response
    html_tags = beautify_html(beautify_tags(data["tag_response"]), title=True, title_string="Tags")
    st.write("")
    st.markdown(html_tags, unsafe_allow_html=True)

    # displaying summary response
    html_summary = beautify_html(data["summary_response"], title=True, title_string="Summary")
    st.write("")    
    st.markdown(html_summary, unsafe_allow_html=True)

    # displaying entity response
    st.write("")
    entities_html =  beautify_entities(data["entity_response"])
    st.markdown(beautify_html(entities_html, title=True, title_string="Entities"), unsafe_allow_html=True)

    # downloading results as pdf
    pdfile = HTML(string=corpus+html_tags+html_summary+beautify_html(entities_html, title=True, title_string="Entities")).write_pdf()
    download_button_str = download_file(pdfile, 'corpus_tags_summary_entities.pdf')
    st.markdown(download_button_str, unsafe_allow_html=True)

    # displaying hidden entities 
    unique_entities = list(set([tag[1] for tag in data["entity_response"]]))
    hidden_entities_html = beautify_html(mask_entities(data["entity_response"], entities_html, unique_entities), title=True, title_string="Hidden Entities")
    st.write("")
    st.markdown(hidden_entities_html, unsafe_allow_html=True)

    # downloading pdf of hidden entities
    pdfile = HTML(string=hidden_entities_html).write_pdf()
    download_button_str = download_file(pdfile, 'corpus_hidden_entities.pdf')
    st.markdown(download_button_str, unsafe_allow_html=True)