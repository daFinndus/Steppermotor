import time
import pigpio
import steppermotor
from socket import *
from threading import Thread
from steppermotor import StepperMotor

# GPIO pins of the steppermotor
steppins = [17, 27, 22, 18]

# Step sequence for the steppermotor
fullstepsequence = (
    (1, 0, 1, 0),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
    (1, 0, 0, 1),
)


class MyServer:
    echo_port = 50000  # Port for the server
    bufsize = 1024  # Set maximum bufsize
    name = input("Set name: ").replace(" ", "")  # Set up a custom name

    def __init__(self):
        self.pi_device = pigpio.pi()  # Initialize pi object
        self.motor = StepperMotor(self.pi_device, steppins, fullstepsequence)  # Initialize steppermotor object

        self.data_recv = None  # Storage for received messages
        self.data_send = None  # Storage for sent messages

        self.socket_connection = socket(AF_INET, SOCK_STREAM)  # Create IpV4-TCP/IP-socket
        self.socket_connection.bind(('', self.echo_port))  # Bind IP to socket
        self.socket_connection.listen(1)  # Listen for clients -> execute following code after connection

        print("Server is running.")
        print(f"Server-Device: {gethostname()}")
        print(f"Server-IP Address: {gethostbyname(gethostname())}")

        # Wait until client accepted the connection with the server
        # The variable self.conn stores every available information about the client
        self.conn, (self.remotehost, self.remoteport) = self.socket_connection.accept()
        print(f"Connected with '{self.remotehost}:{self.remoteport}'.")  # Print data about client

        self.thread_recv = Thread(target=self.worker_recv)  # Setup thread for receiving messages
        # self.thread_send = Thread(target=self.worker_send)  # Setup thread for sending messages

        self.exit = False  # Initiate boolean to end it all

        self.thread_recv.start()  # Start thread to receive messages
        # self.thread_send.start()  # Start thread to send messages

    # Function to receive messages
    def worker_recv(self):
        while not self.exit:  # While self.exit is false
            try:
                self.data_recv = self.conn.recv(self.bufsize)
            except Exception as e:  # Catch error and print
                print(f"Error in receiving message: {e}")
            # Receive data from client with certain bufsize
            if self.data_recv:  # If server receives data from the client
                self.function_dispatcher(self.data_recv.decode())

    # Function to send messages
    def worker_send(self):
        while not self.exit:
            try:
                # Setup sendable data for the client which displays information about the server cpu temperature
                self.data_send = input().lower()  # Send custom text message to client

                # Format the data to a nice string
                self.data_send = f"{self.name}: '{self.data_send}'"

                # Send the client the data_send string
                self.conn.send(self.data_send.encode())

                # Sleep for a second
                time.sleep(1)
            except Exception as e:  # Catch error and print
                print(f"Error occurred in sending message: {e}")

    # Debug function
    @staticmethod
    def hello_print():
        print("Hello.")

    # Dispath function to execute afterward
    def function_dispatcher(self, command):

        print(f"Entered command: '{command}'")
        command_parts = command.split()

        functions = {
            "debug": self.hello_print,
            "start": steppermotor.start_pigpiod,
            "stop": steppermotor.stop_pigpiod,
            "disable": self.motor.disable_stepper_motor,
            "set": self.motor.set_stepper_delay,
            "cw-step": self.motor.do_clockwise_step,
            "ccw-step": self.motor.do_counterclockwise_step,
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
        # self.thread_send.join()  # Stop thread after function is executed completely
        self.socket_connection.close()  # Close socket
        print("Executing stop_connection() is done.")  # Debug
