# Enhanced Jarvis - Advanced AI Intelligence
# File: src/enhanced_jarvis.py

import anthropic
import sqlite3
import json
import sys
import os
from datetime import datetime, timedelta
import re

# Add config directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.credentials import CLAUDE_API_KEY

class EnhancedJarvis:
    """
    Enhanced AI Assistant with Advanced Learning and Memory
    
    New AI Implementation Concepts:
    - Cross-Session Memory: AI remembers conversations between sessions
    - Pattern Learning: AI learns your productivity patterns over time
    - Contextual Intelligence: AI provides increasingly personalized responses
    - Predictive Insights: AI anticipates your needs based on patterns
    - Advanced Analytics: AI analyzes your productivity for optimization
    """
    
    def __init__(self):
        """Initialize Enhanced Jarvis with advanced AI capabilities"""
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        self.db_path = os.path.join('data', 'enhanced_jarvis.db')
        self.setup_enhanced_database()
        self.conversation_context = []
        
    def setup_enhanced_database(self):
        """Create enhanced database for AI learning and memory"""
        os.makedirs('data', exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conversation memory for cross-session learning
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP,
                    user_input TEXT,
                    ai_response TEXT,
                    context_type TEXT,
                    importance_score INTEGER,
                    learning_tags TEXT
                )
            ''')
            
            # Productivity patterns learned by AI
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productivity_patterns (
                    id INTEGER PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    confidence_score REAL,
                    usage_count INTEGER,
                    last_updated TIMESTAMP,
                    validation_score REAL
                )
            ''')
            
            # AI-generated insights and recommendations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_insights (
                    id INTEGER PRIMARY KEY,
                    insight_category TEXT,
                    insight_text TEXT,
                    supporting_data TEXT,
                    confidence REAL,
                    acted_upon BOOLEAN DEFAULT FALSE,
                    effectiveness_rating INTEGER,
                    created_date TIMESTAMP
                )
            ''')
            
            # Task completion analytics for AI learning
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_analytics (
                    id INTEGER PRIMARY KEY,
                    task_description TEXT,
                    task_category TEXT,
                    estimated_duration INTEGER,
                    actual_duration INTEGER,
                    completion_quality INTEGER,
                    energy_level TEXT,
                    time_of_day TEXT,
                    interruption_count INTEGER,
                    completion_date TIMESTAMP,
                    ai_prediction_accuracy REAL
                )
            ''')
            
            # User preferences learned by AI
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learned_preferences (
                    id INTEGER PRIMARY KEY,
                    preference_type TEXT,
                    preference_value TEXT,
                    confidence REAL,
                    supporting_evidence TEXT,
                    last_confirmed TIMESTAMP
                )
            ''')
            
            conn.commit()
            print("✅ Enhanced AI intelligence database initialized!")
    
    def intelligent_conversation(self, user_input):
        """
        Advanced AI conversation with memory and learning
        
        This demonstrates how enterprise AI systems maintain context
        and provide increasingly intelligent responses.
        """
        try:
            # Retrieve relevant memories and patterns
            relevant_memories = self.get_relevant_memories(user_input)
            user_patterns = self.get_user_patterns()
            recent_insights = self.get_recent_insights()
            
            # Build comprehensive context for AI
            context_prompt = self.build_intelligent_context(
                user_input, relevant_memories, user_patterns, recent_insights
            )
            
            # Get AI response with enhanced context
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1200,
                messages=[{"role": "user", "content": context_prompt}]
            )
            
            ai_response = response.content[0].text
            
            # Learn from this interaction
            self.learn_from_conversation(user_input, ai_response)
            
            # Add to current conversation context
            self.conversation_context.append({
                'user': user_input,
                'assistant': ai_response,
                'timestamp': datetime.now()
            })
            
            return ai_response
            
        except Exception as e:
            return f"❌ AI conversation error: {str(e)}"
    
    def build_intelligent_context(self, user_input, memories, patterns, insights):
        """Build comprehensive context for intelligent AI responses"""
        
        context = f"""You are Jarvis, an advanced AI productivity assistant with enhanced intelligence and memory.

CURRENT USER INPUT: {user_input}

RELEVANT CONVERSATION MEMORIES:
{json.dumps(memories[:3], indent=2) if memories else "No relevant memories found"}

USER'S PRODUCTIVITY PATTERNS:
{json.dumps(patterns, indent=2) if patterns else "Learning user patterns..."}

RECENT AI INSIGHTS:
{json.dumps(insights[:2], indent=2) if insights else "No recent insights"}

CURRENT CONVERSATION CONTEXT:
{json.dumps(self.conversation_context[-3:], indent=2) if self.conversation_context else "New conversation"}

ENHANCED AI CAPABILITIES:
- You remember conversations across sessions
- You learn from user's productivity patterns
- You provide increasingly personalized advice
- You anticipate user needs based on learned patterns
- You offer proactive suggestions for optimization

RESPONSE GUIDELINES:
1. Use memory and patterns to provide personalized advice
2. Reference relevant past conversations when helpful
3. Suggest optimizations based on learned patterns
4. Be proactive with insights and recommendations
5. Ask clarifying questions to learn more about the user
6. Provide actionable, specific advice
7. Acknowledge growth and learning progress

Respond as an intelligent AI assistant that genuinely understands and learns from the user."""

        return context
    
    def get_relevant_memories(self, current_input):
        """Retrieve conversation memories relevant to current input"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get memories with high importance scores
            cursor.execute('''
                SELECT user_input, ai_response, context_type, learning_tags, timestamp
                FROM conversation_memory 
                WHERE importance_score >= 7
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            
            memories = cursor.fetchall()
            
            # Simple relevance scoring based on keyword overlap
            relevant_memories = []
            input_words = set(current_input.lower().split())
            
            for memory in memories:
                user_input, ai_response, context_type, learning_tags, timestamp = memory
                memory_words = set((user_input + " " + ai_response).lower().split())
                
                # Calculate relevance score
                overlap = len(input_words.intersection(memory_words))
                if overlap > 1:  # At least 2 words in common
                    relevant_memories.append({
                        'user_input': user_input,
                        'ai_response': ai_response[:200] + "...",  # Truncate for context
                        'context_type': context_type,
                        'relevance_score': overlap,
                        'timestamp': timestamp
                    })
            
            # Sort by relevance
            relevant_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
            return relevant_memories[:5]
    
    def get_user_patterns(self):
        """Get learned productivity patterns"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT pattern_type, pattern_data, confidence_score, usage_count
                FROM productivity_patterns 
                WHERE confidence_score > 0.6
                ORDER BY confidence_score DESC
                LIMIT 5
            ''')
            
            patterns = cursor.fetchall()
            
            return [
                {
                    'type': row[0],
                    'data': json.loads(row[1]) if row[1] else {},
                    'confidence': row[2],
                    'usage_count': row[3]
                } for row in patterns
            ]
    
    def get_recent_insights(self):
        """Get recent AI-generated insights"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT insight_category, insight_text, confidence, effectiveness_rating
                FROM ai_insights 
                WHERE created_date >= date('now', '-7 days')
                ORDER BY confidence DESC
                LIMIT 3
            ''')
            
            insights = cursor.fetchall()
            
            return [
                {
                    'category': row[0],
                    'insight': row[1],
                    'confidence': row[2],
                    'effectiveness': row[3]
                } for row in insights
            ]
    
    def learn_from_conversation(self, user_input, ai_response):
        """Learn and store insights from conversations"""
        # Determine conversation importance and context
        importance = self.assess_conversation_importance(user_input, ai_response)
        context_type = self.categorize_conversation_context(user_input)
        learning_tags = self.extract_learning_tags(user_input, ai_response)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversation_memory
                (timestamp, user_input, ai_response, context_type, importance_score, learning_tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now(), user_input, ai_response, context_type, importance, 
                  json.dumps(learning_tags)))
            
            conn.commit()
    
    def assess_conversation_importance(self, user_input, ai_response):
        """Assess the importance of a conversation for learning"""
        importance = 5  # Base importance
        
        # High importance indicators
        high_importance_keywords = [
            'goal', 'deadline', 'priority', 'important', 'urgent', 
            'project', 'meeting', 'presentation', 'learning', 'improve'
        ]
        
        # Medium importance indicators
        medium_importance_keywords = [
            'schedule', 'plan', 'organize', 'task', 'work', 'productivity'
        ]
        
        user_lower = user_input.lower()
        
        for keyword in high_importance_keywords:
            if keyword in user_lower:
                importance += 2
        
        for keyword in medium_importance_keywords:
            if keyword in user_lower:
                importance += 1
        
        # Cap at 10
        return min(importance, 10)
    
    def categorize_conversation_context(self, user_input):
        """Categorize the type of conversation for better organization"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['schedule', 'plan', 'calendar', 'time']):
            return 'scheduling'
        elif any(word in user_lower for word in ['task', 'work', 'project', 'deadline']):
            return 'task_management'
        elif any(word in user_lower for word in ['learn', 'study', 'course', 'skill']):
            return 'learning'
        elif any(word in user_lower for word in ['goal', 'improve', 'optimize', 'better']):
            return 'optimization'
        elif any(word in user_lower for word in ['meeting', 'presentation', 'client']):
            return 'meeting_prep'
        else:
            return 'general'
    
    def extract_learning_tags(self, user_input, ai_response):
        """Extract learning tags from conversation"""
        tags = []
        
        # Extract entities and keywords
        combined_text = (user_input + " " + ai_response).lower()
        
        # Time-related tags
        time_keywords = ['morning', 'afternoon', 'evening', 'daily', 'weekly']
        for keyword in time_keywords:
            if keyword in combined_text:
                tags.append(f"time:{keyword}")
        
        # Activity tags
        activity_keywords = ['coding', 'meeting', 'email', 'presentation', 'learning', 'planning']
        for keyword in activity_keywords:
            if keyword in combined_text:
                tags.append(f"activity:{keyword}")
        
        # Goal tags
        goal_keywords = ['productivity', 'efficiency', 'organization', 'learning', 'career']
        for keyword in goal_keywords:
            if keyword in combined_text:
                tags.append(f"goal:{keyword}")
        
        return tags
    
    def analyze_productivity_patterns(self):
        """Advanced AI analysis of productivity patterns"""
        try:
            print("\n🧠 AI analyzing your productivity patterns...")
            
            # Get task completion data
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if we have task analytics data
                cursor.execute('SELECT COUNT(*) FROM task_analytics')
                task_count = cursor.fetchone()[0]
                
                if task_count < 5:
                    return self.generate_starter_insights()
                
                cursor.execute('''
                    SELECT task_category, estimated_duration, actual_duration,
                           completion_quality, energy_level, time_of_day,
                           interruption_count, completion_date
                    FROM task_analytics 
                    WHERE completion_date >= date('now', '-30 days')
                ''')
                
                analytics_data = cursor.fetchall()
            
            # Get conversation patterns
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT context_type, COUNT(*) as frequency, learning_tags
                    FROM conversation_memory
                    WHERE timestamp >= date('now', '-14 days')
                    GROUP BY context_type
                    ORDER BY frequency DESC
                ''')
                
                conversation_patterns = cursor.fetchall()
            
            # Create comprehensive analysis prompt
            analysis_prompt = f"""
            Analyze this user's productivity and conversation patterns to generate intelligent insights:
            
            TASK COMPLETION DATA:
            {json.dumps(analytics_data, indent=2)}
            
            CONVERSATION PATTERNS:
            {json.dumps(conversation_patterns, indent=2)}
            
            ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d')}
            
            Provide comprehensive productivity analysis in JSON format:
            {{
                "overall_assessment": {{
                    "productivity_score": 1-10,
                    "efficiency_trend": "improving|stable|declining",
                    "strongest_areas": ["area1", "area2"],
                    "improvement_opportunities": ["opportunity1", "opportunity2"]
                }},
                "time_management_insights": {{
                    "optimal_work_times": ["time periods when most productive"],
                    "energy_patterns": ["observations about energy throughout day"],
                    "time_estimation_accuracy": "how good at estimating task duration",
                    "interruption_management": "patterns with interruptions"
                }},
                "personalized_recommendations": [
                    "specific actionable recommendation based on patterns",
                    "another personalized suggestion",
                    "optimization opportunity"
                ],
                "learning_progress": {{
                    "ai_usage_patterns": "how user is engaging with AI assistant",
                    "skill_development": "progress in productivity/organization skills",
                    "system_adoption": "how well using the AI system"
                }},
                "predictive_insights": [
                    "prediction about future productivity patterns",
                    "anticipated challenges and how to address them"
                ]
            }}
            
            Focus on actionable insights that help improve productivity and AI system usage.
            """
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            ai_analysis = response.content[0].text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_analysis, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                
                # Store insights in database
                self.store_ai_insights(analysis)
                
                return self.format_productivity_analysis(analysis)
            else:
                return "Analysis completed but couldn't parse results. Raw insights:\n" + ai_analysis
                
        except Exception as e:
            return f"❌ Error in pattern analysis: {str(e)}"
    
    def generate_starter_insights(self):
        """Generate insights for new users with limited data"""
        return """
🧠 AI PRODUCTIVITY ANALYSIS - STARTER INSIGHTS
===============================================

📊 Current Status: Building AI Learning Foundation
Your AI assistant is in the early learning phase. Keep using the system daily for increasingly personalized insights!

💡 Getting Started Recommendations:
   • Use detailed task descriptions for better AI learning
   • Record actual completion times to improve predictions
   • Try the daily check-in feature to establish patterns
   • Be consistent with task categorization

🎯 Next Steps:
   • Continue using the system for 1-2 weeks
   • Focus on entering 5-8 tasks daily
   • Provide feedback on time estimates and scheduling
   • Use the calendar export feature to integrate with your workflow

📈 What to Expect:
After 1-2 weeks of consistent usage, you'll start seeing:
   • More accurate time predictions
   • Personalized scheduling suggestions
   • Pattern recognition in your productivity
   • Proactive optimization recommendations

Keep building your AI training data! The system gets smarter with every interaction.
"""
    
    def store_ai_insights(self, analysis):
        """Store AI-generated insights for future reference"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store overall assessment
            overall = analysis.get('overall_assessment', {})
            cursor.execute('''
                INSERT INTO ai_insights 
                (insight_category, insight_text, supporting_data, confidence, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', ('overall_assessment', 
                  f"Productivity score: {overall.get('productivity_score', 'N/A')}/10. {overall.get('efficiency_trend', 'Unknown')} trend.",
                  json.dumps(overall),
                  0.8,
                  datetime.now()))
            
            # Store recommendations
            recommendations = analysis.get('personalized_recommendations', [])
            for rec in recommendations:
                cursor.execute('''
                    INSERT INTO ai_insights 
                    (insight_category, insight_text, supporting_data, confidence, created_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('recommendation', rec, json.dumps(analysis), 0.7, datetime.now()))
            
            conn.commit()
    
    def format_productivity_analysis(self, analysis):
        """Format AI analysis into readable output"""
        output = "\n🧠 AI PRODUCTIVITY ANALYSIS\n" + "="*50 + "\n"
        
        # Overall Assessment
        overall = analysis.get('overall_assessment', {})
        if overall:
            output += "📊 OVERALL ASSESSMENT:\n"
            output += f"   Productivity Score: {overall.get('productivity_score', 'N/A')}/10\n"
            output += f"   Efficiency Trend: {overall.get('efficiency_trend', 'Unknown')}\n"
            
            strongest = overall.get('strongest_areas', [])
            if strongest:
                output += "   Strongest Areas:\n"
                for area in strongest:
                    output += f"      • {area}\n"
            
            improvements = overall.get('improvement_opportunities', [])
            if improvements:
                output += "   Improvement Opportunities:\n"
                for opp in improvements:
                    output += f"      • {opp}\n"
            output += "\n"
        
        # Time Management Insights
        time_insights = analysis.get('time_management_insights', {})
        if time_insights:
            output += "⏰ TIME MANAGEMENT INSIGHTS:\n"
            for key, value in time_insights.items():
                key_formatted = key.replace('_', ' ').title()
                if isinstance(value, list):
                    output += f"   {key_formatted}:\n"
                    for item in value:
                        output += f"      • {item}\n"
                else:
                    output += f"   {key_formatted}: {value}\n"
            output += "\n"
        
        # Recommendations
        recommendations = analysis.get('personalized_recommendations', [])
        if recommendations:
            output += "💡 PERSONALIZED RECOMMENDATIONS:\n"
            for rec in recommendations:
                output += f"   • {rec}\n"
            output += "\n"
        
        # Learning Progress
        learning = analysis.get('learning_progress', {})
        if learning:
            output += "📚 LEARNING PROGRESS:\n"
            for key, value in learning.items():
                key_formatted = key.replace('_', ' ').title()
                output += f"   {key_formatted}: {value}\n"
            output += "\n"
        
        # Predictive Insights
        predictive = analysis.get('predictive_insights', [])
        if predictive:
            output += "🔮 PREDICTIVE INSIGHTS:\n"
            for insight in predictive:
                output += f"   • {insight}\n"
        
        return output
    
    def record_task_completion(self, task_description, category, estimated_min, 
                             actual_min, quality_rating, energy_level):
        """Record task completion for AI learning"""
        now = datetime.now()
        hour = now.hour
        
        time_of_day = (
            "morning" if hour < 12 else 
            "afternoon" if hour < 17 else 
            "evening"
        )
        
        # Simple interruption estimation based on duration variance
        duration_variance = abs(actual_min - estimated_min)
        interruption_estimate = min(duration_variance // 15, 5)  # Rough estimate
        
        # Calculate AI prediction accuracy
        accuracy = 1.0 - min(duration_variance / max(estimated_min, 1), 1.0)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO task_analytics
                (task_description, task_category, estimated_duration, actual_duration,
                 completion_quality, energy_level, time_of_day, interruption_count,
                 completion_date, ai_prediction_accuracy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (task_description, category, estimated_min, actual_min,
                  quality_rating, energy_level, time_of_day, interruption_estimate,
                  now, accuracy))
            
            conn.commit()
        
        return "✅ Task completion recorded! AI is learning from your patterns."

def main():
    """Main function for Enhanced Jarvis"""
    print("🧠 Enhanced Jarvis AI Assistant - Advanced Intelligence Mode")
    print("="*65)
    print("🚀 NEW ADVANCED CAPABILITIES:")
    print("   • Cross-session memory - Remembers all conversations")
    print("   • Pattern learning - Learns your productivity patterns")
    print("   • Contextual intelligence - Increasingly personalized responses")
    print("   • Advanced analytics - Deep insights into your productivity")
    print("   • Predictive suggestions - Anticipates your needs")
    print("\n💬 ENHANCED COMMANDS:")
    print("   'analyze patterns' - Advanced AI productivity analysis")
    print("   'record completion' - Log completed task for AI learning")
    print("   'my patterns' - View learned productivity patterns")
    print("   'insights' - Recent AI-generated insights")
    print("   'quit' - Exit")
    print("   Or just chat naturally - I remember everything!")
    print("="*65)
    
    jarvis = EnhancedJarvis()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Enhanced Jarvis is powering down but remembers everything for next time!")
                break
            
            elif user_input.lower() == 'analyze patterns':
                analysis = jarvis.analyze_productivity_patterns()
                print(analysis)
            
            elif user_input.lower() == 'record completion':
                print("\n📝 Recording completed task for AI learning:")
                description = input("Task description: ")
                category = input("Category (work/learning/personal/admin): ")
                estimated = int(input("Estimated time (minutes): "))
                actual = int(input("Actual time (minutes): "))
                quality = int(input("Completion quality (1-10): "))
                energy = input("Energy level (high/medium/low): ")
                
                result = jarvis.record_task_completion(
                    description, category, estimated, actual, quality, energy
                )
                print(result)
            
            elif user_input.lower() == 'my patterns':
                patterns = jarvis.get_user_patterns()
                if patterns:
                    print("\n📊 Your Learned Productivity Patterns:")
                    for pattern in patterns:
                        print(f"   • {pattern['type']}: {pattern['confidence']:.1%} confidence")
                else:
                    print("📊 Still learning your patterns. Use the system more to see insights!")
            
            elif user_input.lower() == 'insights':
                insights = jarvis.get_recent_insights()
                if insights:
                    print("\n💡 Recent AI Insights:")
                    for insight in insights:
                        print(f"   • {insight['category']}: {insight['insight']}")
                else:
                    print("💡 No recent insights. Keep using the system to generate AI insights!")
            
            else:
                print("\n🤖 Enhanced Jarvis: ", end="")
                response = jarvis.intelligent_conversation(user_input)
                print(response)
                
        except KeyboardInterrupt:
            print("\n👋 Enhanced Jarvis is powering down but remembers everything for next time!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()