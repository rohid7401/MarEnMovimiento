import time
import board
import busio #?
from lcd import LCD
from i2c_pcf8574_interface import I2CPCF8574Interface
import mfrc522
from ideaboard import IdeaBoard

# Configuración de la pantalla LCD
lcd_columns = 16
lcd_rows = 2
i2c = board.I2C()
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=lcd_rows, num_cols=lcd_columns)

# Configuración del lector RFID
lector = mfrc522.MFRC522(
    board.SCK,
    board.MOSI,
    board.MISO,
    board.IO4,
    board.IO5,
)
lector.set_antenna_gain(0x07 << 4)

# Inicialización de IdeaBoard
ib = IdeaBoard()

# Inicialización de variables
num_geisers = 0
frecuencia = 0.0
ultimo_geiser = time.time()

# Mensaje a rotar
mensaje = "MarEnMovimiento   "  # Espacios adicionales para darle margen de rotación

# Función para mostrar mensaje "MarEnMovimiento"
def mostrar_mensaje():
    for i in range(len(mensaje)):
        lcd.clear()
        lcd.print(mensaje[i:i+16])
        time.sleep(0.2)  # Tiempo de espera para el efecto de desplazamiento

# Función para mostrar los datos del géiser y la frecuencia en la pantalla LCD
def mostrar_datos():
    lcd.clear()
    lcd.set_cursor_pos(0, 0)
    lcd.print(f"Géiser #{num_geisers}")
    lcd.set_cursor_pos(1, 0)
    lcd.print(f"Frecuencia: ~{frecuencia:.2f}s")

# Función para leer y actualizar datos en la tarjeta RFID
def leer_tarjeta():
    global num_geisers, frecuencia, ultimo_geiser
    try:
        estado, tipo_tarjeta = lector.request(lector.REQIDL)

        if estado == lector.OK:
            estado, uid = lector.anticoll()

            if estado == lector.OK:
                print("Señal detectada")
                if lector.select_tag(uid) == lector.OK:
                    clave = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                    if lector.auth(lector.AUTHENT1A, 8, clave, uid) == lector.OK:
                        # Leer datos de la tarjeta (número de géiseres y frecuencia)
                        datos = lector.read(8)
                        num_geisers = datos[0] 
                        lector.stop_crypto1()

                        # Calcular la nueva frecuencia basada en el tiempo desde la última erupción
                        tiempo_actual = time.time()
                        tiempo_entre_geisers = tiempo_actual - ultimo_geiser
                        ultimo_geiser = tiempo_actual
                        
                        # Actualizar datos en la tarjeta
                        num_geisers += 1
                        frecuencia = tiempo_entre_geisers  # Actualizar frecuencia con el tiempo entre erupciones
                        datos_a_escribir = [num_geisers, int(frecuencia)] + [0] * 6
                        lector.auth(lector.AUTHENT1A, 8, clave, uid)
                        lector.write(8, bytes(datos_a_escribir))
                        lector.stop_crypto1()

    except KeyboardInterrupt:
        print("Detenido por Ctrl+C")

# Bucle principal
mostrar_mensaje()
ultimo_cambio = time.monotonic()

while True:
    tiempo_actual = time.monotonic()
    # Cada 12 segundos muestra los datos durante 4 segundos
    if tiempo_actual - ultimo_cambio >= 12:
        mostrar_datos()
        time.sleep(4)
        mostrar_mensaje()
        ultimo_cambio = tiempo_actual
    
    # Siempre está escuchando por una tarjeta RFID
    leer_tarjeta()
    time.sleep(0.1)
