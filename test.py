# import pythons libs
import os
import sys
import random
from colorama import Fore, Back, Style
from datetime import date, datetime, timedelta
import requests
import json

# import twilio
from twilio.rest import Client

# import local libraries
from dotenv import load_dotenv
load_dotenv()
TWILIO_ACCOUNT_SID=os.environ.get('ACCOUNT_SID')
TWILIO_AUTH_TOKEN=os.environ.get('AUTH_TOKEN')
import functions as f

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
f.datetime = datetime
f.timedelta = timedelta
f.client = client
f.json = json

import testdata as td

def error_out(msg):
  print(Fore.RED + msg)
  print(Style.RESET_ALL)
  exit()

def print_start(msg):
  print(Fore.WHITE + msg)
  print(Style.RESET_ALL)
  return

def print_success(msg):
  print(Fore.GREEN + msg)
  print(Style.RESET_ALL)
  return

# Test format_tree_data
def test_format_tree_data():
  print_start("Testing format_tree_data")
  executions = [{'sid': 'FN96887eee3139b575f59780f3c59f420a', 'status': 'active', 'steps': 
                 [{'sid': 'FT117e04280c8d0d78afdc9770d5b0bc65', 'execution_sid': 'FN96887eee3139b575f59780f3c59f420a', 
                   'name': 'GET_REPORTING_FILTERS', 'type': 'incomingCall', 'transitioned_to': 'GET_REPORTING_FILTERS', 
                   'transitioned_from': 'Trigger', '@timestamp': datetime(2020, 7, 14, 17, 30, 56), 'variables': 
                     {'gender': 'Other', 'occupation': 'Support', 'favorite_color': 'Admin', 'usage_rating': 'Medium'}, 
                   'searchable': "{'gender': 'Other', 'occupation': 'Support', 'favorite_color': 'Admin', 'usage_rating': 'Medium'}"},
                   {'sid': 'FT6430af37672f70ba0eb8ffef0ce313ee', 'execution_sid': 'FN96887eee3139b575f59780f3c59f420a', 
                   'name': 'ASK_IF_COVID', 'type': 'success', 'transitioned_to': 'ASK_IF_COVID', 'transitioned_from': 
                   'GET_REPORTING_FILTERS', '@timestamp': datetime(2020, 7, 14, 17, 30, 59), 'variables': 
                   {'gender': 'Other', 'occupation': 'Support', 'favorite_color': 'Admin', 'usage_rating': 'Medium'}, 
                   'searchable': "{'gender': 'Other', 'occupation': 'Support', 'favorite_color': 'Admin', 'usage_rating': 'Medium'}"}, 
                   {'sid': 'FT4c9eead07d70145b6b22edaf022a6ecb', 'execution_sid': 'FN96887eee3139b575f59780f3c59f420a', 
                       'name': 'TEST_IF_COVID', 'type': 'keypress', 'transitioned_to': 'TEST_IF_COVID', 'transitioned_from': 'ASK_IF_COVID', 
                       '@timestamp': datetime(2020, 7, 14, 17, 31, 7), 'variables': 
                       {'gender': 'Other', 'occupation': 'Support', 'favorite_color': 'Admin', 'usage_rating': 'Medium'}, 
                       'searchable': "{'gender': 'Other', 'occupation': 'Support', 'favorite_color': 'Admin', 'usage_rating': 'Medium'}"}, 
                   {'sid': 'FTf193e0fd164e4bd19b65a0f33bb3a7b5', 'execution_sid': 'FN96887eee3139b575f59780f3c59f420a', 'name': 'ASK_IF_FEVER', 'type': 'match', 
                       'transitioned_to': 'ASK_IF_FEVER', 'transitioned_from': 'TEST_IF_COVID', '@timestamp': datetime(2020, 7, 14, 17, 31, 7), 
                       'variables': {'gender': 'Other', 'occupation': 'Support', 'favorite_color': 'Admin', 'usage_rating': 'Medium'}, 
                       'searchable': "{'gender': 'Other', 'occupation': 'Support', 'favorite_color': 'Admin', 'usage_rating': 'Medium'}"}]}]
  expected_resp = {'data': [{'id': 'GET_REPORTING_FILTERS.0', 'name': 'GET REPORTING FILTERS', 'parent': '', 'count': 1, 
  'display_name': 'GET REPORTING FILTERS (1) (100%)'}, {'id': 'ASK_IF_COVID.1', 'name': 'ASK IF COVID', 
  'parent': 'GET_REPORTING_FILTERS.0', 'count': 1, 'display_name': 'ASK IF COVID (1) (100%)'}, {'id': 'TEST_IF_COVID.2', 
      'name': 'TEST IF COVID', 'parent': 'ASK_IF_COVID.1', 'count': 1, 'display_name': 'TEST IF COVID (1) (100%)'}]}
  resp = f.format_tree_data(executions)
  if(resp == expected_resp):
    print_success("Passed format_tree_data")
  else:
    error_out("Failed format_tree_data")

if(sys.argv[1].startswith("FW")):
  test_format_tree_data()

# Test format_autopilot_executions
def test_format_autopilot_executions():
  print_start("Testing format_autopilot_executions")
  expected_output = td.autopilot_formatted_executions()
  input = td.autopilot_formatted_queries()
  output = f.format_autopilot_executions(input)
  if(output == expected_output):
    print_success("Passed test_format_autopilot_executions")
  else:
    error_out("Failed test_format_autopilot_executions")

if(sys.argv[1].startswith("UA")):
  test_format_autopilot_executions()

# Ensure Credentials
def check_twilio_credentials():
  print_start("Checking Account SID and Auth Token.")
  if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    return False
  return True

has_creds = check_twilio_credentials()
if has_creds:
  print_success("Account SID and Auth Tokens found.")
else:
  error_out("Account SID and Auth Tokens missing.")

# Test Getting Executions
def test_get_executions(flow_sid):
  print_start("Checking if executions exist in Flow: " + flow_sid)
  try:
    executions = f.get_executions(flow_sid)
    if len(executions) > 0:
      return executions
    return False
  except:
    return False

has_executions = test_get_executions(sys.argv[1])
if has_executions:
  target_execution = random.choice(has_executions)
  print_success("Found executions in flow.")
else:
  error_out("Flow does not have any executions.")

# Test Getting Execution Steps
def test_get_execution_steps(flow_sid, execution_sid):
  print_start("Checking if steps in execution: " + execution_sid)
  try:
    execution_steps = f.get_execution_steps(flow_sid, execution_sid)
    if len(execution_steps) > 0:
      return execution_steps
    return False
  except:
    return False

has_execution_steps = test_get_execution_steps(sys.argv[1], target_execution['sid'])
if has_execution_steps:
  target_execution_step = random.choice(has_execution_steps)
  print_success("Found steps in execution.")
else:
  error_out("Execution does not have any steps.")

# Test Getting Context For Step
def get_execution_step_context(flow_sid, execution_sid, step_sid):
  print_start("Checking for context in step: " + step_sid)
  try:
    execution_step_context = f.get_execution_step_context(flow_sid, execution_sid, step_sid)
    if execution_step_context:
      return execution_step_context
    return False
  except:
    return False

has_execution_step_context = get_execution_step_context(sys.argv[1], target_execution['sid'], target_execution_step['sid'])
if has_execution_steps:
  print_success("Found context in step.")
else:
  error_out("Step does not have any context.")
