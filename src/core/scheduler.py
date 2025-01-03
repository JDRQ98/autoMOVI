import os
import json
import schedule
import time
from datetime import datetime, timedelta
from subprocess import Popen
from win10toast import ToastNotifier

class MOVIScheduler:
    def __init__(self, movi_file="movis.json"):
        self.movi_file = movi_file
        self.notifier = ToastNotifier()

    def load_movi_data(self):
        """Load MOVI data from JSON file."""
        if not os.path.exists(self.movi_file):
            return {}

        with open(self.movi_file, "r") as file:
            return json.load(file)

    def get_pending_movis(self):
        """Get pending MOVIs for the current and next week."""
        movi_data = self.load_movi_data()
        current_date = datetime.now().date()
        next_week_date = current_date + timedelta(weeks=1)

        pending_movis = []

        for date_str, status in movi_data.items():
            if status == "pending":
                movi_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if current_date <= movi_date <= next_week_date:
                    pending_movis.append(date_str)

        return pending_movis

    def trigger_requestor(self, movi_date):
        """Trigger the MOVI requestor script for a given date."""
        # Notify the user
        self.notifier.show_toast(
            "autoMOVI Scheduler",
            f"Requesting MOVI for {movi_date}",
            duration=5
        )

        # Execute requestor.py (implementation pending)
        try:
            # Replace with the actual path to requestor.py
            requestor_script = os.path.join(os.getcwd(), "core", "requestor.py")
            Popen(["python", requestor_script, movi_date])
        except Exception as e:
            self.notifier.show_toast(
                "autoMOVI Scheduler",
                f"Failed to request MOVI for {movi_date}: {str(e)}",
                duration=5
            )

    def check_and_trigger_movis(self):
        """Check for pending MOVIs and trigger requests."""
        pending_movis = self.get_pending_movis()

        if not pending_movis:
            self.notifier.show_toast(
                "autoMOVI Scheduler",
                "No pending MOVIs to process.",
                duration=5
            )
            return

        for movi_date in pending_movis:
            self.trigger_requestor(movi_date)

    def schedule_task(self, time_str):
        """Schedule the task to check and trigger MOVIs at a specific time."""
        schedule.every().day.at(time_str).do(self.check_and_trigger_movis)

    def run(self):
        """Run the scheduler loop."""
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    scheduler = MOVIScheduler()

    # Example: Set the scheduler to run at a user-configured time (e.g., "08:00")
    user_configured_time = "08:00"  # Replace with a dynamic value if needed
    scheduler.schedule_task(user_configured_time)

    print(f"Scheduler is running. Next check at {user_configured_time}.")
    scheduler.run()
