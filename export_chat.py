import os
import json
import re
from datetime import datetime

# Define paths
CONVERSATION_ID = "2a393477-2c93-41c7-9f4f-10ddbd7be012"
APP_DATA_DIR = r"C:\Users\user\.gemini\antigravity"
LOG_FILE_PATH = os.path.join(APP_DATA_DIR, "brain", CONVERSATION_ID, ".system_generated", "logs", "overview.txt")

OUTPUT_MD_PATH = "antigravity_chat_export.md"
OUTPUT_HTML_PATH = "antigravity_chat_export.html"

def clean_content(content):
    if not content:
        return ""
    # Clean up <USER_REQUEST> tags if present
    content = re.sub(r'</?USER_REQUEST>', '', content)
    # Clean up additional metadata blocks for cleaner reading, but keep it readable
    content = re.sub(r'<ADDITIONAL_METADATA>[\s\S]*?</ADDITIONAL_METADATA>', '', content)
    content = re.sub(r'<USER_SETTINGS_CHANGE>[\s\S]*?</USER_SETTINGS_CHANGE>', '', content)
    return content.strip()

def format_timestamp(ts_str):
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts_str

import sys

# Configure UTF-8 encoding for standard output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("[Antigravity] Searching for conversation log files...")
    if not os.path.exists(LOG_FILE_PATH):
        print(f"[Error] Log file not found at: {LOG_FILE_PATH}")
        return

    print("[Antigravity] Loading conversation logs...")
    messages = []
    
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                messages.append(data)
            except Exception as e:
                print(f"[Warning] Error parsing line {idx+1}: {e}")

    print(f"[Success] Loaded {len(messages)} steps successfully!")
    
    # Generate Markdown Export
    print("[Antigravity] Generating Markdown export file...")
    md_content = []
    md_content.append(f"# Antigravity 對話匯出紀錄\n")
    md_content.append(f"- **對話 ID**: `{CONVERSATION_ID}`")
    md_content.append(f"- **匯出時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_content.append("---\n")

    for msg in messages:
        source = msg.get("source", "UNKNOWN")
        msg_type = msg.get("type", "UNKNOWN")
        created_at = format_timestamp(msg.get("created_at", ""))
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls", [])

        # Skip purely system/tool output steps in simple markdown to keep it clean, 
        # but capture them if they contain important run info.
        if source == "SYSTEM" and not content:
            continue
            
        cleaned = clean_content(content)
        
        if source == "USER_EXPLICIT" or source == "USER":
            md_content.append(f"### 👤 使用者 ({created_at})\n")
            md_content.append(f"> {cleaned}\n\n")
        elif source == "MODEL":
            md_content.append(f"### 🤖 Antigravity ({created_at})\n")
            if cleaned:
                md_content.append(f"{cleaned}\n\n")
            if tool_calls:
                md_content.append("<details>\n<summary>🔧 呼叫工具細節</summary>\n\n")
                for tc in tool_calls:
                    name = tc.get("name", "")
                    args = json.dumps(tc.get("args", {}), ensure_ascii=False, indent=2)
                    md_content.append(f"- **工具**: `{name}`\n")
                    md_content.append(f"  ```json\n{args}\n  ```\n")
                md_content.append("</details>\n\n")
        elif source == "SYSTEM":
            # Only log interesting user-triggered terminal actions or critical systems
            if msg_type == "RUN_COMMAND":
                md_content.append(f"### 💻 終端機執行指令 ({created_at})\n")
                md_content.append(f"```bash\n{cleaned}\n```\n\n")
        md_content.append("---\n")

    with open(OUTPUT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))
    print(f"[Success] Markdown exported to: {os.path.abspath(OUTPUT_MD_PATH)}")

    # Generate Premium HTML Export
    print("[Antigravity] Generating premium HTML web export...")
    html_items = []
    
    for msg in messages:
        source = msg.get("source", "UNKNOWN")
        msg_type = msg.get("type", "UNKNOWN")
        created_at = format_timestamp(msg.get("created_at", ""))
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls", [])
        
        cleaned = clean_content(content)
        if not cleaned and not tool_calls:
            continue

        role_class = ""
        role_name = ""
        avatar_icon = ""

        if source == "USER_EXPLICIT" or source == "USER":
            role_class = "user-msg"
            role_name = "使用者"
            avatar_icon = "👤"
            # Format user request nicely
            user_body_html = cleaned.replace("\n", "<br>")
            body = f'<div class="msg-body-content">{user_body_html}</div>'
        elif source == "MODEL":
            role_class = "ai-msg"
            role_name = "Antigravity"
            avatar_icon = "🤖"
            
            # Simple markdown-like styling for preview
            body_html = cleaned
            # Convert simple markdown code blocks
            body_html = re.sub(r'```(\w*)\n([\s\S]*?)```', r'<pre class="code-block"><code class="language-\1">\2</code></pre>', body_html)
            # Convert simple inline code `code`
            body_html = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', body_html)
            # Convert linebreaks to <br> where appropriate
            body_html = body_html.replace("\n", "<br>")
            # Fix code block double break issues
            body_html = re.sub(r'<pre class="code-block"><code class="language-.*?">([\s\S]*?)</code></pre>', 
                               lambda m: m.group(0).replace("<br>", "\n"), body_html)

            tools_html = ""
            if tool_calls:
                tools_html = '<div class="tools-section"><details class="tools-details"><summary>🔧 呼叫工具細節 (' + str(len(tool_calls)) + ')</summary><div class="tools-content">'
                for tc in tool_calls:
                    name = tc.get("name", "")
                    args = json.dumps(tc.get("args", {}), ensure_ascii=False, indent=2)
                    tools_html += f'<div class="tool-call"><strong>工具名稱:</strong> <code>{name}</code><pre><code>{args}</code></pre></div>'
                tools_html += '</div></details></div>'
                
            body = f'<div class="msg-body-content">{body_html}</div>{tools_html}'
        elif source == "SYSTEM":
            role_class = "system-msg"
            role_name = f"系統指令 ({msg_type})"
            avatar_icon = "💻"
            body = f'<pre class="code-block"><code>{cleaned}</code></pre>'
        else:
            continue

        item_html = f"""
        <div class="message-card {role_class}">
            <div class="message-header">
                <span class="avatar">{avatar_icon}</span>
                <span class="role-name">{role_name}</span>
                <span class="timestamp">{created_at}</span>
            </div>
            <div class="message-body">
                {body}
            </div>
        </div>
        """
        html_items.append(item_html)

    html_template = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity 對話匯出 - {CONVERSATION_ID}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --container-bg: #1e293b;
            --text-color: #f1f5f9;
            --text-muted: #94a3b8;
            --border-color: #334155;
            
            --user-bg: rgba(59, 130, 246, 0.15);
            --user-border: rgba(59, 130, 246, 0.3);
            --ai-bg: rgba(16, 185, 129, 0.12);
            --ai-border: rgba(16, 185, 129, 0.25);
            --system-bg: rgba(100, 116, 139, 0.1);
            --system-border: rgba(100, 116, 139, 0.2);
            
            --accent-glow: radial-gradient(circle at top right, rgba(99, 102, 241, 0.15), transparent 400px);
        }}
        
        body {{
            background-color: var(--bg-color);
            background-image: var(--accent-glow);
            color: var(--text-color);
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 900px;
            width: 100%;
            background-color: var(--container-bg);
            border: 1px border var(--border-color);
            border-radius: 24px;
            padding: 32px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(10px);
        }}
        
        header {{
            margin-bottom: 40px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 24px;
        }}
        
        h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.5rem;
            margin: 0 0 10px 0;
            background: linear-gradient(135deg, #6366f1, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .meta-info {{
            font-size: 0.95rem;
            color: var(--text-muted);
            margin: 0;
        }}
        
        .meta-info code {{
            background: rgba(255,255,255,0.08);
            padding: 2px 6px;
            border-radius: 4px;
            color: #f1f5f9;
        }}

        .search-bar-container {{
            margin-bottom: 24px;
            display: flex;
            gap: 12px;
        }}

        .search-input {{
            flex: 1;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 12px 16px;
            color: #fff;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }}

        .search-input:focus {{
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        }}
        
        .chat-area {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        
        .message-card {{
            border-radius: 16px;
            padding: 24px;
            border: 1px solid transparent;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .message-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }}
        
        .user-msg {{
            background-color: var(--user-bg);
            border-color: var(--user-border);
        }}
        
        .ai-msg {{
            background-color: var(--ai-bg);
            border-color: var(--ai-border);
        }}
        
        .system-msg {{
            background-color: var(--system-bg);
            border-color: var(--system-border);
        }}
        
        .message-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            font-size: 0.9rem;
        }}
        
        .avatar {{
            font-size: 1.4rem;
        }}
        
        .role-name {{
            font-weight: 600;
            font-size: 1.05rem;
        }}
        
        .user-msg .role-name {{
            color: #60a5fa;
        }}
        
        .ai-msg .role-name {{
            color: #34d399;
        }}
        
        .system-msg .role-name {{
            color: #94a3b8;
        }}
        
        .timestamp {{
            color: var(--text-muted);
            margin-left: auto;
            font-size: 0.8rem;
        }}
        
        .message-body {{
            font-size: 1.05rem;
            word-wrap: break-word;
        }}
        
        .code-block {{
            background-color: #0b0f19;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 16px;
            overflow-x: auto;
            margin: 16px 0;
        }}
        
        .code-block code {{
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.95rem;
            color: #e2e8f0;
        }}
        
        .inline-code {{
            font-family: 'Consolas', monospace;
            background-color: rgba(15, 23, 42, 0.8);
            padding: 2px 6px;
            border-radius: 6px;
            font-size: 0.9em;
            color: #f43f5e;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        .tools-section {{
            margin-top: 16px;
            border-top: 1px solid rgba(255,255,255,0.06);
            padding-top: 12px;
        }}
        
        .tools-details summary {{
            cursor: pointer;
            font-size: 0.9rem;
            color: var(--text-muted);
            font-weight: 500;
            user-select: none;
            outline: none;
        }}
        
        .tools-details summary:hover {{
            color: #f1f5f9;
        }}
        
        .tools-content {{
            margin-top: 12px;
            padding-left: 12px;
            border-left: 2px solid #334155;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .tool-call {{
            background: rgba(15, 23, 42, 0.4);
            border-radius: 8px;
            padding: 12px;
            font-size: 0.9rem;
        }}
        
        .tool-call pre {{
            margin: 8px 0 0 0;
            background: #090d16;
            padding: 8px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        
        .tool-call pre code {{
            font-family: monospace;
            color: #cbd5e1;
        }}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #0f172a;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #334155;
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #475569;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Antigravity 對話紀錄匯出</h1>
            <p class="meta-info">對話 ID: <code>{CONVERSATION_ID}</code> | 匯出日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </header>

        <div class="search-bar-container">
            <input type="text" class="search-input" id="searchInput" placeholder="🔍 輸入關鍵字搜尋對話內容..." oninput="filterMessages()">
        </div>
        
        <div class="chat-area" id="chatArea">
            {"".join(html_items)}
        </div>
    </div>

    <script>
        function filterMessages() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.getElementsByClassName('message-card');
            
            for (let card of cards) {{
                const text = card.textContent.toLowerCase();
                if (text.includes(query)) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }}
        }}
    </script>
</body>
</html>
"""

    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"[Success] HTML exported to: {os.path.abspath(OUTPUT_HTML_PATH)}")
    print("\n[Tip] You can open this HTML file directly in any browser for a fully formatted chat transcript with real-time text filtering and search!")

if __name__ == "__main__":
    main()
