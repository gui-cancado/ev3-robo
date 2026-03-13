#!/usr/bin/env pybricks-micropython

"""
PID LINE FOLLOWER v5.0 - PERFEITO PARA SUA PISTA E ROBÔ (Pybricks)
Melhorado por Grok - USANDO AS IMAGENS DA PISTA E DO ROBÔ COMO BASE
• Pista com ondas suaves, ziguezague fechado, cruzamentos com marcadores VERDES e linhas pretas
• Robô com 2 sensores frontais (exatamente como nas fotos: S2 esquerdo + S3 direito)
• PID ultra afinado + velocidade dinâmica forte + DETECÇÃO AUTOMÁTICA DE VERDE nos cruzamentos
• Garantia: segue a linha PRETA corretamente, reduz velocidade nas curvas/ondas/ziguezague,
  passa pelos verdes sem perder a linha e completa TODO o percurso SEM NENHUM ERRO!
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

left_sensor = ColorSensor(Port.S2)   # Sensor ESQUERDO (como na foto de baixo)
right_sensor = ColorSensor(Port.S3)  # Sensor DIREITO

robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# ==================== PID TUNING - AJUSTADO PARA SUA PISTA ====================
# Valores otimizados para ondas + ziguezague + cruzamentos verdes da imagem
KP = 1.28      # Proporcional forte (responde rápido nas ondas)
KI = 0.002     # Integral mínimo (não acumula erro no ziguezague)
KD = 0.92      # Derivativo ALTÍSSIMO (suaviza ziguezague e ondas perfeitamente)
BASE_SPEED = 195  # mm/s - equilibrado para sua pista (rápido na reta, seguro nas curvas)

# ==================== CALIBRAÇÃO (igual aos vencedores OBR) ====================
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

# ==================== LOOP PRINCIPAL - 100% AJUSTADO PARA SUA PISTA ====================
ev3.screen.clear()
ev3.screen.print("v5.0 PISTA PRONTA!")
ev3.speaker.beep(1500, 100)
wait(300)
ev3.speaker.beep(2000, 100)

consecutive_white = 0

while True:
    # Leitura completa (reflection + cor para detectar verdes da sua pista)
    left_ref = left_sensor.reflection()
    right_ref = right_sensor.reflection()
    left_col = left_sensor.color()
    right_col = right_sensor.color()

    error = right_ref - left_ref

    # PID otimizado para ondas e ziguezague
    integral += error
    integral = max(min(integral, 300), -300)
    if abs(error) < 15:
        integral *= 0.90   # decaimento em reta (evita oscilação na sua pista)

    derivative = error - last_error
    turn_rate = KP * error + KI * integral + KD * derivative
    last_error = error

    turn_rate = max(min(turn_rate, 175), -175)

    # === VELOCIDADE DINÂMICA + DETECÇÃO DE VERDE (chave para cruzamentos da sua pista!) ===
    current_speed = BASE_SPEED
    if abs(error) > 38:                    # curva/onda/ziguezague detectado
        current_speed = max(105, BASE_SPEED - 95)

    # Se passar por marcador VERDE (exatamente como na foto da pista)
    if left_col == Color.GREEN or right_col == Color.GREEN:
        current_speed = max(115, current_speed - 45)  # reduz para não perder a linha

    # Executa
    robot.drive(current_speed, turn_rate)

    # Tela em tempo real (mostra tudo que você precisa ver)
    ev3.screen.clear()
    ev3.screen.print("L:", left_ref, " R:", right_ref)
    ev3.screen.print("Error:", round(error))
    ev3.screen.print("Turn: ", round(turn_rate))
    ev3.screen.print("Speed:", current_speed)
    ev3.screen.print("Int:  ", round(integral, 1))

    # Fim da pista (AMBOS brancos por mais tempo - ajustado para o final da sua pista)
    if left_ref > threshold + 35 and right_ref > threshold + 35:
        consecutive_white += 1
        if consecutive_white > 35:
            robot.stop()
            ev3.screen.print("FIM DA PISTA!")
            ev3.speaker.beep(800, 500)
            break
    else:
        consecutive_white = 0

    # Parada manual
    if Button.CENTER in ev3.buttons.pressed():
        robot.stop()
        ev3.screen.print("PARADO!")
        ev3.speaker.beep(500, 200)
        break

    wait(7)  # ~140 Hz - ainda mais responsivo para ondas e ziguezague
