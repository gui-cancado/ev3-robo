from pybricks.hubs import EV3Brick
from pybricks.parameters import Port
from pybricks.iodevices import I2CDevice

# Inicializa o hub do robô
ev3 = EV3Brick()

# Mapeia as portas de sensores físicas do robô
portas_robo = [Port.S1, Port.S2, Port.S3, Port.S4]

# Endereços I2C padrões dos 3 canais internos do multiplexador da mindsensors
enderecos_mux = [0x50, 0x51, 0x52]

print("Iniciando varredura nas portas do robô...\n")
multiplexador_encontrado = False

for porta in portas_robo:
    canais_detectados = []
    
    for addr in enderecos_mux:
        try:
            # Inicializa a tentativa de conexão I2C na porta atual
            dispositivo = I2CDevice(porta, addr)
            
            # Registrador 0x08 guarda a assinatura do fabricante (Vendor ID)
            dispositivo.write(bytes([0x08]))
            vendor_bytes = dispositivo.read(8)
            vendor_name = vendor_bytes.decode('utf-8').strip()
            
            # Se a assinatura bater com "mindsens", validamos o canal
            if "mindsens" in vendor_name.lower():
                # Opcional: Lê o modelo do dispositivo no registrador 0x10
                dispositivo.write(bytes([0x10]))
                device_bytes = dispositivo.read(8)
                device_name = device_bytes.decode('utf-8').strip()
                
                canais_detectados.append((addr, device_name))
        except Exception:
            # Ignora erros caso a porta esteja vazia ou use outro tipo de sensor
            continue
            
    if canais_detectados:
        multiplexador_encontrado = True
        print(f"[SUCESSO] Multiplexador mindsensors detectado na {porta}!")
        for idx, (addr, dev_name) in enumerate(canais_detectados):
            print(f"  -> Canal {idx + 1} do MUX Ativo: Endereço I2C {hex(addr)} | Tipo: {dev_name}")
        print("-" * 50)

if not multiplexador_encontrado:
    print("[AVISO] Nenhum multiplexador mindsensors foi localizado nas portas do robô.")
