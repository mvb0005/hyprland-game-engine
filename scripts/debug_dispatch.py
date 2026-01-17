
import os
import time
import socket
import json

# Manual socket implementation to avoid any library wrapping issues
def get_socket_path():
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    return f"{xdg}/hypr/{sig}/.socket.sock"

def send_raw(cmd):
    sock_path = get_socket_path()
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(sock_path)
            client.sendall(cmd.encode('utf-8'))
            resp = client.recv(4096).decode('utf-8').strip()
            return resp
    except Exception as e:
        return str(e)

def test_exec(name, cmd_str):
    filename = f"/tmp/{name}"
    if os.path.exists(filename):
        os.remove(filename)
    
    # The actual command we want hyprland to execute
    target_cmd = f"touch {filename}"
    
    # The full dispatch command string
    # We will format this in different ways
    if cmd_str == "PLAIN":
        # dispatch exec touch /tmp/name
        full = f"dispatch exec {target_cmd}"
    elif cmd_str == "QUOTED_CMD":
        # dispatch exec "touch /tmp/name"
        full = f"dispatch exec \"{target_cmd}\""
    elif cmd_str == "RULE_NO_QUOTE":
        # dispatch exec [workspace 2] touch /tmp/name
        full = f"dispatch exec [workspace 2] {target_cmd}"
    elif cmd_str == "RULE_QUOTE_ALL":
        # dispatch exec "[workspace 2]" "touch /tmp/name"
        full = f"dispatch exec \"[workspace 2]\" \"{target_cmd}\""
    elif cmd_str == "RULE_QUOTE_RULE":
        # dispatch exec "[workspace 2]" touch /tmp/name
        full = f"dispatch exec \"[workspace 2]\" {target_cmd}"
        
    print(f"Test {name}: Sending '{full}'")
    resp = send_raw(full)
    print(f"  Response: {resp}")
    
    time.sleep(0.5)
    
    if os.path.exists(filename):
        print(f"  SUCCESS: {filename} created.")
    else:
        print(f"  FAILURE: {filename} NOT created.")

def main():
    print("Starting Systemic Exec Debug...")
    print(f"Socket: {get_socket_path()}")
    
    test_exec("plain", "PLAIN")
    test_exec("quoted", "QUOTED_CMD")
    test_exec("rule_raw", "RULE_NO_QUOTE")
    test_exec("rule_quote_all", "RULE_QUOTE_ALL")
    test_exec("rule_quote_rule", "RULE_QUOTE_RULE")
    
    # Test complex commands with spaces
    # dispatch exec [workspace 2] sh -c 'touch /tmp/complex'
    full = "dispatch exec [workspace 2] sh -c 'touch /tmp/complex'"
    print(f"Test complex: Sending '{full}'")
    send_raw(full)
    time.sleep(0.5)
    if os.path.exists("/tmp/complex"):
        print("  SUCCESS: complex created.")
    else:
        print("  FAILURE: complex NOT created.")

if __name__ == "__main__":
    main()
