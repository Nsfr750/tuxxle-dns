#!/usr/bin/env python3
"""
Database tools dialog for DNS Server Manager
"""

import logging
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog,
    QProgressBar, QGroupBox, QGridLayout, QLineEdit, QSpinBox,
    QCheckBox, QComboBox, QSplitter, QFrame, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QTextCursor

class DatabaseWorker(QThread):
    """Worker thread for database operations"""
    progress_updated = Signal(int, str)
    finished = Signal(str, bool)
    error = Signal(str)
    
    def __init__(self, operation, database, **kwargs):
        super().__init__()
        self.operation = operation
        self.database = database
        self.kwargs = kwargs
    
    def run(self):
        """Run database operation"""
        try:
            if self.operation == "backup":
                result = self._backup_database()
            elif self.operation == "restore":
                result = self._restore_database()
            elif self.operation == "optimize":
                result = self._optimize_database()
            elif self.operation == "analyze":
                result = self._analyze_database()
            elif self.operation == "cleanup":
                result = self._cleanup_database()
            elif self.operation == "export":
                result = self._export_database()
            elif self.operation == "import":
                result = self._import_database()
            else:
                result = "Unknown operation"
            
            self.finished.emit(result, True)
            
        except Exception as e:
            self.error.emit(f"Error during {self.operation}: {str(e)}")
    
    def _backup_database(self):
        """Backup database"""
        self.progress_updated.emit(10, "Starting backup...")
        
        backup_path = self.kwargs.get('backup_path')
        if not backup_path:
            raise ValueError("Backup path not specified")
        
        self.progress_updated.emit(30, "Creating backup...")
        
        # Copy database file
        source = Path(self.database.db_path)
        destination = Path(backup_path)
        
        if source.exists():
            shutil.copy2(source, destination)
            self.progress_updated.emit(100, "Backup completed")
            return f"Database backed up to: {destination}"
        else:
            raise FileNotFoundError(f"Source database not found: {source}")
    
    def _restore_database(self):
        """Restore database"""
        self.progress_updated.emit(10, "Starting restore...")
        
        restore_path = self.kwargs.get('restore_path')
        if not restore_path:
            raise ValueError("Restore path not specified")
        
        self.progress_updated.emit(30, "Validating backup file...")
        
        source = Path(restore_path)
        destination = Path(self.database.db_path)
        
        if not source.exists():
            raise FileNotFoundError(f"Backup file not found: {source}")
        
        # Validate backup file
        try:
            conn = sqlite3.connect(str(source))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            if not tables:
                raise ValueError("Invalid backup file: no tables found")
                
        except sqlite3.Error as e:
            raise ValueError(f"Invalid backup file: {e}")
        
        self.progress_updated.emit(60, "Creating backup of current database...")
        
        # Create backup of current database
        if destination.exists():
            backup_current = destination.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(destination, backup_current)
        
        self.progress_updated.emit(80, "Restoring database...")
        
        # Restore database
        shutil.copy2(source, destination)
        
        self.progress_updated.emit(100, "Restore completed")
        return f"Database restored from: {source}\nPrevious database backed up to: {backup_current if 'backup_current' in locals() else 'N/A'}"
    
    def _optimize_database(self):
        """Optimize database"""
        self.progress_updated.emit(10, "Starting optimization...")
        
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        
        self.progress_updated.emit(30, "Analyzing database...")
        cursor.execute("ANALYZE")
        
        self.progress_updated.emit(60, "Vacuuming database...")
        cursor.execute("VACUUM")
        
        self.progress_updated.emit(80, "Rebuilding indexes...")
        cursor.execute("REINDEX")
        
        conn.commit()
        conn.close()
        
        self.progress_updated.emit(100, "Optimization completed")
        return "Database optimized successfully"
    
    def _analyze_database(self):
        """Analyze database"""
        self.progress_updated.emit(10, "Starting analysis...")
        
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        
        analysis = []
        analysis.append("=== DATABASE ANALYSIS ===\n")
        
        # Get table info
        self.progress_updated.emit(30, "Analyzing tables...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        analysis.append(f"Tables found: {len(tables)}\n")
        
        for table_name, in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            analysis.append(f"  {table_name}: {count} records")
        
        analysis.append("")
        
        # Get database size
        self.progress_updated.emit(60, "Calculating database size...")
        db_path = Path(self.database.db_path)
        if db_path.exists():
            size_bytes = db_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            analysis.append(f"Database size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
        
        # Get page info
        self.progress_updated.emit(80, "Getting page information...")
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        
        analysis.append(f"Page size: {page_size} bytes")
        analysis.append(f"Page count: {page_count}")
        analysis.append(f"Total pages size: {(page_size * page_count) / (1024 * 1024):.2f} MB")
        
        # Get schema info
        analysis.append("\n=== SCHEMA ===\n")
        for table_name, in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            analysis.append(f"\nTable: {table_name}")
            for col in columns:
                analysis.append(f"  {col[1]} {col[2]} {'NOT NULL' if not col[3] else 'NULL'} {'PRIMARY KEY' if col[5] else ''}")
        
        conn.close()
        
        self.progress_updated.emit(100, "Analysis completed")
        return "\n".join(analysis)
    
    def _cleanup_database(self):
        """Clean up database"""
        self.progress_updated.emit(10, "Starting cleanup...")
        
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        
        # Clean up orphaned records
        self.progress_updated.emit(30, "Cleaning orphaned records...")
        # Add specific cleanup logic based on your database schema
        
        # Clean up old records if timestamp exists
        try:
            cursor.execute("DELETE FROM dns_records WHERE created_at < datetime('now', '-1 year')")
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                self.progress_updated.emit(60, f"Deleted {deleted_count} old records")
        except sqlite3.Error:
            pass  # Table might not have created_at column
        
        self.progress_updated.emit(80, "Optimizing after cleanup...")
        cursor.execute("VACUUM")
        
        conn.commit()
        conn.close()
        
        self.progress_updated.emit(100, "Cleanup completed")
        return "Database cleanup completed"
    
    def _export_database(self):
        """Export database to SQL"""
        self.progress_updated.emit(10, "Starting export...")
        
        export_path = self.kwargs.get('export_path')
        if not export_path:
            raise ValueError("Export path not specified")
        
        conn = sqlite3.connect(self.database.db_path)
        
        self.progress_updated.emit(30, "Exporting data...")
        
        with open(export_path, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
        
        conn.close()
        
        self.progress_updated.emit(100, "Export completed")
        return f"Database exported to: {export_path}"
    
    def _import_database(self):
        """Import database from SQL"""
        self.progress_updated.emit(10, "Starting import...")
        
        import_path = self.kwargs.get('import_path')
        if not import_path:
            raise ValueError("Import path not specified")
        
        self.progress_updated.emit(30, "Creating backup...")
        
        # Create backup
        db_path = Path(self.database.db_path)
        backup_path = db_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(db_path, backup_path)
        
        self.progress_updated.emit(60, "Importing data...")
        
        conn = sqlite3.connect(self.database.db_path)
        
        with open(import_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            conn.executescript(sql_script)
        
        conn.commit()
        conn.close()
        
        self.progress_updated.emit(100, "Import completed")
        return f"Database imported from: {import_path}\nBackup created: {backup_path}"

class DatabaseToolsDialog(QDialog):
    """Database tools dialog window"""
    
    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("Database Tools")
        self.setModal(True)
        self.resize(800, 600)
        
        self._setup_ui()
        self._load_database_info()
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Database Management Tools")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self._setup_info_tab()
        self._setup_backup_tab()
        self._setup_maintenance_tab()
        self._setup_import_export_tab()
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Info")
        self.refresh_button.clicked.connect(self._load_database_info)
        button_layout.addWidget(self.refresh_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _setup_info_tab(self):
        """Setup database information tab"""
        info_layout = QVBoxLayout()
        
        # Database info group
        info_group = QGroupBox("Database Information")
        info_group_layout = QGridLayout()
        
        self.db_path_label = QLabel("Path:")
        self.db_size_label = QLabel("Size:")
        self.db_records_label = QLabel("Records:")
        self.db_modified_label = QLabel("Last Modified:")
        
        info_group_layout.addWidget(QLabel("Database Path:"), 0, 0)
        info_group_layout.addWidget(self.db_path_label, 0, 1)
        info_group_layout.addWidget(QLabel("Database Size:"), 1, 0)
        info_group_layout.addWidget(self.db_size_label, 1, 1)
        info_group_layout.addWidget(QLabel("Total Records:"), 2, 0)
        info_group_layout.addWidget(self.db_records_label, 2, 1)
        info_group_layout.addWidget(QLabel("Last Modified:"), 3, 0)
        info_group_layout.addWidget(self.db_modified_label, 3, 1)
        
        info_group.setLayout(info_group_layout)
        info_layout.addWidget(info_group)
        
        # Analysis results
        analysis_group = QGroupBox("Database Analysis")
        analysis_layout = QVBoxLayout()
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setFont(QFont("Consolas", 9))
        self.analysis_text.setMaximumHeight(200)
        analysis_layout.addWidget(self.analysis_text)
        
        # Analyze button
        analyze_button = QPushButton("Analyze Database")
        analyze_button.clicked.connect(self._analyze_database)
        analysis_layout.addWidget(analyze_button)
        
        analysis_group.setLayout(analysis_layout)
        info_layout.addWidget(analysis_group)
        
        info_layout.addStretch()
        
        # Create widget for tab
        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        self.tab_widget.addTab(info_widget, "Information")
    
    def _setup_backup_tab(self):
        """Setup backup/restore tab"""
        backup_layout = QVBoxLayout()
        
        # Backup section
        backup_group = QGroupBox("Backup Database")
        backup_group_layout = QVBoxLayout()
        
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(QLabel("Backup Path:"))
        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setPlaceholderText("Select backup location...")
        backup_path_layout.addWidget(self.backup_path_edit)
        
        browse_backup_button = QPushButton("Browse")
        browse_backup_button.clicked.connect(self._browse_backup_path)
        backup_path_layout.addWidget(browse_backup_button)
        
        backup_group_layout.addLayout(backup_path_layout)
        
        backup_button = QPushButton("Create Backup")
        backup_button.clicked.connect(self._backup_database)
        backup_group_layout.addWidget(backup_button)
        
        backup_group.setLayout(backup_group_layout)
        backup_layout.addWidget(backup_group)
        
        # Restore section
        restore_group = QGroupBox("Restore Database")
        restore_group_layout = QVBoxLayout()
        
        restore_path_layout = QHBoxLayout()
        restore_path_layout.addWidget(QLabel("Restore From:"))
        self.restore_path_edit = QLineEdit()
        self.restore_path_edit.setPlaceholderText("Select backup file...")
        restore_path_layout.addWidget(self.restore_path_edit)
        
        browse_restore_button = QPushButton("Browse")
        browse_restore_button.clicked.connect(self._browse_restore_path)
        restore_path_layout.addWidget(browse_restore_button)
        
        restore_group_layout.addLayout(restore_path_layout)
        
        restore_button = QPushButton("Restore Database")
        restore_button.clicked.connect(self._restore_database)
        restore_button.setStyleSheet("background-color: #ff6b6b; color: white;")
        restore_group_layout.addWidget(restore_button)
        
        restore_group.setLayout(restore_group_layout)
        backup_layout.addWidget(restore_group)
        
        backup_layout.addStretch()
        
        # Create widget for tab
        backup_widget = QWidget()
        backup_widget.setLayout(backup_layout)
        self.tab_widget.addTab(backup_widget, "Backup/Restore")
    
    def _setup_maintenance_tab(self):
        """Setup maintenance tab"""
        maintenance_layout = QVBoxLayout()
        
        # Maintenance operations
        maintenance_group = QGroupBox("Maintenance Operations")
        maintenance_group_layout = QVBoxLayout()
        
        optimize_button = QPushButton("Optimize Database")
        optimize_button.clicked.connect(self._optimize_database)
        maintenance_group_layout.addWidget(optimize_button)
        
        cleanup_button = QPushButton("Clean Up Database")
        cleanup_button.clicked.connect(self._cleanup_database)
        maintenance_group_layout.addWidget(cleanup_button)
        
        maintenance_group.setLayout(maintenance_group_layout)
        maintenance_layout.addWidget(maintenance_group)
        
        # Results
        results_group = QGroupBox("Operation Results")
        results_layout = QVBoxLayout()
        
        self.maintenance_text = QTextEdit()
        self.maintenance_text.setReadOnly(True)
        self.maintenance_text.setFont(QFont("Consolas", 9))
        self.maintenance_text.setMaximumHeight(150)
        results_layout.addWidget(self.maintenance_text)
        
        results_group.setLayout(results_layout)
        maintenance_layout.addWidget(results_group)
        
        maintenance_layout.addStretch()
        
        # Create widget for tab
        maintenance_widget = QWidget()
        maintenance_widget.setLayout(maintenance_layout)
        self.tab_widget.addTab(maintenance_widget, "Maintenance")
    
    def _setup_import_export_tab(self):
        """Setup import/export tab"""
        import_export_layout = QVBoxLayout()
        
        # Export section
        export_group = QGroupBox("Export Database")
        export_group_layout = QVBoxLayout()
        
        export_path_layout = QHBoxLayout()
        export_path_layout.addWidget(QLabel("Export To:"))
        self.export_path_edit = QLineEdit()
        self.export_path_edit.setPlaceholderText("Select export file...")
        export_path_layout.addWidget(self.export_path_edit)
        
        browse_export_button = QPushButton("Browse")
        browse_export_button.clicked.connect(self._browse_export_path)
        export_path_layout.addWidget(browse_export_button)
        
        export_group_layout.addLayout(export_path_layout)
        
        export_button = QPushButton("Export to SQL")
        export_button.clicked.connect(self._export_database)
        export_group_layout.addWidget(export_button)
        
        export_group.setLayout(export_group_layout)
        import_export_layout.addWidget(export_group)
        
        # Import section
        import_group = QGroupBox("Import Database")
        import_group_layout = QVBoxLayout()
        
        import_path_layout = QHBoxLayout()
        import_path_layout.addWidget(QLabel("Import From:"))
        self.import_path_edit = QLineEdit()
        self.import_path_edit.setPlaceholderText("Select SQL file...")
        import_path_layout.addWidget(self.import_path_edit)
        
        browse_import_button = QPushButton("Browse")
        browse_import_button.clicked.connect(self._browse_import_path)
        import_path_layout.addWidget(browse_import_button)
        
        import_group_layout.addLayout(import_path_layout)
        
        import_button = QPushButton("Import from SQL")
        import_button.clicked.connect(self._import_database)
        import_button.setStyleSheet("background-color: #ff6b6b; color: white;")
        import_group_layout.addWidget(import_button)
        
        import_group.setLayout(import_group_layout)
        import_export_layout.addWidget(import_group)
        
        import_export_layout.addStretch()
        
        # Create widget for tab
        import_export_widget = QWidget()
        import_export_widget.setLayout(import_export_layout)
        self.tab_widget.addTab(import_export_widget, "Import/Export")
    
    def _load_database_info(self):
        """Load database information"""
        try:
            if not self.database:
                return
            
            db_path = Path(self.database.db_path)
            
            # Path
            self.db_path_label.setText(str(db_path))
            
            # Size
            if db_path.exists():
                size_bytes = db_path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                self.db_size_label.setText(f"{size_mb:.2f} MB ({size_bytes:,} bytes)")
                
                # Modified date
                modified_time = datetime.fromtimestamp(db_path.stat().st_mtime)
                self.db_modified_label.setText(modified_time.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                self.db_size_label.setText("File not found")
                self.db_modified_label.setText("N/A")
            
            # Records count
            try:
                records = self.database.list_records()
                self.db_records_label.setText(str(len(records)))
            except:
                self.db_records_label.setText("Error")
                
        except Exception as e:
            self.logger.error(f"Error loading database info: {e}")
    
    def _run_operation(self, operation, **kwargs):
        """Run database operation in background"""
        # Disable controls
        self._set_controls_enabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setVisible(True)
        self.status_label.setText(f"Starting {operation}...")
        
        # Start worker
        self.worker = DatabaseWorker(operation, self.database, **kwargs)
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.finished.connect(self._on_operation_finished)
        self.worker.error.connect(self._on_operation_error)
        self.worker.start()
    
    def _update_progress(self, value, message):
        """Update progress"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def _on_operation_finished(self, result, success):
        """Handle operation completion"""
        # Hide progress
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        # Enable controls
        self._set_controls_enabled(True)
        
        # Show result based on operation type
        if hasattr(self, 'worker') and self.worker.operation == "analyze":
            # Show analysis report in separate dialog
            self._show_analysis_report(result)
        else:
            # Show other operation results in maintenance text
            if hasattr(self, 'maintenance_text'):
                self.maintenance_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {result}")
        
        # Refresh info
        self._load_database_info()
        
        self.logger.info(f"Database operation completed: {result}")
    
    def _show_analysis_report(self, report):
        """Show analysis report in separate dialog"""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
            
            # Create dialog
            report_dialog = QDialog(self)
            report_dialog.setWindowTitle("Database Analysis Report")
            report_dialog.resize(700, 500)
            
            layout = QVBoxLayout()
            
            # Title
            title_label = QLabel("Database Analysis Report")
            title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
            layout.addWidget(title_label)
            
            # Report text
            report_text = QTextEdit()
            report_text.setPlainText(report)
            report_text.setReadOnly(True)
            report_text.setFont(QFont("Consolas", 9))
            layout.addWidget(report_text)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            # Copy button
            copy_button = QPushButton("Copy to Clipboard")
            copy_button.clicked.connect(lambda: self._copy_report_to_clipboard(report))
            button_layout.addWidget(copy_button)
            
            # Save button
            save_button = QPushButton("Save Report")
            save_button.clicked.connect(lambda: self._save_report_to_file(report))
            button_layout.addWidget(save_button)
            
            # Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(report_dialog.accept)
            button_layout.addWidget(close_button)
            
            layout.addLayout(button_layout)
            report_dialog.setLayout(layout)
            
            # Show dialog
            report_dialog.exec_()
            
        except Exception as e:
            self.logger.error(f"Error showing analysis report: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show analysis report:\n{str(e)}")
    
    def _copy_report_to_clipboard(self, report):
        """Copy report to clipboard"""
        try:
            from PySide6.QtWidgets import QApplication
            
            clipboard = QApplication.clipboard()
            clipboard.setText(report)
            
            QMessageBox.information(self, "Success", "Report copied to clipboard")
            
        except Exception as e:
            self.logger.error(f"Error copying to clipboard: {e}")
            QMessageBox.critical(self, "Error", f"Failed to copy report:\n{str(e)}")
    
    def _save_report_to_file(self, report):
        """Save report to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Analysis Report",
                f"database_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                QMessageBox.information(self, "Success", f"Report saved to:\n{file_path}")
                
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save report:\n{str(e)}")
    
    def _on_operation_error(self, error_message):
        """Handle operation error"""
        # Hide progress
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        # Enable controls
        self._set_controls_enabled(True)
        
        # Show error
        if hasattr(self, 'maintenance_text'):
            self.maintenance_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {error_message}")
        
        self.logger.error(f"Database operation error: {error_message}")
        QMessageBox.critical(self, "Operation Error", f"Database operation failed:\n{error_message}")
    
    def _set_controls_enabled(self, enabled):
        """Enable/disable controls"""
        self.refresh_button.setEnabled(enabled)
        self.close_button.setEnabled(enabled)
    
    def _browse_backup_path(self):
        """Browse for backup path"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Backup Location", 
            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
            "Database Files (*.db);;All Files (*)"
        )
        if file_path:
            self.backup_path_edit.setText(file_path)
    
    def _browse_restore_path(self):
        """Browse for restore path"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File",
            "", "Database Files (*.db);;All Files (*)"
        )
        if file_path:
            self.restore_path_edit.setText(file_path)
    
    def _browse_export_path(self):
        """Browse for export path"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Export Location",
            f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
            "SQL Files (*.sql);;All Files (*)"
        )
        if file_path:
            self.export_path_edit.setText(file_path)
    
    def _browse_import_path(self):
        """Browse for import path"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Import File",
            "", "SQL Files (*.sql);;All Files (*)"
        )
        if file_path:
            self.import_path_edit.setText(file_path)
    
    def _backup_database(self):
        """Backup database"""
        backup_path = self.backup_path_edit.text().strip()
        if not backup_path:
            QMessageBox.warning(self, "Warning", "Please select a backup location")
            return
        
        self._run_operation("backup", backup_path=backup_path)
    
    def _restore_database(self):
        """Restore database"""
        restore_path = self.restore_path_edit.text().strip()
        if not restore_path:
            QMessageBox.warning(self, "Warning", "Please select a backup file")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Restore",
            "This will replace the current database. Are you sure?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._run_operation("restore", restore_path=restore_path)
    
    def _optimize_database(self):
        """Optimize database"""
        reply = QMessageBox.question(
            self, "Confirm Optimize",
            "This will optimize the database. The operation may take a few minutes.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._run_operation("optimize")
    
    def _cleanup_database(self):
        """Clean up database"""
        reply = QMessageBox.question(
            self, "Confirm Cleanup",
            "This will clean up old data and optimize the database. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._run_operation("cleanup")
    
    def _analyze_database(self):
        """Analyze database and show report in separate dialog"""
        self._run_operation("analyze")
    
    def _export_database(self):
        """Export database"""
        export_path = self.export_path_edit.text().strip()
        if not export_path:
            QMessageBox.warning(self, "Warning", "Please select an export location")
            return
        
        self._run_operation("export", export_path=export_path)
    
    def _import_database(self):
        """Import database"""
        import_path = self.import_path_edit.text().strip()
        if not import_path:
            QMessageBox.warning(self, "Warning", "Please select an import file")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Import",
            "This will replace the current database. Are you sure?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._run_operation("import", import_path=import_path)
