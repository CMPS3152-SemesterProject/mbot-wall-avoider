import sys
import serial
import os
import threading
import signal
from time import sleep, time
import makeblock
from makeblock.protocols.PackData import MegaPiPackData
from makeblock.utils import short2bytes

ser = None
# print("CMD1")
# ser.write(bytearray(b'\xffU\n\x00\x02\x08\x00\x02\x01\xff\x00\x00\n'))
# sleep(4)
# print("CMD2")
# ser.write(bytearray(b'\xffU\n\x00\x02\x08\x00\x02\x01\x00\xff\x00\n'))
# sleep(4)
# print("CMD3")
# ser.write(bytearray(b'\xffU\n\x00\x02\x08\x00\x02\x01\x00\x00\xff\n'))
# sleep(4)
# print("CMD4")
# ser.write(bytearray(b'\xffU\n\x00\x02\x08\x00\x02\x01\xff\xff\xff\n'))
# sleep(4)
# print("CMD5")
# ser.write(bytearray(b'\xffU\t\x00\x02"-d\x00\xe8\x03\n'))

print("REPL\n===========\n")
os.system('chcp 65001' if os.name == 'nt' else '')  # Set console codepage to UTF-8
while True:
    data = input("Enter command: ")
    if data == "clear":
        os.system('cls' if os.name == 'nt' else 'clear')
        continue
    if data == "reconnect":
        try:
            ser = serial.Serial("COM4", 115200)
        except:
            print("You are already connected.")
            continue
    # print(bytearray(b'\xffU\n'))
    d = None
    try:
        d = eval("b'\\xffU\\n" + data + "\\n'")
    except:
        print("Bad command.")
        continue
    byte_command = bytearray(d)
    try:
        ser.write(byte_command)
    except:
        try:
            ser = serial.Serial("COM4", 115200)
            sleep(3)
            ser.write(byte_command)
        except:
            print("Cable error. Please reconnect and then type 'reconnect'")
    #res = ser.read(100)
    #print("\nResponse:")
    #print(res)





# exiting = False
# total = 0
# buf = bytearray()
# sent_count = 0
# received_count = 0
# start_time = time()
#
#
# def __exiting(signal, frame):
#     global exiting, sent_count, received_count
#     during = time() - start_time
#     print("time:", during, "sent:", sent_count / during / 1024, "recv:", received_count / during / 1024)
#     exiting = True
#     sys.exit(0)
#
#
# signal.signal(signal.SIGINT, __exiting)
# len = 100
# for i in range(len):
#     buf.append(0x31 + i)
#
#
# def on_read():
#     global received_count, exiting, ser
#     while True:
#         if exiting:
#             break
#         if ser.isOpen:
#             len = ser.inWaiting()
#             for i in range(len):
#                 ser.read()
#             received_count = received_count + len
#             sleep(0.0001)
#
#
# thread = threading.Thread(target=on_read, args=())
# thread.start()
# while True:
# #     ser.write(buf)
# #     sent_count = sent_count + len
# #     sleep(0.001)
# #     print(sent_count)
# #
# #     #pack_data = MegaPiPackData()
# #     #pack_data.data = ["COM4"]
# #     #pack_data.data.extend(short2bytes(50))
# #     #pack_data.data.extend(short2bytes(1000))