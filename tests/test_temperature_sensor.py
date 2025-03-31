import makeblock
from makeblock import boards

from time import sleep

makeblock.add_port("COM4")
# Connect to the MeAuriga board
board = boards.MeAuriga.create(BLE=True)

# Read the temperature from the onboard sensor
while True:
    temperature = board.get_temperature()
    print("Temperature:", temperature)
    sleep(0.5)
