import sys
import os

sys.path.append(os.path.abspath("src"))
from load.db import conecta_bd

def cleanup_filtro():
    conn = conecta_bd()
    cur = conn.cursor()
    
    # Identify items to delete
    cur.execute("SELECT item, valor, data, hash FROM transactions WHERE item = 'Filtro'")
    rows = cur.fetchall()
    
    print(f"\n--- Cleaning up 'Filtro' Merchant Pollution ---")
    for item, valor, data, full_hash in rows:
        print(f"Deleting pollution: {item:20} | Val: {valor:8} | Date: {data} | Hash: {full_hash[:8]}")
        cur.execute("DELETE FROM transactions WHERE hash = ?", (full_hash,))
        
    print(f"Total deleted: {len(rows)}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    cleanup_filtro()
