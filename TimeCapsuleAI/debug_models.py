import google.generativeai as genai
from app.utils.helpers import get_env

def main():
    api_key = get_env("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)

    print("Available models:\n")
    for m in genai.list_models():
        print(m.name, "->", m.supported_generation_methods)

if __name__ == "__main__":
    main()
