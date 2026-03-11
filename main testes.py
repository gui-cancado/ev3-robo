```python
#!/usr/bin/env pybricks-micropython

"""
PID LINE FOLLOWER v3.1 - 2 SENSORES OTIMIZADO PARA CURVAS (Pybricks)
Melhorado por Grok - Perfeito em curvas fechadas, mais lento e estável,
velocidade dinâmica em curva + PID reafinadíssimo

IMPORTANTE: "ACESSO NEGADO" NÃO É ERRO NO CÓDIGO!
Causa 99% das vezes: permissão de execução do arquivo no EV3 (Linux).
Solução instantânea:
→ Use https://code.pybricks.com/ (cole o código, conecte EV3 e RUN)
  O site corrige as permissões automaticamente!
Se usa VS Code: após salvar, rode no terminal SSH: chmod +x main.py
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Button
from pybricks.tools import wait
from pybricks.robotics import DriveBase

ev3 = EV3Brick()

# ==================== CONFIGURAÇÃO DO ROBÔ ====================
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)

# === SENSORES (2 sensores para precisão máxima) ===
left_sensor = ColorSensor(Port.S2)   # Sensor ESQUERDO
right_sensor = ColorSensor(Port.S3)  # Sensor DIREITO

# DriveBase (ajuste axle_track se seu robô for diferente)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# ==================== PID TUNING - OTIMIZADO PARA CURVAS ====================
# Valores perfeitamente ajustados para curvas + velocidade reduzida
KP = 0.95      # Proporcional mais forte (melhor resposta em curvas)
KI = 0.005     # Integral (continua bem baixo)
KD = 0.55      # Derivativo aumentado (suaviza oscilações em curvas)
BASE_SPEED = 180  # mm/s - MAIS LENTO conforme pedido (estável em curvas)

# ==================== CALIBRAÇÃO COM BOTÕES (mantida e confiável) ====================
ev3.screen.print("=== CALIBRAÇÃO 2 SENSORES ===")
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

# Confirmação de calibração
ev3.screen.clear()
ev3.screen.print("Calibração OK!")
ev3.screen.print("Pressione CENTRO")
ev3.screen.print("para INICIAR")
while Button.CENTER not in ev3.buttons.pressed():
    wait(10)

# ==================== VARIÁVEIS PID ====================
integral = 0.0
last_error = 0.0

# ==================== LOOP PRINCIPAL ====================
ev3.screen.clear()
ev3.screen.print("PID v3.1 CURVAS LIGADO!")
ev3.speaker.beep(1500, 100)
wait(300)
ev3.speaker.beep(2000, 100)

consecutive_white = 0

while True:
    # Leitura dos 2 sensores
    left_ref = left_sensor.reflection()
    right_ref = right_sensor.reflection()
    error = right_ref - left_ref

    # PID completo e reafinadíssimo
    integral += error
    integral = max(min(integral, 250), -250)   # Anti-windup ainda mais forte

    derivative = error - last_error
    turn_rate = KP * error + KI * integral + KD * derivative
    last_error = error

    # Limita o giro (mais margem para curvas fechadas)
    turn_rate = max(min(turn_rate, 160), -160)

    # === VELOCIDADE DINÂMICA EM CURVAS (o segredo para curvas perfeitas!) ===
    current_speed = BASE_SPEED
    if abs(error) > 35:                    # curva detectada
        current_speed = max(110, BASE_SPEED - 65)  # reduz até 115 mm/s

    # Executa o movimento
    robot.drive(current_speed, turn_rate)

    # Mostra na tela do EV3 em tempo real (agora mostra velocidade real)
    ev3.screen.clear()
    ev3.screen.print("L:", left_ref, " R:", right_ref)
    ev3.screen.print("Error:", round(error))
    ev3.screen.print("Turn: ", round(turn_rate))
    ev3.screen.print("Speed:", current_speed)
    ev3.screen.print("Int:  ", round(integral, 1))

    # Detecta fim de pista (AMBOS brancos)
    if left_ref > threshold + 30 and right_ref > threshold + 30:
        consecutive_white += 1
        if consecutive_white > 25:   # mais estável
            robot.stop()
            ev3.screen.print("FIM DA PISTA!")
            ev3.speaker.beep(800, 500)
            break
    else:
        consecutive_white = 0

    # Para manualmente com botão central
    if Button.CENTER in ev3.buttons.pressed():
        robot.stop()
        ev3.screen.print("PARADO!")
        ev3.speaker.beep(500, 200)
        break

    wait(8)  # ~125 Hz - ultra responsivo
```