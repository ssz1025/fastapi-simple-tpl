"""
Database backup and restore script.

Usage:
    # Backup
    python scripts/db_backup.py backup
    
    # Restore
    python scripts/db_backup.py restore backup_file.db
"""

import argparse
import asyncio
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings


def backup_sqlite(db_path: str, backup_dir: str = "./backups"):
    """Backup SQLite database."""
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = Path(backup_dir) / f"backup_{timestamp}.db"
    
    print(f"📦 Backing up database to {backup_file}...")
    shutil.copy2(db_path, backup_file)
    
    print(f"✅ Backup created: {backup_file}")
    return str(backup_file)


def restore_sqlite(backup_file: str, db_path: str):
    """Restore SQLite database from backup."""
    print(f"♻️  Restoring database from {backup_file}...")
    
    if not Path(backup_file).exists():
        print(f"❌ Backup file not found: {backup_file}")
        sys.exit(1)
    
    shutil.copy2(backup_file, db_path)
    
    print(f"✅ Database restored successfully")


def list_backups(backup_dir: str = "./backups"):
    """List all available backups."""
    backup_path = Path(backup_dir)
    
    if not backup_path.exists():
        print(f"No backups found in {backup_dir}")
        return
    
    backups = sorted(backup_path.glob("backup_*.db"))
    
    if not backups:
        print(f"No backups found in {backup_dir}")
        return
    
    print(f"\n📋 Available backups in {backup_dir}:")
    for i, backup in enumerate(backups, 1):
        size = backup.stat().st_size / 1024  # KB
        modified = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  {i}. {backup.name} ({size:.1f} KB) - {modified}")


async def backup_postgres():
    """Backup PostgreSQL database (requires pg_dump)."""
    settings = get_settings()
    
    print("📦 PostgreSQL backup not implemented yet")
    print(f"   Use: pg_dump -h {settings.database.postgresql.host} "
          f"-U {settings.database.postgresql.username} "
          f"-d {settings.database.postgresql.database} > backup.sql")


def main():
    parser = argparse.ArgumentParser(description="Database backup/restore")
    parser.add_argument("action", choices=["backup", "restore", "list"],
                        help="Action to perform")
    parser.add_argument("file", nargs="?", help="Backup file (for restore)")
    parser.add_argument("--db-path", default="./data/app.db", help="Database path")
    parser.add_argument("--backup-dir", default="./backups", help="Backup directory")
    
    args = parser.parse_args()
    
    if args.action == "backup":
        settings = get_settings()
        
        if settings.database.type == "sqlite":
            backup_sqlite(args.db_path, args.backup_dir)
        else:
            asyncio.run(backup_postgres())
    
    elif args.action == "restore":
        if not args.file:
            print("❌ Please specify backup file to restore")
            sys.exit(1)
        
        settings = get_settings()
        
        if settings.database.type == "sqlite":
            restore_sqlite(args.file, args.db_path)
        else:
            print("❌ Restore only supported for SQLite")
    
    elif args.action == "list":
        list_backups(args.backup_dir)


if __name__ == "__main__":
    main()
