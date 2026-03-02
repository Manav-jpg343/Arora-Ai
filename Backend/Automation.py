# Import required libraries
# from email import message
# from unittest import result
# from urllib import response
# from click import command
from email.mime import application
from AppOpener import close, open as appopen   # Import functions to open and close apps.
from webbrowser import open as webopen   # Import web browser functionality.
from pywhatkit import search, playonyt   # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values   # Import dotenv to manage environment varisbles.
from bs4 import BeautifulSoup   # Import BeautifulSoup for parsing HTML content.
from rich import print   # Import rich for styled console output.
from groq import Groq   # Import Groq for AI chat functionalities.
import webbrowser   # Import webbrowser for opening URLs.
import subprocess   # Import subprocess for interacting with the system.
import requests   # Import requests for making HTTP requests.
import keyboard   # Import keyboard for keyboard-related actions.
import asyncio   # Import asynciio for asynchronous programming.
import os 

# Import Windows control functions
from Backend.WindowsControl import (
    mouse_click, mouse_double_click, mouse_right_click, mouse_move, mouse_scroll,
    type_text_instant, press_key, hotkey, 
    focus_window, minimize_window, maximize_window, snap_window_left, snap_window_right,
    take_screenshot, run_command, open_url, open_file, open_folder,
    copy, paste, cut, undo, redo, select_all, save,
    new_tab, close_tab, switch_window, close_window,
    wait, get_clipboard, set_clipboard
) 

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")   # Retrieve the Groq API key.

# Define CSS classes for parsing specific elements in HTML content.
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# Define a user-agent for making web request.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize the Groq client with API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; fell free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letter"}]

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic)   # Use pywhatkit's search function to perfrom a Google search.
    return True   # Indicate success.

# Function to generate content using AI and save it to a file.
def Content(Topic):

    # Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'   # Default text editor.
        subprocess.Popen([default_text_editor, File])   # Open the file in Notepad.

    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})   # Add the user's prompt to messages.

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # Specify the AI model.
            messages=SystemChatBot + messages[-10:],   # Include system instructions and chat history limit to 10.
            max_tokens=2048,   # Limit the maximum tokens in the response.
            temperature=0.7,   # Adjust response randomness.
            top_p=1,   # Use nucleus sampling for response diversity.
            stream=False,   # Disable streaming response.
            stop=None   # Allow the model to determine stopping  
        )

        Answer = completion.choices[0].message.content
        Answer = Answer.replace("</s>", "")   # Remove unwanted tokens from the response.
        messages.append({"role": "assistant", "content": Answer})   # Add the AI's response to messages.
        return Answer
    
    Topic: str = Topic.replace("Content", "")   # Remove "Content" from the topic.
    ContentByAI = ContentWriterAI(Topic)   # Generate content using AI.

    # Save the generated content to a text file.
    with open(rf"Data\{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)   # Write the content to the file.
        file.close()

    OpenNotepad(rf"Data\{Topic.lower().replace(' ','')}.txt")   # Open the file in Notepad.
    return True   # Indicate success.

# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"   # Contruct the YouTube search URL.
    webbrowser.open(Url4Search)   # Open the search URL in a web browser.
    return True   # Indiacate Success.

# Function to play a video on YouTube.
def PlayYouTube(query):
    playonyt(query)   # Use pywhatkit's playonyt function to play the video.
    return True   # Indicate success.

# Function to open an application or a relevant webpage.
def OpenApp(app, sess=requests.session()):
    
    # Map generic terms to specific application names
    app_aliases = {
        "browser": "chrome",
        "web browser": "chrome",
        "internet": "chrome",
        "mail": "outlook",
        "email": "outlook",
        "music": "spotify",
        "video": "vlc",
        "text editor": "notepad",
        "editor": "notepad",
        "terminal": "cmd",
        "command prompt": "cmd",
    }
    
    # Check if the app name is an alias and replace it
    app_lower = app.lower().strip()
    if app_lower in app_aliases:
        app = app_aliases[app_lower]
    
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)   # Attempt to open the app.
        return True   # Indicate success.
    
    except:
        # Nested function to extract links from HTML content.
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')   # Parse the HTML content.
            links = soup.find_all('a', {'jsname': 'UWckNb'})   # Find relevant links.
            return [link.get('href') for link in links]   # Return the links.
        
        # Nested function to perform a Google search and retrieve HTML.
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"   # Construct the Google search URL.
            headers = {"User-Agent": useragent}   # Use the predefined user-agent.
            response = sess.get(url, headers=headers)   # Perform the GET request.

            if response.status_code == 200:
                return response.text   # Return the HTML content.
            else:
                print("Failed to retrieve search results.")   # Print an error message.
            return None
        
        html = search_google(app)   # Perform the Google search.

        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])   # Open the first link in a web browser.
            else:
                # Fallback: just open a Google search page for the app
                webopen(f"https://www.google.com/search?q={app}")

        return True   # Indicate success.
    
# Function to close an application.
def CloseApp(app):

    if "chrome" in app:
        pass   # Skip if the app is Chrome.
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)   # Attempt to close the app.
            return True   # Indicate success.
        except:
            return False   # Indicate failure.

# Function to type precise text into the current focused window.
def TypeText(text):
    keyboard.write(text)   # Type the text character by character.
    return True

# Function to execute system-level commands.
def System(command):

    # Nested function to mute the system volume.
    def mute():
        keyboard.press_and_release("volume mute")   # Simulate the mute key press.

    # Nested function to unmute the system volume.
    def unmute():
        keyboard.press_and_release("volume mute")   # Simulate the unmute key press.

    # Nested function to increase the system volume.
    def volume_up():
        keyboard.press_and_release("volume up")   # Simulate the volume up key press.

    # Nested function to decrease the system volume.
    def volume_down():
        keyboard.press_and_release("volume down")   # Simulate the volume down key press.

    # Execte the appropriate command. 
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume_up":
        volume_up()
    elif  command == "volume_down":
        volume_down()

    return True   # Indicate sucess.
    
# Asyncohronous function to translate and execute uesr commands.
async def TranslateAndExecute(commands: list[str]):

    funcs = []   # List to store asynchronous task.

    for command in commands:
            
        if command.startswith("open "):   # Handle "open" commands.

            if "open it" in command:   # Ignore "open it" commands.
                pass

            if "open file" == command:   # Ignore "open file" commands.
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))   # Schedule app opening.
                funcs.append(fun)

        elif command.startswith("general "):   # Placeholder for general commands.
            pass

        elif command.startswith("realtime "):   # Placeholder for real-time commands.
            pass

        elif command.startswith("close "):   # Handle "close" commands.
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))   # Schedule app closing.
            funcs.append(fun)

        elif command.startswith("play "):   # Handle "play" commands.
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))   # Schedule YouTube playback.
            funcs.append(fun)

        elif command.startswith("content "):   # Handle "content" commands.
            fun = asyncio.to_thread(Content, command.removeprefix("content "))   # Schedule content creation.
            funcs.append(fun)

        elif command.startswith("google search"):   # Handle Google search commands.
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))   # Schedule Google search.
            funcs.append(fun)

        elif command.startswith("youtube search "):   # Handle YouTube search commands.
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))   # Schedule YouTube search.
            funcs.append(fun)

        elif command.startswith("system "):   # Handle system commands.
            fun = asyncio.to_thread(System, command.removeprefix("system "))   # Schedule system command..
            funcs.append(fun)

        elif command.startswith("type "):   # Handle custom type command.
            fun = asyncio.to_thread(type_text_instant, command.removeprefix("type "))   # Schedule text typing.
            funcs.append(fun)

        # ==================== NEW WINDOWS CONTROL COMMANDS ====================
        
        elif command == "click" or command.startswith("click "):   # Handle click commands
            args = command.removeprefix("click ").strip()
            if args and args != "click":
                # Parse coordinates if provided (e.g., "click 500 300")
                parts = args.split()
                if len(parts) >= 2:
                    try:
                        x, y = int(parts[0]), int(parts[1])
                        fun = asyncio.to_thread(mouse_click, x, y)
                    except ValueError:
                        fun = asyncio.to_thread(mouse_click)
                else:
                    fun = asyncio.to_thread(mouse_click)
            else:
                fun = asyncio.to_thread(mouse_click)
            funcs.append(fun)

        elif command == "right click" or command.startswith("right click "):   # Handle right click
            args = command.removeprefix("right click ").strip()
            if args and args != "right click":
                parts = args.split()
                if len(parts) >= 2:
                    try:
                        x, y = int(parts[0]), int(parts[1])
                        fun = asyncio.to_thread(mouse_right_click, x, y)
                    except ValueError:
                        fun = asyncio.to_thread(mouse_right_click)
                else:
                    fun = asyncio.to_thread(mouse_right_click)
            else:
                fun = asyncio.to_thread(mouse_right_click)
            funcs.append(fun)

        elif command == "double click" or command.startswith("double click "):   # Handle double click
            args = command.removeprefix("double click ").strip()
            if args and args != "double click":
                parts = args.split()
                if len(parts) >= 2:
                    try:
                        x, y = int(parts[0]), int(parts[1])
                        fun = asyncio.to_thread(mouse_double_click, x, y)
                    except ValueError:
                        fun = asyncio.to_thread(mouse_double_click)
                else:
                    fun = asyncio.to_thread(mouse_double_click)
            else:
                fun = asyncio.to_thread(mouse_double_click)
            funcs.append(fun)

        elif command == "scroll up":   # Handle scroll up
            fun = asyncio.to_thread(mouse_scroll, 5)
            funcs.append(fun)

        elif command == "scroll down":   # Handle scroll down
            fun = asyncio.to_thread(mouse_scroll, -5)
            funcs.append(fun)

        elif command.startswith("scroll "):   # Handle scroll with amount
            args = command.removeprefix("scroll ").strip()
            try:
                amount = int(args)
                fun = asyncio.to_thread(mouse_scroll, amount)
            except ValueError:
                if "up" in args:
                    fun = asyncio.to_thread(mouse_scroll, 5)
                else:
                    fun = asyncio.to_thread(mouse_scroll, -5)
            funcs.append(fun)

        elif command.startswith("move mouse "):   # Handle mouse move
            args = command.removeprefix("move mouse ").strip()
            parts = args.split()
            if len(parts) >= 2:
                try:
                    x, y = int(parts[0]), int(parts[1])
                    fun = asyncio.to_thread(mouse_move, x, y)
                    funcs.append(fun)
                except ValueError:
                    pass

        elif command.startswith("hotkey "):   # Handle hotkey combinations
            args = command.removeprefix("hotkey ").strip()
            keys = args.replace("+", " ").split()
            fun = asyncio.to_thread(hotkey, *keys)
            funcs.append(fun)

        elif command.startswith("press key "):   # Handle single key press
            key = command.removeprefix("press key ").strip()
            fun = asyncio.to_thread(press_key, key)
            funcs.append(fun)

        elif command.startswith("focus window "):   # Handle focus window
            window_name = command.removeprefix("focus window ").strip()
            fun = asyncio.to_thread(focus_window, window_name)
            funcs.append(fun)

        elif command == "minimize window" or command.startswith("minimize window "):   # Handle minimize
            window_name = command.removeprefix("minimize window ").strip()
            if window_name and window_name != "minimize window":
                fun = asyncio.to_thread(minimize_window, window_name)
            else:
                fun = asyncio.to_thread(minimize_window)
            funcs.append(fun)

        elif command == "maximize window" or command.startswith("maximize window "):   # Handle maximize
            window_name = command.removeprefix("maximize window ").strip()
            if window_name and window_name != "maximize window":
                fun = asyncio.to_thread(maximize_window, window_name)
            else:
                fun = asyncio.to_thread(maximize_window)
            funcs.append(fun)

        elif command == "snap left":   # Handle snap left
            fun = asyncio.to_thread(snap_window_left)
            funcs.append(fun)

        elif command == "snap right":   # Handle snap right
            fun = asyncio.to_thread(snap_window_right)
            funcs.append(fun)

        elif command == "take screenshot":   # Handle screenshot
            fun = asyncio.to_thread(take_screenshot)
            funcs.append(fun)

        elif command.startswith("run command "):   # Handle run command
            cmd = command.removeprefix("run command ").strip()
            fun = asyncio.to_thread(run_command, cmd)
            funcs.append(fun)

        elif command == "copy":   # Handle copy
            fun = asyncio.to_thread(copy)
            funcs.append(fun)

        elif command == "paste":   # Handle paste
            fun = asyncio.to_thread(paste)
            funcs.append(fun)

        elif command == "cut":   # Handle cut
            fun = asyncio.to_thread(cut)
            funcs.append(fun)

        elif command == "select all":   # Handle select all
            fun = asyncio.to_thread(select_all)
            funcs.append(fun)

        elif command == "undo":   # Handle undo
            fun = asyncio.to_thread(undo)
            funcs.append(fun)

        elif command == "redo":   # Handle redo
            fun = asyncio.to_thread(redo)
            funcs.append(fun)

        elif command == "save":   # Handle save
            fun = asyncio.to_thread(save)
            funcs.append(fun)

        elif command == "new tab":   # Handle new tab
            fun = asyncio.to_thread(new_tab)
            funcs.append(fun)

        elif command == "close tab":   # Handle close tab
            fun = asyncio.to_thread(close_tab)
            funcs.append(fun)

        elif command == "switch window":   # Handle switch window (Alt+Tab)
            fun = asyncio.to_thread(switch_window)
            funcs.append(fun)

        elif command == "close window":   # Handle close window (Alt+F4)
            fun = asyncio.to_thread(close_window)
            funcs.append(fun)

        elif command.startswith("open url "):   # Handle open URL
            url = command.removeprefix("open url ").strip()
            fun = asyncio.to_thread(open_url, url)
            funcs.append(fun)

        elif command.startswith("open file "):   # Handle open file
            filepath = command.removeprefix("open file ").strip()
            fun = asyncio.to_thread(open_file, filepath)
            funcs.append(fun)

        elif command.startswith("open folder "):   # Handle open folder
            folderpath = command.removeprefix("open folder ").strip()
            fun = asyncio.to_thread(open_folder, folderpath)
            funcs.append(fun)

        elif command.startswith("wait "):   # Handle wait
            args = command.removeprefix("wait ").strip()
            try:
                seconds = float(args)
                fun = asyncio.to_thread(wait, seconds)
                funcs.append(fun)
            except ValueError:
                pass

        # ==================== END NEW COMMANDS ====================

        else:
            print(f"No Function Found. For {command}")   # Print an error for unrecognized commands.

    results = await asyncio.gather(*funcs)   # Exeute all tasks concurrently. 
        
    for result in results:   # Process the results.
        if isinstance(result, str):
            yield result
        else:
            yield result

# Asynchronous funstion to automate command execution.
async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands):   # Translate and execute commands.
        yield result
    
# if __name__ == "__main__":
#     asyncio.run(Automation(["open chrome"]))