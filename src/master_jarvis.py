#!/usr/bin/env python3
"""
Master Jarvis - Unified AI Assistant System
Combines basic_jarvis.py + enhanced_jarvis.py + visual_jarvis.py
All AI training and data stored in one unified system
"""

import sqlite3
import json
import requests
import sys
import os
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading

# Visual enhancements
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    VISUAL_AVAILABLE = True
except ImportError:
    VISUAL_AVAILABLE = False
    print("Note: Install 'pip install colorama' for enhanced visual interface")

# Add config path for credentials
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
try:
    from credentials import CLAUDE_API_KEY
except ImportError:
    CLAUDE_API_KEY = None
    print("Warning: credentials.py not found. Some AI features will be limited.")

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

class VisualEffects:
    """Visual effects and animations for enhanced interface"""
    
    @staticmethod
    def print_animated_text(text, delay=0.03, color=None):
        """Typewriter effect for text"""
        if not VISUAL_AVAILABLE or color is None:
            print(text)
            return
            
        colors = {
            'blue': Fore.CYAN,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'red': Fore.RED,
            'magenta': Fore.MAGENTA,
            'white': Fore.WHITE
        }
        
        color_code = colors.get(color, Fore.WHITE)
        for char in text:
            print(color_code + char, end='', flush=True)
            time.sleep(delay)
        print(Style.RESET_ALL)
    
    @staticmethod
    def show_loading_animation(text, duration=2):
        """Show spinning loading animation"""
        if not VISUAL_AVAILABLE:
            print(f"{text}...")
            time.sleep(duration)
            return
            
        frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                print(f'\r{Fore.CYAN}{frame} {text}...{Style.RESET_ALL}', end='', flush=True)
                time.sleep(0.1)
        
        print(f'\r{Fore.GREEN}✓ {text} complete!{Style.RESET_ALL}')
    
    @staticmethod
    def print_header(title):
        """Print a beautiful header"""
        if not VISUAL_AVAILABLE:
            print(f"\n=== {title} ===\n")
            return
            
        width = max(60, len(title) + 10)
        border = '=' * width
        
        print(f"\n{Fore.CYAN}{border}")
        print(f"{Fore.YELLOW}{title:^{width}}")
        print(f"{Fore.CYAN}{border}{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_menu_option(number, description, icon="▶"):
        """Print a styled menu option"""
        if not VISUAL_AVAILABLE:
            print(f"{number}. {description}")
            return
            
        print(f"{Fore.GREEN}{icon} {Fore.YELLOW}{number}.{Fore.WHITE} {description}{Style.RESET_ALL}")
    
    @staticmethod
    def print_ai_response(text, thinking=False):
        """Print AI responses with special formatting"""
        if not VISUAL_AVAILABLE:
            if thinking:
                print("🤔 AI is thinking...")
            print(f"🤖 Jarvis: {text}")
            return
            
        if thinking:
            VisualEffects.show_loading_animation("AI Processing", 1)
            
        print(f"\n{Fore.CYAN}🤖 {Fore.MAGENTA}Jarvis:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{text}{Style.RESET_ALL}\n")

class MasterJarvisDatabase:
    """Unified database system for all Jarvis features"""
    
    def __init__(self, db_path='data/master_jarvis.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize all database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced tasks table with time support
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                urgency_score INTEGER DEFAULT 5,
                importance_score INTEGER DEFAULT 5,
                estimated_time REAL,
                actual_time REAL,
                category TEXT DEFAULT 'admin',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                due_date TIMESTAMP,
                due_time TEXT,
                energy_level TEXT DEFAULT 'medium',
                context TEXT,
                tags TEXT,
                is_recurring INTEGER DEFAULT 0,
                recurrence_pattern TEXT,
                recurrence_end_date TIMESTAMP,
                parent_task_id INTEGER,
                FOREIGN KEY (parent_task_id) REFERENCES tasks (id)
            )
        ''')
        
        # Conversations table for enhanced AI memory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                context TEXT,
                session_id TEXT,
                conversation_type TEXT DEFAULT 'general'
            )
        ''')
        
        # Productivity patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productivity_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Schedules table for saved schedules
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                schedule_date TEXT NOT NULL,
                schedule_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User preferences and settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_task(self, title, description="", urgency=5, importance=5, 
                 estimated_time=None, category="general", due_date=None, 
                 energy_level="medium", context="", tags=""):
        """Add a new task with comprehensive data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks 
            (title, description, urgency_score, importance_score, estimated_time, 
             category, due_date, energy_level, context, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, urgency, importance, estimated_time, 
              category, due_date, energy_level, context, tags))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_tasks(self, status='pending', limit=None):
        """Get tasks with intelligent sorting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, title, description, 
                   COALESCE(urgency_score, 5) as urgency_score, 
                   COALESCE(importance_score, 5) as importance_score, 
                   estimated_time, actual_time, category, status, created_at,
                   completed_at, due_date, energy_level, context, tags,
                   (COALESCE(urgency_score, 5) + COALESCE(importance_score, 5)) as priority_total
            FROM tasks 
            WHERE status = ?
            ORDER BY priority_total DESC, created_at ASC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (status,))
        tasks = cursor.fetchall()
        conn.close()
        
        return tasks
    
    def complete_task(self, task_id, actual_time=None):
        """Mark task as complete and record actual time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP, actual_time = ?
            WHERE id = ?
        ''', (actual_time, task_id))
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_input, ai_response, context="", session_id="", conversation_type="general"):
        """Save conversation for AI learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (user_input, ai_response, context, session_id, conversation_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_input, ai_response, context, session_id, conversation_type))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, limit=10, session_id=None):
        """Get conversation history for context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT user_input, ai_response, context, timestamp 
                FROM conversations 
                WHERE session_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (session_id, limit))
        else:
            cursor.execute('''
                SELECT user_input, ai_response, context, timestamp 
                FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return list(reversed(conversations))  # Return in chronological order
    
    def analyze_productivity_patterns(self):
        """Analyze user productivity patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Time estimation accuracy
        cursor.execute('''
            SELECT estimated_time, actual_time, category
            FROM tasks 
            WHERE estimated_time IS NOT NULL AND actual_time IS NOT NULL
        ''')
        
        time_data = cursor.fetchall()
        
        # Task completion rates by category
        cursor.execute('''
            SELECT category, 
                   COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                   COUNT(*) as total
            FROM tasks 
            GROUP BY category
        ''')
        
        completion_data = cursor.fetchall()
        
        conn.close()
        
        return {
            'time_estimation': time_data,
            'completion_rates': completion_data
        }

class MasterJarvisAI:
    """Unified AI system for all Jarvis intelligence"""
    
    def __init__(self, database):
        self.db = database
        self.session_id = f"session_{int(time.time())}"
        
    def call_claude_api(self, prompt, context=""):
        """Call Claude API with conversation context"""
        if not CLAUDE_API_KEY:
            print("Debug: No CLAUDE_API_KEY found")
            return self._fallback_response(prompt)
        
        print(f"Debug: API Key present: {CLAUDE_API_KEY[:15]}..." if CLAUDE_API_KEY else "Debug: No API Key")
        
        # Get conversation history for context
        history = self.db.get_conversation_history(5, self.session_id)
        context_prompt = ""
        
        if history:
            context_prompt = "\n\nRecent conversation context:\n"
            for user_msg, ai_msg, _, timestamp in history:
                context_prompt += f"User: {user_msg}\nJarvis: {ai_msg}\n\n"
        
        full_prompt = f"""You are Jarvis, an advanced personal AI assistant. You help with productivity, task management, and career development as an AI Integration Specialist.

Current context: {context}
{context_prompt}

User request: {prompt}

Provide helpful, specific, and actionable advice. Be conversational but professional."""

        try:
            print("Debug: Making API request...")
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1000,
                    "messages": [
                        {"role": "user", "content": full_prompt}
                    ]
                },
                timeout=30
            )
            
            print(f"Debug: API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['content'][0]['text']
                
                print("Debug: API call successful!")
                
                # Save conversation for learning
                self.db.save_conversation(prompt, ai_response, context, self.session_id)
                
                return ai_response
            else:
                print(f"Debug: API error - Status: {response.status_code}, Response: {response.text}")
                return self._fallback_response(prompt)
                
        except Exception as e:
            print(f"Debug: API Exception: {str(e)}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt):
        """Fallback responses when API isn't available"""
        fallback_responses = {
            'schedule': "I'd help you schedule that task. Without API access, I recommend breaking it into 2-hour focused blocks.",
            'analyze': "Based on your task patterns, I notice you work best in the mornings. Consider scheduling complex tasks before 11 AM.",
            'suggest': "For productivity improvement, try the Pomodoro technique: 25 minutes focused work, 5 minute breaks.",
            'career': "For AI Integration Specialist development, focus on: API integrations, database design, and system architecture.",
            'time': "Time estimation tip: For coding tasks, multiply your initial estimate by 1.5 to account for debugging and testing.",
            'priority': "Use the Urgency vs Importance matrix: High urgency + High importance = Do first."
        }
        
        prompt_lower = prompt.lower()
        for key, response in fallback_responses.items():
            if key in prompt_lower:
                return response
        
        return "I'm here to help with task management, scheduling, and productivity optimization. What specific challenge are you facing?"
    
    def analyze_task(self, task_title, task_description=""):
        """AI analysis of a task"""
        prompt = f"Analyze this task for time estimation and priority: '{task_title}' - {task_description}"
        return self.call_claude_api(prompt, "task analysis")
    
    def suggest_schedule_optimization(self, tasks):
        """AI suggestions for schedule optimization"""
        task_summary = "\n".join([f"- {task[1]} (Priority: {task[4] + task[5]})" for task in tasks[:5]])
        prompt = f"Given these tasks, suggest an optimal schedule:\n{task_summary}"
        return self.call_claude_api(prompt, "schedule optimization")
    
    def provide_daily_briefing(self):
        """Generate daily productivity briefing"""
        patterns = self.db.analyze_productivity_patterns()
        pending_tasks = len(self.db.get_tasks('pending'))
        
        prompt = f"Provide a daily briefing for someone with {pending_tasks} pending tasks. Focus on productivity optimization and AI Integration Specialist career development."
        return self.call_claude_api(prompt, "daily briefing")
    
    def natural_language_scheduling(self, user_input):
        """Process natural language scheduling requests"""
        prompt = f"Parse this scheduling request and suggest specific actions: '{user_input}'"
        return self.call_claude_api(prompt, "natural language scheduling")

class MasterJarvis:
    """Main Master Jarvis system combining all features"""
    
    def __init__(self):
        self.db = MasterJarvisDatabase()
        self.ai = MasterJarvisAI(self.db)
        self.visual = VisualEffects()
        
    def show_startup_animation(self):
        """Beautiful startup sequence"""
        self.visual.print_header("🤖 MASTER JARVIS AI ASSISTANT 🤖")
        
        if VISUAL_AVAILABLE:
            self.visual.show_loading_animation("Initializing AI systems", 2)
            self.visual.show_loading_animation("Loading your data", 1.5)
            self.visual.show_loading_animation("Preparing personalized insights", 1)
            
        self.visual.print_animated_text("✨ Welcome! Your unified AI assistant is ready.", color='green')
        print()
    
    def show_main_menu(self):
        """Display streamlined main menu"""
        self.visual.print_header("MASTER JARVIS - UNIFIED CONTROL CENTER")
        
        print(f"{Fore.CYAN if VISUAL_AVAILABLE else ''}📋 TASK MANAGEMENT{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        self.visual.print_menu_option("1", "🎯 Smart Task Manager (Add/Schedule/Recurring)")
        self.visual.print_menu_option("2", "📊 Smart Task Dashboard") 
        self.visual.print_menu_option("3", "✅ Complete Task")
        self.visual.print_menu_option("4", "🗑️  Delete Tasks (Single/Multiple)")
        self.visual.print_menu_option("5", "🧹 Clean Up Recurring Tasks")
        
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}🤖 AI INTELLIGENCE{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        self.visual.print_menu_option("6", "💬 Enhanced AI Conversation")
        self.visual.print_menu_option("7", "📈 AI Productivity Analysis")
        self.visual.print_menu_option("8", "☀️  Daily AI Briefing")
        
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}📅 SCHEDULE MANAGEMENT{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        self.visual.print_menu_option("9", "📋 Create Daily Schedule")
        self.visual.print_menu_option("10", "💾 Save/Load Schedules")
        self.visual.print_menu_option("11", "📤 Export Calendar")
        self.visual.print_menu_option("12", "📅 Schedule Task for Specific Day")
        
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}🗓️ WEEKLY PLANNING{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        self.visual.print_menu_option("13", "🗓️ Smart Weekly Planner")
        self.visual.print_menu_option("14", "📊 Weekly Dashboard") 
        self.visual.print_menu_option("15", "📤 Export Weekly Calendar")
        
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}🔧 SYSTEM{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        self.visual.print_menu_option("16", "📊 System Analytics")
        self.visual.print_menu_option("17", "⚙️  Preferences")
        self.visual.print_menu_option("0", "🚪 Exit")
        
        print(f"\n{Fore.YELLOW if VISUAL_AVAILABLE else ''}✨ Streamlined AI learning - focused on your top 3 categories!{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
    
    def add_intelligent_task(self):
        """Add task with AI analysis"""
        self.visual.print_header("➕ ADD INTELLIGENT TASK")
        
        title = input("📝 Task title: ").strip()
        if not title:
            print("❌ Task title cannot be empty!")
            return
        
        description = input("📋 Task description (optional): ").strip()
        
        # AI analysis
        self.visual.print_ai_response("Analyzing your task...", thinking=True)
        ai_analysis = self.ai.analyze_task(title, description)
        
        self.visual.print_ai_response(ai_analysis)
        
        # Get priority scores
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}🎯 Priority Assessment (1-10 scale):{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        print("=" * 50)
        
        try:
            print("⚡ Urgency (how soon needed):")
            print("   Scale: 1=Low urgency, 10=Extremely urgent")
            urgency_input = input("   Enter urgency (1-10): ").strip()
            urgency = int(urgency_input) if urgency_input else 5
            urgency = max(1, min(10, urgency))  # Ensure 1-10 range
            
            print(f"\n🎯 Importance (impact if not completed):")
            print("   Scale: 1=Low impact, 10=Critical impact")
            importance_input = input("   Enter importance (1-10): ").strip()
            importance = int(importance_input) if importance_input else 5
            importance = max(1, min(10, importance))  # Ensure 1-10 range
            
            print(f"\n⏱️  Time Estimation:")
            estimated_time_input = input("   Estimated hours (or press Enter to skip): ").strip()
            estimated_time = float(estimated_time_input) if estimated_time_input else None
            
        except ValueError:
            print("⚠️ Invalid input detected, using default values...")
            urgency, importance, estimated_time = 5, 5, None
        
        print(f"\n✅ Priority scores set: Urgency={urgency}/10, Importance={importance}/10")
        
        print(f"\n📂 Task Category:")
        category = input("   Enter category (work/personal/learning/admin): ").strip() or "general"
        
        # Add deadline input
        due_date_input = input("📅 Deadline (YYYY-MM-DD) or 'none': ").strip()
        due_date = None
        if due_date_input.lower() not in ['none', 'n', '']:
            try:
                due_date = datetime.strptime(due_date_input, "%Y-%m-%d").strftime("%Y-%m-%d")
                print(f"✅ Deadline set for: {due_date}")
            except ValueError:
                print("⚠️ Invalid date format, no deadline set")
        
        # Add to database
        task_id = self.db.add_task(
            title=title,
            description=description,
            urgency=urgency,
            importance=importance,
            estimated_time=estimated_time,
            category=category,
            due_date=due_date
        )
        
        priority_total = urgency + importance
        priority_level = "🔥 HIGH" if priority_total >= 16 else "🟡 MEDIUM" if priority_total >= 12 else "🟢 LOW"
        
        print(f"\n✅ Task added successfully!")
        print(f"🆔 Task ID: {task_id}")
        print(f"🎯 Priority: {priority_level} ({priority_total}/20)")
        
        input("\n📱 Press Enter to continue...")
    
    def smart_task_manager(self):
        """Unified task creation: regular tasks, recurring tasks, and natural language scheduling"""
        self.visual.print_header("🎯 SMART TASK MANAGER")
        
        print("🚀 Welcome to your unified task creation center!")
        print("Choose how you'd like to create tasks:")
        
        self.visual.print_menu_option("1", "📝 Natural Language - Just describe what you need")
        self.visual.print_menu_option("2", "📋 Structured Entry - Fill in detailed fields") 
        self.visual.print_menu_option("3", "🔄 Recurring Task - Repeating schedule")
        self.visual.print_menu_option("4", "⚡ Quick Add - Title and category only")
        
        method = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Select method (1-4): {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
        
        if method == '1':
            self._natural_language_task_creation()
        elif method == '2':
            self._structured_task_creation()
        elif method == '3':
            self._recurring_task_creation()
        elif method == '4':
            self._quick_task_creation()
        else:
            print("❌ Invalid choice!")
            input("\n📱 Press Enter to continue...")
    
    def _natural_language_task_creation(self):
        """Natural language task creation with AI parsing"""
        self.visual.print_header("📝 NATURAL LANGUAGE TASK CREATION")
        
        print("🗣️ Describe what you need to do in natural language:")
        print("💡 Examples:")
        print("   • 'Schedule team meeting for Friday at 2 PM about Q4 planning'")
        print("   • 'Complete budget review by next Tuesday - high priority'")
        print("   • 'Set up daily standup meetings for the next month'")
        
        while True:
            user_input = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}What do you need to do? {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
            
            if not user_input:
                print("❌ Please describe your task")
                continue
                
            # AI analysis of natural language input
            self.visual.print_ai_response("🤖 Analyzing your request...", thinking=True)
            
            ai_prompt = f"""
            Parse this task request and extract structured information:
            "{user_input}"
            
            Provide a JSON response with:
            - title: clear task title
            - description: detailed description
            - category: admin, meetings, or personal
            - urgency: 1-10 scale
            - importance: 1-10 scale  
            - estimated_time: hours (number)
            - due_date: YYYY-MM-DD format if mentioned
            - due_time: HH:MM format if mentioned
            - is_recurring: true/false
            - recurrence_pattern: daily/weekly/monthly if recurring
            """
            
            ai_response = self.ai.call_claude_api(ai_prompt, "natural language task parsing")
            
            # Try to parse AI response as JSON
            try:
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    
                    print(f"\n✅ I understood:")
                    print(f"📝 Task: {parsed_data.get('title', 'Untitled')}")
                    print(f"📂 Category: {parsed_data.get('category', 'admin')}")
                    print(f"🎯 Priority: {parsed_data.get('urgency', 5)}/10 urgency, {parsed_data.get('importance', 5)}/10 importance")
                    if parsed_data.get('due_date'):
                        print(f"📅 Due: {parsed_data.get('due_date')}" + (f" at {parsed_data.get('due_time')}" if parsed_data.get('due_time') else ""))
                    if parsed_data.get('estimated_time'):
                        print(f"⏱️ Estimated: {parsed_data.get('estimated_time')} hours")
                    
                    confirm = input(f"\n✅ Create this task? (y/n): ").strip().lower()
                    if confirm == 'y':
                        self._create_task_from_parsed_data(parsed_data)
                        
                else:
                    # Fallback to manual entry if AI parsing fails
                    print("🤖 I'll help you create this task step by step.")
                    self._create_task_manually(user_input)
                    
            except (json.JSONDecodeError, KeyError):
                # Fallback to manual entry
                print("🤖 Let me help you create this task:")
                self._create_task_manually(user_input)
            
            # Ask if they want to add another
            another = input("\n📝 Add another task? (y/n): ").strip().lower()
            if another != 'y':
                break
    
    def _create_task_from_parsed_data(self, data):
        """Create task from AI-parsed data"""
        task_id = self.db.add_task(
            title=data.get('title', 'Untitled Task'),
            description=data.get('description', ''),
            urgency=min(10, max(1, data.get('urgency', 5))),
            importance=min(10, max(1, data.get('importance', 5))),
            estimated_time=data.get('estimated_time'),
            category=data.get('category', 'admin'),
            due_date=data.get('due_date')
        )
        
        # Add time if specified
        if data.get('due_time'):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE tasks SET due_time = ? WHERE id = ?', (data.get('due_time'), task_id))
            conn.commit()
            conn.close()
        
        print(f"✅ Task created! ID: {task_id}")
    
    def _create_task_manually(self, user_input):
        """Manual task creation fallback"""
        title = input(f"📝 Task title: ").strip() or user_input[:50]
        
        print(f"\n📂 Category:")
        self.visual.print_menu_option("1", "📋 Admin")
        self.visual.print_menu_option("2", "👥 Meetings") 
        self.visual.print_menu_option("3", "🏠 Personal")
        
        cat_choice = input("Select category (1-3): ").strip()
        categories = {'1': 'admin', '2': 'meetings', '3': 'personal'}
        category = categories.get(cat_choice, 'admin')
        
        urgency = int(input("⚡ Urgency (1-10): ") or "5")
        importance = int(input("🎯 Importance (1-10): ") or "5")
        
        task_id = self.db.add_task(
            title=title,
            description=user_input,
            urgency=urgency,
            importance=importance,
            category=category
        )
        
        print(f"✅ Task created manually! ID: {task_id}")
    
    def _structured_task_creation(self):
        """Structured task entry with all fields"""
        self.visual.print_header("📋 STRUCTURED TASK CREATION")
        
        while True:
            title = input("📝 Task title: ").strip()
            if not title:
                print("❌ Task title cannot be empty!")
                continue
            
            description = input("📋 Task description (optional): ").strip()
            
            # AI analysis
            self.visual.print_ai_response("Analyzing your task...", thinking=True)
            ai_analysis = self.ai.analyze_task(title, description)
            self.visual.print_ai_response(ai_analysis)
            
            # Streamlined category selection
            print(f"\n📂 Task Category:")
            self.visual.print_menu_option("1", "📋 Admin")
            self.visual.print_menu_option("2", "👥 Meetings") 
            self.visual.print_menu_option("3", "🏠 Personal")
            
            cat_choice = input("Select category (1-3): ").strip()
            categories = {'1': 'admin', '2': 'meetings', '3': 'personal'}
            category = categories.get(cat_choice, 'admin')
            
            # Priority assessment
            print(f"\n🎯 Priority Assessment (1-10 scale):")
            try:
                urgency = int(input("⚡ Urgency (1-10): ") or "5")
                importance = int(input("🎯 Importance (1-10): ") or "5") 
                estimated_time = float(input("⏱️ Estimated hours: ") or "0") or None
            except ValueError:
                urgency, importance, estimated_time = 5, 5, None
            
            # Deadline and time
            due_date, due_time = self._get_deadline_and_time(category)
            
            # Create task
            task_id = self.db.add_task(
                title=title,
                description=description,
                urgency=urgency,
                importance=importance,
                estimated_time=estimated_time,
                category=category,
                due_date=due_date
            )
            
            # Add time if specified
            if due_time:
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute('UPDATE tasks SET due_time = ? WHERE id = ?', (due_time, task_id))
                conn.commit()
                conn.close()
            
            priority_total = urgency + importance
            priority_level = "🔥 HIGH" if priority_total >= 16 else "🟡 MEDIUM" if priority_total >= 12 else "🟢 LOW"
            
            print(f"\n✅ Task created successfully!")
            print(f"🆔 Task ID: {task_id}")
            print(f"🎯 Priority: {priority_level} ({priority_total}/20)")
            if due_date:
                print(f"📅 Due: {due_date}" + (f" at {due_time}" if due_time else ""))
            
            another = input("\n📝 Add another task? (y/n): ").strip().lower()
            if another != 'y':
                break
    
    def _get_deadline_and_time(self, category):
        """Get deadline and time, with special handling for meetings"""
        due_date_input = input("📅 Deadline (YYYY-MM-DD) or 'none': ").strip()
        due_date = None
        due_time = None
        
        if due_date_input.lower() not in ['none', 'n', '']:
            try:
                due_date = datetime.strptime(due_date_input, "%Y-%m-%d").strftime("%Y-%m-%d")
                
                # For meetings, always ask for time
                if category == 'meetings':
                    due_time = input("🕒 Meeting time (HH:MM, e.g., 14:30): ").strip()
                    if due_time and ':' not in due_time:
                        due_time = None  # Invalid format
                else:
                    # For other categories, time is optional
                    due_time = input("🕒 Specific time (optional, HH:MM): ").strip() or None
                    
            except ValueError:
                print("⚠️ Invalid date format, no deadline set")
        
        return due_date, due_time
    
    def delete_tasks(self):
        """Delete single or multiple tasks"""
        self.visual.print_header("🗑️ DELETE TASKS")
        
        pending_tasks = self.db.get_tasks('pending', limit=20)
        
        if not pending_tasks:
            print("📋 No pending tasks to delete!")
            input("\n📱 Press Enter to continue...")
            return
        
        print("🗑️ Delete Options:")
        self.visual.print_menu_option("1", "🗑️ Delete single task")
        self.visual.print_menu_option("2", "🔥 Delete multiple tasks")
        self.visual.print_menu_option("3", "💥 Delete all completed tasks")
        
        method = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Select method (1-3): {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
        
        if method == '1':
            self._delete_single_task(pending_tasks)
        elif method == '2':
            self._delete_multiple_tasks(pending_tasks)
        elif method == '3':
            self._delete_completed_tasks()
        else:
            print("❌ Invalid choice!")
        
        input("\n📱 Press Enter to continue...")
    
    def _delete_single_task(self, tasks):
        """Delete single task"""
        print("📋 Your pending tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task[1]} (ID: {task[0]})")
        
        try:
            choice = int(input("\n🔢 Enter task number to delete: ")) - 1
            if 0 <= choice < len(tasks):
                task = tasks[choice]
                task_id, title = task[0], task[1]
                
                confirm = input(f"⚠️ Really delete '{title}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    conn = sqlite3.connect(self.db.db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                    conn.commit()
                    conn.close()
                    print("✅ Task deleted successfully!")
            else:
                print("❌ Invalid task number!")
        except ValueError:
            print("❌ Please enter a valid number!")
    
    def _delete_multiple_tasks(self, tasks):
        """Delete multiple tasks at once"""
        print("📋 Your pending tasks:")
        for i, task in enumerate(tasks, 1):
            priority_total = (task[3] or 5) + (task[4] or 5)  # urgency + importance
            priority_icon = "🔥" if priority_total >= 16 else "🟡" if priority_total >= 12 else "🟢"
            print(f"  {i}. {priority_icon} {task[1]} (ID: {task[0]})")
        
        print(f"\n💡 Enter task numbers to delete:")
        print(f"Examples: '1,3,5' or '1-5' or '1,3,7-10'")
        
        selection = input("📝 Task numbers to delete: ").strip()
        
        if not selection:
            print("❌ No tasks selected!")
            return
        
        # Parse selection
        task_indices = self._parse_task_selection(selection, len(tasks))
        
        if not task_indices:
            print("❌ Invalid selection format!")
            return
        
        # Show selected tasks
        selected_tasks = [tasks[i-1] for i in task_indices if 1 <= i <= len(tasks)]
        
        print(f"\n⚠️ You selected {len(selected_tasks)} tasks for deletion:")
        for task in selected_tasks:
            print(f"  • {task[1]} (ID: {task[0]})")
        
        confirm = input(f"\n⚠️ Delete all {len(selected_tasks)} selected tasks? (y/n): ").strip().lower()
        
        if confirm == 'y':
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            task_ids = [task[0] for task in selected_tasks]
            placeholders = ','.join(['?' for _ in task_ids])
            cursor.execute(f"DELETE FROM tasks WHERE id IN ({placeholders})", task_ids)
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"✅ Successfully deleted {deleted_count} tasks!")
        else:
            print("❌ Deletion cancelled.")
    
    def _parse_task_selection(self, selection, max_tasks):
        """Parse user selection like '1,3,5' or '1-5' or '1,3,7-10'"""
        indices = set()
        
        try:
            parts = selection.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Range like '1-5'
                    start, end = map(int, part.split('-'))
                    indices.update(range(start, end + 1))
                else:
                    # Single number like '3'
                    indices.add(int(part))
            
            # Filter valid indices
            return [i for i in indices if 1 <= i <= max_tasks]
            
        except ValueError:
            return []
    
    def _delete_completed_tasks(self):
        """Delete all completed tasks"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
        completed_count = cursor.fetchone()[0]
        
        if completed_count == 0:
            print("📋 No completed tasks to delete!")
            conn.close()
            return
        
        confirm = input(f"⚠️ Delete all {completed_count} completed tasks? (y/n): ").strip().lower()
        
        if confirm == 'y':
            cursor.execute("DELETE FROM tasks WHERE status = 'completed'")
            deleted_count = cursor.rowcount
            conn.commit()
            print(f"✅ Deleted {deleted_count} completed tasks!")
        else:
            print("❌ Deletion cancelled.")
        
        conn.close()
    
    def cleanup_recurring_tasks(self):
        """Clean up excessive recurring task instances"""
        self.visual.print_header("🧹 CLEAN UP RECURRING TASKS")
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Find recurring task patterns
        cursor.execute('''
            SELECT title, COUNT(*) as count
            FROM tasks 
            WHERE status = 'pending'
            AND title NOT LIKE '[RECURRING]%'
            GROUP BY title
            HAVING count > 5
            ORDER BY count DESC
        ''')
        
        recurring_patterns = cursor.fetchall()
        
        if not recurring_patterns:
            print("✅ No excessive recurring tasks found!")
            input("\n📱 Press Enter to continue...")
            return
        
        print("🔍 Found these excessive recurring tasks:")
        for i, (title, count) in enumerate(recurring_patterns, 1):
            print(f"  {i}. '{title}' - {count} instances")
        
        print(f"\n⚠️ Options:")
        self.visual.print_menu_option("1", "Delete ALL excessive recurring instances")
        self.visual.print_menu_option("2", "Keep only next 7 days worth")
        self.visual.print_menu_option("3", "Keep only next 3 occurrences")
        self.visual.print_menu_option("4", "Manual cleanup by task type")
        
        choice = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Select cleanup option (1-4): {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
        
        if choice == '1':
            # Delete all recurring instances, keep only parent tasks
            cursor.execute('''
                DELETE FROM tasks 
                WHERE status = 'pending' 
                AND title NOT LIKE '[RECURRING]%'
                AND title IN (
                    SELECT title FROM tasks 
                    WHERE status = 'pending' 
                    GROUP BY title 
                    HAVING COUNT(*) > 5
                )
            ''')
            
            deleted = cursor.rowcount
            print(f"🗑️ Deleted {deleted} excessive recurring task instances")
            
        elif choice == '2':
            # Keep only next 7 days worth
            today = datetime.now().date()
            week_from_now = today + timedelta(days=7)
            
            for title, count in recurring_patterns:
                cursor.execute('''
                    DELETE FROM tasks 
                    WHERE status = 'pending' 
                    AND title = ?
                    AND (due_date IS NULL OR due_date > ?)
                ''', (title, week_from_now.strftime("%Y-%m-%d")))
            
            deleted = cursor.rowcount
            print(f"🗑️ Kept only next 7 days worth, deleted {deleted} future instances")
            
        elif choice == '3':
            # Keep only next 3 occurrences
            for title, count in recurring_patterns:
                cursor.execute('''
                    DELETE FROM tasks 
                    WHERE id NOT IN (
                        SELECT id FROM tasks 
                        WHERE status = 'pending' 
                        AND title = ?
                        ORDER BY due_date ASC, created_at ASC
                        LIMIT 3
                    )
                    AND status = 'pending'
                    AND title = ?
                ''', (title, title))
            
            deleted = cursor.rowcount
            print(f"🗑️ Kept only next 3 occurrences per task, deleted {deleted} instances")
            
        elif choice == '4':
            # Manual cleanup
            for i, (title, count) in enumerate(recurring_patterns, 1):
                keep = input(f"How many instances of '{title}' to keep? (current: {count}): ").strip()
                try:
                    keep_count = int(keep)
                    if keep_count < count:
                        cursor.execute('''
                            DELETE FROM tasks 
                            WHERE id NOT IN (
                                SELECT id FROM tasks 
                                WHERE status = 'pending' 
                                AND title = ?
                                ORDER BY due_date ASC, created_at ASC
                                LIMIT ?
                            )
                            AND status = 'pending'
                            AND title = ?
                        ''', (title, keep_count, title))
                        
                        print(f"🗑️ Kept {keep_count} instances of '{title}'")
                except ValueError:
                    print(f"⚠️ Skipped '{title}' - invalid number")
        
        else:
            print("❌ Invalid choice!")
            conn.close()
            input("\n📱 Press Enter to continue...")
            return
        
        conn.commit()
        
        # Show final count
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
        final_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Cleanup complete!")
        print(f"📊 You now have {final_count} pending tasks")
        print(f"💡 Use Option 2 (Smart Task Dashboard) to verify the cleanup")
        
        input("\n📱 Press Enter to continue...")
    
    def add_recurring_task(self):
        """Add recurring task with intelligent scheduling"""
        self.visual.print_header("🔄 ADD RECURRING TASK")
        
        title = input("📝 Task title: ").strip()
        if not title:
            print("❌ Task title cannot be empty!")
            return
        
        description = input("📋 Task description (optional): ").strip()
        
        # AI analysis for recurring task
        self.visual.print_ai_response("Analyzing your recurring task pattern...", thinking=True)
        ai_analysis = self.ai.analyze_task(f"Recurring: {title}", description)
        self.visual.print_ai_response(ai_analysis)
        
        # Get recurrence pattern
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}🔄 Recurrence Pattern:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        print("=" * 50)
        self.visual.print_menu_option("1", "Daily (every day)")
        self.visual.print_menu_option("2", "Weekly (same day each week)")
        self.visual.print_menu_option("3", "Bi-weekly (every 2 weeks)")
        self.visual.print_menu_option("4", "Monthly (same date each month)")
        
        pattern_choice = input("\nSelect recurrence pattern (1-4): ").strip()
        
        patterns = {
            '1': 'daily',
            '2': 'weekly', 
            '3': 'biweekly',
            '4': 'monthly'
        }
        
        pattern = patterns.get(pattern_choice, 'weekly')
        
        # Get end date or number of occurrences
        print(f"\n🗓️ Recurrence Duration:")
        duration_type = input("Enter number of occurrences (e.g., '10') or end date (YYYY-MM-DD): ").strip()
        
        end_date = None
        max_occurrences = 10  # Default
        
        try:
            # Try to parse as number of occurrences
            max_occurrences = int(duration_type)
        except ValueError:
            # Try to parse as date
            try:
                end_date = datetime.strptime(duration_type, "%Y-%m-%d").strftime("%Y-%m-%d")
                max_occurrences = None
            except ValueError:
                print("⚠️ Invalid input, defaulting to 10 occurrences")
                max_occurrences = 10
        
        # Get other task details
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}📊 Task Details:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        print("=" * 50)
        
        try:
            print("⚡ Urgency (how soon needed):")
            urgency_input = input("   Enter urgency (1-10): ").strip()
            urgency = int(urgency_input) if urgency_input else 5
            urgency = max(1, min(10, urgency))
            
            print("🎯 Importance (impact if not completed):")
            importance_input = input("   Enter importance (1-10): ").strip()
            importance = int(importance_input) if importance_input else 5
            importance = max(1, min(10, importance))
            
            print("⏱️ Time Estimation:")
            estimated_time_input = input("   Estimated hours per occurrence: ").strip()
            estimated_time = float(estimated_time_input) if estimated_time_input else 1.0
            
        except ValueError:
            urgency, importance, estimated_time = 5, 5, 1.0
        
        print(f"\n📂 Task Category:")
        category = input("   Enter category (admin/meetings/learning/personal): ").strip() or "admin"
        if category not in ['admin', 'meetings', 'learning', 'personal']:
            category = 'admin'
        
        # Create the parent recurring task
        parent_task_id = self.db.add_task(
            title=f"[RECURRING] {title}",
            description=f"Recurring {pattern}: {description}",
            urgency=urgency,
            importance=importance,
            estimated_time=estimated_time,
            category=category,
            due_date=end_date
        )
        
        # Generate recurring task instances
        instances_created = self._generate_recurring_instances(
            parent_task_id, title, description, urgency, importance, 
            estimated_time, category, pattern, end_date, max_occurrences
        )
        
        priority_total = urgency + importance
        priority_level = "🔥 HIGH" if priority_total >= 16 else "🟡 MEDIUM" if priority_total >= 12 else "🟢 LOW"
        
        print(f"\n✅ Recurring task created successfully!")
        print(f"🆔 Parent Task ID: {parent_task_id}")
        print(f"🔄 Pattern: {pattern.title()}")
        print(f"📅 Generated {instances_created} task instances")
        print(f"🎯 Priority: {priority_level} ({priority_total}/20)")
        
        input("\n📱 Press Enter to continue...")
    
    def _generate_recurring_instances(self, parent_id, title, description, urgency, importance, 
                                    estimated_time, category, pattern, end_date, max_occurrences):
        """Generate individual task instances for recurring tasks"""
        
        instances = []
        start_date = datetime.now().date()
        current_date = start_date
        count = 0
        
        # Generate instances based on pattern
        while count < (max_occurrences or 50):  # Cap at 50 if no end date
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                if current_date > end_dt:
                    break
            
            # Skip weekends for certain patterns (optional logic)
            if pattern == 'daily' and current_date.weekday() >= 5:  # Skip weekends for daily tasks
                current_date += timedelta(days=1)
                continue
            
            # Create task instance
            task_id = self.db.add_task(
                title=title,
                description=description,
                urgency=urgency,
                importance=importance,
                estimated_time=estimated_time,
                category=category,
                due_date=current_date.strftime("%Y-%m-%d")
            )
            
            # Update task to mark as recurring instance
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks 
                SET is_recurring = 1, 
                    recurrence_pattern = ?,
                    parent_task_id = ?
                WHERE id = ?
            ''', (pattern, parent_id, task_id))
            conn.commit()
            conn.close()
            
            instances.append(task_id)
            count += 1
            
            # Calculate next occurrence
            if pattern == 'daily':
                current_date += timedelta(days=1)
            elif pattern == 'weekly':
                current_date += timedelta(weeks=1)
            elif pattern == 'biweekly':
                current_date += timedelta(weeks=2)
            elif pattern == 'monthly':
                # Add one month (approximate)
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        return len(instances)
    
    def schedule_task_specific_day(self):
        """Schedule existing tasks for specific days of the week"""
        self.visual.print_header("📅 SCHEDULE TASK FOR SPECIFIC DAY")
        
        # Get pending tasks
        tasks = self.db.get_tasks('pending', limit=20)
        
        if not tasks:
            print("📋 No pending tasks to schedule!")
            print("💡 Add tasks first using Option 1.")
            input("\n📱 Press Enter to continue...")
            return
        
        print("📋 Your pending tasks:")
        for i, task in enumerate(tasks, 1):
            task_id, title, description, urgency, importance, est_time, actual_time, category, status, created_at, completed_at, due_date, energy_level, context, tags, priority_total = task
            
            priority_level = "🔥" if priority_total >= 16 else "🟡" if priority_total >= 12 else "🟢"
            time_str = f"⏱️ {est_time}h" if est_time else "⏱️ No estimate"
            
            print(f"  {i}. {priority_level} {title}")
            print(f"      🆔 ID: {task_id} | {time_str} | 📂 {category}")
        
        # Select task to schedule
        try:
            task_choice = int(input(f"\n🔢 Select task number to schedule: ")) - 1
            if not (0 <= task_choice < len(tasks)):
                print("❌ Invalid task number!")
                input("\n📱 Press Enter to continue...")
                return
            
            selected_task = tasks[task_choice]
            task_id, title = selected_task[0], selected_task[1]
            
            print(f"\n✅ Selected: {title}")
            
            # Select specific day
            print(f"\n📅 Select specific day:")
            self.visual.print_menu_option("1", "Monday")
            self.visual.print_menu_option("2", "Tuesday") 
            self.visual.print_menu_option("3", "Wednesday")
            self.visual.print_menu_option("4", "Thursday")
            self.visual.print_menu_option("5", "Friday")
            self.visual.print_menu_option("6", "Saturday")
            self.visual.print_menu_option("7", "Sunday")
            
            day_choice = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Select day (1-7): {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
            
            days = {
                '1': 'Monday',
                '2': 'Tuesday', 
                '3': 'Wednesday',
                '4': 'Thursday',
                '5': 'Friday',
                '6': 'Saturday',
                '7': 'Sunday'
            }
            
            if day_choice not in days:
                print("❌ Invalid day selection!")
                input("\n📱 Press Enter to continue...")
                return
            
            selected_day = days[day_choice]
            
            # Select specific date or next occurrence
            print(f"\n🗓️ Schedule for {selected_day}:")
            self.visual.print_menu_option("1", f"Next {selected_day}")
            self.visual.print_menu_option("2", f"Specific date")
            
            date_choice = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Choose option (1-2): {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
            
            target_date = None
            
            if date_choice == '1':
                # Find next occurrence of selected day
                today = datetime.now()
                days_ahead = list(days.keys()).index(day_choice) - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                target_date = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                
            elif date_choice == '2':
                # Get specific date
                date_input = input("📅 Enter specific date (YYYY-MM-DD): ").strip()
                try:
                    datetime.strptime(date_input, "%Y-%m-%d")
                    target_date = date_input
                except ValueError:
                    print("❌ Invalid date format!")
                    input("\n📱 Press Enter to continue...")
                    return
            else:
                print("❌ Invalid choice!")
                input("\n📱 Press Enter to continue...")
                return
            
            # Get time slot (optional)
            time_slot = input("🕒 Preferred time (e.g., '9:00 AM' or press Enter to skip): ").strip()
            
            # Update task with scheduled date
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks 
                SET due_date = ?, 
                    context = COALESCE(context, '') || ? 
                WHERE id = ?
            ''', (target_date, f" | Scheduled: {selected_day} {target_date}" + (f" at {time_slot}" if time_slot else ""), task_id))
            conn.commit()
            conn.close()
            
            # AI scheduling advice
            self.visual.print_ai_response("Analyzing optimal scheduling for this task...", thinking=True)
            schedule_prompt = f"I scheduled '{title}' for {selected_day}, {target_date}" + (f" at {time_slot}" if time_slot else "") + ". Any scheduling optimization advice?"
            ai_advice = self.ai.call_claude_api(schedule_prompt, "specific day scheduling")
            self.visual.print_ai_response(ai_advice)
            
            print(f"\n✅ Task scheduled successfully!")
            print(f"📅 {title}")
            print(f"🗓️ Scheduled for: {selected_day}, {target_date}")
            if time_slot:
                print(f"🕒 Time: {time_slot}")
            
        except ValueError:
            print("❌ Please enter a valid number!")
        except Exception as e:
            print(f"❌ Error scheduling task: {str(e)}")
        
        input("\n📱 Press Enter to continue...")
    
    def _calculate_days_until_due(self, due_date, start_date):
        """Calculate days between start_date and due_date"""
        if not due_date:
            return None
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d")
            start = datetime.strptime(start_date, "%Y-%m-%d")
            return (due - start).days
        except (ValueError, TypeError):
            return None
    
    def show_smart_dashboard(self):
        """Display intelligent task dashboard"""
        self.visual.print_header("📊 SMART TASK DASHBOARD")
        
        tasks = self.db.get_tasks('pending', limit=10)
        
        if not tasks:
            print("🎉 No pending tasks! You're all caught up!")
            input("\n📱 Press Enter to continue...")
            return
        
        print(f"📋 Showing {len(tasks)} pending tasks (sorted by priority):\n")
        
        for i, task in enumerate(tasks, 1):
            task_id, title, description, urgency, importance, est_time, actual_time, category, status, created_at, completed_at, due_date, energy_level, context, tags, priority_total = task
            
            priority_level = "🔥" if priority_total >= 16 else "🟡" if priority_total >= 12 else "🟢"
            time_str = f"⏱️ {est_time}h" if est_time else "⏱️ No estimate"
            
            # Add deadline information
            deadline_info = ""
            if due_date:
                try:
                    due = datetime.strptime(due_date, "%Y-%m-%d")
                    today = datetime.now()
                    days_diff = (due - today).days
                    
                    if days_diff < 0:
                        deadline_info = f" | 🚨 OVERDUE ({abs(days_diff)} days)"
                        deadline_color = Fore.RED if VISUAL_AVAILABLE else ""
                    elif days_diff == 0:
                        deadline_info = f" | ⏰ DUE TODAY"
                        deadline_color = Fore.RED if VISUAL_AVAILABLE else ""
                    elif days_diff <= 3:
                        deadline_info = f" | 📅 Due in {days_diff} days"
                        deadline_color = Fore.YELLOW if VISUAL_AVAILABLE else ""
                    elif days_diff <= 7:
                        deadline_info = f" | 📆 Due {due_date}"
                        deadline_color = Fore.CYAN if VISUAL_AVAILABLE else ""
                    else:
                        deadline_info = f" | 📅 Due {due_date}"
                        deadline_color = ""
                except ValueError:
                    deadline_info = f" | 📅 Due {due_date}"
                    deadline_color = ""
            else:
                deadline_color = ""
            
            if VISUAL_AVAILABLE:
                print(f"{Fore.YELLOW}{i:2d}.{Style.RESET_ALL} {priority_level} {deadline_color}{title}{Style.RESET_ALL}")
                print(f"    🆔 ID: {task_id} | {time_str} | 📂 {category} | 🎯 Priority: {priority_total}/20{deadline_info}")
            else:
                print(f"{i:2d}. {priority_level} {title}")
                print(f"    ID: {task_id} | {time_str} | Category: {category} | Priority: {priority_total}/20{deadline_info}")
            
            if description:
                print(f"    📝 {description}")
            print()
        
        # AI optimization suggestions
        self.visual.print_ai_response("Analyzing your task list for optimization opportunities...", thinking=True)
        ai_suggestions = self.ai.suggest_schedule_optimization(tasks)
        self.visual.print_ai_response(ai_suggestions)
        
        input("\n📱 Press Enter to continue...")
    
    def enhanced_ai_conversation(self):
        """Advanced AI conversation with memory"""
        self.visual.print_header("💬 ENHANCED AI CONVERSATION")
        
        print("🤖 Starting enhanced AI conversation with memory...")
        print("💡 Commands: 'quit', 'exit', 'my patterns', 'insights', 'help'")
        print("✨ I remember our previous conversations and learn from your productivity patterns!\n")
        
        while True:
            try:
                user_input = input(f"{Fore.GREEN if VISUAL_AVAILABLE else ''}You: {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q', 'back']:
                    print("👋 Ending conversation. All insights saved!")
                    break
                
                if user_input.lower() == 'help':
                    print("""
🤖 Enhanced AI Commands:
• 'my patterns' - Show your productivity patterns
• 'insights' - Get personalized productivity insights  
• 'analyze tasks' - AI analysis of your current tasks
• 'career advice' - AI Integration Specialist guidance
• 'schedule help' - Scheduling optimization suggestions
• 'quit' or 'exit' - End conversation
                    """)
                    continue
                
                if user_input.lower() == 'my patterns':
                    patterns = self.db.analyze_productivity_patterns()
                    if patterns['time_estimation']:
                        print("⏱️ Your Time Estimation Patterns:")
                        for est, actual, category in patterns['time_estimation'][-5:]:
                            accuracy = (min(est, actual) / max(est, actual)) * 100 if est and actual else 0
                            print(f"  📂 {category}: Estimated {est}h, Actual {actual}h ({accuracy:.0f}% accurate)")
                    else:
                        print("📊 Not enough completion data yet. Complete more tasks with time tracking!")
                    continue
                
                if user_input.lower() == 'insights':
                    self.visual.print_ai_response("Generating personalized insights...", thinking=True)
                    insights = self.ai.provide_daily_briefing()
                    self.visual.print_ai_response(insights)
                    continue
                
                if not user_input:
                    continue
                
                # Get AI response with conversation memory
                self.visual.print_ai_response("Processing...", thinking=True)
                ai_response = self.ai.call_claude_api(user_input, "enhanced conversation")
                self.visual.print_ai_response(ai_response)
                
            except KeyboardInterrupt:
                print("\n👋 Conversation ended.")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
    
    def natural_language_scheduling(self):
        """Natural language task scheduling"""
        self.visual.print_header("🎯 NATURAL LANGUAGE SCHEDULING")
        
        print("🗣️  Tell me what you want to schedule in natural language!")
        print("💡 Examples:")
        print("   • 'Schedule 2 hours of Python practice tomorrow morning'")
        print("   • 'Block time for presentation prep this afternoon'")
        print("   • 'What should I focus on for the next hour?'")
        print()
        
        while True:
            user_input = input(f"{Fore.GREEN if VISUAL_AVAILABLE else ''}Scheduling request: {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
            
            if user_input.lower() in ['quit', 'exit', 'back', 'q']:
                break
            
            if not user_input:
                continue
            
            # Process natural language request
            self.visual.print_ai_response("Understanding your scheduling request...", thinking=True)
            ai_response = self.ai.natural_language_scheduling(user_input)
            self.visual.print_ai_response(ai_response)
            
            # Ask if they want to create the task
            create_task = input("\n🤔 Would you like me to create this as a task? (y/n): ").strip().lower()
            
            if create_task == 'y':
                # Extract task details and create
                print("✅ Creating task based on your request...")
                # You could add more sophisticated parsing here
                task_id = self.db.add_task(title=user_input, category="scheduled")
                print(f"✅ Task created with ID: {task_id}")
            
            print("\n" + "="*50)
    
    def ai_productivity_analysis(self):
        """AI-powered productivity analysis"""
        self.visual.print_header("📈 AI PRODUCTIVITY ANALYSIS")
        
        self.visual.print_ai_response("Analyzing your productivity patterns...", thinking=True)
        
        patterns = self.db.analyze_productivity_patterns()
        tasks = self.db.get_tasks('pending')
        completed_tasks = self.db.get_tasks('completed')
        
        # Generate comprehensive analysis
        analysis_context = f"""
        Productivity Analysis Data:
        - Pending tasks: {len(tasks)}
        - Completed tasks: {len(completed_tasks)}  
        - Time estimation data points: {len(patterns['time_estimation'])}
        - Categories tracked: {len(patterns['completion_rates'])}
        """
        
        ai_analysis = self.ai.call_claude_api(
            "Provide a comprehensive productivity analysis with actionable insights and recommendations.",
            analysis_context
        )
        
        self.visual.print_ai_response(ai_analysis)
        
        # Show specific pattern data
        if patterns['completion_rates']:
            print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}📊 Task Completion by Category:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
            for category, completed, total in patterns['completion_rates']:
                completion_rate = (completed / total) * 100 if total > 0 else 0
                print(f"  📂 {category}: {completed}/{total} ({completion_rate:.1f}%)")
        
        input("\n📱 Press Enter to continue...")
    
    def daily_ai_briefing(self):
        """Generate daily AI briefing"""
        self.visual.print_header("☀️ DAILY AI BRIEFING")
        
        self.visual.print_ai_response("Preparing your personalized daily briefing...", thinking=True)
        
        briefing = self.ai.provide_daily_briefing()
        self.visual.print_ai_response(briefing)
        
        # Add specific daily stats
        pending_tasks = self.db.get_tasks('pending', limit=5)
        
        if pending_tasks:
            print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}🎯 Today's Top Priorities:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
            for i, task in enumerate(pending_tasks, 1):
                priority_total = task[4] + task[5]  # urgency + importance
                priority_icon = "🔥" if priority_total >= 16 else "🟡" if priority_total >= 12 else "🟢"
                print(f"  {i}. {priority_icon} {task[1]} (Priority: {priority_total}/20)")
        
        input("\n📱 Press Enter to continue...")
    
    def complete_task(self):
        """Complete a task with time tracking"""
        self.visual.print_header("✅ COMPLETE TASK")
        
        # Get ALL pending tasks, including recurring instances - simplified query
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, description, urgency_score, importance_score, 
                   estimated_time, actual_time, category, status, created_at,
                   completed_at, due_date, energy_level, context, tags
            FROM tasks 
            WHERE status = 'pending' 
            ORDER BY created_at ASC
        ''')
        pending_tasks = cursor.fetchall()
        conn.close()
        
        if not pending_tasks:
            print("🎉 No pending tasks to complete!")
            input("\n📱 Press Enter to continue...")
            return
        
        print(f"📋 Your pending tasks ({len(pending_tasks)} total):")
        for i, task in enumerate(pending_tasks, 1):
            task_id = task[0]
            title = task[1] 
            due_date = task[11]
            
            # Add deadline info
            deadline_info = ""
            if due_date:
                try:
                    due = datetime.strptime(due_date, "%Y-%m-%d")
                    today = datetime.now()
                    days_diff = (due - today).days
                    
                    if days_diff < 0:
                        deadline_info = f" 🚨 OVERDUE"
                    elif days_diff == 0:
                        deadline_info = f" ⏰ DUE TODAY"
                    elif days_diff <= 3:
                        deadline_info = f" 📅 Due in {days_diff} days"
                except ValueError:
                    deadline_info = f" 📅 Due {due_date}"
            
            print(f"  {i}. {title} (ID: {task_id}){deadline_info}")
        
        try:
            choice = int(input("\n🔢 Enter task number to complete: ")) - 1
            if 0 <= choice < len(pending_tasks):
                task = pending_tasks[choice]
                task_id = task[0]
                title = task[1]
                estimated_time = task[5]
                
                print(f"\n✅ Completing: {title}")
                
                if estimated_time:
                    actual_time_input = input(f"⏱️  Actual time spent? (estimated: {estimated_time}h): ").strip()
                    try:
                        actual_time = float(actual_time_input) if actual_time_input else None
                    except ValueError:
                        actual_time = None
                else:
                    actual_time_input = input("⏱️  How long did this take? (hours): ").strip()
                    try:
                        actual_time = float(actual_time_input) if actual_time_input else None
                    except ValueError:
                        actual_time = None
                
                self.db.complete_task(task_id, actual_time)
                
                print(f"🎉 Task completed successfully!")
                
                # AI learning from completion
                if estimated_time and actual_time:
                    difference = abs(estimated_time - actual_time)
                    if difference > 0.5:  # If off by more than 30 minutes
                        learning_prompt = f"I estimated {estimated_time}h for '{title}' but it took {actual_time}h. What can I learn for better estimates?"
                        self.visual.print_ai_response("Learning from this completion...", thinking=True)
                        ai_learning = self.ai.call_claude_api(learning_prompt, "task completion learning")
                        self.visual.print_ai_response(ai_learning)
                
            else:
                print("❌ Invalid task number!")
        except ValueError:
            print("❌ Please enter a valid number!")
        
        input("\n📱 Press Enter to continue...")
    
    def run(self):
        """Main application loop"""
        try:
            self.show_startup_animation()
            
            while True:
                try:
                    self.show_main_menu()
                    
                    choice = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Enter your choice: {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
                    
                    if choice == '0':
                        self.visual.print_animated_text("👋 Thank you for using Master Jarvis! Your AI learns from every interaction.", color='blue')
                        break
                    elif choice == '1':
                        self.smart_task_manager()
                    elif choice == '2':
                        self.show_smart_dashboard()
                    elif choice == '3':
                        self.complete_task()
                    elif choice == '4':
                        self.delete_tasks()
                    elif choice == '5':
                        self.cleanup_recurring_tasks()
                    elif choice == '6':
                        self.enhanced_ai_conversation()
                    elif choice == '7':
                        self.ai_productivity_analysis()
                    elif choice == '8':
                        self.daily_ai_briefing()
                    elif choice == '9':
                        self.create_daily_schedule()
                    elif choice == '10':
                        self.manage_saved_schedules()
                    elif choice == '11':
                        self.export_calendar()
                    elif choice == '12':
                        self.schedule_task_specific_day()
                    elif choice == '13':
                        self.smart_weekly_planner()
                    elif choice == '14':
                        self.weekly_dashboard()
                    elif choice == '15':
                        self.export_weekly_calendar()
                    elif choice == '16':
                        self.show_system_analytics()
                    elif choice == '17':
                        self.manage_preferences()
                    else:
                        print("❌ Invalid choice! Please select a number from 0-17.")
                        time.sleep(1)
                
                except KeyboardInterrupt:
                    print("\n👋 Exiting Master Jarvis...")
                    break
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    input("📱 Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    
    def delete_task(self):
        """Delete a task"""
        self.visual.print_header("🗑️ DELETE TASK")
        
        pending_tasks = self.db.get_tasks('pending', limit=10)
        
        if not pending_tasks:
            print("📋 No pending tasks to delete!")
            input("\n📱 Press Enter to continue...")
            return
        
        print("📋 Your pending tasks:")
        for i, task in enumerate(pending_tasks, 1):
            print(f"  {i}. {task[1]} (ID: {task[0]})")
        
        try:
            choice = int(input("\n🔢 Enter task number to delete: ")) - 1
            if 0 <= choice < len(pending_tasks):
                task = pending_tasks[choice]
                task_id = task[0]
                
                confirm = input(f"⚠️  Really delete '{task[1]}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    conn = sqlite3.connect(self.db.db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                    conn.commit()
                    conn.close()
                    
                    print("✅ Task deleted successfully!")
                else:
                    print("❌ Deletion cancelled.")
            else:
                print("❌ Invalid task number!")
        except ValueError:
            print("❌ Please enter a valid number!")
        
        input("\n📱 Press Enter to continue...")
    
    def create_daily_schedule(self):
        """Create AI-optimized daily schedule"""
        self.visual.print_header("📋 CREATE DAILY SCHEDULE")
        
        # Get pending tasks for scheduling
        tasks = self.db.get_tasks('pending', limit=15)
        
        if not tasks:
            print("🎉 No pending tasks to schedule! You're all caught up!")
            input("\n📱 Press Enter to continue...")
            return
        
        print("🤖 Creating AI-optimized daily schedule...\n")
        
        # Schedule configuration
        print("⚙️ Schedule Configuration:")
        work_hours = input("⏰ Work hours (e.g., '9-17' for 9 AM to 5 PM): ").strip() or "9-17"
        schedule_date = input("📅 Date (YYYY-MM-DD) or 'today': ").strip()
        
        if schedule_date.lower() == 'today' or not schedule_date:
            schedule_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            start_hour, end_hour = map(int, work_hours.split('-'))
        except ValueError:
            start_hour, end_hour = 9, 17
        
        # AI schedule optimization
        self.visual.print_ai_response("Analyzing tasks and creating optimal schedule...", thinking=True)
        
        # Process tasks safely with None handling
        safe_tasks = []
        for task in tasks:
            # Unpack with safe defaults
            (task_id, title, description, urgency, importance, est_time, actual_time, 
             category, status, created_at, completed_at, due_date, energy_level, 
             context, tags, priority_total) = task
            
            # Ensure all values are not None
            urgency = urgency if urgency is not None else 5
            importance = importance if importance is not None else 5
            priority_total = priority_total if priority_total is not None else (urgency + importance)
            est_time = est_time if est_time is not None else 1.0
            category = category if category is not None else "general"
            
            safe_task = {
                'id': task_id,
                'title': title,
                'description': description or "",
                'urgency': urgency,
                'importance': importance,
                'priority_total': priority_total,
                'est_time': est_time,
                'category': category
            }
            safe_tasks.append(safe_task)
        
        # Get AI scheduling recommendations
        task_summary = "\n".join([f"- {task['title']} (Priority: {task['priority_total']}/20, Est: {task['est_time']}h)" for task in safe_tasks])
        ai_prompt = f"""
        Create an optimized daily schedule for {schedule_date} from {start_hour}:00 to {end_hour}:00.
        
        Available tasks:
        {task_summary}
        
        Consider:
        - High priority tasks in peak energy hours (morning)
        - Batch similar tasks together
        - Include breaks and buffer time
        - Energy levels throughout the day
        
        Provide a structured schedule with time blocks.
        """
        
        ai_schedule = self.ai.call_claude_api(ai_prompt, "daily scheduling")
        
        # Create structured schedule
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}🗓️ AI-Optimized Schedule for {schedule_date}:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        print("=" * 60)
        
        # Display AI recommendations
        self.visual.print_ai_response(ai_schedule)
        
        # Create time-blocked schedule
        current_hour = start_hour
        scheduled_tasks = []
        
        print(f"\n{Fore.YELLOW if VISUAL_AVAILABLE else ''}⏰ Detailed Time Blocks:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        
        for i, task in enumerate(safe_tasks[:8]):  # Schedule top 8 priority tasks
            if current_hour >= end_hour:
                break
            
            # All values are now safe (no None values)
            priority_total = task['priority_total']
            est_time = task['est_time']
            title = task['title']
            category = task['category']
            
            # Estimate time block (default 1-2 hours if no estimate)
            time_needed = est_time if est_time > 0 else (2 if priority_total >= 16 else 1.5)
            time_needed = min(time_needed, 3)  # Max 3-hour blocks
            
            end_time = current_hour + time_needed
            if end_time > end_hour:
                end_time = end_hour
                time_needed = end_hour - current_hour
            
            if time_needed < 0.5:  # Not enough time left
                break
            
            priority_icon = "🔥" if priority_total >= 16 else "🟡" if priority_total >= 12 else "🟢"
            
            print(f"  {current_hour:02.0f}:{00:02.0f}-{end_time:02.0f}:{00:02.0f} {priority_icon} {title}")
            print(f"      📂 {category} | ⏱️ {time_needed:.1f}h | 🎯 Priority: {priority_total}/20")
            
            scheduled_tasks.append({
                'time': f"{current_hour:02.0f}:{00:02.0f}-{end_time:02.0f}:{00:02.0f}",
                'task': title,
                'priority': priority_total,
                'category': category
            })
            
            current_hour = end_time + 0.25  # 15-minute buffer between tasks
        
        # Add breaks
        print(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}☕ Recommended Breaks:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        print(f"  10:30-10:45 ☕ Coffee Break")
        print(f"  12:00-13:00 🍽️  Lunch Break") 
        print(f"  15:00-15:15 🚶 Afternoon Break")
        
        # Save schedule option
        save_schedule = input(f"\n💾 Save this schedule? (y/n): ").strip().lower()
        if save_schedule == 'y':
            schedule_name = input("📝 Schedule name: ").strip() or f"Schedule_{schedule_date}"
            
            schedule_data = {
                'date': schedule_date,
                'work_hours': work_hours,
                'tasks': scheduled_tasks,
                'ai_recommendations': ai_schedule[:500] if ai_schedule else "AI recommendations generated"
            }
            
            # Save to database
            try:
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO schedules (name, schedule_date, schedule_data)
                    VALUES (?, ?, ?)
                ''', (schedule_name, schedule_date, json.dumps(schedule_data, cls=DateTimeEncoder)))
                conn.commit()
                conn.close()
                
                print(f"✅ Schedule '{schedule_name}' saved successfully!")
            except Exception as e:
                print(f"⚠️ Schedule created but couldn't save: {str(e)}")
        
        input("\n📱 Press Enter to continue...")
    
    def manage_saved_schedules(self):
        """Manage saved schedules"""
        self.visual.print_header("💾 SAVED SCHEDULES")
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, schedule_date, created_at 
            FROM schedules 
            ORDER BY created_at DESC
        ''')
        schedules = cursor.fetchall()
        conn.close()
        
        if not schedules:
            print("📋 No saved schedules found.")
            print("💡 Create a daily schedule first to save it!")
            input("\n📱 Press Enter to continue...")
            return
        
        print(f"📋 Your saved schedules ({len(schedules)} total):\n")
        
        for i, (schedule_id, name, schedule_date, created_at) in enumerate(schedules, 1):
            print(f"  {i}. 📅 {name}")
            print(f"      📅 Date: {schedule_date} | 🕒 Created: {created_at[:16]}")
        
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}Options:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        self.visual.print_menu_option("v", "View schedule details", "👁️")
        self.visual.print_menu_option("d", "Delete schedule", "🗑️")
        self.visual.print_menu_option("e", "Export schedule", "📤")
        self.visual.print_menu_option("q", "Back to main menu", "⬅️")
        
        choice = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Enter choice: {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip().lower()
        
        if choice == 'q':
            return
        elif choice == 'v':
            try:
                schedule_num = int(input("Enter schedule number to view: ")) - 1
                if 0 <= schedule_num < len(schedules):
                    schedule_id = schedules[schedule_num][0]
                    self._view_schedule_details(schedule_id)
                else:
                    print("❌ Invalid schedule number!")
            except ValueError:
                print("❌ Please enter a valid number!")
        elif choice == 'd':
            try:
                schedule_num = int(input("Enter schedule number to delete: ")) - 1
                if 0 <= schedule_num < len(schedules):
                    schedule_id, name = schedules[schedule_num][0], schedules[schedule_num][1]
                    confirm = input(f"⚠️ Really delete '{name}'? (y/n): ").strip().lower()
                    if confirm == 'y':
                        conn = sqlite3.connect(self.db.db_path)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
                        conn.commit()
                        conn.close()
                        print("✅ Schedule deleted successfully!")
                else:
                    print("❌ Invalid schedule number!")
            except ValueError:
                print("❌ Please enter a valid number!")
        elif choice == 'e':
            try:
                schedule_num = int(input("Enter schedule number to export: ")) - 1
                if 0 <= schedule_num < len(schedules):
                    schedule_id = schedules[schedule_num][0]
                    self._export_schedule(schedule_id)
                else:
                    print("❌ Invalid schedule number!")
            except ValueError:
                print("❌ Please enter a valid number!")
        
        input("\n📱 Press Enter to continue...")
    
    def _view_schedule_details(self, schedule_id):
        """View detailed schedule information"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, schedule_date, schedule_data 
            FROM schedules 
            WHERE id = ?
        ''', (schedule_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            print("❌ Schedule not found!")
            return
        
        name, schedule_date, schedule_data_str = result
        schedule_data = json.loads(schedule_data_str)
        
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}📅 Schedule: {name}{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        print(f"📅 Date: {schedule_date}")
        print(f"⏰ Work Hours: {schedule_data.get('work_hours', 'N/A')}")
        print("\n⏰ Time Blocks:")
        
        for task in schedule_data.get('tasks', []):
            priority_icon = "🔥" if task['priority'] >= 16 else "🟡" if task['priority'] >= 12 else "🟢"
            print(f"  {task['time']} {priority_icon} {task['task']}")
            print(f"      📂 {task['category']} | 🎯 Priority: {task['priority']}/20")
        
        if 'ai_recommendations' in schedule_data:
            print(f"\n{Fore.MAGENTA if VISUAL_AVAILABLE else ''}🤖 AI Recommendations:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
            print(schedule_data['ai_recommendations'][:300] + "..." if len(schedule_data['ai_recommendations']) > 300 else schedule_data['ai_recommendations'])
    
    def _export_schedule(self, schedule_id):
        """Export schedule in various formats"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, schedule_date, schedule_data 
            FROM schedules 
            WHERE id = ?
        ''', (schedule_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            print("❌ Schedule not found!")
            return
        
        name, schedule_date, schedule_data_str = result
        schedule_data = json.loads(schedule_data_str)
        
        print(f"\n📤 Export Options for '{name}':")
        self.visual.print_menu_option("1", "Text format (.txt)")
        self.visual.print_menu_option("2", "Calendar format (.ics)")
        self.visual.print_menu_option("3", "HTML format (.html)")
        
        export_choice = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Export format: {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
        
        safe_filename = name.replace(' ', '_').replace('/', '_')
        
        if export_choice == '1':
            # Text export
            filename = f"data/{safe_filename}_{schedule_date}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"📅 {name}\n")
                f.write(f"Date: {schedule_date}\n")
                f.write(f"Work Hours: {schedule_data.get('work_hours', 'N/A')}\n\n")
                f.write("⏰ SCHEDULE:\n")
                f.write("=" * 50 + "\n")
                
                for task in schedule_data.get('tasks', []):
                    f.write(f"{task['time']} - {task['task']}\n")
                    f.write(f"    Category: {task['category']} | Priority: {task['priority']}/20\n\n")
                
                if 'ai_recommendations' in schedule_data:
                    f.write("\n🤖 AI RECOMMENDATIONS:\n")
                    f.write("=" * 50 + "\n")
                    f.write(schedule_data['ai_recommendations'])
            
            print(f"✅ Text schedule exported to: {filename}")
        
        elif export_choice == '2':
            # ICS Calendar export
            filename = f"data/{safe_filename}_{schedule_date}.ics"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("BEGIN:VCALENDAR\n")
                f.write("VERSION:2.0\n")
                f.write("PRODID:Jarvis AI Assistant\n")
                
                for task in schedule_data.get('tasks', []):
                    start_time, end_time = task['time'].split('-')
                    start_hour, start_min = map(int, start_time.split(':'))
                    end_hour, end_min = map(int, end_time.split(':'))
                    
                    # Create datetime strings for ICS format
                    dt = datetime.strptime(schedule_date, "%Y-%m-%d")
                    start_dt = dt.replace(hour=start_hour, minute=start_min)
                    end_dt = dt.replace(hour=end_hour, minute=end_min)
                    
                    f.write("BEGIN:VEVENT\n")
                    f.write(f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}\n")
                    f.write(f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}\n")
                    f.write(f"SUMMARY:{task['task']}\n")
                    f.write(f"DESCRIPTION:Category: {task['category']} | Priority: {task['priority']}/20\n")
                    f.write("END:VEVENT\n")
                
                f.write("END:VCALENDAR\n")
            
            print(f"✅ Calendar file exported to: {filename}")
            print("📱 Import this .ics file into Outlook, Google Calendar, or Apple Calendar")
        
        elif export_choice == '3':
            # HTML export
            filename = f"data/{safe_filename}_{schedule_date}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>{name} - {schedule_date}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .schedule-item {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #3498db; }}
        .time {{ font-weight: bold; color: #2c3e50; }}
        .task {{ font-size: 1.1em; color: #34495e; }}
        .details {{ color: #7f8c8d; font-size: 0.9em; }}
        .high-priority {{ border-left-color: #e74c3c; }}
        .medium-priority {{ border-left-color: #f39c12; }}
        .low-priority {{ border-left-color: #27ae60; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📅 {name}</h1>
        <p>Date: {schedule_date} | Work Hours: {schedule_data.get('work_hours', 'N/A')}</p>
    </div>
""")
                
                for task in schedule_data.get('tasks', []):
                    priority_class = "high-priority" if task['priority'] >= 16 else "medium-priority" if task['priority'] >= 12 else "low-priority"
                    priority_icon = "🔥" if task['priority'] >= 16 else "🟡" if task['priority'] >= 12 else "🟢"
                    
                    f.write(f"""
    <div class="schedule-item {priority_class}">
        <div class="time">{task['time']}</div>
        <div class="task">{priority_icon} {task['task']}</div>
        <div class="details">📂 {task['category']} | 🎯 Priority: {task['priority']}/20</div>
    </div>
""")
                
                if 'ai_recommendations' in schedule_data:
                    f.write(f"""
    <div class="header" style="margin-top: 30px;">
        <h2>🤖 AI Recommendations</h2>
    </div>
    <div style="background: #e8f6f3; padding: 15px; border-radius: 5px;">
        <p>{schedule_data['ai_recommendations']}</p>
    </div>
""")
                
                f.write("""
</body>
</html>
""")
            
            print(f"✅ HTML schedule exported to: {filename}")
            print("🌐 Open this file in your web browser for a beautiful printable schedule")
        
        else:
            print("❌ Invalid export choice!")
    
    def export_calendar(self):
        """Export calendar - unified entry point"""
        self.visual.print_header("📤 EXPORT CALENDAR")
        
        print("📅 Calendar Export Options:")
        self.visual.print_menu_option("1", "Export saved schedule")
        self.visual.print_menu_option("2", "Export current tasks as calendar")
        self.visual.print_menu_option("3", "Create & export new schedule")
        
        choice = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Enter choice: {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
        
        if choice == '1':
            self.manage_saved_schedules()
        elif choice == '2':
            self._export_tasks_as_calendar()
        elif choice == '3':
            self.create_daily_schedule()
        else:
            print("❌ Invalid choice!")
        
        input("\n📱 Press Enter to continue...")
    
    def _export_tasks_as_calendar(self):
        """Export current tasks as calendar events"""
        tasks = self.db.get_tasks('pending', limit=10)
        
        if not tasks:
            print("📋 No pending tasks to export!")
            return
        
        schedule_date = input("📅 Date for tasks (YYYY-MM-DD) or 'today': ").strip()
        if schedule_date.lower() == 'today' or not schedule_date:
            schedule_date = datetime.now().strftime("%Y-%m-%d")
        
        filename = f"data/tasks_calendar_{schedule_date}.ics"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("BEGIN:VCALENDAR\n")
            f.write("VERSION:2.0\n")
            f.write("PRODID:Jarvis AI Assistant\n")
            
            current_hour = 9  # Start at 9 AM
            
            for task in tasks:
                task_id, title, description, urgency, importance, est_time, actual_time, category, status, created_at, completed_at, due_date, energy_level, context, tags, priority_total = task
                
                # Default 1 hour if no estimate
                duration = est_time or 1.0
                
                dt = datetime.strptime(schedule_date, "%Y-%m-%d")
                start_dt = dt.replace(hour=current_hour, minute=0)
                end_dt = dt.replace(hour=current_hour + int(duration), minute=int((duration % 1) * 60))
                
                f.write("BEGIN:VEVENT\n")
                f.write(f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}\n")
                f.write(f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}\n")
                f.write(f"SUMMARY:{title}\n")
                f.write(f"DESCRIPTION:Category: {category} | Priority: {priority_total}/20")
                if description:
                    f.write(f" | Notes: {description}")
                f.write("\n")
                f.write("END:VEVENT\n")
                
                current_hour += max(1, int(duration))
                if current_hour >= 17:  # Don't go past 5 PM
                    break
            
            f.write("END:VCALENDAR\n")
        
        print(f"✅ Tasks exported to calendar: {filename}")
        print("📱 Import this .ics file into your calendar app")
    
    def smart_weekly_planner(self):
        """AI-powered weekly schedule optimization"""
        self.visual.print_header("🗓️ SMART WEEKLY PLANNER")
        
        # Get all pending tasks
        tasks = self.db.get_tasks('pending', limit=50)
        
        if not tasks:
            print("🎉 No pending tasks to schedule! You're all caught up!")
            input("\n📱 Press Enter to continue...")
            return
        
        print(f"📋 Found {len(tasks)} tasks to schedule across the week")
        
        # Weekly planning configuration
        print("\n⚙️ Weekly Planning Configuration:")
        start_date = input("📅 Week starting date (YYYY-MM-DD) or 'this week': ").strip()
        
        if start_date.lower() == 'this week' or not start_date:
            # Get Monday of current week
            today = datetime.now()
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
            start_date = monday.strftime("%Y-%m-%d")
        
        work_hours = input("⏰ Daily work hours (e.g., '9-17'): ").strip() or "9-17"
        try:
            start_hour, end_hour = map(int, work_hours.split('-'))
            daily_hours = end_hour - start_hour
        except ValueError:
            start_hour, end_hour = 9, 17
            daily_hours = 8
        
        # Weekly goals and focus areas
        print(f"\n🎯 Weekly Focus Areas:")
        weekly_goals = input("📝 Main goals for this week (optional): ").strip()
        priority_focus = input("🔥 Priority focus (high/medium/low): ").strip().lower() or "high"
        
        # Process tasks safely for weekly planning
        safe_tasks = []
        total_estimated_hours = 0
        
        for task in tasks:
            (task_id, title, description, urgency, importance, est_time, actual_time, 
             category, status, created_at, completed_at, due_date, energy_level, 
             context, tags, priority_total) = task
            
            # Safe defaults
            urgency = urgency if urgency is not None else 5
            importance = importance if importance is not None else 5
            priority_total = priority_total if priority_total is not None else (urgency + importance)
            est_time = est_time if est_time is not None else 1.5
            category = category if category is not None else "general"
            energy_level = energy_level if energy_level is not None else "medium"
            
            total_estimated_hours += est_time
            
            safe_task = {
                'id': task_id,
                'title': title,
                'description': description or "",
                'urgency': urgency,
                'importance': importance,
                'priority_total': priority_total,
                'est_time': est_time,
                'category': category,
                'energy_level': energy_level,
                'due_date': due_date,
                'days_until_due': self._calculate_days_until_due(due_date, start_date) if due_date else None
            }
            safe_tasks.append(safe_task)
        
        # AI weekly optimization
        self.visual.print_ai_response("🧠 Analyzing tasks for optimal weekly distribution...", thinking=True)
        
        # Create AI prompt for weekly planning
        task_summary = "\n".join([
            f"- {task['title']} (Priority: {task['priority_total']}/20, Est: {task['est_time']}h, Category: {task['category']}, Energy: {task['energy_level']})"
            for task in safe_tasks[:15]  # Limit for API
        ])
        
        ai_prompt = f"""
        Create an optimal weekly schedule from {start_date} for the following tasks.
        
        Weekly Parameters:
        - Work hours: {work_hours} daily ({daily_hours} hours/day = {daily_hours * 5} hours/week)
        - Total task time: {total_estimated_hours:.1f} hours
        - Weekly goals: {weekly_goals or 'General productivity'}
        - Priority focus: {priority_focus}
        
        Available tasks:
        {task_summary}
        
        Optimization principles:
        1. High priority/urgency tasks scheduled in peak energy times (Monday-Wednesday mornings)
        2. Group similar categories together for focus
        3. Balance workload across the week
        4. Match task energy requirements to daily energy patterns
        5. Leave buffer time for unexpected tasks
        
        Provide strategic weekly planning advice and daily focus recommendations.
        """
        
        ai_weekly_analysis = self.ai.call_claude_api(ai_prompt, "weekly planning")
        
        # Display AI analysis
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}🧠 AI Weekly Analysis:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        self.visual.print_ai_response(ai_weekly_analysis)
        
        # Generate weekly schedule
        weekly_schedule = self._generate_weekly_schedule(safe_tasks, start_date, start_hour, end_hour)
        
        # Display weekly overview
        self._display_weekly_overview(weekly_schedule, start_date)
        
        # Save weekly schedule option
        save_weekly = input(f"\n💾 Save this weekly schedule? (y/n): ").strip().lower()
        if save_weekly == 'y':
            schedule_name = input("📝 Weekly schedule name: ").strip() or f"Week_{start_date}"
            
            weekly_data = {
                'start_date': start_date,
                'work_hours': work_hours,
                'weekly_goals': weekly_goals,
                'priority_focus': priority_focus,
                'schedule': weekly_schedule,
                'ai_analysis': ai_weekly_analysis[:500] if ai_weekly_analysis else "AI analysis generated",
                'total_hours': total_estimated_hours
            }
            
            try:
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO schedules (name, schedule_date, schedule_data)
                    VALUES (?, ?, ?)
                ''', (schedule_name, start_date, json.dumps(weekly_data, cls=DateTimeEncoder)))
                conn.commit()
                conn.close()
                
                print(f"✅ Weekly schedule '{schedule_name}' saved successfully!")
            except Exception as e:
                print(f"⚠️ Weekly schedule created but couldn't save: {str(e)}")
        
        input("\n📱 Press Enter to continue...")
    
    def _generate_weekly_schedule(self, tasks, start_date, start_hour, end_hour):
        """Generate deadline-aware optimized weekly schedule from tasks"""
        
        # Sort tasks by deadline urgency first, then by priority
        def sort_key(task):
            # Deadline priority: tasks due within the week get highest priority
            deadline_priority = 0
            if task['days_until_due'] is not None:
                if task['days_until_due'] <= 0:  # Overdue
                    deadline_priority = 1000
                elif task['days_until_due'] <= 7:  # Due within week
                    deadline_priority = 100 - task['days_until_due']  # Earlier deadlines = higher priority
                else:  # Due later
                    deadline_priority = 10
            
            # Combine deadline priority with task priority
            return (-deadline_priority, -task['priority_total'], task['energy_level'] != 'high')
        
        sorted_tasks = sorted(tasks, key=sort_key)
        
        # Create weekly structure
        weekly_schedule = {}
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for i, day in enumerate(weekdays):
            date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i)
            weekly_schedule[day] = {
                'date': date.strftime("%Y-%m-%d"),
                'tasks': [],
                'total_hours': 0,
                'focus_theme': '',
                'deadline_alerts': []
            }
        
        # Track deadline conflicts
        deadline_warnings = []
        daily_capacity = (end_hour - start_hour) * 0.8  # 80% utilization
        
        # Distribute tasks with deadline awareness
        for task in sorted_tasks:
            best_day = self._find_best_day_for_task(task, weekly_schedule, weekdays, daily_capacity, start_date)
            
            if best_day:
                day_schedule = weekly_schedule[best_day]
                
                # Add task to selected day
                day_schedule['tasks'].append({
                    'title': task['title'],
                    'est_time': task['est_time'],
                    'priority': task['priority_total'],
                    'category': task['category'],
                    'energy_level': task['energy_level'],
                    'due_date': task['due_date'],
                    'days_until_due': task['days_until_due'],
                    'deadline_status': self._get_deadline_status(task['days_until_due'])
                })
                day_schedule['total_hours'] += task['est_time']
                
                # Check for deadline conflicts
                if task['days_until_due'] is not None and task['days_until_due'] <= 3:
                    day_schedule['deadline_alerts'].append(f"⚠️ '{task['title']}' due in {task['days_until_due']} days")
            else:
                # Couldn't fit task in the week
                deadline_warnings.append(f"⚠️ Could not schedule '{task['title']}' - consider extending work hours or rescheduling")
        
        # Assign daily focus themes based on scheduled tasks
        for day, schedule in weekly_schedule.items():
            if schedule['tasks']:
                categories = [task['category'] for task in schedule['tasks']]
                main_category = max(set(categories), key=categories.count)
                
                # Check for deadline-focused days
                urgent_tasks = [t for t in schedule['tasks'] if t.get('deadline_status') == 'urgent']
                if urgent_tasks:
                    schedule['focus_theme'] = f"🔥 Deadline Focus ({main_category.title()})"
                else:
                    schedule['focus_theme'] = f"{main_category.title()} Focus"
        
        # Store warnings for display
        if deadline_warnings:
            weekly_schedule['_warnings'] = deadline_warnings
        
        return weekly_schedule
    
    def _find_best_day_for_task(self, task, weekly_schedule, weekdays, daily_capacity, start_date):
        """Find the best day to schedule a task considering deadlines and capacity"""
        
        # If task has a deadline, try to schedule it appropriately
        if task['days_until_due'] is not None:
            target_day_index = min(task['days_until_due'], 4)  # Cap at Friday (index 4)
            
            # Try to schedule on or before the target day
            for day_offset in range(max(0, target_day_index - 1), min(len(weekdays), target_day_index + 2)):
                if day_offset < len(weekdays):
                    day_name = weekdays[day_offset]
                    day_schedule = weekly_schedule[day_name]
                    
                    # Check if task fits
                    if day_schedule['total_hours'] + task['est_time'] <= daily_capacity:
                        return day_name
        
        # No deadline constraints - find best available day
        for day_name in weekdays:
            day_schedule = weekly_schedule[day_name]
            if day_schedule['total_hours'] + task['est_time'] <= daily_capacity:
                return day_name
        
        # All days full - put in least full day
        least_full_day = min(weekdays, key=lambda d: weekly_schedule[d]['total_hours'])
        return least_full_day
    
    def _get_deadline_status(self, days_until_due):
        """Get deadline status for color coding and alerts"""
        if days_until_due is None:
            return 'none'
        elif days_until_due <= 0:
            return 'overdue'
        elif days_until_due <= 1:
            return 'urgent'
        elif days_until_due <= 3:
            return 'approaching'
        elif days_until_due <= 7:
            return 'thisweek'
        else:
            return 'future'
    
    def _display_weekly_overview(self, weekly_schedule, start_date):
        """Display beautiful weekly schedule overview with deadline awareness"""
        
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}🗓️ WEEKLY SCHEDULE OVERVIEW{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        print("=" * 80)
        
        total_week_hours = 0
        deadline_alerts = []
        
        for day, schedule in weekly_schedule.items():
            if day.startswith('_'):  # Skip metadata keys
                continue
                
            date_obj = datetime.strptime(schedule['date'], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%m/%d")
            
            total_week_hours += schedule['total_hours']
            
            # Collect deadline alerts
            deadline_alerts.extend(schedule.get('deadline_alerts', []))
            
            # Day header with workload color coding
            if VISUAL_AVAILABLE:
                if schedule['total_hours'] > 6:
                    day_color = Fore.RED  # Heavy day
                elif schedule['total_hours'] > 4:
                    day_color = Fore.YELLOW  # Moderate day
                else:
                    day_color = Fore.GREEN  # Light day
                
                print(f"\n{day_color}📅 {day} ({formatted_date}) - {schedule['focus_theme']}{Style.RESET_ALL}")
                print(f"{day_color}⏱️ Total: {schedule['total_hours']:.1f} hours{Style.RESET_ALL}")
            else:
                print(f"\n📅 {day} ({formatted_date}) - {schedule['focus_theme']}")
                print(f"⏱️ Total: {schedule['total_hours']:.1f} hours")
            
            # Task list for the day with deadline indicators
            if schedule['tasks']:
                for i, task in enumerate(schedule['tasks'], 1):
                    # Priority indicators
                    priority_icon = "🔥" if task['priority'] >= 16 else "🟡" if task['priority'] >= 12 else "🟢"
                    energy_icon = "⚡" if task['energy_level'] == 'high' else "🔋" if task['energy_level'] == 'medium' else "💤"
                    
                    # Deadline indicators
                    deadline_status = task.get('deadline_status', 'none')
                    deadline_icon = ""
                    deadline_color = ""
                    
                    if VISUAL_AVAILABLE:
                        if deadline_status == 'overdue':
                            deadline_icon = "🚨"
                            deadline_color = Fore.RED
                        elif deadline_status == 'urgent':
                            deadline_icon = "⏰"
                            deadline_color = Fore.RED
                        elif deadline_status == 'approaching':
                            deadline_icon = "📅"
                            deadline_color = Fore.YELLOW
                        elif deadline_status == 'thisweek':
                            deadline_icon = "📆"
                            deadline_color = Fore.CYAN
                    else:
                        if deadline_status == 'overdue':
                            deadline_icon = "[OVERDUE]"
                        elif deadline_status == 'urgent':
                            deadline_icon = "[URGENT]"
                        elif deadline_status == 'approaching':
                            deadline_icon = "[DUE SOON]"
                        elif deadline_status == 'thisweek':
                            deadline_icon = "[THIS WEEK]"
                    
                    # Display task with deadline info
                    task_line = f"  {i}. {priority_icon} {task['title']}"
                    if deadline_icon:
                        if VISUAL_AVAILABLE:
                            task_line += f" {deadline_color}{deadline_icon}{Style.RESET_ALL}"
                        else:
                            task_line += f" {deadline_icon}"
                    
                    print(task_line)
                    
                    # Task details
                    details = f"     ⏱️ {task['est_time']}h | 📂 {task['category']} | {energy_icon} {task['energy_level']}"
                    if task.get('due_date'):
                        details += f" | 📅 Due: {task['due_date']}"
                    print(details)
            else:
                print("  🎉 Light day - perfect for catch-up or planning!")
        
        # Show deadline alerts
        if deadline_alerts:
            print(f"\n{Fore.RED if VISUAL_AVAILABLE else ''}🚨 DEADLINE ALERTS:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
            for alert in deadline_alerts:
                print(f"   {alert}")
        
        # Show scheduling warnings
        if '_warnings' in weekly_schedule:
            print(f"\n{Fore.YELLOW if VISUAL_AVAILABLE else ''}⚠️ SCHEDULING WARNINGS:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
            for warning in weekly_schedule['_warnings']:
                print(f"   {warning}")
        
        # Weekly summary
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}📊 WEEKLY SUMMARY:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        print(f"⏱️ Total planned hours: {total_week_hours:.1f}")
        print(f"📈 Daily average: {total_week_hours/5:.1f} hours")
        print(f"📅 Deadline-critical tasks: {len(deadline_alerts)}")
        
        # Workload assessment
        if total_week_hours > 35:
            print(f"⚠️ {Fore.RED if VISUAL_AVAILABLE else ''}High workload week - consider delegating or rescheduling{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        elif total_week_hours < 20:
            print(f"🎯 {Fore.GREEN if VISUAL_AVAILABLE else ''}Light week - good opportunity for strategic projects{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        else:
            print(f"✅ {Fore.GREEN if VISUAL_AVAILABLE else ''}Well-balanced week!{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        
        # Deadline distribution analysis
        total_tasks = sum(len(schedule['tasks']) for schedule in weekly_schedule.values() if not isinstance(schedule, list))
        deadline_tasks = sum(1 for schedule in weekly_schedule.values() if not isinstance(schedule, list) 
                           for task in schedule['tasks'] if task.get('due_date'))
        
        if deadline_tasks > 0:
            print(f"📅 Tasks with deadlines: {deadline_tasks}/{total_tasks} ({deadline_tasks/total_tasks*100:.0f}%)")
    
    def weekly_dashboard(self):
        """Display weekly dashboard with analytics"""
        self.visual.print_header("📊 WEEKLY DASHBOARD")
        
        # Get saved weekly schedules
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, schedule_date, schedule_data, created_at
            FROM schedules 
            WHERE name LIKE 'Week_%' OR schedule_data LIKE '%weekly_goals%'
            ORDER BY created_at DESC
            LIMIT 5
        ''')
        weekly_schedules = cursor.fetchall()
        conn.close()
        
        if not weekly_schedules:
            print("📋 No weekly schedules found.")
            print("💡 Create a weekly schedule first using option 14!")
            input("\n📱 Press Enter to continue...")
            return
        
        print(f"📊 Weekly Schedules Dashboard ({len(weekly_schedules)} recent weeks):\n")
        
        for i, (schedule_id, name, schedule_date, schedule_data_str, created_at) in enumerate(weekly_schedules, 1):
            try:
                schedule_data = json.loads(schedule_data_str)
                
                # Check if it's actually weekly data
                if 'schedule' in schedule_data and isinstance(schedule_data['schedule'], dict):
                    total_hours = schedule_data.get('total_hours', 0)
                    weekly_goals = schedule_data.get('weekly_goals', 'N/A')
                    
                    print(f"  {i}. 📅 {name}")
                    print(f"      📅 Week of: {schedule_date}")
                    print(f"      ⏱️ Total hours: {total_hours:.1f}")
                    print(f"      🎯 Goals: {weekly_goals[:50]}{'...' if len(weekly_goals) > 50 else ''}")
                    print(f"      📝 Created: {created_at[:16]}")
                    print()
                    
            except (json.JSONDecodeError, KeyError):
                # Skip non-weekly schedules
                continue
        
        print(f"{Fore.CYAN if VISUAL_AVAILABLE else ''}Options:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        self.visual.print_menu_option("v", "View detailed weekly schedule", "👁️")
        self.visual.print_menu_option("a", "Weekly analytics comparison", "📈")
        self.visual.print_menu_option("q", "Back to main menu", "⬅️")
        
        choice = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Enter choice: {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip().lower()
        
        if choice == 'v':
            try:
                week_num = int(input("Enter week number to view: ")) - 1
                if 0 <= week_num < len(weekly_schedules):
                    self._view_weekly_details(weekly_schedules[week_num])
                else:
                    print("❌ Invalid week number!")
            except ValueError:
                print("❌ Please enter a valid number!")
        elif choice == 'a':
            self._show_weekly_analytics(weekly_schedules)
        
        input("\n📱 Press Enter to continue...")
    
    def _view_weekly_details(self, schedule_tuple):
        """View detailed weekly schedule"""
        schedule_id, name, schedule_date, schedule_data_str, created_at = schedule_tuple
        
        try:
            schedule_data = json.loads(schedule_data_str)
            
            print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}📅 Weekly Schedule: {name}{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
            print(f"📅 Week of: {schedule_date}")
            print(f"🎯 Goals: {schedule_data.get('weekly_goals', 'N/A')}")
            print(f"⏰ Work hours: {schedule_data.get('work_hours', 'N/A')}")
            print(f"⏱️ Total planned: {schedule_data.get('total_hours', 0):.1f} hours")
            
            if 'schedule' in schedule_data:
                self._display_weekly_overview(schedule_data['schedule'], schedule_date)
            
            if 'ai_analysis' in schedule_data:
                print(f"\n{Fore.MAGENTA if VISUAL_AVAILABLE else ''}🤖 AI Analysis:{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
                print(schedule_data['ai_analysis'])
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Error viewing schedule: {str(e)}")
    
    def _show_weekly_analytics(self, weekly_schedules):
        """Show analytics across multiple weeks"""
        print(f"\n{Fore.CYAN if VISUAL_AVAILABLE else ''}📈 WEEKLY ANALYTICS{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        
        total_weeks = 0
        total_hours = 0
        weekly_hours = []
        
        for schedule_tuple in weekly_schedules:
            try:
                schedule_data = json.loads(schedule_tuple[3])
                if 'total_hours' in schedule_data:
                    hours = schedule_data['total_hours']
                    total_hours += hours
                    weekly_hours.append(hours)
                    total_weeks += 1
            except (json.JSONDecodeError, KeyError):
                continue
        
        if total_weeks > 0:
            avg_hours = total_hours / total_weeks
            min_hours = min(weekly_hours)
            max_hours = max(weekly_hours)
            
            print(f"📊 Analytics for {total_weeks} weeks:")
            print(f"   ⏱️ Average weekly hours: {avg_hours:.1f}")
            print(f"   📈 Highest week: {max_hours:.1f} hours")
            print(f"   📉 Lightest week: {min_hours:.1f} hours")
            print(f"   📊 Total planned: {total_hours:.1f} hours")
            
            # Productivity insights
            if avg_hours > 35:
                print(f"   💡 {Fore.YELLOW if VISUAL_AVAILABLE else ''}Trend: High workload weeks - consider workload balancing{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
            elif avg_hours < 25:
                print(f"   💡 {Fore.GREEN if VISUAL_AVAILABLE else ''}Trend: Sustainable pace - good work-life balance{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
            else:
                print(f"   💡 {Fore.GREEN if VISUAL_AVAILABLE else ''}Trend: Well-balanced weekly planning{Style.RESET_ALL if VISUAL_AVAILABLE else ''}")
        else:
            print("📊 No weekly data available for analytics")
    
    def export_weekly_calendar(self):
        """Export weekly schedules in various formats"""
        self.visual.print_header("📤 EXPORT WEEKLY CALENDAR")
        
        # Get weekly schedules
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, schedule_date, schedule_data
            FROM schedules 
            WHERE name LIKE 'Week_%' OR schedule_data LIKE '%weekly_goals%'
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        weekly_schedules = cursor.fetchall()
        conn.close()
        
        if not weekly_schedules:
            print("📋 No weekly schedules found to export.")
            print("💡 Create a weekly schedule first using option 14!")
            input("\n📱 Press Enter to continue...")
            return
        
        print(f"📋 Available weekly schedules:\n")
        
        valid_schedules = []
        for i, (schedule_id, name, schedule_date, schedule_data_str) in enumerate(weekly_schedules, 1):
            try:
                schedule_data = json.loads(schedule_data_str)
                if 'schedule' in schedule_data:
                    print(f"  {i}. 📅 {name} (Week of {schedule_date})")
                    valid_schedules.append((schedule_id, name, schedule_date, schedule_data))
            except json.JSONDecodeError:
                continue
        
        if not valid_schedules:
            print("❌ No valid weekly schedules found!")
            input("\n📱 Press Enter to continue...")
            return
        
        try:
            selection_input = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Select weekly schedule to export: {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
            
            if not selection_input:
                print("❌ No selection made!")
                input("\n📱 Press Enter to continue...")
                return
            
            choice = int(selection_input) - 1
            if 0 <= choice < len(valid_schedules):
                schedule_id, name, schedule_date, schedule_data = valid_schedules[choice]
                print(f"\n✅ Selected: {name}")
                self._export_weekly_schedule(name, schedule_date, schedule_data)
            else:
                print(f"❌ Invalid selection! Please enter a number between 1 and {len(valid_schedules)}.")
        except ValueError:
            print(f"❌ Please enter a valid number between 1 and {len(valid_schedules)}!")
        except Exception as e:
            print(f"❌ Export error: {str(e)}")
        
        input("\n📱 Press Enter to continue...")
    
    def _export_weekly_schedule(self, name, start_date, schedule_data):
        """Export weekly schedule in multiple formats"""
        
        print(f"\n📤 Export Options for '{name}':")
        self.visual.print_menu_option("1", "Weekly Calendar (.ics) - Import to calendar apps")
        self.visual.print_menu_option("2", "Weekly Overview (.html) - Beautiful printable format")
        self.visual.print_menu_option("3", "Weekly Planner (.txt) - Simple text format")
        self.visual.print_menu_option("4", "All formats")
        
        export_choice = input(f"\n{Fore.GREEN if VISUAL_AVAILABLE else ''}Export format: {Style.RESET_ALL if VISUAL_AVAILABLE else ''}").strip()
        
        # Debug output to see what we're getting
        print(f"Debug: You entered '{export_choice}' (length: {len(export_choice)})")
        
        safe_name = name.replace(' ', '_').replace('/', '_')
        exported_files = []
        
        # Make sure we're comparing strings correctly
        if export_choice == '1':
            print("📊 Exporting ICS Calendar format...")
            try:
                self._export_weekly_ics(safe_name, start_date, schedule_data)
                exported_files.append("ICS Calendar")
            except Exception as e:
                print(f"❌ Error creating ICS file: {str(e)}")
                return
                
        elif export_choice == '2':
            print("📊 Exporting HTML format...")
            try:
                self._export_weekly_html(safe_name, start_date, schedule_data)
                exported_files.append("HTML Overview")
            except Exception as e:
                print(f"❌ Error creating HTML file: {str(e)}")
                return
                
        elif export_choice == '3':
            print("📊 Exporting Text format...")
            try:
                self._export_weekly_txt(safe_name, start_date, schedule_data)
                exported_files.append("Text Planner")
            except Exception as e:
                print(f"❌ Error creating text file: {str(e)}")
                return
                
        elif export_choice == '4':
            print("📊 Exporting all formats...")
            try:
                self._export_weekly_ics(safe_name, start_date, schedule_data)
                self._export_weekly_html(safe_name, start_date, schedule_data)
                self._export_weekly_txt(safe_name, start_date, schedule_data)
                exported_files = ["ICS Calendar", "HTML Overview", "Text Planner"]
            except Exception as e:
                print(f"❌ Error creating files: {str(e)}")
                return
        else:
            print(f"❌ Invalid export choice '{export_choice}'! Please enter 1, 2, 3, or 4.")
            print("💡 Tip: Make sure to enter just the number without any extra characters.")
            return
        
        # Success message
        if len(exported_files) == 1:
            print(f"✅ Weekly schedule exported as {exported_files[0]}!")
        else:
            print(f"✅ Weekly schedule exported in all formats: {', '.join(exported_files)}!")
        
        print(f"📁 Files saved in: data/ folder")
        print(f"💡 Look for files starting with: {safe_name}_weekly_{start_date}")
        
        # Show the actual file path
        import os
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        print(f"📍 Full path: {data_path}")
        
        # List files that were created
        try:
            import os
            if os.path.exists('data'):
                files = [f for f in os.listdir('data') if f.startswith(safe_name)]
                if files:
                    print(f"📋 Created files:")
                    for file in files:
                        print(f"   • {file}")
                else:
                    print("⚠️ No files found in data folder")
            else:
                print("⚠️ Data folder does not exist - creating it now")
                os.makedirs('data', exist_ok=True)
        except Exception as e:
            print(f"📁 File listing error: {str(e)}")
    
    def _export_weekly_ics(self, name, start_date, schedule_data):
        """Export weekly schedule as ICS calendar file"""
        filename = f"data/{name}_weekly_{start_date}.ics"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("BEGIN:VCALENDAR\n")
                f.write("VERSION:2.0\n")
                f.write("PRODID:Jarvis AI Assistant - Weekly Planner\n")
                
                weekly_schedule = schedule_data.get('schedule', {})
                work_hours = schedule_data.get('work_hours', '9-17')
                
                try:
                    start_hour = int(work_hours.split('-')[0])
                except (ValueError, IndexError):
                    start_hour = 9  # Default fallback
                
                for day_name, day_schedule in weekly_schedule.items():
                    if day_name.startswith('_'):  # Skip metadata
                        continue
                        
                    if day_schedule.get('tasks'):
                        date_str = day_schedule['date']
                        current_hour = start_hour
                        
                        for task in day_schedule['tasks']:
                            # Calculate time slots with bounds checking
                            task_duration = task.get('est_time', 1.0)
                            
                            # Ensure current_hour is within valid range
                            if current_hour < 0:
                                current_hour = 9
                            elif current_hour > 23:
                                current_hour = 17
                            
                            # Calculate end hour, ensuring it doesn't exceed 23
                            end_hour = min(current_hour + int(task_duration), 23)
                            end_minute = int((task_duration % 1) * 60)
                            
                            # Ensure end_minute is within valid range
                            if end_minute >= 60:
                                end_minute = 59
                            elif end_minute < 0:
                                end_minute = 0
                            
                            try:
                                dt = datetime.strptime(date_str, "%Y-%m-%d")
                                start_dt = dt.replace(hour=current_hour, minute=0)
                                end_dt = dt.replace(hour=end_hour, minute=end_minute)
                                
                                # Generate unique event ID
                                event_id = f"jarvis-{start_dt.strftime('%Y%m%d%H%M%S')}-{hash(task['title']) % 10000}"
                                
                                f.write("BEGIN:VEVENT\n")
                                f.write(f"UID:{event_id}@jarvis-ai-assistant\n")
                                f.write(f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}\n")
                                f.write(f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}\n")
                                f.write(f"SUMMARY:{task.get('title', 'Untitled Task')}\n")
                                
                                # Build description with available info
                                desc_parts = []
                                if task.get('category'):
                                    desc_parts.append(f"Category: {task['category']}")
                                if task.get('priority'):
                                    desc_parts.append(f"Priority: {task['priority']}/20")
                                if task.get('energy_level'):
                                    desc_parts.append(f"Energy: {task['energy_level']}")
                                
                                if desc_parts:
                                    f.write(f"DESCRIPTION:{' | '.join(desc_parts)}\n")
                                
                                f.write("END:VEVENT\n")
                                
                                # Move to next time slot, ensuring we don't exceed day boundaries
                                current_hour = min(end_hour + 1, 23)
                                
                            except (ValueError, OverflowError) as e:
                                print(f"⚠️ Skipping task '{task.get('title', 'Unknown')}' - datetime error: {str(e)}")
                                continue
                
                f.write("END:VCALENDAR\n")
            
            print(f"✅ Weekly calendar exported: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating ICS file: {str(e)}")
            print(f"💡 This might be due to invalid schedule data or file permissions.")
            return False
    
    def _export_weekly_html(self, name, start_date, schedule_data):
        """Export weekly schedule as HTML"""
        filename = f"data/{name}_weekly_{start_date}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>{name} - Weekly Schedule</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; margin-bottom: 20px; }}
        .week-overview {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin: 20px 0; }}
        .day-card {{ border: 2px solid #ecf0f1; border-radius: 8px; padding: 15px; background: #f8f9fa; }}
        .day-header {{ font-weight: bold; color: #2c3e50; border-bottom: 1px solid #bdc3c7; padding-bottom: 8px; margin-bottom: 10px; }}
        .task-item {{ margin: 8px 0; padding: 8px; border-radius: 4px; }}
        .high-priority {{ background: #ffeaa7; border-left: 4px solid #e17055; }}
        .medium-priority {{ background: #fab1a0; border-left: 4px solid #fd79a8; }}
        .low-priority {{ background: #a4f7c0; border-left: 4px solid #00b894; }}
        .task-details {{ font-size: 0.85em; color: #636e72; margin-top: 4px; }}
        .weekly-summary {{ background: #e8f6f3; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .goals {{ background: #ffeaa7; padding: 15px; border-radius: 8px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🗓️ {name}</h1>
        <p>📅 Week of {start_date} | ⏰ Work Hours: {schedule_data.get('work_hours', 'N/A')} | ⏱️ Total: {schedule_data.get('total_hours', 0):.1f} hours</p>
    </div>
""")
            
            # Weekly goals
            if schedule_data.get('weekly_goals'):
                f.write(f"""
    <div class="goals">
        <h3>🎯 Weekly Goals</h3>
        <p>{schedule_data['weekly_goals']}</p>
    </div>
""")
            
            # Weekly overview
            f.write('<div class="week-overview">')
            
            weekly_schedule = schedule_data.get('schedule', {})
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            
            for day in weekdays:
                if day in weekly_schedule:
                    day_schedule = weekly_schedule[day]
                    day_date = day_schedule.get('date', '')
                    
                    f.write(f"""
        <div class="day-card">
            <div class="day-header">📅 {day}<br><small>{day_date}</small></div>
            <div><strong>{day_schedule.get('focus_theme', '')}</strong></div>
            <div>⏱️ {day_schedule.get('total_hours', 0):.1f} hours</div>
""")
                    
                    for task in day_schedule.get('tasks', []):
                        priority_class = "high-priority" if task['priority'] >= 16 else "medium-priority" if task['priority'] >= 12 else "low-priority"
                        priority_icon = "🔥" if task['priority'] >= 16 else "🟡" if task['priority'] >= 12 else "🟢"
                        energy_icon = "⚡" if task['energy_level'] == 'high' else "🔋" if task['energy_level'] == 'medium' else "💤"
                        
                        f.write(f"""
            <div class="task-item {priority_class}">
                <div>{priority_icon} {task['title']}</div>
                <div class="task-details">⏱️ {task['est_time']}h | 📂 {task['category']} | {energy_icon}</div>
            </div>
""")
                    
                    f.write('        </div>')
            
            f.write('</div>')
            
            # Weekly summary
            f.write(f"""
    <div class="weekly-summary">
        <h3>📊 Weekly Summary</h3>
        <p>⏱️ Total planned hours: {schedule_data.get('total_hours', 0):.1f}</p>
        <p>📈 Daily average: {schedule_data.get('total_hours', 0)/5:.1f} hours</p>
        <p>🎯 Priority focus: {schedule_data.get('priority_focus', 'N/A').title()}</p>
    </div>
""")
            
            if 'ai_analysis' in schedule_data:
                f.write(f"""
    <div class="weekly-summary">
        <h3>🤖 AI Weekly Analysis</h3>
        <p>{schedule_data['ai_analysis']}</p>
    </div>
""")
            
            f.write("""
</body>
</html>
""")
        
        print(f"✅ Weekly HTML exported: {filename}")
    
    def _export_weekly_txt(self, name, start_date, schedule_data):
        """Export weekly schedule as text file"""
        filename = f"data/{name}_weekly_{start_date}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"🗓️ {name}\n")
            f.write(f"Week of {start_date}\n")
            f.write(f"Work Hours: {schedule_data.get('work_hours', 'N/A')}\n")
            f.write(f"Total Hours: {schedule_data.get('total_hours', 0):.1f}\n")
            f.write("=" * 60 + "\n\n")
            
            if schedule_data.get('weekly_goals'):
                f.write(f"🎯 WEEKLY GOALS:\n{schedule_data['weekly_goals']}\n\n")
            
            weekly_schedule = schedule_data.get('schedule', {})
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            
            for day in weekdays:
                if day in weekly_schedule:
                    day_schedule = weekly_schedule[day]
                    f.write(f"📅 {day.upper()} ({day_schedule.get('date', '')}) - {day_schedule.get('focus_theme', '')}\n")
                    f.write(f"⏱️ Total: {day_schedule.get('total_hours', 0):.1f} hours\n")
                    f.write("-" * 40 + "\n")
                    
                    for i, task in enumerate(day_schedule.get('tasks', []), 1):
                        priority_icon = "🔥" if task['priority'] >= 16 else "🟡" if task['priority'] >= 12 else "🟢"
                        energy_icon = "⚡" if task['energy_level'] == 'high' else "🔋" if task['energy_level'] == 'medium' else "💤"
                        
                        f.write(f"{i}. {priority_icon} {task['title']}\n")
                        f.write(f"   ⏱️ {task['est_time']}h | 📂 {task['category']} | {energy_icon} {task['energy_level']}\n")
                    
                    f.write("\n")
            
            if 'ai_analysis' in schedule_data:
                f.write("🤖 AI WEEKLY ANALYSIS:\n")
                f.write("=" * 60 + "\n")
                f.write(schedule_data['ai_analysis'])
        
        print(f"✅ Weekly text file exported: {filename}")
    
    def show_system_analytics(self):
        """Show system analytics"""
        self.visual.print_header("📊 SYSTEM ANALYTICS")
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
        completed_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        
        conn.close()
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        print(f"📊 Master Jarvis System Analytics:")
        print(f"   📋 Total tasks created: {total_tasks}")
        print(f"   ✅ Tasks completed: {completed_tasks}")
        print(f"   📈 Completion rate: {completion_rate:.1f}%")
        print(f"   💬 AI conversations: {total_conversations}")
        print(f"   🧠 AI learning active: {'Yes' if CLAUDE_API_KEY else 'Limited (no API key)'}")
        print(f"   🎨 Visual interface: {'Enabled' if VISUAL_AVAILABLE else 'Basic (install colorama)'}")
        
        input("\n📱 Press Enter to continue...")
    
    def manage_preferences(self):
        """Manage user preferences"""
        self.visual.print_header("⚙️ PREFERENCES")
        print("🚧 This feature will be implemented in the next update!")
        input("\n📱 Press Enter to continue...")

if __name__ == "__main__":
    master_jarvis = MasterJarvis()
    master_jarvis.run()