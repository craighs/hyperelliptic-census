import sqlite3
import sys

def clean_database(q):
    db_name = f"gf{q}_curves.db"
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Check total rows before cleanup
        cursor.execute("SELECT COUNT(*) FROM explicit_curves")
        before_count = cursor.fetchone()[0]
        print(f"Total curves before cleanup: {before_count}")
        
        # Delete duplicates, keeping the one with the lowest internal SQLite rowid
        cursor.execute("""
            DELETE FROM explicit_curves
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM explicit_curves
                GROUP BY id
            )
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        # Check total rows after cleanup
        cursor.execute("SELECT COUNT(*) FROM explicit_curves")
        after_count = cursor.fetchone()[0]
        
        print(f"Duplicates removed: {deleted_count}")
        print(f"Total distinct curves remaining: {after_count}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # You can pass 64 as an argument, or default to 64
    Q = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    clean_database(Q)
