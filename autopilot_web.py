from flask import Flask, request, jsonify
from datetime import date, datetime, timedelta
import threading

from elasticsearch import Elasticsearch
es = Elasticsearch()

import glob as g

app = Flask(__name__)
arr = []

@app.route('/autopilot/event', methods=['POST'])
def example():
  data = request.form
  if data.get("Event") == "onDialogueTaskEnd":
    event = {
      "sid": data.get('Sid'),
      "execution_sid": data.get('DialogueSid'),
      "name": data.get('CurrentTask'),
      "@timestamp": datetime.utcnow(),
    }
    es.index(index=g.ELASTICSEARCH_AUTOPILOT_INDEX_NAME, id=event['sid'], body=event)
  return jsonify({"success": True})

es.indices.create(index=g.ELASTICSEARCH_AUTOPILOT_INDEX_NAME, ignore=400)
app.run()

# def run():
#   threading.Thread(target=app.run).start()

