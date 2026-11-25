# Eetu Kyrönlahti
# 25.11.2026
# 4. Harjoitus: DHT22 ja MQTT

import machine
import time
import network
import dht

from umqtt.simple import MQTTClient
from hktiedot import SSID, PASSWORD, OPISKELIJATUNNUS


# Otetaan DHT22-anturi käyttöön
sensor = dht.DHT22(machine.Pin(21))

# Yhdistetään WiFi-verkkoon
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Yhdistetään verkkoon...")

while not wlan.isconnected():
    time.sleep(1)

ip = wlan.ifconfig()[0]
print("Verkkoon yhdistetty!")

# MQTT broker
client = MQTTClient(
    ("picow-" + OPISKELIJATUNNUS).encode(),
    "iot.research.hamk.fi",
    keepalive=60
)

# MQTT-aiheet
TOPIC_LAMPOTILA = ("HAMK/Fo/DHT22/" + OPISKELIJATUNNUS + "/lampotila").encode()
TOPIC_KOSTEUS = ("HAMK/Fo/DHT22/" + OPISKELIJATUNNUS + "/kosteus").encode()

# Edelliset mittaustulokset
edellinenLampotila = ""
edellinenKosteus = ""

# Mitataan arvot 10 sekunnin välein
while True:
    sensor.measure()
    lampotila = sensor.temperature()
    kosteus = sensor.humidity()
    
    print("Lämpötila:", lampotila, "°C")
    print("Kosteus:", kosteus, "%")

    # Yhdistetään MQTT-brokeriin
    client.connect()

    # Tarkistetaan lämpötilan muutos
    if lampotila != edellinenLampotila:
        client.publish(
            TOPIC_LAMPOTILA,
            str(lampotila).encode()
        )
        edellinenLampotila = lampotila
        print("MQTT: Lämpötila lähetetty")
    else:
        print("MQTT: Lämpötilaa ei lähetetty")

    # Tarkistetaan kosteuden muutos
    if kosteus != edellinenKosteus:
        client.publish(
            TOPIC_KOSTEUS,
            str(kosteus).encode()
        )
        edellinenKosteus = kosteus
        print("MQTT: Kosteus lähetetty")
    else:
        print("MQTT: Kosteytta ei lähetetty")

    # Katkaistaan MQTT-yhteys
    client.disconnect()

    # Odotetaan 10 sekuntia
    time.sleep(10)