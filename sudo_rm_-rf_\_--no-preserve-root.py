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

vl = 0 #constante que define a velocidade dos motores
gb = 0 #o quanto o robô deve virar para fazer a próxima leitura de distancia
ag = 0 #alcance da garra
gn = gb * -1
while True:
    d3 = sri.distance()
    if d3> d2 & d1 > d2:
        mte.run_angle(speed=vl, rotation_angle=gn, wait=False)
        mtd.run_angle(speed=vl, rotation_angle=gb)
        while sri.distance() >= ag:
            mte.run_angle(speed=vl, rotation_angle=gb, wait=False)
            mtd.run_angle(speed=vl, rotation_angle=gb)
        #faça a garra pegar a bola
        d1 = 0
        d2 = 0
        d3 = 0

    d1 = d2
    d2 = d3
    mte.run_angle(speed=vl, rotation_angle=gb, wait=False)
    mtd.run_angle(speed=vl, rotation_angle=gn)