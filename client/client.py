import json
import threading
import time
from socket import *
from threading import Thread

# Dictionary of help commands
_help_dict = {
    "help": "Display the help menu.",
    "set": "Set the delay after each step in Hz.",
    "cw-step": "Do a step clockwise.",
    "ccw-step": "Do a step counterclockwise - Doesn't work.",
    "cw-degrees": "Move the motor clockwise by degrees.",
    "ccw-degrees": "Move the motor counterclockwise by degrees.",
    "disconnect": "Disconnect from the server.",
    "shutdown": "Shutdown the application, client and server."
}


# This only works with the gpio version of the stepper_motor.py
class MyClient:
    def __init__(self):
        self.__SERVER_PORT = 50000  # Port for the server
        self.__BUFSIZE = 1024  # Set maximum bufsize

        self.host = input("Enter Server-IP Address: ").replace(" ", "")  # Set IP of host
        self.name = f"{gethostname()}:{self.__SERVER_PORT}"

        self.data_recv = None  # Storage for received messages
        self.data_send = None  # Storage for sent messages

        self.socket_connection = socket(AF_INET, SOCK_STREAM)  # Create IpV4-TCP/IP-socket
        self.socket_connection.connect((self.host, self.__SERVER_PORT))  # Connect to the server via IP and port

        print(f"Connected to Server: '{self.host}'.")

        self.exit = False  # Initiate boolean to end it all
        self.quit = False  # Initiate boolean to stop threads

        self.thread_send = Thread(target=self.worker_send)  # Setup thread for sending messages
        self.thread_send.start()  # Start thread to send messages

        self.lock = threading.Lock()  # Lock for the shutdown function

    # Function to send messages
    def worker_send(self):
        while not self.quit:
            try:
                # Setup data for the server which displays information about the client cpu frequency
                self.data_send = self.encode_json()  # Send a custom text message to server

                # Format the data to a nice string
                self.data_send = f"{self.data_send}"

                # Send the server the data_send string
                self.socket_connection.send(self.encode_json())

                # Sleep for a second
                time.sleep(1)
            except Exception as e:  # Catch error and print
                print(f"Error occurred in sending message: {e}")
        print("Stopped thread because self.quit is true.")

    # Function to formulate a registered message
    def prepare_message(self):
        while not self.quit:
            message = input("> ").lower()
            # Display the help menu
            if message == "help":
                for help_entry, help_desc in _help_dict.items():
                    print(f"{help_entry}: {help_desc}")
                break
            # Set the step delay in Hz
            elif message == "set":
                step_freq = input("Choose the frequency value > ")
                message = f"set {step_freq}"
                print(f"Setting up delay_after_step to {step_freq} Hz.")
            # Step clockwise
            elif message == "cw-step":
                step_amount = input("Choose how many steps the motor should make > ")
                message = f"cw-step {step_amount}"
            # Step counterclockwise
            elif message == "ccw-step":
                step_amount = input("Choose how many steps the motor should make > ")
                message = f"ccw-step {step_amount}"
            # Move clockwise by degrees
            elif message == "cw-degrees":
                degrees = input("Choose how many degrees the motor should make > ")
                message = f"cw-degrees {degrees}"
            # Move counterclockwise by degrees
            elif message == "ccw-degrees":
                degrees = input("Choose how many degrees the motor should make > ")
                message = f"ccw-degrees {degrees}"
            # Exit the socket connection
            elif message == "disconnect":
                threading.Thread(target=self.stop_connection).start()
            elif message == "shutdown":
                threading.Thread(target=self.shutdown).start()
            else:
                print("Your message isn't registered in our dictionary. Type 'help' for help.")
                break
            # Finally, return the message
            return message

    # Function to turn a message into json
    def encode_json(self):
        message = input("> ").lower()
        return json.dumps(message)

    # Function to stop the connection - Doesn't close the application
    def stop_connection(self):
        self.quit = True  # Stop the while loop in worker_send
        time.sleep(1)
        self.thread_send.join()  # Stop thread for sending messages
        print("Stopped thread for sending messages.")
        time.sleep(1)
        self.socket_connection.close()  # Close socket
        print(f"Stopped connection for: {self.name}")
        time.sleep(1)
        print("Closing the application...")
        time.sleep(1)
        self.exit = True  # Stop the whole application
        exit(0)

    # Function to shut down the application
    def shutdown(self):
        with self.lock:
            print("Shutting down...")
            self.stop_connection()
