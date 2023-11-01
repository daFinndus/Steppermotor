import time
from collections import deque
from os import system

import pigpio


class StepperMotor:
    def __init__(self, pi, pins, sequence):
        # Check if the pigpio daemon is running
        if not isinstance(pi, pigpio.pi):
            raise TypeError("The daemon isn't initialized yet.")

        # Set pins in the list to output
        for pin in pins:
            pi.set_mode(pin, pigpio.OUTPUT)

        self.pins = pins  # Save pins
        self.sequence = sequence  # Save step sequence

        self.deque = deque(sequence)  # Queuing the step sequence
        self.pi = pi  # Pi object is part of the class
        self.__delay_after_step = None  # Delay after each step

    # Function to set the delay after each step
    def set_stepper_delay(self, step_freq):
        # Check if the step frequency is valid
        if 0 < step_freq < 1500:
            self.__delay_after_step = 1 / step_freq
            print(f"Set stepper delay to {1 / step_freq} seconds / {step_freq} Hz.")
        else:
            print("Invalid frequency. Please choose a number between 1 and 1499.")

    # Function to do a step forward
    def do_clockwise_step(self, amount):
        for _ in range(amount):
            self.deque.rotate(1)  # Rotate a step forward in our frequency tuple
            self.do_step_and_delay(self.deque[0])  # Override bit encode with a certain step
            print("Going forward...")

    # Function to do a step backward
    def do_counterclockwise_step(self, amount):
        for _ in range(amount):
            self.deque.rotate(-1)  # Rotate a step backwards in our frequency tuple
            self.do_step_and_delay(self.deque[0])  # Override bit encode with a certain step
            print("Going backward...")

    # Function to execute the step and then sleep for the __delay.after_step time
    def do_step_and_delay(self, step):
        number = 0  # Number to iterate through the steps
        for pin in self.pins:
            self.pi.write(pin, step[number])
            number += 1
        time.sleep(self.__delay_after_step)

    # Start the motor and enable the pins
    def enable_stepper_motor(self):
        self.pi = pigpio.pi()  # Initialize a new pigpio daemon
        print("Initialized a new pigpio daemon.")
        for pin in self.pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)  # Set pins to output
        print("Set pins to output.")
        self.deque = deque(self.sequence)  # Reset the deque
        print("Motor is powered on again.")

    # Stop the motor and disable the pins
    def disable_stepper_motor(self):
        for pin in self.pins:
            self.pi.write(pin, 0)  # Set all pins to 0
        self.pi.stop()  # Stop the pigpio daemon
        print("Motor is powered off and pins aren't in use by pigpio anymore.")
        print("Please restart the pigpio daemon to use the motor again.")


# Function to start the pigpio daemon
def start_pigpiod():
    system("sudo systemctl start pigpiod")
    time.sleep(0.5)
    print("Pigpio daemon is initialized.")


# Function to stop the pigpio daemon
def stop_pigpiod():
    system("sudo systemctl disable pigpiod")
    time.sleep(0.5)
    print("Pigpio daemon is disabled.")
