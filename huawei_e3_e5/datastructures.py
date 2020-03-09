from huawei_lte_api.enums.sms import BoxTypeEnum as BoxTypeEnum

class SMSMessage():

    def init(self):
        pass

    def __init__(self, message, smsBox=BoxTypeEnum.LOCAL_INBOX):
        self._message = message
        self._smsBox = smsBox
        self.init()

    '''
    class BoxTypeEnum(enum.IntEnum):
        LOCAL_INBOX = 1
        LOCAL_SENT = 2
        LOCAL_DRAFT = 3
        LOCAL_TRASH = 4
        SIM_INBOX = 5
        SIM_SENT = 6
        SIM_DRAFT = 7
        MIX_INBOX = 8
        MIX_SENT = 9
        MIX_DRAFT = 10
    '''

    def __repr__(self):
        fromto = u'to'
        if self._smsBox == BoxTypeEnum.LOCAL_TRASH :
            fromto = u'trash'
        if self._smsBox in (BoxTypeEnum.LOCAL_INBOX,
                            BoxTypeEnum.SIM_INBOX,
                            BoxTypeEnum.MIX_INBOX
                            ):
            fromto = u'from'
        elif self._smsBox in (BoxTypeEnum.LOCAL_DRAFT,
                            BoxTypeEnum.SIM_DRAFT,
                            BoxTypeEnum.MIX_DRAFT
                            ):
            fromto = u'draft'

        result = u'< {}: {} time: {} index: {} box: {} content: "{}" >'
        return result.format(fromto, self.phone, self.smsDate, self.index,
                             self.box2str(self.smsBox), self.content)

    def box2str(self, boxType):
        return (
                '',
                'LOCAL_INBOX',
                'LOCAL_SENT',
                'LOCAL_DRAFT',
                'LOCAL_TRASH',
                'SIM_INBOX',
                'SIM_SENT',
                'SIM_DRAFT',
                'MIX_INBOX',
                'MIX_SENT',
                'MIX_DRAFT'
                )[boxType]

    @property
    def message(self):
        return self._message

    @property
    def messageStr(self):
        result = u'Message {}:\n'.format(self.box2str(self.smsBox))
        for k, v in self._message.items():
            result += u'{}: {}\n'.format(k.ljust(10), v) 
        return result

    @property
    def smsBox(self):
        return self._smsBox
    
    @smsBox.setter
    def smsBox(self, value):
        self._smsBox = value
    
    @property
    def smstat(self):
        if 'Smstat' in self._message:
            return self._message['Smstat']
        return None
    
    @smstat.setter
    def smstat(self, value):
        self._message['Smstat'] = value
    
    @property
    def index(self):
        if 'Index' in self._message:
            return self._message['Index']
        return None
    
    @index.setter
    def index(self, value):
        self._message['Index'] = value
    
    @property
    def phone(self):
        if 'Phone' in self._message:
            return self._message['Phone']
        return None
    
    @phone.setter
    def phone(self, value):
        self._message['Phone'] = value
    
    @property
    def content(self):
        if 'Content' in self._message:
            return self._message['Content']
        return None
    
    @content.setter
    def content(self, value):
        self._message['Content'] = value
    
    @property
    def smsDate(self):
        if 'Date' in self._message:
            return self._message['Date']
        return None
    
    @smsDate.setter
    def smsDate(self, value):
        self._message['Date'] = value
    
    @property
    def sca(self):
        if 'Sca' in self._message:
            return self._message['Sca']
        return None
    
    @sca.setter
    def sca(self, value):
        self._message['Sca'] = value
    
    @property
    def saveType(self):
        if 'SaveType' in self._message:
            return self._message['SaveType']
        return None
    
    @saveType.setter
    def saveType(self, value):
        self._message['SaveType'] = value
    
    @property
    def priority(self):
        if 'Priority' in self._message:
            return self._message['Priority']
        return None
    
    @priority.setter
    def priority(self, value):
        self._message['Priority'] = value
    
    @property
    def smsType(self):
        if 'SmsType' in self._message:
            return self._message['SmsType']
        return None
    
    @smsType.setter
    def smsType(self, value):
        self._message['SmsType'] = value


def main():
    message = {'Smstat': '0', 'Index': '40002', 'Phone': '+33600000000',
               'Content': 'Bien reçu le message depuis HUAWEI-7755.',
               'Date': '2020-03-07 19:29:17', 'Sca': None,
               'SaveType': '4', 'Priority': '0', 'SmsType': '1'}
    sms = SMSMessage(message, smsBox=BoxTypeEnum.LOCAL_INBOX)
    print(sms)
    print(sms.content)
    print(sms.message)
    print(sms.messageStr)


if __name__ == '__main__':
    main()
