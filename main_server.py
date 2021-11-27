from flask import Flask, render_template, request
import json
import os
import NRFSender
import time
import schedule
import threading


app= Flask(__name__)

command_msg = ""
schedule_dict = {}

pipes = {
    "lamp_1":  [0xE0, 0xE0, 0xF1, 0xF1, 0xE0],
    "lamp_2":  [0xE1, 0xE0, 0xF1, 0xF1, 0xE0],
    "lamp_3":  [0xE1, 0xE1, 0xF1, 0xF1, 0xE0],
    "strip_1": [0xE0, 0xE0, 0xF0, 0xF1, 0xE0],
    "strip_2": [0xE0, 0xE0, 0xF1, 0xF0, 0xE0]
}

animations = {
    "animation1": 0,
    "animation2": 1,
    "animation3": 2,
}


def get_general_data():
    resp_json = {}
    with open("dataStorage/general.json") as json_file:
        resp_json = json_file.read()
    if not resp_json=="":
        return json.loads(resp_json)
    return None

tempral_data_storage = get_general_data()



def set_json(request):
    key = request.split(":", 1)[0]
    value = request.split(":", 1)[1]
    file_dir = "dataStorage/"+key+".json"
    
    with open(file_dir, "w") as data_file:
        data_file.write(value)

def set_json_2(request): 
    key = request.split(":", 1)[0]
    value = request.split(":", 1)[1]

    tempral_data_storage[key] = value
    with open("dataStorage/general.json", "w") as data_file:
        data_file.write(json.dumps(tempral_data_storage))
    
    
def is_open(file_name):
    if os.path.exists(file_name):
        try:
            os.rename(file_name, file_name) #can't rename an open file so an error will be thrown
            return False
        except:
            return True
    raise NameError

def get_data_storage_string():
    return json.dumps(tempral_data_storage)

def send_msg(pipe, msg):
    pass    
    

def check_send_msg(request):
    device_id = request.split(":")[0]
    pipe = pipes[device_id]
    msg = ""

    device = request.split("_")[0]
    if device == "lamp":
        msg = request.split(":")[1] #request e.g. lamp_3:1
    
    elif device == "strip":
        switch = request.split(":")[1][0]
        command = request.split("_")[2]#request e.g. strip_1:1_#3dff64 
        header = "A" #animation
        if command[0] == "#":
            header = "C" #color
            command = "0x"+command[1:]
        else:
            command = animations[command]

            #command = command.lstrip('#')
            #rgb = tuple(int(command[i:i+2], 16) for i in (0, 2, 4))
            #command = str(rgb[0]) + str(rgb[1]) + str(rgb[2])
        
        msg = header + switch + str(command)

    elif device == "preset":
        pass
    
   # print("{} | {} | {}".format(device_id, pipe, msg))
    
    NRFSender.send_msg(str(msg), pipes[device_id])

def remove_jobs_of_preset(preset_name):
    try:
        for job in schedule_dict[preset_name]:
            schedule.cancel_job(job)
    except:
        pass

def switch_preset(preset, manual_switch="X"):
    switch = str(preset["switch"])
    if manual_switch != "X":
        switch = manual_switch

    if preset["lamp_1"] == "1":
        check_send_msg("lamp_1:"+ switch)
        tempral_data_storage["lamp_1"] = switch
    else:
        check_send_msg("lamp_1:"+ "0")
        tempral_data_storage["lamp_1"] = "0"

    if preset["lamp_2"] == "1":
        check_send_msg("lamp_2:"+ switch)
        tempral_data_storage["lamp_2"] = switch
    else:
        check_send_msg("lamp_2:"+ "0")
        tempral_data_storage["lamp_2"] = "0"

    if preset["lamp_3"] == "1":
        check_send_msg("lamp_3:"+ switch)
        tempral_data_storage["lamp_3"] =switch
    else:
        check_send_msg("lamp_3:"+ "0")
        tempral_data_storage["lamp_3"] = "0"


    if preset["strip_1"].split("_")[0] == "1":
        check_send_msg("strip_1:"+ switch + "_" + preset["strip_1"].split("_")[1])
        tempral_data_storage["strip_1"] = switch + "_" + preset["strip_1"].split("_")[1]
    else:
        check_send_msg("strip_1:"+ "0" + "_" + preset["strip_1"].split("_")[1])
        tempral_data_storage["strip_1"] = "0" + "_" + preset["strip_1"].split("_")[1]

    if preset["strip_2"].split("_")[0] == "1":
        check_send_msg("strip_2:"+ switch + "_" + preset["strip_2"].split("_")[1])
        tempral_data_storage["strip_2"] = switch + "_" + preset["strip_2"].split("_")[1]
    else:
        check_send_msg("strip_2:"+ "0" + "_" + preset["strip_2"].split("_")[1])
        tempral_data_storage["strip_2"] = "0" + "_" + preset["strip_2"].split("_")[1]


def check_preset_update(request_string):
    req = request_string.split(":")[0]
    if(req == "delete_preset"):
        del tempral_data_storage[request_string.split(":")[1]]
        remove_jobs_of_preset(request_string.split(":")[1])
        with open("dataStorage/general.json", "w") as data_file:
            data_file.write(json.dumps(tempral_data_storage))
        return True
    elif req == "preset_names":
        return True
    elif req.split("_")[0] == "preset": #e.g. if preset_1 is saved, req is "preset_1"
        remove_jobs_of_preset(req)
        add_preset_to_schedule(req)
        return True
    elif req == "presetNum":
        return True
    return False


def check_set_json(request):
    if request.split(":")[0] == "delete_preset":
        return False
    return True

@app.route('/dataStorageString', methods=['GET', 'POST'])
def dataStorageString():    
    return get_data_storage_string()

@app.route("/", methods=['GET', 'POST'])
def index():
    
    name = list(request.form.to_dict())
    if request.method == 'POST':
        request_string = request.form.get('setJson')
        if request_string != None:
            if check_set_json(request_string):
                set_json_2(request_string)
            if not check_preset_update(request_string): #don't send anything if its just a preset update
                check_send_msg(request_string)
        else:
            request_string = request.form.get('realTimeColorChange')    
            if request_string != None:
                    check_send_msg(request_string) #realtime color change
            
    return render_template("buttons.html")







def add_preset_to_schedule(preset_name):
    preset = json.loads(tempral_data_storage[preset_name])
    switch_preset(preset)
    schedule_dict[preset_name] = []

    days = preset["days"].split("_")
    print("---")
    print("added on")
    for i in range(len(days)):
        if days[i] == "1":
            time_from = str(preset["timeFrom"].replace("_", ":"))
            time_to = str(preset["timeTo"].replace("_", ":"))

            
            if i == 0:
                schedule_dict[preset_name].append(schedule.every().monday.at(time_from).do(switch_preset, preset=preset, manual_switch="1"))
                schedule_dict[preset_name].append(schedule.every().monday.at(time_to).do(switch_preset, preset=preset, manual_switch="0"))
                print(i)
            elif i == 1:
                schedule_dict[preset_name].append(schedule.every().tuesday.at(time_from).do(switch_preset, preset=preset, manual_switch="1"))
                schedule_dict[preset_name].append(schedule.every().tuesday.at(time_to).do(switch_preset, preset=preset, manual_switch="0"))
                print(i)
            elif i == 2:
                schedule_dict[preset_name].append(schedule.every().wednesday.at(time_from).do(switch_preset, preset=preset, manual_switch="1"))
                schedule_dict[preset_name].append(schedule.every().wednesday.at(time_to).do(switch_preset, preset=preset, manual_switch="0"))
                print(i)
            elif i == 3:
                schedule_dict[preset_name].append(schedule.every().thursday.at(time_from).do(switch_preset, preset=preset, manual_switch="1"))
                schedule_dict[preset_name].append(schedule.every().thursday.at(time_to).do(switch_preset, preset=preset, manual_switch="0"))
                print(i)
            elif i == 4:
                schedule_dict[preset_name].append(schedule.every().friday.at(time_from).do(switch_preset, preset=preset, manual_switch="1"))
                schedule_dict[preset_name].append(schedule.every().friday.at(time_to).do(switch_preset, preset=preset, manual_switch="0"))
                print(i)
            elif i == 5:
                schedule_dict[preset_name].append(schedule.every().saturday.at(time_from).do(switch_preset, preset=preset, manual_switch="1"))
                schedule_dict[preset_name].append(schedule.every().saturday.at(time_to).do(switch_preset, preset=preset, manual_switch="0"))
                print(i)
            elif i == 6:
                schedule_dict[preset_name].append(schedule.every().sunday.at(time_from).do(switch_preset, preset=preset, manual_switch="1"))
                schedule_dict[preset_name].append(schedule.every().sunday.at(time_to).do(switch_preset, preset=preset, manual_switch="0"))
                print(i)
    print("---")


def schedule_thread():
    print("starting schedule thread")
    while True:
        schedule.run_pending()
        time.sleep(1)
    

def start_thread():
    x = threading.Thread(target=schedule_thread, args=())
    x.daemon = True
    x.start()


if __name__ == "__main__":
    preset_names = tempral_data_storage["preset_names"].split(":")
    for preset_name in preset_names:
        try:
            if json.loads(tempral_data_storage[preset_name])["repeat"] != "1":
                add_preset_to_schedule(json.loads(tempral_data_storage[preset_name]))
        except:
            pass
    
        
    if False:
        try:
            start_thread()  
        except (KeyboardInterrupt, SystemExit):
            sys.exit()
        

    app.run( host="192.168.2.118", port="5000", threaded=False)
    

    