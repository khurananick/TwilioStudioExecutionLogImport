import random, datetime, string, os, binascii, secrets
import functions as f
import glob as g

from elasticsearch import Elasticsearch
es = Elasticsearch()

# Keep "Trigger" and "Ended" items, but you can change all the stuff in the middle if needed.
routes = [
  ["Trigger", "ASK_IF_COVID", "TEST_IF_COVID", "ASK_IF_FEVER", "TEST_IF_FEVER", "SAY_CONNECTING_TO_COVID_RESPONSE_TEAM", "SEND_TO_COVID_RESPONSE_TEAM", "Ended"],
  ["Trigger", "ASK_IF_COVID", "TEST_IF_COVID", "SAY_FORWARDING_TO_NURSE", "FORWARD_TO_NURSE_LINE", "Ended"],
  ["Trigger", "ASK_IF_COVID", "TEST_IF_COVID", "ASK_IF_FEVER", "TEST_IF_FEVER", "SAY_FORWARDING_TO_NURSE", "FORWARD_TO_NURSE_LINE", "Ended"]
]

# Feel free to add more personas.
def get_random_persona():
  return {
    "gender":         random.choice(["Male", "Female", "Other"]),
    "occupation":     random.choice(["Developer", "Support", "Admin"]),
    "favorite_color": random.choice(["Red", "Green", "Blue"]),
    "usage_rating":   random.choice(["High", "Low", "Medium"]),
    "age":            random.choice(range(23,85))
  }

executions = []
def create_random_execution():
  execution_sid = secrets.token_hex(15)
  execution = { "sid": execution_sid, "status": "finished", "steps": [] }
  route = random.choice(routes)
  persona = get_random_persona()
  arrlen = len(route)
  for i in range(arrlen):
    step_name = route[i]
    sid = secrets.token_hex(15)
    t = datetime.datetime.utcnow()
    t2 = t + datetime.timedelta(seconds=i)
    step = {
      "sid": sid,
      "execution_sid": execution_sid,
      "name": step_name,
      "type": "type",
      "@timestamp": datetime.datetime.strptime(t2.strftime('%Y-%m-%d %H:%M:%S+00:00'), '%Y-%m-%d %H:%M:%S+00:00'),
      "searchable": persona,
      "variables": persona,
      "searchable": str(persona)
    }
    if(i == 0):
      step["transitioned_from"] = ""
    else:
      step["transitioned_from"] = route[i-1]

    if(i == (arrlen-1)):
      step["transitioned_to"] = ""
    else:
      step["transitioned_to"] = route[i+1]
    print(step)
    execution["steps"].append(step)
    es.index(index=g.ELASTICSEARCH_INDEX_NAME, id=sid, body=step)
  executions.append(execution)
  es.index(index=g.ELASTICSEARCH_TREE_INDEX_NAME, id="0", body=f.format_tree_data(executions))

def init():
  es.indices.create(index=g.ELASTICSEARCH_INDEX_NAME, ignore=400)
  es.indices.create(index=g.ELASTICSEARCH_TREE_INDEX_NAME, ignore=400)
  create_random_execution()
  f.setInterval(g.FAKER_REFRESH_RATE_IN_SECONDS, create_random_execution)

init()
