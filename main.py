import json
import os
import tkinter as tk
from tkinter import Label, Button, Frame, messagebox, filedialog


file_path = filedialog.askopenfilename(title="Select Telegram JSON file to analyze")

if not file_path or not file_path.endswith(".json"):
    print("Error: Please select a valid JSON file")
    exit()


def load_json():
    try:
        with open(file_path, 'r', encoding="utf8") as f:
            data = json.load(f)
            print("JSON file read successfully!")
            return data
    except json.JSONDecodeError:
        print("Error: The file is not a valid JSON file")
        exit()

# Initialize libraries
def initialize_dictionaries(data):
    participants      = {}
    words_dict        = {}
    total_date_dict   = {}
    total_time_dict   = {}
    char_count_dict   = {}
    word_count_dict   = {}
    person_word_dict  = {}
    person_date_dict  = {}

    for i in data.get('messages', []):
        if i.get('type') != 'message':
            continue

        from_person = i.get('from', 'Unknown')

        # New person
        if from_person not in participants:
            participants[from_person]     = 0
            char_count_dict[from_person]  = 0
            word_count_dict[from_person]  = 0
            person_word_dict[from_person] = {}
            person_date_dict[from_person] = {}

        date_str = i.get('date', '')[0:10]
        time_str = i.get('date', '')[11:13]

        if date_str:
            total_date_dict[date_str] = total_date_dict.get(date_str, 0) + 1
            person_date_dict[from_person][date_str] = \
                person_date_dict[from_person].get(date_str, 0) + 1
        if time_str:
            total_time_dict[time_str] = total_time_dict.get(time_str, 0) + 1

        participants[from_person] += 1

        text = i.get('text', '')
        if isinstance(text, list):
            text = " ".join(
                seg if isinstance(seg, str) else seg.get('text', '')
                for seg in text
            )

        if isinstance(text, str):
            for word in text.lower().split():
                if len(word) > 3:
                    words_dict[word] = words_dict.get(word, 0) + 1
                    person_word_dict[from_person][word] = \
                        person_word_dict[from_person].get(word, 0) + 1

            char_count_dict[from_person] += len(text.replace(" ", ""))
            word_count_dict[from_person] += len(text.split())

    return (participants, words_dict, total_date_dict, total_time_dict,
            char_count_dict, word_count_dict, person_word_dict, person_date_dict)


# Get statistics
def get_total_messages(participants):
    return sum(participants.values())

def get_total_words(word_count_dict):
    return sum(word_count_dict.values())

def get_total_characters(char_count_dict):
    return sum(char_count_dict.values())

def calculate_averages(participants, total_date_dict, word_count_dict, char_count_dict):
    totalmsgs   = get_total_messages(participants)
    total_words = get_total_words(word_count_dict)
    total_chars = get_total_characters(char_count_dict)
    days        = len(total_date_dict) or 1

    avg_msg_len       = total_chars / totalmsgs  if totalmsgs else 0
    avg_word_len      = total_words / totalmsgs  if totalmsgs else 0
    avg_msgs_per_day  = totalmsgs   / days
    avg_words_per_day = total_words / days
    avg_chars_per_day = total_chars / days

    return avg_msg_len, avg_word_len, avg_msgs_per_day, avg_words_per_day, avg_chars_per_day


# Saving statistics to .txt file
def save_stats_to_file(participants, words_dict, total_date_dict, total_time_dict,
                        char_count_dict, word_count_dict, person_word_dict, person_date_dict):

    totalmsgs   = get_total_messages(participants)
    total_words = get_total_words(word_count_dict)
    total_chars = get_total_characters(char_count_dict)
    (avg_msg_len, avg_word_len,
     avg_msgs_per_day, avg_words_per_day, avg_chars_per_day) = \
        calculate_averages(participants, total_date_dict, word_count_dict, char_count_dict)

    SEP = "-" * 100 + "\n"

    with open("chat_stats.txt", "w", encoding="utf-8") as f:

        f.write("----:TELEGRAM CHAT STATS:----\n")
        f.write(f"Total Messages : {totalmsgs}\n")
        f.write(f"Total Words : {total_words}\n")
        f.write(f"Total Characters : {total_chars}\n")
        f.write(f"Total Days Talked : {len(total_date_dict)}\n")
        f.write(SEP)

        f.write("-: Most Used Words :-\n")
        top_words = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        for word, count in top_words:
            f.write(f"{word} - {count}\n")
        f.write(SEP)


        f.write("--: Averages :--\n")
        f.write("-: Average Message Length :-\n")
        f.write(f"{round(avg_msg_len, 2)} Characters\n")
        f.write(f"{round(avg_word_len, 2)} Words\n")
        f.write("-: Averages Per Day :-\n")
        f.write(f"{round(avg_msgs_per_day, 2)} Messages\n")
        f.write(f"{round(avg_words_per_day, 2)} Words\n")
        f.write(f"{round(avg_chars_per_day, 2)} Characters\n")
        f.write(SEP)



        f.write("-: Most Active Dates :-\n")
        sorted_dates = sorted(total_date_dict.items(), key=lambda x: x[1], reverse=True)[:5]

        for date_str, msg_count in sorted_dates:
            f.write(f"{date_str}: {msg_count} messages\n")
            day_senders = {
                person: counts[date_str]
                for person, counts in person_date_dict.items()
                if date_str in counts
            }
            for person, count in sorted(day_senders.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{person}: {count}\n")
            f.write("\n")
        f.write(SEP)



        f.write("--: Per Person Stats :--\n")

        f.write("-:Total Messages:-\n")
        for person, count in sorted(participants.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{person}: {count}\n")

        f.write("-:Total Words:-\n")
        for person, count in sorted(word_count_dict.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{person}: {count}\n")

        f.write("-:Total Characters:-\n")
        for person, count in sorted(char_count_dict.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{person}: {count}\n")




        f.write("-:Top 5 Words Per Person:-\n")
        for person, wdict in sorted(person_word_dict.items()):
            if not wdict:
                continue
            top5 = sorted(wdict.items(), key=lambda x: x[1], reverse=True)[:5]
            top5_str = ", ".join(f"{w} ({c})" for w, c in top5)
            f.write(f"{person}: {top5_str}\n")

        f.write(SEP)

    print("chat_stats.txt saved successfully!")



# Open stats file func

def open_stats_file():
    save_stats_to_file(participants, words_dict, total_date_dict, total_time_dict,
                       char_count_dict, word_count_dict, person_word_dict, person_date_dict)
    if os.path.exists("chat_stats.txt"):
        os.startfile("chat_stats.txt")
    else:
        messagebox.showerror("Error", "The file 'chat_stats.txt' does not exist")



data = load_json()
(participants, words_dict, total_date_dict, total_time_dict,
 char_count_dict, word_count_dict, person_word_dict, person_date_dict) = \
    initialize_dictionaries(data)

totalmsgs = get_total_messages(participants)
(avg_msg_len, avg_word_len,
 avg_msgs_per_day, avg_words_per_day, avg_chars_per_day) = \
    calculate_averages(participants, total_date_dict, word_count_dict, char_count_dict)



# Tkinter UI

root = tk.Tk()
root.title("Telegram Chat Stats")
root.geometry("820x560")
root.configure(bg="white")


stats_frame = Frame(root, bg="white")
stats_frame.pack(pady=10)

Label(stats_frame,
      text=f"Total messages:\n{totalmsgs}",
      font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2
      ).grid(row=0, column=0, padx=5, pady=5)

Label(stats_frame,
      text=f"Total words:\n{get_total_words(word_count_dict)}",
      font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2
      ).grid(row=0, column=1, padx=5, pady=5)

Label(stats_frame,
      text=f"Total characters:\n{get_total_characters(char_count_dict)}",
      font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2
      ).grid(row=0, column=2, padx=5, pady=5)


Label(root,
      text=f"{len(total_date_dict)} DAYS TALKED",
      font=("Arial", 16, "bold"), bg="red", fg="yellow", width=40, height=2
      ).pack(pady=10)


Label(root, text="-Most used words-", font=("Arial", 14, "bold"), bg="white").pack()
top_words = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)[:5]
if len(top_words) >= 5:
    Label(root,
          text=", ".join(f"{w} - {c}" for w, c in top_words),
          font=("Arial", 12), bg="white"
          ).pack()
else:
    Label(root, text="Not enough data to display most used words.",
          font=("Arial", 12), bg="white").pack()


Label(root, text="-Averages per day-", font=("Arial", 14, "bold"), bg="white").pack(pady=5)

avg_frame = Frame(root, bg="white")
avg_frame.pack(pady=5)

Label(avg_frame,
      text=f"Messages:\n{round(avg_msgs_per_day, 2)}",
      font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2
      ).grid(row=0, column=0, padx=5, pady=5)

Label(avg_frame,
      text=f"Words:\n{round(avg_words_per_day, 2)}",
      font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2
      ).grid(row=0, column=1, padx=5, pady=5)

Label(avg_frame,
      text=f"Characters:\n{round(avg_chars_per_day, 2)}",
      font=("Arial", 14, "bold"), bg="lightblue", width=20, height=2
      ).grid(row=0, column=2, padx=5, pady=5)


Label(root, text="-Most active dates and messages-",
      font=("Arial", 14, "bold"), bg="white").pack(pady=5)

active_frame = Frame(root, bg="white")
active_frame.pack(pady=5)

sorted_dates = sorted(total_date_dict.items(), key=lambda x: x[1], reverse=True)[:3]
for i, (date_str, msg_count) in enumerate(sorted_dates):
    Label(active_frame,
          text=f"{date_str}\n{msg_count} messages",
          font=("Arial", 14, "bold"), bg="lightgreen", width=20, height=2
          ).grid(row=0, column=i, padx=5, pady=5)


Button(root,
       text="Open Stats File",
       font=("Arial", 12, "bold"),
       bg="steelblue", fg="white",
       padx=10, pady=5,
       command=open_stats_file
       ).pack(pady=20)

root.mainloop()