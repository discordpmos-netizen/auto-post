import argparse
import os
import shutil
import time
from pathlib import Path

from openai import OpenAI
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

CRAYO_URL = "https://app.crayo.ai/"
YOUTUBE_UPLOAD_URL = "https://studio.youtube.com/channel/UC/videos/upload"
DEFAULT_EXPORT_DIR = r"C:\Users\DR_LE\OneDrive\Desktop\Ai videos\finished_no need to edit"


class AutomationError(RuntimeError):
    pass


def generate_reddit_story_script(client: OpenAI, model: str) -> str:
    prompt = (
        "Write a compelling Reddit-style story script for a vertical short video. "
        "Duration target: 1 minute 15 seconds when read aloud (about 190-220 words). "
        "Tone: dramatic hook, fast pacing, clean language, satisfying ending. "
        "Return plain text script only with no markdown."
    )

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ],
    )
    return response.output_text.strip()


def wait_and_click(page, selector: str, timeout: int = 20000):
    page.locator(selector).first.wait_for(state="visible", timeout=timeout)
    page.locator(selector).first.click()


def click_button_by_text(page, text: str, timeout: int = 20000):
    page.get_by_role("button", name=text, exact=False).first.wait_for(
        state="visible", timeout=timeout
    )
    page.get_by_role("button", name=text, exact=False).first.click()


def run_crayo_flow(page, script_text: str):
    page.goto(CRAYO_URL, wait_until="domcontentloaded")

    # Paste/copy the generated script into Crayo's script input.
    prompt_box = page.locator("textarea, [contenteditable='true']").first
    prompt_box.wait_for(state="visible", timeout=30000)
    prompt_box.click()
    prompt_box.fill(script_text)

    # Press next (top right) twice.
    click_button_by_text(page, "Next")
    click_button_by_text(page, "Next")

    # Select soap video background.
    page.get_by_text("Soap", exact=False).first.click(timeout=20000)

    # Press next.
    click_button_by_text(page, "Next")

    # Select Natasha voice for intro and script voice.
    page.get_by_text("Natasha", exact=False).first.click(timeout=20000)
    # If there is a separate script voice dropdown/section.
    natasha_candidates = page.get_by_text("Natasha", exact=False)
    if natasha_candidates.count() > 1:
        natasha_candidates.nth(1).click()

    # Disable background music if enabled.
    music_toggle = page.locator("label:has-text('Background Music') input[type='checkbox']")
    if music_toggle.count() > 0 and music_toggle.first.is_checked():
        music_toggle.first.click()

    # Generate.
    click_button_by_text(page, "Generate", timeout=30000)


def export_from_crayo(page, download_dir: Path, final_export_dir: Path):
    final_export_dir.mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)

    with page.expect_download(timeout=120000) as download_info:
        click_button_by_text(page, "Export", timeout=120000)

    download = download_info.value
    filename = download.suggested_filename
    source = download_dir / filename
    download.save_as(str(source))

    destination = final_export_dir / filename
    shutil.copy2(source, destination)
    return destination


def upload_to_youtube(page, video_path: Path, title: str, description: str = ""):
    page.goto(YOUTUBE_UPLOAD_URL, wait_until="domcontentloaded")

    file_input = page.locator("input[type='file']")
    file_input.first.wait_for(state="attached", timeout=30000)
    file_input.first.set_input_files(str(video_path))

    title_box = page.locator("#textbox").nth(0)
    title_box.fill(title)

    if description:
        description_box = page.locator("#textbox").nth(1)
        description_box.fill(description)

    # Move through YouTube upload wizard and publish.
    for _ in range(3):
        click_button_by_text(page, "Next", timeout=45000)

    click_button_by_text(page, "Public", timeout=45000)
    click_button_by_text(page, "Publish", timeout=45000)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Reddit story with ChatGPT, produce it in Crayo, and upload to YouTube."
    )
    parser.add_argument("--openai-model", default="gpt-4o-mini")
    parser.add_argument("--profile-dir", default=".playwright_profile")
    parser.add_argument("--download-dir", default="downloads")
    parser.add_argument("--export-dir", default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--video-title", default="Reddit Story You Won't Believe")
    parser.add_argument("--video-description", default="")
    args = parser.parse_args()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise AutomationError("OPENAI_API_KEY is required.")

    client = OpenAI(api_key=openai_api_key)
    script_text = generate_reddit_story_script(client, args.openai_model)

    profile_dir = Path(args.profile_dir).resolve()
    download_dir = Path(args.download_dir).resolve()
    export_dir = Path(args.export_dir)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            accept_downloads=True,
            downloads_path=str(download_dir),
        )
        page = context.new_page()

        try:
            run_crayo_flow(page, script_text)
            video_path = export_from_crayo(page, download_dir, export_dir)
            upload_to_youtube(page, video_path, args.video_title, args.video_description)
        except PlaywrightTimeoutError as exc:
            raise AutomationError(
                "A required page element did not load in time. "
                "You may need to log in to Crayo or YouTube in the persistent browser profile first."
            ) from exc
        finally:
            context.close()


if __name__ == "__main__":
    main()
