#!/usr/bin/env python
# -*- coding: utf-8 -*-

# *******************************************************************************
# Copyright 2017 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# *******************************************************************************


import curses
import os
import time

if os.name == 'nt':
    import msvcrt


    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)


    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *  # Uses Dynamixel SDK library

# ********* DYNAMIXEL Model definition *********
# ***** (Use only one definition at a time) *****
MY_DXL = 'X_SERIES'  # XM430-W210 (11.5 V )

# Control table address
# Setari parametrii motor
if MY_DXL == 'X_SERIES':
    # adrese parametrii
    ADDR_TORQUE_ENABLE = 64
    ADDR_GOAL_POSITION = 116
    ADDR_PRESENT_POSITION = 132
    ADDR_PPRESENT_VELOCITY = 128
    ADDR_OPERATING_MODE = 11
    ADDR_GOAL_VELOCITY = 104

    # valoare parametru
    DXL_MINIMUM_POSITION_VALUE = 0  # Refer to the Minimum Position Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE = 4095  # Refer to the Maximum Position Limit of product eManual
    GOAL_VELOCITY = 80  # Viteza motor stanga
    BAUDRATE = 1000000

# DYNAMIXEL Protocol Version (1.0 / 2.0)
# https://emanual.robotis.com/docs/en/dxl/protocol2/
# Se foloseste pentru a apela programul packetHandler
PROTOCOL_VERSION = 2.0

# Factory default ID of all DYNAMIXEL is 1
DXL1_ID = 1
DXL2_ID = 2
DXL_Broadcast_ID = 254

# Use the actual port assigned to the U2D2.
# ex) Windows: "COM*", Linux: "/dev/ttyUSB*", Mac: "/dev/tty.usbserial-*"
# Se foloseste pentru a apela programul portHandler l91
DEVICENAME = '/dev/ttyUSB0'  # se inlocuieste cu COM@ pt windows

TORQUE_ENABLE = 1  # Value for enabling the torque
TORQUE_DISABLE = 0  # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 20  # Dynamixel moving status threshold
CHANGE_TO_VELOCITY = 1  # Control mode for velocity

dxl_goal_velocity = GOAL_VELOCITY  # Goal velocity for all ID

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

# Change operating mode
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_Broadcast_ID, ADDR_OPERATING_MODE,
                                                          CHANGE_TO_VELOCITY)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("ALL Dynamixel Control Mode successfully changed")

# Enable Dynamixel Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_Broadcast_ID, ADDR_TORQUE_ENABLE,
                                                          TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("ALL Dynamixel Torque has been successfully enabeled")

# Definire viteza maxima/dorita

dxl_goal_velocity = int(input('Input the velocity for all motors: '))  # max ???

print("Control with: \n   W \n a s d")
"""
Control by wasd
Motor ID 1 - Left
Motor ID 2 - Right
ESC iesire
"""
time_sleep = 0.1

# Get the curses window, turn off echoing of keyboard to screen, turn on
# instant (no waiting) key response, and use special values for cursor keys
screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)

key_pressed = False

try:

    while True:
        char = screen.getch()
        if char == ord('q'):
            break
        elif char == curses.KEY_UP:
            if not key_pressed:
                key_pressed = True
                # Setare viteza si sens ambele motoare
                dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_Broadcast_ID,
                                                                          ADDR_GOAL_VELOCITY,
                                                                          dxl_goal_velocity)  # motoarele se invart in aceeasi directie
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))

                print("moving forward... \n")
            else:
                pass

        elif char == curses.KEY_DOWN:
            if not key_pressed:
                key_pressed = True
                # Setare viteza si sens ambele motoare
                dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_Broadcast_ID,
                                                                          ADDR_GOAL_VELOCITY,
                                                                          -1 * dxl_goal_velocity)  # - viteza pt a merge in sens opus
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))

                print("moving backward... \n")
            else:
                pass

        elif char == curses.KEY_RIGHT:
            if not key_pressed:
                key_pressed = True
                # Setare viteza si sens pentru motorul 1
                dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL1_ID,
                                                                          ADDR_GOAL_VELOCITY, 100)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))

                # Setare viteza si sens pentru motorul 2
                dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL2_ID,
                                                                          ADDR_GOAL_VELOCITY, -1 * 100)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))

                print("turning right... \n")
            else:
                pass

        elif char == curses.KEY_LEFT:
            if not key_pressed:
                key_pressed = True
                # Setare viteza si sens pentru motorul 1
                dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL1_ID,
                                                                          ADDR_GOAL_VELOCITY, -1 * 100)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))

                # Setare viteza si sens pentru motorul 2
                dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL2_ID,
                                                                          ADDR_GOAL_VELOCITY, 1 * 100)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))

                print("turning left... \n")
            else:
                pass

        elif char == 10:
            print
            "stop"

        if key_pressed:
            time.sleep(time_sleep)
            key_pressed = False  # pentru a debloca tasta
            dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_Broadcast_ID,
                                                                      ADDR_GOAL_VELOCITY,
                                                                      0)  # opreste motorul
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))
            else:
                print("Motor Stoped\n")
        else:
            pass




finally:
    # Close down curses properly, inc turn echo back on!
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()

dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_Broadcast_ID, ADDR_TORQUE_ENABLE,
                                                          TORQUE_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("ALL Dynamixel Torque has been successfully disabled")

# Close port
portHandler.closePort()
