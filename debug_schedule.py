# Schedule Debug Tool - Save as debug_schedules.py
# This will help us see what's actually in your database

import sqlite3
import json
import os
from datetime import datetime

# Check if database exists and what's in it
db_path = os.path.join('data', 'jarvis.db')

print("🔍 JARVIS DATABASE DEBUG TOOL")
print("=" * 50)

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    print("💡 Create a schedule first to generate the database")
else:
    print(f"✅ Database found at: {db_path}")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if saved_schedules table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='saved_schedules';
        """)
        
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ saved_schedules table doesn't exist")
            print("💡 Running table creation...")
            
            # Create the missing table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_schedules (
                    id INTEGER PRIMARY KEY,
                    schedule_name TEXT,
                    schedule_data TEXT,
                    created_date TIMESTAMP,
                    task_count INTEGER
                )
            ''')
            conn.commit()
            print("✅ saved_schedules table created")
        else:
            print("✅ saved_schedules table exists")
        
        # Check what's actually in the table
        cursor.execute("SELECT COUNT(*) FROM saved_schedules")
        count = cursor.fetchone()[0]
        
        print(f"\n📊 Schedules in database: {count}")
        
        if count > 0:
            print("\n📋 SAVED SCHEDULES:")
            cursor.execute("""
                SELECT id, schedule_name, created_date, task_count, 
                       substr(schedule_data, 1, 100) as preview
                FROM saved_schedules 
                ORDER BY created_date DESC
            """)
            
            schedules = cursor.fetchall()
            
            for schedule_id, name, created_date, task_count, preview in schedules:
                print(f"\n🔸 Schedule #{schedule_id}")
                print(f"   Name: {name}")
                print(f"   Created: {created_date}")
                print(f"   Tasks: {task_count}")
                print(f"   Data Preview: {preview}...")
                
                # Try to show the full schedule
                cursor.execute("SELECT schedule_data FROM saved_schedules WHERE id = ?", (schedule_id,))
                full_data = cursor.fetchone()[0]
                
                try:
                    schedule_obj = json.loads(full_data)
                    if 'schedule' in schedule_obj and schedule_obj['schedule']:
                        print(f"   📅 Schedule Items:")
                        for i, item in enumerate(schedule_obj['schedule'][:3], 1):  # Show first 3
                            time_slot = item.get('time', 'No time')
                            task = item.get('task', 'No task')
                            print(f"      {i}. {time_slot}: {task}")
                        if len(schedule_obj['schedule']) > 3:
                            print(f"      ... and {len(schedule_obj['schedule']) - 3} more items")
                    else:
                        print(f"   ⚠️ Schedule structure issue")
                except json.JSONDecodeError:
                    print(f"   ❌ JSON decode error in schedule data")
        else:
            print("\n💡 No schedules found in database")
            print("This means your recent schedule creation didn't save properly")

print("\n" + "=" * 50)
print("🔧 NEXT STEPS:")
if not os.path.exists(db_path) or count == 0:
    print("1. Your schedules aren't saving to the database")
    print("2. The schedule creation succeeded but save failed") 
    print("3. Try creating a simple 2-task schedule to test")
else:
    print("1. Schedules exist in database - the display code is the issue")
    print("2. Your basic_jarvis.py needs the complete updated code")
    print("3. The manage schedules section has placeholder text instead of real code")