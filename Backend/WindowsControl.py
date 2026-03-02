"""
WindowsControl.py - Comprehensive Windows Automation Module for Edith AI

This module provides full control over Windows including:
- Mouse control (click, move, drag, scroll)
- Keyboard control (type, hotkeys, key combinations)
- Window management (focus, minimize, maximize, move, resize, close)
- Screen capture and OCR
- Clipboard operations
- System commands and process management
- File/folder operations
"""

import pyautogui
import pyperclip
import subprocess
import os
import time
import ctypes
from typing import Optional, Tuple, List
import json

# Configure pyautogui safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions

# Try to import optional dependencies
try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False

try:
    from pywinauto import Application, Desktop
    from pywinauto.findwindows import find_windows, ElementNotFoundError
    HAS_PYWINAUTO = True
except ImportError:
    HAS_PYWINAUTO = False


# ==================== MOUSE CONTROL ====================

def mouse_click(x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1) -> str:
    """Click at position (x, y) or current position if not specified."""
    try:
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
            return f"Clicked {button} button {clicks} time(s) at ({x}, {y})"
        else:
            pyautogui.click(clicks=clicks, button=button)
            pos = pyautogui.position()
            return f"Clicked {button} button {clicks} time(s) at current position ({pos.x}, {pos.y})"
    except Exception as e:
        return f"Click failed: {str(e)}"

def mouse_double_click(x: Optional[int] = None, y: Optional[int] = None) -> str:
    """Double-click at position."""
    return mouse_click(x, y, clicks=2)

def mouse_right_click(x: Optional[int] = None, y: Optional[int] = None) -> str:
    """Right-click at position."""
    return mouse_click(x, y, button="right")

def mouse_move(x: int, y: int, duration: float = 0.25) -> str:
    """Move mouse to position (x, y)."""
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return f"Moved mouse to ({x}, {y})"
    except Exception as e:
        return f"Move failed: {str(e)}"

def mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> str:
    """Drag from start position to end position."""
    try:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
        return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"
    except Exception as e:
        return f"Drag failed: {str(e)}"

def mouse_scroll(clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> str:
    """Scroll up (positive) or down (negative) at position."""
    try:
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x, y)
            return f"Scrolled {clicks} clicks at ({x}, {y})"
        else:
            pyautogui.scroll(clicks)
            return f"Scrolled {clicks} clicks at current position"
    except Exception as e:
        return f"Scroll failed: {str(e)}"

def get_mouse_position() -> Tuple[int, int]:
    """Get current mouse position."""
    pos = pyautogui.position()
    return (pos.x, pos.y)

def get_screen_size() -> Tuple[int, int]:
    """Get screen resolution."""
    size = pyautogui.size()
    return (size.width, size.height)


# ==================== KEYBOARD CONTROL ====================

def type_text(text: str, interval: float = 0.02) -> str:
    """Type text character by character."""
    try:
        pyautogui.write(text, interval=interval)
        return f"Typed: {text[:50]}..." if len(text) > 50 else f"Typed: {text}"
    except Exception as e:
        return f"Type failed: {str(e)}"

def type_text_instant(text: str) -> str:
    """Type text instantly using clipboard (supports unicode)."""
    try:
        old_clipboard = pyperclip.paste()
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        pyperclip.copy(old_clipboard)  # Restore clipboard
        return f"Typed (instant): {text[:50]}..." if len(text) > 50 else f"Typed: {text}"
    except Exception as e:
        return f"Type failed: {str(e)}"

def press_key(key: str) -> str:
    """Press a single key (e.g., 'enter', 'tab', 'escape', 'f1')."""
    try:
        pyautogui.press(key)
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Key press failed: {str(e)}"

def hotkey(*keys) -> str:
    """Press a combination of keys (e.g., 'ctrl', 'c' for copy)."""
    try:
        pyautogui.hotkey(*keys)
        return f"Pressed hotkey: {'+'.join(keys)}"
    except Exception as e:
        return f"Hotkey failed: {str(e)}"

def hold_key(key: str, duration: float = 0.5) -> str:
    """Hold a key for specified duration."""
    try:
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        return f"Held key '{key}' for {duration}s"
    except Exception as e:
        return f"Hold key failed: {str(e)}"

# Common keyboard shortcuts
def copy() -> str:
    return hotkey('ctrl', 'c')

def paste() -> str:
    return hotkey('ctrl', 'v')

def cut() -> str:
    return hotkey('ctrl', 'x')

def undo() -> str:
    return hotkey('ctrl', 'z')

def redo() -> str:
    return hotkey('ctrl', 'y')

def select_all() -> str:
    return hotkey('ctrl', 'a')

def save() -> str:
    return hotkey('ctrl', 's')

def find() -> str:
    return hotkey('ctrl', 'f')

def new_tab() -> str:
    return hotkey('ctrl', 't')

def close_tab() -> str:
    return hotkey('ctrl', 'w')

def switch_window() -> str:
    return hotkey('alt', 'tab')

def close_window() -> str:
    return hotkey('alt', 'f4')

def open_task_manager() -> str:
    return hotkey('ctrl', 'shift', 'escape')

def open_run_dialog() -> str:
    return hotkey('win', 'r')

def open_file_explorer() -> str:
    return hotkey('win', 'e')

def minimize_all() -> str:
    return hotkey('win', 'd')

def screenshot() -> str:
    return hotkey('win', 'shift', 's')

def lock_screen() -> str:
    return hotkey('win', 'l')


# ==================== WINDOW MANAGEMENT ====================

def get_all_windows() -> List[dict]:
    """Get list of all open windows."""
    if not HAS_PYGETWINDOW:
        return []
    
    windows = []
    for w in gw.getAllWindows():
        if w.title:
            windows.append({
                "title": w.title,
                "left": w.left,
                "top": w.top,
                "width": w.width,
                "height": w.height,
                "visible": w.visible,
                "minimized": w.isMinimized,
                "maximized": w.isMaximized
            })
    return windows

def find_window(title_contains: str) -> Optional[object]:
    """Find a window by partial title match."""
    if not HAS_PYGETWINDOW:
        return None
    
    windows = gw.getWindowsWithTitle(title_contains)
    return windows[0] if windows else None

def focus_window(title_contains: str) -> str:
    """Bring a window to foreground by title."""
    try:
        if HAS_PYGETWINDOW:
            window = find_window(title_contains)
            if window:
                window.activate()
                return f"Focused window: {window.title}"
        
        # Fallback using pywinauto
        if HAS_PYWINAUTO:
            app = Application().connect(title_re=f".*{title_contains}.*")
            app.top_window().set_focus()
            return f"Focused window containing: {title_contains}"
        
        return f"Window '{title_contains}' not found"
    except Exception as e:
        return f"Focus failed: {str(e)}"

def minimize_window(title_contains: str = None) -> str:
    """Minimize a window or the active window if no title specified."""
    try:
        if title_contains and HAS_PYGETWINDOW:
            window = find_window(title_contains)
            if window:
                window.minimize()
                return f"Minimized: {window.title}"
        else:
            hotkey('win', 'down')
            return "Minimized active window"
        return f"Window '{title_contains}' not found"
    except Exception as e:
        return f"Minimize failed: {str(e)}"

def maximize_window(title_contains: str = None) -> str:
    """Maximize a window or the active window if no title specified."""
    try:
        if title_contains and HAS_PYGETWINDOW:
            window = find_window(title_contains)
            if window:
                window.maximize()
                return f"Maximized: {window.title}"
        else:
            hotkey('win', 'up')
            return "Maximized active window"
        return f"Window '{title_contains}' not found"
    except Exception as e:
        return f"Maximize failed: {str(e)}"

def restore_window(title_contains: str) -> str:
    """Restore a minimized window."""
    try:
        if HAS_PYGETWINDOW:
            window = find_window(title_contains)
            if window:
                window.restore()
                return f"Restored: {window.title}"
        return f"Window '{title_contains}' not found"
    except Exception as e:
        return f"Restore failed: {str(e)}"

def move_window(title_contains: str, x: int, y: int) -> str:
    """Move a window to position (x, y)."""
    try:
        if HAS_PYGETWINDOW:
            window = find_window(title_contains)
            if window:
                window.moveTo(x, y)
                return f"Moved {window.title} to ({x}, {y})"
        return f"Window '{title_contains}' not found"
    except Exception as e:
        return f"Move window failed: {str(e)}"

def resize_window(title_contains: str, width: int, height: int) -> str:
    """Resize a window."""
    try:
        if HAS_PYGETWINDOW:
            window = find_window(title_contains)
            if window:
                window.resizeTo(width, height)
                return f"Resized {window.title} to {width}x{height}"
        return f"Window '{title_contains}' not found"
    except Exception as e:
        return f"Resize window failed: {str(e)}"

def snap_window_left() -> str:
    """Snap active window to left half of screen."""
    return hotkey('win', 'left')

def snap_window_right() -> str:
    """Snap active window to right half of screen."""
    return hotkey('win', 'right')


# ==================== CLIPBOARD OPERATIONS ====================

def get_clipboard() -> str:
    """Get clipboard content."""
    try:
        return pyperclip.paste()
    except:
        return ""

def set_clipboard(text: str) -> str:
    """Set clipboard content."""
    try:
        pyperclip.copy(text)
        return f"Copied to clipboard: {text[:50]}..." if len(text) > 50 else f"Copied to clipboard: {text}"
    except Exception as e:
        return f"Clipboard set failed: {str(e)}"


# ==================== SCREEN CAPTURE ====================

def take_screenshot(filename: str = None, region: Tuple[int, int, int, int] = None) -> str:
    """Take a screenshot, optionally of a specific region (x, y, width, height)."""
    try:
        if filename is None:
            filename = f"screenshot_{int(time.time())}.png"
        
        if region:
            img = pyautogui.screenshot(region=region)
        else:
            img = pyautogui.screenshot()
        
        filepath = os.path.join(os.getcwd(), "Data", filename)
        img.save(filepath)
        return f"Screenshot saved to: {filepath}"
    except Exception as e:
        return f"Screenshot failed: {str(e)}"

def locate_on_screen(image_path: str, confidence: float = 0.9) -> Optional[Tuple[int, int, int, int]]:
    """Find an image on screen and return its location (x, y, width, height)."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            return (location.left, location.top, location.width, location.height)
        return None
    except Exception as e:
        return None

def click_image(image_path: str, confidence: float = 0.9) -> str:
    """Find an image on screen and click its center."""
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.click(location)
            return f"Clicked image at ({location.x}, {location.y})"
        return f"Image not found on screen: {image_path}"
    except Exception as e:
        return f"Click image failed: {str(e)}"


# ==================== SYSTEM COMMANDS ====================

def run_command(command: str, wait: bool = True) -> str:
    """Run a system command."""
    try:
        if wait:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout or result.stderr
            return f"Command executed: {command}\nOutput: {output[:500]}" if output else f"Command executed: {command}"
        else:
            subprocess.Popen(command, shell=True)
            return f"Command started in background: {command}"
    except subprocess.TimeoutExpired:
        return f"Command timed out: {command}"
    except Exception as e:
        return f"Command failed: {str(e)}"

def run_program(program_path: str, args: List[str] = None) -> str:
    """Run a program with optional arguments."""
    try:
        cmd = [program_path] + (args or [])
        subprocess.Popen(cmd)
        return f"Started program: {program_path}"
    except Exception as e:
        return f"Failed to start program: {str(e)}"

def run_powershell(script: str) -> str:
    """Run a PowerShell command or script."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", script],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout or result.stderr
        return output[:1000] if output else "PowerShell command executed"
    except Exception as e:
        return f"PowerShell failed: {str(e)}"

def open_url(url: str) -> str:
    """Open a URL in the default browser."""
    try:
        import webbrowser
        webbrowser.open(url)
        return f"Opened URL: {url}"
    except Exception as e:
        return f"Failed to open URL: {str(e)}"

def open_file(filepath: str) -> str:
    """Open a file with its default application."""
    try:
        os.startfile(filepath)
        return f"Opened file: {filepath}"
    except Exception as e:
        return f"Failed to open file: {str(e)}"

def open_folder(folderpath: str) -> str:
    """Open a folder in File Explorer."""
    try:
        subprocess.Popen(f'explorer "{folderpath}"')
        return f"Opened folder: {folderpath}"
    except Exception as e:
        return f"Failed to open folder: {str(e)}"


# ==================== FILE OPERATIONS ====================

def create_file(filepath: str, content: str = "") -> str:
    """Create a new file with optional content."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Created file: {filepath}"
    except Exception as e:
        return f"Failed to create file: {str(e)}"

def read_file(filepath: str) -> str:
    """Read content from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Failed to read file: {str(e)}"

def append_to_file(filepath: str, content: str) -> str:
    """Append content to a file."""
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content)
        return f"Appended to file: {filepath}"
    except Exception as e:
        return f"Failed to append to file: {str(e)}"

def delete_file(filepath: str) -> str:
    """Delete a file."""
    try:
        os.remove(filepath)
        return f"Deleted file: {filepath}"
    except Exception as e:
        return f"Failed to delete file: {str(e)}"

def create_folder(folderpath: str) -> str:
    """Create a new folder."""
    try:
        os.makedirs(folderpath, exist_ok=True)
        return f"Created folder: {folderpath}"
    except Exception as e:
        return f"Failed to create folder: {str(e)}"

def list_files(folderpath: str) -> List[str]:
    """List files in a folder."""
    try:
        return os.listdir(folderpath)
    except Exception as e:
        return []


# ==================== UI AUTOMATION (Advanced) ====================

def interact_with_app(app_title: str, action: str, control_title: str = None, control_type: str = None) -> str:
    """
    Interact with a specific application's UI elements.
    Actions: click, type, select, check, etc.
    """
    if not HAS_PYWINAUTO:
        return "pywinauto not available for advanced UI automation"
    
    try:
        app = Application(backend='uia').connect(title_re=f".*{app_title}.*")
        window = app.top_window()
        
        if control_title:
            # Find control by title
            control = window.child_window(title=control_title, control_type=control_type)
        else:
            control = window
        
        if action == "click":
            control.click()
            return f"Clicked on '{control_title}' in {app_title}"
        elif action == "type":
            control.type_keys(control_title, with_spaces=True)
            return f"Typed in {app_title}"
        elif action == "focus":
            control.set_focus()
            return f"Focused '{control_title}' in {app_title}"
        else:
            return f"Unknown action: {action}"
            
    except Exception as e:
        return f"UI automation failed: {str(e)}"

def get_ui_elements(app_title: str) -> str:
    """Get all UI elements of an application (for debugging)."""
    if not HAS_PYWINAUTO:
        return "pywinauto not available"
    
    try:
        app = Application(backend='uia').connect(title_re=f".*{app_title}.*")
        window = app.top_window()
        return window.print_control_identifiers(depth=2)
    except Exception as e:
        return f"Failed to get UI elements: {str(e)}"


# ==================== WAIT FUNCTIONS ====================

def wait(seconds: float) -> str:
    """Wait for specified seconds."""
    time.sleep(seconds)
    return f"Waited {seconds} seconds"

def wait_for_window(title_contains: str, timeout: int = 30) -> str:
    """Wait for a window to appear."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if HAS_PYGETWINDOW:
            windows = gw.getWindowsWithTitle(title_contains)
            if windows:
                return f"Window '{title_contains}' appeared"
        time.sleep(0.5)
    return f"Timeout waiting for window: {title_contains}"


# ==================== NOTIFICATION/ALERT ====================

def show_alert(title: str, message: str) -> str:
    """Show a Windows message box."""
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)  # 0x40 = MB_ICONINFORMATION
        return f"Showed alert: {title}"
    except Exception as e:
        return f"Alert failed: {str(e)}"


# ==================== CONVENIENCE FUNCTIONS ====================

def search_start_menu(query: str) -> str:
    """Open Start menu and search."""
    try:
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.write(query, interval=0.05)
        return f"Searched Start menu for: {query}"
    except Exception as e:
        return f"Start menu search failed: {str(e)}"

def open_settings() -> str:
    """Open Windows Settings."""
    return hotkey('win', 'i')

def open_action_center() -> str:
    """Open Windows Action Center."""
    return hotkey('win', 'a')

def switch_virtual_desktop_left() -> str:
    """Switch to virtual desktop on the left."""
    return hotkey('ctrl', 'win', 'left')

def switch_virtual_desktop_right() -> str:
    """Switch to virtual desktop on the right."""
    return hotkey('ctrl', 'win', 'right')

def create_virtual_desktop() -> str:
    """Create a new virtual desktop."""
    return hotkey('ctrl', 'win', 'd')

def close_virtual_desktop() -> str:
    """Close current virtual desktop."""
    return hotkey('ctrl', 'win', 'f4')

def task_view() -> str:
    """Open Task View (virtual desktop overview)."""
    return hotkey('win', 'tab')


# ==================== MAIN INTERFACE FUNCTION ====================

def execute_windows_command(command: str, **params) -> str:
    """
    Main interface to execute Windows commands.
    This function maps command names to their implementations.
    """
    commands = {
        # Mouse
        "click": lambda: mouse_click(params.get('x'), params.get('y'), params.get('button', 'left'), params.get('clicks', 1)),
        "double_click": lambda: mouse_double_click(params.get('x'), params.get('y')),
        "right_click": lambda: mouse_right_click(params.get('x'), params.get('y')),
        "move_mouse": lambda: mouse_move(params.get('x', 0), params.get('y', 0)),
        "drag": lambda: mouse_drag(params.get('start_x', 0), params.get('start_y', 0), params.get('end_x', 0), params.get('end_y', 0)),
        "scroll": lambda: mouse_scroll(params.get('clicks', 3), params.get('x'), params.get('y')),
        "scroll_up": lambda: mouse_scroll(3),
        "scroll_down": lambda: mouse_scroll(-3),
        
        # Keyboard
        "type": lambda: type_text_instant(params.get('text', '')),
        "press": lambda: press_key(params.get('key', 'enter')),
        "hotkey": lambda: hotkey(*params.get('keys', [])),
        "copy": copy,
        "paste": paste,
        "cut": cut,
        "undo": undo,
        "redo": redo,
        "select_all": select_all,
        "save": save,
        "find": find,
        "new_tab": new_tab,
        "close_tab": close_tab,
        "switch_window": switch_window,
        "close_window": close_window,
        "screenshot": screenshot,
        
        # Window management
        "focus": lambda: focus_window(params.get('window', '')),
        "minimize": lambda: minimize_window(params.get('window')),
        "maximize": lambda: maximize_window(params.get('window')),
        "restore": lambda: restore_window(params.get('window', '')),
        "snap_left": snap_window_left,
        "snap_right": snap_window_right,
        
        # System
        "open_url": lambda: open_url(params.get('url', '')),
        "open_file": lambda: open_file(params.get('path', '')),
        "open_folder": lambda: open_folder(params.get('path', '')),
        "run_command": lambda: run_command(params.get('cmd', '')),
        "search_start": lambda: search_start_menu(params.get('query', '')),
        "open_settings": open_settings,
        "task_manager": open_task_manager,
        "file_explorer": open_file_explorer,
        "minimize_all": minimize_all,
        "lock": lock_screen,
        
        # Wait
        "wait": lambda: wait(params.get('seconds', 1)),
    }
    
    if command in commands:
        return commands[command]()
    else:
        return f"Unknown command: {command}"


# Export commonly used functions
__all__ = [
    # Mouse
    'mouse_click', 'mouse_double_click', 'mouse_right_click', 'mouse_move', 
    'mouse_drag', 'mouse_scroll', 'get_mouse_position', 'get_screen_size',
    
    # Keyboard
    'type_text', 'type_text_instant', 'press_key', 'hotkey', 'hold_key',
    'copy', 'paste', 'cut', 'undo', 'redo', 'select_all', 'save', 'find',
    'new_tab', 'close_tab', 'switch_window', 'close_window',
    
    # Window
    'get_all_windows', 'find_window', 'focus_window', 'minimize_window',
    'maximize_window', 'restore_window', 'move_window', 'resize_window',
    'snap_window_left', 'snap_window_right',
    
    # Clipboard
    'get_clipboard', 'set_clipboard',
    
    # Screen
    'take_screenshot', 'locate_on_screen', 'click_image',
    
    # System
    'run_command', 'run_program', 'run_powershell', 'open_url', 'open_file', 
    'open_folder', 'open_task_manager', 'open_run_dialog', 'open_file_explorer',
    'minimize_all', 'lock_screen', 'open_settings',
    
    # File
    'create_file', 'read_file', 'append_to_file', 'delete_file', 
    'create_folder', 'list_files',
    
    # UI
    'interact_with_app', 'get_ui_elements',
    
    # Wait
    'wait', 'wait_for_window',
    
    # Alert
    'show_alert',
    
    # Convenience
    'search_start_menu', 'task_view', 'create_virtual_desktop',
    
    # Main interface
    'execute_windows_command'
]
