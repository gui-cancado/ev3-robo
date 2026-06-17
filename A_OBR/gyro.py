from pybricks.hubs import EV3Brick
from pybricks.parameters import Port
from pybricks.iodevices import I2CDevice
import time

# Inicializa o bloco EV3
ev3 = EV3Brick()

# DEFINIÇÕES DO PROTOCOLO MINDSENSORS
PORTA_ROBO = Port.S1      # Ajuste para a porta física do bloco onde o MUX está conectado
ENDERECO_MUX_CH2 = 0x51   # Endereço fixo do Canal 2 solicitado
REG_MODO = 0x52           # Registrador para configurar o sensor
REG_DADO = 0x54           # Registrador de onde leremos o ângulo do Giroscópio

print("Conectando ao multiplexador no endereço 0x51...")

try:
    # Abre o canal de comunicação I2C direto com o endereço 0x51
    mux_ch2 = I2CDevice(PORTA_ROBO, ENDERECO_MUX_CH2)
    
    # Configura o Giroscópio para o Modo 0 (Medição de Ângulo)
    # Enviamos o registrador seguido do valor do modo desejado
    mux_ch2.write(bytes([REG_MODO, 0x00]))
    time.sleep(0.1)  # Pequena pausa necessária para o hardware processar a configuração
    
    print("[SUCESSO] Giroscópio configurado no Modo Ângulo!")
    print("Gire o sensor para testar as leituras. Pressione Ctrl+C para parar.\n")
    
    while True:
        # Aponta o ponteiro I2C para o registrador de dados e requisita 2 bytes
        mux_ch2.write(bytes([REG_DADO]))
        dados = mux_ch2.read(2)
        
        # Converte os bytes recebidos em ordem Little-Endian
        angulo = dados[0] + (dados[1] << 8)
        
        # Converte para inteiro sinalizado de 16 bits para interpretar ângulos negativos corretamente
        if angulo >= 32768:
            angulo -= 65536
            
        print(f"Ângulo Atual: {angulo}°")
        time.sleep(0.1)

except Exception as erro:
    print(f"[ERRO] Não foi possível ler o endereço 0x51.")
    print(f"Verifique se o cabo do MUX está firme e se o Giroscópio está na porta C2. Detalhes: {erro}")
