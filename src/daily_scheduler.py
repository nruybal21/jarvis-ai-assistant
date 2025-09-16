# Complete Enhanced Daily Schedule Creator with Specific Day Recurring Tasks
# File: src/daily_scheduler.py

import sqlite3
import json
import requests
import re
from datetime import datetime, timedelta
import os

class DailyScheduleCreator:
    def __init__(self):
        """Initialize Daily Schedule Creator with enhanced time parsing"""
        self.db_path = "data/jarvis.db"
        self.setup_recurring_tasks_database()
        
    def setup_recurring_tasks_database(self):
        """Setup database tables for recurring tasks"""
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced recurring tasks table with frequency_details
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recurring_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                preferred_time TEXT,
                frequency TEXT NOT NULL,
                frequency_details TEXT,
                category TEXT DEFAULT 'General',
                priority INTEGER DEFAULT 5,
                is_active INTEGER DEFAULT 1,
                created_date TEXT,
                notes TEXT
            )
        ''')
        
        # Daily schedules table (enhanced)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_date TEXT NOT NULL,
                schedule_data TEXT NOT NULL,
                schedule_type TEXT DEFAULT 'daily',
                created_date TEXT,
                total_time_minutes INTEGER,
                recurring_tasks_included INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def extract_time_from_description(self, description):
        """Extract specific times from task descriptions using regex"""
        # Patterns to match various time formats
        time_patterns = [
            r'\bat\s+(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',  # "at 10:15 AM"
            r'\bdue\s+at\s+(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',  # "due at 08:00 AM"
            r'\bby\s+(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',  # "by 5:30 PM"
            r'\b(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',  # "10:15 AM" anywhere in text
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                period = match.group(3).upper()
                
                # Convert to 24-hour format
                if period == 'PM' and hour != 12:
                    hour += 12
                elif period == 'AM' and hour == 12:
                    hour = 0
                    
                return f"{hour:02d}:{minute:02d}"
        
        return None
    
    def ask_claude(self, question, context=""):
        """AI analysis for scheduling"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {"Content-Type": "application/json"}
        
        full_prompt = f"""
        You are an expert daily scheduling assistant. Analyze the provided tasks and create an optimal daily schedule.
        
        Context: {context}
        
        Task: {question}
        
        Provide a detailed daily schedule with specific time slots, considering:
        - Energy levels throughout the day
        - Task priorities and complexity
        - Natural work rhythms
        - Buffer time between tasks
        - Realistic time estimates
        
        Format your response as a structured schedule.
        """
        
        data = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": full_prompt}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                return "AI scheduling analysis temporarily unavailable. Using optimized default scheduling."
        except Exception as e:
            return "Using intelligent default scheduling based on best practices."
    
    def add_recurring_task(self):
        """Add a new recurring task with specific day selection"""
        print("\n📅 ADD RECURRING TASK")
        print("=" * 40)
        
        task_name = input("📝 Task name: ").strip()
        if not task_name:
            print("❌ Task name required.")
            return
            
        try:
            duration = int(input("⏱️  Duration (minutes): "))
        except ValueError:
            print("❌ Please enter a valid number for duration.")
            return
            
        print("\n🔄 Frequency options:")
        print("1. Daily (every day)")
        print("2. Weekdays only (Monday-Friday)")
        print("3. Weekends only (Saturday-Sunday)")
        print("4. Specific day(s) of the week")
        print("5. Custom pattern")
        
        freq_choice = input("Choose frequency (1-5): ").strip()
        
        if freq_choice == "1":
            frequency = "daily"
            frequency_details = "daily"
            
        elif freq_choice == "2":
            frequency = "weekdays"
            frequency_details = "weekdays"
            
        elif freq_choice == "3":
            frequency = "weekends"
            frequency_details = "weekends"
            
        elif freq_choice == "4":
            print("\n📅 Select specific day(s):")
            print("1. Monday    2. Tuesday   3. Wednesday  4. Thursday")
            print("5. Friday    6. Saturday  7. Sunday")
            print("\nEnter day numbers separated by commas (e.g., 1,3,5 for Mon/Wed/Fri)")
            
            day_input = input("Selected days: ").strip()
            if not day_input:
                print("❌ No days selected.")
                return
                
            try:
                day_numbers = [int(x.strip()) for x in day_input.split(',')]
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                selected_days = [day_names[i-1] for i in day_numbers if 1 <= i <= 7]
                
                if not selected_days:
                    print("❌ No valid days selected.")
                    return
                    
                frequency = "specific_days"
                frequency_details = ",".join(selected_days)
                print(f"✅ Selected: {', '.join(selected_days)}")
                
            except (ValueError, IndexError):
                print("❌ Invalid day selection.")
                return
                
        elif freq_choice == "5":
            print("\n🔧 Custom pattern examples:")
            print("- 'every other Monday' (bi-weekly)")
            print("- 'first Friday of month'")
            print("- 'Monday,Wednesday,Friday' (specific days)")
            
            custom_pattern = input("Describe custom pattern: ").strip()
            if not custom_pattern:
                print("❌ No pattern specified.")
                return
                
            frequency = "custom"
            frequency_details = custom_pattern
            
        else:
            print("❌ Invalid option.")
            return
        
        preferred_time = input("🕐 Preferred time (HH:MM format, or press Enter for flexible): ").strip()
        
        # Validate time format if provided
        if preferred_time:
            try:
                datetime.strptime(preferred_time, "%H:%M")
            except ValueError:
                print("❌ Invalid time format. Use HH:MM (e.g., 09:30)")
                return
                
        category = input("📂 Category (work/personal/health): ").strip() or "General"
        
        try:
            priority = int(input("📊 Priority (1-10, default 5): ") or "5")
        except ValueError:
            priority = 5
            
        notes = input("📋 Notes (optional): ").strip()
        
        # Store recurring task with enhanced frequency data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recurring_tasks 
            (task_name, duration_minutes, preferred_time, frequency, frequency_details, category, priority, created_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_name, duration, preferred_time, frequency, frequency_details, category, priority, 
              datetime.now().isoformat(), notes))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Recurring task '{task_name}' added successfully!")
        print(f"🔄 Frequency: {frequency_details}")
        print(f"⏱️  Duration: {duration} minutes")
        if preferred_time:
            print(f"🕐 Preferred time: {preferred_time}")
            
    def view_recurring_tasks(self):
        """View all recurring tasks with detailed frequency information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add frequency_details column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE recurring_tasks ADD COLUMN frequency_details TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        cursor.execute('''
            SELECT id, task_name, duration_minutes, preferred_time, frequency, frequency_details, category, priority
            FROM recurring_tasks WHERE is_active = 1
            ORDER BY priority DESC, task_name
        ''')
        
        tasks = cursor.fetchall()
        conn.close()
        
        if not tasks:
            print("📝 No recurring tasks found.")
            return
            
        print("\n📅 RECURRING TASKS")
        print("=" * 80)
        
        for task in tasks:
            id, name, duration, pref_time, freq, freq_details, category, priority = task
            time_str = f" at {pref_time}" if pref_time else " (flexible time)"
            
            # Use frequency_details if available, otherwise use frequency
            frequency_display = freq_details if freq_details else freq.title()
            
            print(f"[{id}] 📋 {name}")
            print(f"    🔄 {frequency_display} | ⏱️ {duration} min{time_str}")
            print(f"    📂 {category} | 📊 Priority: {priority}/10")
            print("-" * 80)
            
    def delete_recurring_task(self):
        """Delete a recurring task"""
        self.view_recurring_tasks()
        
        try:
            task_id = int(input("\n🗑️  Enter task ID to delete: "))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get task details
            cursor.execute('SELECT task_name FROM recurring_tasks WHERE id = ? AND is_active = 1', (task_id,))
            task = cursor.fetchone()
            
            if task:
                confirm = input(f"❓ Delete '{task[0]}'? (y/N): ").lower()
                if confirm.startswith('y'):
                    cursor.execute('UPDATE recurring_tasks SET is_active = 0 WHERE id = ?', (task_id,))
                    conn.commit()
                    print(f"🗑️  Recurring task deleted successfully!")
                else:
                    print("❌ Deletion cancelled.")
            else:
                print("❌ Task ID not found.")
                
            conn.close()
            
        except ValueError:
            print("❌ Please enter a valid task ID number.")
    
    def get_recurring_tasks_for_date(self, target_date):
        """Get recurring tasks that should occur on a specific date with enhanced day matching"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add frequency_details column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE recurring_tasks ADD COLUMN frequency_details TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            pass
        
        cursor.execute('''
            SELECT task_name, duration_minutes, preferred_time, category, priority, frequency, frequency_details
            FROM recurring_tasks WHERE is_active = 1
        ''')
        
        all_recurring = cursor.fetchall()
        conn.close()
        
        applicable_tasks = []
        weekday = target_date.weekday()  # 0=Monday, 6=Sunday
        day_name = target_date.strftime("%A")
        
        for task_name, duration, pref_time, category, priority, frequency, freq_details in all_recurring:
            include_task = False
            
            if frequency == "daily":
                include_task = True
            elif frequency == "weekdays" and weekday < 5:  # Mon-Fri
                include_task = True
            elif frequency == "weekends" and weekday >= 5:  # Sat-Sun
                include_task = True
            elif frequency == "specific_days":
                # Check if today is in the specific days list
                if freq_details and day_name in freq_details:
                    include_task = True
            elif frequency == "custom":
                # Basic pattern matching for custom frequencies
                if freq_details and day_name.lower() in freq_details.lower():
                    include_task = True
            elif frequency == "weekly":
                # Legacy weekly support - treat as every week on same day
                include_task = True
                
            if include_task:
                applicable_tasks.append({
                    'task': task_name,
                    'duration': duration,
                    'preferred_time': pref_time,
                    'category': category,
                    'priority': priority,
                    'type': 'recurring'
                })
                
        return applicable_tasks
    
    def create_daily_schedule(self):
        """Create a comprehensive daily schedule including recurring tasks"""
        print("\n📅 DAILY SCHEDULE CREATOR")
        print("=" * 50)
        
        # Get target date
        date_input = input("📅 Date (YYYY-MM-DD) or press Enter for today: ").strip()
        if date_input:
            try:
                target_date = datetime.strptime(date_input, "%Y-%m-%d")
            except ValueError:
                print("❌ Invalid date format. Using today.")
                target_date = datetime.now()
        else:
            target_date = datetime.now()
            
        date_str = target_date.strftime("%Y-%m-%d")
        weekday = target_date.strftime("%A")
        
        print(f"📅 Creating schedule for {weekday}, {target_date.strftime('%B %d, %Y')}")
        
        # Get recurring tasks for this date
        recurring_tasks = self.get_recurring_tasks_for_date(target_date)
        
        if recurring_tasks:
            print(f"\n🔄 Found {len(recurring_tasks)} recurring tasks for this day:")
            for task in recurring_tasks:
                time_str = f" at {task['preferred_time']}" if task['preferred_time'] else ""
                print(f"   • {task['task']} ({task['duration']} min{time_str})")
        
        # Get additional tasks for the day
        print(f"\n📝 Enter additional tasks for {weekday}:")
        print("(Include specific times like 'Meeting at 10:15 AM' or 'Due at 08:00 AM')")
        print("(Type each task and press Enter. Type 'done' when finished)")
        
        additional_tasks = []
        while True:
            task_input = input("➕ Task: ").strip()
            if task_input.lower() in ['done', 'finished', 'complete']:
                break
            if task_input:
                # Extract time from task description
                extracted_time = self.extract_time_from_description(task_input)
                
                try:
                    duration = int(input(f"   ⏱️  Estimated minutes for '{task_input}': "))
                    category = input(f"   📂 Category (work/personal/learning): ").strip() or "General"
                    
                    additional_tasks.append({
                        'task': task_input,
                        'duration': duration,
                        'category': category,
                        'preferred_time': extracted_time,  # Use extracted time
                        'priority': 5,
                        'type': 'additional'
                    })
                    
                    if extracted_time:
                        print(f"   🕐 Detected time: {extracted_time}")
                        
                except ValueError:
                    print("   ❌ Invalid duration. Skipping task.")
        
        # Combine all tasks
        all_tasks = recurring_tasks + additional_tasks
        
        if not all_tasks:
            print("❌ No tasks to schedule.")
            return
            
        # Generate structured schedule with proper time handling
        schedule = self.generate_accurate_schedule(all_tasks, target_date)
        
        # Get AI scheduling analysis
        task_summary = []
        total_minutes = 0
        for task in all_tasks:
            task_summary.append(f"{task['task']} ({task['duration']} min, {task['category']})")
            total_minutes += task['duration']
            
        context = f"""
        Date: {weekday}, {date_str}
        Total tasks: {len(all_tasks)}
        Total estimated time: {total_minutes} minutes ({total_minutes//60}h {total_minutes%60}m)
        Fixed-time tasks: {sum(1 for t in all_tasks if t['preferred_time'])}
        """
        
        ai_analysis = self.ask_claude(
            f"Analyze this optimized daily schedule: {', '.join(task_summary)}",
            context
        )
        
        # Display the schedule
        self.display_daily_schedule(schedule, date_str, weekday, ai_analysis)
        
        # Save option
        save_choice = input("\n💾 Save this schedule? (y/N): ").lower()
        if save_choice.startswith('y'):
            self.save_daily_schedule(schedule, date_str, total_minutes, True)
            print("✅ Schedule saved successfully!")
            
    def generate_accurate_schedule(self, tasks, target_date):
        """Generate schedule with accurate time placement"""
        # Separate fixed-time and flexible tasks
        fixed_time_tasks = [t for t in tasks if t['preferred_time']]
        flexible_tasks = [t for t in tasks if not t['preferred_time']]
        
        # Sort fixed-time tasks by their preferred time
        fixed_time_tasks.sort(key=lambda x: x['preferred_time'])
        
        # Sort flexible tasks by priority
        flexible_tasks.sort(key=lambda x: x['priority'], reverse=True)
        
        schedule = []
        
        # Add fixed-time tasks first - these go at their exact specified times
        for task in fixed_time_tasks:
            schedule.append({
                'time': task['preferred_time'],
                'task': task['task'],
                'duration': f"{task['duration']} min",
                'category': task['category'],
                'type': task['type'],
                'priority': 'FIXED TIME'
            })
        
        # Schedule flexible tasks around fixed ones
        if flexible_tasks:
            # Find available time slots
            available_slots = self.find_available_time_slots(fixed_time_tasks, target_date)
            
            for i, task in enumerate(flexible_tasks):
                if i < len(available_slots):
                    slot_time = available_slots[i]
                    schedule.append({
                        'time': slot_time,
                        'task': task['task'],
                        'duration': f"{task['duration']} min",
                        'category': task['category'],
                        'type': task['type'],
                        'priority': f"Priority {task['priority']}"
                    })
        
        # Sort final schedule by time
        schedule.sort(key=lambda x: x['time'])
        
        return schedule
    
    def find_available_time_slots(self, fixed_tasks, target_date):
        """Find available time slots between fixed appointments"""
        available_slots = []
        
        # Define work day boundaries
        work_start = datetime.strptime("08:00", "%H:%M").time()
        work_end = datetime.strptime("18:00", "%H:%M").time()
        
        if not fixed_tasks:
            # No fixed tasks, start from work day beginning
            current_time = work_start
            for i in range(8):  # Up to 8 flexible slots
                available_slots.append(current_time.strftime("%H:%M"))
                current_time = (datetime.combine(target_date.date(), current_time) + timedelta(minutes=60)).time()
        else:
            # Find gaps between fixed tasks
            current_time = work_start
            
            for fixed_task in sorted(fixed_tasks, key=lambda x: x['preferred_time']):
                fixed_time = datetime.strptime(fixed_task['preferred_time'], "%H:%M").time()
                
                # If there's a gap before this fixed task
                if current_time < fixed_time:
                    available_slots.append(current_time.strftime("%H:%M"))
                
                # Move current time past this fixed task
                task_end = (datetime.combine(target_date.date(), fixed_time) + 
                           timedelta(minutes=fixed_task['duration'] + 15)).time()  # 15 min buffer
                current_time = max(current_time, task_end)
            
            # Add slots after last fixed task if there's time
            while current_time < work_end and len(available_slots) < 8:
                available_slots.append(current_time.strftime("%H:%M"))
                current_time = (datetime.combine(target_date.date(), current_time) + timedelta(minutes=60)).time()
        
        return available_slots
    
    def display_daily_schedule(self, schedule, date_str, weekday, ai_analysis):
        """Display the generated daily schedule"""
        print(f"\n📅 OPTIMIZED DAILY SCHEDULE")
        print(f"📆 {weekday}, {date_str}")
        print("=" * 60)
        
        for item in schedule:
            type_icon = "🔄" if item['type'] == 'recurring' else "📝"
            priority_display = f" | {item['priority']}" if item['priority'] != 'FIXED TIME' else " | FIXED"
            
            print(f"{item['time']} | {type_icon} {item['task']}")
            print(f"         ⏱️ {item['duration']} | 📂 {item['category']}{priority_display}")
            print("-" * 60)
            
        print(f"\n🤖 AI SCHEDULING INSIGHTS:")
        print(ai_analysis[:300] + "..." if len(ai_analysis) > 300 else ai_analysis)
        
    def save_daily_schedule(self, schedule, date_str, total_minutes, includes_recurring):
        """Save the daily schedule to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        schedule_data = {
            'date': date_str,
            'schedule': schedule,
            'created_at': datetime.now().isoformat(),
            'total_minutes': total_minutes
        }
        
        cursor.execute('''
            INSERT INTO daily_schedules 
            (schedule_date, schedule_data, schedule_type, created_date, total_time_minutes, recurring_tasks_included)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date_str, json.dumps(schedule_data), 'daily', datetime.now().isoformat(), 
              total_minutes, 1 if includes_recurring else 0))
        
        conn.commit()
        conn.close()
        
    def manage_recurring_tasks_menu(self):
        """Recurring tasks management menu"""
        while True:
            print("\n🔄 RECURRING TASKS MANAGEMENT")
            print("=" * 40)
            print("1. ➕ Add new recurring task")
            print("2. 👀 View all recurring tasks") 
            print("3. 🗑️  Delete recurring task")
            print("4. 🔙 Back to main menu")
            
            choice = input("\nChoose an option (1-4): ").strip()
            
            if choice == "1":
                self.add_recurring_task()
            elif choice == "2":
                self.view_recurring_tasks()
            elif choice == "3":
                self.delete_recurring_task()
            elif choice == "4":
                break
            else:
                print("❌ Invalid option. Please choose 1-4.")
            
            if choice != "4":
                input("\n⏸️  Press Enter to continue...")

def main():
    """Main daily scheduler interface"""
    scheduler = DailyScheduleCreator()
    
    while True:
        print("\n" + "="*50)
        print("📅 DAILY SCHEDULE CREATOR")
        print("="*50)
        print("1. 📝 Create daily schedule (with recurring tasks)")
        print("2. 🔄 Manage recurring tasks")
        print("3. 👀 View saved schedules")
        print("4. 🔙 Back to main Jarvis")
        print("="*50)
        
        choice = input("🎯 Choose an option (1-4): ").strip()
        
        if choice == "1":
            scheduler.create_daily_schedule()
        elif choice == "2":
            scheduler.manage_recurring_tasks_menu()
        elif choice == "3":
            print("💡 Use main Jarvis menu → Option 7: Export Schedule to Calendar")
        elif choice == "4":
            break
        else:
            print("❌ Invalid option. Please choose 1-4.")
        
        if choice != "4":
            input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    main()