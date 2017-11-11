"""
This is the Daemon app that runs the a SIP phone on a Raspi with cool added
hardware, like an Astral wallphone or an AS Elektrisk Bureau.

Most of the threading is going to be via HardwareAbstractionLayer. That's
where we need to asynchronously wait for interactions from the user. SipClient
will logically also need to make asynchronous callbacks - 'we are connected,
stop playing the ringing tone.

WebServer is also going to have some callbacks.
"""


import os
import Queue
import signal
import sys
import yaml


from phonedaemon.modules.Ringer import AlsaRinger
from phonedaemon.modules.HardwareAbstractionLayer \
    import HardwareAbstractionLayer
from phonedaemon.modules.Webserver import Webserver
from phonedaemon.modules.DialTimer import DialTimer
from phonedaemon.modules.pjsip.SipClient import SipClient


CALLBACK_QUEUE = Queue.Queue()

class TelephoneDaemon(object):
    """
    This is the Daemon class, it sets up the sip connection and waits for
    events.
    """
    config = None  # Contains config loaded from yaml.
    dialling_timeout = None  # How long off-hook before tim

    dial_number = ""  # Stores the number to be dialled.

    off_hook = False  # Flag: Is the earpiece on or off the hook?

    app_hal = None
    app_sip_client = None
    app_webserver = None
    app_timer = None
    app_ringer = None

    def __init__(self):
        print "[STARTUP]"

        self.config = yaml.load(file("configuration.yaml", 'r'))

        if "diallingtimeout" in self.config:
            self.dialling_timeout = int(self.config["diallingtimeout"])
            print "[INFO] Using dialling timeout value:", self.dialling_timeout

        self.app_timer = DialTimer(timeout_length=self.dialling_timeout)

        signal.signal(signal.SIGINT, self.OnSignal)

        # TODO: Select tone/hardware ring when latter is implemented.
        self.app_ringer = AlsaRinger(self.config["soundfiles"],
                                 self.config["alsadevices"])

        self.app_webserver = Webserver(self)


        # TODO: We're going to ignore all SIP stuff till we have the HAL good.
        """
        self.app_sip_client = SipClient()
        self.app_sip_client.SipRegister(self.config["sip"]["username"],
                                        self.config["sip"]["hostname"],
                                        self.config["sip"]["password"])
        self.app_sip_client.RegisterCallbacks(
            OnIncomingCall=self.on_incoming_call,
            OnOutgoingCall=self.on_outgoing_call,
            OnRemoteHungupCall=self.on_remote_hungup_call,
            OnSelfHungupCall=self.on_self_hungup_call)

        # Start SipClient thread
        self.app_sip_client.start()
        """

        raw_input("Waiting.\n")


    def earpiece_lifted:
        """
        The user has lifted the earpiece. Start dialling.
        """
        print "[INFO] Handset lifted.
    
    def number_complete:
        """
        The user has entered a number. Send to SIP or handle.
        """
        print [INFO] Number complete

    def timeout_reached:
        """
        The user has not entered a number. Play the timeout tone.
        """
        self.app_ringer.play_error()

    def earpiece_replaced:
        """
        The user has replaced the earpiece. Whatever you're doing. stop.
        Stop all tones, close SIP call, stop dialling.
        """

    def call_failed:
        """
        The SIP client returned an error on dialling. Stop all tones and play
        the error code.
        """

    def incoming_call:
        """
        The SIP client reports an incoming call. Cancel dialling and play the
        ringtone. This should also trap the earpiece so that the call can be
        answered.
        """

    def on_hook(self):
        print "[PHONE] On hook"
        self.offHook = False
        self.Ringtone.stophandset()
        # Hang up calls
        if self.app_sip_client is not None:
            self.app_sip_client.SipHangup()

    def off_hook(self):
        print "[PHONE] Off hook"
        self.offHook = True
        # Reset current number when off hook
        self.dial_number = ""

        self.app_timer.start()

        # TODO: State for ringing, don't play tone if ringing :P
        print "Try to start dialtone"
        self.app_ringer.starthandset("dialtone")

        self.app_ringer.stop()
        if self.app_sip_client is not None:
            self.app_sip_client.SipAnswer()

    def on_verify_hook(self, state):
        if not state:
            self.offHook = False
            self.app_ringer.stophandset()

    def on_incoming_call(self):
        print "[INCOMING]"
        self.app_ringer.start()

    def on_outgoing_call(self):
        print "[OUTGOING] "

    def on_remote_hungup_call(self):
        print "[HUNGUP] Remote disconnected the call"
        # Now we want to play busy-tone..
        self.app_ringer.starthandset("busytone")

    def on_self_hungup_call(self):
        print "[HUNGUP] Local disconnected the call"

    def got_digit(self, digit):
        print "[DIGIT] Got digit: %s" % digit
        self.app_ringer.stophandset()
        self.dial_number += str(digit)
        print "[NUMBER] We have: %s" % self.dial_number

        self.app_timer.reset()  # Reset the end-of-dialling clock.

        """
        # Shutdown command, since our filesystem isn't read only (yet?)
        # This hopefully prevents dataloss.
        # TODO: stop rebooting..

        Commented for probable removal. I may add a reboot command to the web
        interface, but the device is set up for SSH, and I don't forsee a
        situation where a clean reboot is needed but ssh is inaccessible.

        if self.dial_number == "0666":
            self.Ringtone.playfile(self.config["soundfiles"]["shutdown"])
            os.system("halt")
        """

    def on_timer_end(self):
        print "[OFFHOOK TIMEOUT]"
        if self.dial_number:
            print "[PHONE] Dialling number: %s" % self.dial_number
            self.app_sip_client.SipCall(self.dial_number)
        self.dial_number = ""

    def OnSignal(self, signal, frame):
        print "[SIGNAL] Shutting down on %s" % signal
        #self.app_hal.StopVerifyHook()  # Not using this right now.
        #self.app_sip_client.StopLinphone()  # Replace with pjsip clean exit
        self.app_ringer.clean_exit()
        sys.exit(0)


def main():
    TDaemon = TelephoneDaemon()


if __name__ == "__main__":
    main()
