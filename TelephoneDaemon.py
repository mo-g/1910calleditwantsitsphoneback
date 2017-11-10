import os
import Queue
import signal
import sys
import yaml

from modules.Ringtone import Ringtone
from modules.RotaryDial import RotaryDial
from modules.Webserver import Webserver
from modules.DialTimer import DialTimer
from modules.linphone import Wrapper
# alternative SIP-implementation
#from modules.pjsip.SipClient import SipClient

callback_queue = Queue.Queue()

class TelephoneDaemon:
"""
This is the Daemon class, it sets up the sip connection and waits for events. 
"""
    # Number to be dialed
    dial_number = ""

    # On/off hook state
    offHook = False

    # Off hook timeout
    offHookTimeoutTimer = None

    RotaryDial = None
    SipClient = None
    WebServer = None
    DialTimer = None

    config = None

    def __init__(self):
        print "[STARTUP]"

        self.config = yaml.load(file("configuration.yml",'r'))

        signal.signal(signal.SIGINT, self.OnSignal)

        """
        So, here we need to allow selection of hardware ringing. This is fine
        for now though, so I won't change it till I implement ringing.
        """
        self.Ringtone = Ringtone(self.config)

        # This is to indicate boot complete. Not very realistic, but fun.
        #self.Ringtone.playfile(config["soundfiles"]["startup"])

        # Rotary dial
        self.RotaryDial = RotaryDial()
        self.RotaryDial.RegisterCallback(NumberCallback = self.GotDigit, OffHookCallback = self.OffHook, OnHookCallback = self.OnHook, OnVerifyHook = self.OnVerifyHook)

        """
        Need a system here to select the SIP backend programmatically, or by
        a code flag in the worst case.
        """
        self.SipClient = Wrapper.Wrapper()
        self.SipClient.StartLinphone()
        self.SipClient.SipRegister(self.config["sip"]["username"], self.config["sip"]["hostname"], self.config["sip"]["password"])
        self.SipClient.RegisterCallbacks(OnIncomingCall = self.OnIncomingCall, OnOutgoingCall = self.OnOutgoingCall, OnRemoteHungupCall = self.OnRemoteHungupCall, OnSelfHungupCall = self.OnSelfHungupCall)

        # Start SipClient thread
        self.SipClient.start()

        # Web interface to enable remote configuration and debugging.
        self.Webserver = Webserver(self)

        raw_input("Waiting.\n")

    def OnHook(self):
        print "[PHONE] On hook"
        self.offHook = False
        self.Ringtone.stophandset()
        # Hang up calls
        if self.SipClient is not None:
            self.SipClient.SipHangup()

    def OffHook(self):
        print "[PHONE] Off hook"
        self.offHook = True
        # Reset current number when off hook
        self.dial_number = ""
        
        """
        Need a Timer setup here.
        """
        self.DialTimer = None

        # TODO: State for ringing, don't play tone if ringing :P
        print "Try to start dialtone"
        self.Ringtone.starthandset(self.config["soundfiles"]["dialtone"])

        self.Ringtone.stop()
        if self.SipClient is not None:
            self.SipClient.SipAnswer()

    def OnVerifyHook(self, state):
        if not state:
            self.offHook = False
            self.Ringtone.stophandset()

    def OnIncomingCall(self):
        print "[INCOMING]"
        self.Ringtone.start()

    def OnOutgoingCall(self):
        print "[OUTGOING] "

    def OnRemoteHungupCall(self):
        print "[HUNGUP] Remote disconnected the call"
        # Now we want to play busy-tone..
        self.Ringtone.starthandset(self.config["soundfiles"]["busytone"])

    def OnSelfHungupCall(self):
        print "[HUNGUP] Local disconnected the call"

    def GotDigit(self, digit):
        print "[DIGIT] Got digit: %s" % digit
        self.Ringtone.stophandset()
        self.dial_number += str(digit)
        print "[NUMBER] We have: %s" % self.dial_number

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


        """
        This is bad. we need a better way to detect when dialling is completed
        in order to be agnostic about number length, allow operator calls, etc
        
        if len(self.dial_number) == 8:
            if self.offHook:
                print "[PHONE] Dialing number: %s" % self.dial_number
                self.SipClient.SipCall(self.dial_number)
                self.dial_number = ""
       """
       
       
       self.DialTimer.Reset() #Reset the clock that waits for end of dialling.


    def OnTimerExpired(self):
        print "[OFFHOOK TIMEOUT]"
        if self.dial_number:
            print "[PHONE] Dialling number: %s" % self.dial_number
            self.SipClient.SipCall(self.dial_number)
        self.dial_number = ""

    def OnSignal(self, signal, frame):
        print "[SIGNAL] Shutting down on %s" % signal
        self.RotaryDial.StopVerifyHook()
        self.SipClient.StopLinphone()
        sys.exit(0)

def main():
    TDaemon = TelephoneDaemon()

if __name__ == "__main__":
    main()
