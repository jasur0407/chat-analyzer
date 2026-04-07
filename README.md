# Telegram Chat Analyzer Using JSON

A desktop Python app to display the chat statistics from the exported Telegram JSON file

## Features
Analyze group chats and direct messages

Displays:
* Total messages, words, characters
* Most used words
* Most active dates
* Average stats per day
* Per-user statistics

## Requirements

* Python 3.10+

## How to Run

1. Clone the repo:

```
git clone https://github.com/jasur0407/chat-analyzer
cd chat-analyzer
```

2. Add your Telegram exported file:

* Export chat as JSON from Telegram available by three-dots on the top-right corner

3. Run the app:

```
python main.py
```

## Output

* Tkinter UI shows main stats
* Detailed stats saved in `chat_stats.txt` in the same folder and can be accessed using `Open Stats File` button

## Notes

* Only works with Telegram JSON files
* Make sure the JSON format is valid