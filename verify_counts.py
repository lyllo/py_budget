import sys
import os

sys.path.append(os.path.abspath("src"))
from load.db import conecta_bd

def verify_final():
    conn = conecta_bd()
    cur = conn.cursor()
    
    dates = ['2025-12-15', '2025-12-16', '2025-12-21']
    for d in dates:
        print(f"\n--- Transactions for {d} ---")
        cur.execute("SELECT item, valor, hash, parcela, categoria FROM transactions WHERE data = ? ORDER BY valor ASC", (d,))
        rows = cur.fetchall()
        print(f"Count: {len(rows)}")
        for r in rows:
            parcela = str(r[3]) if r[3] else ""
            categoria = str(r[4]) if r[4] else ""
            print(f"Item: {r[0]:30} | Val: {r[1]:8} | Par: {parcela:4} | Cat: {categoria:10} | Hash: {r[2][:8]}")
        
    conn.close()

if __name__ == "__main__":
    verify_final()
