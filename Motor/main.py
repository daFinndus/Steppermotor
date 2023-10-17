import pigpio
import steppermotor as sp

# GPIO pins of the steppermotor
steppins = [17, 27, 22, 18]

# Step sequence for the steppermotor
fullstepsequence = (
    (1, 0, 1, 0),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
    (1, 0, 0, 1),
)

sp.stop_pigpiod()  # Disable pigpio daemon
sp.start_pigpiod()  # Start pigpio daemon

pi_device = pigpio.pi()  # Initialize the pi object
sp_device = sp.StepperMotor(pi_device, steppins, fullstepsequence)  # Initialize the steppermotor object
sp_device.set_stepper_delay(500)  # Set frequency of steppermotor

sp_device.do_clockwise_step(2048)
sp_device.do_counterclockwise_step(2048)

sp_device.disable_stepper_motor(steppins)  # Turn off motor and clear pigpio ressources
