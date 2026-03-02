# Project Edith AI (Arora-Ai)

Welcome to **Project Edith AI**, a powerful Multi-Agent Orchestrator designed to act as an intelligent voice assistant. 

## 🧠 Architecture

The system is built on a robust multi-agent architecture designed to process input, plan actions, execute tasks, and validate results.

*   **Listener (Ears):** Captures multi-modal input (voice/text) from the user.
*   **Strategist (Brain):** Analyzes the input and creates an execution plan, determining the intent and required steps.
*   **Executor (Hand):** Runs the plan asynchronously to interact with APIs, local systems, or perform automated tasks.
*   **Overseer (Quality Control):** Validates the results from the Executor and triggers self-correction if necessary before the final response is delivered.

## 🚀 Getting Started

### Prerequisites
* Python 3.12+
* API Keys for required services (e.g., Groq, HuggingFace, default `.env` configuration)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Abhijit1018/Arora-Ai.git
   cd "Arora-Ai"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the environment and install dependencies:**
   *Windows:*
   ```bash
   .\.venv\Scripts\activate
   pip install -r Requirements.txt
   ```
   *Mac/Linux:*
   ```bash
   source .venv/bin/activate
   pip install -r Requirements.txt
   ```

4. **Environment Variables:**
   Provide the necessary keys in a `.env` file at the root of the project.
   *Example:*
   ```env
   Assistantname=Edith
   # Add other required API keys here
   ```

### Running the Assistant
To launch the Artificial Intelligence, run the `Main.py` script:
```bash
python Main.py
```
This will start both the agent orchestration background processes and the graphical user interface.

## 🛠️ Components Overview
*   **Backend:** Contains the core agents (`Listener.py`, `Strategist.py`, `Executor.py`, `Overseer.py`), API integrations, context memory, text-to-speech, and system info tracking.
*   **Frontend:** Houses the PyQt-based Graphical User Interface (`GUI.py`), assets, and configuration files.
*   **Data:** Stores persistent memory, chat logs, and temporary multi-media files.

## 🤝 Contribution
Feel free to open issues or submit pull requests for any improvements or bug fixes!
