import mysql.connector
import pandas as pd
import numpy as np
import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
)
from llama_index.core.utilities.sql_wrapper import SQLDatabase
from llama_index.indices.struct_store.sql_query import SQLTableRetrieverQueryEngine
from llama_index.indices.vector_store.base import VectorStoreIndex
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from sqlalchemy.engine import URL

from llama_index.llms.litellm import LiteLLM
from litellm import embedding

from tabulate import tabulate

from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface_api import HuggingFaceInferenceAPIEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

GOOGLE_API_KEY = "???"  # add your Google API key here
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

#os.environ["HUGGINGFACE_API_KEY"] = "???"
os.environ["HF_TOKEN"] = "???" # huggingface token

db_user = "root"
db_password = "Password" # Enter your password here
db_host = "localhost"  
db_name = "testgenedata" # name of the database
db_port = "3306" # specify your port here

# needed to be done this way due to special characters in pw
connect_url = URL.create(
    'mysql+mysqldb',
    username=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_name)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Password", # change to correct pw
  database="testgenedata" # change to correct name
)

# Uncomment to select LLM and embedding

# specify Gemini rather than OpenAI
Settings.embed_model = GeminiEmbedding(model='models/text-embedding-004')
#Settings.llm = Gemini(model="models/gemini-2.0-flash-exp")
Settings.llm = Gemini(model="models/gemini-1.5-pro")

#Settings.embed_model = embedding(model='huggingface/mistralai/Mistral-7B-v0.1')
#Settings.llm = LiteLLM(model="huggingface/mistralai/Mistral-7B-v0.1")
#Settings.llm = LiteLLM(model="huggingface/meta-llama/Llama-3.2-1B-Instruct")
# Settings.llm = LiteLLM(model="huggingface/HuggingFaceH4/zephyr-7b-alpha")

#Settings.llm = HuggingFaceInferenceAPI(model_name="meta-llama/Llama-3.3-70B")
#Settings.embed_model = HuggingFaceInferenceAPIEmbedding(model_name="BAAI/bge-small-en-v1.5")

engine = create_engine(connect_url)
metadata_obj = MetaData()
metadata_obj.reflect(engine)

sql_database = SQLDatabase(engine, view_support=True)

table_node_mapping = SQLTableNodeMapping(sql_database)

# context for the various tables
default_context = "This table stores the Spearman's correlation weight between pairs of genes (GeneA and GeneB) in a subcluster of cells from a sample. The first part of the table name indicates the sample."

context = {
    "samples" : "This table lists the patient samples the data came from. OA6 is a patient with osteoarthritis (OA). CN4 is a healthy patient.",
    "ligand_receptor_pairs": "This tables lists pairs of ligand genes and their corresponding receptor genes",
    "transcription_factors": "This table stores a list of transcription factors",
    "cn4": "This table stores the Spearman's correlation weight between pairs of genes (GeneA and GeneB) in all of the cells in the CN4 sample",
    "oa6": "This table stores the Spearman's correlation weight between pairs of genes (GeneA and GeneB) in all of the cells in the OA6 sample",
    "inflammation_genes": "This table stores genes that are related to inflammation"
}

table_schema_objs = []
for table_name in metadata_obj.tables.keys():
    table_schema_objs.append(SQLTableSchema(table_name=table_name, context=context.get(table_name, default_context)))

obj_index = ObjectIndex.from_objects(
    table_schema_objs,
    table_node_mapping,
    VectorStoreIndex,
)

query_engine = SQLTableRetrieverQueryEngine(
    sql_database, obj_index.as_retriever(similarity_top_k=0)
)

query = "What is the schema of all the tables?"
response = query_engine.query(query)
print(query)
print(response)

# Code to print out SQL response as a table
mycursor = mydb.cursor()
print(response.metadata["sql_query"])

mycursor.execute(response.metadata["sql_query"])
results = mycursor.fetchall()
field_names = [i[0] for i in mycursor.description]
print(tabulate(results, headers=field_names, tablefmt='psql'))