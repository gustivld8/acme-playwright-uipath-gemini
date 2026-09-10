# ACME System 1 Data Scraper & AI Summarizer

Automation pipeline using Playwright, UiPath REFramework, and Google Gemini API.

## Architecture & Workflow
1. **Dispatcher (Python + Playwright)**: Scrapes "Open" work items from ACME System 1 dynamically in the background and populates the UiPath Orchestrator Queue.
2. **Performer (UiPath REFramework)**: Fetches queue items, calls Gemini API (`gemini-1.5-flash`) to generate concise one-sentence summaries, and logs the output into Google Sheets.
3. **Rate Limit Handling**: Implemented custom throttling (delay mechanisms) to respect Gemini Free Tier limits (RPM/RPD).

## Tech Stack
- Python (Playwright)
- UiPath Studio (REFramework, VB.NET Integration)
- Google Gemini API (`gemini-1.5-flash`)
- Google Sheets API
