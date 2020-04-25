import requests
import configparser
import time
import logging

logging.basicConfig(filename="/mars/logs/mars_room_sensor.log", level=logging.DEBUG,format='%(asctime)s %(message)s')

sensor_config = configparser.ConfigParser()
mars_config = configparser.ConfigParser()

sensor_config.read('/mars/mars-sensor.ini')
mars_config.read('/mars/scripts/mars.ini')

# Read MARS configuration
cloudRetryTimes = int(mars_config['mars']['post_retry_times'])
sleep_interval = int(mars_config['mars']['post_interval'])

# Read sensor configuration
sensor_id = 'sensor_'+ sensor_config['sensor']['sensor_id']
server_room_id = mars_config[sensor_id]['server_room_id']
motion_sensor_name_list = mars_config[sensor_id]['motion_sensor'].split(';')

room_url = mars_config['mars']['post_url_room_status']+server_room_id+'/status'

api_headers = {
    'Authorization': 'Bearer '+sensor_config['homeassistant']['api_token'],
    'Content-Type': 'application/json',
}

cloud_headers = {
    'Content-Type': 'application/json',
}
        
def get_and_send_sensor_signal():
    
    if(check_room_availability_by_sensors()):
        post_room_status("1")
    else:
        post_room_status("0")

def post_room_status(room_status):
    post_url = room_url
    responseCode = 123
    retryTimes = cloudRetryTimes
    while(retryTimes > 0):
        print("Sending..."+post_url)
        try:
            response = requests.post(url=post_url,data = room_status, headers = cloud_headers)
            log_debug("Send to server with data:" + str(room_status) + ":"+str(response.status_code))  
            responseCode = response.status_code
        except requests.exceptions.RequestException as e:
            log_error(e)
        finally:
            if(responseCode==200 or responseCode==201):
                retryTimes = 0
            else:
                retryTimes = retryTimes - 1
            time.sleep(1)
    

def check_room_availability_by_sensors():
    motion_sensor_status = False
    for motion_sensor_name in motion_sensor_name_list:
        if(get_motion_sensor_status(motion_sensor_name)):
            motion_sensor_status = True
            
    return motion_sensor_status
    
def get_motion_sensor_status(motion_sensor_name):
    url = 'http://127.0.0.1:8123/api/states/binary_sensor.'+motion_sensor_name
    data = 'off'
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
    
    if(data == 'off'):
        return False
    else:
        return True
    
def log_debug(debug):
    logging.debug(debug)   
    
def log_info(info):
    logging.info(info)     

def log_error(error):
    logging.error(error)
           

### Main ######################################################################
 
if __name__ == '__main__':
    
    #time.sleep(200)#sleep for 200 to wait ha service to start
    log_info("MARS sensor room start...")
    try:     
        while(True):
            get_and_send_sensor_signal() 
            log_info("Sleep for "+str(sleep_interval)+" seconds.")
            time.sleep(sleep_interval)
    finally:
        log_info("MARS sensor room end.")