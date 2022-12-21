import socket
import sys
import threading
import pickle

distance_vector = {}
neighbors = []

if __name__ == '__main__':

    node_count = 0
    with open(sys.argv[1] + ".costs", 'r') as f:
        node_count = f.readline().strip()
        for line in f:
            line = line.strip().split()
            distance_vector[int(line[0])] = int(line[1])
            neighbors.append(int(line[0]))

    port = int(sys.argv[1])
    distance_vector[port] = 0

    for i in range(3000, 3000 + int(node_count)):
        if i not in distance_vector.keys():
            distance_vector[i] = 9999

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen(int(node_count))
    server_socket.settimeout(5)

    i = 0
    while i < len(neighbors):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', neighbors[i]))
            client_socket.sendall(pickle.dumps(distance_vector))
            client_socket.close()
            i+=1
        except:
            pass

    try:
        while True:
            isChanged = False

            for neighbor in neighbors:
                conn, addr = server_socket.accept()
                data = conn.recv(1024)
                data = pickle.loads(data)
                conn.close()

                neighbour = 0
                for key in data:
                    if data[key] == 0:
                        neighbour = key
                        break

                for key in data.keys():
                    if key in distance_vector.keys():
                        if distance_vector[key] > data[key] + distance_vector[neighbour]:
                            distance_vector[key] = data[key] + distance_vector[neighbour]
                            isChanged = True
                    else:
                        distance_vector[key] = data[key] + distance_vector[neighbour]
                        isChanged = True

            if isChanged:
                isChanged = False
                i = 0
                while i < len(neighbors):
                    try:
                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client_socket.connect(('localhost', neighbors[i]))
                        client_socket.sendall(pickle.dumps(distance_vector))
                        client_socket.close()
                        i += 1
                    except:
                        pass


    except socket.timeout:
        conn.close()
        server_socket.close()
        for key in distance_vector.keys():
            d = distance_vector[key]
            print(f'{port} -{key} | {d}')
