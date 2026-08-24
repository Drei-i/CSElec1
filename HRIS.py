"""
Adaptive HRIS & Payroll Engine
Author: Jude Andrei E. Rabaya (CS4D)
Date: August 24, 2026

Features:
- Standard-library web server & UI (No pip dependencies needed)
- Real-time evaluation of Adaptive HRIS Rules
- Dynamic UI personalization based on employee workload and financial state
"""

import http.server
import json
import socketserver
import threading
import urllib.parse
import webbrowser

PORT = 8080

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adaptive HRIS Payroll Dashboard</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --accent-blue: #38bdf8;
            --accent-green: #4ade80;
            --accent-amber: #fbbf24;
            --accent-rose: #f43f5e;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); padding: 1.5rem; min-height: 100vh; }
        .container { max-width: 960px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.5rem; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--card-border); padding-bottom: 1rem; }
        .badge { font-size: 0.75rem; padding: 0.25rem 0.6rem; border-radius: 9999px; background: #0369a1; color: #e0f2fe; font-weight: 600; }
        
        .grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
        @media (min-width: 768px) { .grid { grid-template-columns: 1fr 1.3fr; } }
        
        .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 1.25rem; }
        h2 { font-size: 1.1rem; margin-bottom: 1rem; color: var(--accent-blue); display: flex; align-items: center; gap: 0.5rem; }
        
        .form-group { margin-bottom: 1rem; }
        label { display: block; font-size: 0.85rem; color: var(--text-sub); margin-bottom: 0.35rem; }
        input[type="text"], input[type="number"], select {
            width: 100%; padding: 0.6rem 0.75rem; border-radius: 6px; border: 1px solid var(--card-border);
            background: #0f172a; color: var(--text-main); font-size: 0.9rem; outline: none;
        }
        input:focus { border-color: var(--accent-blue); }
        
        .range-wrap { display: flex; align-items: center; gap: 0.75rem; }
        input[type="range"] { flex: 1; accent-color: var(--accent-blue); }
        .val-display { min-width: 45px; font-size: 0.85rem; font-weight: 600; text-align: right; }

        .stat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1rem; }
        .stat-box { background: #0f172a; padding: 0.85rem; border-radius: 8px; border: 1px solid var(--card-border); }
        .stat-box .title { font-size: 0.75rem; color: var(--text-sub); }
        .stat-box .amount { font-size: 1.2rem; font-weight: 700; margin-top: 0.25rem; }

        .rule-card { border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; border-left: 4px solid #475569; background: #0f172a; }
        .rule-card.active-surge { border-left-color: var(--accent-amber); background: #451a0320; }
        .rule-card.active-ewa { border-left-color: var(--accent-green); background: #052e1620; }
        .rule-header { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.35rem; }
        .rule-desc { font-size: 0.8rem; color: var(--text-sub); line-height: 1.4; }
        .rule-badge { font-size: 0.7rem; padding: 0.15rem 0.4rem; border-radius: 4px; }
        .badge-inactive { background: #334155; color: #94a3b8; }
        .badge-active { background: #0284c7; color: #f0f9ff; font-weight: bold; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <div>
            <h1>SmartPay HRIS</h1>
            <p style="font-size: 0.85rem; color: var(--text-sub);">Adaptive Payroll & Workload Intelligence Engine</p>
        </div>
        <span class="badge">Jude Andrei E. Rabaya | CS4D</span>
    </header>

    <div class="grid">
        <!-- Input Controls -->
        <div class="card">
            <h2>Employee Parameters</h2>
            <div class="form-group">
                <label>Employee Name</label>
                <input type="text" id="name" value="Alex Rivera" oninput="recompute()">
            </div>
            <div class="form-group">
                <label>Base Salary (PHP / Month)</label>
                <input type="number" id="baseSalary" value="28000" step="1000" oninput="recompute()">
            </div>
            <div class="form-group">
                <label>Overtime Hours (Current Cycle)</label>
                <div class="range-wrap">
                    <input type="range" id="overtimeHours" min="0" max="40" value="18" oninput="recompute()">
                    <span class="val-display" id="otVal">18 hrs</span>
                </div>
            </div>
            <div class="form-group">
                <label>Consecutive Workdays (Without Rest)</label>
                <div class="range-wrap">
                    <input type="range" id="workdays" min="1" max="14" value="7" oninput="recompute()">
                    <span class="val-display" id="daysVal">7 days</span>
                </div>
            </div>
            <div class="form-group">
                <label>Emergency Advance Requested?</label>
                <select id="advanceReq" onchange="recompute()">
                    <option value="yes" selected>Yes (Need Mid-Month Cash Flow)</option>
                    <option value="no">No</option>
                </select>
            </div>
        </div>

        <!-- Adaptive Engine Output -->
        <div class="card">
            <h2>Payroll Breakdown</h2>
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="title">Gross Base Pay</div>
                    <div class="amount" id="grossBase">₱28,000.00</div>
                </div>
                <div class="stat-box">
                    <div class="title">Total Overtime Pay</div>
                    <div class="amount" style="color: var(--accent-amber);" id="otPay">₱0.00</div>
                </div>
                <div class="stat-box">
                    <div class="title">Standard Deductions</div>
                    <div class="amount" style="color: var(--accent-rose);" id="deductions">-₱3,200.00</div>
                </div>
                <div class="stat-box">
                    <div class="title">Estimated Net Take-Home</div>
                    <div class="amount" style="color: var(--accent-green);" id="netPay">₱0.00</div>
                </div>
            </div>

            <h2>Active Adaptive Triggers</h2>
            
            <!-- Rule 1 Container -->
            <div id="rule1Card" class="rule-card">
                <div class="rule-header">
                    <span>Rule 1: Fatigue Surge & Wellness Protection</span>
                    <span id="rule1Badge" class="rule-badge badge-inactive">INACTIVE</span>
                </div>
                <div class="rule-desc" id="rule1Desc">
                    Standard OT rate active. Threshold: >15 OT hours and ≥6 consecutive workdays.
                </div>
            </div>

            <!-- Rule 2 Container -->
            <div id="rule2Card" class="rule-card">
                <div class="rule-header">
                    <span>Rule 2: Earned Wage Access (EWA) Liquidity</span>
                    <span id="rule2Badge" class="rule-badge badge-inactive">INACTIVE</span>
                </div>
                <div class="rule-desc" id="rule2Desc">
                    Standard monthly cutoff active. Threshold: Base salary ≤ ₱30k + advance request.
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function recompute() {
    const base = parseFloat(document.getElementById('baseSalary').value) || 0;
    const otHours = parseInt(document.getElementById('overtimeHours').value) || 0;
    const workdays = parseInt(document.getElementById('workdays').value) || 0;
    const advanceReq = document.getElementById('advanceReq').value === 'yes';

    document.getElementById('otVal').innerText = otHours + " hrs";
    document.getElementById('daysVal').innerText = workdays + " days";

    const hourlyRate = (base / 22) / 8;
    const deductions = base * 0.11; // 11% mandatory taxes/contributions

    // --- ADAPTIVE RULE 1: Burnout / Fatigue Compensation ---
    // If Overtime > 15 hours AND Consecutive Workdays >= 6 -> Apply 1.25x Overtime Surge Multiplier + Wellness Day
    let otMultiplier = 1.25; // Standard standard multiplier
    let rule1Active = false;

    if (otHours > 15 && workdays >= 6) {
        otMultiplier = 1.25 * 1.25; // 25% surge boost = 1.5625x
        rule1Active = true;
    }

    const totalOtPay = otHours * hourlyRate * otMultiplier;
    const netTakeHome = base + totalOtPay - deductions;

    // --- ADAPTIVE RULE 2: Low-Income Liquidity / Earned Wage Access ---
    // If Base Salary <= 30,000 AND Advance Requested -> Unlock 40% zero-interest advance limit
    let rule2Active = false;
    let ewaMaxAmount = 0;

    if (base <= 30000 && advanceReq) {
        rule2Active = true;
        ewaMaxAmount = (base + totalOtPay) * 0.40;
    }

    // Update UI Stats
    document.getElementById('grossBase').innerText = '₱' + base.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('otPay').innerText = '₱' + totalOtPay.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('deductions').innerText = '-₱' + deductions.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('netPay').innerText = '₱' + netTakeHome.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

    // Update Rule 1 UI
    const r1Card = document.getElementById('rule1Card');
    const r1Badge = document.getElementById('rule1Badge');
    const r1Desc = document.getElementById('rule1Desc');
    if (rule1Active) {
        r1Card.className = 'rule-card active-surge';
        r1Badge.className = 'rule-badge badge-active';
        r1Badge.innerText = 'TRIGGERED (SURGE ACTIVE)';
        r1Desc.innerHTML = `<strong>Overtime Surge Multiplier (1.56x) Applied.</strong> High fatigue index detected (${otHours} OT hrs across ${workdays} consecutive days). System auto-allocated <strong>1 Mandatory Paid Wellness Rest Credit</strong>.`;
    } else {
        r1Card.className = 'rule-card';
        r1Badge.className = 'rule-badge badge-inactive';
        r1Badge.innerText = 'INACTIVE';
        r1Desc.innerText = 'Standard OT rate (1.25x). Triggers when OT > 15 hrs and consecutive workdays ≥ 6.';
    }

    // Update Rule 2 UI
    const r2Card = document.getElementById('rule2Card');
    const r2Badge = document.getElementById('rule2Badge');
    const r2Desc = document.getElementById('rule2Desc');
    if (rule2Active) {
        r2Card.className = 'rule-card active-ewa';
        r2Badge.className = 'rule-badge badge-active';
        r2Badge.innerText = 'TRIGGERED (EWA UNLOCKED)';
        r2Desc.innerHTML = `<strong>Earned Wage Access Enabled:</strong> Eligible for zero-interest instant cashout up to <strong>₱${ewaMaxAmount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</strong> (40% accrued earnings) to mitigate mid-cycle liquidity stress.`;
    } else {
        r2Card.className = 'rule-card';
        r2Badge.className = 'rule-badge badge-inactive';
        r2Badge.innerText = 'INACTIVE';
        r2Desc.innerText = 'Standard monthly settlement. Triggers when base salary ≤ ₱30,000 and advance request is flagged.';
    }
}
window.onload = recompute;
</script>
</body>
</html>
"""

class PayrollHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_DASHBOARD.encode("utf-8"))

    def log_message(self, format, *args):
        # Silence routine server access logs in terminal
        return

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PayrollHandler) as httpd:
        print("=" * 60)
        print("  SMARTPAY ADAPTIVE HRIS & PAYROLL SYSTEM")
        print("  Author  : Jude Andrei E. Rabaya")
        print("  Section : CS4D")
        print(f"  Status  : Server running at http://localhost:{PORT}")
        print("=" * 60)
        print(">> Open your browser and navigate to http://localhost:8080")
        print(">> Press Ctrl+C in your terminal to stop the server.")
        try:
            webbrowser.open(f"http://localhost:{PORT}")
        except Exception:
            pass
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
