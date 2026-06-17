#!/usr/bin/env pybricks-micropython
from pybricks.iodevices import I2CDevice
from pybricks.parameters import Port
from pybricks.hubs import EV3Brick
from pybricks.tools import wait

ev3 = EV3Brick()

# Testa as 4 portas e todos os endereços I2C possíveis (0x08–0x77)
for port in [Port.S1, Port.S2, Port.S3, Port.S4]:
    ev3.screen.clear()
    ev3.screen.print("Escaneando", str(port))
    found = []

    for addr in range(0x08, 0x78):
        try:
            dev = I2CDevice(port, addr)
            dev.read(reg=0x00, length=1)
            found.append(hex(addr))
        except OSError:
            pass

    if found:
        ev3.screen.clear()
        ev3.screen.print("Porta:", str(port))
        for a in found:
            ev3.screen.print("Addr:", a)
        ev3.speaker.beep(1000, 300)
        wait(4000)
    else:
        ev3.screen.print("Nada encontrado")
        wait(1000)

ev3.screen.clear()
ev3.screen.print("Scan completo")
