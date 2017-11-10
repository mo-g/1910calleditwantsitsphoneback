"""
This module simply provides the class DialTimer, which abstracts
threading.Timer to provide a more appropriate interface to DialTimer()
"""


from threading import Timer


class DialTimer(object):
    """
    This class runs a timer in the background. When the timer expires without
    Reset() being called, the number is sent to the SIP handler for dialling.
    This abstraction is probably very unnecessary, but it keeps
    TelephoneDaemon() a little cleaner.
    """

    timeout_length = 3  # Seems a sensible default to use.
    timer_object = None
    end_of_timer_callback = None

    def __init__(self):
        """
        Set up the class.
        """

        self.timer_object = Timer(self.timeout_length, self.timer_end)
        self.timer_object.start()

    def reset(self):
        """
        Reset the timer.
        """
        self.timer_object.cancel()
        self.__init__()

    def timer_end(self):
        """
        Make the callback to the calling application. This is unnecessary.
        """
        self.end_of_timer_callback()

    # Handles the callbacks we're supplying
    def register_callback(self, callback):
        """
        Register callback for timer. This is probably also super-unnecessary.
        """
        self.end_of_timer_callback = callback
