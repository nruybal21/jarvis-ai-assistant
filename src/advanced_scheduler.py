# src/advanced_scheduler.py
import anthropic
import json
import sys
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.credentials import CLAUDE_API_KEY
from src.database import JarvisDatabase

@dataclass
class ScheduledTask:
    """Represents a task with scheduling metadata"""
    id: str
    title: str
    duration: int  # minutes
    priority: str  # high/medium/low
    category: str
    dependencies: List[str]  # task IDs this depends on
    deadline: Optional[datetime]
    energy_level: str  # high/medium/low
    recurring: Optional[str]  # daily/weekly/monthly
    project: Optional[str]
    estimated_start: Optional[datetime] = None
    buffer_needed: int = 0  # minutes of buffer time

class AdvancedScheduler:
    """
    Advanced scheduling system with project coordination and optimization
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        self.db = JarvisDatabase()
        print("Advanced Scheduler initialized")
    
    def analyze_project(self, project_description: str, deadline: str = None) -> Dict:
        """Break down a complex project into scheduled tasks with dependencies"""
        
        prompt = f"""
        Analyze this project and break it into a structured task plan:
        
        Project: {project_description}
        Deadline: {deadline if deadline else "Not specified"}
        Current date: {datetime.now().strftime('%Y-%m-%d')}
        
        Create a comprehensive project breakdown with:
        {{
            "project_overview": {{
                "total_estimated_hours": "number",
                "complexity_level": "low/medium/high", 
                "key_milestones": ["milestone 1", "milestone 2"],
                "success_criteria": "clear success definition"
            }},
            "task_breakdown": [
                {{
                    "task_id": "unique_id",
                    "title": "specific task name",
                    "description": "detailed description",
                    "estimated_duration": 60,
                    "priority": "high/medium/low",
                    "category": "research/development/communication/review",
                    "dependencies": ["task_id_1", "task_id_2"],
                    "energy_level": "high/medium/low",
                    "buffer_time": 15,
                    "deliverable": "what gets produced"
                }}
            ],
            "scheduling_recommendations": {{
                "optimal_sequence": "recommended order explanation",
                "parallel_opportunities": "tasks that can be done simultaneously",
                "risk_factors": "potential scheduling challenges",
                "time_buffers": "recommended buffer strategies"
            }}
        }}
        
        Focus on realistic time estimates and clear dependencies.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            print(f"Error analyzing project: {e}")
            return None
    
    def create_weekly_schedule(self, tasks: List[Dict], constraints: Dict = None) -> Dict:
        """Generate optimized weekly schedule considering energy patterns and constraints"""
        
        # Get user's productivity patterns from database
        productivity_stats = self.db.get_productivity_stats(30)
        
        constraints = constraints or {}
        tasks_json = json.dumps(tasks, default=str)
        
        prompt = f"""
        Create an optimized weekly schedule for these tasks:
        
        Tasks: {tasks_json}
        
        User constraints:
        - Work hours: {constraints.get('work_hours', '9 AM - 5 PM')}
        - Break preferences: {constraints.get('breaks', '15 min every 90 min')}
        - Deep work blocks: {constraints.get('focus_blocks', '2-3 hour chunks')}
        - Meeting-free times: {constraints.get('focus_time', 'mornings preferred')}
        
        Historical productivity data: {productivity_stats}
        
        Generate a weekly schedule:
        {{
            "weekly_overview": {{
                "total_productive_hours": "number",
                "high_energy_allocation": "percentage to complex tasks",
                "buffer_time_included": "total buffer minutes",
                "workload_balance": "even/front-loaded/back-loaded"
            }},
            "daily_schedules": {{
                "monday": [
                    {{
                        "time": "9:00 AM",
                        "duration": 90,
                        "task": "task title",
                        "type": "deep work/communication/admin",
                        "energy_match": "high/medium/low",
                        "reasoning": "why this time slot"
                    }}
                ],
                "tuesday": [],
                "wednesday": [],
                "thursday": [],
                "friday": []
            }},
            "optimization_insights": {{
                "energy_optimization": "how energy levels were considered",
                "dependency_resolution": "how task dependencies were handled", 
                "risk_mitigation": "scheduling risks and mitigations",
                "improvement_suggestions": "ways to optimize further"
            }}
        }}
        
        Prioritize realistic scheduling with appropriate buffers.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            print(f"Error creating weekly schedule: {e}")
            return None
    
    def optimize_existing_schedule(self, current_schedule: List[Dict]) -> Dict:
        """Analyze and optimize an existing schedule for better productivity"""
        
        schedule_json = json.dumps(current_schedule, default=str)
        
        prompt = f"""
        Analyze this existing schedule and suggest optimizations:
        
        Current schedule: {schedule_json}
        Current time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}
        
        Provide optimization analysis:
        {{
            "current_analysis": {{
                "workload_assessment": "balanced/overloaded/underutilized",
                "energy_alignment": "how well tasks match optimal energy times",
                "buffer_adequacy": "sufficient/insufficient buffer time",
                "dependency_issues": "any scheduling conflicts"
            }},
            "optimization_suggestions": [
                {{
                    "change_type": "reschedule/reorder/split/combine",
                    "original_task": "current task",
                    "suggested_change": "specific modification",
                    "reasoning": "why this improves productivity",
                    "impact": "high/medium/low improvement"
                }}
            ],
            "alternative_schedule": {{
                "time_blocks": "optimized time allocation",
                "task_reordering": "better sequence",
                "energy_optimization": "energy-task matching improvements"
            }},
            "productivity_forecast": {{
                "estimated_efficiency_gain": "percentage",
                "stress_reduction": "high/medium/low",
                "completion_probability": "percentage"
            }}
        }}
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            print(f"Error optimizing schedule: {e}")
            return None
    
    def handle_schedule_conflicts(self, conflicts: List[Dict]) -> Dict:
        """Resolve scheduling conflicts with intelligent suggestions"""
        
        conflicts_json = json.dumps(conflicts, default=str)
        
        prompt = f"""
        Resolve these scheduling conflicts intelligently:
        
        Conflicts: {conflicts_json}
        
        Provide conflict resolution:
        {{
            "conflict_analysis": {{
                "conflict_severity": "high/medium/low",
                "impact_assessment": "what gets affected",
                "resolution_complexity": "simple/moderate/complex"
            }},
            "resolution_options": [
                {{
                    "option": "solution description",
                    "trade_offs": "what gets sacrificed",
                    "feasibility": "easy/moderate/difficult",
                    "recommendation_score": "1-10"
                }}
            ],
            "recommended_solution": {{
                "primary_action": "main solution",
                "secondary_adjustments": "supporting changes",
                "timeline_impact": "how deadlines are affected",
                "mitigation_strategies": "reducing negative impacts"
            }}
        }}
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            print(f"Error resolving conflicts: {e}")
            return None

def main():
    """Test the advanced scheduling system"""
    print("Advanced Scheduling System")
    print("=" * 40)
    
    scheduler = AdvancedScheduler()
    
    while True:
        print("\nAdvanced Scheduling Options:")
        print("1. Analyze and break down a project")
        print("2. Create optimized weekly schedule")
        print("3. Optimize existing schedule")
        print("4. Resolve scheduling conflicts")
        print("5. Back to main menu")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            project = input("\nDescribe your project: ")
            deadline = input("Deadline (optional, press Enter to skip): ") or None
            
            result = scheduler.analyze_project(project, deadline)
            if result:
                print("\nPROJECT ANALYSIS:")
                overview = result.get('project_overview', {})
                print(f"Estimated hours: {overview.get('total_estimated_hours')}")
                print(f"Complexity: {overview.get('complexity_level')}")
                print(f"Key milestones: {', '.join(overview.get('key_milestones', []))}")
                
                print(f"\nTasks identified: {len(result.get('task_breakdown', []))}")
                for task in result.get('task_breakdown', [])[:3]:
                    print(f"- {task.get('title')} ({task.get('estimated_duration')} min)")
        
        elif choice == "2":
            print("\nEnter tasks for weekly scheduling:")
            tasks = []
            while True:
                task = input("Task (or press Enter when done): ").strip()
                if not task:
                    break
                duration = input(f"Duration for '{task}' (minutes): ")
                priority = input("Priority (high/medium/low): ") or "medium"
                
                tasks.append({
                    "title": task,
                    "duration": int(duration) if duration.isdigit() else 60,
                    "priority": priority
                })
            
            if tasks:
                constraints = {
                    "work_hours": "9 AM - 5 PM",
                    "breaks": "15 min every 90 min",
                    "focus_blocks": "2-3 hour chunks"
                }
                
                result = scheduler.create_weekly_schedule(tasks, constraints)
                if result:
                    print("\nWEEKLY SCHEDULE CREATED:")
                    overview = result.get('weekly_overview', {})
                    print(f"Total productive hours: {overview.get('total_productive_hours')}")
                    print(f"Workload balance: {overview.get('workload_balance')}")
                    
                    # Show Monday as example
                    monday = result.get('daily_schedules', {}).get('monday', [])
                    if monday:
                        print("\nMonday schedule preview:")
                        for item in monday[:3]:
                            print(f"{item.get('time')}: {item.get('task')} ({item.get('duration')} min)")
        
        elif choice == "3":
            print("\nOptimization feature requires existing schedule data.")
            print("This would analyze your current calendar and suggest improvements.")
            
        elif choice == "4":
            print("\nConflict resolution feature helps when you have:")
            print("- Overlapping meetings")
            print("- Impossible deadlines") 
            print("- Resource constraints")
            
        elif choice == "5":
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()