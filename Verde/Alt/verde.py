#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Color
from pybricks.tools import wait



def virar_esquerda(motor_a, motor_b, duration=800):
    motor_a.dc(0)
    motor_b.dc(50)
    wait(duration)


def retorno_180(motor_a, motor_b, duration=800):
    motor_a.dc(-50)
    motor_b.dc(50)
    wait(duration)


def correcao_verde_azul(score, color_sensor):
    # Update score based on detected color and return new score
    if color_sensor.color() == Color.GREEN:
        score += 2
    elif color_sensor.color() == Color.BLUE:
        score += 1
    else:
        score -= 1

    if score < 0:
        score = 0
    elif score > 10:
        score = 10

    return score


def verde_check(score, action, black, line_sensor, motor_a, motor_b):
    # Decide maneuvers based on score and line reflection; return updated (score, action)
    if score > 8 and line_sensor < (black * 1.125):
        retorno_180(motor_a, motor_b)
        action = '180'
        score = 0
    elif score > 8:
        virar_esquerda(motor_a, motor_b)
        action = 'TurnLeft'
        score = 0

    return score, action
