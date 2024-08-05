import time
import board
import busio
from digitalio import DigitalInOut, Direction
from mfrc522 import SimpleMFRC522

# Pines del lector RFID
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.D10)
cs.direction = Direction.OUTPUT

# Inicialización del lector RFID
rfid = SimpleMFRC522(spi, cs)

# Configuración del pin para el LED
led = DigitalInOut(board.D2)
led.direction = Direction.OUTPUT

def main():
    while True:
        try:
            # Comprueba la presencia de una tarjeta
            id, text = rfid.read()
            if id:
                print("UID tag: %s" % id)
                print("Text: %s" % text)

                # Encendemos el led y lo apagamos.
                led.value = True
                time.sleep(0.3)
                led.value = False
                time.sleep(1.0)
        except Exception as e:
            print("Error: ", e)

if __name__ == "__main__":
    main()
