# MBTI Personality Test

A modern web application that conducts MBTI personality tests through a conversational chat interface. Built with Flask and Langchain.

## Features

- Conversational chat interface for personality assessment
- Dark mode modern UI design
- Real-time interaction using Socket.IO
- MBTI personality type determination with detailed explanations
- Responsive design for all devices

## Tech Stack

- **Backend**: Flask, Langchain, OpenAI
- **Frontend**: HTML, CSS, JavaScript
- **Real-time Communication**: Socket.IO
- **Styling**: Custom CSS with responsive design

## Quick Start

The easiest way to get started is to use the provided start script:

```bash
./start.sh
```

This script will:
1. Create a virtual environment if needed
2. Install all dependencies
3. Set up the .env file if it doesn't exist
4. Prompt you for your OpenAI API key
5. Start the application

## Manual Setup Instructions

If you prefer to set things up manually:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd personalityTest
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Copy the example env file: `cp .env.example .env`
   - Edit the `.env` file and add your OpenAI API key: `OPENAI_API_KEY=your_openai_api_key_here`
   - You can get an API key from [OpenAI's platform](https://platform.openai.com/api-keys)

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## How It Works

1. The application uses Flask as a web server and Socket.IO for real-time communication.
2. Langchain with OpenAI's GPT model processes user responses to determine personality traits.
3. The test asks a series of questions targeting the four MBTI dimensions: E/I, S/N, T/F, and J/P.
4. After completing the questionnaire, the application calculates the MBTI type and provides detailed explanations.

## Project Structure

```
personalityTest/
├── app.py                  # Main Flask application
├── models/
│   └── mbti_analyzer.py    # MBTI analysis logic
├── static/
│   ├── css/
│   │   └── styles.css      # CSS styles
│   ├── js/
│   │   └── script.js       # Frontend JavaScript
│   └── images/             # Image assets
├── templates/
│   ├── index.html          # Main page template
│   └── result.html         # Results page template
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- MBTI personality framework
- OpenAI for the language model
- Langchain for the conversational AI toolkit 