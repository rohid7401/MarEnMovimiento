import board
import mfrc522

def escribir_tarjeta():
    lector = mfrc522.MFRC522(
        board.SCK,  # Pin SCK
        board.MOSI,  # Pin MOSI
        board.MISO,  # Pin MISO
        board.IO4,   # Pin RST
        board.IO5,   # Pin SDA
    )

    lector.set_antenna_gain(0x07 << 4)

    print("\n Acérquese la tarjeta al lector para escribir datos en la dirección 0x08 \n")
    
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
                            datos_a_escribir = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
                            estado = lector.write(8, datos_a_escribir)
                            lector.stop_crypto1()

                            if estado == lector.OK:
                                print("Datos escritos en la tarjeta")
                            else:
                                print("Error al escribir datos en la tarjeta")
                        else:
                            print("Error de autenticación")
                    else:
                        print("Error al seleccionar la tarjeta")

    except KeyboardInterrupt:
        print("Detenido por Ctrl+C")



while True:
    escribir_tarjeta()