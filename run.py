# import pythons libs
import os
import sys
from datetime import date, datetime, timedelta
import requests

# import 3rd party libs
from twilio.rest import Client
from elasticsearch import Elasticsearch

# import local libs
from dotenv import load_dotenv
load_dotenv()
TWILIO_ACCOUNT_SID=os.environ.get('ACCOUNT_SID')
TWILIO_AUTH_TOKEN=os.environ.get('AUTH_TOKEN')
import functions as f
import glob as g

es = Elasticsearch()
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
f.datetime = datetime
f.timedelta = timedelta
f.client = client

def run_5min_import_to_elastic_search(flow_sid):
  start_date = datetime.utcnow() - timedelta(minutes=g.PERIOD_IN_MINUTES)
  end_date = datetime.utcnow() + timedelta(minutes=1)
  print(f"Getting data for period {start_date} to {end_date}")
  # pull all the logs.
  executions = f.get_all_flow_execution_log_details(flow_sid, start_date, end_date)
  # if logs returned, push to elasticsearch
  if len(executions) > 0:
    # create index if not exists
    for execution in executions:
      for step in execution['steps']:
        existing = es.get(index=g.ELASTICSEARCH_INDEX_NAME, id=step['sid'], ignore=[400, 404])
        if not existing.get('found'):
          print(f"Adding execution step to index: {step['sid']}")
          es.index(index=g.ELASTICSEARCH_INDEX_NAME, id=step['sid'], body=step)
    es.index(index=g.ELASTICSEARCH_TREE_INDEX_NAME, id="0", body=f.format_tree_data(executions))
  else:
    print("No execution logs found.")

def init():
  flow_sid = sys.argv[1]
  run_5min_import_to_elastic_search(flow_sid)
  es.indices.create(index=g.ELASTICSEARCH_INDEX_NAME, ignore=400)
  es.indices.create(index=g.ELASTICSEARCH_TREE_INDEX_NAME, ignore=400)
  f.setInterval(g.REFRESH_RATE_IN_SECONDS, run_5min_import_to_elastic_search, flow_sid)

init()

# delete existing index
# es.indices.delete(index=g.ELASTICSEARCH_INDEX_NAME, ignore=[400, 404])
# es.indices.delete(index=g.ELASTICSEARCH_TREE_INDEX_NAME, ignore=[400, 404])
# FW80a732d2352f5e212413f8c46ad4446b
