# Cyrus-assistant

# Jarvis Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

Jarvis Assistant is an advanced, interactive AI-powered chat application built with Streamlit. It serves as a versatile assistant capable of handling various roles such as tutor, coding assistant, career helper, and more. The app features a modern UI with dark mode support, session management, code execution, voice output, file uploads, and integration with AI engines like Gemini and Ollama. It emphasizes user experience with animations, avatars, and customizable prompts.

This project is designed for developers and users interested in building or using extensible AI assistants with memory persistence, command handling, and enhanced interaction features.

## Features

- **Interactive Chat UI**: Responsive conversation interface with message editing, deletion, pinning, regeneration, and reactions (upvote/downvote).
- **Session Management**: Create, switch, clear, export, and summarize sessions with persistent memory.
- **AI Engines**: Supports Google Gemini and Ollama for generating responses; fallback mechanisms for availability.
- **Customizable Roles & Tones**: Select from roles (e.g., tutor, coding assistant, researcher) and tones (e.g., friendly, humorous, professional).
- **Quick Prompts**: Predefined and user-addable templates for common queries.
- **Code Execution**: Safely run Python code snippets with timeout controls and output display.
- **Voice Output**: Optional text-to-speech for assistant responses (if dependencies are installed).
- **File Uploads**: Attach and process text files in messages.
- **Search & Filters**: Search messages, filter by role/pinned, and sort by timestamp.
- **Dark Mode**: Toggleable theme for better accessibility.
- **Animations & Avatars**: Fade-in effects, emojis for roles, and success animations.
- **Prompt Builder**: Dynamic prompt generation based on context, role, and tone.
- **Security**: Safe HTML escaping, controlled code execution, and error handling.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip for package management

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/jarvis-assistant.git
   cd jarvis-assistant
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   **requirements.txt** (sample):
   ```
   streamlit>=1.0.0
   google-generativeai  # For Gemini (optional)
   ollama  # For Ollama (optional)
   pydub  # For voice (optional)
   # Add other deps as needed: uuid, json, subprocess, etc. (most are standard library)
   ```

3. Set up environment variables (e.g., in `.env`):
   - `JARVIS_API_KEY`: Your Google Gemini API key (optional).
   - `OLLAMA_URL`: URL for Ollama server (default: http://localhost:11434).
   - `HISTORY_FILE`: Path to memory storage (default: history.json).

4. Run the app:
   ```
   streamlit run main.py
   ```

## Usage

1. Launch the app via Streamlit.
2. Use the sidebar to configure:
   - Select role and tone.
   - Enable features like voice or code execution.
   - Manage sessions and quick prompts.
3. In the main area:
   - View and interact with conversation history.
   - Compose messages, attach files, and send.
   - Search, filter, and sort messages.
4. The assistant responds automatically to user inputs, using context from memory.

### Example

- Ask: "Explain quantum computing simply."
- Use quick prompt: "Summarize" for concise overviews.
- Run code: Copy and execute Python snippets from responses.

## Configuration

- **Settings**: Edit `config/settings.py` for defaults like model names, history file, and API keys.
- **Custom Modules**: Extend functionality in `core/` directory (e.g., add new engines or commands).
- **Voice Engine**: Requires additional setup; handle exceptions if not available.

## Project Structure

```
jarvis-assistant/
├── App.py               # Entry point: Streamlit app
├── config/
│   └── settings.py       # Configuration class
├── core/
│   ├── assistant.py      # JarvisAssistant logic
│   ├── command_engine.py # Command handling
│   ├── gemini_engine.py  # Gemini integration
│   ├── memory.py         # Memory management
│   ├── ollama_engine.py  # Ollama integration
│   ├── prompt_controller.py # Prompt building
│   ├── utils.py          # Utility functions
│   └── voice_engine.py   # Voice output (optional)
├── requirements.txt      # Dependencies
└── README.md             # This file
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/YourFeature`.
3. Commit changes: `git commit -m 'Add YourFeature'`.
4. Push to branch: `git push origin feature/YourFeature`.
5. Open a Pull Request.

Report issues or suggest enhancements via GitHub Issues.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the UI.
- AI powered by [Google Gemini](https://ai.google.dev/) and [Ollama](https://ollama.com/).
- Inspired by conversational AI assistants like JARVIS from Iron Man.

For questions, contact [your.email@example.com].