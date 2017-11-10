import threading
from threading import Timer


class DialTimer:
    """
    This class runs a timer in the background. When the timer expires without
    Reset() being called, the number is sent to the SIP handler for dialling.
    """

    timeout_length = None
    TimerObject = None

    def __init__(self):
        """
        Set up the class.
        """

        self.offHookTimeoutTimer = Timer(5, self.OnOffHookTimeout)
        self.offHookTimeoutTimer.start()

    def Reset():
        """
        Reset the timer.
        """

    # Handles the callbacks we're supplying
    def RegisterCallback(self, NumberCallback, OffHookCallback,
                         OnHookCallback, OnVerifyHook):
        self.NumberCallback = NumberCallback
        self.OffHookCallback = OffHookCallback
        self.OnHookCallback = OnHookCallback
        self.OnVerifyHook = OnVerifyHook

        input = GPIO.input(self.pin_onhook)
        if input:
            self.OffHookCallback()
        else:
            self.OnHookCallback()
