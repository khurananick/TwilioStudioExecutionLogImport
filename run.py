# import pythons libs
import os
import sys
from datetime import date, datetime, timedelta
import requests
import json

# import 3rd party libs
from twilio.rest import Client
from elasticsearch import Elasticsearch
from threading import Thread
from time import sleep

# import local libs
from dotenv import load_dotenv
load_dotenv()
TWILIO_ACCOUNT_SID=os.environ.get('ACCOUNT_SID')
TWILIO_AUTH_TOKEN=os.environ.get('AUTH_TOKEN')

import functions as f

es = Elasticsearch()
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
f.datetime = datetime
f.timedelta = timedelta
f.client = client
f.json = json

ELASTICSEARCH_INDEX_NAME            = "studio_execution_logs"
ELASTICSEARCH_TREE_INDEX_NAME       = "studio_execution_logs_tree"
ELASTICSEARCH_TREE_LIVE_INDEX_NAME  = "studio_execution_logs_tree_live"
PERIOD_IN_MINUTES                   = 5 # (60*24*15) # 15 days
REFRESH_RATE_IN_SECONDS             = 15

def call_at_interval(period, callback, args):
  while True:
    sleep(period)
    callback(*args)

def setInterval(period, callback, *args):
  Thread(target=call_at_interval, args=(period, callback, args)).start()

def run_5min_import_to_elastic_search(flow_sid):
  start_date = datetime.utcnow() - timedelta(minutes=PERIOD_IN_MINUTES)
  end_date = datetime.utcnow() + timedelta(minutes=1)
  print(f"Getting data for period {start_date} to {end_date}")
  # pull all the logs.
  executions = f.get_all_flow_execution_log_details(flow_sid, start_date, end_date)
  # if logs returned, push to elasticsearch
  if len(executions) > 0:
    # create index if not exists
    es.indices.create(index=ELASTICSEARCH_INDEX_NAME, ignore=400)
    es.indices.create(index=ELASTICSEARCH_TREE_INDEX_NAME, ignore=400)
    for execution in executions:
      for step in execution['steps']:
        existing = es.get(index=ELASTICSEARCH_INDEX_NAME, id=step['sid'], ignore=[400, 404])
        if not existing['found']:
          print(f"Adding execution step to index: {step['sid']}")
          es.index(index=ELASTICSEARCH_INDEX_NAME, id=step['sid'], body=step)
    es.index(index=ELASTICSEARCH_TREE_INDEX_NAME, id="0", body=f.format_tree_data(executions))
  else:
    print("No execution logs found.")

def init():
  flow_sid = sys.argv[1]
  run_5min_import_to_elastic_search(flow_sid)
  setInterval(REFRESH_RATE_IN_SECONDS, run_5min_import_to_elastic_search, flow_sid)

init()

# delete existing index
# es.indices.delete(index=ELASTICSEARCH_INDEX_NAME, ignore=[400, 404])
# es.indices.delete(index=ELASTICSEARCH_TREE_INDEX_NAME, ignore=[400, 404])
