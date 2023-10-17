from server import MyServer


# Function to set up the socket and start our server
def start_server():
    server = MyServer()

    while not server.exit:
        pass
    print("The server has stopped.")


if __name__ == "__main__":
    start_server()
