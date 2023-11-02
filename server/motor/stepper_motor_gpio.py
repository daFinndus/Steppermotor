import time
import RPi.GPIO as GPIO


class StepperMotor:
    def __init__(self, pins, sequence):
        self.pins = pins  # Save pins
        self.sequence = sequence  # Save step sequence

        self.pins_reversed = self.pins[::-1]  # Reverse the pins
        self.sequence_reversed = self.sequence[::-1]  # Reverse the sequence

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # Set GPIO mode to BOARD

        # Set pins in the list to output
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

        self.__delay_after_step = None  # Delay after each step

        self.debug_mode = False

    # Function to set the delay after each step
    def set_stepper_delay(self, step_freq):
        # Check if the step frequency is valid
        if 0 < step_freq < 600:
            self.__delay_after_step = 1 / step_freq
            print(f"Set stepper delay to {1 / step_freq} seconds / {step_freq} Hz.")
        else:
            print("Invalid frequency. Please choose a number between 1 and 600.")

    # Function to do a step forward
    def do_clockwise_step(self, steps):
        for _ in range(steps):
            for step in range(4):
                if self.debug_mode: print(f"Step {step + 1}: ")
                for pin in range(4):
                    GPIO.output(self.pins[pin], self.sequence[step][pin])
                    if self.debug_mode: print(f"Set pin {self.pins[pin]} to {self.sequence[step][pin]}.")
                time.sleep(self.__delay_after_step)

    # Function to do a step backward - This should work, but doesn't
    def do_counterclockwise_step(self, steps):
        for _ in range(steps):
            for step in range(4):
                if self.debug_mode: print(f"Step {step + 1}: ")
                for pin in range(4):
                    GPIO.output(self.pins[pin], self.sequence_reversed[step][pin])
                    if self.debug_mode: print(f"Set pin {self.pins[pin]} to {self.sequence_reversed[step][pin]}.")
                time.sleep(self.__delay_after_step)

    # Function to clean up all pins
    def clean_up_gpio(self):
        for pin in self.pins:
            GPIO.output(pin, 0)
        GPIO.cleanup()
        print("Cleaned up all pins.")
