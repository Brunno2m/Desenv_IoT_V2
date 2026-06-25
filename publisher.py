import json
import os
import random
import time

import paho.mqtt.client as mqtt

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
PUBLISH_INTERVAL_SECONDS = float(os.getenv("PUBLISH_INTERVAL_SECONDS", "5"))

ZONAS = [
    "frente_lavra",
    "galeria_acesso_02",
    "rampa_transporte",
]

SENSORES = {
    "CH4": ["sensor_ch4_01", "sensor_ch4_02"],
    "CO": ["sensor_co_01", "sensor_co_02"],
}


def gerar_valor(tipo_dado: str) -> float:
    if tipo_dado == "CH4":
        return round(random.uniform(0.1, 1.2), 2)
    return round(random.uniform(5.0, 60.0), 2)


def publicar_telemetria(client: mqtt.Client) -> None:
    for zona in ZONAS:
        for tipo_dado, sensores in SENSORES.items():
            for sensor_id in sensores:
                payload = {
                    "sensor_id": sensor_id,
                    "tipo_dado": tipo_dado,
                    "valor": gerar_valor(tipo_dado),
                }
                topico = f"mineracao/{zona}/{sensor_id}/telemetria"
                info = client.publish(topico, json.dumps(payload), qos=0, retain=False)

                if info.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"Publicado em {topico}: {payload}")
                else:
                    print(f"Falha ao publicar em {topico}. rc={info.rc}")


client = mqtt.Client()
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
client.loop_start()

try:
    while True:
        publicar_telemetria(client)
        time.sleep(PUBLISH_INTERVAL_SECONDS)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()