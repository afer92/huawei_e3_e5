import time
import sys
from datetime import datetime
import queue
import logging
import logging.handlers
from pprint import pformat
import argparse
import sqlite3
from huawei_lte_api.enums.sms import BoxTypeEnum as BoxTypeEnum
try:
    from huawei_e3_e5.huawei_exxxx import HuaweiModem
except ModuleNotFoundError:
    from huawei_exxxx import HuaweiModem
try:
    from huawei_e3_e5.datastructures import SMSMessage
except ModuleNotFoundError:
    from datastructures import SMSMessage


class HuaweiDb(HuaweiModem):

    qsearch_in_id = u'SELECT `ID`,`SenderNumber`,`RecipientID` FROM `inbox` WHERE `ID`=?;'
    qsearch_in = u'SELECT `ID`,`SenderNumber`,`RecipientID` FROM `inbox` WHERE `ReceivingDateTime`=? AND `SenderNumber`=?;'
    qinsert_in = u'INSERT INTO `inbox` (`ReceivingDateTime`,`Text`,`SenderNumber`,`RecipientID`,`UDH`) VALUES (?,?,?,?,?);'
    qdelete_in = u'DELETE FROM `inbox` WHERE `ID`=?;'

    qsearch_out_id = u'SELECT `ID`,`DestinationNumber`,`SenderID` FROM `outbox` WHERE `SenderID`=?;'
    qsearch_out = u'SELECT `ID`,`DestinationNumber`,`SenderID` FROM `outbox` WHERE `SendingDateTime`=? AND `DestinationNumber`=? AND `SenderID`=?;'
    qinsert_out = u'INSERT INTO `outbox` (`SendingDateTime`,`Text`,`DestinationNumber`,`SenderID`,`UDH`,`CreatorID`) VALUES (?,?,?,?,?,?);'
    qdelete_out = u'DELETE FROM `outbox` WHERE `ID`=?;'

    def __init__(self, interface=None, sysfs_path=None,
                 ip='192.168.8.1', log=None, logLevel=logging.INFO,
                 on_receive=None, on_send=None, on_event_parm=None,
                 user=None, password=None,
                 db_file=None, update_db=False):

        if on_event_parm == 'self':
            self._on_event_parm = self

        HuaweiModem.__init__(self, interface=interface, sysfs_path=sysfs_path,
                             ip=ip, log=log, logLevel=logLevel,
                             on_receive=on_receive, on_send=on_send, on_event_parm=on_event_parm,
                             user=user, password=password)

        self._db_file = db_file
        self._update_db = update_db
        self._cnx = None
        self._cursor = None
        self._id = None

        if update_db:
            # self.update_db()
            log.debug(u'db updated')

    def get_cursor(self):
        try:
            cnx = sqlite3.connect(self._db_file)
        except sqlite3.Error as e:
            log.warning(u'erreur sqlite3: %s' % (e.args[0]))
            return(None, None)
        else:
            self._cursor = cnx.cursor()
            self._cnx = cnx
        return (self._cnx, self._cursor)

    def get_cursor_check(self):
        if self._cnx is None:
            self.get_cursor()
        elif self._cursor is None:
            self._cursor = cnx.cursor()
        return self._cnx

    def curs_update(self, query, params):
        result = False
        if self.get_cursor_check() is None:
            return
        try:
            self._cursor.execute(query, params)
            self._cnx.commit()
            result = True
        except sqlite3.Error as e:
            self.log.warning(u'erreur sqlite3: {}'.format(e.args[0]))
        return result

    def curs_read(self, query, params=None):
        result = None
        if self.get_cursor_check() is None:
            return
        try:
            if params is None:
                self._cursor.execute(query)
            else:
                self._cursor.execute(query, params)
        except sqlite3.Error as e:
            self.log.warning(u'erreur sqlite3: {}'.format(e.args[0]))
        return self._cursor

    def sms_in_db(self, sms):
        if sms.from_to == 'from':
            # qsearch_in = u'SELECT `ID`,`SenderNumber`,`RecipientID` FROM `inbox` WHERE `ReceivingDateTime`=? AND `SenderNumber`=?;'
            query = self.qsearch_in
            params = (sms.smsDate, sms.phone)
        else:
            # qsearch_out = u'SELECT `ID`,`DestinationNumber`,`SenderID` FROM `outbox` WHERE `SendingDateTime`=? AND `DestinationNumber`=? AND `SenderID`=?;'
            query = self.qsearch_out
            params = (sms.smsDate, sms.phone, sms.index)
        curs = self.curs_read(query, params=params)
        if curs is None:
            return (None, None)
        rows = curs.fetchall()
        self.log.debug(rows)
        if len(rows) == 0:
            return (False, None)
        else:
            return (True, rows[0])

    def sms_store_in_db(self, sms):
        (in_db, row) = self.sms_in_db(sms)
        if in_db is None:
            return False
        if in_db:
            self.log.warning(u'sms already in db\n{}'.format(row))
            return True
        else:
            if sms.from_to == u'from':
                query = self.qinsert_in
                params = (sms.smsDate, sms.content, sms.phone, sms.index, '')
            else:
                query = self.qinsert_out
                params = (sms.smsDate, sms.content, sms.phone, sms.index, 'Reserved', -1)
            result = self.curs_update(query, params)
            return result

    def sms_load_from_db(self, table, filter):
        if table == 'inbox':
            fields = ['ID', 'SenderNumber', 'Text', 'ReceivingDateTime', 'RecipientID']
        elif table == 'outbox':
            fields = ['ID', 'DestinationNumber', 'Text', 'SendingDateTime', 'SenderID']
        query = u'SELECT {} FROM {} WHERE {}';
        query = query.format(u','.join(fields), table, filter)
        curs = self.curs_read(query, params=None)
        if curs is None:
            return []
        rows = curs.fetchall()
        smss = []
        for row in rows:
            sms = SMSMessage({})
            sms.id = row[0]
            sms.content = row[2]
            sms.phone = row[1]
            sms.smsDate  = row[3]
            sms.index = row[4]
            if table == 'inbox':
                sms.smsBox = BoxTypeEnum.LOCAL_INBOX
            if table == 'outbox':
                sms.smsBox = BoxTypeEnum.LOCAL_SENT
            smss.append(sms)
        return smss

    @property
    def db_file(self):
        return self._db_file

    @db_file.setter
    def db_file(self, value):
        self._db_file = value

    @property
    def update_db(self):
        return self._update_db

    @update_db.setter
    def update_db(self, value):
        self._update_db = value


def main():

    def find_gsm(logLevel=logging.INFO):
        gsms = []
        try:
            gsms = modem.load(logLevel=loglevel)
        except UnboundLocalError:
            pass
        trycount = 10
        while len(gsms) == 0:
            print(u'.', end='', flush=True)
            sys.stdout.flush()
            time.sleep(5)
            try:
                gsms = modem.load(logLevel=logLevel)
            except UnboundLocalError:
                pass
            trycount += -1
            if trycount == 0:
                return None
        print(u'')
        sys.stdout.flush()
        if trycount < 10:
            print(u'Waiting')
            for i in range(1, 10):
                time.sleep(1)
                print(u'.', end='', flush=True)
                sys.stdout.flush()
        return (gsms[0].interface, gsms[0].path)

    def on_receive(sms, param):
        print('<- {}'.format(sms))
        if param.db_file:
            print(u'result : {}\n{}'.format(param.sms_store_in_db(sms), sms))

    def on_send(sms, param):
        print('-> {}'.format(sms))
        if param.db_file:
            print(u'result : {}\n{}'.format(param.sms_store_in_db(sms), sms))

    #
    # parse arguments
    #
    loglevel = logging.INFO
    parser = argparse.ArgumentParser(description='Test module HuaweiDb.')
    parser.add_argument(u'--all', u'-a', help='Dump all datas', action="store_true")
    parser.add_argument(u'--debug', u'-d', help='Logging debug', action="store_true")
    parser.add_argument(u'--warning', u'-w', help='Logging warning', action="store_true")
    parser.add_argument(u'--critical', u'-c', help='Logging critical', action="store_true")
    parser.add_argument(u'--update_db', u'-s', help='Update db', action="store_true")
    parser.add_argument(u'--dbfile', u'-f', help='Sqlite3 file')
    parser.add_argument(u'--idsms', u'-i', help='SMS ID')
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
        modem = HuaweiDb(user=args.user, password=args.password, db_file=args.dbfile,
                         on_receive=on_receive, on_send=on_send, on_event_parm='self')
    else:
        modem = HuaweiDb(db_file=args.dbfile,
                         on_receive=on_receive, on_send=on_send, on_event_parm='self')

    if modem.present is False:
        return

    if args.all:
        modem.all_data(callback=print)
        return
        
    print(modem)
    print(modem.in_messages)
    print(modem.out_messages)

    in_messages = modem.in_messages
    for message in in_messages:
        omsg = SMSMessage(message)
        on_receive(omsg, modem)

    if args.dbfile:
        print(u'sms_load_from_db')
        smss = modem.sms_load_from_db('inbox', "`RecipientID`='{}'".format(args.idsms))
        for sms in smss:
            print(u'message id (in):{}\n{}'.format(sms.index, sms))
        smss = modem.sms_load_from_db('outbox', "`SenderID`='{}'".format(args.idsms))
        for sms in smss:
            print(u'message id (out):{}\n{}'.format(sms.index, sms))


if __name__ == '__main__':
    main()