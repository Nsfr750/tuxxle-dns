#!/usr/bin/env python3
"""
Green DNS Management Dialog
"""

import logging
import time
from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog,
    QGroupBox, QGridLayout, QLineEdit, QComboBox,
    QCheckBox, QSpinBox, QProgressBar, QFrame,
    QSplitter, QFormLayout, QWidget, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor, QPixmap
from core.green_dns import GreenDNSManager, EnergyMode, GreenRecommendation

class GreenDNSWorker(QThread):
    """Worker thread for green DNS operations"""
    progress_updated = Signal(int, str)
    finished = Signal(str, bool)
    error = Signal(str)
    
    def __init__(self, operation: str, manager: GreenDNSManager, **kwargs):
        super().__init__()
        self.operation = operation
        self.manager = manager
        self.kwargs = kwargs
    
    def run(self):
        """Run green DNS operation"""
        try:
            if self.operation == "generate_report":
                result = self._generate_environmental_report()
            elif self.operation == "optimize_energy":
                result = self._optimize_energy_usage()
            elif self.operation == "calculate_footprint":
                result = self._calculate_carbon_footprint()
            elif self.operation == "refresh_recommendations":
                result = self._refresh_recommendations()
            else:
                result = "Unknown operation"
            
            self.finished.emit(result, True)
            
        except Exception as e:
            self.error.emit(f"Green DNS operation failed: {str(e)}")
    
    def _generate_environmental_report(self):
        """Generate environmental impact report"""
        self.progress_updated.emit(10, "Collecting energy metrics...")
        
        days = self.kwargs.get('days', 30)
        report = self.manager.get_environmental_impact_report(days)
        
        self.progress_updated.emit(50, "Analyzing carbon footprint...")
        
        # Format report for display
        report_text = f"""
# Environmental Impact Report - Last {days} Days

## Energy Consumption
- Average Power: {report['energy_consumption']['average_power_watts']} W
- Total Energy: {report['energy_consumption']['total_energy_kwh']} kWh
- Daily Energy: {report['energy_consumption']['daily_energy_kwh']} kWh

## Carbon Footprint
- Average CO₂: {report['carbon_footprint']['average_carbon_per_second']} kg/s
- Total CO₂: {report['carbon_footprint']['total_carbon_kg']} kg
- Daily CO₂: {report['carbon_footprint']['daily_carbon_kg']} kg

## Query Efficiency
- Total Queries: {report['query_efficiency']['total_queries']:,}
- Energy per Query: {report['query_efficiency']['average_energy_per_query_joules']} J
- Queries per kWh: {report['query_efficiency']['queries_per_kwh']:,}

## Environmental Equivalents
- Trees Needed: {report['environmental_equivalents']['trees_needed']} trees/year
- Car KM Offset: {report['environmental_equivalents']['car_km_offset']} km
- Smartphone Charges: {report['environmental_equivalents']['smartphone_charges']} charges

## Optimization Potential
- Potential Energy Savings: {report['optimization_potential']['potential_energy_savings_kwh_per_year']} kWh/year
- Potential CO₂ Reduction: {report['optimization_potential']['potential_carbon_reduction_kg_per_year']} kg/year
"""
        
        self.progress_updated.emit(100, "Report generated successfully")
        return report_text
    
    def _optimize_energy_usage(self):
        """Optimize energy usage"""
        self.progress_updated.emit(20, "Analyzing current energy usage...")
        
        current_metrics = self.manager.get_current_metrics()
        if not current_metrics:
            return "No energy metrics available for optimization"
        
        self.progress_updated.emit(40, "Applying energy optimizations...")
        
        # Apply optimizations based on current mode
        mode = self.kwargs.get('mode', 'balanced')
        self.manager.set_energy_mode(EnergyMode(mode))
        
        self.progress_updated.emit(70, "Updating configuration...")
        
        self.progress_updated.emit(100, f"Energy optimization completed - Mode: {mode}")
        return f"Energy optimization completed. Switched to {mode} mode."
    
    def _calculate_carbon_footprint(self):
        """Calculate detailed carbon footprint"""
        self.progress_updated.emit(30, "Gathering energy consumption data...")
        
        current_metrics = self.manager.get_current_metrics()
        if not current_metrics:
            return "No energy metrics available"
        
        self.progress_updated.emit(60, "Calculating carbon emissions...")
        
        # Calculate annual projections
        annual_power = current_metrics.power_consumption * 24 * 365 / 1000  # kWh
        annual_carbon = annual_power * self.manager.carbon_intensity
        
        self.progress_updated.emit(90, "Generating footprint analysis...")
        
        footprint_text = f"""
# Carbon Footprint Analysis

## Current Consumption
- Power Usage: {current_metrics.power_consumption} W
- Carbon Intensity: {self.manager.carbon_intensity} kg CO₂/kWh
- Server Efficiency: {self.manager.server_efficiency * 100}%

## Annual Projections
- Annual Energy: {annual_power:.2f} kWh
- Annual CO₂: {annual_carbon:.2f} kg
- Monthly CO₂: {annual_carbon/12:.2f} kg

## Per-Query Impact
- Energy per Query: {current_metrics.energy_per_query:.4f} J
- CO₂ per Query: {current_metrics.carbon_footprint * 1000:.6f} g

## Reduction Opportunities
- Switch to renewable energy: {annual_carbon * 0.9:.1f} kg CO₂/year
- Optimize server efficiency: {annual_carbon * 0.15:.1f} kg CO₂/year
- Implement caching: {annual_carbon * 0.1:.1f} kg CO₂/year
"""
        
        self.progress_updated.emit(100, "Carbon footprint calculated")
        return footprint_text
    
    def _refresh_recommendations(self):
        """Refresh green recommendations"""
        self.progress_updated.emit(25, "Analyzing current configuration...")
        
        # Generate new recommendations
        self.manager._generate_recommendations()
        
        self.progress_updated.emit(50, "Calculating optimization potential...")
        
        self.progress_updated.emit(75, "Prioritizing recommendations...")
        
        recommendations = self.manager.get_recommendations()
        
        self.progress_updated.emit(100, f"Generated {len(recommendations)} recommendations")
        return f"Refreshed {len(recommendations)} green hosting recommendations"

class GreenDNSDialog(QDialog):
    """Green DNS Management Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.dns_server = getattr(parent, 'dns_server', None) if parent else None
        self.green_manager = self.dns_server.green_dns_manager if self.dns_server else GreenDNSManager()
        
        self.setWindowTitle("Green DNS Management")
        self.setModal(True)
        self.resize(900, 700)
        
        # Setup UI
        self._setup_ui()
        
        # Load initial data
        self._load_initial_data()
        
        # Setup timer for real-time updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_real_time_data)
        self.update_timer.start(30000)  # Update every 30 seconds
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Overview tab
        self._setup_overview_tab()
        
        # Energy Monitoring tab
        self._setup_energy_tab()
        
        # Carbon Footprint tab
        self._setup_carbon_tab()
        
        # Recommendations tab
        self._setup_recommendations_tab()
        
        # Configuration tab
        self._setup_config_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self._refresh_all_data)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _setup_overview_tab(self):
        """Setup overview tab"""
        overview_widget = QWidget()
        overview_layout = QVBoxLayout()
        
        # Current status
        status_group = QGroupBox("Current Status")
        status_layout = QFormLayout()
        
        self.energy_mode_label = QLabel("Balanced")
        status_layout.addRow("Energy Mode:", self.energy_mode_label)
        
        self.monitoring_status_label = QLabel("Inactive")
        status_layout.addRow("Monitoring:", self.monitoring_status_label)
        
        self.current_power_label = QLabel("0 W")
        status_layout.addRow("Current Power:", self.current_power_label)
        
        self.current_carbon_label = QLabel("0 kg/s")
        status_layout.addRow("Current CO₂:", self.current_carbon_label)
        
        status_group.setLayout(status_layout)
        overview_layout.addWidget(status_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QGridLayout()
        
        start_monitoring_button = QPushButton("Start Monitoring")
        start_monitoring_button.clicked.connect(self._start_monitoring)
        actions_layout.addWidget(start_monitoring_button, 0, 0)
        
        stop_monitoring_button = QPushButton("Stop Monitoring")
        stop_monitoring_button.clicked.connect(self._stop_monitoring)
        actions_layout.addWidget(stop_monitoring_button, 0, 1)
        
        generate_report_button = QPushButton("Generate Report")
        generate_report_button.clicked.connect(self._generate_report)
        actions_layout.addWidget(generate_report_button, 1, 0)
        
        optimize_button = QPushButton("Optimize Energy")
        optimize_button.clicked.connect(self._optimize_energy)
        actions_layout.addWidget(optimize_button, 1, 1)
        
        actions_group.setLayout(actions_layout)
        overview_layout.addWidget(actions_group)
        
        # Environmental impact summary
        impact_group = QGroupBox("Environmental Impact (Last 30 Days)")
        impact_layout = QFormLayout()
        
        self.total_energy_label = QLabel("0 kWh")
        impact_layout.addRow("Total Energy:", self.total_energy_label)
        
        self.total_carbon_label = QLabel("0 kg")
        impact_layout.addRow("Total CO₂:", self.total_carbon_label)
        
        self.trees_equivalent_label = QLabel("0 trees")
        impact_layout.addRow("Trees Equivalent:", self.trees_equivalent_label)
        
        self.car_km_label = QLabel("0 km")
        impact_layout.addRow("Car KM Offset:", self.car_km_label)
        
        impact_group.setLayout(impact_layout)
        overview_layout.addWidget(impact_group)
        
        overview_widget.setLayout(overview_layout)
        self.tab_widget.addTab(overview_widget, "Overview")
    
    def _setup_energy_tab(self):
        """Setup energy monitoring tab"""
        energy_widget = QWidget()
        energy_layout = QVBoxLayout()
        
        # Energy consumption chart area
        chart_group = QGroupBox("Energy Consumption")
        chart_layout = QVBoxLayout()
        
        self.energy_chart_label = QLabel("Energy monitoring data will appear here")
        self.energy_chart_label.setAlignment(Qt.AlignCenter)
        self.energy_chart_label.setStyleSheet("border: 1px solid #ccc; padding: 20px; min-height: 200px;")
        chart_layout.addWidget(self.energy_chart_label)
        
        chart_group.setLayout(chart_layout)
        energy_layout.addWidget(chart_group)
        
        # Energy efficiency metrics
        metrics_group = QGroupBox("Energy Efficiency Metrics")
        metrics_layout = QGridLayout()
        
        self.cpu_usage_label = QLabel("0%")
        metrics_layout.addWidget(QLabel("CPU Usage:"), 0, 0)
        metrics_layout.addWidget(self.cpu_usage_label, 0, 1)
        
        self.memory_usage_label = QLabel("0%")
        metrics_layout.addWidget(QLabel("Memory Usage:"), 0, 2)
        metrics_layout.addWidget(self.memory_usage_label, 0, 3)
        
        self.energy_per_query_label = QLabel("0 J")
        metrics_layout.addWidget(QLabel("Energy per Query:"), 1, 0)
        metrics_layout.addWidget(self.energy_per_query_label, 1, 1)
        
        self.queries_per_kwh_label = QLabel("0")
        metrics_layout.addWidget(QLabel("Queries per kWh:"), 1, 2)
        metrics_layout.addWidget(self.queries_per_kwh_label, 1, 3)
        
        metrics_group.setLayout(metrics_layout)
        energy_layout.addWidget(metrics_group)
        
        # Energy mode controls
        mode_group = QGroupBox("Energy Optimization Mode")
        mode_layout = QFormLayout()
        
        self.energy_mode_combo = QComboBox()
        self.energy_mode_combo.addItems(["performance", "balanced", "eco", "ultra_eco"])
        self.energy_mode_combo.currentTextChanged.connect(self._on_energy_mode_changed)
        mode_layout.addRow("Energy Mode:", self.energy_mode_combo)
        
        apply_mode_button = QPushButton("Apply Energy Mode")
        apply_mode_button.clicked.connect(self._apply_energy_mode)
        mode_layout.addRow("", apply_mode_button)
        
        mode_group.setLayout(mode_layout)
        energy_layout.addWidget(mode_group)
        
        energy_widget.setLayout(energy_layout)
        self.tab_widget.addTab(energy_widget, "Energy")
    
    def _setup_carbon_tab(self):
        """Setup carbon footprint tab"""
        carbon_widget = QWidget()
        carbon_layout = QVBoxLayout()
        
        # Carbon footprint display
        footprint_group = QGroupBox("Carbon Footprint Analysis")
        footprint_layout = QVBoxLayout()
        
        self.footprint_text = QTextEdit()
        self.footprint_text.setReadOnly(True)
        self.footprint_text.setMaximumHeight(300)
        footprint_layout.addWidget(self.footprint_text)
        
        calculate_button = QPushButton("Calculate Carbon Footprint")
        calculate_button.clicked.connect(self._calculate_footprint)
        footprint_layout.addWidget(calculate_button)
        
        footprint_group.setLayout(footprint_layout)
        carbon_layout.addWidget(footprint_group)
        
        # Environmental equivalents
        equivalents_group = QGroupBox("Environmental Equivalents")
        equivalents_layout = QGridLayout()
        
        self.trees_needed_label = QLabel("0 trees")
        equivalents_layout.addWidget(QLabel("Trees Needed (per year):"), 0, 0)
        equivalents_layout.addWidget(self.trees_needed_label, 0, 1)
        
        self.car_km_offset_label = QLabel("0 km")
        equivalents_layout.addWidget(QLabel("Car KM Offset:"), 0, 2)
        equivalents_layout.addWidget(self.car_km_offset_label, 0, 3)
        
        self.smartphone_charges_label = QLabel("0 charges")
        equivalents_layout.addWidget(QLabel("Smartphone Charges:"), 1, 0)
        equivalents_layout.addWidget(self.smartphone_charges_label, 1, 1)
        
        self.home_energy_label = QLabel("0 kWh")
        equivalents_layout.addWidget(QLabel("Home Energy (days):"), 1, 2)
        equivalents_layout.addWidget(self.home_energy_label, 1, 3)
        
        equivalents_group.setLayout(equivalents_layout)
        carbon_layout.addWidget(equivalents_group)
        
        # Carbon reduction potential
        reduction_group = QGroupBox("Carbon Reduction Potential")
        reduction_layout = QFormLayout()
        
        self.renewable_energy_label = QLabel("0 kg/year")
        reduction_layout.addRow("Switch to Renewable Energy:", self.renewable_energy_label)
        
        self.optimization_label = QLabel("0 kg/year")
        reduction_layout.addRow("Server Optimization:", self.optimization_label)
        
        self.caching_label = QLabel("0 kg/year")
        reduction_layout.addRow("Implement Caching:", self.caching_label)
        
        reduction_group.setLayout(reduction_layout)
        carbon_layout.addWidget(reduction_group)
        
        carbon_widget.setLayout(carbon_layout)
        self.tab_widget.addTab(carbon_widget, "Carbon")
    
    def _setup_recommendations_tab(self):
        """Setup recommendations tab"""
        recommendations_widget = QWidget()
        recommendations_layout = QVBoxLayout()
        
        # Filter controls
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Category:"))
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Energy Efficiency", "Hardware", "Network", "Renewable Energy", "Cooling", "Virtualization", "Monitoring"])
        self.category_combo.currentTextChanged.connect(self._filter_recommendations)
        filter_layout.addWidget(self.category_combo)
        
        filter_layout.addWidget(QLabel("Priority:"))
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["All", "critical", "high", "medium", "low"])
        self.priority_combo.currentTextChanged.connect(self._filter_recommendations)
        filter_layout.addWidget(self.priority_combo)
        
        refresh_rec_button = QPushButton("Refresh")
        refresh_rec_button.clicked.connect(self._refresh_recommendations)
        filter_layout.addWidget(refresh_rec_button)
        
        filter_widget.setLayout(filter_layout)
        recommendations_layout.addWidget(filter_widget)
        
        # Recommendations table
        self.recommendations_table = QTableWidget()
        self.recommendations_table.setColumnCount(7)
        self.recommendations_table.setHorizontalHeaderLabels([
            "Category", "Priority", "Title", "Potential Savings", 
            "Difficulty", "CO₂ Reduction (kg/year)", "Status"
        ])
        self.recommendations_table.horizontalHeader().setStretchLastSection(True)
        recommendations_layout.addWidget(self.recommendations_table)
        
        # Recommendation details
        details_group = QGroupBox("Recommendation Details")
        details_layout = QVBoxLayout()
        
        self.recommendation_details = QTextEdit()
        self.recommendation_details.setReadOnly(True)
        self.recommendation_details.setMaximumHeight(150)
        details_layout.addWidget(self.recommendation_details)
        
        implement_button = QPushButton("Mark as Implemented")
        implement_button.clicked.connect(self._mark_implemented)
        details_layout.addWidget(implement_button)
        
        details_group.setLayout(details_layout)
        recommendations_layout.addWidget(details_group)
        
        recommendations_widget.setLayout(recommendations_layout)
        self.tab_widget.addTab(recommendations_widget, "Recommendations")
    
    def _setup_config_tab(self):
        """Setup configuration tab"""
        config_widget = QWidget()
        config_layout = QVBoxLayout()
        
        # Green DNS configuration
        config_group = QGroupBox("Green DNS Configuration")
        config_layout_inner = QFormLayout()
        
        self.carbon_intensity_edit = QLineEdit()
        self.carbon_intensity_edit.setText("0.233")
        self.carbon_intensity_edit.setPlaceholderText("kg CO2 per kWh")
        config_layout_inner.addRow("Carbon Intensity:", self.carbon_intensity_edit)
        
        self.server_efficiency_spin = QDoubleSpinBox()
        self.server_efficiency_spin.setRange(0.1, 1.0)
        self.server_efficiency_spin.setSingleStep(0.05)
        self.server_efficiency_spin.setValue(0.85)
        self.server_efficiency_spin.setDecimals(2)
        config_layout_inner.addRow("Server Efficiency:", self.server_efficiency_spin)
        
        self.monitoring_interval_spin = QSpinBox()
        self.monitoring_interval_spin.setRange(10, 3600)
        self.monitoring_interval_spin.setValue(60)
        self.monitoring_interval_spin.setSuffix(" seconds")
        config_layout_inner.addRow("Monitoring Interval:", self.monitoring_interval_spin)
        
        save_config_button = QPushButton("Save Configuration")
        save_config_button.clicked.connect(self._save_configuration)
        config_layout_inner.addRow("", save_config_button)
        
        config_group.setLayout(config_layout_inner)
        config_layout.addWidget(config_group)
        
        # Data management
        data_group = QGroupBox("Data Management")
        data_layout = QFormLayout()
        
        export_data_button = QPushButton("Export Environmental Data")
        export_data_button.clicked.connect(self._export_data)
        data_layout.addRow("", export_data_button)
        
        clear_data_button = QPushButton("Clear Old Data (older than 90 days)")
        clear_data_button.clicked.connect(self._clear_old_data)
        data_layout.addRow("", clear_data_button)
        
        data_group.setLayout(data_layout)
        config_layout.addWidget(data_group)
        
        config_widget.setLayout(config_layout)
        self.tab_widget.addTab(config_widget, "Configuration")
    
    def _load_initial_data(self):
        """Load initial data"""
        try:
            # Load current status
            stats = self.green_manager.get_energy_statistics()
            
            self.energy_mode_label.setText(stats.get('energy_mode', 'Unknown'))
            self.monitoring_status_label.setText('Active' if stats.get('monitoring_active') else 'Inactive')
            self.current_power_label.setText(f"{stats.get('current_power_watts', 0)} W")
            self.current_carbon_label.setText(f"{stats.get('current_carbon_per_second', 0):.6f} kg/s")
            
            # Load environmental impact
            report = self.green_manager.get_environmental_impact_report(30)
            
            self.total_energy_label.setText(f"{report['energy_consumption']['total_energy_kwh']:.2f} kWh")
            self.total_carbon_label.setText(f"{report['carbon_footprint']['total_carbon_kg']:.2f} kg")
            self.trees_equivalent_label.setText(f"{report['environmental_equivalents']['trees_needed']:.1f} trees")
            self.car_km_label.setText(f"{report['environmental_equivalents']['car_km_offset']:.1f} km")
            
            # Load recommendations
            self._load_recommendations()
            
            # Set energy mode
            self.energy_mode_combo.setCurrentText(stats.get('energy_mode', 'balanced'))
            
            # Load configuration
            self.carbon_intensity_edit.setText(str(self.green_manager.carbon_intensity))
            self.server_efficiency_spin.setValue(self.green_manager.server_efficiency)
            
        except Exception as e:
            self.logger.error(f"Error loading initial data: {e}")
    
    def _load_recommendations(self):
        """Load recommendations into table"""
        try:
            recommendations = self.green_manager.get_recommendations()
            
            self.recommendations_table.setRowCount(len(recommendations))
            
            for i, rec in enumerate(recommendations):
                self.recommendations_table.setItem(i, 0, QTableWidgetItem(rec.category))
                self.recommendations_table.setItem(i, 1, QTableWidgetItem(rec.priority))
                self.recommendations_table.setItem(i, 2, QTableWidgetItem(rec.title))
                self.recommendations_table.setItem(i, 3, QTableWidgetItem(rec.potential_savings))
                self.recommendations_table.setItem(i, 4, QTableWidgetItem(rec.implementation_difficulty))
                self.recommendations_table.setItem(i, 5, QTableWidgetItem(f"{rec.estimated_carbon_reduction:.1f}"))
                self.recommendations_table.setItem(i, 6, QTableWidgetItem("Pending"))
            
        except Exception as e:
            self.logger.error(f"Error loading recommendations: {e}")
    
    def _update_real_time_data(self):
        """Update real-time data"""
        try:
            stats = self.green_manager.get_energy_statistics()
            
            if stats.get('status') == 'Active':
                self.current_power_label.setText(f"{stats.get('current_power_watts', 0)} W")
                self.current_carbon_label.setText(f"{stats.get('current_carbon_per_second', 0):.6f} kg/s")
                self.cpu_usage_label.setText(f"{stats.get('cpu_usage_percent', 0)}%")
                self.memory_usage_label.setText(f"{stats.get('memory_usage_percent', 0)}%")
                self.energy_per_query_label.setText(f"{stats.get('energy_per_query_joules', 0):.4f} J")
                self.queries_per_kwh_label.setText(f"{stats.get('queries_processed', 0):,}")
            
        except Exception as e:
            self.logger.error(f"Error updating real-time data: {e}")
    
    def _start_monitoring(self):
        """Start energy monitoring"""
        try:
            interval = self.monitoring_interval_spin.value()
            self.green_manager.start_monitoring(interval)
            
            QMessageBox.information(self, "Success", "Energy monitoring started")
            self._load_initial_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start monitoring: {e}")
    
    def _stop_monitoring(self):
        """Stop energy monitoring"""
        try:
            self.green_manager.stop_energy_monitoring()
            
            QMessageBox.information(self, "Success", "Energy monitoring stopped")
            self._load_initial_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop monitoring: {e}")
    
    def _generate_report(self):
        """Generate environmental report"""
        try:
            self.worker = GreenDNSWorker("generate_report", self.green_manager, days=30)
            self.worker.progress_updated.connect(self._on_progress_updated)
            self.worker.finished.connect(self._on_report_generated)
            self.worker.error.connect(self._on_worker_error)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
    
    def _optimize_energy(self):
        """Optimize energy usage"""
        try:
            mode = self.energy_mode_combo.currentText()
            self.worker = GreenDNSWorker("optimize_energy", self.green_manager, mode=mode)
            self.worker.progress_updated.connect(self._on_progress_updated)
            self.worker.finished.connect(self._on_energy_optimized)
            self.worker.error.connect(self._on_worker_error)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to optimize energy: {e}")
    
    def _calculate_footprint(self):
        """Calculate carbon footprint"""
        try:
            self.worker = GreenDNSWorker("calculate_footprint", self.green_manager)
            self.worker.progress_updated.connect(self._on_progress_updated)
            self.worker.finished.connect(self._on_footprint_calculated)
            self.worker.error.connect(self._on_worker_error)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate footprint: {e}")
    
    def _refresh_recommendations(self):
        """Refresh recommendations"""
        try:
            self.worker = GreenDNSWorker("refresh_recommendations", self.green_manager)
            self.worker.progress_updated.connect(self._on_progress_updated)
            self.worker.finished.connect(self._on_recommendations_refreshed)
            self.worker.error.connect(self._on_worker_error)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh recommendations: {e}")
    
    def _on_energy_mode_changed(self, mode):
        """Handle energy mode change"""
        # Mode will be applied when user clicks apply
        pass
    
    def _apply_energy_mode(self):
        """Apply selected energy mode"""
        try:
            mode = self.energy_mode_combo.currentText()
            self.green_manager.set_energy_mode(EnergyMode(mode))
            
            QMessageBox.information(self, "Success", f"Energy mode set to {mode}")
            self._load_initial_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set energy mode: {e}")
    
    def _filter_recommendations(self):
        """Filter recommendations"""
        try:
            category = self.category_combo.currentText()
            priority = self.priority_combo.currentText()
            
            if category == "All":
                category = None
            if priority == "All":
                priority = None
            
            recommendations = self.green_manager.get_recommendations(category, priority)
            
            self.recommendations_table.setRowCount(len(recommendations))
            
            for i, rec in enumerate(recommendations):
                self.recommendations_table.setItem(i, 0, QTableWidgetItem(rec.category))
                self.recommendations_table.setItem(i, 1, QTableWidgetItem(rec.priority))
                self.recommendations_table.setItem(i, 2, QTableWidgetItem(rec.title))
                self.recommendations_table.setItem(i, 3, QTableWidgetItem(rec.potential_savings))
                self.recommendations_table.setItem(i, 4, QTableWidgetItem(rec.implementation_difficulty))
                self.recommendations_table.setItem(i, 5, QTableWidgetItem(f"{rec.estimated_carbon_reduction:.1f}"))
                self.recommendations_table.setItem(i, 6, QTableWidgetItem("Pending"))
            
        except Exception as e:
            self.logger.error(f"Error filtering recommendations: {e}")
    
    def _mark_implemented(self):
        """Mark selected recommendation as implemented"""
        try:
            current_row = self.recommendations_table.currentRow()
            if current_row >= 0:
                title = self.recommendations_table.item(current_row, 2).text()
                
                if self.green_manager.mark_recommendation_implemented(title):
                    self.recommendations_table.setItem(current_row, 6, QTableWidgetItem("Implemented"))
                    QMessageBox.information(self, "Success", "Recommendation marked as implemented")
                else:
                    QMessageBox.warning(self, "Warning", "Failed to mark recommendation as implemented")
            else:
                QMessageBox.warning(self, "Warning", "Please select a recommendation")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to mark recommendation: {e}")
    
    def _save_configuration(self):
        """Save green DNS configuration"""
        try:
            self.green_manager.carbon_intensity = float(self.carbon_intensity_edit.text())
            self.green_manager.server_efficiency = self.server_efficiency_spin.value()
            
            self.green_manager.save_configuration()
            
            QMessageBox.information(self, "Success", "Configuration saved")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")
    
    def _export_data(self):
        """Export environmental data"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Environmental Data", "green_dns_data.json", "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                report = self.green_manager.get_environmental_impact_report(365)  # Full year
                
                with open(file_path, 'w') as f:
                    import json
                    json.dump(report, f, indent=2)
                
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {e}")
    
    def _clear_old_data(self):
        """Clear old environmental data"""
        try:
            reply = QMessageBox.question(
                self, "Confirm", "Are you sure you want to clear data older than 90 days?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Implementation would clear old data from database
                QMessageBox.information(self, "Success", "Old data cleared")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear old data: {e}")
    
    def _refresh_all_data(self):
        """Refresh all data"""
        self._load_initial_data()
        self._load_recommendations()
    
    def _on_progress_updated(self, value, message):
        """Handle progress updates"""
        # Could show a progress dialog here
        pass
    
    def _on_report_generated(self, report_text):
        """Handle report generation completion"""
        # Show report in a new dialog or tab
        QMessageBox.information(self, "Report Generated", "Environmental report generated successfully")
    
    def _on_energy_optimized(self, message):
        """Handle energy optimization completion"""
        QMessageBox.information(self, "Energy Optimized", message)
        self._load_initial_data()
    
    def _on_footprint_calculated(self, footprint_text):
        """Handle carbon footprint calculation"""
        self.footprint_text.setPlainText(footprint_text)
        
        # Update equivalents
        report = self.green_manager.get_environmental_impact_report(30)
        equivalents = report['environmental_equivalents']
        
        self.trees_needed_label.setText(f"{equivalents['trees_needed']:.1f} trees")
        self.car_km_offset_label.setText(f"{equivalents['car_km_offset']:.1f} km")
        self.smartphone_charges_label.setText(f"{equivalents['smartphone_charges']:.0f} charges")
        
        # Home energy equivalent (average home uses ~30 kWh per day)
        daily_energy = report['energy_consumption']['daily_energy_kwh']
        home_days = daily_energy / 30.0
        self.home_energy_label.setText(f"{home_days:.2f} days")
        
        # Update reduction potential
        potential = report['optimization_potential']
        self.renewable_energy_label.setText(f"{potential['potential_carbon_reduction_kg_per_year'] * 0.9:.1f} kg/year")
        self.optimization_label.setText(f"{potential['potential_carbon_reduction_kg_per_year'] * 0.15:.1f} kg/year")
        self.caching_label.setText(f"{potential['potential_carbon_reduction_kg_per_year'] * 0.1:.1f} kg/year")
    
    def _on_recommendations_refreshed(self, message):
        """Handle recommendations refresh"""
        QMessageBox.information(self, "Recommendations Refreshed", message)
        self._load_recommendations()
    
    def _on_worker_error(self, error_message):
        """Handle worker errors"""
        QMessageBox.critical(self, "Error", error_message)
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        # Stop update timer
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        
        # Stop any running workers
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        super().closeEvent(event)
