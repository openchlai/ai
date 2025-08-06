import socket
import threading	# using threading to enable sharing of one model instance instead of each process loading its own instance
import os
import time
from mel import N_SAMPLES_BYTES
from aii import load_model, transcribe

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

model, tokenizer, transcribe_options, decode_options = load_model()

# model_name = "large-v3.pt" 
# model_alignment_heads = b"ABzY8gWO1E0{>%R7(9S+Kn!D~%ngiGaR?*L!iJG9p-nab0JQ=-{D1-g00"
#model_name = "/home/kimani/tiny.pt" 
#model_alignment_heads = b"ABzY8bu8Lr0{>%RKn9Fp%m@SkK7Kt=7ytkO"
#model, tokenizer, transcribe_options, decode_options = load_model(model_name, model_alignment_heads, "en", "transcribe") # one model timeshared among clients -- use mutex

#buf = bytearray()
#ts0 = time.time()
#audio_features = encode_audio(model, transcribe_options, decode_options, buf)
#result = decode_audio(model, tokenizer, transcribe_options, decode_options, audio_features, 0.0) # test outside of sock
#ts1 = time.time()
#diff = round(ts1-ts0,2)
#print(f"{diff} | {result}")


def handle_client(conn, addr):
	print(f"[client] Connection from {addr}")
	buffer = [bytearray(),bytearray()]
	b = 1
	offset = 0
	if 1: # try:
		while True:
			data = conn.recv(640)  	# 20ms SLIN

			if not data:
				print(f"[client] Connection closed by {addr}")
				break

			if b == 1:
				buffer[1].extend(data)
				bn = len(buffer[1]) 
				if (bn - offset) >= 160000:			# every 5 seconds
					bm = (bn - offset) - 160000
					if bm > 0:		# truncate excess bytes  
						data = buffer[1][-bm:]
						buffer[1][:] = buffer[1][:-bm]
						#print(f" > excess bytes: {bm} {len(data)} {len(buffer[1])}")

					ts0 = time.time()
					out = transcribe(model, tokenizer, transcribe_options, decode_options, buffer[1])
					ts1 = time.time()
					diff = round(ts1 - ts0,2)
					print(f"{diff:<6} | {bn//32000:<3} {bn} | {out}")

					"""
					ts0 = time.time()	
					result, outs = transcribe(model, tokenizer, transcribe_options, decode_options, buffer[1]) 
					ts1 = time.time()
					diff = round(ts1 - ts0,2)
					for o in outs:
						print(f"{diff:<6} | {bn//32000:<3} {bn} | {round(o['start'],2)}, {round(o['end'],2)}, {o['isend']} | {o['text']}")
					"""

					# todo: use sliding-window instead of reset
					offset += 160000
					if bn >= N_SAMPLES_BYTES:
						buffer[1].clear()
						offset = 0
						# todo calc word timestamps here
					
					if bm > 0:
						buffer[1].extend(data)
						#print(f" > repopulate:   {bm} {len(data)} {len(buffer[1])}")
				continue

			for index, byte in enumerate(data):
				if byte == 13:
					print(f"[client] uid={buffer[0]}")
					b=1
					continue
				buffer[b].append(byte)
	#except Exception as e:
	#	print(f"[client] Error: {e}")
	#finally:
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
	print("--------------------")
	start_server()
