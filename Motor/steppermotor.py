from collections import deque
from os import system
from time import sleep

import pigpio

# GPIO pins of the steppermotor
steppins = [17, 27, 22, 18]

# Step sequence for the steppermotor
fullstepsequence = (
    (1, 0, 1, 0),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
    (1, 0, 0, 1),
)


class StepperMotor:
    def __init__(self, pi, pins, sequence):
        # Check if the pigpio daemon is running
        if not isinstance(pi, pigpio.pi):
            raise TypeError("The daemon isn't initialized yet.")

        # Set pins in list to output
        for pin in pins:
            pi.set_mode(pin, pigpio.OUTPUT)

        self.deque = deque(sequence)  # Queuing the step sequence
        self.pi = pi  # Pi object is part of the class
        self.__delay_after_step = None  # Delay after each step

    # Function to set the delay after each step
    def set_stepper_delay(self, step_freq):
        # Check if the step frequency is valid
        if (step_freq > 0) and (step_freq < 1500):
            self.__delay_after_step = 1 / step_freq

    # Function to do a step backward
    def do_counterclockwise_step(self):
        self.deque.rotate(-1)  # Rotate a step backwards in our frequency tuple
        self.do_step_and_delay(self.deque[0])  # Override bit encode with certain step

    # Function to do a step forward
    def do_clockwise_step(self):
        self.deque.rotate(1)  # Rotate a step forward in our frequency tuple
        self.do_step_and_delay(self.deque[0])

    def do_step_and_delay(self, step):
        number = 0
        for pin in steppins:
            self.pi.write(pin, step[number])
            number += 1
        sleep(self.__delay_after_step)

    def disable_stepper_motor(self, pins):
        for pin in pins:
            self.pi.write(pin, 0)


runs = 5

system("sudo systemctl disable pigpiod")
sleep(0.5)
system("sudo systemctl start pigpiod")

while runs > 0:
    pi_device = pigpio.pi()
    sp = StepperMotor(pi_device, steppins, fullstepsequence)
    sp.set_stepper_delay(600)
    for steps in range(5096):
        sp.do_clockwise_step()
    for steps in range(5096):
        sp.do_counterclockwise_step()
    runs -= 1
    sp.disable_stepper_motor(steppins)
    print(f"Runs available: {runs}")
