from datetime import datetime, timedelta

# Get current date and time
now = datetime.now()
print("Current date and time:", now)

# Format date and time
formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
print("Formatted date and time:", formatted_date)

# Add 7 days
future_date = now + timedelta(days=7)
print("Date after 7 days:", future_date)

# Subtract 7 days
past_date = now - timedelta(days=7)
print("Date 7 days ago:", past_date)

# Difference between two dates
date1 = datetime(2025, 7, 3)
date2 = datetime(2025, 7, 10)
difference = date2 - date1
print(f"Days between {date1.date()} and {date2.date()}: {difference.days} days")
