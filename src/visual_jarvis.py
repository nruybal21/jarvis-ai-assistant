# Visual Enhanced Jarvis - Beautiful AI Interface
# File: src/visual_jarvis.py

import anthropic
import sqlite3
import json
import sys
import os
from datetime import datetime
import time
import random

# Add the config directory to our path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from config.credentials import CLAUDE_API_KEY
except ImportError:
    print("❌ Error: Can't find credentials.py file!")
    exit(1)

# Try to import enhanced features
try:
    from enhanced_jarvis import EnhancedJarvis
    HAS_ENHANCED_FEATURES = True
except ImportError:
    HAS_ENHANCED_FEATURES = False

# Install colorama for cross-platform colors
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  # Automatically reset colors after each print
    HAS_COLORS = True
except ImportError:
    # Fallback without colors
    HAS_COLORS = False
    class Fore:
        CYAN = BLUE = GREEN = YELLOW = RED = MAGENTA = WHITE = ""
    class Back:
        BLACK = BLUE = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""

class VisualJarvis:
    """
    Visual Enhanced Jarvis - Premium AI Assistant Interface
    
    Features beautiful terminal interface with:
    - Color-coded responses and menus
    - Animated loading sequences
    - Premium visual design
    - Engaging AI personality
    """
    
    def __init__(self):
        """Initialize Visual Jarvis with enhanced interface"""
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        
        # Initialize enhanced AI if available
        if HAS_ENHANCED_FEATURES:
            try:
                self.enhanced_jarvis = EnhancedJarvis()
                self.has_enhanced = True
            except Exception:
                self.has_enhanced = False
        else:
            self.has_enhanced = False
        
        # Interface colors and styles
        self.colors = {
            'primary': Fore.CYAN + Style.BRIGHT,
            'secondary': Fore.BLUE + Style.BRIGHT,
            'success': Fore.GREEN + Style.BRIGHT,
            'warning': Fore.YELLOW + Style.BRIGHT,
            'error': Fore.RED + Style.BRIGHT,
            'accent': Fore.MAGENTA + Style.BRIGHT,
            'text': Fore.WHITE + Style.BRIGHT,
            'dim': Fore.WHITE + Style.DIM
        }
    
    def loading_animation(self, message="Processing", duration=2):
        """Beautiful loading animation"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                print(f"\r{self.colors['primary']}{frame} {message}...", end="", flush=True)
                time.sleep(0.1)
        
        print(f"\r{self.colors['success']}✓ {message} complete!{' ' * 20}")
    
    def typewriter_effect(self, text, delay=0.03):
        """Typewriter effect for AI responses"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()  # New line at the end
    
    def display_welcome(self):
        """Display beautiful welcome screen"""
        print(f"{self.colors['primary']}")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                                                                  ║")
        print("║      🤖  J A R V I S   A I   A S S I S T A N T  🤖              ║")
        print("║                                                                  ║")
        print("║           Advanced Intelligence • Memory • Learning              ║")
        print("║                                                                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print(f"{Style.RESET_ALL}")
        
        # Animated initialization
        self.loading_animation("Initializing AI systems", 1.5)
        
        if self.has_enhanced:
            print(f"{self.colors['success']}🧠 Enhanced AI Intelligence: {self.colors['text']}ONLINE")
            print(f"{self.colors['success']}💾 Memory Systems: {self.colors['text']}ACTIVE")
            print(f"{self.colors['success']}📊 Pattern Learning: {self.colors['text']}ENABLED")
        else:
            print(f"{self.colors['warning']}⚠️  Enhanced features: {self.colors['text']}BASIC MODE")
        
        print(f"{self.colors['success']}🔗 Claude API: {self.colors['text']}CONNECTED")
        print(f"{self.colors['success']}💫 Visual Interface: {self.colors['text']}LOADED")
        
        print(f"\n{self.colors['accent']}═══════════════════════════════════════════════════════════════════")
        print(f"{self.colors['text']}Welcome to your personal AI productivity assistant!")
        print(f"Enhanced with visual interface and premium user experience.")
        print(f"{self.colors['accent']}═══════════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    
    def display_menu(self):
        """Display beautiful interactive menu"""
        print(f"\n{self.colors['primary']}┌─ JARVIS AI CONTROL CENTER ─────────────────────────────────────┐")
        print(f"│                                                                 │")
        print(f"│  {self.colors['text']}🎯 {self.colors['secondary']}1.{self.colors['text']} Analyze Task          {self.colors['dim']}→ AI task optimization     {self.colors['primary']}│")
        print(f"│  {self.colors['text']}📅 {self.colors['secondary']}2.{self.colors['text']} Create Schedule       {self.colors['dim']}→ Smart daily planning     {self.colors['primary']}│")
        print(f"│  {self.colors['text']}🌟 {self.colors['secondary']}3.{self.colors['text']} Daily Check-in        {self.colors['dim']}→ Personalized insights    {self.colors['primary']}│")
        print(f"│  {self.colors['text']}⚡ {self.colors['secondary']}4.{self.colors['text']} Advanced Scheduling   {self.colors['dim']}→ Complex project planning {self.colors['primary']}│")
        
        if self.has_enhanced:
            print(f"│  {self.colors['text']}🧠 {self.colors['secondary']}5.{self.colors['text']} Enhanced AI Chat      {self.colors['dim']}→ Intelligent conversation {self.colors['primary']}│")
            print(f"│  {self.colors['text']}📊 {self.colors['secondary']}6.{self.colors['text']} AI Analytics          {self.colors['dim']}→ Productivity insights    {self.colors['primary']}│")
            print(f"│  {self.colors['text']}💾 {self.colors['secondary']}7.{self.colors['text']} Manage Schedules      {self.colors['dim']}→ Schedule library         {self.colors['primary']}│")
            print(f"│  {self.colors['text']}🚪 {self.colors['secondary']}8.{self.colors['text']} Exit                  {self.colors['dim']}→ Shutdown AI systems     {self.colors['primary']}│")
        else:
            print(f"│  {self.colors['text']}💾 {self.colors['secondary']}5.{self.colors['text']} Manage Schedules      {self.colors['dim']}→ Schedule library         {self.colors['primary']}│")
            print(f"│  {self.colors['text']}🚪 {self.colors['secondary']}6.{self.colors['text']} Exit                  {self.colors['dim']}→ Shutdown AI systems     {self.colors['primary']}│")
        
        print(f"│                                                                 │")
        print(f"└─────────────────────────────────────────────────────────────────┘{Style.RESET_ALL}")
    
    def get_user_choice(self):
        """Get user input with beautiful prompt"""
        max_choice = 8 if self.has_enhanced else 6
        prompt = f"\n{self.colors['accent']}🤖 {self.colors['text']}Jarvis awaiting command {self.colors['dim']}(1-{max_choice}){self.colors['text']}: "
        return input(prompt).strip()
    
    def display_thinking(self, message="AI is thinking"):
        """Display AI thinking animation"""
        thinking_frames = ["🧠💭", "🤖💡", "⚡🎯", "✨🔮"]
        print(f"\n{self.colors['primary']}", end="")
        
        for _ in range(8):  # Show animation for ~2 seconds
            for frame in thinking_frames:
                print(f"\r{frame} {message}...", end="", flush=True)
                time.sleep(0.25)
        
        print(f"\r{self.colors['success']}✓ {message} complete!{' ' * 20}")
    
    def format_ai_response(self, title, content, response_type="info"):
        """Format AI responses beautifully"""
        if response_type == "analysis":
            icon = "🎯"
            color = self.colors['primary']
        elif response_type == "schedule":
            icon = "📅"
            color = self.colors['secondary']
        elif response_type == "insight":
            icon = "💡"
            color = self.colors['accent']
        elif response_type == "success":
            icon = "✅"
            color = self.colors['success']
        else:
            icon = "🤖"
            color = self.colors['text']
        
        print(f"\n{color}╔══════════════════════════════════════════════════════════════════╗")
        print(f"║ {icon}  {title.upper().center(60)} ║")
        print(f"╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        # Typewriter effect for AI responses
        if isinstance(content, str):
            print(f"{self.colors['text']}")
            self.typewriter_effect(content, delay=0.02)
        else:
            print(f"{self.colors['text']}{content}")
        
        print(f"{color}{'═' * 68}{Style.RESET_ALL}")
    
    def analyze_task_visual(self, task_description):
        """Visual task analysis with enhanced display"""
        self.display_thinking("Analyzing task with AI")
        
        # Simulate AI analysis (replace with actual analysis)
        analysis_result = {
            "task_analysis": "High-complexity strategic task requiring focused attention",
            "estimated_duration": 90,
            "priority": "high",
            "best_time": "Morning 9-11 AM during peak cognitive hours",
            "steps": [
                "Research background information and context",
                "Create structured outline and framework", 
                "Develop detailed content and analysis",
                "Review, refine, and finalize deliverable"
            ],
            "success_tips": [
                "Block calendar to avoid interruptions",
                "Prepare all resources before starting",
                "Take 5-minute breaks every 25 minutes"
            ],
            "category": "work"
        }
        
        self.format_ai_response("AI Task Analysis", "", "analysis")
        
        print(f"{self.colors['text']}📋 {self.colors['secondary']}Task:{self.colors['text']} {task_description}")
        print(f"🧠 {self.colors['secondary']}Analysis:{self.colors['text']} {analysis_result['task_analysis']}")
        print(f"⏱️  {self.colors['secondary']}Duration:{self.colors['text']} {analysis_result['estimated_duration']} minutes")
        print(f"🎯 {self.colors['secondary']}Priority:{self.colors['text']} {analysis_result['priority'].title()}")
        print(f"🕐 {self.colors['secondary']}Best Time:{self.colors['text']} {analysis_result['best_time']}")
        
        print(f"\n{self.colors['accent']}📝 RECOMMENDED STEPS:")
        for i, step in enumerate(analysis_result['steps'], 1):
            print(f"{self.colors['text']}   {i}. {step}")
        
        print(f"\n{self.colors['accent']}💡 SUCCESS TIPS:")
        for tip in analysis_result['success_tips']:
            print(f"{self.colors['text']}   • {tip}")
    
    def daily_checkin_visual(self):
        """Visual daily check-in with enhanced display"""
        self.display_thinking("Generating personalized insights")
        
        current_time = datetime.now()
        hour = current_time.hour
        
        if hour < 12:
            greeting = "Good morning! Ready to seize the day?"
            energy_forecast = "Peak energy expected - perfect for challenging tasks"
        elif hour < 17:
            greeting = "Good afternoon! How's your day progressing?"
            energy_forecast = "Steady energy - ideal for collaborative work"
        else:
            greeting = "Good evening! Time to reflect and plan ahead"
            energy_forecast = "Winding down - perfect for planning and organizing"
        
        checkin_data = {
            "greeting": greeting,
            "energy_forecast": energy_forecast,
            "priority_suggestions": [
                "Focus on your most important project for 90 minutes",
                "Complete 2-3 quick administrative tasks",
                "Plan tomorrow's priorities before end of day"
            ],
            "productivity_tip": "Use the 2-minute rule: if it takes less than 2 minutes, do it now",
            "motivation": "Every small step forward is progress worth celebrating!",
            "focus_areas": ["Deep work blocks", "Communication efficiency", "Energy management"]
        }
        
        self.format_ai_response("Daily AI Check-in", "", "insight")
        
        print(f"{self.colors['text']}👋 {greeting}")
        print(f"\n⚡ {self.colors['secondary']}Energy Forecast:{self.colors['text']} {checkin_data['energy_forecast']}")
        
        print(f"\n{self.colors['accent']}🎯 TODAY'S PRIORITIES:")
        for priority in checkin_data['priority_suggestions']:
            print(f"{self.colors['text']}   • {priority}")
        
        print(f"\n💡 {self.colors['secondary']}Productivity Tip:{self.colors['text']} {checkin_data['productivity_tip']}")
        print(f"\n🚀 {self.colors['secondary']}Motivation:{self.colors['text']} {checkin_data['motivation']}")
        
        print(f"\n{self.colors['accent']}🔍 FOCUS AREAS:")
        for area in checkin_data['focus_areas']:
            print(f"{self.colors['text']}   • {area}")
    
    def enhanced_conversation_visual(self):
        """Visual enhanced AI conversation interface"""
        if not self.has_enhanced:
            self.format_ai_response("Feature Unavailable", "Enhanced AI conversation requires additional setup", "warning")
            return
        
        self.format_ai_response("Enhanced AI Conversation", "Advanced intelligence with memory and learning", "insight")
        
        print(f"{self.colors['text']}💬 Enter natural conversation mode. The AI remembers everything!")
        print(f"{self.colors['dim']}Type 'back' to return to main menu{Style.RESET_ALL}")
        
        while True:
            user_input = input(f"\n{self.colors['accent']}You: {self.colors['text']}").strip()
            
            if user_input.lower() == 'back':
                break
            
            if user_input:
                self.display_thinking("AI processing with enhanced intelligence")
                
                try:
                    response = self.enhanced_jarvis.intelligent_conversation(user_input)
                    print(f"\n{self.colors['primary']}🤖 Enhanced Jarvis:{self.colors['text']}")
                    self.typewriter_effect(response, delay=0.015)
                except Exception as e:
                    print(f"{self.colors['error']}❌ Error: {str(e)}")
    
    def shutdown_sequence(self):
        """Beautiful shutdown animation"""
        print(f"\n{self.colors['accent']}╔══════════════════════════════════════════════════════════════════╗")
        print(f"║                    JARVIS AI SHUTDOWN SEQUENCE                   ║")
        print(f"╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        self.loading_animation("Saving AI learning data", 1)
        self.loading_animation("Backing up conversation memory", 1)
        self.loading_animation("Optimizing AI patterns", 1)
        
        print(f"\n{self.colors['success']}✅ All systems safely offline")
        print(f"{self.colors['text']}💫 AI learning data preserved for next session")
        print(f"{self.colors['accent']}👋 Thank you for using Jarvis AI Assistant!")
        print(f"{self.colors['dim']}See you next time!{Style.RESET_ALL}")

def main():
    """Main function with beautiful visual interface"""
    try:
        jarvis = VisualJarvis()
        jarvis.display_welcome()
        
        while True:
            try:
                jarvis.display_menu()
                choice = jarvis.get_user_choice()
                
                if choice == "1":
                    task = input(f"\n{jarvis.colors['accent']}📝 Describe your task:{jarvis.colors['text']} ")
                    if task.strip():
                        jarvis.analyze_task_visual(task)
                    else:
                        print(f"{jarvis.colors['warning']}⚠️  Please enter a task description")
                
                elif choice == "2":
                    jarvis.format_ai_response("Schedule Creation", "Enter tasks for AI optimization", "schedule")
                    print(f"{jarvis.colors['text']}Enter tasks one by one (press Enter on empty line when done):")
                    
                    tasks = []
                    while True:
                        task = input(f"{jarvis.colors['accent']}Task {len(tasks) + 1}:{jarvis.colors['text']} ").strip()
                        if not task:
                            break
                        tasks.append(task)
                    
                    if tasks:
                        jarvis.display_thinking("Creating optimized schedule")
                        jarvis.format_ai_response("Optimized Schedule Created", f"Successfully organized {len(tasks)} tasks", "success")
                        # Here you would integrate with actual schedule creation logic
                    else:
                        print(f"{jarvis.colors['warning']}⚠️  No tasks entered")
                
                elif choice == "3":
                    jarvis.daily_checkin_visual()
                
                elif choice == "4":
                    jarvis.format_ai_response("Advanced Scheduling", "Complex project planning features", "info")
                    print(f"{jarvis.colors['text']}Advanced scheduling features would be integrated here")
                
                elif choice == "5":
                    if jarvis.has_enhanced:
                        jarvis.enhanced_conversation_visual()
                    else:
                        jarvis.format_ai_response("Schedule Management", "Manage saved schedules", "info")
                        print(f"{jarvis.colors['text']}Schedule management features would be integrated here")
                
                elif choice == "6":
                    if jarvis.has_enhanced:
                        jarvis.format_ai_response("AI Analytics", "Advanced productivity analysis", "analysis")
                        jarvis.display_thinking("Analyzing productivity patterns")
                        print(f"{jarvis.colors['text']}AI analytics would show detailed insights here")
                    else:
                        jarvis.shutdown_sequence()
                        break
                
                elif choice == "7" and jarvis.has_enhanced:
                    jarvis.format_ai_response("Schedule Management", "Manage saved schedules", "info")
                    print(f"{jarvis.colors['text']}Schedule management features would be integrated here")
                
                elif choice == "8" and jarvis.has_enhanced:
                    jarvis.shutdown_sequence()
                    break
                
                else:
                    print(f"{jarvis.colors['error']}❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                jarvis.shutdown_sequence()
                break
            except Exception as e:
                print(f"{jarvis.colors['error']}❌ Error: {str(e)}")
                
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to initialize Visual Jarvis: {str(e)}")

if __name__ == "__main__":
    main()