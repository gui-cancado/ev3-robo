#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

ev3 = EV3Brick()
motor_a = Motor(Port.A)
motor_d = Motor(Port.D)
left_sensor  = ColorSensor(Port.S3)
right_sensor = ColorSensor(Port.S4)

ev3.screen.print("Pressione CENTRO para iniciar")
while Button.CENTER not in ev3.buttons.pressed():
    wait(10)

ev3.screen.clear()
ev3.screen.print("SEGUINDO LINHA!")
ev3.speaker.beep(1500, 100)
wait(300)
ev3.speaker.beep(2000, 100)

while True:
    left_color  = left_sensor.color()
    right_color = right_sensor.color()

    left_black  = left_color  == Color.BLACK
    right_black = right_color == Color.BLACK
    left_green  = left_color  == Color.GREEN
    right_green = right_color == Color.GREEN



    if left_black and right_black:

        motor_a.dc(28.5)
        motor_d.dc(25)
        action = "FIM DE PISTA"

    elif left_green and right_green:

        motor_a.dc(0)
        motor_d.dc(0)
        wait(300)
        action = "OBJETIVO FEITO"

    elif left_green:

        motor_a.dc(28.5)
        motor_d.dc(25)
        wait(200)
        motor_a.dc(35)
        motor_d.dc(-15)
        wait(250)
        action = "CURVA VERDE ESQ"
        wait(500)

    elif right_green:

        motor_a.dc(28.5)
        motor_d.dc(25)
        wait(200)
        motor_a.dc(-15)
        motor_d.dc(35)
        wait(250)
        action = "CURVA VERDE DIR"
        wait(500)

    elif left_black:

        motor_a.dc(25)
        motor_d.dc(-12.5)
        action = "ESQ"

    elif right_black:

        motor_d.dc(25)
        motor_a.dc(-12.5)
        action = "DIR"

    else:

        motor_a.dc(28.5)
        motor_d.dc(25)
        action = "RETO"

    # --- Display ---
    ev3.screen.clear()
    ev3.screen.print("Esq:", left_color)
    ev3.screen.print("Dir:", right_color)
    ev3.screen.print("Acao:", action)


    if Button.CENTER in ev3.buttons.pressed():
        motor_a.dc(0)
        motor_d.dc(0)
        ev3.screen.clear()
        ev3.screen.print("PARADO!")
        ev3.speaker.beep(500, 200)
        break

    wait(10)
