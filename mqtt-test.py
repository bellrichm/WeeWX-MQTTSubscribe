import paho.mqtt.client as mqtt

HOST = "weather-data.local"
PORT = 1883
KEEPALIVE = 60
TOPIC = 'weather/loop'
CLIENTID = ''
USERNAME = None
PASSWORD = None

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print('%s: %s\n' %(msg.topic, msg.payload))

client = mqtt.Client(client_id=CLIENTID)

client.on_connect = on_connect
client.on_message = on_message

if USERNAME is not None and PASSWORD is not None:
    self.client.username_pw_set(USERNAME, PASSWORD)

client.connect(HOST, PORT, KEEPALIVE)

print("Host is %s" % HOST)  
print("Port is %s" % PORT) 
print("Keep alive is %s" % KEEPALIVE) 
print("Topic is %s" % TOPIC) 
print("Client id is %s" % CLIENTID) 
print("Username is %s" % USERNAME) 
if PASSWORD is not None:
    print("Password is set")   
else:
    print("Password is not set")
        
client.loop_forever()