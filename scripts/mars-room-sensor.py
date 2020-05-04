import requests
import configparser
import time
import logging

from logging.handlers import RotatingFileHandler

sensor_config = configparser.ConfigParser()
mars_config = configparser.ConfigParser()

sensor_config.read('/mars/mars-sensor.ini')
mars_config.read('/mars/scripts/mars.ini')

# === Read MARS configuration ===
cloudRetryTimes = int(mars_config['mars']['post_retry_times'])
sleep_interval = int(mars_config['mars']['post_interval'])
sensor_on_last_time = int(mars_config['mars']['sensor_on_last_time'])
sensor_interval = 10

# === Read sensor configuration ===
sensor_room_list = sensor_config['sensor']['sensor_id'].split(';')

room_availability = {}

sensor_status = {}

# === Init logger ===
logger = logging.getLogger("MARS")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)    

# add a rotating handler
handler = RotatingFileHandler(mars_config['logger']['log_file'], maxBytes=int(mars_config['logger']['file_size']), backupCount=int(mars_config['logger']['backup_count']))
handler.setFormatter(formatter)
logger.addHandler(handler)

#logging.basicConfig(filename="/mars/logs/mars_room_sensor.log", level=logging.DEBUG,format='%(asctime)s %(message)s')

# Init headers
api_headers = {
    'Authorization': 'Bearer '+sensor_config['homeassistant']['api_token'],
    'Content-Type': 'application/json',
}

cloud_headers = {
    'Content-Type': 'application/json',
}
        
def get_and_send_sensor_signal():
    sleep_count = sleep_interval / sensor_interval
    sleep_time = 0
    for sensor_room in sensor_room_list:
        room_availability[sensor_room] = 'error'
    while(sleep_time < sleep_count):
        for sensor_room in sensor_room_list:
            log_info("Start to check for room : "+sensor_room)
            if(room_availability[sensor_room] != 'on'):
                room_availability[sensor_room] = check_room_availability_by_sensors(sensor_room)
            log_info("Room availability for " + sensor_room + " = " + room_availability[sensor_room])
        log_info("Sleep for "+str(sensor_interval)+" seconds ["+str(sleep_time)+"].")
        time.sleep(sensor_interval)
        sleep_time = sleep_time + 1
    
    for sensor_room in sensor_room_list:
        if(room_availability[sensor_room] == 'on'):
            post_room_status(sensor_room,"1")
        else:
            if(room_availability[sensor_room] == 'off'):
                post_room_status(sensor_room,"0")
            else:
                post_room_status(sensor_room,"-1")        

def post_room_status(sensor_room,room_status):
    post_url = mars_config['mars']['post_url_room_status']+mars_config[sensor_room]['server_room_id']+'/status'
    responseCode = 123
    retryTimes = cloudRetryTimes
    while(retryTimes > 0):
        log_debug("Sending..."+post_url)
        try:
            response = requests.post(url=post_url,data = room_status, headers = cloud_headers)
            log_debug("Send to server for " + sensor_room + "["+mars_config[sensor_room]['server_room_id']+"] with data:" + str(room_status) + ":"+str(response.status_code))  
            responseCode = response.status_code
        except requests.exceptions.RequestException as e:
            log_error(e)
        finally:
            if(responseCode==200 or responseCode==201):
                retryTimes = 0
            else:
                retryTimes = retryTimes - 1
            time.sleep(1)
    

def check_room_availability_by_sensors(sensor_room):
    all_motion_sensor_status = 'error'
    one_motion_sensor_status = 'error'
    for motion_sensor_name in mars_config[sensor_room]['motion_sensor'].split(';'):
        one_motion_sensor_status = get_motion_sensor_status(motion_sensor_name)
        if(one_motion_sensor_status == 'on'):
            all_motion_sensor_status = 'on'
        else:
            if(all_motion_sensor_status == 'error' and one_motion_sensor_status == 'off'):
                all_motion_sensor_status = 'off'     
            
    return all_motion_sensor_status
    
def get_motion_sensor_status(motion_sensor_name):
    motion_sensor_last_on_time = 0
    motion_sensor_status = 'error'
    if(motion_sensor_name in sensor_status):
        motion_sensor_last_on_time = sensor_status[motion_sensor_name]
        
    if (motion_sensor_last_on_time > 0):
        if(time() - motion_sensor_last_on_time > sensor_on_last_time):
           motion_sensor_status = get_motion_sensor_status_from_ha(motion_sensor_name)
           cache_sensor_status(motion_sensor_name,motion_sensor_status)
        else:
           motion_sensor_status = 'on'
    else:
        motion_sensor_status = get_motion_sensor_status_from_ha(motion_sensor_name)
        cache_sensor_status(motion_sensor_name,motion_sensor_status)
    
    return motion_sensor_status

def cache_sensor_status(motion_sensor_name,motion_sensor_status):
    if(motion_sensor_status == 'on'):
        sensor_status[motion_sensor_name] = time()
    else:
        sensor_status[motion_sensor_name] = 0
        
        
# Return stats: on / off / error    
def get_motion_sensor_status_from_ha(motion_sensor_name):
    url = 'http://127.0.0.1:8123/api/states/binary_sensor.'+motion_sensor_name
    data = 'error'
    responseCode = 123
    
    try:
        response = requests.get(url, headers=api_headers)  
        responseCode = response.status_code
        if (responseCode == 200):
            data = response.json()['state']
    except requests.exceptions.RequestException as e:
        log_error(e)
    finally:
        log_debug("[get_motion_sensor_status]["+motion_sensor_name+"]: HTTP response = "+str(responseCode) + " status ="+str(data))
    
    if(data != 'on' and data != 'off'):
        log_error("return data wrong ["+str(data)+"]")
        data = 'error'
        
    return data
    
def log_debug(debug):
    logger.debug(debug)   
    
def log_info(info):
    logger.info(info)     

def log_error(error):
    logger.error(error)
           

### Main ######################################################################
 
if __name__ == '__main__':
    
    #time.sleep(200)#sleep for 200 to wait ha service to start
    log_info("MARS sensor room start...")
    try:     
        while(True):
            get_and_send_sensor_signal() 
    finally:
        log_info("MARS sensor room end.")