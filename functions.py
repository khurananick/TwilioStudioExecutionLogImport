def format_execution(execution):
  return {
    "sid": execution.sid,
    "status": execution.status,
    "steps": []
  }

def format_step(step):
  return {
    "sid": step.sid,
    "execution_sid": step.execution_sid,
    "name": step.transitioned_to,
    "type": step.name,
    "transitioned_to": step.transitioned_to,
    "transitioned_from": step.transitioned_from,
    "@timestamp": datetime.strptime(str(step.date_created), '%Y-%m-%d %H:%M:%S+00:00'),
    "context": {}
  }

def percent_str(num, den):
  pct = round((num/den) * 100)
  return f"{pct}%"

def format_tree_data(executions):
  # put all step transitions into multidimentional array
  arr = []
  longest = 0
  for execution in executions:
    narr = []
    for step in execution['steps']:
      if step['transitioned_from'] !='Trigger':
        narr.append(step['transitioned_from'])
    if len(narr) > longest:
      longest = len(narr)
    narr = list(dict.fromkeys(narr))
    arr.append(narr)
  # adds index to each item
  for narr in arr:
    i = 0
    for step in narr:
      narr[i] = f"{step}.{i}"
      i+=1
  # format into steps
  data = {}
  fkey = ""
  for narr in arr:
    i = 0
    for step in narr:
      if not fkey:
        fkey = step
      if not data.get(step):
        parent = narr[i-1] if i > 0 else ""
        data[step] = {
          "id": step,
          "name": step.split(".")[0].replace('_', ' '),
          "parent": parent,
          "count": 0
        }
      data[step]['count'] += 1
      i += 1
  # add %s
  for step in data:
    data[step]['display_name'] = f"{data[step]['name']} ({data[step]['count']}) ({percent_str(data[step]['count'], data[fkey]['count'])})"
  # convert data hash to list
  data = list(data.values())
  return { "data":  data }

def get_executions(flow_sid, start_date=None, end_date=None):
  if not start_date:
    start_date = datetime.now() - timedelta(days=1)
  if not end_date:
    end_date = datetime.now() + timedelta(days=1)
  arr = []
  executions = client.studio.v1.flows(flow_sid).executions.list(
                 date_created_from=start_date,
                 date_created_to=end_date,
                 limit=20
               )
  for execution in executions:
    arr.append(format_execution(execution))
  return arr

def get_execution(flow_sid, execution_sid):
  execution = client.studio.v1.flows(flow_sid).executions(execution_sid).fetch()
  return format_execution(execution)

def get_execution_steps(flow_sid, execution_sid):
  arr = []
  steps = client.studio.v1 \
    .flows(flow_sid) \
    .executions(execution_sid) \
    .steps.list()
  for step in steps:
    arr.append(format_step(step))
  arr.reverse()
  return arr

def get_execution_step_context(flow_sid, execution_sid, step_sid):
  context = client.studio.v1 \
    .flows(flow_sid) \
    .executions(execution_sid) \
    .steps(step_sid) \
    .step_context() \
    .fetch()
  return context.context['widgets']

def get_all_flow_execution_log_details(flow_sid, start_date=None, end_date=None):
  executions = get_executions(flow_sid, start_date, end_date)
  for execution in executions:
    execution['steps'] = get_execution_steps(flow_sid, execution['sid'])
    # for step in execution['steps']:
      # step['context'] = get_execution_step_context(flow_sid, execution['sid'], step['sid'])
  return executions

