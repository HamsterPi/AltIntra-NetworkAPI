# Tested locally for prototyping.
# Need to add notifier when client is missing using counter, dict and list
# Need to remove device from dict when disconnected
# Need to add functionality to enable random client diconnection

# server.py
import socket
import threading
import sys
import time
import re
import os


class Server(object):

    def __init__(self, connected_devices = {}, ip_address = "0.0.0.0", port = 8000, server_running = True, serversocket = "", list_of_connected_ip = [], no_of_clients = 0):
        # Stores all devices connected to the server.
        self.connected_devices = connected_devices
        # The IP address for the server.
        self.ip_address = ip_address
        # The port from which the server is accessible.
        self.port = port
        # Enables server.
        self.server_running = server_running
        # Socket created to host server.
        self.serversocket = serversocket
        # List to keep track of all IP Addresses connected to server.
        self.list_of_connected_ip = list_of_connected_ip
        # Compares devices to number of clients. Used to determine if a device has gone offline.
        self.no_of_clients = no_of_clients
        self.new_list = []

    # The function for establishing the server.
    def start_server(self):
        print("\nServer started")

        # 32-bit IPv4, TCP/ICP.
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Provide the socket an ip address and port.
        socket_details = (self.ip_address, self.port)
        self.serversocket.bind(socket_details)
        # Limtited to 100 connections max.
        self.serversocket.listen(100)

    # The function that creates a thread for threading processes.
    def start_client_thread(self, connection, address, no_of_clients):
        th = threading.Thread(target=self.client_thread, args=(connection, address, self.no_of_clients))
        th.start()
        self.connected_devices[connection]['thread'] = th

    # The function that broadcasts data to all clients (except the original sender).
    def broadcast(self, message, original_conn):
        # Loop through connected devices and send data through connection.
        for connections in self.connected_devices:
            if connections != original_conn:
                connections.send(message.encode())

    # The function that handles a client connection thread.
    def client_thread(self, connection, address, no_of_clients):

        welcome = "Welcome to the Centralised Management System\n"
        # All strings are default unicode, so they must be converted back to bytes before being sent.
        connection.send(welcome.encode())

        # If the client sends the server data, send the data to every other client as well.
        while self.server_running:

            # Need to write code to handle if a client disappears from network
            # Send request to end client thread function.
            try:
                data = "Data please\n"
                connection.send(data.encode())

                message = connection.recv(1024)
                # Either data will come or the socket will timeout.
                if message is not None:

                    enc_message = message.decode()

                    dec_message, senders_name, termination_mess = self.decode_message(enc_message)

                    # Statement is used if the client device is going offline on purpose such by a keyboard interrupt. Used for testing.
                    if termination_mess == "End communication with server":

                       self.end_client_thread(connection)

                    elif re.match("H\w+\d", enc_message):

                        print("Hooray, you are still connected!")

                    else:

                        message_to_send = '{} {} < {} > {}'.format(senders_name, self.no_of_clients, address, dec_message)
                        print(message_to_send)
                        self.broadcast(message_to_send, connection)

                else:
                    pass

            except KeyboardInterrupt:
                print("Finished")

            except OSError:
               pass

    # The function that removes a disconnected client.
    def end_client_thread(self, original_connection):
        # Decrement number of clients as one is disconnected.
        self.no_of_clients -= 1
        # Duplicate connected devices.
        dict = self.connected_devices
        for connections in dict:
            # Iterate through connected devices.
            if connections == original_connection:
                # Close the connection that is being disconnected.
                connections.close()




    # The function that removes a client's name from the end of the message.
    def decode_message(self, message):
        # Splits message to get the senders name.
        split_message = message.split(" ") 
        # Leaves message intact to check if it is the termination message sent from client.
        term_message = message

        # Obtains the actual typed message.
        typed_message = split_message[0:-1]

        # Removes senders name from end of message.
        sender = split_message.pop(-1)

        # Rejoins the message with the sentence.
        join_typed_message = ""
        for word in typed_message:
            join_typed_message += word + " "

        # Return a tuple containing the message, the clients name and the original message.
        return (join_typed_message, sender, term_message)

    def connecting_client(self, no_of_clients):
        # Since a client is being connected, increment number of clients connected.
        self.no_of_clients += 1

        connection, address = self.serversocket.accept()

        # Obtain the new device's name upon connection to server.
        new_client = connection.recv(1024)
        new_client = new_client.decode()

        # Adds the device IP address along with name.
        self.add_client_to_list(self.list_of_connected_ip, address, new_client)

        # Adds IP Address and port to the connected devices dictionary.
        self.connected_devices[connection] = {'IP Address': address}

        # Print connected device info to check what is being displayed.
        print('Client {} {} connected'.format(no_of_clients, address))

        # Start thread for the client.
        self.start_client_thread(connection, address, no_of_clients)

    # The function that adds the IP address and name of a dispenser to list. This is done more than once and saves having to repeat code.
    def add_client_to_list(self, list, address, name):
        # Retrieves an IP Address and port and assigns them to variables.
        ip, port = address[0], address[1]

        list.append((ip, name))

    def get_status(self):
        message = "Give me your information"
        self.broadcast(message.encode())


# Main loop.
# Loops forever and if there is a cliet waitig to connect, make a thread for the client.
def main():

    server = Server()

    server.start_server()

    try:

        while True:

            print("Length of connected devices: ", len(server.connected_devices), "Number of Clients connected: ",  server.no_of_clients)

            print("List of dispensers connected ",  server.list_of_connected_ip)

            server.connecting_client(server.no_of_clients)

    except KeyboardInterrupt:

        print("\nServer shutting down")

        for connections in server.connected_devices:
            # Close all client connections.
            connections.close()

        server.serversocket.close()
        server.server_running = False

        print("\nGoodbye")
        os.system('python3 menu.py')
        #sys.exit(0)


if __name__ == '__main__':
    main()