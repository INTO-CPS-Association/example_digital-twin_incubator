from gpiozero import LED
from time import sleep

led = LED(12)#heater

while True:
    led.on()
    sleep(30)
    led.off()
    sleep(30)
