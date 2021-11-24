from flask import Flask, render_template, request
import json
import os
import NRFSender
import time
import schedule
import threading


app= Flask(__name__)

command_msg = ""

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
    
    #print("{} | {} | {}".format(device_id, pipe, msg))
    
    NRFSender.send_msg(str(msg), pipes[device_id])





@app.route('/dataStorageString', methods=['GET', 'POST'])
def dataStorageString():    
    return get_data_storage_string()

@app.route("/", methods=['GET', 'POST'])
def index():
    
    name = list(request.form.to_dict())
    if request.method == 'POST':
        request_string = request.form.get('setJson')
        if request_string != None:
            #print(request_string)
            check_send_msg(request_string)
            set_json_2(request_string)


        else:
            request_string = request.form.get('realTimeColorChange')    
            if request_string != None:
                    check_send_msg(request_string) #realtime color change
            
    return render_template("buttons.html")


def test_thread_function():
    while True:
        print("test")
        time.sleep(2)
    

def start_thread():
    x = threading.Thread(target=test_thread_function, args=())
    x.daemon = True
    x.start()


if __name__ == "__main__":
    try:
        start_thread()  
    except (KeyboardInterrupt, SystemExit):
        cleanup_stop_thread()
        sys.exit()
    

    app.run( host="192.168.2.118", port="5000", debug=True, threaded=True)

    