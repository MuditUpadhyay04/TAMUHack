let video = document.createElement("video");
document.body.appendChild(video);  // This adds the video element to the DOM
let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let captureInterval;
let stream;
let lexInterval;

document.getElementById("button").addEventListener("click", startCapture);
document.getElementById("stopButton").addEventListener("click", stopCapture);
let storeTran = ""
startBtn = document.getElementById("startMute")
stopBtn = document.getElementById("stopUnmute")
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');

        storeTran = transcript
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
    };
} else {
    alert("Speech recognition is not supported in this browser.");
    startBtn.disabled = true;
}

startBtn.addEventListener('click', async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Your browser does not support audio recording.");
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunks = [];
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.start();
        console.log("Recording started.");

        recognition.start(); // Start transcribing
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } catch (error) {
        console.error("Error accessing microphone:", error);
        alert("Could not access your microphone.");
    }
});

stopBtn.addEventListener('click', async() => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        console.log("Recording stopped.");
    }

    if (recognition) {
        recognition.stop(); // Stop transcribing
        console.log("Speech recognition stopped.");
    }

    startBtn.disabled = false;
    stopBtn.disabled = true;

    // Optional: Save the recorded audio as a file

    console.log("Audio URL:", storeTran);

    userInput = `You are a job interviewer for a software engineering position, and your focus is on evaluating the interviewee's soft skills 
    rather than their technical expertise. Be supportive but Don't say anything else or give hints on how to solve the problem. Here is their input: `+ storeTran
    let responseText
    let polly_tr
    const message = userInput;
            if (message) {



                try {
                    const response = await fetch('http://localhost:5005/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message }),
                    });

                    const data = await response.json();
                    polly_tr = data.response


                } catch (error) {
                    console.error('Error:', error);

                }
            }
    callPollyASAP(polly_tr)


});

async function callPollyASAP(textA){
    try {
        console.log(textA)
        const response = await fetch('http://127.0.0.1:5003/polly', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ textA })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }

        // Convert response to Blob and create an object URL
        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);

        // Play the audio directly
        audioPlayer.src = audioUrl;
        audioPlayer.style.display = 'block'; // Show the audio player
        audioPlayer.play();


    } catch (error) {
        console.error("Error:", error);

    }
}

function startCapture() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (userStream) {
            stream = userStream;  // Store stream reference
            video.srcObject = stream;
            video.play();
            canvas.width = 180;  // Set canvas size
            canvas.height = 140; // Adjust as needed
            captureInterval = setInterval(sendImage, 10); // Start sending images every 2 seconds
        })
        .catch(function (err) {
            console.log("Error accessing webcam: " + err);
        });
}

function sendImage() {
    if (video.paused || video.ended) return;

    // Draw the current video frame onto the canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get the base64 image data from the canvas
    let imageData = canvas.toDataURL("image/png");

    // Send image to Flask backend
    fetch('http://127.0.0.1:5003/upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageData.split(',')[1] }) // Send only the image data (remove base64 header)
    })
    .then(response => response.json())
    .then(data => {


    })
    .catch(err => console.log("Error:", err));
}

function stopCapture() {
    clearInterval(captureInterval);  // Stop the image capturing interval
    if (stream) {
        // Stop all tracks of the video stream (to stop the webcam)
        stream.getTracks().forEach(track => track.stop());
    }
    fetch('http://127.0.0.1:5003/calculate', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.confidence)
        console.log(data.contact)

    })
    .catch(err => console.log("Error:", err));
    video.srcObject = null; // Disconnect the video feed
}