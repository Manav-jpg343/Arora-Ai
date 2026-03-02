import sys
import os
import asyncio

# Adjust Python path to resolve Backend as a package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Backend.Model import FirstLayerDMM

test_prompts = [
    "type hello world in the browser",
    "can you type my name is edith",
    "open chrome and type machine learning"
]

print("--- Testing FirstLayerDMM ---")
for p in test_prompts:
    res = FirstLayerDMM(prompt=p)
    print(f"Prompt: '{p}' -> Result: {res}")
