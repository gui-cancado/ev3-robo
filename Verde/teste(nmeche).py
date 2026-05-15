#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait, StopWatch

ev3          = EV3Brick()
motor_a      = Motor(Port.A)
motor_d      = Motor(Port.B)
line_sensor  = ColorSensor(Port.S3)
green_sensor = ColorSensor(Port.S1)

# === CALIBRAÇÃO ===
ev3.screen.print("=== CALIBRAÇÃO ===")
ev3.screen.print("Coloque no PRETO")
ev3.screen.print("Pressione CENTRO")
while Button.CENTER not in ev3.buttons.pressed():
    wait(10)
black = line_sensor.reflection()
ev3.screen.print("PRETO:", black)
wait(800)
ev3.screen.print("Coloque no BRANCO")
ev3.screen.print("Pressione CENTRO")
while Button.CENTER not in ev3.buttons.pressed():
    wait(10)
white = line_sensor.reflection()
ev3.screen.print("BRANCO:", white)
wait(800)
threshold = (black + white) // 2
ev3.screen.print("Threshold:", threshold)
ev3.speaker.beep(1000, 200)
wait(1000)

# === PARÂMETROS PID ===
KP           = 0.5
KI           = 0.01
KD           = 0.35
INTEGRAL_MAX = 300
BASE_SPEED   = 25
CYCLE_MS     = 10

# === PARÂMETROS DO VERDE ===
# GREEN_BIAS       : magnitude do erro forçado durante a curva verde.
#                    Positivo = vira direita | Negativo = vira esquerda
# GREEN_HOLD_CYCLES: ciclos com bias TRAVADO no máximo (linha ignorada).
#                    Aumente se o robô largar a curva cedo demais.
# GREEN_DECAY      : quanto o bias cai por ciclo APÓS o hold terminar.
# GREEN_COOLDOWN   : ciclos ignorados depois que o bias zera.
GREEN_BIAS        = 90
GREEN_HOLD_CYCLES = 35    # ~350 ms de curva garantida sem interferência da linha
GREEN_DECAY       = 4     # decaimento suave depois do hold
GREEN_COOLDOWN    = 50    # ~500 ms de cooldown após a manobra

integral   = 0.0
last_error = 0.0
loop_count = 0
green_bias = 0.0
green_hold = 0            # ciclos restantes de hold (linha ignorada)
green_cd   = 0            # ciclos restantes de cooldown
timer      = StopWatch()

ev3.screen.clear()
ev3.screen.print("SEGUINDO LINHA")
ev3.speaker.beep(1500, 100)
wait(300)
ev3.speaker.beep(2000, 100)

while True:
    timer.reset()

    reflection = line_sensor.reflection()

    # ── Máquina de estado do verde ────────────────────────────
    #
    #  COOLDOWN → ignora o sensor (evita re-gatilho)
    #  HOLD     → bias travado, linha completamente ignorada
    #  DECAY    → bias caindo, linha volta a influenciar aos poucos
    #  IDLE     → sem verde, PID normal
    #
    if green_cd > 0:
        green_cd -= 1                          # ainda em cooldown

    elif green_hold > 0:
        green_hold -= 1                        # cumprindo hold obrigatório
        green_bias = float(GREEN_BIAS)         # mantém bias no máximo

        if green_hold == 0:
            # hold terminou → começa o decaimento
            pass

    elif green_bias > 0:
        # fase de decaimento
        green_bias = max(0.0, green_bias - GREEN_DECAY)
        if green_bias == 0.0:
            green_cd   = GREEN_COOLDOWN
            integral   = 0.0                   # limpa integral ao sair do verde
            last_error = 0.0

    else:
        # estado IDLE: verifica o sensor
        if green_sensor.color() == Color.GREEN:
            green_bias = float(GREEN_BIAS)
            green_hold = GREEN_HOLD_CYCLES
            integral   = 0.0                   # limpa integral ao entrar no verde
            last_error = 0.0
            ev3.speaker.beep(1200, 80)

    # ── Cálculo do erro ───────────────────────────────────────
    line_error = ((reflection - threshold) / (white - black)) * 100

    if green_bias > 0:
        # Durante hold e decaimento:
        # o erro É o bias — a linha não interfere.
        # Conforme o bias decai, a linha vai assumindo naturalmente.
        weight = green_bias / GREEN_BIAS       # 1.0 → 0.0
        error  = weight * GREEN_BIAS + (1.0 - weight) * line_error
    else:
        error = line_error

    # ── PID (inalterado) ──────────────────────────────────────
    if (error > 0) != (last_error > 0):
        integral = 0.0
    else:
        integral += error
        integral = max(min(integral, INTEGRAL_MAX), -INTEGRAL_MAX)

    derivative = error - last_error
    last_error = error

    turn = (KP * error) + (KI * integral) + (KD * derivative)
    turn = max(min(turn, BASE_SPEED), -BASE_SPEED)

    motor_a.dc(BASE_SPEED - turn)
    motor_d.dc(BASE_SPEED + turn)

    # ── Display ───────────────────────────────────────────────
    loop_count += 1
    if loop_count % 10 == 0:
        if green_hold > 0:
            action = "VERDE-HOLD"
        elif green_bias > 0:
            action = "VERDE-SAIDA"
        elif green_cd > 0:
            action = "COOLDOWN"
        else:
            action = "RETO" if abs(turn) < 10 else "CURVA"
        ev3.screen.clear()
        ev3.screen.print("Refl:", reflection)
        ev3.screen.print("Err:", round(error, 1))
        ev3.screen.print("Turn:", round(turn, 1))
        ev3.screen.print("Acao:", action)

    # ── Parada por botão ──────────────────────────────────────
    if Button.CENTER in ev3.buttons.pressed():
        motor_a.dc(0)
        motor_d.dc(0)
        ev3.screen.clear()
        ev3.screen.print("PARADO!")
        ev3.speaker.beep(500, 300)
        break

    elapsed = timer.time()
    if elapsed < CYCLE_MS:
        wait(CYCLE_MS - elapsed)
