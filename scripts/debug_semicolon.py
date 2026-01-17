
import os
import socket
import time

def send_raw(cmd):
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    sock_path = f"{xdg}/hypr/{sig}/.socket.sock"
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(sock_path)
            client.sendall(cmd.encode('utf-8'))
            return client.recv(4096).decode('utf-8').strip()
    except Exception as e:
        return str(e)

def main():
    # Test rules with semicolons
    print("Testing rules with semicolons...")
    filename = "/tmp/semicolon_test"
    if os.path.exists(filename): os.remove(filename)
    
    # [workspace 2;float]
    cmd = f"dispatch exec [workspace 2;float] touch {filename}"
    print(f"Sending: {cmd}")
    print(f"Response: {send_raw(cmd)}")
    
    time.sleep(1)
    if os.path.exists(filename):
        print("SUCCESS: Semicolon rule worked.")
    else:
        print("FAILURE: Semicolon rule failed.")

if __name__ == "__main__":
    main()
