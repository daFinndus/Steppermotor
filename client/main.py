from client import MyClient


# Function to set up the socket and connect to the server
def start_client():
    client = MyClient()

    # Wait until the client is stopped
    while not client.exit:
        pass
    print("The client is stopped.")


if __name__ == "__main__":
    start_client()
