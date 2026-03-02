import cohere   # Import the Cohere library for AI services.
from rich import print   # Import the Rich library to enhance terminal outputs.
from dotenv import dotenv_values   # Import dotenv to load environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve API key.
CohereAPIKey = env_vars.get("CohereAPIKey")

# Create a Cohere client using the provided API key.
co = cohere.Client(api_key=CohereAPIKey)

# Define a list of recognized function keywords for task categorization.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "type",
    # Windows control commands
    "click", "right click", "double click", "scroll", "move mouse",
    "hotkey", "press key", "focus window", "minimize window", "maximize window",
    "snap left", "snap right", "take screenshot", "run command",
    "copy", "paste", "select all", "undo", "redo", "save",
    "new tab", "close tab", "switch window", "close window",
    "open url", "open file", "open folder", "wait"
]

# Initialize an empty list to store user messages.
messages = []

# Define the preamble that guides the AI model on how to categorize queries.
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
-> Respond with 'type (text)' if a query is explicitly asking you to physically type, write out, or input a specific text into the active window (e.g., 'type hello world', 'type my name is edith').
-> Respond with 'click (x, y)' or 'click' if a query is asking to click at a position or current position. Use 'right click' for right clicks, 'double click' for double clicks.
-> Respond with 'scroll up' or 'scroll down' if a query is asking to scroll.
-> Respond with 'hotkey (keys)' if a query is asking to press a keyboard shortcut like 'press ctrl+c', 'press alt+tab', etc. Respond with 'hotkey ctrl c' for ctrl+c.
-> Respond with 'press key (key)' if a query is asking to press a single key like 'press enter', 'press escape', etc.
-> Respond with 'focus window (window name)' if a query is asking to focus/switch to a specific window.
-> Respond with 'minimize window (window name)' or 'minimize window' to minimize a window or the active window.
-> Respond with 'maximize window (window name)' or 'maximize window' to maximize a window or the active window.
-> Respond with 'snap left' or 'snap right' if a query is asking to snap the window to left or right half of screen.
-> Respond with 'take screenshot' if a query is asking to take a screenshot.
-> Respond with 'run command (command)' if a query is asking to run a system/terminal command.
-> Respond with 'copy', 'paste', 'cut', 'select all', 'undo', 'redo', 'save' for these common operations.
-> Respond with 'new tab', 'close tab', 'switch window', 'close window' for these window/tab operations.
-> Respond with 'open url (url)' if a query is asking to open a specific URL.
-> Respond with 'open file (filepath)' if a query is asking to open a specific file.
-> Respond with 'open folder (folderpath)' if a query is asking to open a specific folder.
-> Respond with 'wait (seconds)' if a query requires waiting for a specified time.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Define a chat history with predefined user-chatbot interactions for context.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    {"role": "User", "message": "type hello world in the browser"},
    {"role": "Chatbot", "message": "type hello world"},
    {"role": "User", "message": "open notepad and type my name is edith"},
    {"role": "Chatbot", "message": "open notepad, type my name is edith"},
    {"role": "User", "message": "click on the screen"},
    {"role": "Chatbot", "message": "click"},
    {"role": "User", "message": "click at position 500 300"},
    {"role": "Chatbot", "message": "click 500 300"},
    {"role": "User", "message": "scroll down"},
    {"role": "Chatbot", "message": "scroll down"},
    {"role": "User", "message": "press ctrl+c"},
    {"role": "Chatbot", "message": "hotkey ctrl c"},
    {"role": "User", "message": "press enter"},
    {"role": "Chatbot", "message": "press key enter"},
    {"role": "User", "message": "switch to chrome window"},
    {"role": "Chatbot", "message": "focus window chrome"},
    {"role": "User", "message": "minimize this window"},
    {"role": "Chatbot", "message": "minimize window"},
    {"role": "User", "message": "maximize notepad"},
    {"role": "Chatbot", "message": "maximize window notepad"},
    {"role": "User", "message": "take a screenshot"},
    {"role": "Chatbot", "message": "take screenshot"},
    {"role": "User", "message": "copy this text"},
    {"role": "Chatbot", "message": "copy"},
    {"role": "User", "message": "paste it here"},
    {"role": "Chatbot", "message": "paste"},
    {"role": "User", "message": "open chrome, go to google.com and search for python"},
    {"role": "Chatbot", "message": "open chrome, wait 2, open url https://google.com, wait 1, type python, press key enter"},
    {"role": "User", "message": "snap this window to the left"},
    {"role": "Chatbot", "message": "snap left"},
    {"role": "User", "message": "run ipconfig command"},
    {"role": "Chatbot", "message": "run command ipconfig"}
]

# Define the main function for decision-making on queries.
def FirstLayerDMM(prompt: str = "test"):
    from groq import Groq
    
    # Initialize the Groq client
    GroqAPIKey = env_vars.get("GroqAPIKey")
    client = Groq(api_key=GroqAPIKey)
    
    # Format chat history for Groq
    groq_messages = [{"role": "system", "content": preamble}]
    
    # Limit chat history to the last 10 messages to significantly speed up processing
    recent_history = ChatHistory[-10:] if len(ChatHistory) > 10 else ChatHistory
    
    for msg in recent_history:
        role = "user" if msg["role"] == "User" else "assistant"
        groq_messages.append({"role": role, "content": msg["message"]})
        
    groq_messages.append({"role": "user", "content": prompt})

    # Create a chat completion with Groq
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=groq_messages,
        temperature=0.7,
        max_tokens=1024,
        stream=False
    )

    response = completion.choices[0].message.content
    
    # Remove newline characters and split responses into indiviual tasks.
    response = response.replace("\n", "")
    response = response.split(",")

    # Strip leading and trailing whitespaces from each task.
    response = [i.strip() for i in response]

    # Initialize an empty list to filter valid tasks.
    temp = []

    # Filter the tasks based on recongnized funtiong keybords.
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)   #Add valid tasks to the filtered list.

    # Update the response with the filtered list of tasks.
    response = temp

    # If '(query)' is in the response, recursively call the function for further clarification.
    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse   # Return the clarified response.
    else:
        return response   # Return the filtered response.

#Entry point for the script.
if __name__ == "__main__":
    # Continuously prompt the user for input and process it.
    while True:
        print(FirstLayerDMM(input(">>>")))   # Print the categorized response.