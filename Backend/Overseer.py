"""
Overseer.py - The Overseer Agent

The quality control and self-correction agent. Validates results from
the Executor, triggers re-planning when steps fail, and ensures the
user gets a proper response.

Responsibilities:
- Validate Executor results
- Trigger Strategist re-planning on failure (self-correction loop)
- Decide whether to retry, skip, or report failures
- Ensure response quality before sending to user
- Track error patterns for learning
"""

import datetime
from dotenv import dotenv_values
from Backend.ContextMemory import memory

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Edith")

MAX_RETRIES = 2  # Maximum re-plan attempts


class Overseer:
    """
    The Overseer agent. Validates execution results and triggers
    self-correction when things go wrong.
    """

    def __init__(self):
        self.error_log = []  # Track errors for pattern detection
        self.retry_count = 0  # Current retry count for active plan

    async def validate_and_correct(self, plan: dict, execution_result: dict,
                                    strategist, executor, status_callback=None) -> dict:
        """
        Validate execution results. If a step failed, attempt self-correction.

        Args:
            plan: The original plan from Strategist
            execution_result: The result dict from Executor.execute_plan()
            strategist: Strategist instance for re-planning
            executor: Executor instance for re-execution
            status_callback: Optional function to update GUI status

        Returns:
            Final result dict with corrected output if applicable.
        """
        def set_status(msg):
            if status_callback:
                status_callback(msg)

        # If plan succeeded, just return
        if execution_result["success"]:
            self.retry_count = 0
            return execution_result

        # Plan had a failure
        failed_step = execution_result.get("failed_step")
        if not failed_step:
            self.retry_count = 0
            return execution_result

        # Log the error
        error_info = {
            "step": failed_step,
            "error": self._get_step_error(execution_result, failed_step),
            "plan_intent": plan.get("intent", ""),
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.error_log.append(error_info)
        memory.log_event("error", f"Step failed: {failed_step.get('description', 'unknown')}")

        # Check if we should retry
        if self.retry_count >= MAX_RETRIES:
            set_status("Max retries reached")
            self.retry_count = 0
            return self._build_failure_response(execution_result, failed_step)

        # ──── SELF-CORRECTION LOOP ────
        self.retry_count += 1
        set_status(f"Self-correcting (attempt {self.retry_count}/{MAX_RETRIES})...")

        error_message = self._get_step_error(execution_result, failed_step)

        # Ask Strategist for a revised plan
        new_plan = strategist.replan_after_failure(
            original_plan=plan,
            failed_step=failed_step,
            error=error_message
        )

        if new_plan and new_plan.get("steps"):
            set_status("Executing corrected plan...")
            print(f"[Overseer] Re-plan created with {len(new_plan['steps'])} steps")

            # Execute the revised plan
            new_result = await executor.execute_plan(new_plan, status_callback)

            # Recursively validate (up to MAX_RETRIES)
            return await self.validate_and_correct(
                new_plan, new_result, strategist, executor, status_callback
            )

        # Re-planning failed - return partial results
        self.retry_count = 0
        return self._build_failure_response(execution_result, failed_step)

    def _get_step_error(self, execution_result: dict, failed_step: dict) -> str:
        """Extract error message for a failed step."""
        results = execution_result.get("results", {})
        step_id = failed_step.get("id")
        if step_id in results:
            return results[step_id].get("error", "Unknown error")
        return "Step not found in results"

    def _build_failure_response(self, execution_result: dict, failed_step: dict) -> dict:
        """Build a user-friendly failure response."""
        error = self._get_step_error(execution_result, failed_step)
        step_desc = failed_step.get("description", failed_step.get("action", "unknown"))

        # Combine any successful responses with failure notification
        partial_response = execution_result.get("response", "")
        failure_msg = f"I wasn't able to complete '{step_desc}'. "

        if "not found" in error.lower() or "not running" in error.lower():
            failure_msg += "The application might not be installed. "
        elif "timeout" in error.lower():
            failure_msg += "The operation timed out. "
        elif "permission" in error.lower():
            failure_msg += "I don't have permission for that. "
        else:
            failure_msg += "Let me know if you'd like me to try a different approach. "

        response = f"{partial_response} {failure_msg}".strip() if partial_response else failure_msg.strip()

        return {
            "success": False,
            "results": execution_result.get("results", {}),
            "response": response,
            "failed_step": failed_step
        }

    def get_error_summary(self) -> str:
        """Get a summary of recent errors for debugging."""
        if not self.error_log:
            return "No errors logged."

        recent = self.error_log[-5:]
        lines = ["Recent errors:"]
        for err in recent:
            step = err["step"]
            lines.append(f"  - {step.get('description', 'unknown')}: {err['error']}")
        return "\n".join(lines)

    def clear_error_log(self):
        """Clear the error log."""
        self.error_log.clear()
        self.retry_count = 0
