import socket
import threading	# using threading to enable sharing of one model instance instead of each process loading its own instance
import os
import time
N_SAMPLES = 16000*30
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

#model, tokenizer, transcribe_options, decode_options = load_model() # one model timeshared among clients -- use mutex

#buf = bytearray(0,0,0,0,0) 
#transcribe(model, tokenizer, transcribe_options, decode_options, buf) # test outside of sock

def handle_client(conn, addr):
	print(f"[client] Connection from {addr}")
	buffer = [bytearray(),bytearray()]
	b = 0
	offset = 0
	try:
		while True:
			data = conn.recv(640)  	# 20ms SLIN
			if not data:
				print(f"[client] Connection closed by {addr}")
				break
			if b == 1:
				buffer[1].extend(data)
				bn = len(buffer[1])
				if (bn - offset) >= 80000:			# every 5 seconds
					print(f"transcribe: {bn//16000} {bn}")
					if bn > N_SAMPLES:			# truncate if greater than 30 seconds
						print(f"more than 30 sec ... {bn-N_SAMPLES}")  
						data[:] = buffer[1][-(bn-N_SAMPLES):]
						buffer[1][:] = buffer[1][:N_SAMPLES]
					# transcribe(model, tokenizer, transcribe_options, decode_options, buffer[1]) 
					offset += 80000
					if bn >= N_SAMPLES:
						buffer[1].clear()
						offset = 0
					if bn > N_SAMPLES:
						print(f"repopulate ... {len(data)}")
						buffer[1].extend(data)
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
