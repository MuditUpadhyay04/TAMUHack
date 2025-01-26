import base64
from io import BytesIO

import cv2
import numpy as np
import openai
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import random
from dotenv import load_dotenv
import os
import boto3
from flask_cors import CORS
from playsound import playsound
import wave
import json

app = Flask(__name__, static_folder='static')

flag = 0
total_conf = 0
total = 0
total_eye = 0
openai.api_key = [key]
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_image():
    global flag, total_conf, total, total_eye

    flag += 1
    if flag % 100 == 0:
        rekognition_client = boto3.client('rekognition', region_name='us-east-1')
        YAW_TOLERANCE = 10
        PITCH_TOLERANCE = 10
        data = request.json
        img_data = data.get('image')

        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Encode the processed image to send it back
        _, img_encoded = cv2.imencode('.png', img)
        img_bytes = img_encoded.tobytes()

        response = rekognition_client.detect_faces(
            Image={'Bytes': img_bytes},
            Attributes=['ALL']
        )

        if 'FaceDetails' in response:
            for face_detail in response['FaceDetails']:
                if 'Emotions' in face_detail:
                    emotions = face_detail['Emotions']
                    dominant_emotion = max(emotions, key=lambda x: x['Confidence'])
                    emotion_type = dominant_emotion['Type']
                    emotion_confidence = dominant_emotion['Confidence']
                    if emotion_type == "HAPPY" or emotion_type == "CALM":
                        total_conf += emotion_confidence / 100
                    else:
                        total_conf -= 1
                    total += 1
                    print(dominant_emotion)
                if 'EyeDirection' in face_detail:
                    eye_direction = face_detail['EyeDirection']
                    yaw = eye_direction['Yaw']
                    pitch = eye_direction['Pitch']

                    if abs(yaw) <= YAW_TOLERANCE and abs(pitch) <= PITCH_TOLERANCE:
                        eye_focus_status = "Viewing"
                        total_eye += 1
                    else:
                        eye_focus_status = "Nope"
                        total_eye -= 0.25
                    print(eye_focus_status)

    return jsonify({"confidence": 0})

@app.route('/index')
def index():
    # Render the login page
    return render_template('index.html')

@app.route('/calculate', methods=['GET'])
def calc():
    if total > 0:
        percentage_confidence = (total_conf / total) * 100.0
        percentage_contact = (total_eye / total) * 100.0
    else:
        percentage_confidence = 0.0
        percentage_contact = 0.0
    print(percentage_confidence)
    print(percentage_contact)
    return jsonify({"confidence": int(percentage_confidence), "contact": int(percentage_contact)})


@app.route('/polly', methods=['POST'])
def polly():
    print("here")
    polly_client = boto3.client(
        "polly",
        region_name="us-east-1",  # Change region as needed
        aws_access_key_id="key",  # Replace with your AWS credentials
        aws_secret_access_key="key")
    try:
        # Get text input from the JavaScript client
        data = request.json
        text_to_synthesize = data.get("text", "")

        if not text_to_synthesize:
            return jsonify({"error": "No text provided"}), 400

        # Use Polly to synthesize the text into speech
        response = polly_client.synthesize_speech(
            Text=text_to_synthesize,
            OutputFormat="mp3",
            VoiceId="Joanna"  # Change to the desired voice, e.g., Matthew, Ivy, etc.
        )

        # Save the MP3 to memory (BytesIO)
        if "AudioStream" in response:
            audio_stream = BytesIO(response["AudioStream"].read())
            audio_stream.seek(0)

            # Return the audio file as a response
            return send_file(
                audio_stream,
                mimetype="audio/mpeg",
                as_attachment=True,
                download_name="speech.mp3"  # Suggested filename for download
            )
        else:
            return jsonify({"error": "Failed to generate audio"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Load the dataset
dataset = pd.read_csv('cleaned_file.csv')

openai.api_key = [key]

@app.route('/')
def home():
    return render_template('index.html')


# Load the dataset
dataset = pd.read_csv('cleaned_file.csv')

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Polly client
polly_client = boto3.Session(
    aws_access_key_id=os.getenv(''),
    aws_secret_access_key=os.getenv(''),
    region_name=''
).client('polly')

@app.route('/login')
def login():
    # Render the login page
    return render_template('login.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/easy')
def easy():

    question = "In this problem, your program should read two whole numbers from the input, and print them out in increasing order. The input contains one line, which has two integers a and b, separated by a single space. Output the smaller number first, and the larger number second.\n\nSample 1:\n\nInput: 4 10\nOutput: 4 10\nSample 2:\nInput: 96 1\nOutput: 1 96"
    solution = "def solve():\n\tline = input()\n\ta, b = line.split()\n\ta = int(a)\n\tb = int(b)\n\n\tif a < b:\n\t\tprint(a, b)\n\telse:\n\t\tprint(b, a)"

    question_with_linebreaks = question.replace("\n", "<br>")

    return render_template('easy.html', question=question_with_linebreaks, solution=solution)

@app.route('/medium')
def medium():

    question = "In this problem, your program should take sum of N integers. The first line of the input contains an integer N, the number of integers your program should add. The next line contains the N integers to add the sum of the integers from the input.\n\nExample 1\n\nInput:\n2\n1 1\n\nOutput:\n2\n\nExample 2\n\nInput:\n5\n1 2 3 4 5\n\nOutput:\n15\n"
    solution = "def solve():\n\tn = int(input())\n\n\t# Read the integers to sum\n\tnumbers = list(map(int, input().split()))\n\n\t# Compute the sum of the numbers\n\tresult = sum(numbers)\n\n\t# Output the result\n\tprint(result)"

    question_with_linebreaks = question.replace("\n", "<br>")

    return render_template('medium.html', question=question_with_linebreaks, solution=solution)

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/hard')
def loadHardProblem():
    print("Loading dataset...")
    limited_dataset = dataset.head(100)  # Limit the dataset to 100 rows
    random_problem = limited_dataset.sample()  # Select a random problem

    question = random_problem['question'].values[0]
    solution = random_problem['solutions'].values[0]

    question_with_linebreaks = question.replace("\n", "<br>")

    return render_template('hard.html', question=question_with_linebreaks, solution=solution)

@app.route('/')
def mainPage():
    return render_template('main.html')

@app.route('/submit', methods=['POST'])
def compare_code():
    user_answer = request.form.get('user-answer')
    solution = request.form.get('solution')
    question = request.form.get('question')
    segments = solution.split("\n")

    segmentsPrompt = f"""
Here is a coding question

Question: {question}

Here is its solution

Correct Solution:
{solution}

Now, break the solution into logical code segments. Each segment should:
1. Represent a distinct, meaningful part of the algorithm (e.g., initialization, loops, conditions, or function calls).
2. Contain **multiple lines of code** whenever possible, but no more than 5 lines per segment.
3. Avoid splitting related lines (e.g., lines in the same loop, function, or condition) into separate segments.

If it's just some random nonsensical code that isn't even code, give a 0
Do not break the solution into one-line segments unless absolutely necessary (e.g., for clarity or if a single line is a meaningful step).

Separate each segment with a `|` character. Do not respond with anything other than the segmented solution.

"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful code comparison tool."},
                {"role": "user", "content": segmentsPrompt}
            ],
            max_tokens=600,
            temperature=0
        )

        response_content = response['choices'][0]['message']['content'].strip()

        segments = response_content.split("|")
        segments = [segment.strip() for segment in segments if segment.strip()]  # Clean up empty segments

    except Exception as e:
        return jsonify({'error': str(e)})

    prompt = f"""
You are a code analysis tool. Below are two Python code snippets and a description of the task they are meant to accomplish.

Question: {question}

User's Attempt:
{user_answer}

Correct Solution:
{solution}  

You are a helpful code analyzer
Assess if the user's attempted solution 1. Properly answers the question, and 2. Is logically equivalent to the correct solution. It's okay if the user's code is not exactly like the other code, just rank it out of 100, and add more points depending on how logically close the user's program is with the solution
Make sure to say where the code is similar, if possible. If the ONLY difference is tabs and spaces, still give the user a 100. In the end, ask the user something along the lines of "If you want a rundown of the correct solution, please select the code segment and I will explain!"
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful code comparison tool."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0
        )

        analysis = response['choices'][0]['message']['content'].strip()

        return render_template('submit.html',
                               user_answer=user_answer,
                               solution=solution,
                               analysis=analysis,
                               segments=segments)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/results')
def resultsPage():
    return render_template('results.html')

@app.route('/explain_segment', methods=['POST'])
def explain_segment():

    print("sup")
    data = request.get_json()
    segment = data['segment']
    question = data['question']

    print("supp")

    # Generate the GPT response
    prompt = f"""
    You are a code analysis tool. Below is a Python code segment and a question regarding its functionality.

    Question: {question}

    Code Segment:
    {segment}

    Please explain in brief bullet points this segment in relation to the question, highlighting what it does.
    """
    print("suppp")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful code analyzer."},
                      {"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        print("supppp")

        explanation = response['choices'][0]['message']['content'].strip()

        # Return the audio file URL for the frontend to handle
        return jsonify({'explanation': explanation})

    except Exception as e:
        print("suppppp")

        return jsonify({'error': str(e)})



if __name__ == '__main__':
    app.run(debug=True)
