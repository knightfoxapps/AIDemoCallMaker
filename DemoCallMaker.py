import openai
import boto3
import random
import re
from tqdm import tqdm
import os
import sys
import json
from datetime import datetime, timedelta
from dateutil.parser import parse
from pydub import AudioSegment
import tempfile

# Function to setup API keys
def setup_keys():
    openai_key = input("Enter your OpenAI API key: ")
    aws_access_key = input("Enter your AWS Access Key ID: ")
    aws_secret_key = input("Enter your AWS Secret Access Key: ")
    region = input("Enter your AWS region (e.g., us-east-1): ")

    credentials = {
        'openai_key': openai_key,
        'aws_access_key': aws_access_key,
        'aws_secret_key': aws_secret_key,
        'region': region
    }

    save = input("Would you like to save these credentials for future use? (yes/no): ")
    if save.lower() == 'yes':
        with open('credentials.json', 'w') as f:
            json.dump(credentials, f)
        print("Credentials saved.")
    return credentials

# Check if setup is required
if '-setup' in sys.argv or not os.path.exists('credentials.json'):
    creds = setup_keys()
else:
    with open('credentials.json', 'r') as f:
        creds = json.load(f)

# Configure OpenAI and AWS
openai.api_key = creds['openai_key']
polly = boto3.client('polly', aws_access_key_id=creds['aws_access_key'], aws_secret_access_key=creds['aws_secret_key'], region_name=creds['region'])
print("Polly client created successfully:", polly is not None)

# Interactive Setup
print("Welcome to the Call Center Sample Generator")
company_name = input("Enter the company name to be used for all calls: ")
sector = input("Enter the business sector (e.g., e-commerce): ")
products = input("Enter products separated by commas (e.g., Laptop,Phone,Tablet): ").split(',')
location = input("Enter customer locations separated by commas: ").split(',')
start_date = parse(input("Enter start date (YYYY-MM-DD): "))
end_date = parse(input("Enter end date (YYYY-MM-DD): "))
num_conversations = int(input("Enter the number of conversations to generate: "))
num_agents = int(input("Enter the number of agent names to generate: "))
specific_topic = input("Enter a specific topic for the conversations or press Enter to skip and get a variety: ")
moods = input("Enter customer moods separated by commas (e.g., polite, angry, frustrated): ").split(',')

# Function to determine gender based on name
def get_voice(name, voices_female, voices_male):
    female_names = ['Amanda', 'Jessica', 'Emily', 'Sarah', 'Jennifer', 'Laura', 'Anna', 'Joanna', 'Kendra', 'Kimberly', 'Samantha', 'Rachel', 'Lisa']
    first_name = name.split()[0]
    if first_name in female_names:
        return random.choice(voices_female)
    else:
        return random.choice(voices_male)

# Function to space out digits
def space_digits(text):
    return re.sub(r'(\d)', r'\1 ', text)

# Split text into manageable chunks for Polly
def split_text(text, max_length=2900):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, chunk = [], ""
    for sentence in sentences:
        if len(chunk) + len(sentence) + 1 > max_length:
            chunks.append(chunk.strip())
            chunk = sentence
        else:
            chunk += " " + sentence
    if chunk:
        chunks.append(chunk.strip())
    return chunks

# Generate common customer issues based on sector using AI
if specific_topic:
    issues = [specific_topic.strip()]
else:
    issues_prompt = f"List 10 common customer service issues typically faced in the {sector} industry."
    issues_response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": issues_prompt}]
    )
    print("ChatGPT issues response:", issues_response)
    issues = [issue.strip('- ').strip() for issue in issues_response.choices[0].message.content.strip().split('\n') if issue]

# Generate agent names using AI
agent_prompt = f"Generate {num_agents} realistic customer service agent full names. List them clearly numbered."
agent_response = openai.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": agent_prompt}]
)
print("ChatGPT agent names response:", agent_response)

agents = []
for line in agent_response.choices[0].message.content.strip().split('\n'):
    match = re.match(r'^\d+\.\s*(.*)', line.strip())
    if match:
        agents.append(match.group(1).strip())
    elif line.strip():
        agents.append(line.strip())

# Voice assignments
female_voices = ['Joanna', 'Kendra', 'Kimberly']
male_voices = ['Matthew', 'Justin', 'Kevin']

# Prepare for generation
dates = [start_date + timedelta(days=i%((end_date-start_date).days+1)) for i in range(num_conversations)]

# Directory for audio files
audio_dir = "call_audios"
os.makedirs(audio_dir, exist_ok=True)

# Generate conversations and audio files
for i in tqdm(range(num_conversations), desc="Generating Calls"):
    agent = random.choice(agents)
    product = random.choice(products).strip()
    issue = random.choice(issues).strip()
    cust_location = random.choice(location).strip()
    date_str = dates[i].strftime('%Y-%m-%d')

    customer_tone = random.choice(moods).strip()
    resolution_type = random.choice(["resolved directly", "required escalation"])

    agent_voice = get_voice(agent, female_voices, male_voices)
    customer_voice = random.choice(female_voices + male_voices)

    prompt = f"""
    Generate a realistic call-center conversation between a customer service agent named {agent} and a customer for {company_name}.

    Sector: {sector}
    Product: {product}
    Customer Issue: {issue}
    Customer Location: {cust_location}
    Customer Tone: {customer_tone}
    Resolution Type: {resolution_type}

    Requirements:
    - Use plain 'Agent:' and 'Customer:' tags without any special characters.
    - Conversation length must be at least 20 exchanges.
    """

    response = openai.chat.completions.create(model="gpt-4-turbo", messages=[{"role": "user", "content": prompt}], max_tokens=1200)
    print(f"ChatGPT conversation response for call {i+1}:", response)
    conversation_text = response.choices[0].message.content.strip()

    conversation_audio = AudioSegment.empty()
    num_chunks = 0

    for exchange in conversation_text.split("\n"):
        exchange = exchange.strip()
        if exchange.startswith("Agent:"):
            voice, pan = agent_voice, -1.0
        elif exchange.startswith("Customer:"):
            voice, pan = customer_voice, 1.0
        else:
            continue
        text = space_digits(exchange.split(":", 1)[1].strip())
        for chunk in split_text(text):
            attempts = 0
            success = False
            while attempts < 3 and not success:
                try:
                    print(f"\n[Polly Call Attempt {attempts+1}] Voice: {voice}, Chunk Length: {len(chunk)}\nChunk: {chunk}")
                    audio_response = polly.synthesize_speech(
                        Text=chunk,
                        OutputFormat='mp3',
                        VoiceId=voice,
                        Engine='neural'
                    )
                    if 'AudioStream' not in audio_response:
                        raise RuntimeError("Polly response missing 'AudioStream'")
                    print("Polly response metadata:", audio_response['ResponseMetadata'])
                    audio_bytes = audio_response['AudioStream'].read()
                    print("Polly audio bytes length:", len(audio_bytes))

                    if len(audio_bytes) < 2000:
                        raise ValueError("Audio too short – possibly incomplete response.")

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                        temp_audio.write(audio_bytes)
                        temp_audio.flush()
                        segment = AudioSegment.from_file(temp_audio.name, format='mp3').set_channels(2).pan(pan)
                        os.unlink(temp_audio.name)
                    conversation_audio += segment
                    num_chunks += 1
                    success = True

                except Exception as e:
                    print(f"[Attempt {attempts + 1}] Polly failed for chunk:\n{chunk[:100]}...\nError: {e}")
                    attempts += 1

            if not success:
                print(f"[SKIPPED] Polly failed after 3 attempts for this chunk.")

    audio_filename = f"{date_str}_{agent.replace(' ', '_')}_{i+1}.mp3"
    audio_path = os.path.join(audio_dir, audio_filename)
    conversation_audio.export(audio_path, format="mp3")
    print(f"Exported audio with {num_chunks} chunks to {audio_filename}, duration: {conversation_audio.duration_seconds:.2f}s")

print(f"\nAll conversations generated with stereo audio saved in '{audio_dir}' directory.")
