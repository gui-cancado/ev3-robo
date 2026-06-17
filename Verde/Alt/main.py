#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait, StopWatch
import verde

ev3 = EV3Brick()
motor_a = Motor(Port.A)
motor_b = Motor(Port.B)
line_sensor = ColorSensor(Port.S3)
color_sensor = ColorSensor(Port.S4)

reflecao = line_sensor.reflection()


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
CYCLE_MS     = 10          # Tempo de ciclo fixo em ms

integral   = 0.0
last_error = 0.0
loop_count = 0
timer      = StopWatch()

ev3.screen.clear()
ev3.screen.print("SEGUINDO LINHA")
ev3.speaker.beep(1500, 100)
wait(300)
ev3.speaker.beep(2000, 100)
score = 0
#score_final = 0
'''
def correcao_verde_azul():
    global score_final
    global action
    if color_sensor.color() == Color.GREEN:
        score+=2
    elif color_sensor.color() == Color.BLUE:
        score+=1
    else:
        score-=1
    
    if action != 'RETO':
        score = 0
   
    if score < 0:
        score = 0
    elif score > 10: score = 10
    
    return score
'''

action = ''
'''
def verde_check():
    global score
    global action
    #if action == 'RETO':
    #    wait(500)
    #if action == 'RETO':
    #    #if color_sensor.color() == Color.GREEN or Color.BLUE:
    if score > 8  and line_sensor.reflection() < (black*1.25):
        retorno_180()
        action = '180 Caralho'
        score = 0
    elif score > 8:
        virar_esquerda()
        action = 'TurnLeft'
        score = 0
        #elif (color_sensor.color() == Color.GREEN or Color.BLUE) and line_sensor.reflection() < 20 :
        #elif correcao_verde_azul() > 5 and line_sensor.reflection() < 20:
        #    retorno_180()
'''
#score = 0
while True:
    timer.reset()

    reflection = line_sensor.reflection()

    # Erro normalizado -100 a +100
    error = ((reflection - threshold) / (white - black)) * 100

    # Anti-windup: zera integral ao cruzar a linha
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
    motor_b.dc(BASE_SPEED + turn)

    # Update score from detected color
    score = verde.correcao_verde_azul(score, color_sensor)
    #score = 0
    '''
    if color_sensor.color() == Color.GREEN:
        score+=2
    elif color_sensor.color() == Color.BLUE:
        score+=1
    else:
        score-=1
   
    if score < 0:
        score = 0
    elif score > 10:
        score = 10
    '''

    
    
    # Display a cada 10 ciclos (~100ms)
    loop_count += 1
    if loop_count % 10 == 0:
        #action = "RETO" if abs(turn) < 10 else "CURVA"
        if abs(turn) < 10:
            action = 'RETO'
        elif turn < 0:
            action = 'turnRight'
        else:
            action = 'turnLeft'
        
        ev3.screen.clear()
        ev3.screen.print("Refl:", reflection)
        ev3.screen.print("Err:", round(error, 1))
        ev3.screen.print("Turn:", round(turn, 1))
        ev3.screen.print("Acao:", action)
        ev3.screen.print("Score: ", score)
        ev3.screen.print("Cor: ", color_sensor.color())

    # VERDE: handle green/blue corrections and maneuvers
    score, action = verde.verde_check(score, action, black, reflecao, motor_a, motor_b)
    
    #correcao_verde_azul()
    # Parada por botão
    if Button.CENTER in ev3.buttons.pressed():
        motor_a.dc(0)
        motor_b.dc(0)
        ev3.screen.clear()
        ev3.screen.print("PARADO!")
        ev3.speaker.beep(500, 300)
        break

    # Ciclo fixo
    elapsed = timer.time()
    if elapsed < CYCLE_MS:
        wait(CYCLE_MS - elapsed)
