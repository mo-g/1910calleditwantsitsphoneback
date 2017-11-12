"""
# Rotary Dial Parser
# Expects the following hardware rules:
# 1 is 1 pulse
# 9 is 9 pulses
# 0 is 10 pulses
"""


from threading import Timer
from RPi import GPIO


BCM_PINS = {
    "aseb": {
        "earpiece": 3,
        "digits": 4,
        "dialling": None
    },
    "astral": {
        "earpiece": 22,
        "digits" : 17,
        "dialling": 27
    }
}

CONVERT = {
    1:1,
    2:2,
    3:3,
    4:4,
    5:5,
    6:6,
    7:7,
    8:8,
    9:9,
    10:0
}

PROJECT = "astral"


class HardwareAbstractionLayer(object):
    """
    Superclass to allow disambiguation between different implementations of
    dialer hardware from different phone conversion projects.
    """

    pin_earpiece = BCM_PINS[PROJECT]["earpiece"]  # on/off hook events
    pin_digits = BCM_PINS[PROJECT]["digits"]  # rotary data source
    pin_dialling = BCM_PINS[PROJECT]["dialling"]  # high if not dialling

    pulse_count = 0  # Count the number of pulses detected

    onhook_timer = None  # Timer object to ensure we're on hook
    debounce_timer = None  # Timer object for debounce cleaning.

    dialling = False
    hook = False

    callback_digit = None
    callback_onhook = None
    callback_offhook = None

    def __init__(self):
        GPIO.setmode(GPIO.BCM)  # Broadcom pin numbers.

        GPIO.setup(self.pin_dialling, GPIO.IN) #Listen for dialling start/end.
        GPIO.add_event_detect(self.pin_dialling,
                              GPIO.BOTH,
                              callback=self.dialling_state)

        GPIO.setup(self.pin_digits, GPIO.IN) #Listen for digits.
        GPIO.add_event_detect(self.pin_digits,
                              GPIO.BOTH,
                              callback=self.detect_clicks)

        # Listen for on/off hooks
        GPIO.setup(self.pin_earpiece, GPIO.IN)
        GPIO.add_event_detect(self.pin_earpiece,
                              GPIO.BOTH,
                              callback=self.earpiece_event,
                              bouncetime=100)  # Is bouncetime a debounce constant!?

    def clean_exit(self):
        """
        Safely close the GPIO when closing the app.
        """
        GPIO.cleanup()

    def dialling_state(self, channel):
        """
        GPIO detects whether the rotary dial is active.
        """
        if not GPIO.input(channel):
            return None

        if not self.dialling:
            self.dialling = True
        else:
            pulses = self.pulse_count
            if pulses % 2:
                raise IOError("Count is not divisible by 2")
            self.callback_digit(CONVERT[pulses])

    def detect_clicks(self, channel):
        """
        GPIO detects a state change on the rotary detection pin. This is where
        I count the clicks and assemble a digit from the data.
        """
        if GPIO.input(channel):
            self.pulse_count += 1

    def earpiece_event(self, channel):
        """
        GPIO detects a state change
        """
        self.hook = bool(GPIO.input(channel))

        # Are we on hook or off hook?
        # If off hook, look for the dialling state.

    def register_callbacks(self,
                           callback_digit,
                           callback_onhook,
                           callback_offhook):
        """
        Register callbacks for the interface with the calling application
        """
        self.callback_digit = callback_digit
        self.callback_onhook = callback_onhook
        self.callback_offhook = callback_offhook

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


