"""
SQLite database management for DNS records
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Optional
from .dns_records import DNSRecord, DNSRecordType

class DNSSQLiteDatabase:
    """SQLite database for DNS records persistence"""
    
    def __init__(self, db_path: str = "dns_records.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create DNS records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dns_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        record_type TEXT NOT NULL,
                        value TEXT NOT NULL,
                        ttl INTEGER DEFAULT 300,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(name, record_type)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_dns_records_name 
                    ON dns_records(name)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_dns_records_type 
                    ON dns_records(record_type)
                ''')
                
                conn.commit()
                self.logger.info(f"Database initialized: {self.db_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def add_record(self, record: DNSRecord) -> bool:
        """Add a DNS record to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO dns_records 
                    (name, record_type, value, ttl, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (record.name, record.record_type.name, record.value, record.ttl))
                
                conn.commit()
                self.logger.info(f"Added record to database: {record}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to add record to database: {e}")
            return False
    
    def remove_record(self, name: str, record_type: DNSRecordType) -> bool:
        """Remove a DNS record from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM dns_records 
                    WHERE name = ? AND record_type = ?
                ''', (name, record_type.name))
                
                affected_rows = cursor.rowcount
                conn.commit()
                
                if affected_rows > 0:
                    self.logger.info(f"Removed record from database: {name} {record_type.name}")
                    return True
                else:
                    self.logger.warning(f"Record not found in database: {name} {record_type.name}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to remove record from database: {e}")
            return False
    
    def get_record(self, name: str, record_type: DNSRecordType) -> Optional[DNSRecord]:
        """Get a specific DNS record from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT name, record_type, value, ttl 
                    FROM dns_records 
                    WHERE name = ? AND record_type = ?
                ''', (name, record_type.name))
                
                row = cursor.fetchone()
                if row:
                    return DNSRecord(
                        name=row[0],
                        record_type=DNSRecordType[row[1]],
                        value=row[2],
                        ttl=row[3]
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get record from database: {e}")
            return None
    
    def list_records(self) -> List[DNSRecord]:
        """List all DNS records from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT name, record_type, value, ttl 
                    FROM dns_records 
                    ORDER BY name, record_type
                ''')
                
                records = []
                for row in cursor.fetchall():
                    records.append(DNSRecord(
                        name=row[0],
                        record_type=DNSRecordType[row[1]],
                        value=row[2],
                        ttl=row[3]
                    ))
                
                return records
                
        except Exception as e:
            self.logger.error(f"Failed to list records from database: {e}")
            return []
    
    def search_records(self, query: str) -> List[DNSRecord]:
        """Search DNS records by name or value"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                search_pattern = f"%{query}%"
                cursor.execute('''
                    SELECT name, record_type, value, ttl 
                    FROM dns_records 
                    WHERE name LIKE ? OR value LIKE ?
                    ORDER BY name, record_type
                ''', (search_pattern, search_pattern))
                
                records = []
                for row in cursor.fetchall():
                    records.append(DNSRecord(
                        name=row[0],
                        record_type=DNSRecordType[row[1]],
                        value=row[2],
                        ttl=row[3]
                    ))
                
                return records
                
        except Exception as e:
            self.logger.error(f"Failed to search records in database: {e}")
            return []
    
    def get_records_by_type(self, record_type: DNSRecordType) -> List[DNSRecord]:
        """Get all records of a specific type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT name, record_type, value, ttl 
                    FROM dns_records 
                    WHERE record_type = ?
                    ORDER BY name
                ''', (record_type.name,))
                
                records = []
                for row in cursor.fetchall():
                    records.append(DNSRecord(
                        name=row[0],
                        record_type=DNSRecordType[row[1]],
                        value=row[2],
                        ttl=row[3]
                    ))
                
                return records
                
        except Exception as e:
            self.logger.error(f"Failed to get records by type from database: {e}")
            return []
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
            self.logger.info(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore database: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total records
                cursor.execute('SELECT COUNT(*) FROM dns_records')
                total_records = cursor.fetchone()[0]
                
                # Records by type
                cursor.execute('''
                    SELECT record_type, COUNT(*) 
                    FROM dns_records 
                    GROUP BY record_type
                ''')
                records_by_type = dict(cursor.fetchall())
                
                # Most recent record
                cursor.execute('''
                    SELECT name, record_type, updated_at 
                    FROM dns_records 
                    ORDER BY updated_at DESC 
                    LIMIT 1
                ''')
                latest_record = cursor.fetchone()
                
                return {
                    'total_records': total_records,
                    'records_by_type': records_by_type,
                    'latest_record': latest_record,
                    'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get database statistics: {e}")
            return {}
    
    def clear_all_records(self) -> bool:
        """Clear all DNS records from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM dns_records')
                conn.commit()
                self.logger.info("All records cleared from database")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to clear database: {e}")
            return False
