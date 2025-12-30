import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

def extract_bounds(bounds_str):
    # Format: [x1,y1][x2,y2]
    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
    return 0, 0, 0, 0

def extract_transaction_fields(texts):
    if len(texts) != 4: return None
    
    # Heuristic: 
    # Value contains 'R$'
    # Type contains keywords (Buy, Pix, etc)
    # The other two are Merchant and Category. 
    # Usually Merchant comes before Category in the visual stream, but let's be flexible.
    
    keywords = ['Compra', 'Pix', 'Transferência', 'Pagamento', 'boleto', 'TransferÃªncia', 'Contestação', 'Crédito', 'Estorno']
    
    value = None
    type_line = None
    remaining = []
    
    for t in texts:
        if 'R$' in t and value is None:
            value = t
        elif any(kw in t for kw in keywords) and type_line is None:
            type_line = t
        else:
            remaining.append(t)
            
    if value is None or type_line is None:
        return None
        
    # In BTG, Merchant usually appears before Category in the XML tree if flattened correctly
    merchant = remaining[0] if remaining else "Unknown"
    category = remaining[1] if len(remaining) > 1 else ""
    
    return {
        'type_line': type_line,
        'merchant': merchant,
        'category': category,
        'value': value,
        'all_texts': texts
    }

def is_authorized(texts):
    for t in texts:
        if 'não autorizada' in t.lower(): return False
    return True

def create_signature(merchant, value, date):
    # Simplistic signature for deduplication
    content = f"{merchant}_{value}_{date}".replace(" ", "")
    return hash(content)

def reconstruct():
    logs_dir = 'logs'
    # Pattern: scroll_000_sigs_0_20251222_144146.xml
    pattern = re.compile(r'scroll_(\d+)_sigs_(\d+)_(\d{8})_(\d{6})\.xml')
    
    all_files = os.listdir(logs_dir)
    session_files = []
    for f in all_files:
        match = pattern.match(f)
        if match:
            # Sort factors: Timestamp (Date+Time), Scroll index
            ts = f"{match.group(3)}_{match.group(4)}"
            scroll = int(match.group(1))
            session_files.append((ts, scroll, f))
            
    session_files.sort() # Sorts by ts then scroll
    
    collected_data = [] 
    session_stream = [] 
    
    current_date = None
    date_pattern = re.compile(r'\d{1,2}/[A-Z][a-z]{2}')
    
    # Process files in strict chronological capture order
    for ts, scroll, filename in session_files:
        path = os.path.join(logs_dir, filename)
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except: continue
        
        scroll_objects = []
        seen_snapshot_fps = set()
        
        # Pattern for dates
        date_pattern = re.compile(r'\d{1,2}/[A-Z][a-z]{2}')
        
        # 1. Capture snapshot Ground Truth using Structure-Based Heuristics
        for node in root.iter():
            if node.tag != 'android.view.ViewGroup':
                continue
            
            # Use direct children check if possible, or flattened for simplicity as per user's analysis
            child_text_nodes = list(node.iter('android.widget.TextView'))
            # Filter matches for actual text
            child_texts = [c.get('text', '') for c in child_text_nodes if c.get('text', '').strip()]
            
            # RULE: 1 TextView = Date
            if len(child_texts) == 1:
                txt = child_texts[0]
                if date_pattern.search(txt) or 'Hoje' in txt or 'Ontem' in txt:
                    _, y1, _, _ = extract_bounds(node.get('bounds', '[0,0][0,0]'))
                    scroll_objects.append({'y': y1, 'type': 'date', 'text': txt, 'fp': f"DATE:{txt}"})
            
            # RULE: 4 TextViews = Complete Transaction
            elif len(child_texts) == 4:
                fields = extract_transaction_fields(child_texts)
                if fields and is_authorized(child_texts):
                    bounds = extract_bounds(node.get('bounds', '[0,0][0,0]'))
                    scroll_objects.append({
                        'y': bounds[1], 
                        'type': 'tx', 
                        'data': fields, 
                        'fp': f"{fields['merchant']}|{fields['value']}|{fields['type_line']}"
                    })

        scroll_objects.sort(key=lambda x: x['y'])
        
        if not session_stream:
            session_stream.extend(scroll_objects)
            continue

        # 2. Date-Agnostic Sequence Alignment
        # Align using ONLY transactions. Ignore DATE markers for the match calculation.
        session_tx_fps = [obj['fp'] for obj in session_stream if obj['type'] == 'tx']
        scroll_tx_fps = [obj['fp'] for obj in scroll_objects if obj['type'] == 'tx']
        
        best_tx_overlap = 0
        for size in range(min(len(session_tx_fps), len(scroll_tx_fps), 30), 0, -1):
            if session_tx_fps[-size:] == scroll_tx_fps[:size]:
                best_tx_overlap = size
                break
        
        # 3. Merge starting from the first UNSEEN transaction in the scroll
        # We find the index in scroll_objects where the 'best_tx_overlap'-th transaction ends.
        tx_count = 0
        skip_to_idx = 0
        if best_tx_overlap > 0:
            for i, obj in enumerate(scroll_objects):
                if obj['type'] == 'tx':
                    tx_count += 1
                    if tx_count == best_tx_overlap:
                        skip_to_idx = i + 1
                        break
        
        session_stream.extend(scroll_objects[skip_to_idx:])
            
    # Final Output Generation with stateful Date consistency and Session Merging
    current_date = "Unknown"
    last_output_date = None
    seen_sigs = set() # (Date, Merchant, Value, Type)
    
    for obj in session_stream:
        if obj['type'] == 'date':
            current_date = obj['text']
        else:
            fields = obj['data']
            # Strict uniqueness signature for merging sessions
            sig = f"{current_date}|{fields['merchant']}|{fields['value']}|{fields['type_line']}"
            if sig in seen_sigs:
                continue
            
            # Lazy Output: only print date header when we have a unique transaction to show for it
            if current_date != last_output_date:
                collected_data.append(current_date)
                last_output_date = current_date
            
            collected_data.append(fields['merchant'])
            collected_data.append(fields['category'])
            collected_data.append(fields['value'])
            collected_data.append(fields['type_line'])
            seen_sigs.add(sig)
            
    output_file = 'in/btg_mobile_reconstructed.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in collected_data:
            f.write(line + "\n")
            
    print(f"Reconstructed {len(seen_sigs)} unique transactions from {len(session_stream)} Ground-Truth objects.")

if __name__ == "__main__":
    reconstruct()
