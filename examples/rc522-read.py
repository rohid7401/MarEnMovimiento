import time
import board
import mfrc522
from ideaboard import IdeaBoard


def leer_tarjeta():
    lector = mfrc522.MFRC522(
        board.SCK,  # Pin SCK
        board.MOSI,  # Pin MOSI
        board.MISO,  # Pin MISO
        board.IO4,   # Pin RST
        board.IO5,   # Pin SDA
    )

    lector.set_antenna_gain(0x07 << 4)


    print("\n Acérquese la tarjeta al lector para leer datos de la dirección 0x08 \n")
    try:
        while True:
            estado, tipo_tarjeta = lector.request(lector.REQIDL)

            if estado == lector.OK:
                estado, uid = lector.anticoll()

                if estado == lector.OK:
                    print("Nueva tarjeta detectada")
                    print("  - Tipo de tarjeta: 0x%02x" % tipo_tarjeta)
                    print("  - UID: 0x%02x%02x%02x%02x" % (uid[0], uid[1], uid[2], uid[3]))
                    print('')

                    if lector.select_tag(uid) == lector.OK:
                        clave = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                        if lector.auth(lector.AUTHENT1A, 8, clave, uid) == lector.OK:
                            datos = lector.read(8)
                            print("Datos de la dirección 8: %s" % datos)
                            lector.stop_crypto1()
                        else:
                            print("Error de autenticación")
                    else:
                        print("Error al seleccionar la tarjeta")

    except KeyboardInterrupt:
        print("Detenido por Ctrl+C")


while True:
    leer_tarjeta()