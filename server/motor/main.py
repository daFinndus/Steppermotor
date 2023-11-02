from stepper_motor_gpio import StepperMotor

# GPIO pins of the stepper motor
__STEPPINS = [17, 27, 22, 18]

# Step sequence for the stepper motor
__STEP_SEQUENCE = (
    (1, 0, 1, 0),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
    (1, 0, 0, 1),
)

motor = StepperMotor(__STEPPINS, __STEP_SEQUENCE)

motor.set_stepper_delay(200)
motor.do_clockwise_step(1000)
motor.set_stepper_delay(1)
motor.do_clockwise_step(10)
