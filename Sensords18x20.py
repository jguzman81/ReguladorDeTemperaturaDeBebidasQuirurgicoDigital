# **************************************  #
# Desarrollador: John Guzman-Oscar Segura #
# Fundacion Universitaria Areandina       #  
# Ingeniería de sistemas - Virtual        #
# Fecha: Julio.20, 2022                   #
#                                         #
# ****************************************#


#**************************************
#Cargue las bibliotecas necesarias    #
#**************************************
from machine import Pin,I2C #Protocolo sincronico (SCL-SDA)
import machine # Libreria de aprendizaje automatizado
import network # Establece la conexión de red




# ***************************************
#Cargue de las bibliotecas necesarias   #
# ***************************************
from machine import Pin,I2C #Protocolo sincronico (SCL-SDA)
import machine # Libreria de aprendizaje automatizado
import network # Establece la conexión de red
import wifi_credentials # Guarda las credenciales red del usuario
import urequests # Envia la petición al servidor Web
import ssd1306 # Libreria controlador OLED
import ds18x20 # Libreria controlador sensor ds18x20 
import onewire # Libreria de Bus de comunicación para el sensor
import time # Libreria para cronometrar la duración de un intervalo de tiempo
# *************************************
# Creación de objetos:                #
# *************************************

led = machine.Pin(32,machine.Pin.OUT) #Led que nos identifica conexion exitosa
ds_pin = machine.Pin(15) # Pin de conexion de datos del sensor ds18x20
dat = machine.Pin(15)       # puerto del sensor ds18x20
i2c = I2C(0,scl=Pin(23), sda=Pin(22), freq=100000)      #Inicializa el i2c
lcd=ssd1306.SSD1306_I2C(128,64,i2c)          #Crea el objeto lcd ,Especifica colum & Filas
ventilateur=Pin(2,Pin.OUT)  # puerto del sensor del ventilador
heater=Pin(4,Pin.OUT)      # puerto del sensor del calentador
led1=Pin(18,Pin.OUT)         # Led indicador de temperatura alta
led2=Pin(21,Pin.OUT)         # Led indicador de temperatura baja
led3=Pin(19,Pin.OUT)         # Led indicador de temperatura correcta
ds = ds18x20.DS18X20(onewire.OneWire(dat))     # Crea el objeto  onewire
roms = ds.scan() # Almacena los datos del sensor

# ********************************************
# Configura la red en la ESP32 como estación #
# ********************************************
sta = network.WLAN(network.STA_IF)
if not sta.isconnected(): 
  print('Conectándose a la red...') 
  sta.active(True) 
  #sta.connect('Usuario Wifi ssid', 'Contraseña wifi') 
  sta.connect(wifi_credentials.ssid, wifi_credentials.password) 
  while not sta.isconnected(): 
    pass 
print('Configurando la red:', sta.ifconfig()) 

# **************************************
# Constantes y Variables               *
# **************************************
HTTP_HEADERS = {'Content-Type': 'application/json'} 
THINGSPEAK_WRITE_API_KEY = 'I4RWLEPFGP3J37I0' 
UPDATE_TIME_INTERVAL = 750  # en ms 
last_update = time.ticks_ms() 
# En esta parte del codigo se define:
# - La llave de envio de información del sensor ds18x20
# - se establece los intervalos de tiempos
# que llegan a nuesto servidor THINGSPEAK . 


# **************************************
# Bucle principal:                     *
#***************************************
while True: 
    if time.ticks_ms() - last_update >= UPDATE_TIME_INTERVAL:  # condición para el envio de información. . 
        ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))  # lectura del sensor y bus de datos 
        roms = ds_sensor.scan() # Almacena los datos del sensor 
        ds_sensor.convert_temp() # Convierte la información para la lectura
        for rom in roms:  # Ciclo para el recorrido de los datos del sensor en OLED
          print(ds_sensor.read_temp(rom))
          lcd.fill(0)
          lcd.text("  Temperatura",0,10)
          lcd.text(str(ds_sensor.read_temp(rom)),24,35)
          lcd.text("    grados C",0,50) 
          lcd.show()
          if ( ds_sensor.read_temp(rom)>=25): #Condicional para activar ventilador
               print('Temperatura=', ds_sensor.read_temp(rom),'activar cooler')
               lcd.text("    Caliente",0,20)
               lcd.show()
               ventilateur.value(0) #Activa el ventilador 
               led1.value(0)
               led2.value(1)
               led3.value(1)
          elif (ds_sensor.read_temp(rom)<=10): ##Condicional para activar calentador
              print('Temperature=', ds_sensor.read_temp(rom), 'activar calor')
              lcd.text("  Fria",0,20)
              lcd.show()
              heater.value(0) #Activa el calentador
              led1.value(1)
              led2.value(0)
              led3.value(1)
          else: #Condicional para desactivar ventilador y calentador 
                 print('temperatura correcta',ds_sensor.read_temp(rom))
                 lcd.text("  correcta",0,20)
                 lcd.show()
                 ventilateur.value(1)
                 heater.value(1)
                 led3.value(0)
                 led1.value(1)
                 led2.value(1)
                 #Envio de datos a los campos de las graficas del servidor
        ds18x20_readings = {'field1':ds_sensor.read_temp(rom), 'field2':ds_sensor.read_temp(rom)} 
        request = urequests.post( 
          'http://api.thingspeak.com/update?api_key=' +
          THINGSPEAK_WRITE_API_KEY, 
          json = ds18x20_readings, 
          headers = HTTP_HEADERS )  
        request.close() 
        print(ds18x20_readings) 
         
        led.value(not led.value()) 
        last_update = time.ticks_ms()
#**************************************
#        #Fin del codigo              #
#**************************************