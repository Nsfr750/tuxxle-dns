#!/usr/bin/env python3
"""
IP Converter dialog for IPv4/IPv6 conversion
"""

import logging
from typing import List, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog,
    QGroupBox, QGridLayout, QLineEdit, QComboBox,
    QRadioButton, QButtonGroup, QCheckBox, QSpinBox,
    QSplitter, QFrame, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QTextCursor
from core.ip_converter import IPConverter

class BatchConverterWorker(QThread):
    """Worker thread for batch IP conversion"""
    progress_updated = Signal(int, str)
    finished = Signal(list)
    error = Signal(str)
    
    def __init__(self, ip_list: List[str], method: str, converter: IPConverter):
        super().__init__()
        self.ip_list = ip_list
        self.method = method
        self.converter = converter
    
    def run(self):
        """Run batch conversion"""
        try:
            results = []
            total = len(self.ip_list)
            
            for i, ip in enumerate(self.ip_list):
                if not ip.strip():
                    continue
                
                progress = int((i / total) * 100)
                self.progress_updated.emit(progress, f"Processing {ip}...")
                
                try:
                    if self.method == "ipv4_to_ipv6":
                        if self.converter.is_valid_ipv4(ip):
                            ipv6 = self.converter.ipv4_to_ipv6_mapped(ip)
                            results.append((ip, ipv6, "Success", None))
                        else:
                            results.append((ip, "", "Invalid IPv4", None))
                    
                    elif self.method == "ipv6_to_ipv4":
                        if self.converter.is_valid_ipv6(ip):
                            ipv4 = self.converter.get_ipv4_from_ipv6(ip)
                            if ipv4:
                                results.append((ip, ipv4, "Success", None))
                            else:
                                results.append((ip, "", "No embedded IPv4", None))
                        else:
                            results.append((ip, "", "Invalid IPv6", None))
                    
                    elif self.method == "info":
                        info = self.converter.get_ip_info(ip)
                        info_str = f"Type: {info['type']}, Valid: {info['is_valid']}"
                        if info['ipv4_equivalent']:
                            info_str += f", IPv4: {info['ipv4_equivalent']}"
                        if info['ipv6_equivalent']:
                            info_str += f", IPv6: {info['ipv6_equivalent']}"
                        results.append((ip, info_str, "Info", None))
                    
                except Exception as e:
                    results.append((ip, "", "Error", str(e)))
            
            self.progress_updated.emit(100, "Conversion completed")
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"Batch conversion failed: {str(e)}")

class IPConverterDialog(QDialog):
    """IP Converter dialog window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.converter = IPConverter()
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("IPv4/IPv6 Converter")
        self.setModal(True)
        self.resize(800, 600)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("IPv4/IPv6 Address Converter")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self._setup_single_convert_tab()
        self._setup_batch_convert_tab()
        self._setup_info_tab()
        self._setup_dns_tab()
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Clear button
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self._clear_all)
        button_layout.addWidget(self.clear_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _setup_single_convert_tab(self):
        """Setup single conversion tab"""
        single_layout = QVBoxLayout()
        
        # Conversion type selection
        type_group = QGroupBox("Conversion Type")
        type_layout = QVBoxLayout()
        
        self.ipv4_to_ipv6_radio = QRadioButton("IPv4 → IPv6 (Mapped)")
        self.ipv4_to_ipv6_radio.setChecked(True)
        type_layout.addWidget(self.ipv4_to_ipv6_radio)
        
        self.ipv6_to_ipv4_radio = QRadioButton("IPv6 → IPv4 (Extract)")
        type_layout.addWidget(self.ipv6_to_ipv4_radio)
        
        self.ipv4_to_6to4_radio = QRadioButton("IPv4 → IPv6 (6to4)")
        type_layout.addWidget(self.ipv4_to_6to4_radio)
        
        self.ipv4_to_teredo_radio = QRadioButton("IPv4 → IPv6 (Teredo)")
        type_layout.addWidget(self.ipv4_to_teredo_radio)
        
        type_group.setLayout(type_layout)
        single_layout.addWidget(type_group)
        
        # Input/Output area
        io_group = QGroupBox("Conversion")
        io_layout = QGridLayout()
        
        io_layout.addWidget(QLabel("Input:"), 0, 0)
        self.single_input_edit = QLineEdit()
        self.single_input_edit.setPlaceholderText("Enter IP address...")
        io_layout.addWidget(self.single_input_edit, 0, 1)
        
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self._single_convert)
        io_layout.addWidget(self.convert_button, 0, 2)
        
        io_layout.addWidget(QLabel("Output:"), 1, 0)
        self.single_output_edit = QLineEdit()
        self.single_output_edit.setReadOnly(True)
        io_layout.addWidget(self.single_output_edit, 1, 1, 1, 2)
        
        io_group.setLayout(io_layout)
        single_layout.addWidget(io_group)
        
        # Additional options
        options_group = QGroupBox("Additional Options")
        options_layout = QVBoxLayout()
        
        self.compress_ipv6_check = QCheckBox("Compress IPv6 address")
        self.compress_ipv6_check.setChecked(True)
        options_layout.addWidget(self.compress_ipv6_check)
        
        self.validate_input_check = QCheckBox("Validate input before conversion")
        self.validate_input_check.setChecked(True)
        options_layout.addWidget(self.validate_input_check)
        
        options_group.setLayout(options_layout)
        single_layout.addWidget(options_group)
        
        single_layout.addStretch()
        
        # Create widget for tab
        single_widget = QFrame()
        single_widget.setLayout(single_layout)
        self.tab_widget.addTab(single_widget, "Single Convert")
    
    def _setup_batch_convert_tab(self):
        """Setup batch conversion tab"""
        batch_layout = QVBoxLayout()
        
        # Input area
        input_group = QGroupBox("Input IP Addresses")
        input_layout = QVBoxLayout()
        
        input_label = QLabel("Enter IP addresses (one per line):")
        input_layout.addWidget(input_label)
        
        self.batch_input_edit = QTextEdit()
        self.batch_input_edit.setPlaceholderText("192.168.1.1\n10.0.0.1\n::ffff:192.168.1.1")
        self.batch_input_edit.setMaximumHeight(150)
        input_layout.addWidget(self.batch_input_edit)
        
        # File operations
        file_layout = QHBoxLayout()
        
        load_button = QPushButton("Load from File")
        load_button.clicked.connect(self._load_from_file)
        file_layout.addWidget(load_button)
        
        clear_button = QPushButton("Clear Input")
        clear_button.clicked.connect(self._clear_batch_input)
        file_layout.addWidget(clear_button)
        
        input_layout.addLayout(file_layout)
        input_group.setLayout(input_layout)
        batch_layout.addWidget(input_group)
        
        # Conversion options
        options_group = QGroupBox("Batch Options")
        options_layout = QGridLayout()
        
        options_layout.addWidget(QLabel("Conversion Method:"), 0, 0)
        self.batch_method_combo = QComboBox()
        self.batch_method_combo.addItems(["IPv4 → IPv6 (Mapped)", "IPv6 → IPv4 (Extract)", "IP Information"])
        options_layout.addWidget(self.batch_method_combo, 0, 1)
        
        options_layout.addWidget(QLabel("Skip Invalid:"), 1, 0)
        self.skip_invalid_check = QCheckBox("Skip invalid addresses")
        self.skip_invalid_check.setChecked(True)
        options_layout.addWidget(self.skip_invalid_check, 1, 1)
        
        options_group.setLayout(options_layout)
        batch_layout.addWidget(options_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        batch_layout.addWidget(self.progress_bar)
        
        # Convert button
        self.batch_convert_button = QPushButton("Start Batch Conversion")
        self.batch_convert_button.clicked.connect(self._batch_convert)
        batch_layout.addWidget(self.batch_convert_button)
        
        # Results area
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Input", "Output", "Status", "Error"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        results_layout.addWidget(self.results_table)
        
        # Export button
        export_button = QPushButton("Export Results")
        export_button.clicked.connect(self._export_results)
        results_layout.addWidget(export_button)
        
        results_group.setLayout(results_layout)
        batch_layout.addWidget(results_group)
        
        # Create widget for tab
        batch_widget = QFrame()
        batch_widget.setLayout(batch_layout)
        self.tab_widget.addTab(batch_widget, "Batch Convert")
    
    def _setup_info_tab(self):
        """Setup IP information tab"""
        info_layout = QVBoxLayout()
        
        # Input area
        input_group = QGroupBox("IP Address Analysis")
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("IP Address:"), 0, 0)
        self.info_input_edit = QLineEdit()
        self.info_input_edit.setPlaceholderText("Enter IP address to analyze...")
        input_layout.addWidget(self.info_input_edit, 0, 1)
        
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self._analyze_ip)
        input_layout.addWidget(self.analyze_button, 0, 2)
        
        input_group.setLayout(input_layout)
        info_layout.addWidget(input_group)
        
        # Results area
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()
        
        self.info_results_edit = QTextEdit()
        self.info_results_edit.setReadOnly(True)
        self.info_results_edit.setFont(QFont("Consolas", 9))
        results_layout.addWidget(self.info_results_edit)
        
        results_group.setLayout(results_layout)
        info_layout.addWidget(results_group)
        
        # Create widget for tab
        info_widget = QFrame()
        info_widget.setLayout(info_layout)
        self.tab_widget.addTab(info_widget, "IP Analysis")
    
    def _setup_dns_tab(self):
        """Setup DNS record conversion tab"""
        dns_layout = QVBoxLayout()
        
        # DNS conversion area
        dns_group = QGroupBox("DNS Record Conversion")
        dns_inner_layout = QGridLayout()
        
        # Record type
        dns_inner_layout.addWidget(QLabel("Record Type:"), 0, 0)
        self.dns_type_combo = QComboBox()
        self.dns_type_combo.addItems(["A → AAAA", "AAAA → A"])
        dns_inner_layout.addWidget(self.dns_type_combo, 0, 1)
        
        # Record value
        dns_inner_layout.addWidget(QLabel("Record Value:"), 1, 0)
        self.dns_value_edit = QLineEdit()
        self.dns_value_edit.setPlaceholderText("Enter IP address...")
        dns_inner_layout.addWidget(self.dns_value_edit, 1, 1)
        
        # Convert button
        self.dns_convert_button = QPushButton("Convert Record")
        self.dns_convert_button.clicked.connect(self._convert_dns_record)
        dns_inner_layout.addWidget(self.dns_convert_button, 1, 2)
        
        # Results
        dns_inner_layout.addWidget(QLabel("Converted Value:"), 2, 0)
        self.dns_result_edit = QLineEdit()
        self.dns_result_edit.setReadOnly(True)
        dns_inner_layout.addWidget(self.dns_result_edit, 2, 1, 1, 2)
        
        dns_group.setLayout(dns_inner_layout)
        dns_layout.addWidget(dns_group)
        
        # DNS batch conversion
        batch_group = QGroupBox("Batch DNS Conversion")
        batch_inner_layout = QVBoxLayout()
        
        batch_label = QLabel("DNS Records (format: TYPE VALUE):")
        batch_inner_layout.addWidget(batch_label)
        
        self.dns_batch_edit = QTextEdit()
        self.dns_batch_edit.setPlaceholderText("A 192.168.1.1\nAAAA ::ffff:192.168.1.2\nA 10.0.0.1")
        self.dns_batch_edit.setMaximumHeight(100)
        batch_inner_layout.addWidget(self.dns_batch_edit)
        
        dns_batch_button = QPushButton("Convert DNS Records")
        dns_batch_button.clicked.connect(self._batch_convert_dns)
        batch_inner_layout.addWidget(dns_batch_button)
        
        # DNS results
        self.dns_results_table = QTableWidget()
        self.dns_results_table.setColumnCount(3)
        self.dns_results_table.setHorizontalHeaderLabels(["Original", "Converted", "Status"])
        self.dns_results_table.horizontalHeader().setStretchLastSection(True)
        batch_inner_layout.addWidget(self.dns_results_table)
        
        batch_group.setLayout(batch_inner_layout)
        dns_layout.addWidget(batch_group)
        
        # Create widget for tab
        dns_widget = QFrame()
        dns_widget.setLayout(dns_layout)
        self.tab_widget.addTab(dns_widget, "DNS Records")
    
    def _single_convert(self):
        """Convert single IP address"""
        input_ip = self.single_input_edit.text().strip()
        if not input_ip:
            QMessageBox.warning(self, "Warning", "Please enter an IP address")
            return
        
        try:
            if self.ipv4_to_ipv6_radio.isChecked():
                if self.converter.is_valid_ipv4(input_ip):
                    result = self.converter.ipv4_to_ipv6_mapped(input_ip)
                    if self.compress_ipv6_check.isChecked():
                        result = self.converter.compress_ipv6(result)
                    self.single_output_edit.setText(result)
                else:
                    QMessageBox.warning(self, "Error", "Invalid IPv4 address")
            
            elif self.ipv6_to_ipv4_radio.isChecked():
                if self.converter.is_valid_ipv6(input_ip):
                    result = self.converter.get_ipv4_from_ipv6(input_ip)
                    if result:
                        self.single_output_edit.setText(result)
                    else:
                        QMessageBox.warning(self, "Error", "IPv6 address does not contain embedded IPv4")
                else:
                    QMessageBox.warning(self, "Error", "Invalid IPv6 address")
            
            elif self.ipv4_to_6to4_radio.isChecked():
                if self.converter.is_valid_ipv4(input_ip):
                    result = self.converter.ipv4_to_6to4(input_ip)
                    self.single_output_edit.setText(result)
                else:
                    QMessageBox.warning(self, "Error", "Invalid IPv4 address")
            
            elif self.ipv4_to_teredo_radio.isChecked():
                if self.converter.is_valid_ipv4(input_ip):
                    result = self.converter.ipv4_to_teredo(input_ip)
                    self.single_output_edit.setText(result)
                else:
                    QMessageBox.warning(self, "Error", "Invalid IPv4 address")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Conversion failed: {str(e)}")
    
    def _batch_convert(self):
        """Start batch conversion"""
        input_text = self.batch_input_edit.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, "Warning", "Please enter IP addresses")
            return
        
        # Parse input
        ip_list = [line.strip() for line in input_text.split('\n') if line.strip()]
        
        if not ip_list:
            QMessageBox.warning(self, "Warning", "No valid IP addresses found")
            return
        
        # Get conversion method
        method_map = {
            "IPv4 → IPv6 (Mapped)": "ipv4_to_ipv6",
            "IPv6 → IPv4 (Extract)": "ipv6_to_ipv4",
            "IP Information": "info"
        }
        method = method_map[self.batch_method_combo.currentText()]
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.batch_convert_button.setEnabled(False)
        
        # Start worker
        self.worker = BatchConverterWorker(ip_list, method, self.converter)
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.finished.connect(self._on_batch_finished)
        self.worker.error.connect(self._on_batch_error)
        self.worker.start()
    
    def _update_progress(self, value, message):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def _on_batch_finished(self, results):
        """Handle batch conversion completion"""
        self.progress_bar.setVisible(False)
        self.batch_convert_button.setEnabled(True)
        
        # Populate results table
        self.results_table.setRowCount(len(results))
        
        for i, (input_ip, output, status, error) in enumerate(results):
            self.results_table.setItem(i, 0, QTableWidgetItem(input_ip))
            self.results_table.setItem(i, 1, QTableWidgetItem(output))
            self.results_table.setItem(i, 2, QTableWidgetItem(status))
            self.results_table.setItem(i, 3, QTableWidgetItem(error or ""))
        
        # Resize columns
        self.results_table.resizeColumnsToContents()
    
    def _on_batch_error(self, error_message):
        """Handle batch conversion error"""
        self.progress_bar.setVisible(False)
        self.batch_convert_button.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Batch conversion failed:\n{error_message}")
    
    def _analyze_ip(self):
        """Analyze IP address"""
        ip = self.info_input_edit.text().strip()
        if not ip:
            QMessageBox.warning(self, "Warning", "Please enter an IP address")
            return
        
        try:
            info = self.converter.get_ip_info(ip)
            
            # Format results
            results = []
            results.append(f"=== IP Address Analysis ===")
            results.append(f"Original: {info['original']}")
            results.append(f"Type: {info['type']}")
            results.append(f"Valid: {info['is_valid']}")
            
            if info['ipv4_equivalent']:
                results.append(f"IPv4 Equivalent: {info['ipv4_equivalent']}")
            
            if info['ipv6_equivalent']:
                results.append(f"IPv6 Equivalent: {info['ipv6_equivalent']}")
            
            if info['compressed']:
                results.append(f"Compressed IPv6: {info['compressed']}")
            
            if info['expanded']:
                results.append(f"Expanded IPv6: {info['expanded']}")
            
            results.append(f"Private: {info['is_private']}")
            results.append(f"Loopback: {info['is_loopback']}")
            results.append(f"Multicast: {info['is_multicast']}")
            
            if 'error' in info:
                results.append(f"Error: {info['error']}")
            
            self.info_results_edit.setText('\n'.join(results))
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")
    
    def _convert_dns_record(self):
        """Convert single DNS record"""
        record_type = self.dns_type_combo.currentText()
        value = self.dns_value_edit.text().strip()
        
        if not value:
            QMessageBox.warning(self, "Warning", "Please enter a record value")
            return
        
        try:
            if record_type == "A → AAAA":
                new_type, new_value = self.converter.convert_dns_record("A", value)
            else:  # AAAA → A
                new_type, new_value = self.converter.convert_dns_record("AAAA", value)
            
            self.dns_result_edit.setText(f"{new_type} {new_value}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"DNS conversion failed: {str(e)}")
    
    def _batch_convert_dns(self):
        """Convert DNS records in batch"""
        input_text = self.dns_batch_edit.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, "Warning", "Please enter DNS records")
            return
        
        # Parse DNS records
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]
        results = []
        
        for line in lines:
            try:
                parts = line.split(maxsplit=1)
                if len(parts) != 2:
                    results.append((line, "", "Invalid format"))
                    continue
                
                record_type, value = parts
                new_type, new_value = self.converter.convert_dns_record(record_type, value)
                results.append((line, f"{new_type} {new_value}", "Success"))
            
            except Exception as e:
                results.append((line, "", f"Error: {str(e)}"))
        
        # Populate results table
        self.dns_results_table.setRowCount(len(results))
        
        for i, (original, converted, status) in enumerate(results):
            self.dns_results_table.setItem(i, 0, QTableWidgetItem(original))
            self.dns_results_table.setItem(i, 1, QTableWidgetItem(converted))
            self.dns_results_table.setItem(i, 2, QTableWidgetItem(status))
        
        # Resize columns
        self.dns_results_table.resizeColumnsToContents()
    
    def _load_from_file(self):
        """Load IP addresses from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load IP Addresses",
            "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.batch_input_edit.setPlainText(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def _export_results(self):
        """Export batch results to file"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No results to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results",
            "ip_conversion_results.txt",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.csv'):
                        # CSV format
                        f.write("Input,Output,Status,Error\n")
                        for row in range(self.results_table.rowCount()):
                            input_ip = self.results_table.item(row, 0).text()
                            output = self.results_table.item(row, 1).text()
                            status = self.results_table.item(row, 2).text()
                            error = self.results_table.item(row, 3).text()
                            f.write(f'"{input_ip}","{output}","{status}","{error}"\n')
                    else:
                        # Text format
                        f.write("=== IP Conversion Results ===\n\n")
                        for row in range(self.results_table.rowCount()):
                            input_ip = self.results_table.item(row, 0).text()
                            output = self.results_table.item(row, 1).text()
                            status = self.results_table.item(row, 2).text()
                            error = self.results_table.item(row, 3).text()
                            f.write(f"Input: {input_ip}\n")
                            f.write(f"Output: {output}\n")
                            f.write(f"Status: {status}\n")
                            if error:
                                f.write(f"Error: {error}\n")
                            f.write("-" * 40 + "\n")
                
                QMessageBox.information(self, "Success", f"Results exported to:\n{file_path}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export results:\n{str(e)}")
    
    def _clear_batch_input(self):
        """Clear batch input"""
        self.batch_input_edit.clear()
    
    def _clear_all(self):
        """Clear all inputs and results"""
        self.single_input_edit.clear()
        self.single_output_edit.clear()
        self.batch_input_edit.clear()
        self.info_input_edit.clear()
        self.info_results_edit.clear()
        self.dns_value_edit.clear()
        self.dns_result_edit.clear()
        self.dns_batch_edit.clear()
        
        # Clear tables
        self.results_table.setRowCount(0)
        self.dns_results_table.setRowCount(0)
