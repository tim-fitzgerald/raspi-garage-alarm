#!/usr/bin/python3
import json
import os
import time
from functools import wraps
from itertools import cycle
from multiprocessing import Process, Value

import RPi.GPIO as GPIO
from flask import Flask, abort, redirect, render_template, request, url_for
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

twilio_sid = os.getenv("TWILIO_SID")
twilio_token = os.getenv("TWILIO_TOKEN")
twilio_number = os.getenv("TWILIO_NUM")
alarm_number = os.getenv("ALARM_NUMBER")

client = Client(twilio_sid, twilio_token)

GPIO.setmode(GPIO.BCM)

SENSORS = [
    {"name": "Window 1", "pin": 18, "status": None, "old_status": None},
    {"name": "Window 2", "pin": 24, "status": None, "old_status": None},
    {"name": "Door", "pin": 26, "status": None, "old_status": None},
]

for s in SENSORS:
    GPIO.setup(s["pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

ARMED = False

with open("numbers.json") as json_config:
    approved_numbers = json.load(json_config)


def check_sensor(sensor):
    if GPIO.input(sensor):
        status = "open"
    else:
        status = "closed"

    return status


def send_alert(sensor):
    message = client.messages.create(
        to=alarm_number,
        from_=twilio_number,
        body="Garage Alarm Triggered on sensor " + sensor["name"],
    )
    print(message.sid)


def alarm_loop():
    while True:
        global ARMED
        ARMED = True
        for sensor in SENSORS:
            sensor["old_status"] = sensor["status"]
            sensor["status"] = check_sensor(sensor["pin"])
            if sensor["status"] != sensor["old_status"]:
                if sensor["status"] == "open":
                    print(sensor["name"] + " is open!")
                    send_alert(sensor)
            else:
                None

        time.sleep(0.1)


def validate_twilio_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(twilio_token)
        request_valid = validator.validate(
            request.url, request.form, request.headers.get("X-TWILIO-SIGNATURE", "")
        )
        if request_valid:
            return f(*args, **kwargs)
        else:
            return abort(403)

    return decorated_function


@app.before_first_request
def init_sensors():
    for sensor in SENSORS:
        sensor['status'] = check_sensor(sensor['pin'])


@app.route("/start", methods=["POST"])
@validate_twilio_request
def start():
    global p
    global ARMED
    p = Process(target=alarm_loop)
    p.start()
    ARMED = True
    resp = MessagingResponse()
    resp.message("Alarm is now armed")
    return str(resp)


@app.route("/stop", methods=["POST"])
@validate_twilio_request
def stop():
    global p
    global ARMED
    p.terminate()
    ARMED = False
    resp = MessagingResponse()
    resp.message("Alarm is disarmed")
    return str(resp)


@app.route("/sms", methods=["GET", "POST"])
@validate_twilio_request
def sms():
    global ARMED
    number = request.form["From"].lower()
    message_body = request.form["Body"].lower()

    if number not in approved_numbers.values():
        print("Number not permitted")

    if message_body == "arm":
        return redirect(url_for("start"))
    elif message_body == "disarm":
        return redirect(url_for("stop"))
    elif message_body == "state":
        resp = MessagingResponse()
        states = ""
        init_sensors()
        for sens in SENSORS:
            states += sens['name'] + ": " + sens['status'] + "\n"
        if ARMED:
            resp.message(str("Armed" + "\n" + states))
        else:
            resp.message(str("Disarmed" + "\n" + states))
        return str(resp)
    else:
        resp = MessagingResponse()
        resp.message("Not a valid option!")
        return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
