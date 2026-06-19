#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor, UltrasonicSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait

# Inicializa o bloco EV3
ev3 = EV3Brick()

# Configuração dos motores nas portas A e B, conforme o bloco inicial
motor_a = Motor(Port.A)
motor_b = Motor(Port.B)

# Configuração dos sensores nas portas 1 a 4, conforme indicam os números nos blocos
ultrassonico_1 = UltrasonicSensor(Port.S1)
giroscopio_2   = GyroSensor(Port.S2)
sensor_cor_3   = ColorSensor(Port.S3)
sensor_cor_4   = ColorSensor(Port.S4)

# Funções auxiliares para replicar os blocos de movimento originais (%)
def iniciar_movimento_reto(velocidade_pct):
    motor_a.dc(velocidade_pct)
    motor_b.dc(velocidade_pct)

def iniciar_movimento_tanque(vel_a_pct, vel_b_pct):
    motor_a.dc(vel_a_pct)
    motor_b.dc(vel_b_pct)

# repita para sempre
while True:
    # Lemos as cores atuais para evitar leituras inconsistentes no meio da verificação
    cor_3 = sensor_cor_3.color()
    cor_4 = sensor_cor_4.color()
    angulo = giroscopio_2.angle()

    # 1. se cor 3 = preto E cor 4 = preto
    if cor_3 == Color.BLACK and cor_4 == Color.BLACK:
        iniciar_movimento_reto(25)
        wait(500) # espera 0.5 s

    # 2. senão, se cor 3 = verde E cor 4 = verde
    elif cor_3 == Color.GREEN and cor_4 == Color.GREEN:
        iniciar_movimento_tanque(75, -70)
        wait(1700) # espera 1.7 s

    # 3. senão, se ângulo <= -15 (equivalente a < -15 ou = -15)
    elif angulo <= -15:
        iniciar_movimento_reto(40)
        wait(200) # espera 0.2 s

    # 4. senão, se distância < 15 cm (150 mm)
    elif ultrassonico_1.distance() < 150:
        pass # O bloco correspondente na imagem não possui ações dentro dele

    # 5. senão, se cor 4 = preto
    elif cor_4 == Color.BLACK:
        iniciar_movimento_tanque(45, -45)

    # 6. senão, se cor 3 = preto
    elif cor_3 == Color.BLACK:
        iniciar_movimento_tanque(-45, 45)

    # 7. senão, se cor 3 = verde
    elif cor_3 == Color.GREEN:
        iniciar_movimento_reto(25)
        wait(200) # espera 0.2 s
        iniciar_movimento_tanque(-25, 45)
        wait(800) # espera 0.8 s
        iniciar_movimento_reto(25)

    # 8. senão, se cor 4 = verde
    elif cor_4 == Color.GREEN:
        iniciar_movimento_reto(25)
        wait(300) # espera 0.3 s
        iniciar_movimento_tanque(45, -25)
        wait(900) # espera 0.9 s
        iniciar_movimento_reto(25)

    # 9. senão, se ângulo < -30
    elif angulo < -30:
        giroscopio_2.reset_angle(0) # redefinir ângulo

    # 10. senão, se cor 3 = branco E cor 4 = branco
    elif cor_3 == Color.WHITE and cor_4 == Color.WHITE:
        iniciar_movimento_reto(25)

    # 11. senão final
    else:
        iniciar_movimento_reto(25)
