#!/usr/bin/env pybricks-micropython
"""
╔══════════════════════════════════════════════════════════════╗
║      SEGUIDOR DE LINHA PID — EV3 + Pybricks                  ║
║      Recursos:                                                ║
║        • PID estável em linha reta                            ║
║        • Detecção de cruzamentos (+ / T / transversal)        ║
║        • Detecção de cor VERDE com curva programada           ║
╚══════════════════════════════════════════════════════════════╝
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Button, Color   # <── Color adicionado
from pybricks.tools import wait, StopWatch

# ══════════════════════════════════════════════════════════════
#  HARDWARE
# ══════════════════════════════════════════════════════════════
ev3        = EV3Brick()
motor_a    = Motor(Port.A)          # Motor ESQUERDO
motor_d    = Motor(Port.B)          # Motor DIREITO
line_sensor = ColorSensor(Port.S3)  # Sensor de cor/reflexão


# ══════════════════════════════════════════════════════════════
#  CALIBRAÇÃO
# ══════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════
#  PARÂMETROS PID
# ══════════════════════════════════════════════════════════════
KP           = 0.5
KI           = 0.01
KD           = 0.35
INTEGRAL_MAX = 300
BASE_SPEED   = 25
CYCLE_MS     = 10    # Tempo de ciclo fixo (ms)


# ══════════════════════════════════════════════════════════════
#  PARÂMETROS DE DETECÇÃO DE CRUZAMENTO
#  ──────────────────────────────────────────────────────────
#  Em linha normal, o sensor flutua perto do 'threshold'.
#  Num cruzamento, o sensor fica TOTALMENTE sobre o preto por
#  vários ciclos seguidos (faixa larga de tinta preta).
#
#  CROSS_THRESHOLD: limite de reflexão que define "tudo preto".
#    Ajuste se houver falsos positivos em curvas fechadas.
#    Sugestão: 30–40% do intervalo (black → threshold).
#
#  CROSS_CONFIRM_CYCLES: ciclos consecutivos abaixo do limiar
#    necessários para confirmar o cruzamento (~80 ms a 10 ms/ciclo).
#    Aumente se tiver falsos positivos; diminua se perder cruzamentos.
# ══════════════════════════════════════════════════════════════
CROSS_THRESHOLD     = black + int((threshold - black) * 0.25)
CROSS_CONFIRM_CYCLES = 12

# ── Debounce pós-evento (evita re-detectar o mesmo cruzamento/verde)
# 50 ciclos = ~500 ms
DEBOUNCE_CYCLES = 50


# ══════════════════════════════════════════════════════════════
#  PARÂMETROS DE CURVA VERDE
#  ──────────────────────────────────────────────────────────
#  Quando detectado VERDE, o robô:
#    1. Avança GREEN_ADVANCE_MS para se centralizar no cruzamento.
#    2. Gira no lugar por GREEN_TURN_MS.
#
#  COLOR_CHECK_EVERY: checa cor a cada N ciclos do PID.
#    N=5 → a cada 50 ms. Reduzir pode capturar verde mais rápido,
#    mas aumenta carga de processamento.
#
#  GREEN_TURN_DIR: 1 = vira à ESQUERDA, -1 = vira à DIREITA.
#
#  GREEN_TURN_MS: tempo do giro. Ajuste para obter ~90°.
#    Depende de: velocidade dos motores, peso do robô, superfície.
# ══════════════════════════════════════════════════════════════
COLOR_CHECK_EVERY = 5
GREEN_ADVANCE_MS  = 350   # ms para avançar antes de girar
GREEN_TURN_MS     = 580   # ms de giro (~90° — ajuste conforme robô)
GREEN_TURN_DIR    = 1     # 1 = esquerda | -1 = direita


# ══════════════════════════════════════════════════════════════
#  FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════
def stop_motors():
    """Para ambos os motores imediatamente."""
    motor_a.dc(0)
    motor_d.dc(0)


def reset_pid():
    """Zera o estado do PID (chame após qualquer manobra)."""
    global integral, last_error, cross_counter
    integral      = 0.0
    last_error    = 0.0
    cross_counter = 0


def handle_crossing():
    """
    Executado ao detectar um cruzamento (+ / T / linha transversal).

    Comportamento padrão: sinaliza e avança em frente pelo cruzamento.
    ─────────────────────────────────────────────────────────────────
    PERSONALIZE aqui de acordo com as regras do seu circuito:
      • Girar sempre à direita → motor_a.dc(-BASE_SPEED), motor_d.dc(BASE_SPEED)
      • Parar e aguardar botão → while Button.CENTER not in ev3.buttons.pressed(): wait(10)
      • Contar cruzamentos e agir diferente no 3º → use uma variável global
    """
    stop_motors()
    ev3.screen.clear()
    ev3.screen.print("** CRUZAMENTO **")
    ev3.speaker.beep(700, 150)
    wait(100)

    # Avança para sair completamente do cruzamento antes de retomar o PID
    motor_a.dc(BASE_SPEED)
    motor_d.dc(BASE_SPEED)
    wait(450)

    stop_motors()
    wait(100)
    ev3.screen.clear()
    ev3.screen.print("SEGUINDO LINHA")


def handle_green():
    """
    Executado ao detectar a cor VERDE.

    Sequência:
      1. Para os motores.
      2. Avança GREEN_ADVANCE_MS ms para centralizar no cruzamento.
      3. Gira GREEN_TURN_MS ms (direção = GREEN_TURN_DIR).
      4. Retoma o PID.
    """
    stop_motors()
    ev3.screen.clear()
    ev3.screen.print("** VERDE! **")
    ev3.screen.print("Curva programada")
    ev3.speaker.beep(1200, 150)
    wait(150)
    ev3.speaker.beep(1500, 150)
    wait(100)

    # 1. Avança para o centro do cruzamento
    motor_a.dc(BASE_SPEED)
    motor_d.dc(BASE_SPEED)
    wait(GREEN_ADVANCE_MS)

    # 2. Gira no lugar
    spd = int(BASE_SPEED * 1.2)          # ligeiramente mais rápido para girar
    motor_a.dc(-spd * GREEN_TURN_DIR)
    motor_d.dc( spd * GREEN_TURN_DIR)
    wait(GREEN_TURN_MS)

    stop_motors()
    wait(200)
    ev3.screen.clear()
    ev3.screen.print("SEGUINDO LINHA")


# ══════════════════════════════════════════════════════════════
#  ESTADO INICIAL DO PID
# ══════════════════════════════════════════════════════════════
integral        = 0.0
last_error      = 0.0
loop_count      = 0
cross_counter   = 0   # ciclos consecutivos com reflexão abaixo de CROSS_THRESHOLD
debounce_counter = 0  # ciclos de "imunidade" após um evento especial

timer = StopWatch()

ev3.screen.clear()
ev3.screen.print("SEGUINDO LINHA")
ev3.speaker.beep(1500, 100)
wait(300)
ev3.speaker.beep(2000, 100)


# ══════════════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ══════════════════════════════════════════════════════════════
while True:
    timer.reset()

    # ── Leitura de reflexão ─────────────────────────────────
    reflection = line_sensor.reflection()

    # ── Decrementa debounce ─────────────────────────────────
    if debounce_counter > 0:
        debounce_counter -= 1

    # ── Verificação de cor VERDE (a cada COLOR_CHECK_EVERY ciclos) ──
    #    Só checa se não estiver em período de debounce.
    #    Prioridade: VERDE > CRUZAMENTO > PID normal
    if debounce_counter == 0 and (loop_count % COLOR_CHECK_EVERY == 0):
        detected_color = line_sensor.color()
        if detected_color == Color.GREEN:
            handle_green()
            reset_pid()
            debounce_counter = DEBOUNCE_CYCLES
            loop_count += 1
            continue   # volta ao topo; timer será resetado

    # ── Detecção de cruzamento ──────────────────────────────
    #    Acumula ciclos com reflexão muito baixa (tudo preto).
    if debounce_counter == 0 and reflection < CROSS_THRESHOLD:
        cross_counter += 1
    else:
        cross_counter = 0   # qualquer leitura normal zera o contador

    if cross_counter >= CROSS_CONFIRM_CYCLES:
        handle_crossing()
        reset_pid()
        debounce_counter = DEBOUNCE_CYCLES
        loop_count += 1
        continue   # volta ao topo

    # ── PID ─────────────────────────────────────────────────
    # Erro normalizado: -100 (totalmente no branco) a +100 (totalmente no preto)
    error = ((reflection - threshold) / (white - black)) * 100

    # Anti-windup: zera integral ao cruzar a linha
    if (error > 0) != (last_error > 0):
        integral = 0.0
    else:
        integral += error
    integral = max(min(integral, INTEGRAL_MAX), -INTEGRAL_MAX)

    derivative = error - last_error
    last_error  = error

    turn = (KP * error) + (KI * integral) + (KD * derivative)
    turn = max(min(turn, BASE_SPEED), -BASE_SPEED)

    motor_a.dc(BASE_SPEED - turn)
    motor_d.dc(BASE_SPEED + turn)

    # ── Display (a cada 10 ciclos ≈ 100 ms) ─────────────────
    loop_count += 1
    if loop_count % 10 == 0:
        action = "RETO  " if abs(turn) < 10 else "CURVA "
        ev3.screen.clear()
        ev3.screen.print("Refl:", reflection)
        ev3.screen.print("Err :", round(error, 1))
        ev3.screen.print("Turn:", round(turn, 1))
        ev3.screen.print("Cross cnt:", cross_counter)
        ev3.screen.print("Acao:", action)

    # ── Parada de emergência por botão ──────────────────────
    if Button.CENTER in ev3.buttons.pressed():
        stop_motors()
        ev3.screen.clear()
        ev3.screen.print("PARADO!")
        ev3.speaker.beep(500, 300)
        break

    # ── Ciclo fixo ──────────────────────────────────────────
    elapsed = timer.time()
    if elapsed < CYCLE_MS:
        wait(CYCLE_MS - elapsed)
