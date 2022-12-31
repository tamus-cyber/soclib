"""Miscellaneous functions for soclib"""
import os

def linux_session_check():
    """Check if we're on Wayland or X11 and print a message if we're not

    This function is meant to be called when copy/paste functionality is
    failing on Linux. It will check if we're on Wayland or X11 and print
    a message if we're not. This is meant to be called from a script
    that uses copy/paste functionality.

    Returns:
    - None
    """
    if os.name == "posix":
        # Run echo $XDG_SESSION_TYPE and check if it's wayland
        # If it is, then we're on Wayland
        # If it's not, then we're on X11
        session_manager = os.environ.get("XDG_SESSION_TYPE", "tty")
        # Ignore if using TTY
        if session_manager == "tty":
            return
        if session_manager == "wayland":
            print("Wayland detected. In order to use copy/paste functionality, \
                you must install wl-clipboard.")
        elif session_manager == "x11":
            print("X11 detected. In order to use copy/paste functionality, \
                you must install xclip.")
        else:
            print("Session manager is neither Wayland nor X11. You will have \
                to find a way to use copy/paste functionality manually.")
            return

if __name__ == "__main__":
    print("This script is meant to be imported as a module")
