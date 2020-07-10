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

def error_out(msg):
  print(Fore.RED + msg)
  print(Style.RESET_ALL)
  exit()

def print_start(msg):
  print(Fore.WHITE + msg)
  return

def print_success(msg):
  print(Fore.GREEN + msg)
  print(Style.RESET_ALL)
  return


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

