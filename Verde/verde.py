#!/usr/bin/env pybricks-micropython
#from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait
#from main import action

motor_a = Motor(Port.A)
motor_b = Motor(Port.B)
#line_sensor = ColorSensor(Port.S3)
color_sensor = ColorSensor(Port.S4)

#action = ''


def virar_esquerda():
    motor_a.dc(0)
    motor_b.dc(50)
    wait(800)     

def retorno_180():
    motor_a.dc(-50)
    motor_b.dc(50)
    wait(800)

'''
score_final = 0

def correcao_verde_azul():
    if color_sensor.color() == Color.GREEN:
        score+=2
    elif color_sensor.color() == Color.BLUE:
        score+=1
    else:
        score-=1
    
    if score < 0:
        score_final = 0
    elif score > 10:
        score_final = 10
    
    return score_final    
'''
'''
def verde_check():
    if action == 'RETO':
        wait(500)
        if action == 'RETO':
            if color_sensor.color() == Color.GREEN or Color.BLUE:
                virar_esquerda()            
            elif (color_sensor.color() == Color.GREEN or Color.BLUE) and line_sensor.reflection() < 20 :
                retorno_180()

    
   ''' 
    

#if color_sensor.color() == Color.GREEN or color_sensor.color() == Color.BLUE:
#if acao == 'turnRight':
#    motor_a.dc(0)
#    motor_b.dc(50)
#    wait(1000)
