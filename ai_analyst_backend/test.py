import os
import google.generativeai as genai

api_key = "AIzaSyCMdNKoVgc6uRlJRWtu0sfHTaSqjL0ra3s"
if not api_key:
    print("GEMINI_API_KEY environment variable not set.")
else:
    genai.configure(api_key=api_key)
    print("Available Gemini Models:")
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name} (Supports generateContent)")