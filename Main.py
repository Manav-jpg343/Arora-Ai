"""
Main.py - Aura OS Multi-Agent Orchestrator

Architecture:
  Listener  -->  Strategist  -->  Executor  -->  Overseer
  (Ears)         (Brain)          (Hand)         (Quality Control)

The Listener captures input (voice/text), the Strategist creates
an execution plan, the Executor runs it, and the Overseer validates
results and triggers self-correction if needed.
"""

import threading
import asyncio
import os
import sys
import time
import traceback
from dotenv import dotenv_values

# Adjust Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Backend.Listener import Listener
from Backend.Strategist import Strategist
from Backend.Executor import Executor
from Backend.Overseer import Overseer
from Backend.ContextMemory import memory
from Backend.TextToSpeech import TextToSpeech
from Frontend.GUI import SetAssistantStatus, GetMicrophoneStatus, SetMicrophoneStatus

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Edith")

current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"


def MainExecution():
    """
    Main orchestration loop.
    Wires: Listener -> Strategist -> Executor -> Overseer -> Response
    """
    # Initialize all agents
    listener = Listener()
    strategist = Strategist()
    executor = Executor()
    overseer = Overseer()

    SetAssistantStatus("Idle")
    print(f"[{Assistantname}] Multi-Agent System initialized.")
    print(f"[{Assistantname}] Agents: Listener, Strategist, Executor, Overseer")
    print(f"[{Assistantname}] Waiting for input...")

    while True:
        try:
            # ──── STAGE 1: LISTENER ────
            input_data = listener.listen()

            if input_data is None:
                time.sleep(0.3)  # No input, briefly wait
                continue

            query = input_data["query"]
            if not query:
                continue

            source = input_data["source"]
            print(f"\n[Listener] Input received ({source}): \"{query}\"")

            # Record in memory
            memory.add_user_message(query)

            # ──── STAGE 2: STRATEGIST ────
            SetAssistantStatus("Thinking...")
            plan = strategist.create_plan(query, input_data)

            intent = plan.get("intent", "unknown")
            steps = plan.get("steps", [])
            reasoning = plan.get("reasoning", "")
            print(f"[Strategist] Intent: {intent}")
            print(f"[Strategist] Reasoning: {reasoning}")
            print(f"[Strategist] Plan: {len(steps)} steps")
            for step in steps:
                print(f"  Step {step['id']}: [{step['action']}] {step.get('description', '')}")

            # Check for exit
            if any(s["action"] == "exit" for s in steps):
                SetAssistantStatus("Goodbye!")
                response = "Goodbye! Have a great day."
                TextToSpeech(response)
                memory.add_assistant_message(response)
                break

            # ──── STAGE 3: EXECUTOR ────
            SetAssistantStatus("Executing...")

            # Run the async executor in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                execution_result = loop.run_until_complete(
                    executor.execute_plan(plan, status_callback=SetAssistantStatus)
                )
            finally:
                loop.close()

            print(f"[Executor] Success: {execution_result['success']}")

            # ──── STAGE 4: OVERSEER ────
            SetAssistantStatus("Validating...")

            # Overseer validates and self-corrects if needed
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                final_result = loop.run_until_complete(
                    overseer.validate_and_correct(
                        plan, execution_result, strategist, executor,
                        status_callback=SetAssistantStatus
                    )
                )
            finally:
                loop.close()

            # ──── STAGE 5: RESPONSE ────
            response = final_result.get("response", "").strip()

            if response:
                print(f"[{Assistantname}] Response: {response[:100]}{'...' if len(response) > 100 else ''}")
                memory.add_assistant_message(response)

                SetAssistantStatus("Speaking...")
                TextToSpeech(response)

            if not final_result["success"]:
                print(f"[Overseer] Plan completed with errors")
                failed = final_result.get("failed_step", {})
                if failed:
                    print(f"[Overseer] Failed step: {failed.get('description', 'unknown')}")

            SetAssistantStatus("Idle")

        except Exception as e:
            print(f"[Orchestrator] Error: {e}")
            traceback.print_exc()
            memory.log_event("error", str(e))
            SetAssistantStatus("Error - Recovering...")
            time.sleep(1)
            SetAssistantStatus("Idle")


if __name__ == "__main__":
    def run_gui():
        from Frontend.GUI import GuiApp
        GuiApp()

    # Start Main Orchestration in a background thread
    exe_thread = threading.Thread(target=MainExecution, daemon=True)
    exe_thread.start()

    # GUI must run on main thread
    run_gui()

