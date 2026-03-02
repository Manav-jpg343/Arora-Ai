"""
Executor.py - The Executor (Hand) Agent

Executes the plan produced by the Strategist, step by step.
Each step is mapped to a concrete system function.

Responsibilities:
- Map plan actions to actual system operations
- Execute steps in the correct order (sequential / parallel)
- Handle dependency chains between steps
- Report results and errors back for the Overseer
- Log all actions to ContextMemory
"""

import asyncio
import os
import time
import keyboard
import requests
from AppOpener import open as appopen, close as appclose
from webbrowser import open as webopen
from pywhatkit import search as pywhatkit_search, playonyt
from bs4 import BeautifulSoup
from dotenv import dotenv_values

from Backend.ContextMemory import memory
from Backend.WindowsControl import (
    mouse_click, mouse_double_click, mouse_right_click, mouse_move, mouse_scroll,
    type_text_instant, press_key, hotkey,
    focus_window, minimize_window, maximize_window,
    snap_window_left, snap_window_right,
    take_screenshot, run_command,
    open_url as wc_open_url, open_file as wc_open_file, open_folder as wc_open_folder,
    copy as wc_copy, paste as wc_paste, cut as wc_cut,
    undo as wc_undo, redo as wc_redo, select_all as wc_select_all, save as wc_save,
    new_tab as wc_new_tab, close_tab as wc_close_tab,
    switch_window as wc_switch_window, close_window as wc_close_window,
    wait as wc_wait
)

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Edith")

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# App alias mapping for generic terms
APP_ALIASES = {
    "browser": "chrome", "web browser": "chrome", "internet": "chrome",
    "mail": "outlook", "email": "outlook",
    "music": "spotify", "video": "vlc",
    "text editor": "notepad", "editor": "notepad",
    "terminal": "cmd", "command prompt": "cmd",
}


class StepResult:
    """Result of executing a single step."""

    def __init__(self, step_id: int, success: bool, output: str = "", error: str = ""):
        self.step_id = step_id
        self.success = success
        self.output = output
        self.error = error

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "success": self.success,
            "output": self.output,
            "error": self.error
        }

    def __repr__(self):
        status = "OK" if self.success else "FAIL"
        return f"<StepResult #{self.step_id} {status}: {self.output or self.error}>"


class Executor:
    """
    The Hand agent. Executes plans from the Strategist step by step.
    Reports detailed results for each step.
    """

    def __init__(self):
        # Import heavy modules lazily
        self._chatbot = None
        self._realtime_engine = None

    @property
    def chatbot(self):
        if self._chatbot is None:
            from Backend.Chatbot import ChatBot
            self._chatbot = ChatBot
        return self._chatbot

    @property
    def realtime_engine(self):
        if self._realtime_engine is None:
            from Backend.RealtimeSearchEngine import RealtimeSearchEngine
            self._realtime_engine = RealtimeSearchEngine
        return self._realtime_engine

    async def execute_plan(self, plan: dict, status_callback=None) -> dict:
        """
        Execute a full plan from the Strategist.

        Args:
            plan: The plan dict from Strategist
            status_callback: Optional function to update GUI status

        Returns:
            {
                "success": bool,
                "results": [StepResult, ...],
                "response": str,  # Text response to speak/display
                "failed_step": dict or None
            }
        """
        steps = plan.get("steps", [])
        results = {}
        response_parts = []
        failed_step = None

        def set_status(msg):
            if status_callback:
                status_callback(msg)

        # Group steps: find parallel groups and sequential steps
        execution_order = self._build_execution_order(steps)

        for group in execution_order:
            if len(group) == 1:
                # Sequential execution
                step = group[0]
                set_status(f"Executing: {step.get('description', step['action'])}...")

                result = await self._execute_step(step, results)
                results[step["id"]] = result

                if result.output and step["action"] in ("general", "realtime", "content_write"):
                    response_parts.append(result.output)

                memory.log_event("task_executed", step.get("description", step["action"]))

                if not result.success and step.get("retry", False):
                    # Retry once
                    set_status(f"Retrying: {step.get('description', '')}...")
                    await asyncio.sleep(1)
                    result = await self._execute_step(step, results)
                    results[step["id"]] = result

                if not result.success:
                    failed_step = step
                    memory.log_event("error", f"Step failed: {step.get('description', '')} - {result.error}")
                    # Don't break - let Overseer decide

            else:
                # Parallel execution
                set_status(f"Executing {len(group)} tasks in parallel...")
                tasks = [self._execute_step(step, results) for step in group]
                parallel_results = await asyncio.gather(*tasks, return_exceptions=True)

                for step, result in zip(group, parallel_results):
                    if isinstance(result, Exception):
                        result = StepResult(step["id"], False, error=str(result))
                    results[step["id"]] = result

                    if result.output and step["action"] in ("general", "realtime", "content_write"):
                        response_parts.append(result.output)

                    if not result.success:
                        failed_step = step

        # Build final response
        response = " ".join(response_parts).strip()

        # If no text response was generated but tasks succeeded, create a confirmation
        if not response and not failed_step:
            action_descs = [s.get("description", s["action"]) for s in steps
                           if s["action"] not in ("wait",)]
            if action_descs:
                response = f"Done. {', '.join(action_descs)}."

        return {
            "success": failed_step is None,
            "results": {k: v.to_dict() for k, v in results.items()},
            "response": response,
            "failed_step": failed_step
        }

    def _build_execution_order(self, steps: list) -> list[list[dict]]:
        """
        Build execution order respecting dependencies.
        Groups parallel steps together.
        """
        if not steps:
            return []

        executed = set()
        order = []
        remaining = list(steps)

        while remaining:
            # Find steps whose dependencies are met
            ready = []
            not_ready = []

            for step in remaining:
                deps = step.get("depends_on")
                if deps is None:
                    ready.append(step)
                elif isinstance(deps, list):
                    if all(d in executed for d in deps):
                        ready.append(step)
                    else:
                        not_ready.append(step)
                elif isinstance(deps, int):
                    if deps in executed:
                        ready.append(step)
                    else:
                        not_ready.append(step)
                else:
                    ready.append(step)

            if not ready:
                # Avoid infinite loop - execute remaining sequentially
                for step in remaining:
                    order.append([step])
                    executed.add(step["id"])
                break

            # Group parallel steps
            parallel_group = [s for s in ready if s.get("parallel", False)]
            sequential = [s for s in ready if not s.get("parallel", False)]

            if parallel_group:
                order.append(parallel_group)
                for s in parallel_group:
                    executed.add(s["id"])

            for s in sequential:
                order.append([s])
                executed.add(s["id"])

            remaining = not_ready

        return order

    async def _execute_step(self, step: dict, previous_results: dict) -> StepResult:
        """Execute a single step and return the result."""
        action = step["action"]
        params = step.get("params", {})
        step_id = step["id"]

        try:
            # ───── CONVERSATIONAL ─────
            if action == "general":
                query = params.get("query", "")
                response = await asyncio.to_thread(self.chatbot, query)
                return StepResult(step_id, True, output=response)

            elif action == "realtime":
                query = params.get("query", "")
                response = await asyncio.to_thread(self.realtime_engine, query)
                return StepResult(step_id, True, output=response)

            # ───── APP MANAGEMENT ─────
            elif action == "open_app":
                app = params.get("app", "")
                result = await asyncio.to_thread(self._open_app, app)
                memory.log_event("app_opened", app)
                return StepResult(step_id, True, output=result)

            elif action == "close_app":
                app = params.get("app", "")
                result = await asyncio.to_thread(self._close_app, app)
                memory.log_event("app_closed", app)
                return StepResult(step_id, True, output=result)

            # ───── NAVIGATION ─────
            elif action == "open_url":
                url = params.get("url", "")
                result = await asyncio.to_thread(wc_open_url, url)
                memory.log_event("url_opened", url)
                return StepResult(step_id, True, output=result)

            elif action == "open_file":
                path = params.get("path", params.get("filepath", ""))
                result = await asyncio.to_thread(wc_open_file, path)
                memory.log_event("file_opened", path)
                return StepResult(step_id, True, output=result)

            elif action == "open_folder":
                path = params.get("path", params.get("folderpath", ""))
                result = await asyncio.to_thread(wc_open_folder, path)
                memory.log_event("folder_opened", path)
                return StepResult(step_id, True, output=result)

            # ───── MEDIA ─────
            elif action == "play_media":
                query = params.get("query", "")
                await asyncio.to_thread(playonyt, query)
                return StepResult(step_id, True, output=f"Playing: {query}")

            elif action == "google_search":
                query = params.get("query", "")
                await asyncio.to_thread(pywhatkit_search, query)
                return StepResult(step_id, True, output=f"Searched Google for: {query}")

            elif action == "youtube_search":
                query = params.get("query", "")
                url = f"https://www.youtube.com/results?search_query={query}"
                await asyncio.to_thread(webopen, url)
                return StepResult(step_id, True, output=f"Searched YouTube for: {query}")

            # ───── KEYBOARD ─────
            elif action == "type_text":
                text = params.get("text", "")
                result = await asyncio.to_thread(type_text_instant, text)
                return StepResult(step_id, True, output=result)

            elif action == "press_key":
                key = params.get("key", "enter")
                result = await asyncio.to_thread(press_key, key)
                return StepResult(step_id, True, output=result)

            elif action == "hotkey":
                keys = params.get("keys", [])
                if isinstance(keys, list) and keys:
                    result = await asyncio.to_thread(hotkey, *keys)
                else:
                    result = "No keys specified"
                return StepResult(step_id, True, output=result)

            # ───── MOUSE ─────
            elif action == "click":
                x = params.get("x")
                y = params.get("y")
                result = await asyncio.to_thread(mouse_click, x, y)
                return StepResult(step_id, True, output=result)

            elif action == "right_click":
                x = params.get("x")
                y = params.get("y")
                result = await asyncio.to_thread(mouse_right_click, x, y)
                return StepResult(step_id, True, output=result)

            elif action == "double_click":
                x = params.get("x")
                y = params.get("y")
                result = await asyncio.to_thread(mouse_double_click, x, y)
                return StepResult(step_id, True, output=result)

            elif action == "scroll":
                direction = params.get("direction", "down")
                amount = params.get("amount", 5)
                clicks = amount if direction == "up" else -amount
                result = await asyncio.to_thread(mouse_scroll, clicks)
                return StepResult(step_id, True, output=result)

            elif action == "move_mouse":
                x = params.get("x", 0)
                y = params.get("y", 0)
                result = await asyncio.to_thread(mouse_move, x, y)
                return StepResult(step_id, True, output=result)

            # ───── WINDOW MANAGEMENT ─────
            elif action == "focus_window":
                window = params.get("window", "")
                result = await asyncio.to_thread(focus_window, window)
                memory.log_event("app_opened", window)  # Track focus change
                return StepResult(step_id, True, output=result)

            elif action == "minimize_window":
                window = params.get("window")
                result = await asyncio.to_thread(minimize_window, window)
                return StepResult(step_id, True, output=result)

            elif action == "maximize_window":
                window = params.get("window")
                result = await asyncio.to_thread(maximize_window, window)
                return StepResult(step_id, True, output=result)

            elif action == "snap_window":
                direction = params.get("direction", "left")
                if direction == "left":
                    result = await asyncio.to_thread(snap_window_left)
                else:
                    result = await asyncio.to_thread(snap_window_right)
                return StepResult(step_id, True, output=result)

            elif action == "take_screenshot":
                result = await asyncio.to_thread(take_screenshot)
                return StepResult(step_id, True, output=result)

            # ───── SYSTEM COMMANDS ─────
            elif action == "run_command":
                cmd = params.get("command", params.get("cmd", ""))
                result = await asyncio.to_thread(run_command, cmd)
                return StepResult(step_id, True, output=result)

            elif action == "system_volume":
                vol_action = params.get("action", "")
                key_map = {
                    "mute": "volume mute", "unmute": "volume mute",
                    "up": "volume up", "down": "volume down"
                }
                key = key_map.get(vol_action)
                if key:
                    await asyncio.to_thread(keyboard.press_and_release, key)
                    return StepResult(step_id, True, output=f"Volume: {vol_action}")
                return StepResult(step_id, False, error=f"Unknown volume action: {vol_action}")

            # ───── CLIPBOARD / SHORTCUTS ─────
            elif action == "copy":
                result = await asyncio.to_thread(wc_copy)
                return StepResult(step_id, True, output=result)
            elif action == "paste":
                result = await asyncio.to_thread(wc_paste)
                return StepResult(step_id, True, output=result)
            elif action == "cut":
                result = await asyncio.to_thread(wc_cut)
                return StepResult(step_id, True, output=result)
            elif action == "select_all":
                result = await asyncio.to_thread(wc_select_all)
                return StepResult(step_id, True, output=result)
            elif action == "undo":
                result = await asyncio.to_thread(wc_undo)
                return StepResult(step_id, True, output=result)
            elif action == "redo":
                result = await asyncio.to_thread(wc_redo)
                return StepResult(step_id, True, output=result)
            elif action == "save":
                result = await asyncio.to_thread(wc_save)
                return StepResult(step_id, True, output=result)
            elif action == "new_tab":
                result = await asyncio.to_thread(wc_new_tab)
                return StepResult(step_id, True, output=result)
            elif action == "close_tab":
                result = await asyncio.to_thread(wc_close_tab)
                return StepResult(step_id, True, output=result)
            elif action == "switch_window":
                result = await asyncio.to_thread(wc_switch_window)
                return StepResult(step_id, True, output=result)
            elif action == "close_window":
                result = await asyncio.to_thread(wc_close_window)
                return StepResult(step_id, True, output=result)

            # ───── CONTENT ─────
            elif action == "content_write":
                topic = params.get("topic", "")
                from Backend.Automation import Content
                result = await asyncio.to_thread(Content, topic)
                return StepResult(step_id, True, output=f"Content written for: {topic}")

            elif action == "generate_image":
                prompt = params.get("prompt", "")
                # Trigger image generation via the data file interface
                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write(f"{prompt},True")
                return StepResult(step_id, True, output=f"Generating image: {prompt}")

            # ───── WAIT ─────
            elif action == "wait":
                seconds = float(params.get("seconds", 1))
                await asyncio.sleep(seconds)
                return StepResult(step_id, True, output=f"Waited {seconds}s")

            # ───── EXIT ─────
            elif action == "exit":
                return StepResult(step_id, True, output="Goodbye!")

            else:
                return StepResult(step_id, False, error=f"Unknown action: {action}")

        except Exception as e:
            return StepResult(step_id, False, error=str(e))

    # ───── Helper methods ─────

    def _open_app(self, app: str) -> str:
        """Open an application, with alias resolution and web fallback."""
        app_lower = app.lower().strip()

        # Resolve alias
        if app_lower in APP_ALIASES:
            app = APP_ALIASES[app_lower]

        try:
            appopen(app, match_closest=True, output=True, throw_error=True)
            return f"Opened {app}"
        except Exception:
            # Fallback: try to find and open via Google
            try:
                sess = requests.session()
                url = f"https://www.google.com/search?q={app}"
                headers = {"User-Agent": useragent}
                response = sess.get(url, headers=headers)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = soup.find_all('a', {'jsname': 'UWckNb'})
                    hrefs = [link.get('href') for link in links]
                    if hrefs:
                        webopen(hrefs[0])
                        return f"Opened {app} via web"

                webopen(f"https://www.google.com/search?q={app}")
                return f"Searched for {app}"
            except Exception as e:
                return f"Could not open {app}: {e}"

    def _close_app(self, app: str) -> str:
        """Close an application."""
        if "chrome" in app.lower():
            return "Skipped closing Chrome (in use by system)"
        try:
            appclose(app, match_closest=True, output=True, throw_error=True)
            return f"Closed {app}"
        except Exception:
            return f"Could not close {app}"
