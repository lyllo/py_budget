import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import subprocess
import sys
import os
import threading

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PATH_TO_MAIN_FILE = os.path.join(ROOT_DIR, 'src/config.py')
PATH_TO_AGENT_FILE = os.path.join(ROOT_DIR, 'src/agent.py')

process = None

def submit():
    global process
    selected_preset = radio_var.get()
    output_text.insert(tk.END, f"Selected Preset: {selected_preset}\n")
    output_text.see(tk.END)  # Auto-scroll to the latest entry

    # Set the PRESET environment variable
    os.environ['PRESET'] = selected_preset

    # Execute config.py and capture the output in a separate thread
    process = subprocess.Popen([sys.executable, PATH_TO_MAIN_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    threading.Thread(target=read_output, args=(process, output_text)).start()

def read_output(process, output_widget):
    def check_output():
        while True:
            line = process.stdout.readline()
            if not line:
                break
            output_widget.insert(tk.END, line)
            output_widget.see(tk.END)
        while True:
            line = process.stderr.readline()
            if not line:
                break
            output_widget.insert(tk.END, line)
            output_widget.see(tk.END)
        process.stdout.close()
        process.stderr.close()
        process.wait()
    threading.Thread(target=check_output).start()

def cancel():
    global process
    if process:
        process.terminate()
        output_text.insert(tk.END, "Process terminated.\n")
        output_text.see(tk.END)
        process = None

def submit_agent():
    global process
    agent_output_text.insert(tk.END, "Running agent.py...\n")
    agent_output_text.see(tk.END)  # Auto-scroll to the latest entry

    # Execute agent.py and capture the output in a separate thread
    process = subprocess.Popen([sys.executable, PATH_TO_AGENT_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
    threading.Thread(target=read_output, args=(process, agent_output_text)).start()

def send_command():
    global process
    command = agent_input_text.get("1.0", tk.END).strip()
    if process and command:
        process.stdin.write(command + '\n')
        process.stdin.flush()
        agent_input_text.delete("1.0", tk.END)

def cancel_agent():
    global process
    if process:
        process.terminate()
        agent_output_text.insert(tk.END, "Agent process terminated.\n")
        agent_output_text.see(tk.END)
        process = None

# Create the main window
root = tk.Tk()
root.title("py_budget")
root.geometry("640x480")

# Create a Notebook widget
notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create frames for each tab
frame1 = ttk.Frame(notebook)
frame2 = ttk.Frame(notebook)

# Add frames to the notebook
notebook.add(frame1, text="Config")
notebook.add(frame2, text="Agent")

# Variable to store selected radio button value
radio_var = tk.StringVar(value="read_datasources")

# Create radio buttons in the first tab
radio1 = tk.Radiobutton(frame1, text="Read Datasources", variable=radio_var, value="read_datasources")
radio2 = tk.Radiobutton(frame1, text="Update Database", variable=radio_var, value="update_database")
radio3 = tk.Radiobutton(frame1, text="Dump Database", variable=radio_var, value="dump_database")

# Submit button in the first tab
submit_button = tk.Button(frame1, text="Submit", command=submit)

# Cancel button in the first tab
cancel_button = tk.Button(frame1, text="Cancel", command=cancel)

# Output text area in the first tab
output_text = scrolledtext.ScrolledText(frame1, width=50, height=10, wrap=tk.WORD)

# Layout for the first tab
radio1.pack(anchor=tk.W)
radio2.pack(anchor=tk.W)
radio3.pack(anchor=tk.W)
submit_button.pack(pady=10)
cancel_button.pack(pady=10)
output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Submit button in the second tab
submit_agent_button = tk.Button(frame2, text="Run Agent", command=submit_agent)

# Cancel button in the second tab
cancel_agent_button = tk.Button(frame2, text="Cancel Agent", command=cancel_agent)

# Output text area in the second tab
agent_output_text = scrolledtext.ScrolledText(frame2, width=50, height=10, wrap=tk.WORD)

# Input text area in the second tab
agent_input_text = tk.Text(frame2, height=3, wrap=tk.WORD)

# Send command button in the second tab
send_command_button = tk.Button(frame2, text="Send Command", command=send_command)

# Layout for the second tab
submit_agent_button.pack(pady=10)
cancel_agent_button.pack(pady=10)
agent_output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
agent_input_text.pack(padx=10, pady=10, fill=tk.X)
send_command_button.pack(pady=10)

# Run the application
root.mainloop()