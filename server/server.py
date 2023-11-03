from socket import *

import time
import threading
import motor.stepper_motor as sp

# GPIO pins of the stepper motor
_STEPPINS = [17, 27, 22, 18]

# Step sequence for the stepper motor
_STEP_SEQUENCE = (
    (1, 0, 1, 0),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
    (1, 0, 0, 1),
)


# This only works with the gpio version of the stepper_motor.py
class MyServer:
    def __init__(self):
        self.__ECHO_PORT = 50000  # Port for the server
        self.__BUFSIZE = 1024  # Set maximum bufsize

        self.name = f"{gethostname()}:{self.__ECHO_PORT}"

        self._motor = sp.StepperMotor(_STEPPINS, _STEP_SEQUENCE)  # Initialize stepper motor object

        self.data_recv = None  # Storage for received messages
        self.data_send = None  # Storage for sent messages

        self.socket_connection = socket(AF_INET, SOCK_STREAM)  # Create IpV4-TCP/IP-socket
        self.socket_connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Make IP reusable
        self.socket_connection.bind(('', self.__ECHO_PORT))  # Bind IP to socket
        self.socket_connection.listen(1)  # Listen for clients -> execute the following code after connection

        print("Server is running.")
        print(f"Server-Device: {gethostname()}")
        print(f"Server-IP Address: {gethostbyname(gethostname())}")

        # Wait until the client accepted the connection with the server
        # The variable self.conn stores every available information about the client
        self.conn, (self.remotehost, self.remoteport) = self.socket_connection.accept()
        print(f"Connected with '{self.remotehost}:{self.remoteport}'.")  # Print data about client

        self.exit = False  # Initiate boolean to end it all
        self.quit = False  # Initiate boolean to stop threads

        self.thread_recv = threading.Thread(target=self.worker_recv)  # Setup thread for receiving messages
        self.thread_recv.start()  # Start thread to receive messages

        self.lock = threading.Lock()

    # Function to receive messages
    def worker_recv(self):
        while not self.quit:  # While self.exit is false
            try:
                self.data_recv = self.conn.recv(self.__BUFSIZE)  # Receive data from the client with certain bufsize
            except Exception as e:  # Catch error and print
                print(f"Error in receiving message: {e}")
                break
            # Receive data from the client with certain bufsize
            with self.lock:  # Aquire lock so nothing can execute while the worker is running
                if self.data_recv:  # If server receives data from the client
                    self.function_dispatcher(self.data_recv.decode())
        print("Stopped thread because self.quit is true.")

    # Function for dispatching our messages
    def function_dispatcher(self, command):
        print(f"Entered command: '{command}'")
        command_parts = command.split()  # Split our commands based on whitespace

        # Dictionary with all available functions
        functions = {
            "set": self._motor.set_stepper_delay,
            "cw-step": self._motor.do_clockwise_step,
            "ccw-step": self._motor.do_counterclockwise_step,
            "clean": self._motor.clean_up_gpio,
            "disconnect": self.reset_connection,
            "shutdown": self.shutdown,
        }

        # Check if the received message is a registered function
        if command_parts[0] == "disconnect":
            threading.Thread(target=self.reset_connection).start()
        elif command_parts[0] == "shutdown":
            threading.Thread(target=self.shutdown).start()
        elif command_parts[0] in functions:
            if len(command_parts) == 1:
                functions[command_parts[0]]()
            elif len(command_parts) == 2:
                functions[command_parts[0]](int(command_parts[1]))
            else:
                print("Too many number of arguments.")
        else:
            print("Couldn't find function in dictionary.")

    # Reset the current connection and listen for clients again - Doesn't listen for clients again
    def reset_connection(self):
        print(f"Client {self.remotehost}:{self.remoteport} has disconnected.")
        self.socket_connection.close()  # Socket schließen
        print(f"Closed socket for: {self.name}")
        time.sleep(1)
        self.quit = True  # Stop everything that depends on exit
        self.thread_recv.join()  # Thread für den Empfang beenden
        print(f"Stopped thread for receiving new messages.")

        # Erneut auf Verbindungen warten
        print("Going to setup the socket again...")
        time.sleep(1)
        self.socket_connection = socket(AF_INET, SOCK_STREAM)  # Create IpV4-TCP/IP-socket
        self.socket_connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Make IP reusable
        self.socket_connection.bind(('', self.__ECHO_PORT))  # Bind IP to socket
        self.socket_connection.listen(1)  # Warten auf neue Clients

        print("Waiting for a new client...")

        # Warten auf neue Verbindung
        self.conn, (self.remotehost, self.remoteport) = self.socket_connection.accept()
        print(f"Connected with '{self.remotehost}:{self.remoteport}'.")

        # Starten des Empfangsthreads für den neuen Client
        self.quit = False
        self.thread_recv = threading.Thread(target=self.worker_recv)
        self.thread_recv.start()

    # Function to shut down the application
    def shutdown(self):
        try:
            self.quit = True  # Stop the while loop in worker_recv
            self.thread_recv.join()
            print("Stopped thread for receiving new messages.")
            self._motor.clean_up_gpio()
            print("Disabled stepper motor and cleaned up all pins.")
            time.sleep(1)
            self.socket_connection.close()  # Close socket
            print(f"Stopped connection for: {self.name}")
            self.exit = True  # Stop the whole application
        except KeyboardInterrupt:
            self._motor.clean_up_gpio()
            exit(1)
        finally:
            print("Shutting down...")
            time.sleep(3)
            exit(0)
