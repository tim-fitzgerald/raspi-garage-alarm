## RaspberryPi Garage Alarm
This program implements an alarm system (for a garage in my case) that can be armed and disarmed via
text message and will also send alarm alerts as text messages via Twilio. I am using a Raspberry Pi Zero 
as my computer but this should run on any Raspberry Pi just fine so long as it has an internet
connection. 

### Setup
To get started you will need to set a few environmeent variables:
* `TWILIO_NUM` - the reserved phone number you got from Twilio.
* `TWILIO_SID` - Your account SID from Twilio
* `TWILIO_AUTH` - your auth token from Twilio.
* `ALARM_NUMBER` - the number you want to send the alert/alarm messages to.

You will also need to create a JSON file called `numbers.json` that contains key:pair values of the 
numbers that you wish to allow arm or disarm the system.

For the hardware setup - I am just using very basic magnetic door sensors like [these][3]. Edit the
`SENSORS` array for the pins you wire them to.  

[1]: https://www.twilio.com/
[2]: https://ngrok.com/
[3]: https://www.amazon.ca/Uxcell-a14060400ux0169-Magnetic-Door-Switch/dp/B00PZMG980/ref=sr_1_10?keywords=magnetic+door+sensor&qid=1560042266&s=gateway&sr=8-10
