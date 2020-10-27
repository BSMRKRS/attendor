### Definition of default schedules
###################################

block_schedule = {'8:02': 'class-kirwin-e3','9:27': 'class-kirwin-e1', '10:52': 'apcs', '8:01': 'class-dougherty-e2', '13:01': 'class-dougherty-e1'}
no_schedule = {}
endpoints = {'class-kirwin-e3': 'https://hooks.slack.com/services/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', 'class-kirwin-e1': 'https://hooks.slack.com/services/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', 'class-kirwin-e2': 'https://hooks.slack.com/services/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', 'class-dougherty-e1': 'https://hooks.slack.com/services/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', 'class-dougherty-e2': 'https://hooks.slack.com/services/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', 'apcs': 'https://hooks.slack.com/services/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'}

### Below this is the code, which doesn't need to be touched.
#############################################################

import time
import datetime
import requests

def check_for_notification_time(dt, dest):
  secs = dt.hour * 3600 + dt.minute * 60 + dt.second
  current = datetime.datetime.now()
  diff = secs - (current.hour * 3600 + current.minute * 60 + current.second)
  print(diff)
  if(diff < 10 and diff > 0):
    print("Posting")
    post_attendance_message(dest)
    return(1)

def post_attendance_message(dest, msg = "<!channel> Attendance (Automatically Posted by Kirwin's AttendanceBot)!"):
  print(endpoints)
  print(dest)
  requests.post(dest, json={"text":msg}, headers={'Content-type': 'application/json'})

def check_schedule():
  schedule = determine_schedule()
  for t in schedule.keys():
    dt = datetime.datetime.now()
    dt = dt.replace(hour=int(t.split(':')[0]), minute=int(t.split(':')[1]), second=0)
    check_for_notification_time(dt, endpoints.get(schedule.get(t)))
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

while True:
  check_schedule()
  time.sleep(10)
