import os
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageDraw
import cv2
import ffmpeg
import sys

def resource_path(relative):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative)

FFMPEG_PATH = resource_path("ffmpeg/ffmpeg.exe")

class VideoObjectRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎥 Video Object Removal - Frame Accurate Edition")
        self.root.geometry("1024x800")
        self.root.configure(bg="#121212")

        self.video_path = None
        self.video_name = None
        self.frame_dir = None
        self.cleaned_dir = None
        self.mask_dir = None
        self.output_path = None
        self.output_dir = None
        self.original_fps = 25

        self.image = None
        self.display_image = None
        self.tk_image = None
        self.mask = None
        self.draw = None
        self.scale = 1.0
        self.brush_size = 15

        self.frame_files = []
        self.current_frame_index = 0
        self.buttons = []
        self.mode_var = tk.StringVar(value="single")

        self.build_ui()

    def build_ui(self):
        style = {"bg": "#1e1e1e", "fg": "#ffffff", "activebackground": "#333333", "activeforeground": "#00ffff"}

        toolbar = tk.Frame(self.root, bg="#1e1e1e")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        def styled_btn(text, cmd):
            btn = tk.Button(toolbar, text=text, command=cmd, **style)
            btn.pack(side=tk.LEFT, padx=4, pady=4)
            self.buttons.append(btn)

        styled_btn("📂 Load", self.load_video)
        styled_btn("⬅️ Prev", self.prev_frame)
        styled_btn("➡️ Next", self.next_frame)
        styled_btn("📅 Save Mask", self.save_current_mask)
        styled_btn("🧹 Remove Object", self.remove_object)
        styled_btn("🎞️ Rebuild Video", self.rebuild_video)
        styled_btn("▶️ Preview Output", self.preview_video)
        styled_btn("📅 Save As...", self.save_as_video)
        styled_btn("➕ Zoom In", self.zoom_in)
        styled_btn("➖ Zoom Out", self.zoom_out)
        styled_btn("ℹ️ About", self.show_about_info)


        mode_frame = tk.Frame(self.root, bg="#121212")
        mode_frame.pack(anchor="w", padx=10)
        tk.Radiobutton(mode_frame, text="Single Mask", variable=self.mode_var, value="single", bg="#121212", fg="#fff", selectcolor="#333").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Per-Frame Mask", variable=self.mode_var, value="framewise", bg="#121212", fg="#fff", selectcolor="#333").pack(side=tk.LEFT)

        self.status = tk.Label(self.root, text="Ready", fg="lightgreen", bg="#121212")
        self.status.pack(side=tk.TOP, anchor="w", padx=10)

        self.canvas = tk.Canvas(self.root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<B1-Motion>", self.paint)

        brush_slider_frame = tk.Frame(self.root, bg="#121212")
        brush_slider_frame.pack(fill=tk.X, pady=5)
        tk.Label(brush_slider_frame, text="Brush Size", bg="#121212", fg="white").pack(side=tk.LEFT, padx=5)
        self.brush_slider = tk.Scale(brush_slider_frame, from_=5, to=50, orient=tk.HORIZONTAL, bg="#1e1e1e", fg="white")
        self.brush_slider.set(self.brush_size)
        self.brush_slider.pack(side=tk.LEFT)

        zoom_frame = tk.Frame(self.root, bg="#121212")
        zoom_frame.pack(pady=4)
        tk.Button(zoom_frame, text="+ Zoom In", command=self.zoom_in, bg="#222", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(zoom_frame, text="- Zoom Out", command=self.zoom_out, bg="#222", fg="white").pack(side=tk.LEFT)

        self.log_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10, bg="#1e1e1e", fg="#00ff00", insertbackground='white')
        self.log_text.pack(fill=tk.BOTH, expand=False, padx=10, pady=6)

        footer = tk.Label(self.root, text="© projectworlds.in", fg="#888", bg="#121212", anchor="center")
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=4)

    def show_about_info(self):
        about_win = tk.Toplevel(self.root)
        about_win.title("About")
        about_win.geometry("420x350")
        about_win.configure(bg="#1e1e1e")
        about_win.resizable(False, False)

        tk.Label(about_win, text="🎥 Video Object Removal Tool",
             font=("Helvetica", 15, "bold"), fg="#00ffcc", bg="#1e1e1e").pack(pady=(20, 5))

        tk.Label(about_win, text="Version 1.0",
             font=("Helvetica", 10), fg="white", bg="#1e1e1e").pack()

        tk.Label(about_win, text="Developed by: Project Worlds",
             font=("Helvetica", 10), fg="#aaaaaa", bg="#1e1e1e").pack(pady=(10, 5))

        tk.Label(about_win, text="📺 YouTube: youtube.com/@projectworlds",
             font=("Helvetica", 10, "italic"), fg="#00bfff", bg="#1e1e1e").pack()

        tk.Label(about_win, text="🌐 Website: https://projectworlds.in",
             font=("Helvetica", 10, "italic"), fg="#00bfff", bg="#1e1e1e").pack()

        tk.Label(about_win, text="📧 Email: support@projectworlds.in",
             font=("Helvetica", 10, "italic"), fg="#00bfff", bg="#1e1e1e").pack()

        tk.Label(about_win,
             text="\nThis tool allows frame-accurate object removal\nusing brush-based masking and AI inpainting.\n\nPerfect for content creators and video editors.",
             font=("Helvetica", 10), fg="#cccccc", bg="#1e1e1e", justify="center").pack(pady=10)

        tk.Button(about_win, text="Close", command=about_win.destroy,
              bg="#333333", fg="white", font=("Helvetica", 10)).pack(pady=10)




    def append_log(self, msg):
        self.log_text.after(0, lambda: (
            self.log_text.insert(tk.END, msg + "\n"),
            self.log_text.see(tk.END)
        ))

    def set_status(self, text):
        self.status.after(0, lambda: self.status.config(text=text))

    def set_buttons_state(self, state):
        for btn in self.buttons:
            btn.config(state=state)

    def zoom_in(self):
        self.scale *= 1.1
        self.load_frame_by_index()

    def zoom_out(self):
        self.scale /= 1.1
        self.load_frame_by_index()

    def get_video_fps(self, path):
        try:
            probe = ffmpeg.probe(path)
            fps_str = probe["streams"][0]["r_frame_rate"]
            num, den = map(int, fps_str.split("/"))
            return round(num / den, 2)
        except:
            return 25

    def load_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if not file_path:
            return

        def worker():
            self.set_buttons_state("disabled")
            base = os.path.splitext(os.path.basename(file_path))[0]
            uid = base
            i = 1
            while os.path.exists(f"frames/{uid}"):
                uid = f"{base}_{i}"
                i += 1
            self.video_name = uid

            self.video_path = file_path
            self.frame_dir = f"frames/{uid}"
            self.cleaned_dir = f"cleaned_frames/{uid}"
            self.mask_dir = f"masks/{uid}"
            self.output_dir = f"output/{uid}"
            self.output_path = f"output/{uid}/output_clean_{uid}.mp4"
            self.original_fps = self.get_video_fps(file_path)
            self.scale = 1.0

            os.makedirs(self.frame_dir, exist_ok=True)
            os.makedirs(self.cleaned_dir, exist_ok=True)
            os.makedirs(self.mask_dir, exist_ok=True)
            os.makedirs(self.output_dir, exist_ok=True)

            self.set_status("🟡 Extracting frames...")
            self.append_log(f"🔍 Extracting frames from {file_path}")

            cmd = [
                FFMPEG_PATH,
                "-i", self.video_path,
                "-qscale:v", "1",
                os.path.join(self.frame_dir, "frame_%04d.png")
            ]
            try:
                subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                self.append_log(f"❌ Frame extraction failed: {e}")
                messagebox.showerror("Error", str(e))
                self.set_buttons_state("normal")
                return

            self.frame_files = sorted(f for f in os.listdir(self.frame_dir) if f.endswith(".png"))
            total = len(self.frame_files)

            if total == 0:
                self.append_log("❌ No frames extracted.")
                self.set_status("❌ No frames found.")
                self.set_buttons_state("normal")
                return

            for idx, fname in enumerate(self.frame_files, 1):
                self.append_log(f"[{idx}/{total}] ✅ Loaded: {fname}")

            self.current_frame_index = 0
            self.load_frame_by_index()
            self.set_buttons_state("normal")
            self.set_status(f"✅ {total} frames loaded.")

        threading.Thread(target=worker).start()


    def load_frame_by_index(self):
        if not self.frame_files:
            return

        frame_file = self.frame_files[self.current_frame_index]
        img = Image.open(os.path.join(self.frame_dir, frame_file)).convert("RGB")

        w, h = img.size
        if self.scale == 1.0:
            max_w, max_h = 950, 600
            self.scale = min(1.0, max_w / w, max_h / h)

        disp = img.resize((int(w * self.scale), int(h * self.scale)))

        self.image = img
        self.display_image = disp
        self.tk_image = ImageTk.PhotoImage(disp)

        self.canvas.delete("all")
        self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        mask_path = os.path.join(self.mask_dir, f"mask_{frame_file}")
        if os.path.exists(mask_path):
            self.mask = Image.open(mask_path).convert("L")
        else:
            self.mask = Image.new("L", img.size, 0)

        self.draw = ImageDraw.Draw(self.mask)
        self.set_status(f"🖼️ {frame_file} ({self.current_frame_index+1}/{len(self.frame_files)})")

    def paint(self, event):
        if not self.draw:
            return
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)
        r = self.brush_slider.get()
        self.draw.ellipse([x - r, y - r, x + r, y + r], fill=255)
        self.canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, outline="red")

    def prev_frame(self):
        self.save_current_mask()
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.load_frame_by_index()

    def next_frame(self):
        self.save_current_mask()
        if self.current_frame_index < len(self.frame_files) - 1:
            self.current_frame_index += 1
            self.load_frame_by_index()

    def save_current_mask(self):
        if not self.frame_files or not self.mask:
            return
        mask_path = os.path.join(self.mask_dir, f"mask_{self.frame_files[self.current_frame_index]}")
        self.mask.save(mask_path)
        self.set_status("Mask saved.")

    def remove_object(self):
        if not self.frame_files:
            return

        def worker():
            self.set_buttons_state("disabled")
            self.set_status("🧠 Removing objects...")
            self.append_log("🧠 Starting object removal...")

            cleaned, skipped = 0, 0
            total = len(self.frame_files)

            for idx, fname in enumerate(self.frame_files, 1):
                frame_path = os.path.join(self.frame_dir, fname)
                output_path = os.path.join(self.cleaned_dir, fname)
                mask_name = f"mask_{self.frame_files[self.current_frame_index]}" if self.mode_var.get() == "single" else f"mask_{fname}"
                mask_path = os.path.join(self.mask_dir, mask_name)

                frame = cv2.imread(frame_path)
                if frame is None:
                    self.append_log(f"[{idx}/{total}] ⚠️ Cannot read {fname}")
                    skipped += 1
                    continue

                if not os.path.exists(mask_path):
                    cv2.imwrite(output_path, frame)
                    self.append_log(f"[{idx}/{total}] 🟡 No mask: {fname}")
                    skipped += 1
                    continue

                mask = cv2.imread(mask_path, 0)
                if mask is None or not cv2.countNonZero(mask):
                    cv2.imwrite(output_path, frame)
                    self.append_log(f"[{idx}/{total}] ⚪ Empty mask: {fname}")
                    skipped += 1
                    continue

                mask = cv2.GaussianBlur(mask, (5, 5), 2)
                result = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
                cv2.imwrite(output_path, result)
                self.append_log(f"[{idx}/{total}] ✅ Cleaned: {fname}")
                cleaned += 1

            self.append_log(f"\n✅ Done. {cleaned} cleaned, {skipped} skipped.")
            self.set_status(f"✅ Done: {cleaned} cleaned, {skipped} skipped.")
            self.set_buttons_state("normal")

        threading.Thread(target=worker).start()

    def rebuild_video(self):
        def worker():
            self.set_buttons_state("disabled")
            self.set_status("🔄 Rebuilding video...")
            self.append_log("🔄 Rebuilding video from cleaned frames...")

            total_frames = len([f for f in os.listdir(self.cleaned_dir) if f.endswith(".png")])
            if total_frames == 0:
                self.append_log("❌ No cleaned frames found.")
                self.set_status("❌ Failed: No cleaned frames.")
                self.set_buttons_state("normal")
                return

            self.append_log(f"🔢 Total cleaned frames: {total_frames}")
            self.append_log("⚙️ Encoding video... (this may take a few seconds)")

            cmd = [
                FFMPEG_PATH,
                "-framerate", str(self.original_fps),
                "-i", os.path.join(self.cleaned_dir, "frame_%04d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-y", self.output_path
            ]
            try:
                # FFmpeg runs as hidden process
                subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_log("✅ Video rebuilt successfully.")
                self.set_status("🎉 Video ready!")

                # Simulated progress output
                for i in range(1, total_frames + 1):
                    self.append_log(f"[{i}/{total_frames}] 🧱 Frame encoded")
                    self.root.update_idletasks()

            except Exception as e:
                self.append_log(f"❌ Video rebuild failed: {e}")
                self.set_status("❌ Failed.")
                messagebox.showerror("FFmpeg Error", str(e))

            self.set_buttons_state("normal")

        threading.Thread(target=worker).start()


    def preview_video(self):
        if self.output_path and os.path.exists(self.output_path):
            os.startfile(os.path.abspath(self.output_path))
        else:
            messagebox.showerror("Error",
                                 f"Output file not found:\n{os.path.abspath(self.output_path)}\nPlease rebuild video first.")
            self.set_status(f"❌ Preview failed. File not found: {os.path.abspath(self.output_path)}")

    def save_as_video(self):
        new_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if new_path:
            try:
                os.replace(self.output_path, new_path)
                self.set_status(f"✅ Saved as {new_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoObjectRemoverApp(root)
    root.mainloop()
