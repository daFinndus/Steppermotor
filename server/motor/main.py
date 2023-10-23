import stepper_motor as sp
import pigpio

pi = pigpio.pi()

motor = sp.StepperMotor(pi, [17, 27, 22, 18], sp.FULL_STEP_SEQUENCE)

motor.disable_stepper_motor()
