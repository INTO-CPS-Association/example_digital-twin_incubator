from gpiozero import LED
from time import sleep

led = LED(13)

while True:
    led.on()
    sleep(50)
    led.off()
    sleep(50)
