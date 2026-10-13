import pickle
import csv
import re
import shutil
import zipfile
from pathlib import Path

import numpy as np
from SimilarText import TextSimilarity, load_qa_data
from local_llm import generate_response

ROOT = Path(__file__).resolve().parent


def _model_file(filename):
    model_path = ROOT / "Trained models" / filename
    archive_path = ROOT / "Trained models.zip"
    if not model_path.exists() and archive_path.exists():
        archive_member = f"Trained models/{filename}"
        try:
            with zipfile.ZipFile(archive_path) as archive:
                if archive_member in archive.namelist():
                    model_path.parent.mkdir(exist_ok=True)
                    with archive.open(archive_member) as source, model_path.open("wb") as target:
                        shutil.copyfileobj(source, target)
        except (OSError, zipfile.BadZipFile):
            return model_path
    return model_path


def _load_pickle(path):
    try:
        with path.open("rb") as model_file:
            return pickle.load(model_file)
    except (OSError, pickle.PickleError, EOFError, ImportError, AttributeError):
        return None


personality_model = _load_pickle(_model_file("model.pkl"))
personality_vectorizer = _load_pickle(ROOT / "vectorizer.pkl")
tokenizer = _load_pickle(ROOT / "tokenizer.pickle")
label_encoder = _load_pickle(ROOT / "labelEncoder.pickle")
learning_model = None


def classify_personality(response):
    if personality_model is None or personality_vectorizer is None:
        return "Unknown"
    try:
        features = personality_vectorizer.transform([response])
        return str(personality_model.predict(features)[0])
    except Exception:
        return "Unknown"


def classify_learning_type(sentence):
    global learning_model
    if tokenizer is None or label_encoder is None:
        return "General"
    try:
        if learning_model is None:
            from keras.models import load_model

            model_path = _model_file("LearningStyleClassifier.h5")
            learning_model = load_model(model_path)
        from keras.utils import pad_sequences

        sequences = tokenizer.texts_to_sequences([clean(sentence)])
        padded = pad_sequences(sequences, maxlen=48, truncating="pre")
        prediction = learning_model.predict(padded, verbose=0)
        return str(label_encoder.inverse_transform(np.argmax(prediction, axis=-1))[0])
    except Exception:
        return "General"

# Text preprocessing function
def clean(text):
    text = re.sub(r'[^a-zA-Z ]', '', text)
    text = text.lower()
    return text


qa_path = ROOT / "question_answer.csv"
qa_dict = load_qa_data(str(qa_path))
text_similarity = TextSimilarity()
vectorstore = text_similarity.update_embeddings(qa_dict, save=False)


def send_gptnew(prompt, tem, vecstore=None):
    global vectorstore
    if vecstore is None:
        vecstore = vectorstore
    try:
        matches = text_similarity.top_similar_prompts(prompt, vecstore)
        prompt_similarity = matches[0][1] if matches else 0.0
    except Exception:
        prompt_similarity = 0.0
    database_score = f"Database similarity score is {prompt_similarity:.3f}"
    matching_prompt = next(
        (saved_prompt for saved_prompt in qa_dict if saved_prompt.casefold() == prompt.casefold()),
        None,
    )
    if matching_prompt and qa_dict[matching_prompt]["temperature"] == tem:
        stored_data = qa_dict[matching_prompt]
        return f"{database_score}\nFound in database\n{stored_data['returnstring']}"
    context = ""
    if prompt_similarity > 0.2 and qa_dict:
        similar_conversation = text_similarity.top_similar_docs(prompt, vecstore, qa_dict)
        summary = text_similarity.extractive_summary(prompt, similar_conversation)
        return f"{database_score}\nSearched from database\n{summary}"

    personality = classify_personality(prompt)
    learning_style = classify_learning_type(prompt)
    system_prompt = (
        "You are an academic doubt-solving teacher. Explain concepts clearly, "
        "with useful reasoning, and adapt your explanation to the student's "
        f"learning style ({learning_style}) and personality ({personality})."
    )
    answer = generate_response(prompt, system_prompt, float(tem))
    response_text = (
        f"{database_score}\nYou are a {personality} and prefer a "
        f"{learning_style} way of learning\n{answer}"
    )
    qa_dict[prompt] = {
        "returnstring": response_text,
        "mbti": personality,
        "learning": learning_style,
        "temperature": float(tem),
    }
    vectorstore = text_similarity.update_embeddings(qa_dict, save=False)
    with qa_path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["prompt", "returnstring", "mbti", "learning", "temperature"],
        )
        writer.writerow({"prompt": prompt, **qa_dict[prompt]})
    return response_text
