import threading
import csv
import time
import serial
import settings
import utils
from communicate_v2 import Communicate as com

experiment_state = None
read_state = None
count = 0
is_timekeeping = False
# ser_sensor = serial.Serial("COM4", 9800, timeout=1)
# ser_actuator = serial.Serial("COM5", 9800, timeout=1)


"""
Experiment state : start, stop, killed, paused
Read state       : reading, notreading

TODO:
- try the time keeper
- 'stop' affects all the processes
- read state should also be sent through serial to the other arduino
- handling if arduino not detected



"""

def countdown(n):
    global is_timekeeping
    
    for i in range(n):
        if is_timekeeping == False:
            break
        print(n-i)
        time.sleep(0.99)
        

def time_keeper():
    global experiment_state, is_timekeeping, read_state
    
    if experiment_state == settings.START:
        time_interval, read_duration, executions = [int(float(x)) for x in com.update_time_config()]
    
            
        time_interval *= 5 #later to be changed to 60
        n = 0
        while n < executions and is_timekeeping == True:
            read_state = settings.START
            countdown(time_interval)
            # print("reading")
            # read_state = settings.START
            
            th = threading.Thread(target=data_write)
            th.start()
            
            countdown(read_duration)
            # print("notreading")
            read_state = settings.STOP
            
            n+=1
            
            # pub.experiment_count(n)
            com.publish_count_executions(n)
            
    is_timekeeping = False
        

def experiment_state_check():
    global experiment_state, is_timekeeping, read_state

    while experiment_state != settings.KILLED:
        # experiment_state = update.experiment_state()
        experiment_state = com.update_experiment_state()
        # print(experiment_state)
        time.sleep(0.5)

        
        if experiment_state == settings.STOP:
            read_state = False
            is_timekeeping = False

        
        if experiment_state == settings.START and not is_timekeeping:
            is_timekeeping = True
            th = threading.Thread(target=time_keeper)
            th.start()
            
    is_timekeeping = False
            

def data_write():
    global read_state, count
    
    path = utils.create_path(settings.FOLDER_READINGS)
    
    
    # check the execution of these
    count += 1
    file = open(f"{path}\input{count}.csv", 'w', newline='')
    write = csv.writer(file)

    while read_state == settings.START:
        print("is reading\n")
        line = ser_sensor.readline()
        
        try:
            num = int(line.decode())
        except:
            pass
        
        string = str(num)
        write.writerow([string])
        time.sleep(1)

    file.close()

def main():
    th = threading.Thread(target=experiment_state_check)
    th.start()
    


