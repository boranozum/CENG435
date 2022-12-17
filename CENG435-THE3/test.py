import socket
import sys
import threading
import pickle

distance_vector = {}

def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.bind(("localhost", int(sys.argv[1])))
    s.listen(1)
    while True:
        try:
            conn, addr = s.accept()
            data = conn.recv(1024)
            print(pickle.loads(data))
        except socket.timeout:
            print("timeout")
            s.close()
            break

def send_distance_vector():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for key in distance_vector.keys():
        s.connect(("localhost", int(key)))
        s.sendall(pickle.dumps(distance_vector))

    s.close()

if __name__ == "__main__":

    with open(sys.argv[1] + ".costs", 'r') as f:
        node_count = f.readline().strip()
        for line in f:
            line = line.strip().split()
            distance_vector[int(line[0])] = int(line[1])

    server_thread = threading.Thread(target=server)
    server_thread.start()

    send_distance_vector()
    server_thread.join()