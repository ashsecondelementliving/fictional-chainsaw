import csv
from Main import mainpy
from MainI import mainIpy  
from PhantomCreator import creatorMain

def mapperMain(senderName, input_file, output_file, socketio=None, mode="email"):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        if "vmid" in reader.fieldnames:
            print("Auto Process")
            creatorMain(input_file, senderName, output_file, socketio)
        elif "About" in reader.fieldnames:
            print("Manual Process")
            if mode == "inmail":
                mainIpy(senderName, input_file, output_file, socketio)
            else:
                mainpy(senderName, input_file, output_file, socketio)
        else:
            return "Error: Please enter a valid .csv file"
