# CSElec1
# Adaptive HRIS & Payroll Engine

**Name:** Jude Andrei E. Rabaya  
**Section:** CS4D  
**Date:** August 24, 2026  

---

### Adaptive Rules Logic

* **Rule 1:**  
  **If** `overtime_hours > 15` AND `consecutive_workdays >= 6`  
  → **Then** apply a `1.25x Overtime Surge Multiplier`, credit `1 Paid Wellness Rest Day`, and activate the Fatigue Mitigation status on the UI.

* **Rule 2:**  
  **If** `base_salary <= 30000` AND `emergency_advance_requested == True`  
  → **Then** unlock `Earned Wage Access (EWA)` up to `40% of accrued pay` with zero interest and render the Instant Liquidity panel.

---

### Personalization Logic

Standard HRIS platforms calculate payroll statically without considering employee workload strain or financial stress. This system adapts dynamically:

1. **Workload & Burnout Mitigation:** Tracks real-time fatigue indicators (consecutive streaks and overtime spikes). When thresholds are breached, it automatically scales pay with surge multipliers and allocates rest credits.
2. **Contextual Financial Liquidity:** Detects liquidity needs for entry-to-mid salary brackets and unlocks on-demand Earned Wage Access (EWA), removing reliance on high-interest loans.

---

### How to Run

Zero third-party dependencies required—runs purely on Python's standard library.

#### Android (Termux / Pydroid 3)

* **Termux:**
  ```bash
  python app.py
  
