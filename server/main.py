import motor.stepper_motor as sp
from server import MyServer


# Function to set up the socket and start our server
def start_server():
    sp.start_pigpiod()  # Start the pigpio daemon
    server = MyServer()  # Initialize our server

    # Wait until the server is stopped

    while not server.exit:
        pass
    print("The server has stopped.")


if __name__ == "__main__":
    start_server()
