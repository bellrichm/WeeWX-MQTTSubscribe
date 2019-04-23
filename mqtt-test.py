import paho.mqtt.client as mqtt

MQTT_SERVER = "weather-data.local"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_TOPIC = 'weather/loop'
MQTT_CLIENTID = ''
USERNAME = None
PASSWORD = None

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print('%s: %s\n' %(msg.topic, msg.payload))

client = mqtt.Client(client_id=MQTT_CLIENTID)

client.on_connect = on_connect
client.on_message = on_message

if USERNAME is not None and PASSWORD is not None:
    self.client.username_pw_set(USERNAME, PASSWORD)

client.connect(MQTT_SERVER, MQTT_PORT, MQTT_KEEPALIVE)

client.loop_forever()
