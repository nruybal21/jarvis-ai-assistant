# src/database.py
import sqlite3
import os
from datetime import datetime
import json

class JarvisDatabase:
    """
    Handles all database operations for Jarvis AI Assistant
    """
    
    def __init__(self, db_path="data/jarvis.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create and setup database
        self.init_database()
        print(f"📊 Database initialized at {db_path}")
    
    def init_database(self):
        """Create all necessary tables for Jarvis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tasks table - stores all your tasks and their analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority TEXT,
                estimated_duration INTEGER,
                actual_duration INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                ai_analysis TEXT,
                notes TEXT
            )
        ''')
        
        # Daily insights - stores Jarvis's daily observations about your patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                total_tasks INTEGER,
                completed_tasks INTEGER,
                productivity_score REAL,
                insights TEXT,
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User preferences - learns your preferences over time
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_key TEXT UNIQUE,
                preference_value TEXT,
                confidence_score REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Activity log - tracks everything Jarvis does for you
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT,
                description TEXT,
                data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database tables created successfully")
    
    def add_task(self, title, description="", category="general", priority="medium", 
                 estimated_duration=30, ai_analysis=None):
        """Add a new task to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (title, description, category, priority, 
                             estimated_duration, ai_analysis)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, category, priority, estimated_duration, 
              json.dumps(ai_analysis) if ai_analysis else None))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log this activity
        self.log_activity("task_created", f"Created task: {title}", {"task_id": task_id})
        
        print(f"✅ Task added: {title} (ID: {task_id})")
        return task_id
    
    def complete_task(self, task_id, actual_duration=None, notes=""):
        """Mark a task as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = 'completed', 
                completed_at = CURRENT_TIMESTAMP,
                actual_duration = ?,
                notes = ?
            WHERE id = ?
        ''', (actual_duration, notes, task_id))
        
        conn.commit()
        conn.close()
        
        self.log_activity("task_completed", f"Completed task ID: {task_id}", 
                         {"task_id": task_id, "duration": actual_duration})
        
        print(f"✅ Task {task_id} marked as completed")
    
    def get_pending_tasks(self):
        """Get all pending tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, category, priority, estimated_duration, created_at
            FROM tasks 
            WHERE status = 'pending'
            ORDER BY priority DESC, created_at ASC
        ''')
        
        tasks = cursor.fetchall()
        conn.close()
        
        return tasks
    
    def get_productivity_stats(self, days=7):
        """Get productivity statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get task completion stats
        cursor.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                AVG(CASE WHEN actual_duration IS NOT NULL THEN actual_duration ELSE estimated_duration END) as avg_duration
            FROM tasks 
            WHERE created_at > datetime('now', '-{} days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        '''.format(days))
        
        stats = cursor.fetchall()
        conn.close()
        
        return stats
    
    def save_user_preference(self, key, value, confidence=1.0):
        """Save or update a user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (preference_key, preference_value, confidence_score, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (key, str(value), confidence))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Saved preference: {key} = {value}")
    
    def get_user_preference(self, key, default=None):
        """Get a user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT preference_value FROM user_preferences 
            WHERE preference_key = ?
        ''', (key,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else default
    
    def log_activity(self, activity_type, description, data=None):
        """Log an activity for tracking and analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_log (activity_type, description, data)
            VALUES (?, ?, ?)
        ''', (activity_type, description, json.dumps(data) if data else None))
        
        conn.commit()
        conn.close()
    
    def get_recent_activity(self, limit=10):
        """Get recent activity for displaying to user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT activity_type, description, timestamp
            FROM activity_log
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        activities = cursor.fetchall()
        conn.close()
        
        return activities

def test_database():
    """Test the database functionality"""
    print("🧪 Testing Jarvis Database...")
    
    # Initialize database
    db = JarvisDatabase()
    
    # Test adding tasks
    task_id = db.add_task(
        title="Learn Python basics",
        description="Work through Python tutorial",
        category="learning",
        priority="high",
        estimated_duration=60
    )
    
    # Test getting pending tasks
    pending = db.get_pending_tasks()
    print(f"📋 Pending tasks: {len(pending)}")
    for task in pending:
        print(f"  - {task[1]} ({task[2]}, {task[3]} priority)")
    
    # Test completing a task
    db.complete_task(task_id, actual_duration=45, notes="Completed first chapter")
    
    # Test preferences
    db.save_user_preference("preferred_work_time", "9:00 AM")
    work_time = db.get_user_preference("preferred_work_time")
    print(f"⚙️  Preferred work time: {work_time}")
    
    # Test activity log
    recent_activity = db.get_recent_activity(5)
    print("📈 Recent activity:")
    for activity in recent_activity:
        print(f"  - {activity[1]} at {activity[2]}")
    
    print("✅ Database test completed successfully!")

if __name__ == "__main__":
    test_database()