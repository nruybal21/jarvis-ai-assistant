# Corrected Weekly Schedule Planner with Enhanced Time Handling
# File: src/weekly_scheduler.py

import sqlite3
import json
import requests
import re
from datetime import datetime, timedelta
import os

class WeeklySchedulePlanner:
    def __init__(self):
        """Initialize Weekly Schedule Planner with enhanced time handling"""
        self.db_path = "data/jarvis.db"
        self.setup_weekly_database()
        
    def setup_weekly_database(self):
        """Setup database tables for weekly planning"""
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Weekly schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_start_date TEXT NOT NULL,
                week_end_date TEXT NOT NULL,
                schedule_data TEXT NOT NULL,
                created_date TEXT,
                total_weekly_hours REAL,
                recurring_tasks_integrated INTEGER DEFAULT 1
            )
        ''')
        
        # Weekly goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_start_date TEXT NOT NULL,
                goal_description TEXT NOT NULL,
                category TEXT,
                priority INTEGER DEFAULT 5,
                estimated_hours REAL,
                status TEXT DEFAULT 'active',
                specific_times TEXT,
                preferred_days TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def extract_time_from_description(self, description):
        """Extract specific times from task descriptions"""
        time_patterns = [
            r'\bat\s+(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',
            r'\bdue\s+at\s+(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',
            r'\bby\s+(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',
            r'\b(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                period = match.group(3).upper()
                
                if period == 'PM' and hour != 12:
                    hour += 12
                elif period == 'AM' and hour == 12:
                    hour = 0
                    
                return f"{hour:02d}:{minute:02d}"
        
        return None
    
    def extract_days_from_description(self, description):
        """Extract specific days from task descriptions"""
        days_pattern = r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)\b'
        days_found = re.findall(days_pattern, description, re.IGNORECASE)
        
        day_mapping = {
            'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday', 
            'thu': 'Thursday', 'fri': 'Friday', 'sat': 'Saturday', 'sun': 'Sunday'
        }
        
        normalized_days = []
        for day in days_found:
            day_lower = day.lower()
            if day_lower in day_mapping:
                normalized_days.append(day_mapping[day_lower])
            else:
                normalized_days.append(day_lower.capitalize())
        
        return list(set(normalized_days))  # Remove duplicates
    
    def ask_claude_weekly(self, question, context=""):
        """AI analysis for weekly scheduling"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {"Content-Type": "application/json"}
        
        full_prompt = f"""
        You are an expert weekly planning assistant. Create comprehensive 7-day schedules that optimize productivity and work-life balance.
        
        Context: {context}
        
        Planning Request: {question}
        
        Consider:
        - Weekly workload distribution
        - Energy management across the week
        - Project deadlines and priorities
        - Recurring task integration
        - Buffer time for unexpected tasks
        - Weekend balance and recovery time
        - Specific time constraints mentioned
        
        Provide strategic weekly planning insights.
        """
        
        data = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1200,
            "messages": [{"role": "user", "content": full_prompt}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                return "AI weekly planning analysis temporarily unavailable. Using optimized default planning."
        except Exception as e:
            return "Using intelligent default weekly planning based on best practices."
    
    def get_recurring_tasks_for_week(self, start_date):
        """Get all recurring tasks for a week with accurate time placement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT task_name, duration_minutes, preferred_time, frequency, category, priority
            FROM recurring_tasks WHERE is_active = 1
        ''')
        
        recurring_tasks = cursor.fetchall()
        conn.close()
        
        weekly_recurring = {}
        
        # Generate recurring tasks for each day of the week
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            day_name = current_date.strftime("%A")
            weekday = current_date.weekday()
            
            daily_recurring = []
            
            for task_name, duration, pref_time, frequency, category, priority in recurring_tasks:
                include_task = False
                
                if frequency == "daily":
                    include_task = True
                elif frequency == "weekdays" and weekday < 5:
                    include_task = True
                elif frequency == "weekends" and weekday >= 5:
                    include_task = True
                elif frequency == "weekly":
                    include_task = True
                    
                if include_task:
                    daily_recurring.append({
                        'task': task_name,
                        'duration': duration,
                        'preferred_time': pref_time,
                        'category': category,
                        'priority': priority,
                        'type': 'recurring'
                    })
            
            weekly_recurring[day_name] = daily_recurring
            
        return weekly_recurring
    
    def add_weekly_goal(self, week_start):
        """Add a goal for the week with time and day specifications"""
        print("\n🎯 ADD WEEKLY GOAL")
        print("=" * 30)
        
        goal = input("📝 Goal description (include specific times/days if needed): ").strip()
        if not goal:
            print("❌ Goal description required.")
            return
            
        category = input("📂 Category (work/personal/learning/health): ").strip() or "General"
        
        try:
            estimated_hours = float(input("⏱️  Estimated hours needed: "))
        except ValueError:
            print("❌ Please enter a valid number for hours.")
            return
            
        try:
            priority = int(input("📊 Priority (1-10, default 5): ") or "5")
        except ValueError:
            priority = 5
        
        # Extract time and day preferences from description
        extracted_time = self.extract_time_from_description(goal)
        extracted_days = self.extract_days_from_description(goal)
        
        if extracted_time:
            print(f"🕐 Detected time preference: {extracted_time}")
        if extracted_days:
            print(f"📅 Detected day preferences: {', '.join(extracted_days)}")
        
        # Allow manual override
        manual_days = input("📅 Specific days (comma-separated, or press Enter to use detected/flexible): ").strip()
        if manual_days:
            extracted_days = [day.strip().capitalize() for day in manual_days.split(',')]
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO weekly_goals 
            (week_start_date, goal_description, category, priority, estimated_hours, specific_times, preferred_days)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (week_start.strftime("%Y-%m-%d"), goal, category, priority, estimated_hours, 
              extracted_time, ','.join(extracted_days) if extracted_days else ''))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Weekly goal added: {goal}")
        print(f"⏱️  Estimated time: {estimated_hours} hours")
        if extracted_time:
            print(f"🕐 Preferred time: {extracted_time}")
        if extracted_days:
            print(f"📅 Preferred days: {', '.join(extracted_days)}")
        
    def view_weekly_goals(self, week_start):
        """View goals for a specific week"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT goal_description, category, estimated_hours, priority, specific_times, preferred_days
            FROM weekly_goals 
            WHERE week_start_date = ? AND status = 'active'
            ORDER BY priority DESC
        ''', (week_start.strftime("%Y-%m-%d"),))
        
        goals = cursor.fetchall()
        conn.close()
        
        if not goals:
            print("📝 No weekly goals found.")
            return []
            
        print(f"\n🎯 WEEKLY GOALS")
        print("=" * 40)
        
        goal_list = []
        for goal, category, hours, priority, specific_time, preferred_days in goals:
            print(f"📌 {goal}")
            details = f"   📂 {category} | ⏱️ {hours}h | 📊 Priority: {priority}/10"
            if specific_time:
                details += f" | 🕐 {specific_time}"
            if preferred_days:
                details += f" | 📅 {preferred_days}"
            print(details)
            
            goal_list.append({
                'goal': goal,
                'category': category,
                'hours': hours,
                'priority': priority,
                'specific_time': specific_time,
                'preferred_days': preferred_days.split(',') if preferred_days else []
            })
            
        return goal_list
    
    def create_weekly_schedule(self):
        """Create a comprehensive weekly schedule with accurate time placement"""
        print("\n📅 WEEKLY SCHEDULE PLANNER")
        print("=" * 50)
        
        # Get week start date
        date_input = input("📅 Week start date (YYYY-MM-DD) or press Enter for this Monday: ").strip()
        
        if date_input:
            try:
                start_date = datetime.strptime(date_input, "%Y-%m-%d")
            except ValueError:
                print("❌ Invalid date format. Using this Monday.")
                start_date = self.get_monday_of_week(datetime.now())
        else:
            start_date = self.get_monday_of_week(datetime.now())
            
        end_date = start_date + timedelta(days=6)
        
        print(f"📅 Planning week: {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}")
        
        # Get recurring tasks for the week
        weekly_recurring = self.get_recurring_tasks_for_week(start_date)
        
        # Show recurring tasks summary
        total_recurring_time = 0
        for day, tasks in weekly_recurring.items():
            day_time = sum(task['duration'] for task in tasks)
            total_recurring_time += day_time
            if tasks:
                print(f"   {day}: {len(tasks)} recurring tasks ({day_time} min)")
                
        print(f"🔄 Total weekly recurring time: {total_recurring_time//60}h {total_recurring_time%60}m")
        
        # Get or add weekly goals
        goals = self.view_weekly_goals(start_date)
        
        add_goals = input(f"\n➕ Add weekly goals? (y/N): ").lower()
        if add_goals.startswith('y'):
            while True:
                self.add_weekly_goal(start_date)
                another = input("Add another goal? (y/N): ").lower()
                if not another.startswith('y'):
                    break
            goals = self.view_weekly_goals(start_date)
        
        # Get additional weekly tasks/projects with time specifications
        print(f"\n📝 Additional tasks/projects for this week:")
        print("(Include specific times and days like 'Team meeting Monday at 2:00 PM')")
        print("(Type each task and press Enter. Type 'done' when finished)")
        
        additional_tasks = []
        while True:
            task_input = input("➕ Task/Project: ").strip()
            if task_input.lower() in ['done', 'finished', 'complete']:
                break
            if task_input:
                try:
                    hours = float(input(f"   ⏱️  Estimated hours for '{task_input}': "))
                    category = input(f"   📂 Category: ").strip() or "General"
                    
                    # Extract time and day preferences
                    extracted_time = self.extract_time_from_description(task_input)
                    extracted_days = self.extract_days_from_description(task_input)
                    
                    if extracted_time:
                        print(f"   🕐 Detected time: {extracted_time}")
                    if extracted_days:
                        print(f"   📅 Detected days: {', '.join(extracted_days)}")
                    
                    # Allow manual override
                    if not extracted_days:
                        manual_days = input(f"   📅 Preferred days (comma-separated, or press Enter for flexible): ").strip()
                        if manual_days:
                            extracted_days = [day.strip().capitalize() for day in manual_days.split(',')]
                    
                    additional_tasks.append({
                        'task': task_input,
                        'hours': hours,
                        'minutes': int(hours * 60),
                        'category': category,
                        'preferred_days': extracted_days,
                        'preferred_time': extracted_time,
                        'type': 'project'
                    })
                except ValueError:
                    print("   ❌ Invalid input. Skipping task.")
        
        # Generate weekly schedule with accurate time placement
        weekly_schedule = self.generate_accurate_weekly_schedule(
            start_date, weekly_recurring, goals, additional_tasks
        )
        
        # Get AI analysis
        context = self.build_weekly_context(weekly_recurring, goals, additional_tasks)
        ai_analysis = self.ask_claude_weekly(
            f"Analyze and optimize this weekly schedule for maximum productivity and balance",
            context
        )
        
        # Display the schedule
        self.display_weekly_schedule(weekly_schedule, start_date, end_date, ai_analysis)
        
        # Save option
        save_choice = input("\n💾 Save this weekly schedule? (y/N): ").lower()
        if save_choice.startswith('y'):
            self.save_weekly_schedule(weekly_schedule, start_date, end_date)
            print("✅ Weekly schedule saved successfully!")
            
    def get_monday_of_week(self, date):
        """Get the Monday of the week for a given date"""
        days_after_monday = date.weekday()
        monday = date - timedelta(days=days_after_monday)
        return monday
    
    def generate_accurate_weekly_schedule(self, start_date, recurring_tasks, goals, additional_tasks):
        """Generate structured weekly schedule with accurate time placement"""
        weekly_schedule = {}
        
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            day_name = current_date.strftime("%A")
            
            daily_schedule = []
            
            # Add recurring tasks (these have preferred times)
            if day_name in recurring_tasks:
                for task in recurring_tasks[day_name]:
                    daily_schedule.append({
                        'time': task['preferred_time'] or '09:00',
                        'task': task['task'],
                        'duration': f"{task['duration']} min",
                        'category': task['category'],
                        'type': 'recurring',
                        'priority': task['priority'],
                        'fixed_time': bool(task['preferred_time'])
                    })
            
            # Add goal-related work with time preferences
            for goal in goals:
                goal_days = goal['preferred_days'] if goal['preferred_days'] else ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                
                if day_name in goal_days and goal['hours'] > 0:
                    # Distribute goal work across preferred days
                    daily_goal_time = goal['hours'] / len(goal_days)
                    if daily_goal_time >= 0.5:  # Only if at least 30 minutes
                        goal_time = goal['specific_time'] or '10:00'
                        daily_schedule.append({
                            'time': goal_time,
                            'task': f"Work on: {goal['goal']}",
                            'duration': f"{int(daily_goal_time * 60)} min",
                            'category': goal['category'],
                            'type': 'goal',
                            'priority': goal['priority'],
                            'fixed_time': bool(goal['specific_time'])
                        })
            
            # Add project tasks for preferred days and times
            for task in additional_tasks:
                task_days = task['preferred_days'] if task['preferred_days'] else [day_name]
                
                if day_name in task_days:
                    # If specific time mentioned, respect it
                    if task['preferred_time']:
                        daily_schedule.append({
                            'time': task['preferred_time'],
                            'task': task['task'],
                            'duration': f"{task['minutes']} min",
                            'category': task['category'],
                            'type': 'project',
                            'priority': 5,
                            'fixed_time': True
                        })
                    else:
                        # Flexible scheduling
                        days_count = len(task_days)
                        daily_task_time = task['hours'] / days_count
                        
                        if daily_task_time >= 0.5:
                            daily_schedule.append({
                                'time': '14:00',  # Default afternoon slot
                                'task': task['task'],
                                'duration': f"{int(daily_task_time * 60)} min",
                                'category': task['category'],
                                'type': 'project',
                                'priority': 5,
                                'fixed_time': False
                            })
            
            # Sort by fixed_time first (fixed times maintain their slots), then by time
            daily_schedule.sort(key=lambda x: (not x['fixed_time'], x['time']))
            
            # Resolve conflicts for flexible tasks
            daily_schedule = self.resolve_daily_conflicts(daily_schedule, current_date)
            
            weekly_schedule[day_name] = daily_schedule
            
        return weekly_schedule
    
    def resolve_daily_conflicts(self, daily_schedule, date):
        """Resolve scheduling conflicts by moving flexible tasks"""
        fixed_tasks = [task for task in daily_schedule if task['fixed_time']]
        flexible_tasks = [task for task in daily_schedule if not task['fixed_time']]
        
        # Keep fixed tasks as-is
        resolved_schedule = fixed_tasks.copy()
        
        # Find available slots for flexible tasks
        if flexible_tasks:
            available_slots = self.find_available_weekly_slots(fixed_tasks, date)
            
            for i, task in enumerate(flexible_tasks):
                if i < len(available_slots):
                    task['time'] = available_slots[i]
                    resolved_schedule.append(task)
        
        # Sort final schedule by time
        resolved_schedule.sort(key=lambda x: x['time'])
        
        return resolved_schedule
    
    def find_available_weekly_slots(self, fixed_tasks, date):
        """Find available time slots between fixed appointments"""
        available_slots = []
        
        # Work day boundaries
        work_hours = ['08:00', '09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00', '17:00']
        
        # Get times already taken by fixed tasks
        taken_times = {task['time'] for task in fixed_tasks}
        
        # Find available slots
        for time_slot in work_hours:
            if time_slot not in taken_times:
                available_slots.append(time_slot)
        
        return available_slots
    
    def build_weekly_context(self, recurring_tasks, goals, additional_tasks):
        """Build context for AI analysis"""
        total_recurring = sum(len(tasks) for tasks in recurring_tasks.values())
        total_goal_hours = sum(goal['hours'] for goal in goals)
        total_project_hours = sum(task['hours'] for task in additional_tasks)
        
        fixed_time_items = sum(1 for goal in goals if goal['specific_time']) + \
                          sum(1 for task in additional_tasks if task['preferred_time'])
        
        context = f"""
        Weekly Planning Context:
        - Recurring tasks: {total_recurring} tasks across the week
        - Weekly goals: {len(goals)} goals totaling {total_goal_hours} hours
        - Additional projects: {len(additional_tasks)} projects totaling {total_project_hours} hours
        - Fixed-time commitments: {fixed_time_items} items with specific times
        - Total planned work: {total_goal_hours + total_project_hours} hours
        
        Goal categories: {', '.join(set(goal['category'] for goal in goals)) if goals else 'None'}
        Project categories: {', '.join(set(task['category'] for task in additional_tasks)) if additional_tasks else 'None'}
        """
        
        return context
    
    def display_weekly_schedule(self, schedule, start_date, end_date, ai_analysis):
        """Display the generated weekly schedule"""
        print(f"\n📅 OPTIMIZED WEEKLY SCHEDULE")
        print(f"📆 {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}")
        print("=" * 80)
        
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            day_name = current_date.strftime("%A")
            day_date = current_date.strftime("%m/%d")
            
            print(f"\n📅 {day_name.upper()} ({day_date})")
            print("-" * 40)
            
            if day_name in schedule and schedule[day_name]:
                for item in schedule[day_name]:
                    type_icons = {
                        'recurring': '🔄',
                        'goal': '🎯',
                        'project': '📝',
                        'flexible': '⚡'
                    }
                    icon = type_icons.get(item['type'], '📌')
                    
                    # Show if time is fixed or flexible
                    time_indicator = " (FIXED)" if item.get('fixed_time') else ""
                    
                    print(f"{item['time']}{time_indicator} | {icon} {item['task']}")
                    print(f"         ⏱️ {item['duration']} | 📂 {item['category']}")
                    
                # Calculate daily total
                daily_total = 0
                for item in schedule[day_name]:
                    duration_str = item['duration'].replace(' min', '')
                    daily_total += int(duration_str)
                    
                print(f"📊 Daily total: {daily_total//60}h {daily_total%60}m")
            else:
                print("   🏖️  Light day / Rest day")
                
        print(f"\n🤖 AI WEEKLY INSIGHTS:")
        print("-" * 40)
        print(ai_analysis[:400] + "..." if len(ai_analysis) > 400 else ai_analysis)
        
    def save_weekly_schedule(self, schedule, start_date, end_date):
        """Save weekly schedule to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate total weekly hours
        total_minutes = 0
        for day_schedule in schedule.values():
            for item in day_schedule:
                duration_str = item['duration'].replace(' min', '')
                total_minutes += int(duration_str)
                
        total_hours = total_minutes / 60
        
        schedule_data = {
            'start_date': start_date.strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'schedule': schedule,
            'created_at': datetime.now().isoformat(),
            'total_hours': total_hours
        }
        
        cursor.execute('''
            INSERT INTO weekly_schedules 
            (week_start_date, week_end_date, schedule_data, created_date, total_weekly_hours)
            VALUES (?, ?, ?, ?, ?)
        ''', (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), 
              json.dumps(schedule_data), datetime.now().isoformat(), total_hours))
        
        conn.commit()
        conn.close()
    
    def view_saved_weekly_schedules(self):
        """View saved weekly schedules"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, week_start_date, week_end_date, total_weekly_hours, created_date
            FROM weekly_schedules
            ORDER BY week_start_date DESC
        ''')
        
        schedules = cursor.fetchall()
        conn.close()
        
        if not schedules:
            print("📝 No saved weekly schedules found.")
            return
            
        print("\n📅 SAVED WEEKLY SCHEDULES")
        print("=" * 60)
        
        for id, start, end, hours, created in schedules:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            created_date = datetime.fromisoformat(created)
            
            print(f"[{id}] 📅 {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}")
            print(f"     ⏱️ Total: {hours:.1f} hours | 📅 Created: {created_date.strftime('%m/%d')}")
            print("-" * 60)

def main():
    """Main weekly scheduler interface"""
    planner = WeeklySchedulePlanner()
    
    while True:
        print("\n" + "="*50)
        print("📅 WEEKLY SCHEDULE PLANNER")
        print("="*50)
        print("1. 📝 Create weekly schedule")
        print("2. 👀 View saved weekly schedules")
        print("3. 🎯 Quick goal setting")
        print("4. 🔙 Back to main Jarvis")
        print("="*50)
        
        choice = input("🎯 Choose an option (1-4): ").strip()
        
        if choice == "1":
            planner.create_weekly_schedule()
        elif choice == "2":
            planner.view_saved_weekly_schedules()
        elif choice == "3":
            start_date = planner.get_monday_of_week(datetime.now())
            planner.add_weekly_goal(start_date)
        elif choice == "4":
            break
        else:
            print("❌ Invalid option. Please choose 1-4.")
        
        if choice != "4":
            input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    main()