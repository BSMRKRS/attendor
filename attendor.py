### Definition of default schedules
###################################

block_schedule = {'8:02': 'class-kirwin-e3','9:27': 'class-kirwin-e1', '10:52': 'apcs', '8:01': 'class-dougherty-e2', '13:11': 'class-dougherty-e1'}
no_schedule = {}
endpoints = {'class-kirwin-e3': 'https://hooks.slack.com/services/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', 'class-kirwin-e1': 'https://hooks.slack.com/services/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', 'class-kirwin-e2': 'https://hooks.slack.com/services/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', 'class-dougherty-e1': 'https://hooks.slack.com/services/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', 'class-dougherty-e2': 'https://hooks.slack.com/services/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', 'apcs': 'https://hooks.slack.com/services/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'}
bsm_robotics_user_token = 'xoxp-312023469652-312023469780-1455886460310-f9f818cbc0951b7591cb431dbe72729b'
bsm_apcs_user_token = 'xoxp-1151662380019-1151453665074-1463172420290-3740645fe6f74764685d12a8d8bb83a2'
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
    check_attendance(dt, t, schedule)
    return(1)

def check_attendance(dt, t, schedule):
  token = tokens.get(schedule.get(t))
  master_attendance = get_reactions(token, 'master-attendance-' + schedule.get(t) + '-' + t)
  daily_attendance = get_reactions(token, message_key(dt, t, schedule))
  
  missing = []
  for u in master_attendance:
    if u in daily_attendance:
      pass
    else:
      missing.append(u)
  if len(missing) > 0:
    msg = "Checked " + str(len(master_attendance)) + " students. Please check the attendance! " + " ".join(list(map(lambda u: "<@" + u + ">", missing)))
  else:
    msg = "Attendance looks good for all " + str(len(master_attendance)) + " students!"
  post_attendance_message(endpoints.get(schedule.get(t)), msg)

def get_reactions(token, query, emoji = '+1'):
  url = 'https://slack.com/api/search.messages?token=' + token + '&query=' + query
  resp = requests.get(url)
  channel_id = resp.json()['messages']['matches'][0]['channel']['id']
  message_ts = resp.json()['messages']['matches'][0]['ts']
  url = 'https://slack.com/api/reactions.get?token=' + token + '&timestamp=' + message_ts + '&channel=' + channel_id
  resp = requests.get(url)
  message = resp.json()['message']
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
    notification_time = datetime.datetime.now()
    notification_time = notification_time.replace(hour=int(t.split(':')[0]), minute=int(t.split(':')[1]), second=0)

    check_for_notification_time(notification_time, t, schedule)
    check_for_check_time(notification_time, t, schedule)
  return(1)

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
