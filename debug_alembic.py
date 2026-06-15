import sys
import os
from alembic.config import Config
from alembic.script import ScriptDirectory

# Set path to backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def check_heads():
    try:
        # Point to alembic.ini
        alembic_cfg = Config("backend/alembic.ini")
        alembic_cfg.set_main_option("script_location", "backend/alembic")
        
        script = ScriptDirectory.from_config(alembic_cfg)
        
        heads = script.get_heads()
        print(f"Heads: {heads}")
        
        for head in heads:
            print(f"Head: {head}")
            rev = script.get_revision(head)
            print(f"  File: {rev.path}")
            print(f"  Down Revision: {rev.down_revision}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_heads()
