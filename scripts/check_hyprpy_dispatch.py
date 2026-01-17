
import hyprpy

h = hyprpy.Hyprland()

# Test 1: plain exec
# If dispatch prepends "dispatch", this sends "dispatch exec touch /tmp/hyprpy_test1"
print("Testing dispatch('exec touch /tmp/hyprpy_test1')")
h.dispatch("exec touch /tmp/hyprpy_test1")

import time
import os
time.sleep(0.5)
if os.path.exists("/tmp/hyprpy_test1"):
    print("SUCCESS: dispatch() prepends 'dispatch'")
else:
    print("FAILURE: dispatch() does NOT prepend 'dispatch' (or something else failed)")
    
# Test 2: explicit dispatch
# If dispatch prepends "dispatch", this sends "dispatch dispatch exec ..."
print("Testing dispatch('dispatch exec touch /tmp/hyprpy_test2')")
h.dispatch("dispatch exec touch /tmp/hyprpy_test2")
time.sleep(0.5)
if os.path.exists("/tmp/hyprpy_test2"):
    print("SUCCESS: dispatch('dispatch ...') works")
else:
    print("FAILURE: dispatch('dispatch ...') failed")
