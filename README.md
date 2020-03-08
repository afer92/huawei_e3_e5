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
>>> gsm = HuaweiModem()
>>> gsm
<HuaweiModem None (None)>
DeviceName     : E5577Cs-321
imei           : 863533042457552
imsi           : 208150020735953
iccid          : 8933150018080412939
msisdn         : +33766890253
SerialNumber   : D2L7S19420001570
softwareVersion: 21.333.63.00.1217
hardwareVersion: CL1E5573SM11
MacAddress1    : 88:40:3B:FF:08:57
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
```
