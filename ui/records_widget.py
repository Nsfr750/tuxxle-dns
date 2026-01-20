"""
DNS Records management widget
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QGroupBox, QFormLayout, QLineEdit,
    QSpinBox, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from core.dns_server import DNSServer
from core.dns_records import DNSRecord, DNSRecordType

class RecordDialog(QDialog):
    """Dialog for adding/editing DNS records"""
    
    def __init__(self, parent=None, record: Optional[DNSRecord] = None):
        super().__init__(parent)
        self.record = record
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("Add DNS Record" if record is None else "Edit DNS Record")
        self.setModal(True)
        self.resize(400, 300)
        
        self._setup_ui()
        self._load_record()
    
    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("example.com")
        form_layout.addRow("Domain Name:", self.name_edit)
        
        # Type field
        self.type_combo = QComboBox()
        self.type_combo.addItems([t.name for t in DNSRecordType])
        form_layout.addRow("Record Type:", self.type_combo)
        
        # Value field
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("192.168.1.1")
        form_layout.addRow("Value:", self.value_edit)
        
        # TTL field
        self.ttl_spin = QSpinBox()
        self.ttl_spin.setRange(1, 86400)
        self.ttl_spin.setValue(300)
        self.ttl_spin.setSuffix(" seconds")
        form_layout.addRow("TTL:", self.ttl_spin)
        
        # Help text
        help_label = QLabel(
            "Examples:\n"
            "A: 192.168.1.1\n"
            "AAAA: 2001:db8::1\n"
            "CNAME: www.example.com\n"
            "MX: 10 mail.example.com\n"
            "TXT: \"v=spf1 include:_spf.google.com ~all\""
        )
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        form_layout.addRow(help_label)
        
        # Update help text when type changes
        self.type_combo.currentTextChanged.connect(self._update_help_text)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_record(self):
        """Load existing record data"""
        if self.record:
            self.name_edit.setText(self.record.name)
            self.type_combo.setCurrentText(self.record.record_type.name)
            self.value_edit.setText(self.record.value)
            self.ttl_spin.setValue(self.record.ttl)
    
    def _update_help_text(self):
        """Update help text based on selected record type"""
        record_type = self.type_combo.currentText()
        
        examples = {
            "A": "192.168.1.1",
            "AAAA": "2001:db8::1", 
            "CNAME": "www.example.com",
            "MX": "10 mail.example.com",
            "TXT": "\"v=spf1 include:_spf.google.com ~all\"",
            "NS": "ns1.example.com",
            "SOA": "ns1.example.com admin.example.com 2024010101 7200 3600 1209600 3600",
            "PTR": "1.168.192.in-addr.arpa"
        }
        
        example = examples.get(record_type, "example")
        
        # Find the help label and update it
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and "Examples:" in widget.text():
                widget.setText(f"Examples:\n{record_type}: {example}")
                break
    
    def get_record(self) -> Optional[DNSRecord]:
        """Get DNS record from dialog"""
        try:
            name = self.name_edit.text().strip()
            record_type = DNSRecordType[self.type_combo.currentText()]
            value = self.value_edit.text().strip()
            ttl = self.ttl_spin.value()
            
            if not name or not value:
                QMessageBox.warning(self, "Error", "Name and value are required")
                return None
            
            # Additional validation for MX records
            if record_type == DNSRecordType.MX:
                if ' ' not in value:
                    QMessageBox.warning(self, "Error", 
                        "MX record format: 'priority domain'\nExample: '10 mail.example.com'")
                    return None
                
                try:
                    priority, domain = value.split(' ', 1)
                    int(priority)  # Validate priority is numeric
                except ValueError:
                    QMessageBox.warning(self, "Error", 
                        "MX record format: 'priority domain'\nExample: '10 mail.example.com'")
                    return None
            
            return DNSRecord(name, record_type, value, ttl)
        
        except Exception as e:
            self.logger.error(f"Error creating record: {e}")
            QMessageBox.critical(self, "Error", f"Invalid record data: {e}")
            return None

class RecordsWidget(QWidget):
    """Widget for managing DNS records"""
    
    def __init__(self, dns_server: DNSServer):
        super().__init__()
        self.dns_server = dns_server
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._load_records()
    
    def _setup_ui(self):
        """Setup the records widget UI"""
        layout = QVBoxLayout(self)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("DNS Records")
        title_label.setFont(QFont("", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add button
        self.add_button = QPushButton("Add Record")
        self.add_button.clicked.connect(self._add_record)
        header_layout.addWidget(self.add_button)
        
        # Edit button
        self.edit_button = QPushButton("Edit Record")
        self.edit_button.clicked.connect(self._edit_record)
        self.edit_button.setEnabled(False)
        header_layout.addWidget(self.edit_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete Record")
        self.delete_button.clicked.connect(self._delete_record)
        self.delete_button.setEnabled(False)
        header_layout.addWidget(self.delete_button)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_records)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Records table
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(5)
        self.records_table.setHorizontalHeaderLabels([
            "Domain Name", "Type", "Value", "TTL", "Status"
        ])
        
        # Setup table properties
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.records_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.records_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.records_table)
        
        # Statistics
        self.stats_label = QLabel("Total records: 0")
        self.stats_label.setStyleSheet("color: gray;")
        layout.addWidget(self.stats_label)
    
    def _load_records(self):
        """Load DNS records into table"""
        try:
            records = self.dns_server.list_records()
            
            self.records_table.setRowCount(len(records))
            
            for row, record in enumerate(records):
                # Domain name
                self.records_table.setItem(row, 0, QTableWidgetItem(record.name))
                
                # Record type
                self.records_table.setItem(row, 1, QTableWidgetItem(record.record_type.name))
                
                # Value
                self.records_table.setItem(row, 2, QTableWidgetItem(record.value))
                
                # TTL
                self.records_table.setItem(row, 3, QTableWidgetItem(str(record.ttl)))
                
                # Status
                status_item = QTableWidgetItem("Active")
                status_item.setForeground(Qt.green)
                self.records_table.setItem(row, 4, status_item)
            
            # Update statistics
            self.stats_label.setText(f"Total records: {len(records)}")
            
        except Exception as e:
            self.logger.error(f"Error loading records: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load records: {e}")
    
    def _on_selection_changed(self):
        """Handle table selection change"""
        has_selection = bool(self.records_table.selectedItems())
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def _add_record(self):
        """Add a new DNS record"""
        dialog = RecordDialog(self)
        if dialog.exec() == QDialog.Accepted:
            record = dialog.get_record()
            if record:
                try:
                    self.dns_server.add_record(record)
                    self._load_records()
                    self.logger.info(f"Added DNS record: {record}")
                except Exception as e:
                    self.logger.error(f"Error adding record: {e}")
                    QMessageBox.critical(self, "Error", f"Failed to add record: {e}")
    
    def _edit_record(self):
        """Edit selected DNS record"""
        current_row = self.records_table.currentRow()
        if current_row < 0:
            return
        
        try:
            # Get current record data with safety checks
            name_item = self.records_table.item(current_row, 0)
            type_item = self.records_table.item(current_row, 1)
            value_item = self.records_table.item(current_row, 2)
            ttl_item = self.records_table.item(current_row, 3)
            
            if not all([name_item, type_item, value_item, ttl_item]):
                QMessageBox.warning(self, "Error", "Invalid record selection")
                return
            
            name = name_item.text()
            record_type_name = type_item.text()
            value = value_item.text()
            ttl = int(ttl_item.text())
            
            record_type = DNSRecordType[record_type_name]
            current_record = DNSRecord(name, record_type, value, ttl)
            
            # Open edit dialog
            dialog = RecordDialog(self, current_record)
            if dialog.exec() == QDialog.Accepted:
                new_record = dialog.get_record()
                if new_record:
                    # Remove old record and add new one
                    self.dns_server.remove_record(name, record_type)
                    self.dns_server.add_record(new_record)
                    self._load_records()
                    self.logger.info(f"Updated DNS record: {new_record}")
        
        except Exception as e:
            self.logger.error(f"Error editing record: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit record: {e}")
    
    def _delete_record(self):
        """Delete selected DNS record"""
        current_row = self.records_table.currentRow()
        if current_row < 0:
            return
        
        try:
            # Get record data
            name = self.records_table.item(current_row, 0).text()
            record_type_name = self.records_table.item(current_row, 1).text()
            record_type = DNSRecordType[record_type_name]
            
            # Confirm deletion
            reply = QMessageBox.question(
                self, 'Confirm Delete',
                f'Delete DNS record: {name} ({record_type_name})?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.dns_server.remove_record(name, record_type):
                    self._load_records()
                    self.logger.info(f"Deleted DNS record: {name} {record_type_name}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete record")
        
        except Exception as e:
            self.logger.error(f"Error deleting record: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete record: {e}")
