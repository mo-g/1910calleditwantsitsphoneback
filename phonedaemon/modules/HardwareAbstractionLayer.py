"""
# Rotary Dial Parser
# Expects the following hardware rules:
# 1 is 1 pulse
# 9 is 9 pulses
# 0 is 10 pulses
"""


from threading import Timer
from RPi import GPIO

class HardwareAbstractionLayer(object):
    """
    Superclass to allow disambiguation between different implementations of
    dialer hardware from different phone conversion projects.
    """

    # TODO: Why are these pins hardcoded? Should be config. So should Pi/not.
    pin_earpiece = 3  # on/off hook events THESE PINS ARE BCM NOT HARDWARE
    pin_digits = 4  # rotary data source. THESE PINS ARE BCM NOT HARDWARE
    pin_dialling = None  # this is high when the dialler is off.

    pulse_count = 0  # Count the number of pulses detected

    dialling_timer = None  # Timer object for dialling.
    onhook_timer = None  # Timer object to ensure we're on hook
    debounce_timer = None  # Timer object for debounce cleaning.

    last_input = 0
    digit_timeout = 0.9  # Assume rotation is done after 900ms

    def __init__(self):
        # Set GPIO mode to Broadcom SOC numbering
        GPIO.setmode(GPIO.BCM)

        # Listen for rotary movements
        GPIO.setup(self.pin_rotary, GPIO.IN)
        GPIO.add_event_detect(self.pin_rotary,
                              GPIO.BOTH,
                              callback=self.detect_click)

        # Listen for on/off hooks
        GPIO.setup(self.pin_onhook, GPIO.IN)
        GPIO.add_event_detect(self.pin_onhook,
                              GPIO.BOTH,
                              callback=self.earpiece_event,
                              bouncetime=100)

        self.onhook_timer = Timer(2, self.verifyHook)
        self.onhook_timer.start()

    def detect_click(self, channel):
        """
        GPIO detects a state change on the rotary detection pin. This is where
        I count the clicks and assemble a digit from the data.
        """

    def register_callback(self,
                          NumberCallback,
                          OffHookCallback,
                          OnHookCallback,
                          OnVerifyHook):
        """
        Register callbacks for the interface with the calling application
        """
        self.NumberCallback = NumberCallback
        self.OffHookCallback = OffHookCallback
        self.OnHookCallback = OnHookCallback
        self.OnVerifyHook = OnVerifyHook


class AstralHAL(HardwareAbstractionLayer):
    """
    Subclass of HardwareAbstractionLayer to support the dialer in phones from
    the late period of Astral PLC.
    """
    def __init__(self):
        super(AstralHAL, self).__init__()

    def something_astral_specific(self):
        """
        Do something specific to the Astral wall phone.
        """
        print 'Doing something!'

class ElektriskHAL(HardwareAbstractionLayer):
    """
    Subclass of HardwareAbstractionLayer to support the dialer in the
    AS Elektrisk Bureau desk phone.
    """

    def __init__(self):
        super(ElektriskHAL, self).__init__()

    def something_aseb_specific(self):
        """
        Do something specific to the AS Elektrisk Bureau desk phone.
        """
        print 'Doing something!'


