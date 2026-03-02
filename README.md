<div align="center">
  <img src="Frontend/Graphics/Edith.png" alt="Edith AI Logo" width="200" height="200">
  <h1>Project Edith AI (Arora-Ai)</h1>
  <p><i>A Powerful Multi-Agent Orchestrator designed to act as an Intelligent Voice Assistant.</i></p>

  [![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
</div>

---

## 🌟 Overview

Edith AI is not just a standard chatbot; it's a sophisticated multi-agent system built to understand, plan, execute, and validate tasks autonomously. By separating concerns into distinct "agents," Edith can handle complex, multi-step queries with high reliability and provide a seamless voice-first experience.

## 🏗️ System Architecture

The core of Edith AI is its multi-agent pipeline. Information flows through four specialized agents, creating a robust feedback loop:

```mermaid
graph TD
    %% Define Styles
    classDef listener fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b,font-weight:bold;
    classDef strategist fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100,font-weight:bold;
    classDef executor fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20,font-weight:bold;
    classDef overseer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c,font-weight:bold;
    classDef memory fill:#fff8e1,stroke:#ffa000,stroke-width:2px,stroke-dasharray: 4 4;
    classDef external fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px;

    %% Nodes
    User([\👤 User Input (Voice/Text)\])

    subgraph Orchestrator [Main Orchestration Loop]
        direction TB
        L[🎧 Listener<br/><i>(The Ears)</i>]:::listener
        S[🧠 Strategist<br/><i>(The Brain)</i>]:::strategist
        E[⚙️ Executor<br/><i>(The Hands)</i>]:::executor
        O[🧐 Overseer<br/><i>(Quality Control)</i>]:::overseer
    end

    Mem[(Context Memory)]:::memory
    
    subgraph Actions [External Actions]
        Web(Web Search):::external
        Sys(System Control):::external
        Gen(Media Gen):::external
    end

    Response([\🔊 Output (Speech/GUI)\])

    %% Connections
    User -->|Transcribed Query| L
    L -->|Passes Input| S
    L -.->|Logs Query| Mem
    Mem -.->|Provides Context| S
    
    S -->|Generates Execution Plan| E
    E -->|Performs Actions| Actions
    E -->|Returns Results| O
    
    O -->|Validates Success| Response
    O -.->|Detects Error & <br> Self-Corrects| S
```

### 🧠 The Agents

1.  **🎧 Listener (The Ears):** Constantly monitors for multi-modal input (voice or text). It transcribes audio reliably and captures the user's intent.
2.  **🧠 Strategist (The Brain):** Takes the raw input and current memory context. It reasons about the goal, determines the intent, and creates a step-by-step execution plan.
3.  **⚙️ Executor (The Hands):** The asynchronous workhorse. It takes the Strategist's plan and performs the necessary actions—searching the web, controlling the system, generating images, etc.
4.  **🧐 Overseer (Quality Control):** Intercepts the Executor's results. It validates if the original goal was met. If something failed, it can intelligently route the task back to the Strategist for self-correction before generating the final response.

---

## 🚀 Getting Started

### Prerequisites

*   Python 3.12 or higher
*   API Keys for the required language models and services (e.g., Groq, HuggingFace).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Abhijit1018/Arora-Ai.git
    cd "Arora-Ai"
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the environment and install dependencies:**
    
    *Windows:*
    ```powershell
    .\.venv\Scripts\activate
    pip install -r Requirements.txt
    ```
    
    *Mac/Linux:*
    ```bash
    source .venv/bin/activate
    pip install -r Requirements.txt
    ```

4.  **Environment Variables:**
    Create a `.env` file in the root directory and add your configurations.
    
    *Example `.env`:*
    ```env
    Assistantname=Edith
    # Add your specific API keys here
    # GROQ_API_KEY=your_key_here
    ```

### ▶️ Running the Assistant

To launch Edith AI, simply run the `Main.py` script. This will initialize the agent Orchestrator and open the Graphical User Interface (GUI).

```bash
python Main.py
```

---

## 📂 Project Structure

*   **`/Backend`:** The brain of the operation. Contains all logic for the agents (`Listener.py`, `Strategist.py`, `Executor.py`, `Overseer.py`), API integrations, context memory, and utilities like Text-To-Speech.
*   **`/Frontend`:** The user-facing layer. Contains the PyQt-based Graphical User Interface (`GUI.py`), styling, SVG graphics, and configuration `.data` files for state management.
*   **`/Data`:** The local storage layer. Keeps track of persistent memory, conversation history (`ChatLog.json`), and temporary media files generated during sessions.

## 🤝 Contributing

We welcome contributions to make Edith AI even better! Feel free to:
*   Open an issue to report bugs or suggest features.
*   Submit a Pull Request with improvements to the agents, new tools for the Executor, or UI enhancements.

## 📄 License
This project is open-source and available under the MIT License.
