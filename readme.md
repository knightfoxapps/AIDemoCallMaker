````markdown
   ___    ___      _ _             
  / _ \  / _ \ ___| (_)_ __   __ _ 
 | | | || | | / __| | | '_ \ / _` |
 | |_| || |_| \__ \ | | | | | (_| |
  \___/  \___/|___/_|_|_| |_|\__, |
                             |___/ 
          AI CALLER - Smart Conversation Synth


## 📦 About This Project

This is a powerful Python-based tool that uses **ChatGPT** (via OpenAI) and **Amazon Polly** to generate **realistic call center conversations** and **convert them into stereo audio files** with lifelike voices.

Perfect for:
- Contact center simulations
- QA & agent training
- Audio bot testing
- AI prototype demos

---

## 🚀 Features

✅ Auto-generates full customer service calls (20+ exchanges)  
✅ Natural language conversations with varied tones & moods  
✅ Supports escalation scenarios  
✅ Converts text to audio using **Amazon Polly neural voices**  
✅ Assigns stereo channels to Agent (left) and Customer (right)  
✅ Automatically selects gender-appropriate Polly voices  
✅ Supports mood variations, topic selection, and product location targeting  
✅ Account numbers are spaced for proper audio pronunciation

---

## 🛠️ Setup

### 1. Install Dependencies

Make sure you have Python 3.9+ installed. Then:

```bash
pip install -r requirements.txt

<details> <summary>Requirements</summary>
text
Copy
Edit
openai
boto3
tqdm
python-dateutil
pydub
</details>

You also need FFmpeg installed for audio processing.
Download from: https://ffmpeg.org/download.html

⚙️ First-Time Setup
Run the setup command:

bash
Copy
Edit
python DemoCallMaker.py -setup
You'll be prompted to enter:

OpenAI API Key

AWS Access Key ID / Secret

AWS Region

You can choose to save them in a local credentials.json file.

🧠 How to Use
Just run:

bash
Copy
Edit
python DemoCallMaker.py
You’ll be prompted to enter:

Company name

Sector (e.g., Telecom, E-commerce)

Products (comma-separated)

Customer locations

Date range

Number of calls to generate

Number of agents to generate

Optional specific conversation topic

Customer moods (e.g., polite, angry, frustrated)

That’s it — the app will generate conversations and save audio to the call_audios/ folder.

🔊 Output
📁 call_audios/

Stereo MP3 files

Each file represents one call with alternating agent/customer voices

All calls labeled with date and agent name

Example:

yaml
Copy
Edit
2025-03-05_Michael_Johnson_3.mp3
🧪 Tips
Use shorter ranges and smaller counts for quick testing.

You can inspect each Polly and ChatGPT API response in real time (debug mode).

Play the audio files in a stereo-enabled player for best effect.

🧼 To Reset Config
Delete the saved credentials:

bash
Copy
Edit
rm credentials.json
Then re-run with -setup.

📄 License
MIT License. Use it, fork it, break it, remix it.

🤖 Powered By
OpenAI GPT-4 Turbo

Amazon Polly

PyDub
