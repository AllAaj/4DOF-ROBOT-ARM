import tkinter as tk
import serial
import threading
import time


class RobotArmGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("4 DOF Robot Arm Control")
        self.root.geometry("400x600")
        self.root.configure(bg="#f0f0f0")

        try:
            self.serial_port = serial.Serial('COM19', 9600, timeout=1)
            time.sleep(2)
        except:
            self.serial_port = None
            print("Serial port connection failed")

        # Title
        tk.Label(root, text="🎛 Robot Arm Control", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

        # Sliders for setting target angles
        self.frame_sliders = tk.LabelFrame(root, text="Set Joint Angles", bg="#ffffff", font=("Arial", 10, "bold"))
        self.frame_sliders.pack(padx=20, pady=10, fill="both")

        self.sliders = {}
        axes_info = {
            "Base": (-135, 135),
            "Épaule": (0, 90),
            "Coude": (0, 236),
            "Poignet": (-10, 100)
        }

        for nom, (min_deg, max_deg) in axes_info.items():
            frame = tk.Frame(self.frame_sliders, bg="#ffffff")
            frame.pack(pady=5)
            tk.Label(frame, text=nom, width=10, anchor="w", bg="#ffffff").pack(side=tk.LEFT)
            slider = tk.Scale(frame, from_=min_deg, to=max_deg, orient=tk.HORIZONTAL, length=200, resolution=1,
                              bg="#e6f2ff")
            slider.set(0)
            slider.pack(side=tk.LEFT)
            self.sliders[nom] = slider

        tk.Button(self.frame_sliders, text="Set Angles", width=15, bg="#ccf2ff",
                  command=self.send_slider_positions).pack(pady=5)

        # Position display
        self.frame_positions = tk.LabelFrame(root, text="Current Position", bg="#ffffff", font=("Arial", 10, "bold"))
        self.frame_positions.pack(padx=20, pady=10, fill="both")

        self.labels_position = {}
        for nom in ["Base", "Épaule", "Coude", "Poignet"]:
            frame = tk.Frame(self.frame_positions, bg="#ffffff")
            frame.pack(pady=3)
            tk.Label(frame, text=f"{nom}:", width=10, anchor="w", bg="#ffffff").pack(side=tk.LEFT)
            val_label = tk.Label(frame, text="---", fg="#0000aa", bg="#ffffff", font=("Arial", 10, "bold"))
            val_label.pack(side=tk.LEFT)
            self.labels_position[nom] = val_label

        # Gripper controls
        self.frame_gripper = tk.LabelFrame(root, text="Gripper Control", bg="#ffffff", font=("Arial", 10, "bold"))
        self.frame_gripper.pack(padx=20, pady=10, fill="both")

        tk.Button(self.frame_gripper, text="Open Gripper", bg="#ccffcc", width=15,
                  command=lambda: self.send_command("P+")).pack(pady=5)
        tk.Button(self.frame_gripper, text="Close Gripper", bg="#ffcccc", width=15,
                  command=lambda: self.send_command("P-")).pack(pady=5)

        # Record and Go controls
        self.frame_record = tk.LabelFrame(root, text="Record and Playback", bg="#ffffff", font=("Arial", 10, "bold"))
        self.frame_record.pack(padx=20, pady=10, fill="both")

        tk.Button(self.frame_record, text="📍 Record Position", width=15, bg="#ffffcc",
                  command=lambda: self.send_command("RECORD")).pack(pady=5)
        tk.Button(self.frame_record, text="➡ Go to Positions", width=15, bg="#ccffcc",
                  command=lambda: self.send_command("GO")).pack(pady=5)
        tk.Button(self.frame_record, text="⏹ Stop", width=15, bg="#ffd6cc",
                  command=lambda: self.send_command("STOP")).pack(pady=5)

        # Status
        self.label_status = tk.Label(root, text="Status: Idle", bg="#f0f0f0", font=("Arial", 10))
        self.label_status.pack(pady=10)

        # Start serial reading thread
        self.thread = threading.Thread(target=self.read_serial, daemon=True)
        self.thread.start()

    def send_slider_positions(self):
        if self.serial_port and self.serial_port.is_open:
            values = [str(self.sliders[nom].get()) for nom in ["Base", "Épaule", "Coude", "Poignet"]]
            cmd = "SET:" + ",".join(values)
            self.serial_port.write((cmd + '\n').encode())
            print(f"Sent: {cmd}")

    def send_command(self, cmd):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write((cmd + '\n').encode())
            print(f"Sent: {cmd}")

    def read_serial(self):
        while True:
            if self.serial_port and self.serial_port.in_waiting:
                line = self.serial_port.readline().decode(errors='ignore').strip()
                if line.startswith("POS:"):
                    try:
                        angles = line[4:].split(',')
                        if len(angles) == 4:
                            for i, nom in enumerate(["Base", "Épaule", "Coude", "Poignet"]):
                                self.labels_position[nom].config(text=f"{float(angles[i]):.1f}°")
                    except Exception as e:
                        print(f"Parsing error: {e}")
                elif line.startswith("ACK:"):
                    self.label_status.config(text=f"Status: {line[4:]}")
                print(line)
            time.sleep(0.1)

    def close(self):
        if self.serial_port:
            self.serial_port.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RobotArmGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()