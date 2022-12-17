import socket
import sys
import threading
import pickle
import time

distance_vector = {}
neighbours = []
port = 0
event = threading.Event()
finished = False

def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.bind(("localhost", port))
    s.listen(1)
    while True:
        isChanged = False
        try:
            conn, addr = s.accept()
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
                        print("Changed")
                else:
                    distance_vector[key] = data[key] + distance_vector[neighbour]
                    isChanged = True

            if isChanged:
                event.set()
        except socket.timeout:
            finished = True
            event.set()
            for key in distance_vector.keys():
                d = distance_vector[key]
                print(f'{port} -{key} | {d}')
            s.close()
            break


def client():

    send_distance_vector()

    while event.wait():
        if finished:
            break
        send_distance_vector()
        event.clear()

def send_distance_vector():
    for neighbour in neighbours:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", neighbour))
        s.sendall(pickle.dumps(distance_vector))
        s.close()

if __name__ == "__main__":
    port = int(sys.argv[1])
    with open(sys.argv[1] + ".costs", 'r') as f:
        node_count = f.readline().strip()
        for line in f:
            line = line.strip().split()
            neighbours.append(int(line[0]))
            distance_vector[int(line[0])] = int(line[1])

    distance_vector[port] = 0

    server_thread = threading.Thread(target=server)
    client_thread = threading.Thread(target=client)

    server_thread.start()
    client_thread.start()

    server_thread.join()
    client_thread.join()