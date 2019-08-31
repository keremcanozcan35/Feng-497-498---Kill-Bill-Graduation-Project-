import io
from google.cloud import vision
import os
import re
import mysql.connector as mysql
import time
from picamera import PiCamera
from time import sleep

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client_secrets.json"
trigger = True
deviceid = 'mydeviceid'
is_trigger = 'True'

def detect_text(path):
    deger = []
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    for text in texts:
        deger.append('{}'.format(text.description))

    del deger[0]
    return deger
    
def get_value(myarray):
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    find = "T"
    mynewarray = []
    max = len(myarray)
    print(myarray)
    
    for a in range(0, max):
        temp = myarray[a]
        if temp[:1] in find:
            break
    for s in range(0, a):
        del myarray[0]
    
    max = len(myarray)
    
    for i in range(0, max):
        tempstring = myarray[i]
        if tempstring[:1] in letters:
            myarray[i] = "-"
        else:
            mynewarray.append(myarray[i])

    for z in range(0, 2):
        if '.' in mynewarray[z]:
            mynewarray[z] = re.sub(r"\.", "", mynewarray[z])
        if ',' in mynewarray[z]:
            mynewarray[z] = re.sub(r"\,", "", mynewarray[z])
        
    finalstring = mynewarray[0] + mynewarray[1]
    if len(finalstring) < 4:
        finalstring = mynewarray[0] + mynewarray[1] + mynewarray[2]
    
    finalstring = finalstring[:4]
    return finalstring

def start_processing():
    camera = PiCamera()
    camera.resolution = (1280,1280)
    sleep(2)
    camera.awb_mode = "fluorescent"
    sleep(5)
    camera.capture("/home/pi/Desktop/picture.jpg",format="jpeg",quality=100)
    a = detect_text("/home/pi/Desktop/picture.jpg")
    
    
    # a = detect_text("picture3.jpg")
    # print(b)
    b = get_value(a)
    # print(b)
    return b

def check(device_id, is_trigger):
    # Open database connection
    db = mysql.connect(host='80.211.129.93', database='killbill', user='killbill_user', password='T54bkNgV13rFcdqQ')
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    sql = "SELECT * FROM water_meter WHERE device_id = %s AND is_trigger = %s"
    try:
        # Execute the SQL command
        cursor.execute(sql, (device_id, is_trigger, ))
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        if len(results) == 0:
            print("NOT TRIGGERED")
            return False
        else:
            print("TRIGGERED")
            return True
    except:
        print("Error: unable to fetch data")

def update(last_value, deviceid):
    # Open database connection
    db = mysql.connect(host='80.211.129.93', database='killbill', user='killbill_user', password='T54bkNgV13rFcdqQ')
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = "UPDATE water_meter SET last_value = %s , is_trigger = %s WHERE device_id = %s"
    data = (last_value, "False" , deviceid)
    try:
        # Execute the SQL command
        cursor.execute(sql, data)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
    # disconnect from server
    db.close()


loop = True
while loop == True:
    try:
        trigger = check(deviceid, is_trigger)
        if trigger == True:
            print("running")
            c = start_processing()
            print(c)
            update(c, deviceid)
        else:
            print("sleeping")
        time.sleep(15)
    except KeyboardInterrupt:
        loop == False