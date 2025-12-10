# LAS Python SDK

Official Python SDK for the Local Agent System.

## Installation

```bash
pip install -e .
```

## Usage

```python
from las_sdk import LASClient

# Initialize client
client = LASClient("http://localhost:7777")

# Send query
response = client.query("What is quantum computing?")
print(response["answer"])

# List skills
skills = client.list_skills()
print(f"Available skills: {skills}")

# Transcribe audio
result = client.transcribe("audio.mp3")
print(result["text"])

# Analyze image
analysis = client.analyze_image("screenshot.png", "What's in this image?")
print(analysis)
```

## API Reference

### LASClient

- `query(text, provider=None, model=None)` - Send query to agent
- `list_skills()` - List saved skills
- `get_skill(name)` - Get skill details
- `list_reflections(task_type=None, limit=10)` - List reflections
- `get_lessons(task_description, limit=5)` - Get relevant lessons
- `transcribe(audio_file, language=None, model_size="base")` - Transcribe audio
- `synthesize(text, voice_id=None, rate=150, output_file=None)` - Text-to-speech
- `analyze_image(image_file, prompt)` - Analyze image with vision model
- `list_plugins()` - List plugins
- `load_plugin(name)` - Load a plugin
- `health_check()` - Check API health
