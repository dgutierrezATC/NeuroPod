import time
from threading import Thread

import serial
from pynput import keyboard

import globals as var

# Packet values variables
right_V = 128
right_H = 128
left_V = 128
left_H = 128
allButtons = 0

# Keyboard controller thread variables
kc_thread = None
pressedKeys = {'a': False, 'd': False, 's': False, 'w': False,
               'rotleft': False, 'rotright': False, 'down': False, 'up': False}

# Sender thread variables
end = False


def sendMovement():
    """
    This function creates a package that contains all needed control information and sends it through the serial port.
    """
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

    #print(packet)


def sendMovements():
    """
    This function manages the continuous sending of packages, which contains all needed control information,
    through the serial port by calling the sendMovement function.
    """
    global left_H, left_V, right_H, right_V

    while not end:
        sendMovement()
        time.sleep(0.200)  # Delay 33 ms

    left_H = 128
    left_V = 128
    right_H = 128
    right_V = 128

    sendMovement()


def keyboardInterrupts():
    """
    This function contains all keyboard control code.
    """
    global kc_thread

    def on_press(key):
        global pressedKeys, left_H, left_V, right_H, right_V, end
        try:
            # Left
            if key.char == 'a' and not pressedKeys['a']:
                pressedKeys['a'] = True
                var.left_H_left = -127
                left_H = 128 + var.left_H_left + var.left_H_right

            # Right
            elif key.char == 'd' and not pressedKeys['d']:
                pressedKeys['d'] = True
                var.left_H_right = 127
                left_H = 128 + var.left_H_left + var.left_H_right

            # Forward
            elif key.char == 'w' and not pressedKeys['w']:
                pressedKeys['w'] = True
                var.left_V_up = 127
                left_V = 128 + var.left_V_down + var.left_V_up

            # Backward
            elif key.char == 's' and not pressedKeys['s']:
                pressedKeys['s'] = True
                var.left_V_down = -127
                left_V = 128 + var.left_V_down + var.left_V_up

            # kc_thread stop
            elif key.char == 'q':
                end = True
                kc_thread.stop()

        except AttributeError:
            # Up
            if key == keyboard.Key.up and not pressedKeys['up']:
                pressedKeys['up'] = True
                var.right_V_up = 127
                right_V = 128 + var.right_V_down + var.right_V_up

            # Down
            elif key == keyboard.Key.down and not pressedKeys['down']:
                pressedKeys['down'] = True
                var.right_V_down = -127
                right_V = 128 + var.right_V_down + var.right_V_up

            # Rotate Left
            elif key == keyboard.Key.left and not pressedKeys['rotleft']:
                pressedKeys['rotleft'] = True
                var.right_H_left = -127
                right_H = 128 + var.right_H_left + var.right_H_right

            # Rotate Right
            elif key == keyboard.Key.right and not pressedKeys['rotright']:
                pressedKeys['rotright'] = True
                var.right_H_right = 127
                right_H = 128 + var.right_H_left + var.right_H_right

        except ValueError:
            print("ValueError exception")

    def on_release(key):
        global pressedKeys, left_H, left_V, right_H, right_V
        try:
            # Left
            if key.char == 'a':
                pressedKeys['a'] = False
                var.left_H_left = 0
                left_H = 128 + var.left_H_left + var.left_H_right

            # Right
            elif key.char == 'd':
                pressedKeys['d'] = False
                var.left_H_right = 0
                left_H = 128 + var.left_H_left + var.left_H_right

            # Forward
            elif key.char == 'w':
                pressedKeys['w'] = False
                var.left_V_up = 0
                left_V = 128 + var.left_V_down + var.left_V_up

            # Backward
            elif key.char == 's':
                pressedKeys['s'] = False
                var.left_V_down = 0
                left_V = 128 + var.left_V_down + var.left_V_up

        except AttributeError:
            # Up
            if key == keyboard.Key.up:
                pressedKeys['up'] = False
                var.right_V_up = 0
                right_V = 128 + var.right_V_down + var.right_V_up

            # Down
            elif key == keyboard.Key.down:
                pressedKeys['down'] = False
                var.right_V_down = 0
                right_V = 128 + var.right_V_down + var.right_V_up

            # Rotate Left
            elif key == keyboard.Key.left:
                pressedKeys['rotleft'] = False
                var.right_H_left = 0
                right_H = 128 + var.right_H_left + var.right_H_right

            # Rotate Right
            elif key == keyboard.Key.right:
                pressedKeys['rotright'] = False
                var.right_H_right = 0
                right_H = 128 + var.right_H_left + var.right_H_right

        except ValueError:
            print("ValueError exception")

    kc_thread = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    kc_thread.start()


if __name__ == '__main__':
    # Serial port opening
    hexapodSerial = serial.Serial('COM4', 38400, timeout=1)
    time.sleep(2)  # Wait 2 seconds to allow serial information exchange

    # Sender and KeyboardInterrupts thread initialization
    senderThread = Thread(target=sendMovements)
    senderThread.start()
    keyboardInterrupts()

    # Wait for kc_thread's death
    kc_thread.join()

    # Wait for senderThread's death
    senderThread.join()

    # Serial port closure
    hexapodSerial.close()
