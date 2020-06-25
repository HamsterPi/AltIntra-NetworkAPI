# Tested locally for prototyping.
# Throughout commenting, client, device and dispenser all refer to the same thing.
# Remember to edit the main function more, not the functions within the class.

# client.py
import socket
import select
import sys
import time


class Client(object):

    def __init__(self, name = "Client", ip_address = "0.0.0.0", port = 8000, server_connection = ""):
        # Name given to the dispenser for identification by server.
        self.name = name
        # The server IP address that the dispenser will connect too. Server IP must be static to accomodate.
        self.ip_address = ip_address
        # The port from  which the server is accessible.
        self.port = port
        # The server connection implementing the socket class.
        self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect client to the server with the initiation of client class.
    def is_client_connected(self):
        # Connection begins as false.
        connected = False

        # While the connection is false, attempt to establish a working connection.
        while not connected:
            
            try:
                # If successfully connected, change connected boolean to true and return to main loop.
                self.server_connection.connect((self.ip_address, self.port))
                connected = True
                print("Client Connected\n")
            # An error that occurs if  the client attempts to connect to the server and it fails.
            except ConnectionRefusedError:
                connected = False
            # This error occurs if the connection is already successful, this happens after continuous loops through the main loop
            except OSError:
                # After the connection is successful, this ensures that the connection remains true if it has already been established between client and server.
                connected = True

        # Return the state on this connection.
        return connected


    # The function that changes a device's name.
    def set_clients_name(self):
        self.name = "HandSanitiserDispener22"

    # The function that returns a device's name.
    def get_clients_name(self):
        return self.name

    # The function that encodes the device's name and sends it to the server for identification.
    def send_name_to_server(self):

        self.set_clients_name()
        self.server_connection.send(self.get_clients_name().encode())

    # The function that obtains and decodes data from the server, primarily used to retrieve the status of device.
    def get_data_from_server(self, data_input):

        message = data_input.recv(1024)

        parsed_message = message.decode()

        # Print message to demonstrate successful connection.
        print(parsed_message)

        if parsed_message == "Data please\n":
            self.send_data_to_server()

    # The functon that sends an encoded response back to the server, primarily stats and whether the connection is true.
    def send_data_to_server(self):

        message = self.data_from_device()
        message_with_sender = message + " " + self.name

        self.test_time(10)
        self.server_connection.send(message_with_sender.encode())

    # The function that obtains data from sensors. Currently a dummy function as the physical components don't exist.
    def data_from_device(self):
        return "Data"

    # The function that ends a connection to the server in a controlled fashion with a keyboard interrupt (CTRL+C). Useful for testing.
    def end_connection_to_server(self):

        message = "End Communication with Server"
        self.server_connection.send(message.encode())
        self.server_connection.close()
        print("\nSuccessfully Disconnected from Server")
        sys.exit(0)

    # The function for describing the interval timer that is used for testing. It requires a robust timer that both client and server can use to ensure everything is working correctly.
    def test_time(self, interval):

        while interval > 0:
            time.sleep(1)
            interval -= 1



# Main function.
def main():
    try:
        # Create a client object.
        client = Client()

        # Infite loop to handle connection.
        while client.is_client_connected():

            # Connects client to the server.
            client.send_name_to_server()

            try:

                # Determines any inputs from the server.
                inputs = [client.server_connection]
                read, write, error = select.select(inputs, [], [])

                for data_input in read:

                    # Determine if data is being received from the server.
                    if data_input == client.server_connection:

                        client.get_data_from_server(data_input)

                    else:

                        # Determine if data is being received from the keyboard and print out what the user types back to them.
                        client.send_data_to_server()

            except KeyboardInterrupt:
                # End communication to server.
                client.end_connection_to_server()

    except BrokenPipeError:
        # Call main function and try again.
        main()

if __name__ == '__main__':
    main()
