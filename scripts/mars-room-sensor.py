import requests
import configparser
import time

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

room_url = mars_config['mars']['post_url_room_status']+sensor_config['room']['room_no']+'/status'

api_headers = {
    'Authorization': 'Bearer '+sensor_config['homeassistant']['api_token'],
    'Content-Type': 'application/json',
}

cloud_headers = {
    'Content-Type': 'application/json',
}

# def get_and_send_sensor_signal():
    # global pending_send_faces
    # global toilet_status
    # send_start = time.time()
    # #print(str(send_start) + ":" + str(pending_send_faces))
    # #response = requests.get(lift_url+str(pending_send_faces), headers=headers)
    # sensor_states = get_sensor()
    
    # print(str(send_start) + ":\t\t\t\t" + str(sensor_states).upper())
    # if(sensor_states =='on' and toilet_status!='1'):
        # toilet_status = '1'
        # request_url = toilet_url+str(toilet_status)
        # print("Sending..."+request_url)
        # response = requests.get(request_url, headers=headers)
        # print("Send to server" + str(toilet_status) + ":"+str(response.status_code))
        # url_post = 'http://127.0.0.1:8123/api/services/light/turn_on'
        # response = requests.post(url=url_post)
        
    # if(sensor_states !='on' and toilet_status=='1'):
        # toilet_status = '0'
        # request_url = toilet_url+str(toilet_status)
        # print("Sending..."+request_url)
        # response = requests.get(request_url, headers=headers)
        # print("Send to server" + str(toilet_status) + ":"+str(response.status_code))        
        # url_post = 'http://127.0.0.1:8123/api/services/light/turn_off'
        # response = requests.post(url=url_post)
        
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
            print("Send to server with data:" + str(room_status) + ":"+str(response.status_code))  
            responseCode = response.status_code
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
    
    try:
        response = requests.get(url, headers=api_headers)    
        if (response.status_code == 200):
            data = response.json()['state']

    finally:
        print("[get_motion_sensor_status]["+motion_sensor_name+"]: HTTP response = "+str(response.status_code) + " status ="+str(data))
    
    if(data == 'off'):
        return False
    else:
        return True
    

### Main ######################################################################
 
if __name__ == '__main__':
    
    #time.sleep(200)#sleep for 200 to wait ha service to start
    try:     
        while(True):
            get_and_send_sensor_signal()            
            time.sleep(sleep_interval)
    finally:
        print("End")