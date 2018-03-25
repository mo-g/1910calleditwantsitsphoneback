import RPi.GPIO as GPIO
from threading import Timer
import time
from Rio import *

class RotaryDial:
 
    bounce_time = 25  # ms
    should_verify_hook = True

    def __init__(self, config):
        self.config = config
        Rio.init(GPIO.BOARD)

        self.rotation = Rin(self.config["pins"]["rotation_in"], bounce_interval=self.bounce_time)
        self.pulse = Rin(self.config["pins"]["pulse_in"], bounce_interval=self.bounce_time)
        self.hook = Rin(self.config["pins"]["hook_in"], bounce_interval=self.bounce_time)

        self.rotation_led = Rout(self.config["pins"]["rotation_out"])
        self.pulse_led = Rout(self.config["pins"]["pulse_out"])
        self.hook_led = Rout(self.config["pins"]["hook_out"])

        self.rotation_led.set(not self.rotation.state())
        self.pulse_led.set(self.pulse.state())

        self.rotation.changed = self.rotation_changed
        self.pulse.changed = self.pulse_changed
        self.hook.changed = self.hook_changed

        self.pulses = 0

    def hook_changed(self, new_state, event_time, previous_state_duration):
        self.hook_led.set(new_state)
        if new_state == 1:
            self.hook_state = 1
            self.OnHookCallback()
            
        else:
            self.hook_state = 0
            self.OffHookCallback()

    def StopVerifyHook(self):
        self.should_verify_hook = False

    def verifyHook(self):
        while self.should_verify_hook:
            state = GPIO.input(self.config["pins"]["hook_in"])
            self.OnVerifyHook(state)
            time.sleep(1)

    def pulse_changed(self, new_state, event_time, previous_state_duration):
        self.pulse_led.set(new_state)
        if new_state == 1:
            self.pulses += 1

    def rotation_changed(self, new_state, event_time, previous_state_duration):
        self.rotation_led.set(not new_state)

        if new_state == 0:
            # rotation_started
            self.pulses = 0
        else:
            if self.pulses == 0 or self.pulses > 10:
                if self.rotation_problem:
                    self.rotation_problem(self.pulses)
            else:
                self.rotation_finished(self.pulses % 10)

    # Handles the callbacks we're supplying
    def RegisterCallback(self, NumberCallback, OffHookCallback, OnHookCallback, OnVerifyHook, OnRotationProblem=None):
        self.NumberCallback = NumberCallback
        self.OffHookCallback = OffHookCallback
        self.OnHookCallback = OnHookCallback
        self.OnVerifyHook = OnVerifyHook

        self.rotation_finished = NumberCallback
        self.rotation_problem = OnRotationProblem

        input = GPIO.input(self.config["pins"]["hook_in"])
        print input
        if input:
            self.OnHookCallback()
        else:
            self.OffHookCallback()
