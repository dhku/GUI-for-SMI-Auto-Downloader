import platform

_IS_MAC = platform.system() == "Darwin"

def fs(win_size, mac_size):
    return mac_size if _IS_MAC else win_size

def pt(win_size, mac_size):
    return mac_size if _IS_MAC else win_size
