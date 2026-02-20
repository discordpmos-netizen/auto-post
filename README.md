# Crayo + ChatGPT to YouTube Automation

This script automates the workflow you requested:

1. Uses ChatGPT (OpenAI API) to create a ~1:15 Reddit story script.
2. Opens Crayo AI and inserts the script.
3. Clicks **Next** twice.
4. Selects **Soap** video background.
5. Clicks **Next**.
6. Selects **Natasha** voice for intro and script voice.
7. Disables background music.
8. Clicks **Generate**.
9. Exports the video to:
   `C:\Users\DR_LE\OneDrive\Desktop\Ai videos\finished_no need to edit`
10. Uploads and publishes the file on YouTube.

## Download / run (Windows, step-by-step)

1. **Download this project**
   - If you use Git:
     ```powershell
     git clone <your-repo-url>
     cd auto-post
     ```
   - Or click **Code > Download ZIP**, then extract it and open a terminal in that folder.

2. **Create and activate a virtual environment**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**

   ```powershell
   pip install -r requirements.txt
   py -m playwright install chromium
   ```

4. **Set your OpenAI API key**

   ```powershell
   $env:OPENAI_API_KEY="your_key_here"
   ```

5. **Run the script**

   ```powershell
   py automate_crayo_to_youtube.py
   ```

6. **First run behavior**
   - A browser opens.
   - If not already logged in, sign into Crayo and YouTube in that window.
   - The script continues once pages/elements are available.

## Setup (cross-platform quick commands)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

Set your API key:

```bash
export OPENAI_API_KEY="your_key_here"   # Windows PowerShell: $env:OPENAI_API_KEY="your_key_here"
```

## Run

```bash
python automate_crayo_to_youtube.py
```

Optional arguments:

- `--openai-model` (default: `gpt-4o-mini`)
- `--profile-dir` Playwright profile path (stores logins)
- `--download-dir` temp download folder
- `--export-dir` final export path
- `--video-title`
- `--video-description`

Example:

```powershell
py automate_crayo_to_youtube.py --video-title "Crazy Reddit Story #shorts"
```

## Important notes

- On first run, you may need to manually log into Crayo and YouTube in the opened browser window.
- UI selectors can change on Crayo/YouTube; if they do, update selectors in `automate_crayo_to_youtube.py`.
- Keep the browser visible while automation runs (`headless=False`).
