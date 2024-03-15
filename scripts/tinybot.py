"""
15/03/24

Tiny bot example.

Example script for the purposes of receiving a message, 
decoding the message, and sending a responce 
back on the "/test" prompt. 

Could be expanded for a simple bot.
"""

import meshtastic
import meshtastic.tcp_interface
from pubsub import pub
import atexit


"""Settings (connects via wifi but change to w/e here"""
radio_hostname = "192.168.0.184"  # replace or use meshtastic.local
interface = meshtastic.tcp_interface.TCPInterface(radio_hostname)


def onReceive(packet, interface):  # called when a packet arrives

    decoded = packet.get('decoded')
    msg = decoded.get('text')
    to = packet.get('to')
    frm = packet.get('fromId')

    if msg != None:
        print(f"""msg from {frm}: {msg}
    """)
        if msg == "/test":
            interface.sendText(
                text="testing testing hello thereeee", destinationId=frm)


def termination_code():
    # clean up code
    print("Program is terminating. Performing cleanup tasks...")
    interface.close()


def main():

    pub.subscribe(onReceive, "meshtastic.receive")

    atexit.register(termination_code)  # exit code reg

    while True:
        pass


main()
