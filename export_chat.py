import sqlite3
import json
import os
from datetime import datetime

db_path = r"ResearchAgent\.adk\session.db"
output_file = "chat_export.html"

# HTML Template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat Export - TalkNact Concept Generator</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 10px; border-bottom: 1px solid #ddd; }
        .message { margin-bottom: 20px; clear: both; overflow: hidden; }
        .bubble { padding: 12px 18px; border-radius: 18px; max-width: 80%; display: inline-block; word-wrap: break-word; }
        .user .bubble { background-color: #007bff; color: white; float: right; border-bottom-right-radius: 4px; }
        .bot .bubble { background-color: #e9ecef; color: #333; float: left; border-bottom-left-radius: 4px; }
        .meta { font-size: 0.8em; color: #888; margin-bottom: 4px; }
        .user .meta { text-align: right; margin-right: 10px; }
        .bot .meta { text-align: left; margin-left: 10px; }
        pre, code { background-color: rgba(0,0,0,0.05); padding: 2px 4px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; font-size: 0.9em; }
        .bot pre { background-color: rgba(255,255,255,0.5); padding: 10px; overflow-x: auto; }
        p { margin: 0 0 10px 0; }
        p:last-child { margin: 0; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Session Chat Export</h2>
        <p>Exported on: {date}</p>
        <p style="font-size: 0.9em; color: #666;">Session ID: {session_id}</p>
    </div>
    <div class="chat-container">
        {chat_content}
    </div>
</body>
</html>
"""

def format_text_to_html(text):
    # Very basic markdown-to-html conversion for display
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("\n\n", "</p><p>")
    text = text.replace("\n", "<br>")
    # Bold
    import re
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    return f"<p>{text}</p>"

def export_chat():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get the most recently updated session that has actual events
    cur.execute('''
        SELECT s.id 
        FROM sessions s
        JOIN events e ON s.id = e.session_id
        GROUP BY s.id
        ORDER BY MAX(e.timestamp) DESC 
        LIMIT 1
    ''')
    session_row = cur.fetchone()
    if not session_row:
        print("No sessions found in the database.")
        conn.close()
        return
        
    session_id = session_row[0]
    print(f"Exporting latest session: {session_id}")

    # Get events for this session
    cur.execute("SELECT timestamp, event_data FROM events WHERE session_id=? ORDER BY timestamp", (session_id,))
    events = cur.fetchall()
    
    chat_html = ""
    message_count = 0
    
    for ts, event_json in events:
        try:
            event = json.loads(event_json)
            author = event.get("author", "?")
            content = event.get("content", {})
            parts = content.get("parts", [])
            text_parts = [p.get("text", "") for p in parts if "text" in p]
            
            # Check for generated image artifacts
            actions = event.get("actions", {})
            artifact_delta = actions.get("artifact_delta", {})
            image_html = ""
            for filename in artifact_delta.keys():
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # Construct absolute path to the artifact
                    cwd = os.path.abspath(os.getcwd())
                    # Artifacts from adk web UI are typically stored in the root .adk folder
                    img_path = os.path.join(cwd, ".adk", "artifacts", "users", "user", "sessions", session_id, "artifacts", filename, "versions", "0", filename)
                    
                    # If it's not in the root .adk, check the app-specific one
                    if not os.path.exists(img_path):
                        app_name = event.get("app_name", "ResearchAgent")
                        alt_img_path = os.path.join(cwd, app_name, ".adk", "artifacts", "users", "user", "sessions", session_id, "artifacts", filename, "versions", "0", filename)
                        if os.path.exists(alt_img_path):
                            img_path = alt_img_path

                    # Use file URI
                    uri = "file:///" + img_path.replace("\\", "/")
                    image_html += f'<div style="margin-top: 15px; margin-bottom: 15px;"><img src="{uri}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Generated Image"></div>'

            if not text_parts and not image_html:
                continue
                
            text = " ".join(text_parts)
            
            # Skip compliance agent internal logs
            if author == "ComplianceAgent" or "For context:[ComplianceAgent]" in text:
                continue
                
            # Formatting
            css_class = "user" if author == "user" else "bot"
            display_name = "You" if author == "user" else "TalkNact Concept Generator"
            formatted_text = format_text_to_html(text) + image_html
            
            time_str = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            
            chat_html += f"""
            <div class="message {css_class}">
                <div class="meta">{display_name} • {time_str}</div>
                <div class="bubble">{formatted_text}</div>
            </div>
            """
            message_count += 1
        except Exception as e:
            pass

    conn.close()
    
    if message_count == 0:
        print("No readable chat messages found in this session.")
        return

    # Write the file
    final_html = html_template.replace("{date}", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    final_html = final_html.replace("{session_id}", session_id)
    final_html = final_html.replace("{chat_content}", chat_html)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print(f"\n[SUCCESS] Exported {message_count} messages to '{output_file}'")
    print(f"Double-click {os.path.abspath(output_file)} to open it in your browser, then press Ctrl+P to save as PDF.")

if __name__ == "__main__":
    export_chat()
