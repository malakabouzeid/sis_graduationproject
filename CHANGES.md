# Change List

## Kept and updated

- `app.py`: Replaced Flask routes with an interactive terminal menu and `--ask` / `--recommend` commands. Keeps English chat, temperature control, and course recommendations. Dataset paths resolve relative to the script.
- `helper.py`: Preserves cached English answer matching and optional personality/learning-style classifiers. Loads the bundled personality model when needed and uses safe fallbacks if optional classifier files or TensorFlow are unavailable.
- `local_llm.py`: Uses Ollama's local HTTP interface for generated answers and supports a configurable model.
- `course_recommender.py`: Retained the recommendation logic, fixed its default dataset path, and added prompted or positional student-ID selection with configurable result count.
- `SimilarText.py`, `question_answer.csv`, `vectorizer.pkl`, `tokenizer.pickle`, `labelEncoder.pickle`, `Trained models.zip`, and `uni_assist_dataset/`: Retained because they supply cached answers, optional classifier assets, or the course recommendation data.
- `requirements.txt`: Removed Flask, Flask-CORS, and Gunicorn. The project now installs only the data and similarity packages needed by its terminal workflows.
- `requirements-ml.txt`: Retained as an optional install for TensorFlow/Keras-based learning-style classification.
- `README.md`: Rewritten with terminal setup, run examples, language options, and local-model requirements.
- `SimilarText.py`: Handles prompts with no known vocabulary without dividing their zero vector by zero.

## Removed

- All nine HTML pages from `templates/` and `uni_assist_course_recommendation_starter/templates/`: these were browser-only views.
- `static/css/CJAT.css`, `script.js`, `signin.css`, `style.css`, and `templates/pxfuel.jpg`: these were browser-only assets.
- `credentials.csv`: the plaintext sign-in data was only read by the removed Flask login route.
- `quesans.py`: this unused helper recreated the QA CSV with empty headers and was not part of the chatbot runtime.
- The duplicate Flask starter files under `uni_assist_course_recommendation_starter/`: the recommender is integrated into the root CLI now.
- `MBTI Modelling.zip`: training notebooks and a duplicate classifier archive not used by the terminal application.
- `vecstore.pkl` and `vecstorevectorizer.pkl`: generated similarity caches; the app rebuilds its in-memory vectors from `question_answer.csv`.
- `__pycache__/`: generated Python bytecode, recreated automatically when needed.

The archived trained models and all data used by terminal features were preserved. The Python virtual environment remains at `.venv/`.
