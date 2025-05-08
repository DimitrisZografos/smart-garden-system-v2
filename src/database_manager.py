"""
Database manager for the Smart Garden System.
Handles storing and retrieving sensor data, watering events, and system logs.
"""

import os
import time
import logging
import sqlite3
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages database operations for the Smart Garden System.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the database manager.
        
        Args:
            config: Database configuration from config.yaml
        """
        self.config = config
        self.db_type = config.get('type', 'sqlite')
        
        # Initialize the database
        if self.db_type == 'sqlite':
            self._init_sqlite()
        elif self.db_type == 'postgresql':
            self._init_postgresql()
        else:
            logger.error(f"Unsupported database type: {self.db_type}")
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _init_sqlite(self) -> None:
        """Initialize SQLite database."""
        try:
            # Ensure the data directory exists
            db_path = self.config.get('path', 'data/garden.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Connect to the database
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            # Create tables if they don't exist
            self._create_tables()
            
            logger.info(f"SQLite database initialized at {db_path}")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {str(e)}")
            raise
    
    def _init_postgresql(self) -> None:
        """Initialize PostgreSQL database."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Connect to the database
            self.conn = psycopg2.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                dbname=self.config.get('name', 'garden'),
                user=self.config.get('user', ''),
                password=self.config.get('password', '')
            )
            
            # Create tables if they don't exist
            self._create_tables()
            
            logger.info(f"PostgreSQL database initialized at {self.config.get('host')}:{self.config.get('port')}/{self.config.get('name')}")
        except ImportError:
            logger.error("psycopg2 is not installed. Please install it to use PostgreSQL.")
            raise
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL database: {str(e)}")
            raise
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Create sensor_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp INTEGER NOT NULL
            )
        ''')
        
        # Create watering_events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watering_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration INTEGER NOT NULL,
                moisture_before REAL,
                timestamp INTEGER NOT NULL
            )
        ''')
        
        # Create weather_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                weather_type TEXT,
                precipitation_probability REAL,
                timestamp INTEGER NOT NULL
            )
        ''')
        
        # Create plant_images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plant_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                analysis_result TEXT,
                timestamp INTEGER NOT NULL
            )
        ''')
        
        # Create system_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                component TEXT,
                timestamp INTEGER NOT NULL
            )
        ''')
        
        self.conn.commit()
        cursor.close()
    
    def store_sensor_reading(self, sensor_type: str, value: float) -> None:
        """
        Store a sensor reading in the database.
        
        Args:
            sensor_type: The type of sensor (e.g., 'soil_moisture', 'temperature')
            value: The sensor value
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "INSERT INTO sensor_data (sensor_type, value, timestamp) VALUES (?, ?, ?)",
                (sensor_type, value, int(time.time()))
            )
            
            self.conn.commit()
            cursor.close()
            
            logger.debug(f"Stored {sensor_type} reading: {value}")
        except Exception as e:
            logger.error(f"Error storing sensor reading: {str(e)}")
    
    def store_watering_event(self, duration: int, moisture_before: float) -> None:
        """
        Store a watering event in the database.
        
        Args:
            duration: The duration of watering in seconds
            moisture_before: The soil moisture percentage before watering
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "INSERT INTO watering_events (duration, moisture_before, timestamp) VALUES (?, ?, ?)",
                (duration, moisture_before, int(time.time()))
            )
            
            self.conn.commit()
            cursor.close()
            
            logger.debug(f"Stored watering event: {duration}s, moisture: {moisture_before}%")
        except Exception as e:
            logger.error(f"Error storing watering event: {str(e)}")
    
    def store_weather_data(self, weather_data: Dict[str, Any]) -> None:
        """
        Store weather data in the database.
        
        Args:
            weather_data: Weather data dictionary
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO weather_data 
                (temperature, humidity, pressure, weather_type, precipitation_probability, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    weather_data.get('temperature'),
                    weather_data.get('humidity'),
                    weather_data.get('pressure'),
                    weather_data.get('weather'),
                    weather_data.get('precipitation_probability'),
                    int(time.time())
                )
            )
            
            self.conn.commit()
            cursor.close()
            
            logger.debug("Stored weather data")
        except Exception as e:
            logger.error(f"Error storing weather data: {str(e)}")
    
    def store_image_analysis(self, image_path: str, analysis_result: Optional[str] = None) -> None:
        """
        Store image analysis results in the database.
        
        Args:
            image_path: Path to the captured image
            analysis_result: JSON string with analysis results (optional)
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "INSERT INTO plant_images (image_path, analysis_result, timestamp) VALUES (?, ?, ?)",
                (image_path, analysis_result, int(time.time()))
            )
            
            self.conn.commit()
            cursor.close()
            
            logger.debug(f"Stored image analysis for {image_path}")
        except Exception as e:
            logger.error(f"Error storing image analysis: {str(e)}")
    
    def store_log(self, level: str, message: str, component: Optional[str] = None) -> None:
        """
        Store a system log in the database.
        
        Args:
            level: Log level (e.g., 'INFO', 'ERROR')
            message: Log message
            component: System component that generated the log (optional)
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "INSERT INTO system_logs (level, message, component, timestamp) VALUES (?, ?, ?, ?)",
                (level, message, component, int(time.time()))
            )
            
            self.conn.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Error storing system log: {str(e)}")
    
    def get_sensor_readings(self, sensor_type: str, 
                           limit: int = 100, 
                           start_time: Optional[int] = None, 
                           end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get sensor readings from the database.
        
        Args:
            sensor_type: The type of sensor to get readings for
            limit: Maximum number of readings to return
            start_time: Start timestamp (optional)
            end_time: End timestamp (optional)
            
        Returns:
            List of sensor readings
        """
        try:
            cursor = self.conn.cursor()
            
            query = "SELECT * FROM sensor_data WHERE sensor_type = ?"
            params = [sensor_type]
            
            if start_time is not None:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time is not None:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            # Convert to list of dictionaries
            result = []
            for row in cursor.fetchall():
                if isinstance(row, sqlite3.Row):
                    # SQLite
                    result.append(dict(row))
                else:
                    # PostgreSQL
                    result.append(row)
            
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Error getting sensor readings: {str(e)}")
            return []
    
    def get_latest_sensor_reading(self, sensor_type: str) -> Optional[float]:
        """
        Get the latest reading for a specific sensor type.
        
        Args:
            sensor_type: The type of sensor to get the reading for
            
        Returns:
            The latest sensor value, or None if no readings are available
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "SELECT value FROM sensor_data WHERE sensor_type = ? ORDER BY timestamp DESC LIMIT 1",
                (sensor_type,)
            )
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                if isinstance(row, sqlite3.Row):
                    # SQLite
                    return row['value']
                else:
                    # PostgreSQL
                    return row[0]
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting latest sensor reading: {str(e)}")
            return None
    
    def get_watering_events(self, limit: int = 10, 
                           start_time: Optional[int] = None, 
                           end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get watering events from the database.
        
        Args:
            limit: Maximum number of events to return
            start_time: Start timestamp (optional)
            end_time: End timestamp (optional)
            
        Returns:
            List of watering events
        """
        try:
            cursor = self.conn.cursor()
            
            query = "SELECT * FROM watering_events"
            params = []
            
            if start_time is not None:
                query += " WHERE timestamp >= ?"
                params.append(start_time)
                
                if end_time is not None:
                    query += " AND timestamp <= ?"
                    params.append(end_time)
            elif end_time is not None:
                query += " WHERE timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            # Convert to list of dictionaries
            result = []
            for row in cursor.fetchall():
                if isinstance(row, sqlite3.Row):
                    # SQLite
                    result.append(dict(row))
                else:
                    # PostgreSQL
                    result.append(row)
            
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Error getting watering events: {str(e)}")
            return []
    
    def get_last_watering_time(self) -> Optional[int]:
        """
        Get the timestamp of the last watering event.
        
        Returns:
            Timestamp of the last watering event, or None if no events are available
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "SELECT timestamp FROM watering_events ORDER BY timestamp DESC LIMIT 1"
            )
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                if isinstance(row, sqlite3.Row):
                    # SQLite
                    return row['timestamp']
                else:
                    # PostgreSQL
                    return row[0]
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting last watering time: {str(e)}")
            return None
    
    def close(self) -> None:
        """Close the database connection."""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")