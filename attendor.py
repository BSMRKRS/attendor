### Definition of default schedules
###################################

block_schedule = {'8:02': 'class-kirwin-e3','9:27': 'class-kirwin-e1', '10:52': 'apcs', '8:01': 'class-dougherty-e2', '13:11': 'class-dougherty-e1'}
no_schedule = {}
channels = {'class-kirwin-e1': 'class-kirwin-e1', 'class-kirwin-e2': 'class-kirwin-e2', 'class-kirwin-e3': 'class-kirwin-e3', 'apcs': 'classroom-management', 'class-dougherty-e1': 'class-dougherty-e1', 'class-dougherty-e2': 'class-dougherty-e2'}
endpoints = {'class-kirwin-e3': 'https://hooks.slack.com/services/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', 'class-kirwin-e1': 'https://hooks.slack.com/services/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', 'class-kirwin-e2': 'https://hooks.slack.com/services/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', 'class-dougherty-e1': 'https://hooks.slack.com/services/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', 'class-dougherty-e2': 'https://hooks.slack.com/services/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', 'apcs': 'https://hooks.slack.com/services/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'}
bsm_robotics_user_token = 'xoxb-312023469652-1452572658102-WsoUjPoGQaptjvkm6OkHVxw4'
bsm_apcs_user_token = 'xoxb-1151662380019-1457315696387-wPPEWx6vaTuOTN9s7UAV40KU'
tokens = {'class-kirwin-e1': bsm_robotics_user_token, 'class-kirwin-e2': bsm_robotics_user_token, 'class-kirwin-e3': bsm_robotics_user_token, 'apcs': bsm_apcs_user_token}

### Logic
#########

import datetime
import requests

def check_for_notification_time(dt, t, schedule):
  secs = dt.hour * 3600 + dt.minute * 60 + dt.second
  current = datetime.datetime.now()
  diff = secs - (current.hour * 3600 + current.minute * 60 + current.second)
  print('notify: ' + t + ' ' + str(diff))  
  if(diff < 10 and diff >= 0):
    print("Posting...")
    dest = endpoints.get(schedule.get(t))
    msg = "<!channel> Attendance! (Automatically posted by KirwinAttendanceBot) -- " + message_key(dt, t, schedule)
    post_attendance_message(dest, msg)
    return(1)

def message_key(dt, t, schedule):
  return("-".join([schedule.get(t), str(dt.year), str(dt.month), str(dt.day), t]))

def post_attendance_message(dest, msg = "<!channel> Attendance (Automatically Posted by Kirwin's AttendanceBot)!"):
  requests.post(dest, json={"text":msg}, headers={'Content-type': 'application/json'})

def check_for_check_time(dt, t, schedule):
  secs = dt.hour * 3600 + dt.minute * 60 + dt.second
  current = datetime.datetime.now()
  diff = secs - (current.hour * 3600 + current.minute * 60 + current.second)
  print('check: ' + t + ' ' + str(diff))  
  if((diff < -3600 and diff >= -3610) or (diff < -1800 and diff >= -1810)):
    print("Checking...")
    check_attendance(t, schedule)
    return(1)

def check_attendance(t, schedule):
  token = tokens.get(schedule.get(t))
  channel = get_channel_id(token, channels.get(schedule.get(t)))
  master_attendance = get_reactions(get_master_attendance_message(token, channel, t))
  print(master_attendance)
  daily_attendance = get_reactions(get_daily_attendance_message(token, channel, t))
  print(daily_attendance)
  
  missing = []
  for u in master_attendance:
    if u in daily_attendance:
      pass
    else:
      missing.append(u)
  print(missing)
  if len(missing) > 0:
    msg = "Checked " + str(len(master_attendance)) + " students. Please check the attendance! " + " ".join(list(map(lambda u: "<@" + u + ">", missing)))
  else:
    msg = "Attendance looks good for all " + str(len(master_attendance)) + " students!"
  post_attendance_message(endpoints.get(schedule.get(t)), msg)

def get_channel_id(token, channel_name):
  url = 'https://slack.com/api/conversations.list?token=' + token
  resp = requests.get(url)
  if 'channels' in resp.json().keys():
    channels = resp.json()['channels']
    channel = list(filter(lambda ch: ch['name'] == channel_name, channels))[0]['id']
  else:
    print(resp.json())
    channel = 'Not-Found'
  return(channel)

def get_master_attendance_message(token, channel, t):
  url = 'https://slack.com/api/pins.list?token=' + token + '&channel=' + channel
  resp = requests.get(url)
  if('items' in resp.json().keys()):
    msgs = resp.json()['items']
    msg = list(filter(lambda m: t in m['message']['text'], msgs))[0]['message']
  else:
    print(resp.json())
    msg = {}
  return(msg)

def get_daily_attendance_message(token, channel, t):
  dt = update_dt(t)
  minute_before = dt.timestamp() - 60
  minute_after = dt.timestamp() + 60
  url = 'https://slack.com/api/conversations.history?token=' + token + '&channel=' + channel + '&oldest=' + str(minute_before) + '&latest=' + str(minute_after)
  resp = requests.get(url)
  if('messages' in resp.json().keys()):
    msgs = resp.json()['messages']
    msg = list(filter(lambda m: t in m['text'], msgs))[0]
  else:
    print(resp.json())
    msg = {}
  return(msg)

def get_reactions(message, emoji = '+1'):
  if 'reactions' in message.keys():
    reactions = message['reactions']
    present_potentials = list(filter(lambda rxn: rxn['name'] == emoji, reactions))
    if len(present_potentials) > 0:
      present = present_potentials[0]['users']
    else:
      present = []
  else:
    present = []
  return(present)

def check_schedule():
  schedule = determine_schedule()
  for t in schedule.keys():
    notification_time = update_dt(t)

    check_for_notification_time(notification_time, t, schedule)
    check_for_check_time(notification_time, t, schedule)
  return(1)

def update_dt(t):
    dt = datetime.datetime.now()
    return(dt.replace(hour=int(t.split(':')[0]), minute=int(t.split(':')[1]), second=0))

def default_schedule():
  return [block_schedule, block_schedule, block_schedule, block_schedule, block_schedule, no_schedule, no_schedule][datetime.datetime.today().weekday()]

def determine_schedule():
  #f = open('/home/pi/warning_bell/schedule.txt','r')
  schedule_command = 'auto'#f.read().strip()
  if ':' in schedule_command:
    schedule = schedule_command.split(',')
  elif schedule_command == 'auto':
    schedule = default_schedule()
  else:
    schedule = {'regular': regular_schedule, 'block': block_schedule, 'event_block': event_block_schedule, 'late_block': late_block_schedule, 'none': no_schedule}[schedule_command]
  #f.close()
  return schedule
