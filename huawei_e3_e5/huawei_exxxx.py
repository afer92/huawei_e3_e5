import sys
import time
import logging
import logging.handlers
from pprint import pformat
import argparse
from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Connection import Connection
from huawei_lte_api.enums.sms import BoxTypeEnum as BoxTypeEnum
import subprocess

'''
try:
    from huawei_3g.huawei_exxx import HuaweiModem
except ModuleNotFoundError:
    from huawei_exxx import HuaweiModem
'''


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', '-c', '2', host]

    return subprocess.run(command, capture_output=True).returncode == 0


class HuaweiModem():

    def init(self):
        if self.wait_modem_ready() is False:
            return
        if self._password is None:
            self._base_url = "http://{}/".format(self._ip)
        else:
            self._base_url = "http://{}:{}@{}/".format(self._user, self._password, self._ip)

        self._connection = AuthorizedConnection(self._base_url)
        self._client = Client(self._connection)
        self._infos = self._client.device.information()
        self._present = True

        '''
        self._infos = {}
        try:
            self._infos = self.get_device_infos()
        except TokenError:
            self._get_token_ext()
            self._infos = self.get_device_infos()
        if u'DeviceName' in self._infos.keys():
            pass
        else:
            # modele type E3372
            self._devicename = u'E3372'
        self._log.debug(u'{}'.format(self._infos))
        # self._get_token()
        '''

    def __init__(self, interface=None, sysfs_path=None,
                 ip='192.168.8.1', log=None, logLevel=logging.INFO,
                 on_receive=None, on_send=None, on_event_parm=None,
                 user=None, password=None):
        self._interface = interface
        self._path = sysfs_path
        self._ip = ip
        self._user = user
        self._password = password
        self._logLevel = logLevel

        self._on_receive = on_receive
        self._on_send = on_send
        self._on_event_parm = on_event_parm

        if log is None:
            logger = logging.getLogger(u'HuaweiModem')
            logger.setLevel(logLevel)
            handler = logging.StreamHandler(stream=sys.stdout)
            logger.addHandler(handler)
            self._log = logger
        else:
            self._log = logger

        self._present = False
        self.init()

    def __repr__(self):
        part0 = u'<HuaweiModem {} ({})>'.format(self.interface, self.path)
        part1 = u'\nDeviceName     : %s\nimei           : %s\nimsi           : %s\n' %\
                (self.deviceName, self.imei, self.imsi)
        part2 = u'iccid          : %s\nmsisdn         : %s\n' %\
                (self.iccid, self.msisdn)
        part3 = u'SerialNumber   : %s\nsoftwareVersion: %s\nhardwareVersion: %s\n' %\
                (self.serialNumber, self.softwareVersion, self.hardwareVersion)
        part4 = u'MacAddress1    : %s\nWebUIVersion   : %s\n' % (self.macAddress1, self.webUIVersion)
        part5 = u'ProductFamily  : %s\nclassify       : %s\n' %\
                (self.productFamily, self.classify)
        part6 = u'supportmode    : %s\nworkmode       : %s\n' %\
                (self.supportmode, self.workmode)
        return part0 + part1 + part2 + part3 + part4 + part5 + part6

    def send_sms(self, numbers, message):
        """ send sms to a list of number

        :param numbers: array of phone number
        :param text to send
        """
        """ Added 04th june 2017 by Bjoern"""
        """ Updated 01th febr 2020 by Afer92"""
        phones = u''
        if type(numbers) == str:
            numbers = numbers.split(u',')
        self._client.sms.send_sms(numbers, message)

    def _print_dict(self, name, one_dict, callBack=print):
        if type(one_dict) == str:
            return one_dict
        result = u'\n{}:\n'.format(name)
        for k, v in one_dict.items():
            result += '  {}: {}\n'.format(k.ljust(16), v)
        if callBack is not None:
            callBack(result)
            return result
        else:
            return result

    def control_reboot(self):
        self._client.device.reboot()

    @property
    def interface(self):
        return self._interface

    @property
    def path(self):
        return self._path

    @property
    def ip(self):
        return self._ip

    @property
    def present(self):
        return self._present

    @property
    def base_url(self):
        return self._base_url

    @property
    def deviceName(self):
        if u'DeviceName' in self._infos.keys():
            return self._infos[u'DeviceName']
        else:
            return u''

    @property
    def macAddress1(self):
        if u'MacAddress1' in self._infos.keys():
            return self._infos[u'MacAddress1']
        else:
            return u''

    @property
    def imei(self):
        if u'Imei' in self._infos.keys():
            return self._infos[u'Imei']
        else:
            return u''

    @property
    def imsi(self):
        if u'Imsi' in self._infos.keys():
            return self._infos[u'Imsi']
        else:
            return u''

    @property
    def iccid(self):
        if u'Iccid' in self._infos.keys():
            return self._infos[u'Iccid']
        else:
            return u''

    @property
    def msisdn(self):
        if u'Msisdn' in self._infos.keys():
            return self._infos[u'Msisdn']
        else:
            return u''

    @property
    def hardwareVersion(self):
        if u'HardwareVersion' in self._infos.keys():
            return self._infos[u'HardwareVersion']
        else:
            return u''

    @property
    def softwareVersion(self):
        if u'SoftwareVersion' in self._infos.keys():
            return self._infos[u'SoftwareVersion']
        else:
            return u''

    @property
    def webUIVersion(self):
        if u'WebUIVersion' in self._infos.keys():
            return self._infos[u'WebUIVersion']
        else:
            return u''

    @property
    def macAddress2(self):
        if u'MacAddress2' in self._infos.keys():
            return self._infos[u'MacAddress2']
        else:
            return u''

    @property
    def productFamily(self):
        if u'ProductFamily' in self._infos.keys():
            return self._infos[u'ProductFamily']
        else:
            return u''

    @property
    def classify(self):
        if u'Classify' in self._infos.keys():
            return self._infos[u'Classify']
        else:
            return u''

    @property
    def supportmode(self):
        if u'supportmode' in self._infos.keys():
            return self._infos[u'supportmode']
        else:
            return u''

    @property
    def workmode(self):
        if u'workmode' in self._infos.keys():
            return self._infos[u'workmode']
        else:
            return u''

    @property
    def serialNumber(self):
        if u'SerialNumber' in self._infos.keys():
            return self._infos[u'SerialNumber']
        else:
            return u''

    @property
    def log(self):
        return self._log

    @property
    def on_receive(self):
        return self._on_receive

    @on_receive.setter
    def on_receive(self, value):
        self._on_receive = value

    @property
    def on_send(self):
        return self._on_send

    @on_receive.setter
    def on_send(self, value):
        self._on_send = value

    @property
    def on_event_parm(self):
        return self._on_event_parm

    @on_event_parm.setter
    def on_event_parm(self, value):
        self._on_event_parm = value

    def return_dict(self, result, callback=print):
        if result is None:
            if callback is not None:
                callback('None')
            return {}
        else:
            if callback is not None:
                callback(result)
            return result

    @property
    def device_signal(self, callback=None):
        return self.get_device_signal(callback=callback)

    def get_device_signal(self, callback=None):
        result = self._client.device.signal()
        return self.return_dict(result, callback=callback)

    def print_device_signal(self, callback=print):
        return self._print_dict(u'Device Signal', self.device_signal, callBack=callback)

    @property
    def monitoring_status(self, callback=None):
        return self.get_monitoring_status(callback=callback)

    def get_monitoring_status(self, callback=None):
        result = self._client.monitoring.status()
        return self.return_dict(result, callback=callback)

    def print_monitoring_status(self, callback=print):
        return self._print_dict(u'Monitoring Status', self.monitoring_status, callBack=callback)

    @property
    def message_count(self, callback=None):
        return self.get_message_count(callback=callback)

    def get_message_count(self, callback=None):
        result = self._client.sms.sms_count()
        return self.return_dict(result, callback=callback)

    def print_message_count(self, callback=print):
        return self._print_dict(u'Message Count', self.message_count, callBack=callback)

    @property
    def device_information(self, callback=None):
        return self.get_device_information(callback=callback)

    def get_device_information(self, callback=None):
        result = self._infos
        return self.return_dict(result, callback=callback)

    def print_device_information(self, callback=print):
        return self._print_dict(u'Device Information', self.device_information, callBack=callback)

    @property
    def autorun_version(self, callback=None):
        return self.get_autorun_version(callback=callback)

    def get_autorun_version(self, callback=None):
        result = self._client.device.autorun_version()
        return self.return_dict(result, callback=callback)

    def print_autorun_version(self, callback=print):
        return self._print_dict(u'Autorun Version', self.autorun_version, callBack=callback)

    def _list_messages(self, box_type=BoxTypeEnum.LOCAL_INBOX, callback=print):
        sms_list = self.get_sms_list(box_type=box_type, callback=None)
        smss = []
        if int(sms_list[u'Count']) == 0:
            return smss
        elif int(sms_list[u'Count']) == 1:
            smss.append(sms_list[u'Messages'][u'Message'][0])
            return smss
        for message in sms_list[u'Messages'][u'Message']:
            smss.append(message)
        return smss

    @property
    def in_messages(self):
        return self._list_messages(box_type=BoxTypeEnum.LOCAL_INBOX, callback=None)

    def print_in_messages(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.LOCAL_INBOX)
        return self.build_sms_list(result, callback=callback)

    @property
    def out_messages(self):
        return self._list_messages(box_type=BoxTypeEnum.LOCAL_SENT, callback=None)

    def print_out_messages(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.LOCAL_SENT)
        return self.build_sms_list(result, callback=callback)

    @property
    def draft_messages(self):
        return self._list_messages(box_type=BoxTypeEnum.LOCAL_DRAFT, callback=None)

    def print_draft_messages(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.LOCAL_DRAFT)
        return self.build_sms_list(result, callback=callback)

    @property
    def trash_messages(self):
        return self._list_messages(box_type=BoxTypeEnum.LOCAL_TRASH, callback=None)

    def print_trash_messages(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.LOCAL_TRASH)
        return self.build_sms_list(result, callback=callback)

    @property
    def sim_inbox(self):
        return self._list_messages(box_type=BoxTypeEnum.SIM_INBOX, callback=None)

    def print_sim_inbox(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.SIM_INBOX)
        return self.build_sms_list(result, callback=callback)

    @property
    def sim_sent(self):
        return self._list_messages(box_type=BoxTypeEnum.SIM_SENT, callback=None)

    def print_sim_sent(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.SIM_SENT)
        return self.build_sms_list(result, callback=callback)

    @property
    def sim_draft(self):
        return self._list_messages(box_type=BoxTypeEnum.SIM_DRAFT, callback=None)

    def print_sim_draft(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.SIM_DRAFT)
        return self.build_sms_list(result, callback=callback)

    @property
    def mix_inbox(self):
        return self._list_messages(box_type=BoxTypeEnum.MIX_INBOX, callback=None)

    def print_mix_inbox(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.MIX_INBOX)
        return self.build_sms_list(result, callback=callback)

    @property
    def mix_sent(self):
        return self._list_messages(box_type=BoxTypeEnum.MIX_SENT, callback=None)

    def print_mix_sent(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.MIX_SENT)
        return self.build_sms_list(result, callback=callback)

    @property
    def mix_draft(self):
        return self._list_messages(box_type=BoxTypeEnum.MIX_DRAFT, callback=None)

    def print_mix_draft(self, callback=print):
        result = self._client.sms.get_sms_list(box_type=BoxTypeEnum.MIX_DRAFT)
        return self.build_sms_list(result, callback=callback)

    def get_sms_list(self, box_type=BoxTypeEnum.LOCAL_INBOX, callback=None):
        result = self._client.sms.get_sms_list(box_type=box_type)
        if int(result[u'Count']) == 1:
            result[u'Messages'][u'Message'] = (result[u'Messages'][u'Message'],)
        return self.return_dict(result, callback=callback)

    def build_sms_list(self, sms_list, callback=None):
        result = []
        indx = 0
        if int(sms_list[u'Count']) > 1:
            for message in sms_list[u'Messages'][u'Message']:
                indx += 1
                result.append(self._print_dict(u'Message ({}/{})'.format(indx, sms_list[u'Count']),
                                               message, callBack=callback))
            return result
        elif int(sms_list[u'Count']) == 1:
            result.append(self._print_dict(u'Message ({}/{})'.format('1', '1'),
                                           sms_list[u'Messages'][u'Message'], callBack=callback))
            return result
        else:
            resul = u'Message None:'
            if callback is not None:
                callback(resul)
            return []

    def print_sms_list(self, box_type=BoxTypeEnum.LOCAL_INBOX, callback=print):
        sms_list = self.get_sms_list(box_type=box_type)
        self.build_sms_list(sms_list, callback=callback)

    def all_data(self, callback=None):
        result = u'{}\n'.format(self)
        result += self.print_device_information(callback=None)
        result += self.print_autorun_version(callback=None)
        result += self.print_message_count(callback=None)
        result += self.print_device_signal(callback=None)
        result += u'\nin_messages\n==========='
        smss = self.print_in_messages(callback=None)
        result += u'\n'.join(smss)
        result += u'\nout_messages\n============'
        smss = self.print_out_messages(callback=None)
        result += u'\n'.join(smss)
        result += u'\ndraft_messages\n=============='
        smss = self.print_draft_messages(callback=None)
        result += u'\n'.join(smss)
        result += u'\ntrash_messages\n=============='
        smss = self.print_trash_messages(callback=None)
        result += u'\n'.join(smss)
        result += u'\nsim_inbox\n========='
        smss = self.print_sim_inbox(callback=None)
        result += u'\n'.join(smss)
        result += u'\nsim_sent\n========'
        smss = self.print_sim_sent(callback=None)
        result += u'\n'.join(smss)
        result += u'\nsim_draft\n========='
        smss = self.print_sim_draft(callback=None)
        result += u'\n'.join(smss)
        result += u'\nmix_inbox\n========='
        smss = self.print_mix_inbox(callback=None)
        result += u'\n'.join(smss)
        result += u'\nmix_sent\n========'
        smss = self.print_mix_sent(callback=None)
        result += u'\n'.join(smss)
        result += u'\nmix_draft\n========='
        smss = self.print_mix_draft(callback=None)
        result += u'\n'.join(smss)
        if callback is not None:
            callback(result)
            return result
        else:
            return result

    def wait_modem_ready(self, logLevel=logging.INFO):

        trycount = 12
        result = ping(self._ip)
        while result is False:
            trycount += -1
            time.sleep(5)
            result = ping(self._ip)
            if trycount == 0:
                self.log.warning('No modem found')
                return False
        return True

    def reboot_and_wait(self, logLevel=logging.INFO):

        def log_console(text, logger, handler):
            logger.info(text)
            handler.flush()

        logger = logging.getLogger(u'HuaweiModem_reboot')
        logger.setLevel(logLevel)
        handler = logging.StreamHandler(stream=sys.stdout)
        logger.addHandler(handler)
        log = logger

        log_console('Reboot command send', logger, handler)
        self.control_reboot()

        log_console('Waiting 10s', logger, handler)
        time.sleep(10)

        log_console('Waiting moddem ready', logger, handler)
        modem = self.wait_modem_ready(logLevel=logging.INFO)

        log_console('modem status: {}'.format(self.status), logger, handler)

        log_console('Waiting 10s', logger, handler)
        time.sleep(10)

        log_console('modem status: {}'.format(self.status), logger, handler)

        logger.removeHandler(handler)
        return


def main():

    #
    # parse arguments
    #

    loglevel = logging.INFO
    parser = argparse.ArgumentParser(description='Test module huawei_exxx.')
    parser.add_argument(u'--all', u'-a', help='Dump all datas', action="store_true")
    parser.add_argument(u'--debug', u'-d', help='Logging debug', action="store_true")
    parser.add_argument(u'--warning', u'-w', help='Logging warning', action="store_true")
    parser.add_argument(u'--critical', u'-c', help='Logging critical', action="store_true")
    parser.add_argument(u'--list-out', u'-o', help='Out messages list', action="store_true")
    parser.add_argument(u'--list-in', u'-i', help='In messages list', action="store_true")
    parser.add_argument(u'--reboot', u'-r', help='Reboot usb stick', action="store_true")
    parser.add_argument(u'--number', u'-n', help='Phone numbers comma separated')
    parser.add_argument(u'--text', u'-t', help='sms text')
    parser.add_argument(u'--user', u'-u', help='User')
    parser.add_argument(u'--password', u'-p', help='Password')
    
    args = parser.parse_args()

    if args.debug:
        loglevel = logging.DEBUG
    if args.warning:
        loglevel = logging.WARNING
    if args.critical:
        loglevel = logging.CRITICAL

    if args.user and args.password:
        gsm = HuaweiModem(user=args.user, password=args.password)
    else:
        gsm = HuaweiModem()

    if gsm.present is False:
        return

    if args.all:
        gsm.all_data(callback=print)
        return

    gsm.print_device_information()

    if args.reboot:
        gsm.control_reboot()
        print(u'\nReboot', end='', flush=True)
        sys.stdout.flush()
        result = ping(gsm.ip)
        while result:
            time.sleep(1)
            print(u'.', end='', flush=True)
            sys.stdout.flush()
            result = ping(gsm.ip)
        return

    if args.list_out:
        gsm.print_out_messages()
    elif args.list_in:
        gsm.print_in_messages()

    if args.number and args.text:
        print(args.number, args.text)
        gsm.send_sms(args.number, args.text)


if __name__ == '__main__':
    main()
