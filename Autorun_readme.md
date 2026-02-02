I'll set this up as a user-level systemd service that auto-restarts on crash and a daily timer that restarts it at 14:10 after your DB cron. I'll create the service and timer units, reload systemd, enable and start them, and show status.

[1 tool called]

I'll create a user-level systemd service and a daily timer that restarts it at 14:10. Then I'll reload systemd, enable and start both, and show their status.

[7 tools called]

I'll check the timer status and next run time, then wrap up.

[2 tools called]

I created a user-level systemd service that runs `start_viz.sh`, enabled auto-restart on crash, and added a daily timer to restart it at 14:10 (2:10 PM) after your DB update.

- Check status
  - Service: `systemctl --user status nespreso-viz.service`
  - Timer: `systemctl --user status nespreso-viz-restart.timer`
  - Next run: `systemctl --user list-timers --all`
- Logs
  - Journald: `journalctl --user -u nespreso-viz.service -f`
  - App log: `tail -f /unity/g2/jmiranda/nespreso_viz/logs/viz.log`

Common ops:
- Restart now: `systemctl --user restart nespreso-viz.service`
- Stop: `systemctl --user stop nespreso-viz.service`
- Disable timer: `systemctl --user disable --now nespreso-viz-restart.timer`

It will:
- Keep running without tmux (user lingering enabled).
- Auto-restart on crash.
- Restart daily at 14:10 (2:10 PM).


---

I'll help you change the update time from 2:10 AM to 2:10 PM. Let me first check the current systemd timer configuration to see what needs to be updated.


[1 tool called]

Now I'll update the timer to run at 2:10 PM (14:10) instead of 2:10 AM. I need to modify the timer file and then reload systemd.


[2 tools called]

Now I'll reload systemd to apply the changes and check the status:


[2 tools called]

Perfect! I've successfully updated the timer from 2:10 AM to 2:10 PM (14:10). Let me also update the Autorun_readme.md file to reflect this change:


[2 tools called]

Perfect! I've successfully updated the timer configuration from 2:10 AM to 2:10 PM. Here's what I changed:

## Changes Made:

1. **Updated the systemd timer file** (`/unity/g2/jmiranda/.config/systemd/user/nespreso-viz-restart.timer`):
   - Changed the description from "02:10" to "14:10"
   - Changed the OnCalendar setting from `*-*-* 02:10:00` to `*-*-* 14:10:00`

2. **Updated the documentation** (`Autorun_readme.md`):
   - Added clarification that 14:10 means 2:10 PM
   - Updated both references to make it clear it's afternoon, not morning

3. **Reloaded systemd** to apply the changes

## Current Status:
The timer is now active and waiting for the next trigger at **Friday, September 26, 2025 at 2:10 PM EDT** (about 16 minutes from when I checked). The service will now restart daily at 2:10 PM instead of 2:10 AM, which should be much more convenient for your workflow.