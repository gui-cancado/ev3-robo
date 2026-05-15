#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait, StopWatch
from main import action

motor_a = Motor(Port.A)
motor_b = Motor(Port.B)
color_sensor = ColorSensor(Port.S4)

def verde_check(action):
    if color_sensor.color() == Color.GREEN or color_sensor.color() == Color.BLUE:
        if action == 'turnRight':
            motor_a.dc(0)
            motor_b.dc(50)
            wait(1000)