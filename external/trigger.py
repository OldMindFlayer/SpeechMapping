import serial.tools.list_ports
from tkinter import *

ser = None


def send():
    # send trigger
    ser.write(bytes((240,)))
    print('Trigger send.')


# search for the USB TTL device
for s in serial.tools.list_ports.comports():
    # compare vid and pid of the available serial devices to the pid and vid of the USB TTL device
    if s.vid == 1027:
        if s.pid == 24577:
            # connect to device
            ser = serial.Serial(s.device, baudrate=9600)
            break

# if no device is found print error
if ser is None:
    print('Error: USB device not found.')
# else create GUI with button to send trigger
else:
    print('USB connection established.')

    root = Tk()
    trigger_button = Button(root, text='Trigger', command=send)
    trigger_button.pack()
    root.mainloop()

    ser.close()
