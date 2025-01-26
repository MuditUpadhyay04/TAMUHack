import boto3
import os
from playsound import playsound


def synthesize_speech(text, output_file="speech.mp3", voice_id="Joanna"):
    """
    Synthesize speech using Amazon Polly and save it to a file.

    Args:
        text (str): The text to synthesize.
        output_file (str): The name of the output audio file.
        voice_id (str): The Polly voice ID (e.g., 'Joanna', 'Matthew').
    """
    try:
        # Create a Polly client
        polly_client = boto3.client('polly')

        # Synthesize the speech
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id
        )

        # Save the audio stream to a file
        with open(output_file, 'wb') as file:
            file.write(response['AudioStream'].read())

        print(f"Speech synthesized and saved to {output_file}")

        # Play the audio
        playsound(output_file)

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    text_to_speak = "Hello, this is Amazon Polly. I can convert text into lifelike speech!"
    synthesize_speech(text_to_speak)
