from groq import Groq   # type: ignore #  Importing the Groq library to use its API.
from json import load, dump   # Importing functions to read and write JSON files.
import datetime   # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values   # type: ignore # Improting dotenv_values to read enviroment variables from a .env file.

# Load enviroment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve specific environment variables for username, assistant name, and API key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Initialize an empty list to store chat messages.
messages = []

# Define a system message that provides context to the AI chatbot about its role and behavior.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# A list of system instruction for the  chatbot.
SystemChatBot = [
    {"role": "system", "content": System}
] 

# Attempt to load the chat log from a JSON file.
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)   # Load existing messages from the chat log.
except FileNotFoundError:
    # If the file doesn't exist, create an empty JSON file to store chat logs.
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime.datetime.now()   # Get the current date and time.
    day = current_date_time.strftime("%A")   # Day of the week.
    date = current_date_time.strftime("%D")   # Day of the month.
    month = current_date_time.strftime("%B")   # Full month name.
    year = current_date_time.strftime("%Y")   # Year.
    hour = current_date_time.strftime("%H")   # Hour in 24-hour format.
    minute = current_date_time.strftime("%M")   # Minute.
    second = current_date_time.strftime("%S")   # Second.

    # Format the information into a string.
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# Funcction to modify the chatbot's response for better formatting.
def AnswerModifier(Ansewer):
    lines = Ansewer.split('\n')   # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]   # Remove empty lines.
    modified_answer = '\n' .join(non_empty_lines)   # Join the cleaned lines back together.
    return modified_answer

# Main chatbot function to handle user queries.
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """

    try:
        # Load the existing chat log from the JSON file.
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # Append the user's query to the messaegs list.
        messages.append({"role": "user", "content": f"{Query}"})

        # Make a request to the Graq API for a response.
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # Specify the AI model to ues.
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages[-10:],   # Include system instructions, real-time into, and ONLY last 10 chat history items.
            max_tokens=1024,   # Limit the maximum tokens in the response.
            temperature=0.7,   # Adjust response randomness (higher means more random).
            top_p=1,   # Use nucleus sampling to control diversity.
            stream=False,   # Disable streaming response for faster resolution.
            stop=None   # Allow the model to determine when to stop. 
        )

        Answer = completion.choices[0].message.content
        Answer = Answer.replace("</s>", "")   # Clean up any unwanted tokens from the response.

        # Append the chatbot's response to the messages list.
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated chat log to the JSON file.
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)
        
        # Return the formatted response.
        return AnswerModifier(Ansewer=Answer)
    
    except Exception as e:
        # Handle errors by printing the exception and resetting the chat log.
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)   # Return the query after resetting the log.

# Main program entry point.
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question:")   # Prompt the user for a question.
        print(ChatBot(user_input))   # Call the chatbot function and print its response.