#!/usr/bin/env python3
"""
Green DNS - Energy usage optimization and carbon footprint tracking
"""

import psutil
import time
import json
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import sqlite3
import os

class EnergyMode(Enum):
    """Energy optimization modes"""
    PERFORMANCE = "performance"
    BALANCED = "balanced"
    ECO = "eco"
    ULTRA_ECO = "ultra_eco"

@dataclass
class EnergyMetrics:
    """Energy consumption metrics"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    network_io: Dict[str, int]
    disk_io: Dict[str, int]
    power_consumption: float  # Watts
    carbon_footprint: float   # kg CO2
    queries_processed: int
    energy_per_query: float  # Joules per query

@dataclass
class GreenRecommendation:
    """Green hosting recommendation"""
    category: str
    priority: str  # low, medium, high, critical
    title: str
    description: str
    potential_savings: str
    implementation_difficulty: str
    estimated_carbon_reduction: float  # kg CO2 per year

class GreenDNSManager:
    """Green DNS management and optimization"""
    
    def __init__(self, db_path: str = "config/green_dns.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.energy_mode = EnergyMode.BALANCED
        self.carbon_intensity = 0.233  # kg CO2 per kWh (global average)
        self.server_efficiency = 0.85   # PSU efficiency
        self.metrics_history: List[EnergyMetrics] = []
        self.recommendations: List[GreenRecommendation] = []
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_monitoring = False
        
        # Initialize database
        self._init_database()
        
        # Load configuration
        self._load_configuration()
        
        # Generate initial recommendations
        self._generate_recommendations()
    
    def _init_database(self):
        """Initialize green DNS database"""
        try:
            # Ensure database directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create energy metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS energy_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    cpu_usage REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    network_read INTEGER NOT NULL,
                    network_write INTEGER NOT NULL,
                    disk_read INTEGER NOT NULL,
                    disk_write INTEGER NOT NULL,
                    power_consumption REAL NOT NULL,
                    carbon_footprint REAL NOT NULL,
                    queries_processed INTEGER NOT NULL,
                    energy_per_query REAL NOT NULL
                )
            ''')
            
            # Create recommendations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    potential_savings TEXT NOT NULL,
                    implementation_difficulty TEXT NOT NULL,
                    estimated_carbon_reduction REAL NOT NULL,
                    created_at REAL NOT NULL,
                    implemented BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Create configuration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS green_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Green DNS database initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing green DNS database: {e}")
    
    def _load_configuration(self):
        """Load green DNS configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT key, value FROM green_config")
            config_data = cursor.fetchall()
            
            config = dict(config_data)
            
            # Load energy mode
            if 'energy_mode' in config:
                self.energy_mode = EnergyMode(config['energy_mode'])
            
            # Load carbon intensity
            if 'carbon_intensity' in config:
                self.carbon_intensity = float(config['carbon_intensity'])
            
            # Load server efficiency
            if 'server_efficiency' in config:
                self.server_efficiency = float(config['server_efficiency'])
            
            conn.close()
            
            self.logger.info(f"Loaded green DNS configuration: mode={self.energy_mode.value}")
            
        except Exception as e:
            self.logger.error(f"Error loading green DNS configuration: {e}")
    
    def save_configuration(self):
        """Save green DNS configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = time.time()
            
            # Save configuration
            config_data = [
                ('energy_mode', self.energy_mode.value, current_time),
                ('carbon_intensity', str(self.carbon_intensity), current_time),
                ('server_efficiency', str(self.server_efficiency), current_time)
            ]
            
            cursor.executemany('''
                INSERT OR REPLACE INTO green_config (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', config_data)
            
            conn.commit()
            conn.close()
            
            self.logger.info("Green DNS configuration saved")
            
        except Exception as e:
            self.logger.error(f"Error saving green DNS configuration: {e}")
    
    def start_monitoring(self, interval: int = 60):
        """Start energy monitoring"""
        if self.monitoring_active:
            self.logger.warning("Energy monitoring already active")
            return
        
        self.monitoring_active = True
        self.stop_monitoring = False
        
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info(f"Started energy monitoring with {interval}s interval")
    
    def stop_energy_monitoring(self):
        """Stop energy monitoring"""
        if not self.monitoring_active:
            return
        
        self.stop_monitoring = True
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("Stopped energy monitoring")
    
    def _monitoring_loop(self, interval: int):
        """Main monitoring loop"""
        while self.monitoring_active and not self.stop_monitoring:
            try:
                metrics = self._collect_energy_metrics()
                if metrics:
                    self._save_metrics(metrics)
                    self.metrics_history.append(metrics)
                    
                    # Keep only last 24 hours of data
                    cutoff_time = time.time() - 86400
                    self.metrics_history = [
                        m for m in self.metrics_history 
                        if m.timestamp > cutoff_time
                    ]
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _collect_energy_metrics(self) -> Optional[EnergyMetrics]:
        """Collect current energy metrics"""
        try:
            # Get system metrics (non-blocking)
            cpu_percent = psutil.cpu_percent(interval=0)
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()
            disk = psutil.disk_io_counters()
            
            # Calculate power consumption
            power_consumption = self._calculate_power_consumption(cpu_percent, memory.percent)
            
            # Calculate carbon footprint
            carbon_footprint = self._calculate_carbon_footprint(power_consumption)
            
            # Get query count (would be passed from DNS server)
            queries_processed = self._get_query_count()
            
            # Calculate energy per query
            energy_per_query = (power_consumption * 3600) / max(queries_processed, 1)  # Joules per query
            
            metrics = EnergyMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                disk_io={
                    'bytes_read': disk.read_bytes if disk else 0,
                    'bytes_written': disk.write_bytes if disk else 0
                },
                power_consumption=power_consumption,
                carbon_footprint=carbon_footprint,
                queries_processed=queries_processed,
                energy_per_query=energy_per_query
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting energy metrics: {e}")
            return None
    
    def _calculate_power_consumption(self, cpu_usage: float, memory_usage: float) -> float:
        """Calculate power consumption in watts"""
        try:
            # Base power consumption (idle)
            base_power = 50.0  # watts
            
            # CPU power contribution
            cpu_power = (cpu_usage / 100.0) * 65.0  # Max 65W for CPU
            
            # Memory power contribution
            memory_power = (memory_usage / 100.0) * 20.0  # Max 20W for memory
            
            # Network and disk power
            network_power = 5.0  # Constant network power
            disk_power = 10.0    # Constant disk power
            
            # Apply energy mode efficiency
            mode_multiplier = self._get_energy_mode_multiplier()
            
            total_power = (base_power + cpu_power + memory_power + network_power + disk_power) * mode_multiplier
            
            # Apply PSU efficiency
            total_power = total_power / self.server_efficiency
            
            return round(total_power, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating power consumption: {e}")
            return 100.0  # Default estimate
    
    def _get_energy_mode_multiplier(self) -> float:
        """Get power multiplier based on energy mode"""
        multipliers = {
            EnergyMode.PERFORMANCE: 1.0,
            EnergyMode.BALANCED: 0.85,
            EnergyMode.ECO: 0.70,
            EnergyMode.ULTRA_ECO: 0.55
        }
        return multipliers.get(self.energy_mode, 1.0)
    
    def _calculate_carbon_footprint(self, power_watts: float) -> float:
        """Calculate carbon footprint in kg CO2"""
        try:
            # Convert watts to kWh per hour
            power_kwh = power_watts / 1000.0
            
            # Calculate CO2 per hour
            co2_per_hour = power_kwh * self.carbon_intensity
            
            # Convert to kg CO2 per second (for current moment)
            co2_per_second = co2_per_hour / 3600.0
            
            return round(co2_per_second, 6)
            
        except Exception as e:
            self.logger.error(f"Error calculating carbon footprint: {e}")
            return 0.0
    
    def _get_query_count(self) -> int:
        """Get current query count (placeholder)"""
        # This would be integrated with the DNS server
        # For now, return a simulated value
        return 1000
    
    def _save_metrics(self, metrics: EnergyMetrics):
        """Save energy metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO energy_metrics (
                    timestamp, cpu_usage, memory_usage, network_read, network_write,
                    disk_read, disk_write, power_consumption, carbon_footprint,
                    queries_processed, energy_per_query
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp,
                metrics.cpu_usage,
                metrics.memory_usage,
                metrics.network_io['bytes_sent'],
                metrics.network_io['bytes_recv'],
                metrics.disk_io['bytes_read'],
                metrics.disk_io['bytes_written'],
                metrics.power_consumption,
                metrics.carbon_footprint,
                metrics.queries_processed,
                metrics.energy_per_query
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving energy metrics: {e}")
    
    def _generate_recommendations(self):
        """Generate green hosting recommendations"""
        self.recommendations = []
        
        # Energy efficiency recommendations
        self.recommendations.extend([
            GreenRecommendation(
                category="Energy Efficiency",
                priority="high",
                title="Enable CPU Frequency Scaling",
                description="Configure CPU scaling governor to 'ondemand' or 'powersave' to reduce power consumption during low load periods.",
                potential_savings="15-25% power reduction",
                implementation_difficulty="medium",
                estimated_carbon_reduction=50.0
            ),
            GreenRecommendation(
                category="Energy Efficiency",
                priority="medium",
                title="Optimize DNS Query Caching",
                description="Increase DNS cache size and TTL to reduce external queries and computational overhead.",
                potential_savings="10-20% reduction in query processing",
                implementation_difficulty="low",
                estimated_carbon_reduction=30.0
            ),
            GreenRecommendation(
                category="Hardware",
                priority="high",
                title="Use SSD Storage",
                description="Replace traditional HDDs with SSDs to reduce power consumption and improve query response times.",
                potential_savings="40-60% storage power reduction",
                implementation_difficulty="high",
                estimated_carbon_reduction=80.0
            ),
            GreenRecommendation(
                category="Network",
                priority="medium",
                title="Enable DNS Response Compression",
                description="Implement DNS response compression to reduce network bandwidth usage and transmission energy.",
                potential_savings="20-30% bandwidth reduction",
                implementation_difficulty="medium",
                estimated_carbon_reduction=25.0
            ),
            GreenRecommendation(
                category="Renewable Energy",
                priority="critical",
                title="Switch to Renewable Energy Provider",
                description="Move your hosting to a data center powered by renewable energy sources.",
                potential_savings="80-95% carbon footprint reduction",
                implementation_difficulty="high",
                estimated_carbon_reduction=500.0
            ),
            GreenRecommendation(
                category="Cooling",
                priority="medium",
                title="Optimize Server Cooling",
                description="Implement hot aisle/cold aisle containment and raise ambient temperature to reduce cooling costs.",
                potential_savings="15-25% cooling energy reduction",
                implementation_difficulty="high",
                estimated_carbon_reduction=60.0
            ),
            GreenRecommendation(
                category="Virtualization",
                priority="low",
                title="Consolidate Servers",
                description="Use virtualization to consolidate multiple DNS servers onto fewer physical machines.",
                potential_savings="30-50% hardware reduction",
                implementation_difficulty="medium",
                estimated_carbon_reduction=100.0
            ),
            GreenRecommendation(
                category="Monitoring",
                priority="medium",
                title="Implement Real-time Energy Monitoring",
                description="Deploy detailed energy monitoring to identify optimization opportunities and track improvements.",
                potential_savings="5-15% through optimization",
                implementation_difficulty="low",
                estimated_carbon_reduction=20.0
            )
        ])
        
        # Save recommendations to database
        self._save_recommendations()
    
    def _save_recommendations(self):
        """Save recommendations to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = time.time()
            
            for rec in self.recommendations:
                cursor.execute('''
                    INSERT OR REPLACE INTO recommendations (
                        category, priority, title, description, potential_savings,
                        implementation_difficulty, estimated_carbon_reduction, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rec.category, rec.priority, rec.title, rec.description,
                    rec.potential_savings, rec.implementation_difficulty,
                    rec.estimated_carbon_reduction, current_time
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving recommendations: {e}")
    
    def set_energy_mode(self, mode: EnergyMode):
        """Set energy optimization mode"""
        old_mode = self.energy_mode
        self.energy_mode = mode
        
        self.logger.info(f"Energy mode changed from {old_mode.value} to {mode.value}")
        
        # Save configuration
        self.save_configuration()
        
        # Apply mode-specific optimizations
        self._apply_energy_mode_optimizations()
    
    def _apply_energy_mode_optimizations(self):
        """Apply optimizations based on current energy mode"""
        try:
            if self.energy_mode == EnergyMode.ULTRA_ECO:
                # Ultra eco mode optimizations
                self._optimize_for_ultra_eco()
            elif self.energy_mode == EnergyMode.ECO:
                # Eco mode optimizations
                self._optimize_for_eco()
            elif self.energy_mode == EnergyMode.BALANCED:
                # Balanced mode optimizations
                self._optimize_for_balanced()
            elif self.energy_mode == EnergyMode.PERFORMANCE:
                # Performance mode (minimal optimizations)
                self._optimize_for_performance()
                
        except Exception as e:
            self.logger.error(f"Error applying energy mode optimizations: {e}")
    
    def _optimize_for_ultra_eco(self):
        """Apply ultra eco optimizations"""
        # Reduce query processing threads
        # Increase cache sizes
        # Enable aggressive power saving
        pass
    
    def _optimize_for_eco(self):
        """Apply eco optimizations"""
        # Moderate power saving settings
        pass
    
    def _optimize_for_balanced(self):
        """Apply balanced optimizations"""
        # Balanced performance and efficiency
        pass
    
    def _optimize_for_performance(self):
        """Apply performance optimizations"""
        # Maximum performance, minimal power saving
        pass
    
    def get_environmental_impact_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive environmental impact report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get metrics for the specified period
            cutoff_time = time.time() - (days * 86400)
            
            cursor.execute('''
                SELECT 
                    AVG(power_consumption) as avg_power,
                    AVG(carbon_footprint) as avg_carbon,
                    SUM(queries_processed) as total_queries,
                    AVG(energy_per_query) as avg_energy_per_query,
                    COUNT(*) as data_points
                FROM energy_metrics
                WHERE timestamp > ?
            ''', (cutoff_time,))
            
            result = cursor.fetchone()
            
            if not result or result[4] == 0:
                conn.close()
                return self._get_empty_report(days)
            
            avg_power, avg_carbon, total_queries, avg_energy_per_query, data_points = result
            
            # Calculate totals
            total_hours = days * 24
            total_power_kwh = (avg_power / 1000.0) * total_hours
            total_carbon_kg = avg_carbon * total_hours * 3600  # Convert from per-second to total
            
            # Get recommendations status
            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN implemented = 1 THEN 1 ELSE 0 END) as implemented
                FROM recommendations
            ''')
            
            rec_result = cursor.fetchone()
            total_recommendations, implemented_recommendations = rec_result
            
            conn.close()
            
            report = {
                'period_days': days,
                'data_points': data_points,
                'energy_consumption': {
                    'average_power_watts': round(avg_power, 2),
                    'total_energy_kwh': round(total_power_kwh, 2),
                    'daily_energy_kwh': round(total_power_kwh / days, 2)
                },
                'carbon_footprint': {
                    'average_carbon_per_second': round(avg_carbon, 6),
                    'total_carbon_kg': round(total_carbon_kg, 2),
                    'daily_carbon_kg': round(total_carbon_kg / days, 2)
                },
                'query_efficiency': {
                    'total_queries': total_queries,
                    'average_energy_per_query_joules': round(avg_energy_per_query, 4),
                    'queries_per_kwh': round(total_queries / max(total_power_kwh, 0.001), 0)
                },
                'recommendations': {
                    'total': total_recommendations,
                    'implemented': implemented_recommendations,
                    'implementation_rate': round((implemented_recommendations / max(total_recommendations, 1)) * 100, 1)
                },
                'environmental_equivalents': self._calculate_environmental_equivalents(total_carbon_kg),
                'optimization_potential': self._calculate_optimization_potential()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating environmental impact report: {e}")
            return self._get_empty_report(days)
    
    def _get_empty_report(self, days: int) -> Dict[str, Any]:
        """Get empty report when no data available"""
        return {
            'period_days': days,
            'data_points': 0,
            'energy_consumption': {
                'average_power_watts': 0,
                'total_energy_kwh': 0,
                'daily_energy_kwh': 0
            },
            'carbon_footprint': {
                'average_carbon_per_second': 0,
                'total_carbon_kg': 0,
                'daily_carbon_kg': 0
            },
            'query_efficiency': {
                'total_queries': 0,
                'average_energy_per_query_joules': 0,
                'queries_per_kwh': 0
            },
            'recommendations': {
                'total': len(self.recommendations),
                'implemented': 0,
                'implementation_rate': 0
            },
            'environmental_equivalents': {
                'trees_needed': 0,
                'car_km_offset': 0,
                'smartphone_charges': 0
            },
            'optimization_potential': {
                'potential_energy_savings': 0,
                'potential_carbon_reduction': 0
            }
        }
    
    def _calculate_environmental_equivalents(self, carbon_kg: float) -> Dict[str, float]:
        """Calculate environmental equivalents for carbon footprint"""
        try:
            # Trees absorb ~22 kg CO2 per year
            trees_needed = carbon_kg / 22.0
            
            # Average car emits ~120 g CO2 per km
            car_km_offset = (carbon_kg * 1000) / 120.0
            
            # Smartphone charging emits ~0.008 kg CO2 per charge
            smartphone_charges = carbon_kg / 0.008
            
            return {
                'trees_needed': round(trees_needed, 2),
                'car_km_offset': round(car_km_offset, 2),
                'smartphone_charges': round(smartphone_charges, 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating environmental equivalents: {e}")
            return {'trees_needed': 0, 'car_km_offset': 0, 'smartphone_charges': 0}
    
    def _calculate_optimization_potential(self) -> Dict[str, float]:
        """Calculate potential optimization benefits"""
        try:
            # Calculate potential savings from unimplemented recommendations
            potential_carbon_reduction = sum(
                rec.estimated_carbon_reduction 
                for rec in self.recommendations 
                if rec.priority in ['high', 'critical']
            )
            
            # Estimate energy savings (rough calculation)
            potential_energy_savings = potential_carbon_reduction / self.carbon_intensity
            
            return {
                'potential_energy_savings_kwh_per_year': round(potential_energy_savings, 2),
                'potential_carbon_reduction_kg_per_year': round(potential_carbon_reduction, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating optimization potential: {e}")
            return {'potential_energy_savings_kwh_per_year': 0, 'potential_carbon_reduction_kg_per_year': 0}
    
    def get_current_metrics(self) -> Optional[EnergyMetrics]:
        """Get current energy metrics"""
        return self._collect_energy_metrics()
    
    def get_recommendations(self, category: Optional[str] = None, priority: Optional[str] = None) -> List[GreenRecommendation]:
        """Get filtered recommendations"""
        filtered_recs = self.recommendations
        
        if category:
            filtered_recs = [rec for rec in filtered_recs if rec.category == category]
        
        if priority:
            filtered_recs = [rec for rec in filtered_recs if rec.priority == priority]
        
        return filtered_recs
    
    def mark_recommendation_implemented(self, title: str) -> bool:
        """Mark a recommendation as implemented"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE recommendations 
                SET implemented = TRUE 
                WHERE title = ?
            ''', (title,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Marked recommendation as implemented: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking recommendation as implemented: {e}")
            return False
    
    def get_energy_statistics(self) -> Dict[str, Any]:
        """Get current energy statistics"""
        current_metrics = self.get_current_metrics()
        
        if not current_metrics:
            return {
                'status': 'No data available',
                'monitoring_active': self.monitoring_active,
                'energy_mode': self.energy_mode.value
            }
        
        return {
            'status': 'Active',
            'monitoring_active': self.monitoring_active,
            'energy_mode': self.energy_mode.value,
            'current_power_watts': current_metrics.power_consumption,
            'current_carbon_per_second': current_metrics.carbon_footprint,
            'energy_per_query_joules': current_metrics.energy_per_query,
            'cpu_usage_percent': current_metrics.cpu_usage,
            'memory_usage_percent': current_metrics.memory_usage,
            'queries_processed': current_metrics.queries_processed
        }
