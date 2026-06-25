#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, InfraredSensor
from pybricks.parameters import port
from pybricks.tools import wait

ev3 = EV3Brick
mte = Motor(Port.B)
mtd = Motor(Port.C)
sri = InfraredSensor(port.S4)

d1 = 0
d2 = 0
d3 = 0

ap = 5 * 360 / 3.14 * 5 #distancia (em centimetros) em que o robo vai se aproximar da bolinha
vl = 200 #constante que define a velocidade dos motores
gb = 60 #o quanto o robô deve virar para fazer a próxima leitura de distancia
ag = 5 #alcance da garra
gn = gb * -1
while True:
    d3 = sri.distance() #le e armazena a distancia do sensor infravermelho
    if d3> d2 and d1 > d2:

        #volta para poder olhar a bolinha dnv
        mte.run_angle(speed=vl, rotation_angle=gn, wait=False)
        mtd.run_angle(speed=vl, rotation_angle=gb)

        #se aproxima da bolinha
        mte.run_angle(speed=vl, rotation_angle=ap, wait=False)
        mtd.run_angle(speed=vl, rotation_angle=ap)

        #verifica se o robô ja consegue alcançar a bolinha
        if sri.distance() >= ag:
            wait(10)
            #faça a garra pegar a bola, mas por enquanto, vou fazer o robo procurar outra
        else:

            #volta para procurar a bolinha dnv
            mte.run_angle(speed=vl, rotation_angle=(gn * 2), wait=False)
            mtd.run_angle(speed=vl, rotation_angle=(gb * 2))

        #reseta as variaveis
        d1 = 0
        d2 = 0
        d3 = 0

    d1 = d2
    d2 = d3
    mte.run_angle(speed=vl, rotation_angle=gb, wait=False)
    mtd.run_angle(speed=vl, rotation_angle=gn)
    wait(10)
