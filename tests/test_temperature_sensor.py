import makeblock
from makeblock import boards
makeblock.add_port("COM4")
# Connect to the MeAuriga board
board = boards.MeAuriga.create()

# Read the temperature from the onboard sensor
temperature = board.get_temperature()
print("Temperature:", temperature)
