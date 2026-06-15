import paho.mqtt.client as mqtt
import json, time, random

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()

try:
    while True:
        payload = {
            "temperature": round(20 + random.uniform(0, 10), 2),
            "humidity": round(50 + random.uniform(0, 20), 2)
        }
        client.publish("/iot/sensor001", json.dumps(payload))
        print("Publicado:", payload)
        time.sleep(5)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()