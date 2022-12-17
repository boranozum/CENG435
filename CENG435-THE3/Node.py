import socket
import sys
import threading
import pickle

distance_vector = {}
neighbors = []

def server(sock):
    conn = None
    try:
        while True:
            conn, addr = sock.accept()
            isChanged = False
            data = conn.recv(1024)
            data = pickle.loads(data)

            neighbour = 0
            for key in data.keys():
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
                conn.sendall(pickle.dumps(distance_vector))

    except socket.timeout:
        for key in distance_vector.keys():
            d = distance_vector[key]
            print(f'{port} -{key} | {d}')
        conn.close()


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

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen(int(node_count))
    server_socket.settimeout(5)

    server_thread = threading.Thread(target=server, args=(server_socket,))
    server_thread.start()

    for neighbor in neighbors:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', neighbor))
        client_socket.sendall(pickle.dumps(distance_vector))
        client_socket.close()

    server_thread.join()
    server_socket.close()

