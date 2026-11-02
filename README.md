# Notion Task Popup

A small Windows desktop helper for capturing a task without opening Notion. Press a hotkey, type a title and optional notes, and the task is added to your Notion database.

## Get it ready

### 1. Install Python and the app packages

Use Python 3.10 or newer. In PowerShell, open this project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Connect your Notion database

Create a Notion integration and copy its API key. Then share your task database with that integration so it can access the database.

This version expects the database to have:

- A title column named `Name`.
- A status column named `Status` with the type **Status**.
- A status option whose name matches the value you configure below, such as `To Do`.

Copy the example settings file and open your personal copy:

```powershell
Copy-Item .env.example .env
notepad .env
```

Fill in the three values:

```dotenv
NOTION_API_KEY=your-integration-secret
NOTION_DATABASE_ID=your-database-id
NOTION_STATUS_VALUE=To Do
```

`NOTION_STATUS_VALUE` must match an existing option in the database's `Status` column. The `.env` file is for your local settings and is excluded from Git; `.env.example` is safe to commit because it contains blank placeholders.

## Use the popup

Start the app from PowerShell:

```powershell
python main.py
```

The app checks the Notion connection and stays in the system tray without opening the task window. Then:

1. Press **Ctrl+Alt+Shift+N** to open the popup, or choose **Open task popup** from its tray menu.
2. Enter a task title. Add optional plain-text notes if you like.
3. Press **Enter** from the title or notes field to submit the task, or select **Add task**. In the notes field, use **Shift+Enter** to add a new line.

A successful task is added with the configured status.

Closing the popup hides it so the hotkey and tray remain available. To stop the app, right-click its tray icon and choose **Quit**. If the tray icon is tucked away, open the tray's hidden-icons menu.

## Start it when you sign in (optional)

To have the app run in the background after Windows sign-in, create a shortcut to `.venv\Scripts\pythonw.exe` in your Windows Startup folder. Set the shortcut's argument to the full path to this project's `main.py`, and its **Start in** folder to the project folder. This starts the tray app without a console window; the popup still opens only when you use the hotkey or tray menu.

## If something doesn't connect

- Check that `.env` is in the project folder and all three settings are filled in.
- Make sure the integration has been shared with the database.
- Check that `NOTION_STATUS_VALUE` matches an existing option in the `Status` column exactly.
- Open the popup and use **Check Notion connection** to see the connection status.

Task titles are required. Notes are optional and are added as text in the page content. Image content is not supported yet.
