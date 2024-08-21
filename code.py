import time
import board
import busio 
from lcd import LCD
from i2c_pcf8574_interface import I2CPCF8574Interface
import mfrc522
from ideaboard import IdeaBoard
 
# Configuración de la pantalla LCD
lcd_columns = 16  # Número de columnas del LCD (caracteres por línea)
lcd_rows = 2      # Número de filas del LCD
i2c = board.I2C()  # Inicialización del bus I2C en los pines predeterminados
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=lcd_rows, num_cols=lcd_columns)
# Crea una instancia de la pantalla LCD utilizando la interfaz I2C
 
# Configuración del lector RFID
lector = mfrc522.MFRC522(
    board.SCK,  # Pin para la línea de reloj serial (SCK)
    board.MOSI, # Pin para la línea de datos (MOSI)
    board.MISO, # Pin para la línea de datos (MISO)
    board.IO4,  # Pin para la línea de reinicio (RST)
    board.IO5,  # Pin para la línea de selección de esclavo (SDA)
)
lector.set_antenna_gain(0x07 << 4)  # Ajuste de la ganancia de la antena para mejorar la sensibilidad

# Inicialización de IdeaBoard
ib = IdeaBoard()  # Inicializa la IdeaBoard, que gestiona el hardware en el proyecto

# Inicialización de variables
num_geisers = 0  # Variable para almacenar el número de géiseres detectados
frecuencia = 0.0  # Variable para almacenar la frecuencia (tiempo entre erupciones)
ultimo_geiser = time.time()  # Almacena el tiempo del último géiser detectado

# Mensaje a rotar
mensaje = "MarEnMovimiento   "  # Mensaje a mostrar en la pantalla LCD, con espacios para crear un efecto de desplazamiento
lenmsg = len(mensaje)  # Longitud del mensaje, incluyendo los espacios

# Función para mostrar mensaje "MarEnMovimiento"
def mostrar_mensaje():
    """
    Muestra un mensaje desplazado en la pantalla LCD. El mensaje se mueve de derecha a izquierda,
    creando un efecto de rotación.
    """
    lcd.clear()  # Limpia la pantalla antes de comenzar
    for i in range(lenmsg + lcd_columns):
        lcd.clear()
        # Determina el índice inicial de la subcadena y la longitud visible del mensaje
        inicio = i % lenmsg
        if inicio + lcd_columns <= lenmsg:
            lcd.print(mensaje[inicio:inicio + lcd_columns])  # Muestra una parte del mensaje
        else:
            lcd.print(mensaje[inicio:] + mensaje[:lcd_columns - (lenmsg - inicio)])  # Muestra la parte restante del mensaje en la siguiente vuelta
        time.sleep(0.3)  # Pausa para controlar la velocidad del desplazamiento del mensaje
 
# Función para mostrar los datos del géiser y la frecuencia en la pantalla LCD
def mostrar_datos():
    """
    Limpia la pantalla LCD y muestra el número de géiseres detectados y la frecuencia
    de erupción en segundos. La información se muestra en dos líneas:
    - Línea 1: Número de géiseres detectados.
    - Línea 2: Frecuencia (~tiempo entre erupciones) en segundos.
    """
    lcd.clear()  # Limpia la pantalla LCD
    lcd.set_cursor_pos(0, 0)  # Coloca el cursor en la primera fila, primer carácter
    lcd.print(f"Geiser #{num_geisers}")  # Muestra el número de géiseres detectados
    lcd.set_cursor_pos(1, 0)  # Coloca el cursor en la segunda fila, primer carácter
    lcd.print(f"Freq:~{frecuencia:.2f}")  # Muestra la frecuencia de erupción con dos decimales

# Función para mostrar un mensaje temporal en la pantalla LCD
def mostrar_mensaje_temporal(mensaje, duracion=1):
    """
    Muestra un mensaje específico en la pantalla LCD durante un tiempo determinado.
    Luego, limpia la pantalla.
    
    Parámetros:
    - mensaje: El mensaje que se mostrará en la pantalla LCD.
    - duracion: La cantidad de tiempo (en segundos) que el mensaje se mostrará antes de limpiar la pantalla.
    """
    lcd.clear()  # Limpia la pantalla LCD antes de mostrar el mensaje
    lcd.set_cursor_pos(0, 0)  # Coloca el cursor en la primera fila, primer carácter
    lcd.print(mensaje)  # Muestra el mensaje en la pantalla LCD
    time.sleep(duracion)  # Espera el tiempo especificado (duracion)
    lcd.clear()  # Limpia la pantalla LCD después de mostrar el mensaje

 
# Función para leer y actualizar datos en la tarjeta RFID
def leer_tarjeta():
    """
    Lee los datos almacenados en la tarjeta RFID y actualiza el número de géiseres detectados y la frecuencia.
    Primero, intenta autenticarse para leer los datos. Si tiene éxito, incrementa el número de géiseres y calcula
    la nueva frecuencia basada en el tiempo desde la última erupción. Luego, intenta autenticarse nuevamente para 
    escribir los datos actualizados en la tarjeta.

    Esta función maneja la detección de una tarjeta RFID, la lectura de los datos existentes, la actualización de los 
    datos, y la escritura de los datos actualizados en la tarjeta.
    """
    global num_geisers, frecuencia, ultimo_geiser  # Variables globales para almacenar el estado del sistema
    try:
        estado, tipo_tarjeta = lector.request(lector.REQIDL)  # Solicita la presencia de una tarjeta RFID

        if estado == lector.OK:
            estado, uid = lector.anticoll()  # Detecta la tarjeta y obtiene su UID

            if estado == lector.OK:
                mostrar_mensaje_temporal("Geiser Detectado")  # Muestra un mensaje temporal en la pantalla LCD

                if lector.select_tag(uid) == lector.OK:  # Selecciona la tarjeta detectada para realizar operaciones
                    clave = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]  # Clave predeterminada para la autenticación

                    # Intentar autenticación para lectura
                    if lector.auth(lector.AUTHENT1A, 8, clave, uid) == lector.OK:
                        datos = lector.read(8)  # Lee los datos del bloque 8 de la tarjeta
                        num_geisers = datos[0]  # Actualiza el número de géiseres con el valor leído
                        print(f"Data en tarjeta={datos}")  # Imprime los datos leídos para depuración

                        # Intentar autenticación nuevamente para escritura
                        if lector.auth(lector.AUTHENT1A, 8, clave, uid) == lector.OK:
                            num_geisers += 1  # Incrementa el número de géiseres detectados

                            # Calcular la nueva frecuencia basada en el tiempo desde la última erupción
                            tiempo_actual = time.time()
                            tiempo_entre_geisers = tiempo_actual - ultimo_geiser  # Calcula la frecuencia de erupciones
                            ultimo_geiser = tiempo_actual  # Actualiza el tiempo del último géiser detectado
                            frecuencia = tiempo_entre_geisers  # Actualiza la frecuencia con el tiempo calculado

                            # Preparar los datos a escribir en la tarjeta RFID
                            datos_a_escribir = bytearray([num_geisers, int(frecuencia)] + [0x00] * 14)
                            estado = lector.write(8, datos_a_escribir)  # Escribe los datos actualizados en la tarjeta
                            print(f"Nueva data ={datos_a_escribir}")  # Imprime los nuevos datos para depuración
                            lector.stop_crypto1()  # Finaliza la operación criptográfica

                            if estado == lector.OK:
                                print("Geiser Detectado")  # Confirma que la escritura fue exitosa
                            else:
                                print("Error en la escritura")  # Indica un error en la escritura de datos
                        else:
                            print("Error de autenticación al escribir")  # Indica un error en la autenticación para escritura
                    else:
                        print("Error de autenticación al leer")  # Indica un error en la autenticación para lectura
            else:
                print("Error seleccionando la tarjeta")  # Indica un error al seleccionar la tarjeta detectada
    
    except KeyboardInterrupt:
        print("Detenido por Ctrl+C")  # Maneja la interrupción del teclado para detener el programa de forma segura

 
# Bucle principal
mostrar_mensaje()  # Muestra el mensaje "MarEnMovimiento" en la pantalla LCD al iniciar
ultimo_cambio = time.monotonic()  # Registra el tiempo inicial para controlar la visualización de datos

while True:
    tiempo_actual = time.monotonic()  # Obtiene el tiempo actual para comparar con el último cambio
    # Cada 10 segundos muestra los datos durante 4 segundos
    if tiempo_actual - ultimo_cambio >= 10:
        mostrar_datos()  # Muestra los datos del géiser y la frecuencia en la pantalla LCD
        time.sleep(4)  # Mantiene los datos en pantalla durante 4 segundos
        mostrar_mensaje()  # Vuelve a mostrar el mensaje "MarEnMovimiento"
        ultimo_cambio = tiempo_actual  # Actualiza el tiempo del último cambio

    # Siempre está escuchando por una tarjeta RFID
    leer_tarjeta()  # Verifica si hay una tarjeta RFID presente y realiza las acciones correspondientes
    time.sleep(0.1)  # Espera brevemente antes de la siguiente iteración del bucle
