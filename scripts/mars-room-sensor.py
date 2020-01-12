import requests
import configparser
import time

config = configparser.ConfigParser()

config.read('/mars/mars-room.ini')

room_url = 'http://207.246.95.229/api/room/1/'
room_status = '0'
sleep_interval = 1
motion_sensor_name_list = ['mars_motion_1','mars_motion_2']


headers = {
    'Authorization': 'Bearer '+config['homeassistant']['api_token'],
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
        post_room_status('on')
    else:
        post_room_status('off')

def post_room_status(room_status):
    post_url = room_url+str(room_status)
    print("Sending..."+post_url)
    response = requests.post(url=post_url)
    print("Send to server" + str(room_status) + ":"+str(response.status_code))  
    

def check_room_availability_by_sensors():
    motion_sensor_status = false
    for motion_sensor_name in motion_sensor_name_list:
        if(get_motion_sensor_status(motion_sensor_name)):
            motion_sensor_status = true
            
    return motion_sensor_status
            

def get_motion_sensor_status(motion_sensor_name):
    url = 'http://127.0.0.1:8123/api/states/binary_sensor.'+motion_sensor_name
    response = requests.get(url, headers=headers)
    
    data = 'off'
    
    if (response.status_code == 200):
        data = response.json()['state']

    print("[get_motion_sensor_status]: HTTP response = "+str(response.status_code) + " status ="+str(data))
    
    if(data == 'off'):
        return false
    else:
        return true
    

### Main ######################################################################
 
if __name__ == '__main__':
    
    try:     
        while(True):
            get_and_send_sensor_signal()            
            time.sleep(sleep_interval)
    finally:
        print("End")