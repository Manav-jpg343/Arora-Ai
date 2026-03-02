"""
Strategist.py - The Strategist (Brain) Agent

This is the CORE intelligence of Aura OS. Unlike a simple keyword router,
the Strategist creates multi-step execution plans with reasoning.

Responsibilities:
- Analyze user intent with context awareness
- Create ordered, multi-step action plans
- Resolve references ("the file I just downloaded", "go back")
- Decide when parallel vs sequential execution is needed
- Feed context from memory into decision making
"""

import json
import datetime
import os
from groq import Groq
from dotenv import dotenv_values
from Backend.ContextMemory import memory

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Edith")

client = Groq(api_key=GroqAPIKey)

# ────────────────── STRATEGIST SYSTEM PROMPT ──────────────────

STRATEGIST_PROMPT = f"""You are the Strategist agent for an AI OS assistant named {Assistantname}. The user is {Username}.

Your job is to analyze the user's query and produce a structured JSON execution plan.
You are NOT answering the query - you are PLANNING how to answer or execute it.

You have access to these action types:
- "general": Chat/conversational response (use for greetings, questions answerable by an LLM, general knowledge)
- "realtime": Requires real-time internet search (current events, live data, people, news)
- "open_app": Open a Windows application (param: app name)
- "close_app": Close an application (param: app name)
- "open_url": Open a URL in browser (param: url)
- "open_file": Open a file (param: filepath)
- "open_folder": Open a folder (param: folderpath)
- "play_media": Play a song/video on YouTube (param: query)
- "google_search": Search Google (param: query)
- "youtube_search": Search YouTube (param: query)
- "type_text": Type text into active window (param: text)
- "press_key": Press a keyboard key (param: key name)
- "hotkey": Press key combination (param: keys as list like ["ctrl","c"])
- "click": Mouse click (param: optional x,y coordinates)
- "right_click": Right mouse click (param: optional x,y)
- "double_click": Double mouse click (param: optional x,y)
- "scroll": Scroll up or down (param: direction "up" or "down", optional amount)
- "move_mouse": Move mouse (param: x,y coordinates)
- "focus_window": Focus/switch to a window (param: window title)
- "minimize_window": Minimize a window (param: optional window title)
- "maximize_window": Maximize a window (param: optional window title)
- "snap_window": Snap window left/right (param: "left" or "right")
- "take_screenshot": Capture screenshot
- "run_command": Run a terminal/shell command (param: command string)
- "copy": Copy (Ctrl+C)
- "paste": Paste (Ctrl+V)
- "cut": Cut (Ctrl+X)
- "select_all": Select all (Ctrl+A)
- "undo": Undo (Ctrl+Z)
- "redo": Redo (Ctrl+Y)
- "save": Save (Ctrl+S)
- "new_tab": Open new tab (Ctrl+T)
- "close_tab": Close tab (Ctrl+W)
- "switch_window": Alt+Tab
- "close_window": Alt+F4
- "system_volume": Change volume (param: "mute", "unmute", "up", "down")
- "content_write": Write content/document (param: topic)
- "generate_image": Generate AI image (param: prompt)
- "wait": Wait before next step (param: seconds as number)
- "exit": End conversation / shutdown

IMPORTANT RULES:
1. Output ONLY valid JSON - no markdown code fences, no explanations outside JSON.
2. For multi-step tasks, order steps sequentially. Steps execute in order.
3. Use "depends_on" to mark steps that need a previous step to complete.
4. Use context information to resolve references like "that file", "go back", etc.
5. If a step might fail, mark "retry": true so the Overseer can retry it.
6. For conversational queries, use a single "general" step.
7. Set "parallel": true for steps that can run simultaneously.

OUTPUT FORMAT (strict JSON):
{{
  "intent": "Brief description of what user wants",
  "reasoning": "Your analysis of why you chose these steps",
  "steps": [
    {{
      "id": 1,
      "action": "action_type",
      "params": {{}},
      "description": "What this step does",
      "depends_on": null,
      "retry": false,
      "parallel": false
    }}
  ]
}}

EXAMPLES:

User: "open chrome and search for python tutorials"
{{
  "intent": "Open Chrome browser and search for python tutorials",
  "reasoning": "Need to first open Chrome, wait for it to load, then navigate and search",
  "steps": [
    {{"id": 1, "action": "open_app", "params": {{"app": "chrome"}}, "description": "Open Chrome browser", "depends_on": null, "retry": true, "parallel": false}},
    {{"id": 2, "action": "wait", "params": {{"seconds": 2}}, "description": "Wait for Chrome to load", "depends_on": 1, "retry": false, "parallel": false}},
    {{"id": 3, "action": "open_url", "params": {{"url": "https://www.google.com"}}, "description": "Navigate to Google", "depends_on": 2, "retry": true, "parallel": false}},
    {{"id": 4, "action": "wait", "params": {{"seconds": 1}}, "description": "Wait for page load", "depends_on": 3, "retry": false, "parallel": false}},
    {{"id": 5, "action": "type_text", "params": {{"text": "python tutorials"}}, "description": "Type search query", "depends_on": 4, "retry": false, "parallel": false}},
    {{"id": 6, "action": "press_key", "params": {{"key": "enter"}}, "description": "Press Enter to search", "depends_on": 5, "retry": false, "parallel": false}}
  ]
}}

User: "what's the weather today?"
{{
  "intent": "Get current weather information",
  "reasoning": "This requires real-time data that an LLM doesn't have",
  "steps": [
    {{"id": 1, "action": "realtime", "params": {{"query": "what's the weather today?"}}, "description": "Search for current weather", "depends_on": null, "retry": true, "parallel": false}}
  ]
}}

User: "open notepad and vs code side by side"
{{
  "intent": "Open Notepad and VS Code snapped to left and right",
  "reasoning": "Open both apps then snap them to left and right halves of screen",
  "steps": [
    {{"id": 1, "action": "open_app", "params": {{"app": "notepad"}}, "description": "Open Notepad", "depends_on": null, "retry": true, "parallel": true}},
    {{"id": 2, "action": "open_app", "params": {{"app": "vs code"}}, "description": "Open VS Code", "depends_on": null, "retry": true, "parallel": true}},
    {{"id": 3, "action": "wait", "params": {{"seconds": 2}}, "description": "Wait for apps to load", "depends_on": [1,2], "retry": false, "parallel": false}},
    {{"id": 4, "action": "focus_window", "params": {{"window": "Notepad"}}, "description": "Focus Notepad", "depends_on": 3, "retry": false, "parallel": false}},
    {{"id": 5, "action": "snap_window", "params": {{"direction": "left"}}, "description": "Snap Notepad left", "depends_on": 4, "retry": false, "parallel": false}},
    {{"id": 6, "action": "focus_window", "params": {{"window": "Visual Studio Code"}}, "description": "Focus VS Code", "depends_on": 5, "retry": false, "parallel": false}},
    {{"id": 7, "action": "snap_window", "params": {{"direction": "right"}}, "description": "Snap VS Code right", "depends_on": 6, "retry": false, "parallel": false}}
  ]
}}

User: "thanks, that's all"
{{
  "intent": "User ending conversation",
  "reasoning": "User is saying goodbye",
  "steps": [
    {{"id": 1, "action": "general", "params": {{"query": "thanks, that's all"}}, "description": "Respond to farewell", "depends_on": null, "retry": false, "parallel": false}}
  ]
}}
"""

# ────────────────── FEW-SHOT EXAMPLES ──────────────────

STRATEGIST_EXAMPLES = [
    {"role": "user", "content": "how are you?"},
    {"role": "assistant", "content": '{"intent": "Greeting/conversation", "reasoning": "Simple conversational query", "steps": [{"id": 1, "action": "general", "params": {"query": "how are you?"}, "description": "Respond conversationally", "depends_on": null, "retry": false, "parallel": false}]}'},
    {"role": "user", "content": "who is the current president of USA?"},
    {"role": "assistant", "content": '{"intent": "Get current US president", "reasoning": "Requires real-time information", "steps": [{"id": 1, "action": "realtime", "params": {"query": "who is the current president of USA?"}, "description": "Search for current US president", "depends_on": null, "retry": true, "parallel": false}]}'},
    {"role": "user", "content": "open spotify and play some music, also mute the system first"},
    {"role": "assistant", "content": '{"intent": "Mute system, open Spotify, play music", "reasoning": "First mute system volume, then open Spotify, then play music", "steps": [{"id": 1, "action": "system_volume", "params": {"action": "mute"}, "description": "Mute system volume", "depends_on": null, "retry": false, "parallel": false}, {"id": 2, "action": "open_app", "params": {"app": "spotify"}, "description": "Open Spotify", "depends_on": 1, "retry": true, "parallel": false}, {"id": 3, "action": "wait", "params": {"seconds": 2}, "description": "Wait for Spotify to load", "depends_on": 2, "retry": false, "parallel": false}, {"id": 4, "action": "play_media", "params": {"query": "play some music"}, "description": "Play music", "depends_on": 3, "retry": true, "parallel": false}]}'},
]


# ────────────────── STRATEGIST CLASS ──────────────────

class Strategist:
    """
    The Brain agent. Analyzes user intent with full context awareness
    and produces structured multi-step execution plans.
    """

    def __init__(self):
        self.client = client
        self.plan_history = []  # Track recent plans for learning

    def create_plan(self, query: str, input_metadata: dict = None) -> dict:
        """
        Analyze the user query and create an execution plan.

        Args:
            query: The user's cleaned query
            input_metadata: Additional context from the Listener (source, wake_word, etc.)

        Returns:
            A structured plan dict with intent, reasoning, and steps.
        """
        # Build context-aware prompt
        context = memory.get_context_summary()
        conversation_context = memory.get_conversation_context(last_n=6)

        # Build messages for the LLM
        messages = [{"role": "system", "content": STRATEGIST_PROMPT}]

        # Add few-shot examples
        messages.extend(STRATEGIST_EXAMPLES)

        # Add context
        messages.append({
            "role": "system",
            "content": f"CURRENT CONTEXT:\n{context}"
        })

        # Add recent conversation for continuity
        if conversation_context:
            conv_text = "\n".join([
                f"{'User' if m['role'] == 'user' else Assistantname}: {m['content']}"
                for m in conversation_context[-4:]
            ])
            messages.append({
                "role": "system",
                "content": f"RECENT CONVERSATION:\n{conv_text}"
            })

        # Add the current user query
        messages.append({"role": "user", "content": query})

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=2048,
                temperature=0.3,  # Lower temperature for more deterministic plans
                top_p=1,
                stream=False,
                stop=None
            )

            response_text = completion.choices[0].message.content.strip()

            # Parse the JSON response
            plan = self._parse_plan(response_text)

            if plan:
                self.plan_history.append({
                    "query": query,
                    "plan": plan,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                # Keep only last 20 plans
                self.plan_history = self.plan_history[-20:]
                return plan

        except Exception as e:
            print(f"[Strategist] Error creating plan: {e}")

        # Fallback: treat as general query
        return {
            "intent": "Fallback - treat as general query",
            "reasoning": "Could not parse a structured plan, falling back to general chat",
            "steps": [{
                "id": 1,
                "action": "general",
                "params": {"query": query},
                "description": "Respond as general conversation",
                "depends_on": None,
                "retry": False,
                "parallel": False
            }]
        }

    def _parse_plan(self, response_text: str) -> dict:
        """Parse the LLM response into a valid plan dict."""
        # Try direct JSON parse
        try:
            # Strip markdown code fences if present
            text = response_text.strip()
            if text.startswith("```"):
                # Remove code fences
                lines = text.split("\n")
                text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
                text = text.strip()

            plan = json.loads(text)

            # Validate structure
            if "steps" in plan and isinstance(plan["steps"], list):
                # Ensure each step has required fields
                for step in plan["steps"]:
                    step.setdefault("id", plan["steps"].index(step) + 1)
                    step.setdefault("depends_on", None)
                    step.setdefault("retry", False)
                    step.setdefault("parallel", False)
                    step.setdefault("description", "")
                    step.setdefault("params", {})
                return plan

        except json.JSONDecodeError:
            pass

        # Try to find JSON in the response
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                plan = json.loads(json_str)
                if "steps" in plan:
                    return plan
        except (json.JSONDecodeError, ValueError):
            pass

        return None

    def replan_after_failure(self, original_plan: dict, failed_step: dict, error: str) -> dict:
        """
        Create a revised plan after a step failure.
        Called by the Overseer to implement self-correction.
        """
        messages = [
            {"role": "system", "content": STRATEGIST_PROMPT},
            {"role": "system", "content": f"""
A previous execution plan failed. Create a REVISED plan.

ORIGINAL PLAN:
{json.dumps(original_plan, indent=2)}

FAILED STEP:
{json.dumps(failed_step, indent=2)}

ERROR:
{error}

Create a new plan that works around this failure. You might:
- Try an alternative approach
- Skip the failed step if non-critical
- Add corrective steps before retrying
"""},
            {"role": "user", "content": f"Fix the plan that failed at step: {failed_step.get('description', 'unknown')}"}
        ]

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=2048,
                temperature=0.3,
                stream=False
            )

            response = completion.choices[0].message.content.strip()
            plan = self._parse_plan(response)
            if plan:
                return plan

        except Exception as e:
            print(f"[Strategist] Replan error: {e}")

        return None
