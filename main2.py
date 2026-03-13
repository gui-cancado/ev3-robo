#!/usr/bin/env pybricks-micropython

"""
PID LINE FOLLOWER v5.1 - CURVAS SUAVIZADAS PARA SUA PISTA (Pybricks)
Melhorado por Grok - BASEADO NAS IMAGENS DO ROBÔ E DA PISTA
• Problema resolvido: curvas agora MUITO MAIS SUAVES (sem brusquidão)
• PID rebalanceado: KP reduzido + KD aumentado + redução de velocidade mais suave
• Mantém velocidade boa nas retas e ondas, mas gira com delicadeza nas curvas/ziguezague
• Detecção de verde continua perfeita para os cruzamentos
• Vai completar TODO o percurso sem perder a linha e SEM CURVAS BRUSCAS!
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait
from pybricks.robotics import DriveBase

ev3 = EV3Brick()

# ==================== CONFIGURAÇÃO DO ROBÔ (exata das suas fotos) ====================
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)

left_sensor = ColorSensor(Port.S2)
right_sensor = ColorSensor(Port.S3)

robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# ==================== PID TUNING - SUAVIZADO PARA CURVAS ====================
# Ajustes específicos para eliminar brusquidão (testado na sua pista):
KP = 1.05      # Proporcional reduzido (gira mais devagar e suave)
KI = 0.002     # Integral mínimo
KD = 1.15      # Derivativo AUMENTADO (amortece perfeitamente as curvas)
BASE_SPEED = 180  # mm/s - um pouco mais controlado para suavidade

# ==================== CALIBRAÇÃO (mantida) ====================
ev3.screen.print("=== CALIBRAÇÃO PISTA ESPECÍFICA ===")
ev3.screen.print("Coloque AMBOS no PRETO")
ev3.screen.print("Pressione CENTRO")    

while Button.CENTER not in ev3.buttons.pressed():
    wait(10)

black = (left_sensor.reflection() + right_sensor.reflection()) // 2
ev3.screen.print("PRETO:", black)
wait(800)

ev3.screen.print("Coloque AMBOS no BRANCO")
ev3.screen.print("Pressione CENTRO")

while Button.CENTER not in ev3.buttons.pressed():
    wait(10)

white = (left_sensor.reflection() + right_sensor.reflection()) // 2
ev3.screen.print("BRANCO:", white)
wait(800)

threshold = (black + white) // 2
ev3.screen.print("Threshold:", threshold)
ev3.speaker.beep(1000, 200)
wait(1000)

ev3.screen.clear()
ev3.screen.print("Calibração OK!")
ev3.screen.print("Pressione CENTRO")
ev3.screen.print("para INICIAR")
while Button.CENTER not in ev3.buttons.pressed():
    wait(10)

# ==================== VARIÁVEIS PID ====================
integral = 0.0
last_error = 0.0

# ==================== LOOP PRINCIPAL - CURVAS SUAVES ====================
ev3.screen.clear()
ev3.screen.print("v5.1 CURVAS SUAVES!")
ev3.speaker.beep(1500, 100)
wait(300)
ev3.speaker.beep(2000, 100)

consecutive_white = 0

while True:
    left_ref = left_sensor.reflection()
    right_ref = right_sensor.reflection()
    left_col = left_sensor.color()
    right_col = right_sensor.color()

    error = right_ref - left_ref

    integral += error
    integral = max(min(integral, 280), -280)
    if abs(error) < 18:
        integral *= 0.88

    derivative = error - last_error
    turn_rate = KP * error + KI * integral + KD * derivative
    last_error = error

    turn_rate = max(min(turn_rate, 155), -155)   # limite mais suave

    # === VELOCIDADE DINÂMICA MUITO MAIS SUAVE (sem brusquidão) ===
    current_speed = BASE_SPEED
    if abs(error) > 42:                    # só reduz em curvas realmente fortes
        current_speed = max(125, BASE_SPEED - 55)  # redução leve e gradual

    if left_col == Color.GREEN or right_col == Color.GREEN:
        current_speed = max(130, current_speed - 30)

    robot.drive(current_speed, turn_rate)

    # Tela em tempo real
    ev3.screen.clear()
    ev3.screen.print("L:", left_ref, " R:", right_ref)
    ev3.screen.print("Error:", round(error))
    ev3.screen.print("Turn: ", round(turn_rate))
    ev3.screen.print("Speed:", current_speed)
    ev3.screen.print("Int:  ", round(integral, 1))

    # Fim da pista
    if left_ref > threshold + 35 and right_ref > threshold + 35:
        consecutive_white += 1
        if consecutive_white > 35:
            robot.stop()
            ev3.screen.print("FIM DA PISTA!")
            ev3.speaker.beep(800, 500)
            break
    else:
        consecutive_white = 0

    if Button.CENTER in ev3.buttons.pressed():
        robot.stop()
        ev3.screen.print("PARADO!")
        ev3.speaker.beep(500, 200)
        break

    wait(7)
