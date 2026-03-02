"""
Listener.py - The Listener Agent

Responsible for:
- Capturing user input (voice or text)
- Wake-word detection ("Hey Edith" / "Hey Aura")
- Passing raw input to the Strategist
- Privacy-first: all speech processing stays local where possible
"""

import os
import time
import threading
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Edith")
WakeWord = env_vars.get("WakeWord", f"hey {Assistantname}").lower()

current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"


class Listener:
    """
    The Listener Agent - ears of the system.
    Monitors for user input via text (GUI) or voice (Speech Recognition).
    Supports optional wake-word activation.
    """

    def __init__(self):
        self.is_listening = False
        self.wake_word = WakeWord
        self.wake_word_enabled = True  # Can be toggled off for always-on mode
        self._speech_recognizer = None

    def get_text_input(self) -> str:
        """Check for text input from the GUI."""
        try:
            query_path = rf'{TempDirPath}\Query.data'
            with open(query_path, "r", encoding='utf-8') as f:
                query = f.read().strip()
            if query:
                # Clear the query file
                with open(query_path, "w", encoding='utf-8') as f:
                    f.write("")
                return query
        except FileNotFoundError:
            pass
        return ""

    def get_mic_status(self) -> bool:
        """Check if mic button was pressed in GUI."""
        try:
            with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as f:
                return f.read().strip() == "True"
        except FileNotFoundError:
            return False

    def set_mic_status(self, status: bool):
        """Set mic status."""
        with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as f:
            f.write(str(status))

    def get_voice_input(self) -> str:
        """
        Capture voice input using Speech Recognition.
        Uses the existing SpeechToText module.
        """
        try:
            from Backend.SpeechToText import SpeechRecognition
            self.is_listening = True
            result = SpeechRecognition()
            self.is_listening = False
            return result if result else ""
        except Exception as e:
            self.is_listening = False
            print(f"[Listener] Voice input error: {e}")
            return ""

    def check_wake_word(self, text: str) -> tuple[bool, str]:
        """
        Check if the input starts with the wake word.
        Returns (is_wake_word_detected, cleaned_query).
        """
        text_lower = text.lower().strip()

        # Check for wake word variations
        wake_words = [
            self.wake_word,
            f"hey {Assistantname.lower()}",
            f"ok {Assistantname.lower()}",
            f"hi {Assistantname.lower()}",
            Assistantname.lower(),
        ]

        for ww in wake_words:
            if text_lower.startswith(ww):
                # Remove wake word and return the rest
                cleaned = text_lower[len(ww):].strip().strip(",").strip()
                if cleaned:
                    return True, cleaned
                else:
                    # Just the wake word, await further input
                    return True, ""

        return False, text

    def listen(self) -> dict:
        """
        Main listen cycle. Returns a dict with:
        {
            "source": "text" | "voice",
            "raw_input": str,
            "query": str,          # cleaned query after wake word removal
            "wake_word": bool,     # whether wake word was detected
            "timestamp": float
        }
        """
        # Priority 1: Check for text input from GUI
        text_input = self.get_text_input()
        if text_input:
            wake_detected, cleaned = self.check_wake_word(text_input)
            return {
                "source": "text",
                "raw_input": text_input,
                "query": cleaned if cleaned else text_input,
                "wake_word": wake_detected,
                "timestamp": time.time()
            }

        # Priority 2: Check if mic was activated
        if self.get_mic_status():
            from Frontend.GUI import SetAssistantStatus
            SetAssistantStatus("Listening...")

            voice_input = self.get_voice_input()
            self.set_mic_status(False)

            if voice_input:
                wake_detected, cleaned = self.check_wake_word(voice_input)
                return {
                    "source": "voice",
                    "raw_input": voice_input,
                    "query": cleaned if cleaned else voice_input,
                    "wake_word": wake_detected,
                    "timestamp": time.time()
                }

        return None  # No input available
