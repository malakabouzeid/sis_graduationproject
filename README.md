# AI-Powered Educational Chatbot

This project runs in the terminal. It provides an English educational chatbot backed by a local Ollama model, saved question-and-answer lookup, and a synthetic-data course recommender.

## Setup (Windows)

Install Python, create the virtual environment, and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install Ollama from [ollama.com/download/windows](https://ollama.com/download/windows), then download the default model once:

```powershell
ollama pull gemma3:4b
```

## Run

Launch the interactive terminal menu:

```powershell
.\.venv\Scripts\python.exe .\app.py
```

Ask one question directly:

```powershell
.\.venv\Scripts\python.exe .\app.py --ask "Explain photosynthesis" --temperature 0.4
```

Get course recommendations for a sample student:

```powershell
.\.venv\Scripts\python.exe .\app.py --recommend S0001 --top-n 5
```

Run the recommender directly and specify any dataset student ID, or omit the ID to be prompted:

```powershell
.\.venv\Scripts\python.exe .\course_recommender.py S0002 --top-n 3
.\.venv\Scripts\python.exe .\course_recommender.py
```

The chatbot uses English prompts and responses. The interactive menu lets you adjust temperature during a session. To select another installed Ollama model, set `OLLAMA_MODEL` before launching; the default is `gemma3:4b`.

Exact saved English questions and course recommendations can run without Ollama. New generated responses require Ollama and the downloaded model. Install `requirements-ml.txt` only if you also want the optional TensorFlow learning-style classifier; otherwise the app uses its general-style fallback.

The course recommender uses synthetic sample records in `uni_assist_dataset/`; its output is for demonstration and should not be treated as official academic advising.
