import pigpio
import motor.steppermotor as sp

from socket import *
from threading import Thread

# GPIO pins of the steppermotor
_steppins = [17, 27, 22, 18]

# Step sequence for the steppermotor
_fullstepsequence = (
    (1, 0, 1, 0),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
    (1, 0, 0, 1),
)


class MyServer:
    def __init__(self):
        self.__ECHO_PORT = 50000  # Port for the server
        self.__BUFSIZE = 1024  # Set maximum bufsize

        self.name = input("Set name: ").replace(" ", "")  # Set up a custom name

        self._pi_device = pigpio.pi()  # Initialize pi object
        self._motor = sp.StepperMotor(self._pi_device, _steppins, _fullstepsequence)  # Initialize steppermotor object

        self.data_recv = None  # Storage for received messages
        self.data_send = None  # Storage for sent messages

        self.socket_connection = socket(AF_INET, SOCK_STREAM)  # Create IpV4-TCP/IP-socket
        self.socket_connection.bind(('', self.__ECHO_PORT))  # Bind IP to socket
        self.socket_connection.listen(1)  # Listen for clients -> execute following code after connection

        print("Server is running.")
        print(f"Server-Device: {gethostname()}")
        print(f"Server-IP Address: {gethostbyname(gethostname())}")

        # Wait until client accepted the connection with the server
        # The variable self.conn stores every available information about the client
        self.conn, (self.remotehost, self.remoteport) = self.socket_connection.accept()
        print(f"Connected with '{self.remotehost}:{self.remoteport}'.")  # Print data about client

        self.exit = False  # Initiate boolean to end it all

        self.thread_recv = Thread(target=self.worker_recv)  # Setup thread for receiving messages
        self.thread_recv.start()  # Start thread to receive messages

    # Function to receive messages
    def worker_recv(self):
        while not self.exit:  # While self.exit is false
            try:
                self.data_recv = self.conn.recv(self.__BUFSIZE)  # Receive data from client with certain bufsize
            except Exception as e:  # Catch error and print
                print(f"Error in receiving message: {e}")
            # Receive data from client with certain bufsize
            if self.data_recv:  # If server receives data from the client
                self.function_dispatcher(self.data_recv.decode())

    # Function for dispatching our messages
    def function_dispatcher(self, command):
        print(f"Entered command: '{command}'")
        command_parts = command.split()  # Split our commands based on whitespace

        # Dictionary with all available functions
        functions = {
            "start": sp.start_pigpiod,
            "stop": sp.stop_pigpiod,
            "disable": self._motor.disable_stepper_motor,
            "set": self._motor.set_stepper_delay,
            "cw-step": self._motor.do_clockwise_step,
            "ccw-step": self._motor.do_counterclockwise_step,
        }

        # Check if the received message is a registered function
        if command_parts[0] in functions:
            if len(command_parts) == 1:
                functions[command_parts[0]]()
            elif len(command_parts) == 2:
                functions[command_parts[0]](int(command_parts[1]))
            else:
                print("Too many number of arguments.")
        else:
            print("Couldn't find function in dictionary.")

    # Function to stop the connection
    def stop_connection(self):
        self.exit = True  # Stop everything that depends on exit
        self.thread_recv.join()  # Stop thread after function is executed completely
        self.socket_connection.close()  # Close socket
        print(f"Stopped connection for: {self.name}")  # Debug