"""
This is the Daemon app that runs the a SIP phone on a Raspi with cool added
hardware, like an Astral wallphone or an AS Elektrisk Bureau.

Most of the threading is going to be via HardwareAbstractionLayer. That's
where we need to asynchronously wait for interactions from the user. SipClient
will logically also need to make asynchronous callbacks - 'we are connected,
stop playing the ringing tone.

WebServer is also going to have some callbacks.
"""


import Queue
import signal
import sys
import yaml


from phonedaemon.modules.Ringer import AlsaRinger
from phonedaemon.modules.HardwareAbstractionLayer \
    import HardwareAbstractionLayer
from phonedaemon.modules.DialTimer import DialTimer
# from phonedaemon.modules.Webserver import Webserver
# from phonedaemon.modules.pjsip.SipClient import SipClient


CALLBACK_QUEUE = Queue.Queue()

class TelephoneDaemon(object):
    """
    This is the Daemon class, it sets up the sip connection and waits for
    events.
    """
    config = None  # Contains config loaded from yaml.
    dialling_timeout = None  # How long off-hook before timeout
    reserved_numbers = {}  # Use for implementing app-hooks, e.g. Cortana

    entered_digits = ""  # Stores the number to be dialled.

    app_hal = None
    app_sipclient = None
    app_webserver = None
    app_timer = None
    app_ringer = None

    incoming_call = False

    def __init__(self):
        print "[STARTUP]"

        self.config = yaml.load(file("configuration.yaml", 'r'))

        if "diallingtimeout" in self.config:
            self.dialling_timeout = int(self.config["diallingtimeout"])
            print "[INFO] Using dialling timeout value:", self.dialling_timeout

        self.app_timer = DialTimer(timeout_length=self.dialling_timeout)
        # TODO: Select tone/hardware ring when latter is implemented.
        self.app_ringer = AlsaRinger(self.config["soundfiles"],
                                     self.config["alsadevices"])
        self.app_hal = HardwareAbstractionLayer()
        signal.signal(signal.SIGINT, self.sigint_received)
        #self.app_webserver = Webserver(self)  # Currently locks thread?
        self.app_hal.register_callbacks()


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

    def earpiece_lifted(self):
        """
        The user has lifted the earpiece. Start dialling.
        """
        print "[INFO] Handset lifted."

        if self.incoming_call:
            # answer the call
            return None

        self.entered_digits = ""
        # Begin wait for dialling state.

    def call_number(self):
        """
        The user has entered a number. Send to SIP or handle internally.
        """
        print "[INFO] Calling number"
        self.app_sipclient.SipCall(self.entered_digits)
        # Log call to call log.

    def timeout_reached(self):
        """
        Check if the user has entered a number. Play the timeout tone.
        """
        if self.entered_digits:
            self.call_number()
            return None
        print "[INFO] Number not entered."
        self.app_ringer.play_error()

    def digit_detected(self, digit):
        """
        The HAL has detected that a number has been dialled.
        Reset the timer and append the digit to the number to be dialled.
        """
        print "[INFO] Got digit:", digit
        self.entered_digits += digit
        self.app_timer.reset()

    def earpiece_replaced(self):
        """
        The user has replaced the earpiece. Whatever you're doing. stop.
        Stop all tones, close SIP call, stop dialling.
        """

    def call_failed(self):
        """
        The SIP client returned an error on dialling. Stop all tones and play
        the error code.
        """

    def call_received(self):
        """
        The SIP client reports an incoming call. Cancel dialling and play the
        ringtone. This should also trap the earpiece so that the call can be
        answered.
        """

    def remote_hangup(self):
        """
        The SIP client reports that the call terminated normally by remote
        hang up. Play the dialtone for retro fun.
        """

    def call_dropped(self):
        """
        The SIP client reports a dropped call.
        """

    def sigint_received(self, signal_name, frame):
        """
        Catch a signal from outside app (Ctrl-C) and shutdown cleanly.
        """
        print "[SIGNAL] Shutting down on:", signal_name
        self.app_hal.clean_exit()  # Not using this right now.
        #self.app_sip_client.Stop()  # Replace with real function when made
        self.app_ringer.clean_exit()
        sys.exit(0)


def main():
    """
    Start daemon and return exit code to command l
    """
    return TelephoneDaemon()


if __name__ == "__main__":
    main()
