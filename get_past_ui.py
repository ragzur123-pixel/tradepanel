import json

log_file = r'C:\Users\GranT\.gemini\antigravity-cli\brain\81b3813f-374d-41aa-85a5-5c04e45c4ced\.system_generated\logs\transcript_full.jsonl'
output = []
for line in open(log_file, 'r', encoding='utf-8'):
    if '"Proximity Delta"' in line or 'Proximity Delta' in line:
        try:
            obj = json.loads(line)
            if obj.get('type') == 'PLANNER_RESPONSE':
                for tc in obj.get('tool_calls', []):
                    name = tc.get('name', '')
                    args = tc.get('args', {})
                    if 'replace' in name:
                        chunks = args.get('ReplacementChunks', []) if 'ReplacementChunks' in args else [args]
                        for c in chunks:
                            rc = c.get('ReplacementContent', '')
                            if 'Proximity Delta' in rc:
                                output.append(rc)
        except Exception:
            pass

with open('past_ui.txt', 'w', encoding='utf-8') as f:
    for item in output:
        f.write("---\n" + item + "\n")
print("Done")
