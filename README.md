# huawei_e3_e5
Tool to manage huawei hilink modems (E3 and E5 series)


## Features

- [x] Get modem status
- [ ] Change sim settings
- [x] Get SMS messages
- [x] Send SMS messages
- [x] Modem reboot
- [x] Dump all modem infos

## Usage example

```python
>>> from huawei_e3_e5.huawei_exxxx import HuaweiModem as HuaweiModem
>>> gsm = HuaweiModem(user='admin', password='SECRET') # E5xxxx
>>> gsm = HuaweiModem() # E3xxx
>>> gsm
<HuaweiModem None (None)>
DeviceName     : E5577Cs-321
imei           : 8..............
imsi           : 2..............
iccid          : 8..................
msisdn         : +33.........
SerialNumber   : D...............
softwareVersion: 21.333.63.00.1217
hardwareVersion: CL1E5573SM11
MacAddress1    : 88:00:00:00:00:00
WebUIVersion   : 17.100.20.06.1217
ProductFamily  : LTE
classify       : mobile-wifi
supportmode    : LTE|WCDMA|GSM
workmode       : LTE

>>> gsm.device_signal
{
    'pci': '69',
    'sc': None,
    'cell_id': '105428049',
    'rsrq': '-10dB',
    'rsrp': '-104dBm',
    'rssi': None,
    'sinr': '-3dB',
    'rscp': None,
    'ecio': None,
    'psatt': '1',
    'mode': '7',
    'lte_bandwidth': None,
    'lte_bandinfo': None
}

>>> gsm.send_sms(numbers, message)

>>> gsm.control_reboot()
```
