import makeblock
from makeblock.boards import MeAuriga
from makeblock.modules.rj25 import LineFollower

from time import sleep

makeblock.add_port("COM4")
board = MeAuriga.connect(BLE=True)

lineFollower = LineFollower(board, port=10)


def on_read(value):
    print(value)


def main():
    lineFollower.read(on_read)
    sleep(0.75)
    # print(lineFollower.get_status(port=10))
    # print(lineFollower.get_status())


if __name__ == '__main__':
    while True:
        main()
