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
sensor_interval = 10

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
    sleep_count = sleep_interval / sensor_interval
    sleep_time = 0
    room_availability = 'error'
    while(sleep_time < sleep_count):
        if(room_availability != 'on'):
            room_availability = check_room_availability_by_sensors()
        log_info("Sleep for "+str(sensor_interval)+" seconds ["+str(sleep_time)+"],with room availability = " + room_availability)
        time.sleep(sensor_interval)
        sleep_time = sleep_time + 1
    
    if(room_availability == 'on'):
        post_room_status("1")
    else:
        if(room_availability == 'off'):
            post_room_status("0")
        else:
            post_room_status("-1")        

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
    all_motion_sensor_status = 'error'
    one_motion_sensor_status = 'error'
    for motion_sensor_name in motion_sensor_name_list:
        one_motion_sensor_status = get_motion_sensor_status(motion_sensor_name)
        if(one_motion_sensor_status == 'on'):
            all_motion_sensor_status = 'on'
        else:
            if(all_motion_sensor_status == 'error' and one_motion_sensor_status == 'off'):
                all_motion_sensor_status = 'off'     
            
    return all_motion_sensor_status

# Return stats: on / off / error    
def get_motion_sensor_status(motion_sensor_name):
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
        data = 'error'
        
    return data
    
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
    finally:
        log_info("MARS sensor room end.")