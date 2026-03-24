#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

ev3          = EV3Brick()
motor_a      = Motor(Port.A)
motor_d      = Motor(Port.D)
line_sensor  = ColorSensor(Port.S3)   # sensor de reflectância (PID)
   # sensor esquerdo  (cor)
right_sensor = ColorSensor(Port.S4)   # sensor direito   (cor)

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO PID  ← edite só aqui
# ─────────────────────────────────────────────
PID_CONFIG = {
    "kp"           : 0.5,
    "ki"           : 0.02,
    "kd"           : 0.5,   
    "integral_max" : 300,
    "base_speed"   : 25,
    "turn_max"     : 30,
}

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DE CURVAS VERDES  ← edite só aqui
# ─────────────────────────────────────────────
GREEN_CONFIG = {
    "advance_speed" : 25,   
    "advance_time"  : 200,    
    "turn_outer"    : 35,     
    "turn_inner"    :-15,     
    "turn_time"     : 250,    
    "settle_time"   : 500,    
}


pid_state = {"integral": 0.0, "last_error": 0}

def pid_reset():
    pid_state["integral"]   = 0.0
    pid_state["last_error"] = 0


def pid_step(reflection, threshold, cfg, state):
    """
    Executa um passo do controlador PID.
    Retorna o valor de 'turn' calculado.
    """
    error             = reflection - threshold
    state["integral"] = max(
        min(state["integral"] + error, cfg["integral_max"]),
        -cfg["integral_max"]
    )
    derivative        = error - state["last_error"]
    state["last_error"] = error

    turn = (cfg["kp"] * error) + (cfg["ki"] * state["integral"]) + (cfg["kd"] * derivative)
    turn = max(min(turn, cfg["turn_max"]), -cfg["turn_max"])
    return turn, error, state["integral"], derivative


def handle_green_left(gcfg):
    """Curva verde detectada pelo sensor ESQUERDO."""
    motor_a.dc(gcfg["advance_speed"])
    motor_d.dc(gcfg["advance_speed"])
    wait(gcfg["advance_time"])
    motor_a.dc(gcfg["turn_outer"])
    motor_d.dc(gcfg["turn_inner"])
    wait(gcfg["turn_time"])
    wait(gcfg["settle_time"])
    pid_reset()                          


def handle_green_right(gcfg):
    """Curva verde detectada pelo sensor DIREITO."""
    motor_a.dc(gcfg["advance_speed"])
    motor_d.dc(gcfg["advance_speed"])
    wait(gcfg["advance_time"])
    motor_a.dc(gcfg["turn_inner"])
    motor_d.dc(gcfg["turn_outer"])
    wait(gcfg["turn_time"])
    wait(gcfg["settle_time"])
    pid_reset()


def stop_all(msg="PARADO!"):
    motor_a.dc(0)
    motor_d.dc(0)
    ev3.screen.clear()
    ev3.screen.print(msg)
    ev3.speaker.beep(500, 200)



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


ev3.screen.clear()
ev3.screen.print("SEGUINDO LINHA")
ev3.speaker.beep(1500, 100)
wait(300)
ev3.speaker.beep(2000, 100)

while True:
    # --- leitura de cor (prioridade sobre PID) ---
    left_color  = left_sensor.color()
    right_color = right_sensor.color()

    left_green  = left_color  == Color.GREEN
    right_green = right_color == Color.GREEN
    both_black  = (left_color == Color.BLACK) and (right_color == Color.BLACK)
    both_green  = left_green and right_green

    
    if both_green:
        stop_all("OBJETIVO FEITO")
        break

    elif both_black:
        stop_all("FIM DE PISTA")
        break

    elif left_green:
        action = "CURVA VERDE ESQ"
        ev3.screen.clear()
        ev3.screen.print(action)
        handle_green_left(GREEN_CONFIG)

    elif right_green:
        action = "CURVA VERDE DIR"
        ev3.screen.clear()
        ev3.screen.print(action)
        handle_green_right(GREEN_CONFIG)

    else:
        
        reflection = line_sensor.reflection()
        turn, error, integral, derivative = pid_step(
            reflection, threshold, PID_CONFIG, pid_state
        )
        motor_a.dc(PID_CONFIG["base_speed"] - turn)
        motor_d.dc(PID_CONFIG["base_speed"] + turn)
        action = "RETO" if abs(turn) < 5 else "AJUSTE"

        # --- display ---
        ev3.screen.clear()
        ev3.screen.print("Refl:", reflection)
        ev3.screen.print("Erro:", round(error))
        ev3.screen.print("Integ:", round(integral))
        ev3.screen.print("Deriv:", round(derivative))
        ev3.screen.print("Turn:", round(turn))
        ev3.screen.print("Acao:", action)

    
    if Button.CENTER in ev3.buttons.pressed():
        stop_all()
        break

    wait(10)
