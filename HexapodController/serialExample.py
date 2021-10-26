import time

import serial

right_V = 128
right_H = 128
left_V = 128
left_H = 128
allButtons = 0


def sendMovements():
    packet = bytearray()

    packet.append(0xff)  # Header
    packet.append(right_V)  # Right vertical joystick
    packet.append(right_H)  # Right horizontal joystick
    packet.append(left_V)  # Left vertical joystick
    packet.append(left_H)  # Left horizontal joystick
    packet.append(allButtons)  # Single byte holds all the button data
    packet.append(0)  # 0 char
    packet.append((255 - (right_V + right_H + left_V + left_H + allButtons) % 256))  # Checksum

    hexapodSerial.write(packet)
    time.sleep(0.033)  # Delay 33 ms


if __name__ == '__main__':
    hexapodSerial = serial.Serial('COM4', 38400, timeout=1)
    time.sleep(2)  # Wait 2 seconds to allow serial information exchange

    # Centro
    left_V = 128
    sendMovements()
    time.sleep(0.5)

    # Avance
    left_V = 255
    sendMovements()
    time.sleep(0.5)

    # Parar avance
    left_V = 128
    sendMovements()
    time.sleep(0.5)

    # Rotacion a la derecha
    right_H = 255
    sendMovements()
    time.sleep(0.5)

    # Parar rotacion
    right_H = 128
    sendMovements()
    time.sleep(0.5)

    # Debug
    time_ini = time.time()
    while time.time() - time_ini < 10:
        print(hexapodSerial.readline())
        time.sleep(0.5)

    # Cierre serial
    hexapodSerial.close()