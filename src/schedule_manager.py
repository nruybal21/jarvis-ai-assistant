# src/schedule_manager.py
import sqlite3
import json
import os
from datetime import datetime
from calendar_export import CalendarExporter

class ScheduleManager:
    """Manage storage and retrieval of generated schedules"""
    
    def __init__(self, db_path="data/jarvis.db"):
        self.db_path = db_path
        self.init_schedule_table()
        
    def init_schedule_table(self):
        """Create schedules table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                schedule_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tasks_count INTEGER,
                total_time TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_schedule(self, schedule_data, name=None):
        """Save a generated schedule to the database"""
        
        if name is None:
            name = f"Schedule {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Extract summary info
        tasks_count = len(schedule_data.get('schedule', []))
        total_time = schedule_data.get('total_time', 'Unknown')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO schedules (name, schedule_data, tasks_count, total_time)
            VALUES (?, ?, ?, ?)
        ''', (name, json.dumps(schedule_data), tasks_count, total_time))
        
        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Schedule saved as: {name} (ID: {schedule_id})")
        return schedule_id
    
    def list_schedules(self):
        """List all saved schedules"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, created_at, tasks_count, total_time
            FROM schedules
            ORDER BY created_at DESC
        ''')
        
        schedules = cursor.fetchall()
        conn.close()
        
        return schedules
    
    def get_schedule(self, schedule_id):
        """Retrieve a specific schedule by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, schedule_data, created_at, tasks_count, total_time
            FROM schedules
            WHERE id = ?
        ''', (schedule_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            schedule_id, name, schedule_data, created_at, tasks_count, total_time = result
            return {
                'id': schedule_id,
                'name': name,
                'schedule_data': json.loads(schedule_data),
                'created_at': created_at,
                'tasks_count': tasks_count,
                'total_time': total_time
            }
        return None
    
    def delete_schedule(self, schedule_id):
        """Delete a schedule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM schedules WHERE id = ?', (schedule_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def export_schedule(self, schedule_id, export_type='ics'):
        """Export a saved schedule"""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            print("❌ Schedule not found")
            return None
        
        exporter = CalendarExporter()
        schedule_data = schedule['schedule_data']
        
        if export_type == 'ics':
            filename = f"{schedule['name'].replace(' ', '_')}.ics"
            return exporter.create_ics_file(schedule_data, filename)
        elif export_type == 'html':
            filename = f"{schedule['name'].replace(' ', '_')}.html"
            return exporter.create_html_schedule(schedule_data, filename)
        elif export_type == 'email':
            return exporter.create_email_format(schedule_data)
        
        return None

def schedule_management_menu():
    """Interactive menu for schedule management"""
    manager = ScheduleManager()
    
    while True:
        print("\n📅 SCHEDULE MANAGEMENT")
        print("=" * 30)
        print("1. View saved schedules")
        print("2. Export a saved schedule")
        print("3. Delete a schedule")
        print("4. Back to main menu")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            schedules = manager.list_schedules()
            if schedules:
                print("\n📋 SAVED SCHEDULES:")
                print("-" * 80)
                print(f"{'ID':<4} {'Name':<25} {'Created':<20} {'Tasks':<6} {'Time':<10}")
                print("-" * 80)
                
                for schedule in schedules:
                    schedule_id, name, created_at, tasks_count, total_time = schedule
                    created_short = created_at[:16] if created_at else "Unknown"
                    print(f"{schedule_id:<4} {name[:24]:<25} {created_short:<20} {tasks_count:<6} {total_time:<10}")
            else:
                print("📭 No saved schedules found")
        
        elif choice == "2":
            schedules = manager.list_schedules()
            if not schedules:
                print("📭 No saved schedules to export")
                continue
            
            # Show available schedules
            print("\n📋 AVAILABLE SCHEDULES:")
            for schedule in schedules[:10]:  # Show last 10
                schedule_id, name, created_at, tasks_count, total_time = schedule
                print(f"{schedule_id}: {name} ({tasks_count} tasks, {total_time})")
            
            try:
                schedule_id = int(input("\nEnter schedule ID to export: "))
                
                print("\n📤 EXPORT OPTIONS:")
                print("1. Calendar file (.ics)")
                print("2. HTML schedule")
                print("3. Email format")
                
                export_choice = input("Choose export option (1-3): ").strip()
                
                if export_choice == '1':
                    file_path = manager.export_schedule(schedule_id, 'ics')
                    if file_path:
                        print(f"✅ Calendar file exported: {file_path}")
                        print("📁 Import this file into your calendar app")
                
                elif export_choice == '2':
                    file_path = manager.export_schedule(schedule_id, 'html')
                    if file_path:
                        print(f"✅ HTML schedule exported: {file_path}")
                        print("🌐 Open in browser to view/print")
                
                elif export_choice == '3':
                    email_text = manager.export_schedule(schedule_id, 'email')
                    if email_text:
                        print("\n📧 EMAIL FORMAT:")
                        print("=" * 50)
                        print(email_text)
                        print("=" * 50)
                        print("✅ Copy the text above to paste into email/notes")
                
            except ValueError:
                print("❌ Invalid schedule ID")
        
        elif choice == "3":
            schedules = manager.list_schedules()
            if not schedules:
                print("📭 No saved schedules to delete")
                continue
            
            # Show available schedules
            print("\n📋 AVAILABLE SCHEDULES:")
            for schedule in schedules[:10]:
                schedule_id, name, created_at, tasks_count, total_time = schedule
                print(f"{schedule_id}: {name}")
            
            try:
                schedule_id = int(input("\nEnter schedule ID to delete: "))
                confirm = input(f"Are you sure you want to delete schedule {schedule_id}? (y/N): ")
                
                if confirm.lower() == 'y':
                    if manager.delete_schedule(schedule_id):
                        print("✅ Schedule deleted successfully")
                    else:
                        print("❌ Schedule not found")
                else:
                    print("❌ Deletion cancelled")
                    
            except ValueError:
                print("❌ Invalid schedule ID")
        
        elif choice == "4":
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    schedule_management_menu()