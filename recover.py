import json
import subprocess

transcript_file = r'C:\Users\GranT\.gemini\antigravity-cli\brain\1e57bae7-05c7-4109-85c8-4631aecf5c7e\.system_generated\logs\transcript_full.jsonl'

with open(transcript_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def apply_replacements(content, target_content, replacement_content):
    content = content.replace('\r\n', '\n')
    target_content = target_content.replace('\r\n', '\n')
    replacement_content = replacement_content.replace('\r\n', '\n')
    
    if target_content in content:
        print("MATCHED TARGET!")
        return content.replace(target_content, replacement_content, 1)
    else:
        print("FAILED TO MATCH TARGET:", target_content[:50].replace('\n', ' '))
    return content

files = {}
for target in ['src/app.py', 'src/data_node.py', 'src/worker.py']:
    out = subprocess.check_output(['git', 'show', f':{target}'])
    files[target] = out.decode('utf-8')

for line in lines:
    try:
        obj = json.loads(line)
        if obj.get('type') == 'PLANNER_RESPONSE' and 'tool_calls' in obj:
            tool_calls = obj.get('tool_calls', [])
            for tc in tool_calls:
                func = tc.get('name', '')
                args = tc.get('args', {})
                
                if func == 'replace_file_content':
                    target_file = args.get('TargetFile', '')
                    target_file_rel = target_file.replace('\\', '/')
                    if 'src/' in target_file_rel:
                        target_file_rel = 'src/' + target_file_rel.split('src/')[-1]
                        
                    if target_file_rel in files:
                        t = args.get('TargetContent', '')
                        r = args.get('ReplacementContent', '')
                        print(f"Applying replace to {target_file_rel}")
                        files[target_file_rel] = apply_replacements(files[target_file_rel], t, r)
                        
                elif func == 'multi_replace_file_content':
                    target_file = args.get('TargetFile', '')
                    target_file_rel = target_file.replace('\\', '/')
                    if 'src/' in target_file_rel:
                        target_file_rel = 'src/' + target_file_rel.split('src/')[-1]
                        
                    if target_file_rel in files:
                        chunks = args.get('ReplacementChunks', [])
                        print(f"Applying multi-replace to {target_file_rel} with {len(chunks)} chunks")
                        for chunk in chunks:
                            t = chunk.get('TargetContent', '')
                            r = chunk.get('ReplacementContent', '')
                            files[target_file_rel] = apply_replacements(files[target_file_rel], t, r)
    except Exception as e:
        pass

for f, content in files.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)
print("Recovery Complete!")
