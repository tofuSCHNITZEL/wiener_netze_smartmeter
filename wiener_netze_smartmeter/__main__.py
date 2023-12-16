"""For running the module directly"""

import getopt
import sys
import logging
import asyncio

from .wiener_netze_smartmeter import WienerNetzeSmartMeter

if __name__ == "__main__":
    argumentList = sys.argv[1:]

    OPTIONS = "i:k:rv"
    LONG_OPTIONS = ["interface=", "key=", "raw", "verbose"]

    SERIAL_INTERFACE = DECRYPTION_KEY = None

    RAW_FLAG = False

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, OPTIONS, LONG_OPTIONS)

        # checking each argument
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-i", "--interface"):
                SERIAL_INTERFACE = currentValue

            elif currentArgument in ("-k", "--key"):
                DECRYPTION_KEY = currentValue

            elif currentArgument in ("-r", "--raw"):
                RAW_FLAG = True

            elif currentArgument in ("-v", "--verbose"):
                logging.basicConfig(level=logging.DEBUG)

    except getopt.error as err:
        print(str(err))
        sys.exit(1)

    if not SERIAL_INTERFACE or not DECRYPTION_KEY:
        print(
            "A serial interface (-i/--interface) and a decryption key (-k/--key) must be set"
        )
        sys.exit(1)

    wnsm = WienerNetzeSmartMeter(SERIAL_INTERFACE, DECRYPTION_KEY)
    try:
        while data := asyncio.run(wnsm.read_meter_data()):
            print(data)
            if RAW_FLAG and wnsm.get_last_raw_notification_packet():
                print(
                    f"Raw notification packet:\n{wnsm.get_last_raw_notification_packet().hex()}\nRaw decrypted data:\n{wnsm.get_last_raw_decrypted_data().hex()}"
                )
    except (asyncio.exceptions.CancelledError, KeyboardInterrupt) as e:
        sys.exit(0)
