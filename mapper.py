import csv
from Main import mainpy
from PhantomCreator import creatorMain

def mapperMain(senderName, input_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        if "vmid" in reader.fieldnames:
            print("Auto Process")
            creatorMain(input_file, senderName)
        elif "About" in reader.fieldnames:
            print("Manual Process")
            mainpy (senderName, input_file)
        else: 
            return "Error: Please enter a valid .csv file"