import os
import sys
from datetime import datetime
import shutil

# Add src to path
sys.path.append(os.path.abspath('src'))

from load.db import conecta_bd, carrega_historico, verbose
import load.files as files

def restore():
    print("🚀 Starting Database Restoration from Audited history.xlsx")
    
    PATH_TO_HISTORY_FILE = os.path.join('data', 'history.xlsx')
    if not os.path.exists(PATH_TO_HISTORY_FILE):
        print(f"❌ Error: {PATH_TO_HISTORY_FILE} not found!")
        return

    conn = conecta_bd()
    cur = conn.cursor()
    
    try:
        # 1. Safety Backup
        print("📦 Creating safety backup of 'transactions' table...")
        backup_table = f"transactions_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cur.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM transactions")
        print(f"✅ Backup created in table: {backup_table}")
        
        # 2. Wipe Tables
        print("🧹 Wiping 'transactions', 'duplicates', and 'ignored' tables...")
        cur.execute("TRUNCATE TABLE transactions")
        cur.execute("TRUNCATE TABLE duplicates")
        cur.execute("TRUNCATE TABLE ignored")
        conn.commit()
        print("✅ Tables wiped clean.")
        
        # 3. Re-ingest from Excel
        print(f"📥 Re-ingesting data from {PATH_TO_HISTORY_FILE}...")
        carrega_historico(PATH_TO_HISTORY_FILE)
        
        # 4. Final Verification
        cur.execute("SELECT COUNT(*) FROM transactions")
        count = cur.fetchone()[0]
        print(f"🏁 Restoration Complete! Total records in DB: {count}")
        
    except Exception as e:
        print(f"❌ Error during restoration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    restore()
