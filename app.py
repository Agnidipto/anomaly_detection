import re
from pprint import pprint
from datetime import datetime, timedelta
import requests

LAST_CHECKED_TIME = datetime.now() - timedelta(minutes=10)
NUMBER_OF_LOGS_BEFORE_ERROR = 5

def extract_timestamp(log_line) -> datetime:
  match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3}', log_line)
  if match:
    timestamp_str = match.group(1)
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
  return None

def upload_log_file(file_path, url="http://localhost:8000/debug"):
  # Open file in binary mode
  with open(file_path, "rb") as file:
    # Create multipart form-data with the file
    files = {"file": (file.name, file, "text/plain")}
    
    # Send POST request
    response = requests.post(url, files=files)
      
    # Check response status first
    if response.status_code != 200:
      print(f"Error: Server returned status code {response.status_code}")
      print(f"Response content: {response.text}")
      return None
        
    # Try to parse JSON, handle failures
    try:
      return response.json()
    except requests.exceptions.JSONDecodeError:
      print(f"Couldn't parse JSON response. Raw response: {response.text}")
      return response.text

def main() :

  file = open(r'C:/Work Modules/UIC_US/MS/EEDL/Project/code/logs', 'r')
  log_lines = file.read().split('\n')
  file.close()

  timestamp_lines = []
  date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}')

  for line in log_lines:
    if date_pattern.match(line):
      timestamp_lines.append(line)
    elif timestamp_lines:
      timestamp_lines[-1] += '\n' + line

  n = len(timestamp_lines)
  first_error = -1

  for i in reversed(range(n)) :
    line = timestamp_lines[i]
    log_time = extract_timestamp(line)

    if log_time<LAST_CHECKED_TIME: 
      break
    
    date, time, level, content = line.split(' ', maxsplit=3)
    if level == 'ERROR' : first_error = i
  
  if first_error != -1 :
    print('Error found')
    first_error = max(0, first_error-NUMBER_OF_LOGS_BEFORE_ERROR)
    error_logs = '\n'.join(timestamp_lines[first_error:])

    output_file = open(r'parsed_logs.txt', 'w')
    output_file.write(error_logs)
    output_file.close()
    
    print(f'Sending post request')
    upload_log_file(file_path=r'parsed_logs.txt')
  
if __name__ == '__main__' :
  main()
       