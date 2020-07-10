# import pythons libs
import os
import sys
from datetime import date, datetime, timedelta
import requests
import json

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

def get_all_flow_execution_log_details(apsid):
  executions = {}
  previous_step_name = ""
  queries = client.autopilot.assistants(apsid).queries.list(limit=500)

  # format all executions.
  for query in queries:
    if not executions.get(query.dialogue_sid):
      executions[query.dialogue_sid] = { "steps": [] }
    if query.results.get('task'):
      executions[query.dialogue_sid]['steps'].append({
        "sid": query.sid,
        "execution_sid": query.dialogue_sid,
        "name": query.results.get('task'),
        "type": query.results.get('task'),
        "transitioned_to": previous_step_name,
        "transitioned_from": "",
        "@timestamp": datetime.strptime(str(query.date_created), '%Y-%m-%d %H:%M:%S+00:00'),
        "date_created": query.date_created.isoformat(),
        "variables": {},
        "searchable": ""
      })
      executions[query.dialogue_sid]['steps'] = sorted(executions[query.dialogue_sid]['steps'], key = lambda i: i['date_created']) 
      previous_step_name = query.results.get('task')

  # add transitioned_from
  for key in executions:
    execution = executions[key]
    previous_step_name = ""
    for step in execution["steps"]:
      step['transitioned_from'] = previous_step_name
      previous_step_name = step['name']
    execution["steps"][-1]["transitioned_to"] = "Ended"
  variables_key = "GET_REPORTING_FILTERS"
  has_variables = False
  previous_step_name = ""
  variables = {}
  for step in execution['steps']:
    if previous_step_name == variables_key:
      has_variables = True
      variables = {**variables.copy(), **json.loads(context[variables_key]['body'])}
    previous_step_name = step["name"]
  # assign variables to all the steps
  if has_variables:
    for step in execution['steps']:
      step['variables'] = variables
      step['searchable'] = str(variables)
  return list(executions.values())

def run_5min_import_to_elastic_search(flow_sid):
  # pull all the logs.
  executions = get_all_flow_execution_log_details(flow_sid)
  # if logs returned, push to elasticsearch
  if len(executions) > 0:
    # create index if not exists
    for execution in executions:
      for step in execution['steps']:
        existing = es.get(index=g.ELASTICSEARCH_AUTOPILOT_INDEX_NAME, id=step['sid'], ignore=[400, 404])
        if not existing.get('found'):
          print(f"Adding execution step to index: {step['sid']}")
          es.index(index=g.ELASTICSEARCH_AUTOPILOT_INDEX_NAME, id=step['sid'], body=step)
    es.index(index=g.ELASTICSEARCH_AUTOPILOT_TREE_INDEX_NAME, id="0", body=f.format_tree_data(executions))
  else:
    print("No execution logs found.")

def init():
  flow_sid = sys.argv[1]
  run_5min_import_to_elastic_search(flow_sid)
  es.indices.create(index=g.ELASTICSEARCH_AUTOPILOT_INDEX_NAME, ignore=400)
  es.indices.create(index=g.ELASTICSEARCH_AUTOPILOT_TREE_INDEX_NAME, ignore=400)
  f.setInterval(g.REFRESH_RATE_IN_SECONDS, run_5min_import_to_elastic_search, flow_sid)

init()

# delete existing index
# es.indices.delete(index=g.ELASTICSEARCH_INDEX_NAME, ignore=[400, 404])
# es.indices.delete(index=g.ELASTICSEARCH_TREE_INDEX_NAME, ignore=[400, 404])
# UA5ef7ed6b3211978dff96c773d25b1d23
