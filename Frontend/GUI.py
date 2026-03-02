from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame, QSizePolicy
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize
from dotenv import dotenv_values
import sys
import os
import json

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Edith")
current_dir = os.getcwd()

TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"
DataDirPath = rf"{current_dir}\Data"

# Ensure directories exist
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(DataDirPath, exist_ok=True)

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    try:
        with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        return "False"

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Idle"

def SetQuery(query):
    with open(rf'{TempDirPath}\Query.data', "w", encoding='utf-8') as file:
        file.write(query)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{Assistantname} AI Assistant")
        self.setGeometry(100, 100, 800, 650)
        self.setStyleSheet("background-color: #1a1a2e; color: white;")
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header with agent pipeline status
        header_layout = QHBoxLayout()
        self.title_label = QLabel(f"{Assistantname} AI")
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(self.title_label)
        
        self.status_label = QLabel("Idle")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("color: #00d2ff;")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(self.status_label)
        main_layout.addLayout(header_layout)

        # Agent Pipeline Indicator
        pipeline_layout = QHBoxLayout()
        pipeline_layout.setSpacing(4)
        
        self.agent_labels = {}
        agents = [
            ("Listener", "#4CAF50"),
            ("Strategist", "#FF9800"),
            ("Executor", "#2196F3"),
            ("Overseer", "#9C27B0"),
        ]
        for name, color in agents:
            lbl = QLabel(f" {name} ")
            lbl.setFont(QFont("Arial", 9))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"""
                QLabel {{
                    background-color: #2a2a3e;
                    color: #666;
                    border-radius: 8px;
                    padding: 3px 8px;
                    border: 1px solid #333;
                }}
            """)
            lbl.setFixedHeight(24)
            pipeline_layout.addWidget(lbl)
            self.agent_labels[name] = (lbl, color)
            
            # Arrow between agents (except last)
            if name != "Overseer":
                arrow = QLabel(" → ")
                arrow.setFont(QFont("Arial", 10))
                arrow.setStyleSheet("color: #444;")
                arrow.setFixedWidth(25)
                arrow.setAlignment(Qt.AlignCenter)
                pipeline_layout.addWidget(arrow)

        pipeline_layout.addStretch()
        main_layout.addLayout(pipeline_layout)

        # Chat Area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #16213e;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        main_layout.addWidget(self.chat_area)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #0f3460;
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #e94560;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        # Send Button 
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                border-radius: 15px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5c77;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)

        # Mic Button
        self.mic_btn = QPushButton()
        self.mic_icon_off = QIcon(rf'{GraphicsDirPath}\Mic_off.svg')
        self.mic_icon_on = QIcon(rf'{GraphicsDirPath}\Mic_on.svg')
        self.mic_btn.setIcon(self.mic_icon_off)
        self.mic_btn.setIconSize(QSize(24, 24))
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
        """)
        self.mic_btn.clicked.connect(self.toggle_mic)
        input_layout.addWidget(self.mic_btn)

        main_layout.addLayout(input_layout)

        # Timers
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(500)

        self.chat_timer = QTimer()
        self.chat_timer.timeout.connect(self.update_chat)
        self.chat_timer.start(1000)

        self.last_chat_length = 0
        self.is_mic_active = False

    def send_message(self):
        text = self.input_field.text().strip()
        if text:
            SetQuery(text)
            self.input_field.clear()

    def toggle_mic(self):
        if not self.is_mic_active:
            SetMicrophoneStatus("True")
            self.mic_btn.setIcon(self.mic_icon_on)
            self.is_mic_active = True
        else:
            SetMicrophoneStatus("False")
            self.mic_btn.setIcon(self.mic_icon_off)
            self.is_mic_active = False

    def update_status(self):
        status = GetAssistantStatus()
        self.status_label.setText(status)
        
        # Auto turn off mic icon if backend turned it off
        if GetMicrophoneStatus() == "False" and self.is_mic_active:
            self.mic_btn.setIcon(self.mic_icon_off)
            self.is_mic_active = False

        # Highlight active agent in pipeline based on status
        active_agent = None
        status_lower = status.lower()
        if "listening" in status_lower:
            active_agent = "Listener"
        elif "thinking" in status_lower:
            active_agent = "Strategist"
        elif "executing" in status_lower or "speaking" in status_lower:
            active_agent = "Executor"
        elif "validating" in status_lower or "self-correct" in status_lower:
            active_agent = "Overseer"

        for name, (lbl, color) in self.agent_labels.items():
            if name == active_agent:
                lbl.setStyleSheet(f"""
                    QLabel {{
                        background-color: {color};
                        color: white;
                        border-radius: 8px;
                        padding: 3px 8px;
                        border: 1px solid {color};
                        font-weight: bold;
                    }}
                """)
            else:
                lbl.setStyleSheet(f"""
                    QLabel {{
                        background-color: #2a2a3e;
                        color: #666;
                        border-radius: 8px;
                        padding: 3px 8px;
                        border: 1px solid #333;
                    }}
                """)

    def update_chat(self):
        try:
            with open(rf"{DataDirPath}\ChatLog.json", "r") as f:
                messages = json.load(f)
                
            if len(messages) != self.last_chat_length:
                self.chat_area.clear()
                for msg in messages:
                    role = "You" if msg["role"] == "user" else Assistantname
                    color = "#e94560" if role == "You" else "#00d2ff"
                    self.chat_area.append(f"<b style='color:{color}'>{role}:</b> {msg['content']}<br>")
                self.last_chat_length = len(messages)
                self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
        except (FileNotFoundError, json.JSONDecodeError):
            pass

def GuiApp():
    SetMicrophoneStatus("False")
    SetAssistantStatus("Idle")
    SetQuery("")
    
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GuiApp()