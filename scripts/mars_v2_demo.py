### Imports ###################################################################
 
from picamera.array import PiRGBArray
from picamera import PiCamera
from functools import partial
 
import multiprocessing as mp
import os
import time
import requests
from threading import Timer


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
 
### Setup #####################################################################
 
os.putenv( 'SDL_FBDEV', '/dev/fb0' )
 
resX = 640
resY = 480
 
cx = resX / 2
cy = resY / 2
 
#os.system( "echo 0=150 > /dev/servoblaster" )
#os.system( "echo 1=150 > /dev/servoblaster" )
 
xdeg = 150
ydeg = 150
 
 
# Setup the camera
#camera = PiCamera()
#camera.resolution = ( resX, resY )
#camera.framerate = 60
 
# Use this as our output
#rawCapture = PiRGBArray( camera, size=( resX, resY ) )

# The face cascade file to be used
 
t_start = time.time()
fps = 0
pending_send_faces = 0

headers = {
    'Authorization': 'Bearer ABCDEFGH',
    'Content-Type': 'application/json',
}

payload_on = {
    "entity_id": "light.gateway_light_angelfund"
}

payload_off = {
    'status': 'off',
}

lift_url = 'http://www.macroe.top/api/lift/'
toilet_url = 'http://207.246.95.229/api/room/1/'
toilet_status = '0'
room2_status = 'on'
### Helper Functions ##########################################################
def update_light_status():
    
    response = requests.get("http://207.246.95.229/api/room/2")
    global room2_status
    roomStatus = response.text
    print(roomStatus)
    if(roomStatus =='1' and room2_status != 'on'):        
        url_post = 'http://127.0.0.1:8123/api/services/light/turn_on'
        response = requests.post(url=url_post)
        room2_status = 'on'
    if(roomStatus != '1' and room2_status == 'on'):         
        url_post = 'http://127.0.0.1:8123/api/services/light/turn_off'
        response = requests.post(url=url_post)
        room2_status = 'off'
        
    
def get_and_send_sensor_signal():
    global pending_send_faces
    global toilet_status
    send_start = time.time()
    #print(str(send_start) + ":" + str(pending_send_faces))
    #response = requests.get(lift_url+str(pending_send_faces), headers=headers)
    sensor_states = get_sensor()
    
    print(str(send_start) + ":\t\t\t\t" + str(sensor_states).upper())
    if(sensor_states =='on' and toilet_status!='1'):
        toilet_status = '1'
        request_url = toilet_url+str(toilet_status)
        print("Sending..."+request_url)
        response = requests.get(request_url, headers=headers)
        print("Send to server" + str(toilet_status) + ":"+str(response.status_code))
        url_post = 'http://127.0.0.1:8123/api/services/light/turn_on'
        response = requests.post(url=url_post)
        
    if(sensor_states !='on' and toilet_status=='1'):
        toilet_status = '0'
        request_url = toilet_url+str(toilet_status)
        print("Sending..."+request_url)
        response = requests.get(request_url, headers=headers)
        print("Send to server" + str(toilet_status) + ":"+str(response.status_code))        
        url_post = 'http://127.0.0.1:8123/api/services/light/turn_off'
        response = requests.post(url=url_post)

def get_sensor():
    url = 'http://127.0.0.1:8123/api/states/binary_sensor.mars_motion'
    response = requests.get(url, headers=headers)
    
    data = 'off'
    #print(response.status_code)
    if (response.status_code == 200):
        data = response.json()['state']

    return data 

def get_toilet_status():
    url = toilet_url
    response = requests.get(url, headers=headers)
    
    data = 'off'
    print(response.read())
    if (response.status_code == 200):
        data = response.json()['state']

    return data 

### Main ######################################################################
 
if __name__ == '__main__':
 
    #response = requests.get(toilet_url+'0', headers=headers)
    #while(response.status_code <>200):
     #   response = requests.get(toilet_url+'0', headers=headers)
    
    #rt = RepeatedTimer(1, send_faces)
     
    url_post = 'http://127.0.0.1:8123/api/services/light/turn_on'
    response = requests.post(url=url_post)
    try:     
        while(True):
            get_and_send_sensor_signal()
            update_light_status()
            time.sleep(1)
    finally:
        print("End")