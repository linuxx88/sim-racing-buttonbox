import abc
import ctypes
import sys
import time

VALID_TYPES = {"tap", "hold_start", "hold_stop"}

# Win32 Constants
INPUT_KEYBOARD = 1
KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

class HexInt(int):
    def __repr__(self):
        return f"0x{self:02X}"

# DirectInput / hardware scan codes table
# 0x20: DIK_D (DRS), 0x11: DIK_W (Seat Up), 0x1F: DIK_S (Seat Down)
ACTION_KEY_MAP = {
    "drs": HexInt(0x20),
    "seat_up": HexInt(0x11),
    "seat_down": HexInt(0x1F),
    "seat_forward": HexInt(0x10),
    "seat_backward": HexInt(0x12),
    "pitch_up": HexInt(0x13),
    "pitch_down": HexInt(0x21),
    "yaw_left": HexInt(0x2C),
    "yaw_right": HexInt(0x2E),
    "fov_inc": HexInt(0x14),
    "fov_dec": HexInt(0x22),
    "brake_bias_dec": HexInt(0x30),
    "brake_bias_inc": HexInt(0x2F),
    "tc_inc": HexInt(0x31),
    "tc_dec": HexInt(0x32),
    "eb_inc": HexInt(0x16),
    "eb_dec": HexInt(0x24),
    "abs_inc": HexInt(0x15),
    "abs_dec": HexInt(0x23),
    "headlights_toggle": HexInt(0x26),
    "headlights_flash": HexInt(0x25),
    "wipers_cycle": HexInt(0x18),
    "pit_limiter": HexInt(0x19),
}

# Win32 Ctypes Structures
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class _INPUTunion(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", _INPUTunion),
    ]

# Conditional Win32 API binding
if sys.platform == "win32":
    SendInput = ctypes.windll.user32.SendInput
    SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
    SendInput.restype = ctypes.c_uint
else:
    SendInput = None


class InputInjector(abc.ABC):
    @abc.abstractmethod
    def handle(self, action: str, action_type: str) -> None:
        pass


class MockInjector(InputInjector):
    def handle(self, action: str, action_type: str) -> None:
        print(f"[MOCK_INJECTOR] Action: {action} | Type: {action_type}", flush=True)


class WindowsInjector(InputInjector):
    def __init__(self, key_map=None):
        self.key_map = key_map or ACTION_KEY_MAP

    def press(self, scan_code: int) -> None:
        if SendInput is None:
            return
        extra = ctypes.c_ulong(0)
        ki = KEYBDINPUT(
            wVk=0,
            wScan=scan_code,
            dwFlags=KEYEVENTF_SCANCODE,
            time=0,
            dwExtraInfo=ctypes.pointer(extra),
        )
        inp = INPUT(type=INPUT_KEYBOARD, union=_INPUTunion(ki=ki))
        SendInput(1, ctypes.pointer(inp), ctypes.sizeof(INPUT))

    def release(self, scan_code: int) -> None:
        if SendInput is None:
            return
        extra = ctypes.c_ulong(0)
        ki = KEYBDINPUT(
            wVk=0,
            wScan=scan_code,
            dwFlags=KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP,
            time=0,
            dwExtraInfo=ctypes.pointer(extra),
        )
        inp = INPUT(type=INPUT_KEYBOARD, union=_INPUTunion(ki=ki))
        SendInput(1, ctypes.pointer(inp), ctypes.sizeof(INPUT))

    def handle(self, action: str, action_type: str) -> None:
        scan_code = self.key_map.get(action)
        if scan_code is None:
            return

        if action_type == "tap":
            self.press(scan_code)
            time.sleep(0.05)
            self.release(scan_code)
        elif action_type == "hold_start":
            self.press(scan_code)
        elif action_type == "hold_stop":
            self.release(scan_code)


def get_injector() -> InputInjector:
    if sys.platform == "win32":
        return WindowsInjector()
    return MockInjector()
