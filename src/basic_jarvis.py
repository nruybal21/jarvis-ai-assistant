# src/basic_jarvis.py
import anthropic
import json
import sys
import os
from datetime import datetime

# Import our credentials
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.credentials import CLAUDE_API_KEY

class BasicJarvis:
    """
    Your first AI assistant with basic intelligence
    """
    
    def __init__(self):
        """Initialize Jarvis with Claude connection"""
        print("🤖 Initializing Jarvis AI Assistant...")
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        self.name = "Jarvis"
        print(f"✅ {self.name} is ready to assist!")
    
    def analyze_task(self, user_input):
        """
        Take a user's task request and analyze it intelligently
        """
        print(f"🧠 Analyzing task: '{user_input}'")
        
        # Create a detailed prompt for Claude
        prompt = f"""
        You are Jarvis, a personal AI assistant. Analyze this task request and provide structured insights.
        
        User's request: "{user_input}"
        Current time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}
        
        Please respond with a JSON object containing:
        {{
            "task_name": "A clear, specific task title",
            "category": "work/personal/learning/health/admin",
            "estimated_duration": 30,
            "priority": "high/medium/low",
            "best_time": "suggested time of day with reasoning",
            "preparation": ["what to prepare or gather beforehand"],
            "steps": ["break the task into 2-3 specific steps"],
            "success_criteria": "how to know when this task is complete"
        }}
        
        Make suggestions practical and helpful for someone learning AI while managing work responsibilities.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse Claude's JSON response
            analysis = json.loads(response.content[0].text)
            return analysis
            
        except json.JSONDecodeError:
            print("⚠️  Claude didn't return valid JSON. Here's the raw response:")
            print(response.content[0].text)
            return None
        except Exception as e:
            print(f"❌ Error analyzing task: {str(e)}")
            return None
    
    def suggest_schedule(self, tasks_list):
        """
        Take a list of tasks and suggest an optimal schedule
        """
        print(f"📅 Creating optimal schedule for {len(tasks_list)} tasks...")
        
        # Prepare the task list for Claude
        tasks_text = "\n".join([f"- {task}" for task in tasks_list])
        
        prompt = f"""
        You are Jarvis, a scheduling assistant. Create an optimal daily schedule for these tasks:
        
        Tasks to schedule:
        {tasks_text}
        
        Current time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}
        
        Consider:
        - Energy levels throughout the day (high in morning, dip after lunch)
        - Logical task sequencing
        - Buffer time between tasks
        - Realistic time estimates
        
        Respond with a JSON schedule:
        {{
            "schedule": [
                {{
                    "time": "9:00 AM",
                    "task": "task name",
                    "duration": "30 minutes",
                    "reasoning": "why this time slot"
                }}
            ],
            "total_time": "total estimated time",
            "productivity_tips": ["specific tips for this schedule"],
            "potential_issues": ["things to watch out for"]
        }}
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            
            schedule = json.loads(response.content[0].text)
            return schedule
            
        except Exception as e:
            print(f"❌ Error creating schedule: {str(e)}")
            return None
    
    def daily_check_in(self):
        """
        Provide a daily check-in with personalized insights
        """
        current_time = datetime.now()
        
        prompt = f"""
        You are Jarvis, providing a daily check-in for your user who is learning AI while managing work responsibilities.
        
        Current time: {current_time.strftime('%A, %B %d, %Y at %I:%M %p')}
        
        Provide a helpful daily check-in with:
        {{
            "greeting": "personalized greeting based on time of day",
            "focus_recommendation": "what type of work is best for this time",
            "energy_tip": "advice for maintaining energy",
            "learning_suggestion": "a small AI learning task that fits the current time",
            "productivity_reminder": "one key productivity principle",
            "encouragement": "motivational message for someone building AI skills"
        }}
        
        Keep it concise but genuinely helpful.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            
            check_in = json.loads(response.content[0].text)
            return check_in
            
        except Exception as e:
            print(f"❌ Error during check-in: {str(e)}")
            return None

def main():
    """
    Main function to test Jarvis capabilities
    """
    print("🚀 Starting Basic Jarvis Test")
    print("=" * 50)
    
    # Initialize Jarvis
    jarvis = BasicJarvis()
    
    while True:
        print("\n" + "=" * 30)
        print("What would you like to test?")
        print("1. Analyze a task")
        print("2. Create a schedule")
        print("3. Daily check-in")
        print("4. Quit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            task = input("\n📝 What task would you like analyzed? ")
            result = jarvis.analyze_task(task)
            
            if result:
                print("\n🎯 TASK ANALYSIS:")
                print(f"Task: {result.get('task_name')}")
                print(f"Category: {result.get('category')}")
                print(f"Duration: {result.get('estimated_duration')} minutes")
                print(f"Priority: {result.get('priority')}")
                print(f"Best time: {result.get('best_time')}")
                print(f"Preparation: {', '.join(result.get('preparation', []))}")
                print(f"Success criteria: {result.get('success_criteria')}")
        
        elif choice == "2":
            print("\n📋 Enter tasks for scheduling (one per line, empty line when done):")
            tasks = []
            while True:
                task = input("Task: ").strip()
                if not task:
                    break
                tasks.append(task)
            
            if tasks:
                result = jarvis.suggest_schedule(tasks)
                if result:
                    print("\n📅 SUGGESTED SCHEDULE:")
                    for item in result.get('schedule', []):
                        print(f"{item.get('time')}: {item.get('task')} ({item.get('duration')})")
                    print(f"\nTotal time: {result.get('total_time')}")
        
        elif choice == "3":
            result = jarvis.daily_check_in()
            if result:
                print("\n🌟 DAILY CHECK-IN:")
                print(f"Greeting: {result.get('greeting')}")
                print(f"Focus: {result.get('focus_recommendation')}")
                print(f"Energy: {result.get('energy_tip')}")
                print(f"Learning: {result.get('learning_suggestion')}")
                print(f"Productivity: {result.get('productivity_reminder')}")
                print(f"Encouragement: {result.get('encouragement')}")
        
        elif choice == "4":
            print("\n👋 Goodbye! Jarvis is shutting down.")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()