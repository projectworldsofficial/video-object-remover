# 📘 User Manual: Video Object Remover (EXE Version)

Welcome to the official user manual for **Video Object Remover – Frame Accurate Edition (EXE version)**.  
This guide will help you get started, walk through each feature, and explain the workflow step-by-step.

---

## 📥 Step 1: Download & Launch the Tool

1. Visit the [Releases](https://github.com/your-username/video-object-remover/releases) section on GitHub or SourceForge.
2. Download `VideoObjectRemover.exe`.
3. Double-click to run (no installation or setup required).

> 🟢 No Python or external libraries needed. Everything is pre-packaged.

---

## 🎥 Step 2: Load a Video

1. Click the **📂 Load** button in the top toolbar.
2. Select an `.mp4` video from your computer.
3. The app will extract all frames using FFmpeg (you’ll see progress in the log area).
4. Once done, frames will appear in the preview area.

> ✔️ Progress and status are shown at the bottom and in the green log console.

---

## 🖌️ Step 3: Create a Mask

1. Use your **mouse to draw** over the object you want to remove.
2. Adjust the brush size using the **slider** at the bottom.
3. Two modes available:
   - **Single Mask** (applies same mask to all frames)
   - **Per-Frame Mask** (different mask per frame)
4. Use **➡️ Next** and **⬅️ Prev** to navigate between frames.

> 📝 You’ll see red circles indicating the masked areas.

---

## 💾 Step 4: Save the Mask

1. Click **📅 Save Mask** to save the drawn mask for the current frame.
2. You must save masks before switching frames or applying object removal.

---

## 🧠 Step 5: Remove the Object

1. Click **🧹 Remove Object**
2. The tool will process all frames using OpenCV's inpainting algorithm.
3. Progress will appear in the console below.
4. Cleaned frames are saved internally.

---

## 🎞️ Step 6: Rebuild the Video

1. Click **🎞️ Rebuild Video**
2. FFmpeg will convert cleaned frames back into a video with original FPS.
3. Final video will be saved in the `output/` folder.

> 🥳 You’ll see confirmation when the video is rebuilt successfully.

---

## ▶️ Step 7: Preview or Save Final Output

- Click **▶️ Preview Output** to open the video in your default player.
- Click **📅 Save As...** to export the cleaned video to a custom path.

---

## 🔍 Zoom Controls

- **➕ Zoom In** and **➖ Zoom Out** to better paint fine details.
- Image will rescale automatically.

---

## 📢 About & Credits

Click **ℹ️ About** for credits and links:

- Developed by **Project Worlds**
- Website: [https://projectworlds.in](https://projectworlds.in)
- YouTube: [youtube.com/@projectworlds](https://youtube.com/@projectworlds)

---

## 🗂 Output Folder Structure

After using the app, these folders are created:

