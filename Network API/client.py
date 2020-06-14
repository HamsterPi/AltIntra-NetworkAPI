#Tested Locally
# Throughout commenting, client, device and dispenser all refer to the same thing, all is commented at different points and I kept on changing during

# Remember to edit the main function more, not the functions within the class

#client.py
import socket
import select
import sys
import time


class Client(object):

    def __init__(self, name = "Client", ip_address = "0.0.0.0", port = 8000, server_connection = ""):
        # Name given to the dispenser for identification by server
        self.name = name
        # The IP address the dispenser must connect too. This means Server IP must be static
        self.ip_address = ip_address
        # The port upon which the server is accessible
        self.port = port
        # Server connection using the socket class
        self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect client to server upon initiation of client class
    def is_client_connected(self):
        connected = False # Connection starts as false

        while not connected: # While the connection is false, try connect
            try:
                self.server_connection.connect((self.ip_address, self.port)) # if successfully connected, set connected to true and return to main loop
                connected = True
                print("Client Connected\n")
            except ConnectionRefusedError: # This is an error that occurs when the client tries to connect to server when it is not possible
                connected = False

            except OSError: # This error occurs if connection is already successful, this happens after continuous loops through the main loop
                connected = True # It just sets the connection as true as it means a connection has already been created between client and server

        return connected # return the boolean connected


    # Function to set the devices name
    def set_clients_name(self):
        self.name = "HandSanitiserDispener22"

    # A function to return the devices name
    def get_clients_name(self):
        return self.name

    # Send the devices name for identification for statistics
    def send_name_to_server(self):

        self.set_clients_name()
        self.server_connection.send(self.get_clients_name().encode())

    # A function to get data from the server, most likely used to get status of device
    def get_data_from_server(self, data_input):

        message = data_input.recv(1024)

        parsed_message = message.decode()

        print(parsed_message) # if we have data from the server, print it # Used for testing

        if parsed_message == "Data please\n":
            self.send_data_to_server()

    # Send a response to the get status sent by server, most likely stats and confirmation its still on
    def send_data_to_server(self):

        message = self.data_from_device()
        message_with_sender = message + " " + self.name

        self.test_time(10)
        self.server_connection.send(message_with_sender.encode())

    # Function to get data from sensors, just a dummy string there at the minute used for testing
    def data_from_device(self):
        return "Data"

    # End connection to server in a controlled fashion such as a keyboard interrupt, used for testing
    def end_connection_to_server(self):

        message = "End Communication with Server"
        self.server_connection.send(message.encode())
        self.server_connection.close()
        print("Successfully Disconnected from Server")
        sys.exit(0)

    # interval timer used for testing, must need a robust timer that both client and server can use to ensure everything is working correctly
    def test_time(self, interval):

        while interval > 0:
            time.sleep(1)
            interval -= 1



# Main function
def main():
    try:
        client = Client() # Creating a client object

        # Infinite loop running forever
        while client.is_client_connected():

            client.send_name_to_server() # Connecting client  to server

            try:

                inputs = [client.server_connection] # Only inputs should be from server
                read, write, error = select.select(inputs, [], []) #

                for data_input in read:

                    if data_input == client.server_connection: # are we getting data from the server

                        client.get_data_from_server(data_input)

                    else:

                        # we are getting data from the keyboard
                        # print out what the user types back to them
                        client.send_data_to_server()

            except KeyboardInterrupt:
                # end communication to server
                client.end_connection_to_server()

    except BrokenPipeError:
        main()

if __name__ == '__main__':
    main()
