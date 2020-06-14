#Tested Locally
# Need to add notifier when client is missing using counter, dict and list
# Need to remove device from dict when disconnected
# Need to add functionality to enable random client diconnection
#server.py
#from client import Client
import socket
import threading
import sys
import time
import re


class Server(object):

    def __init__(self, connected_devices = {}, ip_address = "0.0.0.0", port = 8000, server_running = True, serversocket = "", list_of_connected_ip = [], no_of_clients = 0):
        # Used to store the connected devices to server
        self.connected_devices = connected_devices
        # The IP address of the server
        self.ip_address = ip_address
        # The port upon which the server is accessible
        self.port = port
        # Turn server on
        self.server_running = server_running
        # A socket created to host server
        self.serversocket = serversocket
        # A list to keep track of all IP Addresses connected to server
        self.list_of_connected_ip = list_of_connected_ip
        # A number to compare devices to number of clients. This is used to later as a check if a device goes offline and notify the user of system
        self.no_of_clients = no_of_clients

        self.new_list = []

    def start_server(self):
        print("Server Started")

        #setup, 32-bit ipv4, TCP/ICP
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #give the socket an ip address and port
        socket_details = (self.ip_address, self.port)
        self.serversocket.bind(socket_details)
        self.serversocket.listen(100)  #serversocket.listen(100) - max 100 connections

    #function to create a thread
    def start_client_thread(self, connection, address, no_of_clients):
        th = threading.Thread(target=self.client_thread, args=(connection, address, self.no_of_clients))
        th.start()
        self.connected_devices[connection]['thread'] = th

    #broadcast function, send data to all clients(except the original sender)
    def broadcast(self, message, original_conn):
        # loop through connected devices
        # send data to connection
        for connections in self.connected_devices:
            if connections != original_conn:
                connections.send(message.encode())

    #function to handle a client connection thread
    def client_thread(self, connection, address, no_of_clients):

        welcome = "Welcome to the Centralised Management System\n"
        connection.send(welcome.encode()) # all strings are default unicode. converting back to bytes before it can be sent

        #if the client sends us data
        #send the data to every other client
        while self.server_running:

            # Need to write code to handle if a client disappears from network
            # Send to end client thread function
            try:
                data = "Data please\n"
                connection.send(data.encode())

                message = connection.recv(1024)
                #either data will come or socket will time out
                if message is not None:

                    enc_message = message.decode()

                    dec_message, senders_name, termination_mess = self.decode_message(enc_message)

                    # This if statement is used if the client device is going offline on purpose such as a keyboard interrupt. Used for testing
                    if termination_mess == "End Communication with Server":

                       self.end_client_thread(connection)

                    elif re.match("H\w+\d", enc_message): # enc_message == "HandSanitiserDispener1": # Using regular expressions to find the name of dispenser
                     #   name = enc_message # This entire section of code was used to try and discard duplicates of connected devices but was unable to figure out due to working in threads
                     #   pos_counter = []
                     #   i = 0
                     #   while i < len(self.list_of_connected_ip):
                     #       if self.list_of_connected_ip[i][1] == name:
                     #           pos_counter.append(1)
                     #       else:
                     #           pos_counter.append(0)
                     #       i += 1

                    #    if sum(pos_counter) > 1:
                    #       print("Too many with same name")
                    #       i = 0
                    #       while sum(pos_counter) > 1 and  i < len(pos_counter):
                    #           if pos_counter[i] == 1:
                    #             # print("I see a duplicate")
                    #              self.list_of_connected_ip.pop(i)
                    #           i += 1
                    #       print("Hooray duplicates are gone")
                        print("Hooray you are still connected")

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

    # A function to remove a disconnected client
    def end_client_thread(self, original_connection):
        self.no_of_clients -= 1 # Decrement No. of clints as one is disconnected
        dict = self.connected_devices # Duplicate connected devices # Not needed was duplicated for a previous attempt of removing a client
        for connections in dict: # Iterate through connected devices
            if connections == original_connection:
                connections.close() # Close the connection that is disconnecting




    #function to remove clients name from the end of the message
    def decode_message(self, message):
        split_message = message.split(" ") # Splits message to get senders name
        term_message = message # Leaves message intact to check if it is the termination message sent from client

        typed_message = split_message[0:-1] # Gets the actual typed message

        sender = split_message.pop(-1) # Removes senders name from end of message

        join_typed_message = "" # Joins the message back into a sentence
        for word in typed_message:
            join_typed_message += word + " "

        return (join_typed_message, sender, term_message) # Return a tuple of message, clients name and original message

    def connecting_client(self, no_of_clients):
        self.no_of_clients += 1 # Since a client is being connected, increment No. of clients connected

        connection, address = self.serversocket.accept() #conn = connection object, addr = clients ip address and port

        new_client = connection.recv(1024) # Gets the new devices name upon connection to server
        new_client = new_client.decode()

        self.add_client_to_list(self.list_of_connected_ip, address, new_client) # Adds the device IP Address along with name

        self.connected_devices[connection] = {'IP Address': address} # Adds IP Address and port to connected devices dictionary

        print('Client {} {} connected'.format(no_of_clients, address)) # Test print to check what is being displayed

        #start thread for the client
       # print(self.connected_devices) # Print statement to check what devices are connected
        self.start_client_thread(connection, address, no_of_clients)

    # Function to add ip address and name of dispenser to list. This is used as this is done more than once and saved writing repeating amounts of code
    def add_client_to_list(self, list, address, name):
        ip, port = address[0], address[1]  # Gets the IP Address and port and assigns them to variables

        list.append((ip, name))

    def get_status(self):
        message = "Give me your information"
        self.broadcast(message.encode())


#main loop
#loop forever
#if there is a cliet waitig to connect
#make a thread for the client
#goto 1
def main():

    server = Server()

    server.start_server()

    try:

        while True:

            print("Length of connected devices: ", len(server.connected_devices), "Number of Clients connected: ",  server.no_of_clients)

            print("List of dispensers connected ",  server.list_of_connected_ip)

            server.connecting_client(server.no_of_clients)

    except KeyboardInterrupt:

        print("server shutting down")

        for connections in server.connected_devices:
            connections.close() # close all our client connections

        server.serversocket.close()
        server.server_running = False

        print("Goodbye")
        sys.exit(0)


if __name__ == '__main__':
    main()
