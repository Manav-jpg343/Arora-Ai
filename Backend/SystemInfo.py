"""
SystemInfo.py - Cross-Platform System Information Module

Provides system-level information like battery, brightness, disk usage,
network status, etc. Designed with cross-platform compatibility in mind.
"""

import os
import platform
import subprocess
import datetime


def get_system_info() -> dict:
    """Get comprehensive system information."""
    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "username": os.getenv("USERNAME") or os.getenv("USER", "Unknown"),
        "python_version": platform.python_version(),
        "timestamp": datetime.datetime.now().isoformat(),
    }

    # Platform-specific info
    if platform.system() == "Windows":
        info.update(_get_windows_info())
    elif platform.system() == "Darwin":
        info.update(_get_mac_info())
    elif platform.system() == "Linux":
        info.update(_get_linux_info())

    return info


def _get_windows_info() -> dict:
    """Get Windows-specific system info."""
    info = {}

    # Battery info
    try:
        import ctypes
        class SYSTEM_POWER_STATUS(ctypes.Structure):
            _fields_ = [
                ('ACLineStatus', ctypes.c_byte),
                ('BatteryFlag', ctypes.c_byte),
                ('BatteryLifePercent', ctypes.c_byte),
                ('SystemStatusFlag', ctypes.c_byte),
                ('BatteryLifeTime', ctypes.c_ulong),
                ('BatteryFullLifeTime', ctypes.c_ulong),
            ]

        status = SYSTEM_POWER_STATUS()
        ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status))

        if status.BatteryLifePercent != 255:
            info["battery_percent"] = status.BatteryLifePercent
            info["charging"] = status.ACLineStatus == 1
    except Exception:
        pass

    # Disk usage
    try:
        import shutil
        total, used, free = shutil.disk_usage("C:\\")
        info["disk_total_gb"] = round(total / (1024**3), 1)
        info["disk_used_gb"] = round(used / (1024**3), 1)
        info["disk_free_gb"] = round(free / (1024**3), 1)
    except Exception:
        pass

    # Memory
    try:
        result = subprocess.run(
            ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/format:list"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "TotalVisibleMemorySize" in line:
                val = line.split("=")[1].strip()
                if val:
                    info["ram_total_gb"] = round(int(val) / (1024**2), 1)
            elif "FreePhysicalMemory" in line:
                val = line.split("=")[1].strip()
                if val:
                    info["ram_free_gb"] = round(int(val) / (1024**2), 1)
    except Exception:
        pass

    # WiFi status
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "SSID" in line and "BSSID" not in line:
                info["wifi_ssid"] = line.split(":")[1].strip()
                break
    except Exception:
        pass

    return info


def _get_mac_info() -> dict:
    """Get macOS-specific system info."""
    info = {}
    try:
        result = subprocess.run(
            ["pmset", "-g", "batt"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "%" in line:
                import re
                match = re.search(r'(\d+)%', line)
                if match:
                    info["battery_percent"] = int(match.group(1))
                info["charging"] = "charging" in line.lower()
    except Exception:
        pass
    return info


def _get_linux_info() -> dict:
    """Get Linux-specific system info."""
    info = {}
    # Battery
    try:
        bat_path = "/sys/class/power_supply/BAT0/capacity"
        if os.path.exists(bat_path):
            with open(bat_path) as f:
                info["battery_percent"] = int(f.read().strip())
        status_path = "/sys/class/power_supply/BAT0/status"
        if os.path.exists(status_path):
            with open(status_path) as f:
                info["charging"] = f.read().strip().lower() == "charging"
    except Exception:
        pass
    return info


def get_running_processes() -> list[str]:
    """Get list of currently running process names."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=10
            )
            processes = set()
            for line in result.stdout.strip().split("\n"):
                if line:
                    name = line.split(",")[0].strip('"')
                    processes.add(name)
            return sorted(processes)
        else:
            result = subprocess.run(
                ["ps", "-eo", "comm"],
                capture_output=True, text=True, timeout=10
            )
            return sorted(set(result.stdout.strip().split("\n")[1:]))
    except Exception:
        return []


def get_downloads_folder() -> str:
    """Get the user's downloads folder path."""
    if platform.system() == "Windows":
        return os.path.join(os.path.expanduser("~"), "Downloads")
    elif platform.system() == "Darwin":
        return os.path.join(os.path.expanduser("~"), "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


def get_recent_downloads(n: int = 5) -> list[str]:
    """Get the N most recent files from the Downloads folder."""
    downloads = get_downloads_folder()
    try:
        files = []
        for f in os.listdir(downloads):
            filepath = os.path.join(downloads, f)
            if os.path.isfile(filepath):
                files.append((filepath, os.path.getmtime(filepath)))
        files.sort(key=lambda x: x[1], reverse=True)
        return [f[0] for f in files[:n]]
    except Exception:
        return []
