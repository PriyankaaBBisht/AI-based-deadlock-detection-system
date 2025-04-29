import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import pickle
import os
import matplotlib.pyplot as plt
import networkx as nx

from deadlock_detector import DeadlockDetector
from model_trainer import train_and_save_model

# Train model if not exists
if not os.path.exists("models/deadlock_predictor.pkl"):
    train_and_save_model()

model = pickle.load(open("models/deadlock_predictor.pkl", "rb"))
detector = DeadlockDetector()

# ---- Root Window Setup ----
root = tk.Tk()
root.title("AI-Powered Deadlock Detection System")
root.geometry("550x650")
root.configure(bg="#f0f8ff")

header = tk.Label(root, text="💻 AI-Deadlock Detection & Prediction", font=("Helvetica", 16, "bold"), bg="#f0f8ff")
header.pack(pady=15)

# ---- Manual Input Section ----
manual_frame = tk.LabelFrame(root, text="Manual System Metrics", bg="#f0f8ff", font=("Helvetica", 12, "bold"), padx=10, pady=10)
manual_frame.pack(padx=20, pady=10, fill="both")

entries = {}
fields = ["CPU Usage (%)", "Memory Usage (%)", "I/O Wait (%)", "Active Threads"]
for i, field in enumerate(fields):
    tk.Label(manual_frame, text=field, bg="#f0f8ff", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5)
    entry = tk.Entry(manual_frame, width=30)
    entry.grid(row=i, column=1, pady=5)
    entries[field] = entry

result_label = tk.Label(root, text="Prediction: ", font=("Helvetica", 12), bg="#f0f8ff")
result_label.pack(pady=10)

def predict_from_manual():
    try:
        values = [
            float(entries["CPU Usage (%)"].get()),
            float(entries["Memory Usage (%)"].get()),
            float(entries["I/O Wait (%)"].get()),
            int(entries["Active Threads"].get())
        ]
        df = pd.DataFrame([values], columns=['cpu', 'memory', 'io_wait', 'threads'])
        prediction = model.predict(df)[0]
        result = "⚠️ High Risk of Deadlock!" if prediction == 1 else "✅ System is Stable"
        result_label.config(text=f"Prediction: {result}")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

# ---- Button Functions ----
def predict_from_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        required_cols = {'cpu', 'memory', 'io_wait', 'threads'}
        if not required_cols.issubset(df.columns):
            messagebox.showerror("Format Error", "CSV must contain cpu, memory, io_wait, threads columns.")
            return
        predictions = model.predict(df[['cpu', 'memory', 'io_wait', 'threads']])
        df['prediction'] = predictions
        df.to_csv("data/predicted_output.csv", index=False)
        messagebox.showinfo("Success", "Predictions saved to data/predicted_output.csv")

def custom_rag_input():
    input_window = tk.Toplevel(root)
    input_window.title("Custom RAG Input")
    input_window.geometry("400x400")
    input_window.configure(bg="#e6f7ff")

    inputs = {
        "Processes (e.g., P1,P2)": tk.Entry(input_window),
        "Resources (e.g., R1,R2)": tk.Entry(input_window),
        "Requests (e.g., P1:R1,P2:R2)": tk.Entry(input_window),
        "Assignments (e.g., R1:P2,R2:P1)": tk.Entry(input_window)
    }

    for i, (label, entry) in enumerate(inputs.items()):
        tk.Label(input_window, text=label, bg="#e6f7ff", font=("Helvetica", 10)).pack(pady=4)
        entry.pack()

    def submit_custom_graph():
        detector.clear_graph()
        try:
            processes = [p.strip() for p in inputs["Processes (e.g., P1,P2)"].get().split(',')]
            resources = [r.strip() for r in inputs["Resources (e.g., R1,R2)"].get().split(',')]
            requests = [r.strip() for r in inputs["Requests (e.g., P1:R1,P2:R2)"].get().split(',') if r.strip()]
            assignments = [a.strip() for a in inputs["Assignments (e.g., R1:P2,R2:P1)"].get().split(',') if a.strip()]

            for p in processes:
                detector.add_process(p)
            for r in resources:
                detector.add_resource(r)
            for req in requests:
                p, r = req.split(':')
                detector.request_resource(p.strip(), r.strip())
            for a in assignments:
                r, p = a.split(':')
                detector.assign_resource(r.strip(), p.strip())

            cycle = detector.detect_deadlock()
            nx.draw(detector.rag, with_labels=True, node_color='lightgreen', node_size=1500)
            plt.title("Custom Resource Allocation Graph")
            plt.show()

            if cycle:
                detector.resolve_deadlock(cycle)
                messagebox.showwarning("Deadlock Detected", "Cycle found and resolved.")
            else:
                messagebox.showinfo("No Deadlock", "No cycle detected.")
            input_window.destroy()
        except Exception as e:
            messagebox.showerror("Input Error", f"Something went wrong:\n{e}")

    tk.Button(input_window, text="Simulate", command=submit_custom_graph, bg="#007acc", fg="white").pack(pady=15)

def simulate_rag():
    detector.clear_graph()
    detector.add_process("P1")
    detector.add_process("P2")
    detector.add_resource("R1")
    detector.add_resource("R2")

    detector.request_resource("P1", "R1")
    detector.assign_resource("R1", "P2")
    detector.request_resource("P2", "R2")
    detector.assign_resource("R2", "P1")

    cycle = detector.detect_deadlock()
    nx.draw(detector.rag, with_labels=True, node_color='skyblue', node_size=1500)
    plt.title("Resource Allocation Graph - Simulated Deadlock")
    plt.show()

    if cycle:
        detector.resolve_deadlock(cycle)
        messagebox.showwarning("Deadlock Resolved", "Deadlock resolved by terminating a process.")
    else:
        messagebox.showinfo("No Deadlock", "No deadlock detected.")

# ---- Action Buttons ----
btn_frame = tk.Frame(root, bg="#f0f8ff")
btn_frame.pack(pady=10)

buttons = [
    ("Predict (Manual Entry)", predict_from_manual, "#4CAF50"),
    ("Predict from CSV", predict_from_csv, "#FF9800"),
    ("Simulate RAG & Detect", simulate_rag, "#2196F3"),
    ("Custom RAG Input", custom_rag_input, "#673AB7"),
    ("Exit", root.quit, "#F44336")
]

for i, (text, command, color) in enumerate(buttons):
    tk.Button(btn_frame, text=text, command=command, width=25, bg=color, fg="white", font=("Helvetica", 10)).grid(row=i, column=0, pady=6)

root.mainloop()
