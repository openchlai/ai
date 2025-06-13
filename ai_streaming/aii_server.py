import socket
# import multiprocessing
import threading	# using threading to enable sharing of one model instance instead of each process loading its own instance
import os
import time
#from aii import load_model, transcribe

"""
lock = threading.Lock()

# Try to acquire without blocking
if lock.acquire(blocking=False):
    try:
        print("Lock was free, and we acquired it.")
        # Do work while holding the lock
    finally:
        lock.release()
else:
    print("Lock is already held by another thread.")
"""

#model =	load_model() # one model timeshared among clients -- use mutex

def handle_client(conn, addr):
	print(f"[client] Connection from {addr}")
	buffer = [bytearray(),bytearray()]
	b = 0
	try:
		while True:
			data = conn.recv(640)  	# 20ms SLIN
			if not data:
				print(f"[client] Connection closed by {addr}")
				break
			if b == 1:
				#buffer[1].extend(data);
				#if :		# every 2 seconds
				#	transcribe(model, buffer) 
				#	buffer[1].reset()
				continue
			for index, byte in enumerate(data):
				if byte == 13:
					print(f"[client] uid={buffer[0]}")
					b=1
					continue
				buffer[b].append(byte)
	except Exception as e:
		print(f"[client] Error: {e}")
	finally:
		conn.close()

def start_server(host='127.0.0.1', port=8300):
	server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_sock.bind((host, port))
	server_sock.listen()
	print(f"[Main] Listening on {host}:{port}")

	while True:
		conn, addr = server_sock.accept()
		print(f"[Main] Accepted connection from {addr}")
		p = threading.Thread(target=handle_client, args=(conn, addr)) 
		p.start()

if __name__ == "__main__":
	start_server()
