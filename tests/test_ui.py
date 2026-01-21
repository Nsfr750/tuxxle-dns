#!/usr/bin/env python3
"""
Test for UI components functionality
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Mock PySide6 before importing UI modules
with patch.dict('sys.modules', {
    'PySide6': Mock(),
    'PySide6.QtWidgets': Mock(),
    'PySide6.QtCore': Mock(),
    'PySide6.QtGui': Mock()
}):
    from ui.main_window import MainWindow
    from ui.records_widget import RecordsWidget
    from ui.config_widget import ConfigWidget
    from ui.database_widget import DatabaseWidget
    from ui.logs_widget import LogsWidget
    from ui.stats_widget import StatsWidget
    from ui.menu import MenuBar
    from ui.themes import ThemeManager


class TestMainWindow:
    """Test cases for MainWindow class"""
    
    @pytest.fixture
    def mock_dns_server(self):
        """Create a mock DNS server for testing"""
        server = Mock()
        server.is_running.return_value = False
        server.start.return_value = True
        server.stop.return_value = True
        server.get_statistics.return_value = {
            'queries_received': 0,
            'responses_sent': 0,
            'errors': 0,
            'start_time': None,
            'uptime': 0
        }
        return server
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing"""
        config = Mock()
        config.get.return_value = "test_value"
        return config
    
    @pytest.fixture
    def main_window(self, mock_dns_server, mock_config):
        """Create a MainWindow instance for testing"""
        with patch('ui.main_window.QMainWindow'), \
             patch('ui.main_window.QApplication'), \
             patch('ui.main_window.QVBoxLayout'), \
             patch('ui.main_window.QTabWidget'), \
             patch('ui.main_window.QStatusBar'), \
             patch('ui.main_window.QTimer'):
            window = MainWindow(mock_dns_server, mock_config)
            return window
    
    def test_main_window_initialization(self, main_window, mock_dns_server, mock_config):
        """Test MainWindow initialization"""
        assert main_window.dns_server == mock_dns_server
        assert main_window.config == mock_config
        assert hasattr(main_window, 'central_widget')
        assert hasattr(main_window, 'tab_widget')
        assert hasattr(main_window, 'status_bar')
        assert hasattr(main_window, 'menu_bar')
    
    def test_main_window_setup_ui(self, main_window):
        """Test UI setup"""
        # Verify UI components are created
        assert main_window.central_widget is not None
        assert main_window.tab_widget is not None
        assert main_window.status_bar is not None
        assert main_window.menu_bar is not None
    
    def test_main_window_setup_tabs(self, main_window):
        """Test tab setup"""
        # Verify tabs are created
        assert hasattr(main_window, 'records_widget')
        assert hasattr(main_window, 'config_widget')
        assert hasattr(main_window, 'database_widget')
        assert hasattr(main_window, 'logs_widget')
        assert hasattr(main_window, 'stats_widget')
    
    def test_main_window_server_status_update(self, main_window, mock_dns_server):
        """Test server status update"""
        # Mock server running
        mock_dns_server.is_running.return_value = True
        
        # Update status
        main_window.update_server_status()
        
        # Verify status was updated
        assert main_window.server_status_updated is True
    
    def test_main_window_start_server(self, main_window, mock_dns_server):
        """Test starting DNS server"""
        # Start server
        main_window.start_server()
        
        # Verify server start was called
        mock_dns_server.start.assert_called_once()
    
    def test_main_window_stop_server(self, main_window, mock_dns_server):
        """Test stopping DNS server"""
        # Stop server
        main_window.stop_server()
        
        # Verify server stop was called
        mock_dns_server.stop.assert_called_once()
    
    def test_main_window_restart_server(self, main_window, mock_dns_server):
        """Test restarting DNS server"""
        # Restart server
        main_window.restart_server()
        
        # Verify server stop and start were called
        mock_dns_server.stop.assert_called_once()
        mock_dns_server.start.assert_called_once()
    
    def test_main_window_update_statistics(self, main_window, mock_dns_server):
        """Test statistics update"""
        # Mock statistics
        mock_stats = {
            'queries_received': 100,
            'responses_sent': 95,
            'errors': 5,
            'start_time': 1234567890,
            'uptime': 3600
        }
        mock_dns_server.get_statistics.return_value = mock_stats
        
        # Update statistics
        main_window.update_statistics()
        
        # Verify statistics were updated
        assert main_window.current_statistics == mock_stats
    
    def test_main_window_close_event(self, main_window, mock_dns_server):
        """Test window close event"""
        # Mock close event
        mock_event = Mock()
        
        # Handle close event
        main_window.closeEvent(mock_event)
        
        # Verify server is stopped
        mock_dns_server.stop.assert_called_once()


class TestRecordsWidget:
    """Test cases for RecordsWidget class"""
    
    @pytest.fixture
    def mock_dns_server(self):
        """Create a mock DNS server for testing"""
        server = Mock()
        server.get_all_records.return_value = []
        server.add_record.return_value = True
        server.delete_record.return_value = True
        server.update_record.return_value = True
        return server
    
    @pytest.fixture
    def records_widget(self, mock_dns_server):
        """Create a RecordsWidget instance for testing"""
        with patch('ui.records_widget.QWidget'), \
             patch('ui.records_widget.QVBoxLayout'), \
             patch('ui.records_widget.QHBoxLayout'), \
             patch('ui.records_widget.QTableWidget'), \
             patch('ui.records_widget.QPushButton'), \
             patch('ui.records_widget.QLineEdit'), \
             patch('ui.records_widget.QComboBox'):
            widget = RecordsWidget(mock_dns_server)
            return widget
    
    def test_records_widget_initialization(self, records_widget, mock_dns_server):
        """Test RecordsWidget initialization"""
        assert records_widget.dns_server == mock_dns_server
        assert hasattr(records_widget, 'table_widget')
        assert hasattr(records_widget, 'add_button')
        assert hasattr(records_widget, 'edit_button')
        assert hasattr(records_widget, 'delete_button')
        assert hasattr(records_widget, 'refresh_button')
    
    def test_records_widget_load_records(self, records_widget, mock_dns_server):
        """Test loading records into table"""
        # Mock records
        mock_records = [
            Mock(name="example.com", record_type="A", value="192.168.1.1", ttl=300),
            Mock(name="test.com", record_type="AAAA", value="2001:db8::1", ttl=300)
        ]
        mock_dns_server.get_all_records.return_value = mock_records
        
        # Load records
        records_widget.load_records()
        
        # Verify records were loaded
        assert records_widget.table_widget.setRowCount.called
        assert records_widget.current_records == mock_records
    
    def test_records_widget_add_record(self, records_widget, mock_dns_server):
        """Test adding a new record"""
        # Mock record data
        record_data = {
            'name': 'example.com',
            'type': 'A',
            'value': '192.168.1.1',
            'ttl': 300
        }
        
        # Add record
        records_widget.add_record(record_data)
        
        # Verify record was added
        mock_dns_server.add_record.assert_called_once()
    
    def test_records_widget_edit_record(self, records_widget, mock_dns_server):
        """Test editing an existing record"""
        # Mock selected record
        old_record = Mock()
        new_record = Mock()
        
        # Edit record
        records_widget.edit_record(old_record, new_record)
        
        # Verify record was updated
        mock_dns_server.update_record.assert_called_once_with(old_record, new_record)
    
    def test_records_widget_delete_record(self, records_widget, mock_dns_server):
        """Test deleting a record"""
        # Mock selected record
        record = Mock(name="example.com", record_type="A", value="192.168.1.1")
        
        # Delete record
        records_widget.delete_record(record)
        
        # Verify record was deleted
        mock_dns_server.delete_record.assert_called_once()
    
    def test_records_widget_refresh_records(self, records_widget):
        """Test refreshing records"""
        # Refresh records
        records_widget.refresh_records()
        
        # Verify records were reloaded
        assert records_widget.load_records.called


class TestConfigWidget:
    """Test cases for ConfigWidget class"""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing"""
        config = Mock()
        config.get_all.return_value = {
            'dns': {'port': 53, 'bind_address': '0.0.0.0'},
            'logging': {'level': 'INFO', 'file': 'dns_server.log'},
            'ui': {'window_width': 1200, 'window_height': 800}
        }
        return config
    
    @pytest.fixture
    def config_widget(self, mock_config):
        """Create a ConfigWidget instance for testing"""
        with patch('ui.config_widget.QWidget'), \
             patch('ui.config_widget.QVBoxLayout'), \
             patch('ui.config_widget.QTabWidget'), \
             patch('ui.config_widget.QFormLayout'), \
             patch('ui.config_widget.QSpinBox'), \
             patch('ui.config_widget.QLineEdit'), \
             patch('ui.config_widget.QComboBox'):
            widget = ConfigWidget(mock_config)
            return widget
    
    def test_config_widget_initialization(self, config_widget, mock_config):
        """Test ConfigWidget initialization"""
        assert config_widget.config == mock_config
        assert hasattr(config_widget, 'tab_widget')
        assert hasattr(config_widget, 'dns_tab')
        assert hasattr(config_widget, 'logging_tab')
        assert hasattr(config_widget, 'ui_tab')
    
    def test_config_widget_load_config(self, config_widget, mock_config):
        """Test loading configuration into widget"""
        # Load config
        config_widget.load_config()
        
        # Verify config was loaded
        assert config_widget.config_loaded is True
    
    def test_config_widget_save_config(self, config_widget, mock_config):
        """Test saving configuration"""
        # Save config
        config_widget.save_config()
        
        # Verify config was saved
        mock_config.save.assert_called_once()
    
    def test_config_widget_reset_config(self, config_widget, mock_config):
        """Test resetting configuration to defaults"""
        # Reset config
        config_widget.reset_config()
        
        # Verify config was reset
        mock_config.reset_to_defaults.assert_called_once()
        assert config_widget.load_config.called


class TestDatabaseWidget:
    """Test cases for DatabaseWidget class"""
    
    @pytest.fixture
    def mock_database(self):
        """Create a mock database for testing"""
        db = Mock()
        db.list_records.return_value = []
        db.backup.return_value = True
        db.restore.return_value = True
        db.get_statistics.return_value = {'total_records': 0}
        return db
    
    @pytest.fixture
    def database_widget(self, mock_database):
        """Create a DatabaseWidget instance for testing"""
        with patch('ui.database_widget.QWidget'), \
             patch('ui.database_widget.QVBoxLayout'), \
             patch('ui.database_widget.QTableWidget'), \
             patch('ui.database_widget.QPushButton'), \
             patch('ui.database_widget.QProgressBar'):
            widget = DatabaseWidget(mock_database)
            return widget
    
    def test_database_widget_initialization(self, database_widget, mock_database):
        """Test DatabaseWidget initialization"""
        assert database_widget.database == mock_database
        assert hasattr(database_widget, 'table_widget')
        assert hasattr(database_widget, 'backup_button')
        assert hasattr(database_widget, 'restore_button')
        assert hasattr(database_widget, 'refresh_button')
    
    def test_database_widget_load_records(self, database_widget, mock_database):
        """Test loading database records"""
        # Mock records
        mock_records = [
            Mock(name="example.com", record_type="A", value="192.168.1.1"),
            Mock(name="test.com", record_type="AAAA", value="2001:db8::1")
        ]
        mock_database.list_records.return_value = mock_records
        
        # Load records
        database_widget.load_records()
        
        # Verify records were loaded
        assert database_widget.table_widget.setRowCount.called
        assert database_widget.current_records == mock_records
    
    def test_database_widget_backup(self, database_widget, mock_database):
        """Test database backup"""
        # Backup database
        database_widget.backup_database()
        
        # Verify backup was performed
        mock_database.backup.assert_called_once()
    
    def test_database_widget_restore(self, database_widget, mock_database):
        """Test database restore"""
        # Mock backup file
        backup_file = "test_backup.db"
        
        # Restore database
        database_widget.restore_database(backup_file)
        
        # Verify restore was performed
        mock_database.restore.assert_called_once_with(backup_file)
    
    def test_database_widget_update_statistics(self, database_widget, mock_database):
        """Test updating database statistics"""
        # Mock statistics
        mock_stats = {'total_records': 100, 'database_size': 1024}
        mock_database.get_statistics.return_value = mock_stats
        
        # Update statistics
        database_widget.update_statistics()
        
        # Verify statistics were updated
        assert database_widget.current_statistics == mock_stats


class TestLogsWidget:
    """Test cases for LogsWidget class"""
    
    @pytest.fixture
    def logs_widget(self):
        """Create a LogsWidget instance for testing"""
        with patch('ui.logs_widget.QWidget'), \
             patch('ui.logs_widget.QVBoxLayout'), \
             patch('ui.logs_widget.QTextEdit'), \
             patch('ui.logs_widget.QComboBox'), \
             patch('ui.logs_widget.QPushButton'):
            widget = LogsWidget()
            return widget
    
    def test_logs_widget_initialization(self, logs_widget):
        """Test LogsWidget initialization"""
        assert hasattr(logs_widget, 'log_text')
        assert hasattr(logs_widget, 'level_combo')
        assert hasattr(logs_widget, 'clear_button')
        assert hasattr(logs_widget, 'refresh_button')
    
    def test_logs_widget_append_log(self, logs_widget):
        """Test appending log messages"""
        # Append log message
        logs_widget.append_log("Test message", "INFO")
        
        # Verify message was appended
        assert logs_widget.log_text.append.called
    
    def test_logs_widget_clear_logs(self, logs_widget):
        """Test clearing log messages"""
        # Clear logs
        logs_widget.clear_logs()
        
        # Verify logs were cleared
        assert logs_widget.log_text.clear.called
    
    def test_logs_widget_filter_by_level(self, logs_widget):
        """Test filtering logs by level"""
        # Set filter level
        logs_widget.set_log_level("ERROR")
        
        # Verify filter was applied
        assert logs_widget.current_log_level == "ERROR"
    
    def test_logs_widget_refresh_logs(self, logs_widget):
        """Test refreshing log messages"""
        # Refresh logs
        logs_widget.refresh_logs()
        
        # Verify logs were refreshed
        assert logs_widget.logs_refreshed is True


class TestStatsWidget:
    """Test cases for StatsWidget class"""
    
    @pytest.fixture
    def mock_dns_server(self):
        """Create a mock DNS server for testing"""
        server = Mock()
        server.get_statistics.return_value = {
            'queries_received': 1000,
            'responses_sent': 950,
            'errors': 50,
            'start_time': 1234567890,
            'uptime': 3600
        }
        return server
    
    @pytest.fixture
    def stats_widget(self, mock_dns_server):
        """Create a StatsWidget instance for testing"""
        with patch('ui.stats_widget.QWidget'), \
             patch('ui.stats_widget.QVBoxLayout'), \
             patch('ui.stats_widget.QGridLayout'), \
             patch('ui.stats_widget.QLabel'), \
             patch('ui.stats_widget.QProgressBar'):
            widget = StatsWidget(mock_dns_server)
            return widget
    
    def test_stats_widget_initialization(self, stats_widget, mock_dns_server):
        """Test StatsWidget initialization"""
        assert stats_widget.dns_server == mock_dns_server
        assert hasattr(stats_widget, 'queries_label')
        assert hasattr(stats_widget, 'responses_label')
        assert hasattr(stats_widget, 'errors_label')
        assert hasattr(stats_widget, 'uptime_label')
    
    def test_stats_widget_update_statistics(self, stats_widget, mock_dns_server):
        """Test updating statistics display"""
        # Mock statistics
        mock_stats = {
            'queries_received': 2000,
            'responses_sent': 1950,
            'errors': 50,
            'start_time': 1234567890,
            'uptime': 7200
        }
        mock_dns_server.get_statistics.return_value = mock_stats
        
        # Update statistics
        stats_widget.update_statistics()
        
        # Verify statistics were updated
        assert stats_widget.current_statistics == mock_stats
    
    def test_stats_widget_reset_statistics(self, stats_widget, mock_dns_server):
        """Test resetting statistics"""
        # Reset statistics
        stats_widget.reset_statistics()
        
        # Verify statistics were reset
        mock_dns_server.reset_statistics.assert_called_once()
        assert stats_widget.update_statistics.called


class TestMenuBar:
    """Test cases for MenuBar class"""
    
    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window for testing"""
        window = Mock()
        window.start_server = Mock()
        window.stop_server = Mock()
        window.restart_server = Mock()
        window.show_about = Mock()
        window.show_help = Mock()
        return window
    
    @pytest.fixture
    def menu_bar(self, mock_main_window):
        """Create a MenuBar instance for testing"""
        with patch('ui.menu.QMenuBar'), \
             patch('ui.menu.QMenu'), \
             patch('ui.menu.QAction'):
            menu = MenuBar(mock_main_window)
            return menu
    
    def test_menu_bar_initialization(self, menu_bar, mock_main_window):
        """Test MenuBar initialization"""
        assert menu_bar.main_window == mock_main_window
        assert hasattr(menu_bar, 'file_menu')
        assert hasattr(menu_bar, 'server_menu')
        assert hasattr(menu_bar, 'help_menu')
    
    def test_menu_bar_create_actions(self, menu_bar):
        """Test menu action creation"""
        # Verify actions are created
        assert hasattr(menu_bar, 'start_action')
        assert hasattr(menu_bar, 'stop_action')
        assert hasattr(menu_bar, 'restart_action')
        assert hasattr(menu_bar, 'exit_action')
        assert hasattr(menu_bar, 'about_action')
        assert hasattr(menu_bar, 'help_action')
    
    def test_menu_bar_connect_actions(self, menu_bar, mock_main_window):
        """Test menu action connections"""
        # Trigger start action
        if hasattr(menu_bar, 'start_action'):
            menu_bar.start_action.triggered.emit()
            mock_main_window.start_server.assert_called_once()
        
        # Trigger stop action
        if hasattr(menu_bar, 'stop_action'):
            menu_bar.stop_action.triggered.emit()
            mock_main_window.stop_server.assert_called_once()


class TestThemeManager:
    """Test cases for ThemeManager class"""
    
    @pytest.fixture
    def theme_manager(self):
        """Create a ThemeManager instance for testing"""
        with patch('ui.themes.QApplication'):
            manager = ThemeManager()
            return manager
    
    def test_theme_manager_initialization(self, theme_manager):
        """Test ThemeManager initialization"""
        assert hasattr(theme_manager, 'available_themes')
        assert hasattr(theme_manager, 'current_theme')
        assert 'light' in theme_manager.available_themes
        assert 'dark' in theme_manager.available_themes
    
    def test_theme_manager_apply_theme(self, theme_manager):
        """Test applying a theme"""
        # Apply light theme
        result = theme_manager.apply_theme('light')
        
        assert result is True
        assert theme_manager.current_theme == 'light'
    
    def test_theme_manager_invalid_theme(self, theme_manager):
        """Test applying invalid theme"""
        # Apply invalid theme
        result = theme_manager.apply_theme('invalid_theme')
        
        assert result is False
        assert theme_manager.current_theme != 'invalid_theme'
    
    def test_theme_manager_get_available_themes(self, theme_manager):
        """Test getting available themes"""
        themes = theme_manager.get_available_themes()
        
        assert isinstance(themes, list)
        assert 'light' in themes
        assert 'dark' in themes
    
    def test_theme_manager_get_current_theme(self, theme_manager):
        """Test getting current theme"""
        current = theme_manager.get_current_theme()
        
        assert current in theme_manager.available_themes


if __name__ == "__main__":
    pytest.main([__file__])
