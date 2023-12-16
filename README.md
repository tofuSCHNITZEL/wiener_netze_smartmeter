# wiener_netze_smartmeter

Python API for reading data from a Wiener Netze Smart Meter with a serial interface (via infrared)

## Installation

* pip install wiener_netze_smartmeter

## Usage

For reading data from your Wiener Netze Smart Meter you need:
- A Smart Meter from Wiener Netze Type "Isramenko" or "Landis+ Gyr"  
- An infrared serial adapter (only receiving is necessary)
- Your decryption key for 'Kundenschnittstelle' from Wiener Netze web portal (https://smartmeter-web.wienernetze.at/#/anlagedaten)"

to quickly test if data can be received and decrypted you can use:

```
python3 -m wiener_netze_smartmeter --interface COM1 --key aabbccddeeff00112233445566778899
```

to use it in your own python project:

```
import wiener_netze_smartmeter, asyncio

wnsm = wiener_netze_smartmeter.WienerNetzeSmartMeter("COM1", "aabbccddeeff00112233445566778899")

data = asyncio.run(wnsm.read_meter_data())

print(f'Current Power Draw: {data.active_power_in} W')

# All data:
print(data)
```


## Compatibility

* Currently only works with Wiener Netze Smart Meters of Type "Isramenko" and "Landis+ Gyr"   
"Siemens" is currently not supported.   
If you have a Siemens Smart Meter, you can help by opening an issue and posting your raw data (use flag --raw when running the module)

## Credits

* This was made possible with the help and insight from: https://github.com/pocki80

## License

[MIT](https://choosealicense.com/licenses/mit/)