#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################
#    Utility definitions for TMOHS1 exploit
#
#    Created by natthawk
#    Copyright 2022
#########################################

import time
import telnetlib
from getpass import getpass
from ftplib import FTP

chPwdFlag = True


# create a TelnetConnection class to add some case-specific methods to the telnetlib.Telnet class

class TelnetConnection(telnetlib.Telnet):
    def __init__(self, host, wait):
        self.host = host
        self.wait = wait
        super().__init__(host, timeout=wait)
        try:
            self.open(host, timeout=wait)
            print('Trying to connect via telnet. . .')
        except TimeoutError:
            print(
                'Telnet connection attempt timed out. \n. Please reboot the device and try again.')
            quit()
        self.read_until(b'login:')
        self.write(b'root')
        self.login()

    def login(self):
        if chPwdFlag:  # If we know that there should be no root password, we can go ahead and log in
            print(
                'Telnet connection initialized.\nLogging in as root with empty password, please wait. . .')
            self.write(b'\n')
            # wait for a bit because if we don't, things break in inexplicable ways ¯\_(ツ)_/¯
            time.sleep(4)
        else:
            rootPwd = input('Enter your custom root password: ')
            self.write((f'{rootPwd}\n').encode())
        if b'#' not in self.read_very_eager():  # Make sure we actually have a shell
            choice = input('Failed to login as root. Try again? (Y/n): ')
            if choice == 'n':
                quit()
            else:
                self.login()

    def checkAlive(self):
        try:
            if self.sock:
                # we try 3 times for good luck, idk ask stackoverflow
                self.sock.send(telnetlib.IAC + telnetlib.NOP)
                self.sock.send(telnetlib.IAC + telnetlib.NOP)
                self.sock.send(telnetlib.IAC + telnetlib.NOP)
                return True
        except:
            return False

    def resetIfDead(self):
        if not self.checkAlive():
            try:
                self.open(self.host, self.wait)
            except:
                print(
                    'Telnet client died and we could not reconnect. Reboot and try again.')

    def send(self, cmd):
        self.write(cmd.encode() + b'\n')
        time.sleep(1)


def changeRootPwd(conn):
    conn.resetIfDead()
    conn.send('passwd root')

    conn.read_until(b'password:').decode()
    conn.send(getpass('Enter new password:'))
    conn.read_until(b':')
    conn.send(getpass('Confirm new password:'))
    if b'changed by' not in conn.read_very_eager(): # make sure the password was actually changed
        print('Error setting new password. Try again, making sure passwords match.')
        changeRootPwd(conn)
    else:
        global chPwdFlag
        chPwdFlag = False
        print('Root password successfully updated.')


def usrShell(conn):
    conn.resetIfDead()
    conn.mt_interact()  # spawns an interactive telnet client, though I can't figure out how to get it to not echo everything


def ftpEnable(conn):
    conn.resetIfDead()
    conn.send('start-stop-daemon -S -b -a tcpsvd -- -vE 0.0.0.0 21 ftpd -w /')
    conn.send('netstat -tunlp')
    # make sure server is listening on port 21
    if b'0.0.0.0:21' not in conn.read_very_eager():
        print('Error starting FTP server. Try again.')
        chooseAction()
    else:
        print('Started FTP server on port 21.')


def adbTemp(conn):
    conn.resetIfDead()
    # switch usb mode, effective immediately
    conn.send('/sbin/usb/compositions/9025')
    print('Switched USB mode to 9025 (ADB). . .')


def adbPersist(conn):
    adbTemp()
    ftpEnable()
    srv = FTP('192.168.0.1')  # start a FTP connection to the server we started
    srv.login()
    srv.cwd('cache')
    with open('patchUSB.sh', 'rb') as fp:
        # upload the patch script to the cache directory
        srv.storbinary('STOR patchUSB.sh', fp)
    time.sleep(1)
    srv.close()
    # make it executable and run it
    conn.send('chmod +x /cache/patchUSB.sh')
    print('Patching USB init script to persistently enable ADB. . .')
    conn.send('/cache/patchUSB.sh')
    time.sleep(2)
    conn.send('rm /cache/patchUSB.sh')

    # clear the queue so it doesn't get cluttered with our commands getting echoed back, 
    # as it seems telnetlib has a hobby of vomiting them into the read queue
    conn.read_very_eager()
    print('Cleaning up, killing FTP server. . .')
    # we don't need the ftp server anymore, and we don't want to leave it open without the user knowing
    conn.send('killall tcpsvd')


def reboot(conn):
    conn.resetIfDead()
    print('Rebooting. Goodbye!')
    conn.send('reboot')


def moodLighting(conn):
    conn.resetIfDead()
    conn.send('/sbin/ledoff.sh; sleep 2; echo 1 > /sys/class/leds/led\:signal_blue/blink; echo 1 > /sys/class/leds/led\:signal_green/blink')


def disableOmadm(conn):
    conn.resetIfDead()
    # copy omadm init script to backups directory, then delete it from /etc/init.d
    conn.send('if [ ! -d /etc/backups/init.d ];then mkdir -p /etc/backups/init.d; fi; cp /etc/init.d/start_omadm_le /etc/backups/init.d/; rm /etc/init.d/start_omadm_le;')


def chooseAction(conn):
    conn.resetIfDead()
    global chPwdFlag
    if chPwdFlag:
        choice = input('''
The exploit removed the root password of your device. It is STRONGLY recommended to set a custom root password.
Your device will be EXTREMELY INSECURE if you do not.\n
Would you like to set a custom root password? (Y/n):
''')
        while choice not in {'y', 'n', ''}:
            choice = input('Please enter \'y\' or \'n\': ')
        if choice.casefold() == 'y' or choice == '':
            changeRootPwd(conn)
        else:
            chPwdFlag = False
            chooseAction(conn)
    else:
        choice = input(
            '''Select an option:
            1) Change root password
            2) Enough with this script BS, give me a shell!
            3) Enable ADB
            4) Enable ADB - Persistent through reboot (somewhat experimental)
            5) Enable FTP server for / on port 21 - DO NOT LEAVE OPEN
            6) Remove OMA-DM bootstrap (essentially disables firmware updates, recommended)
            7) Enable mood lighting (look at the signal LED)
            8) Reboot
            9) Quit\n
            '''
        )
        match choice:
            case '1':
                changeRootPwd(conn)
            case '2':
                usrShell(conn)
            case '3':
                adbTemp(conn)
            case '4':
                adbPersist(conn)
            case '5':
                ftpEnable(conn)
            case '6':
                disableOmadm(conn)
            case '7':
                moodLighting(conn)
            case '8':
                reboot(conn)
            case '9':
                quit(conn)
            case _:
                print('Please enter a valid choice (1-9)')
                chooseAction(conn)
    chooseAction(conn)
