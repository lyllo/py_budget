import xml.etree.ElementTree as ET
import os

def inspect_structure(filename, target_text):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    for node in root.iter():
        all_texts = [c.get('text', '') for c in node.iter('android.widget.TextView') if c.get('text')]
        if any(target_text in t for t in all_texts):
            print(f"Container: {node.tag} | Bounds: {node.get('bounds')} | Child Count: {len(list(node))}")
            print(f"Texts: {all_texts}")
            print("-" * 20)

if __name__ == "__main__":
    logs_dir = 'logs'
    # Try to find Covabra or Red Sheep in a log that contains them
    f = 'logs/scroll_002_sigs_10_20251222_144203.xml'
    if os.path.exists(f):
        inspect_structure(f, 'Red Sheep Bbq')
