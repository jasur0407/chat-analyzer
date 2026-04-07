import json
from datetime import datetime, date
import os
import tkinter as tk
from tkinter import Label, Button, Frame, messagebox, filedialog


file_path = filedialog.askopenfilename(title="Select Telegram JSON file to analyze")


# Validate the file type
if file_path[-5::] != ".json":
    print("Error: Upload a JSON file")
    exit()


# Load JSON func
def load_json():
    while True:
        try: 
            with open(file_path, 'r', encoding="utf8") as f: 
                data = json.load(f) 
                print("The JSON file is read successfully!")
                return data 
        except json.JSONDecodeError: 
            print("Error: The file is not a valid JSON file") 
            exit()

# Function to initialize dictionaries
def initialize_dictionaries(data):
    participants = {}
    words_dict = {}
    total_date_dict = {}
    total_time_dict = {}
    char_count_dict = {}
    word_count_dict = {}
    person_word_Dict = {}

    # Analyze only messages and initialize
    for i in data.get('messages', []):
        if i.get('type') == 'message':
            from_person = i.get('from', 'Unknown')
            if from_person not in participants:
                participants[from_person] = 0
                char_count_dict[from_person] = 0
                word_count_dict[from_person] = 0
                person_word_Dict[from_person] = {}

            # Get date and time
            date_str = i.get('date', '')[0:10]
            time_str = i.get('date', '')[11:13]

            if date_str:
                total_date_dict[date_str] = total_date_dict.get(date_str, 0) + 1
            if time_str:
                total_time_dict[time_str] = total_time_dict.get(time_str, 0) + 1

            participants[from_person] += 1

            # Word count calc
            text = i.get('text', '')
            if isinstance(text, str):
                for word in text.lower().split():
                    if len(word) > 3:  # Ignore short words
                        words_dict[word] = words_dict.get(word, 0) + 1
                        person_word_Dict[from_person][word] = person_word_Dict[from_person].get(word, 0) + 1

                char_count_dict[from_person] += len(text.replace(" ", ""))
                word_count_dict[from_person] += len(text.split())

    return participants, words_dict, total_date_dict, total_time_dict, char_count_dict, word_count_dict, person_word_Dict

# Function to calculate averages
def calculate_averages(participants, total_date_dict, word_count_dict, char_count_dict):
    totalmsgs = sum(participants.values())
    total_words = sum(word_count_dict.values())
    total_chars = sum(char_count_dict.values())

    avg_msg_len = total_chars / totalmsgs
    avg_word_len = total_words / totalmsgs
    avg_msgs_per_day = totalmsgs / len(total_date_dict)
    avg_words_per_day = total_words / len(total_date_dict)
    avg_chars_per_day = total_chars / len(total_date_dict)

    return avg_msg_len, avg_word_len, avg_msgs_per_day, avg_words_per_day, avg_chars_per_day

# Total messages
def get_total_messages(participants):
    return sum(participants.values())

# Total words
def get_total_words(word_count_dict):
    return sum(word_count_dict.values())

# Total characters
def get_total_characters(char_count_dict):
    return sum(char_count_dict.values())

# Save stats to txt file
def save_stats_to_file(participants, total_date_dict):
    with open("chat_stats.txt", "w") as f:
        f.write("Chat Statistics\n")
        f.write(f"Total Participants: {len(participants)}\n")
        f.write(f"Total Days Talked: {len(total_date_dict)}\n")
        for participant, count in participants.items():
            f.write(f"{participant}: {count} messages\n")

# Output most active dates
def display_most_active_dates(total_date_dict):
    sorted_dates = sorted(total_date_dict.items(), key=lambda x: x[1], reverse=True)[:3]
    print("Most Active Dates:")
    for date, count in sorted_dates:
        print(f"{date}: {count} messages")


# Get tkinter ready
root = tk.Tk()
root.title("Chat Stats")
root.geometry("800x500")
root.configure(bg="white")


data = load_json()
participants, words_dict, total_date_dict, total_time_dict, char_count_dict, word_count_dict, person_word_Dict = initialize_dictionaries(data)

# Stats per participant
participant_stats = [[participant, count] for participant, count in participants.items()]

# Top statistics section
stats_frame = Frame(root, bg="white")
stats_frame.pack(pady=10)

totalmsgs = get_total_messages(participants)
Label(stats_frame, text=f"Total messages:\n{totalmsgs}", font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2).grid(row=0, column=0, padx=5, pady=5)
Label(stats_frame, text=f"Total words:\n{get_total_words(word_count_dict)}", font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2).grid(row=0, column=1, padx=5, pady=5)
Label(stats_frame, text=f"Total characters:\n{get_total_characters(char_count_dict)}", font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2).grid(row=0, column=2, padx=5, pady=5)

# Days talked section
Label(root, text=f"{len(total_date_dict)} DAYS TALKED", font=("Arial", 16, "bold"), bg="red", fg="yellow", width=40, height=2).pack(pady=10)

# Most used words section
Label(root, text="-Most used words-", font=("Arial", 14, "bold"), bg="white").pack()
mostusedwordslist = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)[:5]

# Display if more than 5 words
if len(mostusedwordslist) >= 5:
    most_used_words_text = ", ".join(
        [f"{word} - {count}" for word, count in mostusedwordslist[:5]]
    )
else:
    most_used_words_text = "Not enough data to display most used words."

Label(root, text=most_used_words_text, font=("Arial", 12), bg="white").pack()

# Averages per day section
Label(root, text="-Averages per day-", font=("Arial", 14, "bold"), bg="white").pack(pady=5)

avg_frame = Frame(root, bg="white")
avg_frame.pack(pady=5)

avg_msg_len, avg_word_len, avg_msgs_per_day, avg_words_per_day, avg_chars_per_day = calculate_averages(participants, total_date_dict, word_count_dict, char_count_dict)

Label(avg_frame, text=f"Messages:\n{str(round(avg_msgs_per_day, 2))}", font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2).grid(row=0, column=0, padx=5, pady=5)
Label(avg_frame, text=f"Words:\n{str(round(avg_words_per_day, 2))}", font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2).grid(row=0, column=1, padx=5, pady=5)
Label(avg_frame, text=f"Characters:\n{str(round(avg_chars_per_day, 2))}", font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2).grid(row=0, column=2, padx=5, pady=5)

# Most active dates section
Label(root, text="-Most active dates and messages-", font=("Arial", 14, "bold"), bg="white").pack(pady=5)

active_frame = Frame(root, bg="white")
active_frame.pack(pady=5)

sorted_dates = sorted(total_date_dict.items(), key=lambda x: x[1], reverse=True)[:3]
for i, (date_str, msg_count) in enumerate(sorted_dates):
    Label(active_frame, text=f"{date_str}\n{msg_count} messages", font=("Arial", 14, "bold"), bg="lightgreen", width=20, height=2).grid(row=0, column=i, padx=5, pady=5)

# Open stats file
def open_stats_file():
    if os.path.exists("chat_stats.txt"):
        os.system("chat_stats.txt")
    else:
        messagebox.showerror("Error", "The file 'chat_stats.txt' does not exist")

# Button to open the stats file
btn_open_file = Button(root, text="Open Stats File", command=open_stats_file)
btn_open_file.pack(pady=20)

root.mainloop()