# src/calendar_export.py
import os
from datetime import datetime, timedelta
import uuid

class CalendarExporter:
    """Export schedules to various calendar formats"""
    
    def __init__(self):
        self.export_dir = "exports"
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def create_ics_file(self, schedule_data, filename=None):
        """Create .ics file that can be imported into any calendar application"""
        
        if filename is None:
            filename = f"jarvis_schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.ics"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # ICS file header
        ics_content = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Jarvis AI Assistant//Schedule Export//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]
        
        # Process schedule items
        today = datetime.now().date()
        
        for item in schedule_data.get('schedule', []):
            event_time = self.parse_time(item.get('time', '9:00 AM'))
            duration_str = item.get('duration', '30 minutes')
            duration_mins = self.parse_duration(duration_str)
            
            start_datetime = datetime.combine(today, event_time)
            end_datetime = start_datetime + timedelta(minutes=duration_mins)
            
            # Create unique ID for event
            event_uid = str(uuid.uuid4())
            
            # Format for ICS (UTC format)
            start_str = start_datetime.strftime('%Y%m%dT%H%M%S')
            end_str = end_datetime.strftime('%Y%m%dT%H%M%S')
            
            # Add event to ICS
            ics_content.extend([
                "BEGIN:VEVENT",
                f"UID:{event_uid}",
                f"DTSTART:{start_str}",
                f"DTEND:{end_str}",
                f"SUMMARY:{item.get('task', 'Scheduled Task')}",
                f"DESCRIPTION:Scheduled by Jarvis AI\\nReasoning: {item.get('reasoning', 'Optimized timing')}",
                "STATUS:CONFIRMED",
                "TRANSP:OPAQUE",
                "END:VEVENT"
            ])
        
        # ICS file footer
        ics_content.append("END:VCALENDAR")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(ics_content))
        
        return filepath
    
    def create_html_schedule(self, schedule_data, filename=None):
        """Create HTML file for viewing/printing schedule"""
        
        if filename is None:
            filename = f"jarvis_schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        
        filepath = os.path.join(self.export_dir, filename)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Jarvis AI Schedule - {datetime.now().strftime('%B %d, %Y')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                .schedule-item {{ 
                    margin: 15px 0; 
                    padding: 15px; 
                    border-left: 4px solid #3498db; 
                    background: #f8f9fa; 
                }}
                .time {{ font-weight: bold; color: #e74c3c; }}
                .task {{ font-size: 1.1em; margin: 5px 0; }}
                .reasoning {{ color: #7f8c8d; font-style: italic; }}
                .summary {{ background: #ecf0f1; padding: 15px; margin-top: 20px; }}
                .tips {{ background: #d5f4e6; padding: 15px; margin-top: 20px; }}
                @media print {{ 
                    body {{ margin: 20px; }}
                    .no-print {{ display: none; }}
                }}
            </style>
        </head>
        <body>
            <h1>🤖 Jarvis AI Assistant - Daily Schedule</h1>
            <p><strong>Generated:</strong> {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}</p>
            
            <div class="schedule">
        """
        
        # Add schedule items
        for item in schedule_data.get('schedule', []):
            html_content += f"""
                <div class="schedule-item">
                    <div class="time">{item.get('time', 'TBD')}</div>
                    <div class="task">{item.get('task', 'Unnamed Task')}</div>
                    <div>Duration: {item.get('duration', 'Unknown')}</div>
                    <div class="reasoning">{item.get('reasoning', 'Optimally scheduled')}</div>
                </div>
            """
        
        # Add summary information
        html_content += f"""
            </div>
            
            <div class="summary">
                <h3>📊 Schedule Summary</h3>
                <p><strong>Total Time:</strong> {schedule_data.get('total_time', 'Not calculated')}</p>
                <p><strong>Number of Tasks:</strong> {len(schedule_data.get('schedule', []))}</p>
            </div>
        """
        
        # Add productivity tips if available
        tips = schedule_data.get('productivity_tips', [])
        if tips:
            html_content += """
                <div class="tips">
                    <h3>💡 Productivity Tips</h3>
                    <ul>
            """
            for tip in tips:
                html_content += f"<li>{tip}</li>"
            html_content += "</ul></div>"
        
        html_content += """
            <div class="no-print" style="margin-top: 30px; text-align: center; color: #7f8c8d;">
                <p>Generated by Jarvis AI Assistant</p>
            </div>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def create_email_format(self, schedule_data):
        """Create email-friendly text format for copying/pasting"""
        
        email_content = f"""
JARVIS AI SCHEDULE - {datetime.now().strftime('%A, %B %d, %Y')}
{'=' * 50}

DAILY SCHEDULE:
        """
        
        for item in schedule_data.get('schedule', []):
            email_content += f"""
⏰ {item.get('time', 'TBD')} - {item.get('task', 'Task')}
   Duration: {item.get('duration', 'Unknown')}
   Notes: {item.get('reasoning', 'Optimally scheduled')}
        """
        
        email_content += f"""

SUMMARY:
📊 Total Time: {schedule_data.get('total_time', 'Not calculated')}
📋 Tasks: {len(schedule_data.get('schedule', []))}

TIPS:
        """
        
        for tip in schedule_data.get('productivity_tips', []):
            email_content += f"💡 {tip}\n"
        
        email_content += f"""

Generated by Jarvis AI Assistant at {datetime.now().strftime('%I:%M %p')}
        """
        
        return email_content.strip()
    
    def parse_time(self, time_str):
        """Parse time string to datetime.time object"""
        try:
            # Handle formats like "9:00 AM" or "14:30"
            if 'AM' in time_str or 'PM' in time_str:
                return datetime.strptime(time_str, '%I:%M %p').time()
            else:
                return datetime.strptime(time_str, '%H:%M').time()
        except:
            return datetime.strptime('9:00 AM', '%I:%M %p').time()
    
    def parse_duration(self, duration_str):
        """Parse duration string to minutes"""
        try:
            if 'minute' in duration_str.lower():
                return int(duration_str.split()[0])
            elif 'hour' in duration_str.lower():
                hours = float(duration_str.split()[0])
                return int(hours * 60)
            else:
                return 30  # default
        except:
            return 30

def test_export():
    """Test the export functionality"""
    
    # Sample schedule data
    sample_schedule = {
        'schedule': [
            {
                'time': '9:00 AM',
                'task': 'Review quarterly reports',
                'duration': '90 minutes',
                'reasoning': 'High energy time for analytical work'
            },
            {
                'time': '11:00 AM',
                'task': 'Team standup meeting',
                'duration': '30 minutes',
                'reasoning': 'Good collaboration time after morning focus'
            },
            {
                'time': '2:00 PM',
                'task': 'Python practice session',
                'duration': '60 minutes',
                'reasoning': 'Post-lunch learning optimal for skill building'
            }
        ],
        'total_time': '3 hours',
        'productivity_tips': [
            'Take 5-minute breaks between tasks',
            'Keep water bottle nearby for hydration',
            'Use timer for focused work sessions'
        ]
    }
    
    exporter = CalendarExporter()
    
    # Test all export formats
    ics_file = exporter.create_ics_file(sample_schedule)
    html_file = exporter.create_html_schedule(sample_schedule)
    email_text = exporter.create_email_format(sample_schedule)
    
    print(f"✅ Calendar file created: {ics_file}")
    print(f"✅ HTML schedule created: {html_file}")
    print(f"✅ Email format ready")
    print(f"\nEmail format preview:\n{email_text[:200]}...")

if __name__ == "__main__":
    test_export()