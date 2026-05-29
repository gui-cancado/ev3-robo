from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, InfraredSensor
from pybricks.parameters import Port
from pybricks.tools import wait

ev3 = EV3Brick()

Am = 0 # variável para controle do ângulo de movimento dos motores para frente e para trás
Ag = 0 # alcance da garra para pegar o objeto
Ar = 0 # variável para controle do ângulo de rotação dos motores para olhar ao redor
Me = Motor(Port.B) # declaração da porta do motor esquerdo
Md = Motor(Port.A) # declaração da porta do motor direito
Si = InfraredSensor(Port.S1) # declaração da porta do sensor infravermelho
V = 20 # velocidade dos motores em graus por segundo
D1 = 0 # distância medida pelo sensor infravermelho
D2 = 0 # distância medida pelo sensor infravermelho
D3 = 0 # distância medida pelo sensor infravermelho
while True:
    D1 = Si.distance()
    Md.run_angle(V, Ar)
    Me.run_angle(V, -Ar)
    D2 = Si.distance()
    Md.run_angle(V, Ar)
    Me.run_angle(V, -Ar)
    D3 = Si.distance()
    if D1 < D2 and D2 > D3:
        while D2 > Ag:
            Me.run_angle(V, Am)
            Md.run_angle(V, Am)
            D2 = Si.distance()
    Md.run_angle(V, -Ar)
    Me.run_angle(V, Ar)
