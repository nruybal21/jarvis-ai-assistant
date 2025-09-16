# Complete Enhanced Jarvis - Advanced AI Intelligence
# File: src/enhanced_jarvis.py

import requests
import sqlite3
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add config directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class EnhancedJarvisAI:
    def __init__(self):
        """Initialize Enhanced Jarvis with advanced AI capabilities"""
        self.db_path = "data/enhanced_jarvis.db"
        self.setup_enhanced_database()
        self.conversation_context = []
        print("🧠 Enhanced Jarvis AI - Advanced Intelligence Mode")
        print("💡 Features: Memory, Learning, Pattern Recognition, Career Coaching")
        
    def setup_enhanced_database(self):
        """Setup enhanced database with AI learning tables"""
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                context_data TEXT,
                importance_score INTEGER DEFAULT 5,
                session_id TEXT
            )
        ''')
        
        # Pattern recognition table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence_score REAL,
                usage_count INTEGER DEFAULT 1,
                last_updated TEXT,
                effectiveness_score REAL DEFAULT 5.0
            )
        ''')
        
        # User preferences and goals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_key TEXT UNIQUE NOT NULL,
                profile_value TEXT NOT NULL,
                updated_date TEXT,
                confidence_level REAL DEFAULT 0.8
            )
        ''')
        
        # Task completion tracking for learning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_description TEXT NOT NULL,
                category TEXT,
                estimated_time INTEGER,
                actual_time INTEGER,
                completion_quality INTEGER,
                energy_level TEXT,
                time_of_day INTEGER,
                completion_date TEXT,
                learning_notes TEXT
            )
        ''')
        
        # AI insights and recommendations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                insight_content TEXT NOT NULL,
                supporting_data TEXT,
                confidence_score REAL,
                created_date TEXT,
                applied_date TEXT,
                effectiveness_rating INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def ask_claude_enhanced(self, question, context="", system_prompt="", use_memory=True):
        """Enhanced Claude interaction with memory and context"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {"Content-Type": "application/json"}
        
        # Build comprehensive context if memory is enabled
        if use_memory:
            memory_context = self.get_relevant_memory(question)
            user_profile = self.get_user_profile_context()
            recent_patterns = self.get_recent_patterns()
            
            enhanced_context = f"""
            CONVERSATION MEMORY: {memory_context}
            USER PROFILE: {user_profile}
            RECENT PATTERNS: {recent_patterns}
            CURRENT CONTEXT: {context}
            """
        else:
            enhanced_context = context
        
        if not system_prompt:
            system_prompt = """You are Enhanced Jarvis, an advanced AI assistant with persistent memory and deep learning capabilities. You remember all previous conversations and learn from user patterns to provide increasingly personalized advice.

Your key capabilities:
- Persistent memory across all sessions
- Pattern recognition and learning from user behavior
- Personalized productivity coaching based on historical data
- Career development support for AI Integration Specialist goals
- Context-aware suggestions based on time, energy, and workload
- Emotional intelligence and motivational support

Remember: You have access to conversation history and user patterns. Reference previous discussions naturally and build upon established context. Provide specific, actionable advice that demonstrates your understanding of the user's goals and patterns.

The user is learning AI implementation skills to become an AI Integration Specialist. Support this career development journey with relevant technical insights and industry knowledge."""

        full_prompt = f"""
        {system_prompt}
        
        Enhanced Context: {enhanced_context}
        
        Current User Query: {question}
        
        Provide a response that demonstrates your memory of previous conversations and learning from user patterns. Be specific, helpful, and reference relevant context from our history together.
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
                ai_response = result['content'][0]['text']
                
                # Store conversation in memory
                self.store_conversation(question, ai_response, enhanced_context)
                
                return ai_response
            else:
                return f"AI connection error: {response.status_code}"
        except Exception as e:
            return f"Connection error: {e}"
    
    def store_conversation(self, user_input, ai_response, context):
        """Store conversation with enhanced metadata for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine importance score based on content
        importance = 5
        if any(keyword in user_input.lower() for keyword in ['important', 'career', 'goal', 'problem', 'help', 'learn']):
            importance = 8
        elif any(keyword in user_input.lower() for keyword in ['quick', 'simple', 'just', 'what']):
            importance = 3
        
        session_id = datetime.now().strftime("%Y%m%d")
        
        cursor.execute('''
            INSERT INTO conversations (timestamp, user_input, ai_response, context_data, importance_score, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), user_input, ai_response, context, importance, session_id))
        
        conn.commit()
        conn.close()
        
        # Update conversation context for current session
        self.conversation_context.append({
            'user': user_input,
            'assistant': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 exchanges in memory for performance
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]
    
    def get_relevant_memory(self, query, limit=5):
        """Retrieve relevant conversation history based on query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent high-importance conversations
        cursor.execute('''
            SELECT user_input, ai_response, timestamp FROM conversations 
            WHERE importance_score >= 6
            ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        
        recent_conversations = cursor.fetchall()
        
        # Format for context
        memory_summary = []
        for user_input, ai_response, timestamp in recent_conversations:
            dt = datetime.fromisoformat(timestamp)
            memory_summary.append(f"[{dt.strftime('%m/%d')}] User: {user_input[:100]}... Assistant: {ai_response[:100]}...")
        
        conn.close()
        return "\n".join(memory_summary) if memory_summary else "No relevant memory found."
    
    def get_user_profile_context(self):
        """Get user profile and preferences for context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT profile_key, profile_value FROM user_profile ORDER BY updated_date DESC')
        profile_data = cursor.fetchall()
        
        if not profile_data:
            # Initialize basic profile
            self.update_user_profile("career_goal", "AI Integration Specialist")
            self.update_user_profile("learning_focus", "AI implementation and Python development")
            profile_data = [("career_goal", "AI Integration Specialist"), ("learning_focus", "AI implementation and Python development")]
        
        conn.close()
        
        profile_summary = "; ".join([f"{key}: {value}" for key, value in profile_data])
        return profile_summary
    
    def update_user_profile(self, key, value):
        """Update user profile information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profile (profile_key, profile_value, updated_date)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_recent_patterns(self):
        """Get recent learning patterns for context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_type, pattern_data, confidence_score FROM learning_patterns 
            WHERE last_updated > date('now', '-30 days')
            ORDER BY confidence_score DESC LIMIT 3
        ''')
        
        patterns = cursor.fetchall()
        conn.close()
        
        if patterns:
            pattern_summary = "; ".join([f"{pattern_type}: {json.loads(pattern_data)['summary']}" for pattern_type, pattern_data, _ in patterns])
            return pattern_summary
        return "No recent patterns identified."
    
    def record_task_completion(self, task_description, category, estimated_minutes, actual_minutes, quality_rating=5):
        """Record task completion for pattern learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_hour = datetime.now().hour
        
        # Determine energy level based on time of day
        if 6 <= current_hour <= 10:
            energy_level = "high"
        elif 11 <= current_hour <= 14:
            energy_level = "medium-high"
        elif 15 <= current_hour <= 17:
            energy_level = "medium"
        elif 18 <= current_hour <= 21:
            energy_level = "medium-low"
        else:
            energy_level = "low"
        
        cursor.execute('''
            INSERT INTO task_completions 
            (task_description, category, estimated_time, actual_time, completion_quality, 
             energy_level, time_of_day, completion_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_description, category, estimated_minutes, actual_minutes, quality_rating, 
              energy_level, current_hour, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Generate learning insight
        variance = actual_minutes - estimated_minutes
        variance_percent = (variance / estimated_minutes) * 100 if estimated_minutes > 0 else 0
        
        print(f"✅ Task completion recorded!")
        print(f"📊 Time variance: {variance:+d} minutes ({variance_percent:+.1f}%)")
        print(f"⚡ Energy level: {energy_level}")
        print(f"🏆 Quality rating: {quality_rating}/10")
        
        # Update patterns if significant variance
        if abs(variance_percent) > 20:
            self.update_learning_pattern("time_estimation", {
                "category": category,
                "typical_variance": variance_percent,
                "energy_level": energy_level,
                "summary": f"{category} tasks at {energy_level} energy typically {variance_percent:+.1f}% vs estimate"
            })
    
    def update_learning_pattern(self, pattern_type, pattern_data):
        """Update or create learning patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if pattern exists
        cursor.execute('SELECT id, usage_count FROM learning_patterns WHERE pattern_type = ?', (pattern_type,))
        existing = cursor.fetchone()
        
        if existing:
            pattern_id, usage_count = existing
            cursor.execute('''
                UPDATE learning_patterns 
                SET pattern_data = ?, usage_count = ?, last_updated = ?
                WHERE id = ?
            ''', (json.dumps(pattern_data, cls=DateTimeEncoder), usage_count + 1, datetime.now().isoformat(), pattern_id))
        else:
            cursor.execute('''
                INSERT INTO learning_patterns (pattern_type, pattern_data, last_updated)
                VALUES (?, ?, ?)
            ''', (pattern_type, json.dumps(pattern_data, cls=DateTimeEncoder), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def analyze_productivity_patterns(self):
        """Analyze productivity patterns and generate insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get task completion data
        cursor.execute('''
            SELECT category, energy_level, time_of_day, AVG(actual_time), AVG(completion_quality),
                   COUNT(*) as task_count
            FROM task_completions 
            WHERE completion_date > date('now', '-30 days')
            GROUP BY category, energy_level, time_of_day
            HAVING task_count >= 2
            ORDER BY AVG(completion_quality) DESC
        ''')
        
        patterns = cursor.fetchall()
        
        if not patterns:
            return "📊 Not enough data yet. Complete more tasks to see patterns!"
        
        analysis = ["🧠 PRODUCTIVITY PATTERN ANALYSIS", "=" * 40]
        
        # Best performance analysis
        best_pattern = patterns[0]
        category, energy, hour, avg_time, avg_quality, count = best_pattern
        
        analysis.append(f"\n🏆 OPTIMAL PERFORMANCE ZONE:")
        analysis.append(f"   Category: {category}")
        analysis.append(f"   Energy Level: {energy}")
        analysis.append(f"   Time of Day: {hour}:00")
        analysis.append(f"   Average Quality: {avg_quality:.1f}/10")
        analysis.append(f"   Sample Size: {count} tasks")
        
        # Energy level insights
        cursor.execute('''
            SELECT energy_level, AVG(completion_quality), COUNT(*)
            FROM task_completions 
            WHERE completion_date > date('now', '-30 days')
            GROUP BY energy_level
            ORDER BY AVG(completion_quality) DESC
        ''')
        
        energy_patterns = cursor.fetchall()
        
        analysis.append(f"\n⚡ ENERGY LEVEL PERFORMANCE:")
        for energy, quality, count in energy_patterns:
            analysis.append(f"   {energy.title()}: {quality:.1f}/10 quality ({count} tasks)")
        
        # Time estimation accuracy
        cursor.execute('''
            SELECT category, 
                   AVG(actual_time - estimated_time) as avg_variance,
                   COUNT(*) as task_count
            FROM task_completions 
            WHERE completion_date > date('now', '-30 days') AND estimated_time > 0
            GROUP BY category
            ORDER BY ABS(AVG(actual_time - estimated_time))
        ''')
        
        estimation_accuracy = cursor.fetchall()
        
        analysis.append(f"\n⏱️  TIME ESTIMATION ACCURACY:")
        for category, variance, count in estimation_accuracy:
            accuracy = "excellent" if abs(variance) < 10 else "good" if abs(variance) < 20 else "needs improvement"
            analysis.append(f"   {category}: {variance:+.1f} min avg variance ({accuracy})")
        
        conn.close()
        
        return "\n".join(analysis)
    
    def get_personalized_insights(self):
        """Generate personalized insights based on user data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent activity summary
        cursor.execute('''
            SELECT COUNT(*) FROM conversations 
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        recent_conversations = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM task_completions 
            WHERE completion_date > date('now', '-7 days')
        ''')
        recent_completions = cursor.fetchone()[0]
        
        # Get learning progress indicators
        cursor.execute('''
            SELECT pattern_type, COUNT(*) FROM learning_patterns 
            GROUP BY pattern_type
        ''')
        pattern_counts = cursor.fetchall()
        
        conn.close()
        
        insights = [
            f"📈 PERSONALIZED AI INSIGHTS",
            f"=" * 40,
            f"🗣️  Recent Activity: {recent_conversations} conversations this week",
            f"✅ Task Completions: {recent_completions} tasks completed",
            f"🧠 Learning Patterns: {len(pattern_counts)} pattern types identified",
            f"",
            f"💡 AI is learning your preferences and optimizing recommendations",
            f"🎯 Continue using Enhanced Jarvis to unlock more personalized insights"
        ]
        
        return "\n".join(insights)
    
    def intelligent_conversation(self):
        """Main conversation interface with enhanced capabilities"""
        print("\n💬 ENHANCED AI CONVERSATION MODE")
        print("🧠 I remember our previous conversations and learn from your patterns!")
        print("💡 Try: 'analyze my patterns', 'what should I focus on?', 'how am I improving?'")
        print("📝 Commands: 'record completion', 'my insights', 'my patterns', 'help', 'conversations'")
        print("🚪 Exit: Type 'quit', 'exit', or 'back' to return")
        
        while True:
            print("\n" + "-" * 50)
            user_input = input("🎤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'back', 'bye']:
                print("🤖 Conversation saved! I'll remember everything for next time.")
                break
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() == 'help':
                print("🆘 ENHANCED JARVIS COMMANDS:")
                print("• 'analyze my patterns' - Deep productivity analysis")
                print("• 'record completion [task] [category] [estimated] [actual] [quality]' - Track task")
                print("• 'my insights' - Personalized AI insights")
                print("• 'my patterns' - View learning patterns")
                print("• 'conversations' - View recent conversation history")
                print("• 'focus suggestions' - Get context-aware recommendations")
                print("• General conversation - Ask anything about productivity, career, AI!")
                continue
            
            if user_input.lower().startswith('record completion'):
                # Parse task completion command
                parts = user_input.split(' ', 2)
                if len(parts) >= 3:
                    try:
                        # Simple parsing - could be enhanced with NLP
                        task_desc = input("📝 Task description: ")
                        category = input("📂 Category: ") or "General"
                        estimated = int(input("⏱️  Estimated minutes: "))
                        actual = int(input("⏲️  Actual minutes: "))
                        quality = int(input("🏆 Quality rating (1-10): "))
                        
                        self.record_task_completion(task_desc, category, estimated, actual, quality)
                    except ValueError:
                        print("❌ Please enter valid numbers for time and quality.")
                else:
                    print("💡 Usage: record completion")
                continue
            
            if user_input.lower() in ['my patterns', 'analyze patterns', 'analyze my patterns']:
                analysis = self.analyze_productivity_patterns()
                print(f"\n{analysis}")
                continue
            
            if user_input.lower() in ['my insights', 'insights']:
                insights = self.get_personalized_insights()
                print(f"\n{insights}")
                continue
            
            if user_input.lower() == 'conversations':
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, user_input, ai_response FROM conversations 
                    ORDER BY timestamp DESC LIMIT 5
                ''')
                recent = cursor.fetchall()
                conn.close()
                
                print("\n📚 RECENT CONVERSATION HISTORY:")
                for timestamp, user_q, ai_resp in recent:
                    dt = datetime.fromisoformat(timestamp)
                    print(f"\n[{dt.strftime('%m/%d %H:%M')}]")
                    print(f"You: {user_q[:80]}...")
                    print(f"AI: {ai_resp[:80]}...")
                continue
            
            # Regular AI conversation with memory
            print("🤖 Thinking with full context and memory...")
            response = self.ask_claude_enhanced(user_input)
            print(f"\n🧠 Enhanced Jarvis: {response}")

def main():
    """Main Enhanced Jarvis application"""
    enhanced_jarvis = EnhancedJarvisAI()
    
    # Welcome message with personalization
    print("\n🌟 Welcome back to Enhanced Jarvis!")
    
    # Check for existing conversation history
    conn = sqlite3.connect(enhanced_jarvis.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM conversations')
    conversation_count = cursor.fetchone()[0]
    
    if conversation_count > 0:
        print(f"💭 I remember our {conversation_count} previous conversations!")
        cursor.execute('SELECT user_input FROM conversations ORDER BY timestamp DESC LIMIT 1')
        last_conversation = cursor.fetchone()
        if last_conversation:
            print(f"💡 Last time we discussed: {last_conversation[0][:60]}...")
    else:
        print("🆕 This is our first conversation! I'm excited to learn about you.")
        # Set up initial profile
        enhanced_jarvis.update_user_profile("first_session", datetime.now().isoformat())
    
    conn.close()
    
    while True:
        print("\n" + "="*60)
        print("🧠 ENHANCED JARVIS AI - ADVANCED INTELLIGENCE")
        print("="*60)
        print("1. 💬 Intelligent Conversation (with Memory)")
        print("2. 📊 Analyze My Productivity Patterns")
        print("3. 💡 Get Personalized Insights") 
        print("4. 📝 Record Task Completion")
        print("5. 📚 View Conversation History")
        print("6. 🎯 Update Goals & Preferences")
        print("7. 🔄 Back to Basic Jarvis")
        print("8. ❌ Exit Enhanced Mode")
        print("="*60)
        
        choice = input("🎯 Choose an option (1-8): ").strip()
        
        if choice == "1":
            enhanced_jarvis.intelligent_conversation()
            
        elif choice == "2":
            print("\n📊 PRODUCTIVITY PATTERN ANALYSIS")
            print("-" * 40)
            analysis = enhanced_jarvis.analyze_productivity_patterns()
            print(analysis)
            
        elif choice == "3":
            print("\n💡 PERSONALIZED INSIGHTS")
            print("-" * 40)
            insights = enhanced_jarvis.get_personalized_insights()
            print(insights)
            
        elif choice == "4":
            print("\n📝 RECORD TASK COMPLETION")
            print("-" * 40)
            try:
                task_desc = input("📋 Task description: ").strip()
                if task_desc:
                    category = input("📂 Category (work/personal/learning): ").strip() or "General"
                    estimated = int(input("⏱️  Estimated time (minutes): "))
                    actual = int(input("⏲️  Actual time (minutes): "))
                    quality = int(input("🏆 Quality rating (1-10): "))
                    
                    enhanced_jarvis.record_task_completion(task_desc, category, estimated, actual, quality)
                else:
                    print("❌ Task description required.")
            except ValueError:
                print("❌ Please enter valid numbers.")
                
        elif choice == "5":
            print("\n📚 CONVERSATION HISTORY")
            print("-" * 40)
            conn = sqlite3.connect(enhanced_jarvis.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, user_input, ai_response, importance_score FROM conversations 
                ORDER BY timestamp DESC LIMIT 10
            ''')
            conversations = cursor.fetchall()
            conn.close()
            
            if conversations:
                for timestamp, user_input, ai_response, importance in conversations:
                    dt = datetime.fromisoformat(timestamp)
                    importance_icon = "🔥" if importance >= 8 else "⭐" if importance >= 6 else "💬"
                    print(f"\n{importance_icon} [{dt.strftime('%m/%d %H:%M')}] Importance: {importance}/10")
                    print(f"You: {user_input[:100]}...")
                    print(f"AI: {ai_response[:100]}...")
                    print("-" * 40)
            else:
                print("📝 No conversation history yet. Start chatting to build memory!")
                
        elif choice == "6":
            print("\n🎯 UPDATE GOALS & PREFERENCES")
            print("-" * 40)
            print("Current focus: AI Integration Specialist career development")
            new_goal = input("🎯 Update career goal (or press Enter to keep current): ").strip()
            if new_goal:
                enhanced_jarvis.update_user_profile("career_goal", new_goal)
                print(f"✅ Updated career goal: {new_goal}")
            
            new_focus = input("📚 Update learning focus (or press Enter to skip): ").strip()
            if new_focus:
                enhanced_jarvis.update_user_profile("learning_focus", new_focus)
                print(f"✅ Updated learning focus: {new_focus}")
                
        elif choice == "7":
            print("\n🔄 Switching to Basic Jarvis...")
            print("💡 Run: python src/basic_jarvis.py")
            break
            
        elif choice == "8":
            print("\n🧠 Enhanced Jarvis session complete!")
            print("💭 All conversations and learning saved for next time.")
            print("🚀 Your AI assistant gets smarter with every interaction!")
            break
            
        else:
            print("❌ Invalid option. Please choose 1-8.")
        
        if choice not in ["7", "8"]:
            input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    main()