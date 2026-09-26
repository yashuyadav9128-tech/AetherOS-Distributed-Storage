"""
AetherStore Futuristic Web Dashboard
Theme: Deep Space Mission Control / Nebula Hologram with interactive Visual Cluster Ring,
Blade Server Rack, Dynamic Chaos Engineering HUD, and Multi-Theme Switching.
"""

def get_dashboard_html():
    return """<!DOCTYPE html>
<html lang="en" data-theme="ice">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOS // Distributed Storage Mission Control</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
    <style>
        :root, [data-theme="cyberpunk"] {
            /* Tokyo Cyberpunk Neon (Default) */
            --bg-deep: #060714;
            --bg-surface: rgba(14, 18, 38, 0.82);
            --bg-surface-elevated: rgba(24, 30, 60, 0.75);
            --border-glow: rgba(0, 245, 255, 0.45);
            --border-hairline: rgba(255, 0, 127, 0.25);
            --text-primary: #ffffff;
            --text-secondary: #c7d2fe;
            --text-muted: #818cf8;
            --accent-cyan: #00f5ff;
            --accent-indigo: #a855f7;
            --accent-pink: #ff007f;
            --accent-emerald: #00ff88;
            --accent-amber: #ffb703;
            --accent-rose: #ff0055;
            --ring-glow: rgba(0, 245, 255, 0.35);
            --card-glass: blur(18px);
            --orb-gradient: linear-gradient(135deg, #ff007f, #7928ca, #00f5ff);
            --btn-repair-grad: linear-gradient(135deg, #ec4899, #8b5cf6);
        }

        [data-theme="ice"] {
            /* Ocean Depth Blue */
            --bg-deep: #010a1a;
            --bg-surface: rgba(4, 20, 55, 0.90);
            --bg-surface-elevated: rgba(7, 35, 90, 0.85);
            --border-glow: rgba(37, 150, 255, 0.60);
            --border-hairline: rgba(59, 130, 246, 0.28);
            --text-primary: #e8f4ff;
            --text-secondary: #93c5fd;
            --text-muted: #3b82f6;
            --accent-cyan: #2596ff;
            --accent-indigo: #60a5fa;
            --accent-pink: #818cf8;
            --accent-emerald: #34d399;
            --accent-amber: #fbbf24;
            --accent-rose: #f87171;
            --ring-glow: rgba(37, 150, 255, 0.40);
            --card-glass: blur(20px);
            --orb-gradient: linear-gradient(135deg, #0047ab, #2596ff, #60a5fa);
            --btn-repair-grad: linear-gradient(135deg, #1d4ed8, #2596ff);
        }

        [data-theme="matrix"] {
            /* Cyber Matrix Emerald */
            --bg-deep: #020b06;
            --bg-surface: rgba(4, 30, 16, 0.85);
            --bg-surface-elevated: rgba(6, 46, 25, 0.8);
            --border-glow: rgba(0, 255, 136, 0.5);
            --border-hairline: rgba(0, 255, 136, 0.2);
            --text-primary: #f0fdf4;
            --text-secondary: #86efac;
            --text-muted: #15803d;
            --accent-cyan: #00ff88;
            --accent-indigo: #10b981;
            --accent-pink: #f43f5e;
            --accent-emerald: #00ff88;
            --accent-amber: #eab308;
            --accent-rose: #ff3366;
            --ring-glow: rgba(0, 255, 136, 0.3);
            --card-glass: blur(18px);
            --orb-gradient: linear-gradient(135deg, #059669, #10b981, #00ff88);
            --btn-repair-grad: linear-gradient(135deg, #059669, #10b981);
        }

        [data-theme="inferno"] {
            /* Crimson Inferno */
            --bg-deep: #0f0508;
            --bg-surface: rgba(36, 12, 18, 0.85);
            --bg-surface-elevated: rgba(54, 18, 28, 0.8);
            --border-glow: rgba(255, 51, 102, 0.5);
            --border-hairline: rgba(255, 153, 0, 0.25);
            --text-primary: #fff1f2;
            --text-secondary: #fecdd3;
            --text-muted: #be123c;
            --accent-cyan: #ff9900;
            --accent-indigo: #ff3366;
            --accent-pink: #ff0055;
            --accent-emerald: #10b981;
            --accent-amber: #ffaa00;
            --accent-rose: #ff2a5f;
            --ring-glow: rgba(255, 51, 102, 0.35);
            --card-glass: blur(18px);
            --orb-gradient: linear-gradient(135deg, #ff0055, #ff5500, #ffaa00);
            --btn-repair-grad: linear-gradient(135deg, #ff0055, #ff5500);
        }


        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.12) 0%, transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(56, 189, 248, 0.1) 0%, transparent 45%),
                linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
            color: var(--text-primary);
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
            padding: 24px 32px;
            overflow-x: hidden;
        }

        .container {
            max-width: 1440px;
            margin: 0 auto;
        }

        /* Top HUD Bar */
        .hud-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 24px;
            background: var(--bg-surface);
            border: 1px solid var(--border-hairline);
            border-radius: 18px;
            backdrop-filter: var(--card-glass);
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }

        .brand-cluster {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .brand-orb {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, #0ea5e9, #6366f1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: white;
            box-shadow: 0 0 24px rgba(14, 165, 233, 0.6);
            position: relative;
        }

        .brand-orb::after {
            content: '';
            position: absolute;
            inset: -2px;
            border-radius: 14px;
            background: linear-gradient(135deg, #38bdf8, transparent, #818cf8);
            z-index: -1;
            opacity: 0.7;
        }

        .brand-title h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-tag {
            font-size: 10px;
            font-family: 'JetBrains Mono', monospace;
            padding: 2px 8px;
            border-radius: 6px;
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .brand-title p {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 2px;
            font-family: 'JetBrains Mono', monospace;
        }

        .header-controls {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .theme-select {
            background: var(--bg-surface-elevated);
            color: var(--text-primary);
            border: 1px solid var(--border-hairline);
            padding: 8px 14px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            outline: none;
            transition: all 0.2s ease;
        }

        .theme-select:hover {
            border-color: var(--accent-cyan);
        }

        /* Mission Control Action Deck */
        .deck-banner {
            background: var(--bg-surface);
            border: 1px solid var(--border-hairline);
            border-radius: 18px;
            padding: 18px 24px;
            backdrop-filter: var(--card-glass);
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            position: relative;
            overflow: hidden;
        }

        .deck-banner::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: linear-gradient(180deg, var(--accent-cyan), var(--accent-indigo));
        }

        .deck-label {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .deck-sub {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 2px;
        }

        .action-button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .btn {
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-hairline);
            color: var(--text-primary);
            padding: 9px 16px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            user-select: none;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-kill {
            border-color: rgba(244, 63, 94, 0.4);
            color: #fda4af;
        }
        .btn-kill:hover {
            background: rgba(244, 63, 94, 0.15);
            border-color: var(--accent-rose);
        }

        .btn-revive {
            border-color: rgba(16, 185, 129, 0.4);
            color: #6ee7b7;
        }
        .btn-revive:hover {
            background: rgba(16, 185, 129, 0.15);
            border-color: var(--accent-emerald);
        }

        .btn-corrupt {
            border-color: rgba(245, 158, 11, 0.4);
            color: #fde68a;
        }
        .btn-corrupt:hover {
            background: rgba(245, 158, 11, 0.15);
            border-color: var(--accent-amber);
        }

        .btn-repair {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            border: none;
            color: white;
            box-shadow: 0 4px 16px rgba(2, 132, 199, 0.4);
        }
        .btn-repair:hover {
            background: linear-gradient(135deg, #0369a1, #1d4ed8);
            box-shadow: 0 6px 24px rgba(2, 132, 199, 0.6);
        }

        .btn-rebalance {
            border-color: rgba(139, 92, 246, 0.4);
            color: #c4b5fd;
        }
        .btn-rebalance:hover {
            background: rgba(139, 92, 246, 0.15);
            border-color: #a78bfa;
        }

        /* Metric Grid */
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .metric-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-hairline);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: var(--card-glass);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            border-color: var(--border-glow);
            transform: translateY(-2px);
        }

        .metric-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--border-glow), transparent);
        }

        .metric-title {
            font-size: 11px;
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .metric-value {
            font-size: 28px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-primary);
        }

        .metric-sub {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 6px;
        }

        /* Visual Ring & Rack Layout */
        .topology-split {
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }

        @media (max-width: 1180px) {
            .topology-split {
                grid-template-columns: 1fr;
            }
        }

        .card-main {
            background: var(--bg-surface);
            border: 1px solid var(--border-hairline);
            border-radius: 18px;
            padding: 24px;
            backdrop-filter: var(--card-glass);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        }

        .card-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-hairline);
        }

        .card-head-title {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: -0.3px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Circular Hash Ring Diagram */
        .ring-diagram-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 10px 0;
            position: relative;
        }

        .ring-canvas {
            width: 280px;
            height: 280px;
            position: relative;
        }

        .ring-center-info {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            pointer-events: none;
        }

        .ring-center-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 14px;
            font-weight: 700;
            color: var(--accent-cyan);
        }

        .ring-center-sub {
            font-size: 10px;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-secondary);
        }

        /* Blade Server Rack View */
        .blade-rack {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }

        .blade-chassis {
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-hairline);
            border-radius: 14px;
            padding: 18px;
            position: relative;
            transition: all 0.25s ease;
        }

        .blade-chassis:hover {
            border-color: var(--border-glow);
            transform: translateY(-2px);
        }

        .blade-chassis.online {
            border-left: 4px solid var(--accent-emerald);
        }

        .blade-chassis.dead {
            border-left: 4px solid var(--accent-rose);
            opacity: 0.65;
            background: rgba(30, 15, 20, 0.4);
        }

        .blade-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .blade-id {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-beacon {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }

        .status-beacon.online {
            background: var(--accent-emerald);
            box-shadow: 0 0 10px var(--accent-emerald);
            animation: pulse-beacon 2s infinite;
        }

        .status-beacon.dead {
            background: var(--accent-rose);
            box-shadow: 0 0 10px var(--accent-rose);
        }

        @keyframes pulse-beacon {
            0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        .blade-endpoint {
            font-size: 12px;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }

        .gauge-track {
            height: 7px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 12px;
        }

        .gauge-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-emerald));
            border-radius: 4px;
            transition: width 0.5s ease;
        }

        .blade-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .blade-pill {
            font-size: 11px;
            padding: 3px 8px;
            background: rgba(56, 189, 248, 0.12);
            color: var(--accent-cyan);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
        }

        /* Dual Section: Replica Matrix & Terminal Log */
        .bottom-split {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }

        @media (max-width: 1024px) {
            .bottom-split {
                grid-template-columns: 1fr;
            }
        }

        /* Matrix Table */
        .table-wrap {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th {
            text-align: left;
            padding: 12px 14px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-hairline);
            font-family: 'Space Grotesk', sans-serif;
        }

        td {
            padding: 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }

        .rep-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }

        .rep-healthy {
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .rep-degraded {
            background: rgba(245, 158, 11, 0.15);
            color: var(--accent-amber);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        /* Cyber Console Terminal */
        .terminal-box {
            background: #02050b;
            border: 1px solid var(--border-hairline);
            border-radius: 14px;
            padding: 18px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            height: 380px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-shadow: inset 0 0 24px rgba(0, 0, 0, 0.8);
        }

        .terminal-line {
            display: flex;
            gap: 10px;
            line-height: 1.6;
        }

        .t-time {
            color: var(--text-muted);
            flex-shrink: 0;
        }

        .t-ok {
            color: var(--accent-emerald);
            font-weight: 700;
        }

        .t-warn {
            color: var(--accent-amber);
            font-weight: 700;
        }

        .t-info {
            color: var(--accent-cyan);
            font-weight: 700;
        }

        /* Live Toast Notification */
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--bg-surface);
            border: 1px solid var(--border-glow);
            color: var(--text-primary);
            padding: 14px 22px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: none;
            backdrop-filter: blur(12px);
            z-index: 1000;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 13px;
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Top HUD Header -->
        <header class="hud-header">
            <div class="brand-cluster">
                <div class="brand-orb">&#x25C7;</div>
                <div class="brand-title">
                    <h1>AetherOS Distributed Storage <span class="brand-tag" id="status-pill">QUORUM HEALTHY</span></h1>
                    <p>ENGINE: CONSISTENT HASH RING &bull; RF=3 &bull; SELF-HEALING CRYPTO ENGINE</p>
                </div>
            </div>
            <div class="header-controls">
                <select class="theme-select" id="theme-switcher" onchange="changeTheme(this.value)">
                    <option value="nebula">🌌 Nebula Obsidian</option>
                    <option value="matrix">⚡ Cyber Matrix</option>
                    <option value="solar">☀️ Solar Flare</option>
                </select>
                <button class="btn" onclick="fetchStatus()">&#x21BB; Refresh</button>
            </div>
        </header>

        <!-- Mission Control Interactive Action Deck -->
        <section class="deck-banner">
            <div>
                <div class="deck-label">
                    <span>&#x25C6;</span> Chaos Engineering & Cluster Operations Console
                </div>
                <div class="deck-sub">Direct hardware failure injection, fault detection, and autonomic healing:</div>
            </div>
            <div class="action-button-group">
                <button class="btn btn-kill" onclick="triggerStopNode('Node-2')">&#x25A0; Kill Node-2</button>
                <button class="btn btn-revive" onclick="triggerRestartNode('Node-2')">&#x25B6; Revive Node-2</button>
                <button class="btn btn-corrupt" onclick="triggerCorrupt('Node-3')">&#x26A1; Corrupt Node-3</button>
                <button class="btn btn-repair" onclick="triggerRepair()">&#x1F6E1; Auto-Repair</button>
                <button class="btn btn-rebalance" onclick="triggerRebalance()">&#x2696; Rebalance Ring</button>
            </div>
        </section>

        <!-- Metric Telemetry Cards -->
        <section class="metric-grid">
            <div class="metric-card">
                <div class="metric-title">
                    <span>Node Quorum</span>
                    <span style="color: var(--accent-cyan);">&#x25A3;</span>
                </div>
                <div class="metric-value" id="val-nodes">-- / --</div>
                <div class="metric-sub">Active physical instances</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">
                    <span>Replication Factor</span>
                    <span style="color: var(--accent-indigo);">&#x25C9;</span>
                </div>
                <div class="metric-value">RF = 3</div>
                <div class="metric-sub">Strict redundancy invariant</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">
                    <span>Cluster Health</span>
                    <span style="color: var(--accent-emerald);">&#x2714;</span>
                </div>
                <div class="metric-value" id="val-health" style="color: var(--accent-emerald);">HEALTHY</div>
                <div class="metric-sub" id="val-health-sub">All invariants satisfied</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">
                    <span>Stored Objects</span>
                    <span style="color: var(--accent-amber);">&#x2261;</span>
                </div>
                <div class="metric-value" id="val-objects">1</div>
                <div class="metric-sub">100.00 MB payload (SHA-256 verified)</div>
            </div>
        </section>

        <!-- Topology Split: Circular Ring + Server Blades -->
        <div class="topology-split">
            <!-- Circular Hash Ring Visualization -->
            <div class="card-main">
                <div class="card-head">
                    <div class="card-head-title">&#x25CE; Hash Ring Topology</div>
                </div>
                <div class="ring-diagram-wrap">
                    <canvas id="ringCanvas" width="280" height="280" class="ring-canvas"></canvas>
                    <div class="ring-center-info">
                        <div class="ring-center-title">128-BIT</div>
                        <div class="ring-center-sub">CONSISTENT RING</div>
                    </div>
                </div>
                <p style="font-size: 11px; color: var(--text-muted); text-align: center; margin-top: 10px; font-family: 'JetBrains Mono';">
                    64 Virtual Nodes / Instance
                </p>
            </div>

            <!-- Server Blade Rack -->
            <div class="card-main">
                <div class="card-head">
                    <div class="card-head-title">&#x25A4; Storage Node Blade Chassis</div>
                    <span style="font-size: 12px; color: var(--text-secondary); font-family: 'JetBrains Mono';" id="rack-sub">6 Nodes Configured</span>
                </div>
                <div class="blade-rack" id="nodes-rack">
                    <!-- Dynamic Blade Cards -->
                </div>
            </div>
        </div>

        <!-- Bottom Split: Matrix Table + Cyber Console -->
        <div class="bottom-split">
            <!-- Replica Placement Matrix -->
            <div class="card-main">
                <div class="card-head">
                    <div class="card-head-title">&#x2630; Replica Placement Matrix</div>
                </div>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Object Key</th>
                                <th>Size</th>
                                <th>Target RF</th>
                                <th>Health</th>
                                <th>Replica Nodes</th>
                                <th>Integrity</th>
                            </tr>
                        </thead>
                        <tbody id="matrix-tbody">
                            <tr>
                                <td colspan="6" style="text-align: center; color: var(--text-muted);">Syncing cluster catalog...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Live Cyber Terminal Stream -->
            <div class="card-main">
                <div class="card-head">
                    <div class="card-head-title">&#x25A6; Autonomic Event Stream</div>
                    <span style="font-size: 11px; color: var(--accent-cyan); font-family: 'JetBrains Mono';">LIVE SCRUBBER</span>
                </div>
                <div class="terminal-box" id="terminal-logs">
                    <div class="terminal-line">
                        <span class="t-time">[00:00:00]</span>
                        <span class="t-info">[INIT]</span>
                        <span>Telemetry stream connected to Coordinator:8000</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast" id="toast">Operation executed</div>

    <script>
        let clusterData = null;

        function changeTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            drawRing();
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.style.display = 'block';
            setTimeout(() => { t.style.display = 'none'; }, 3000);
        }

        async function fetchStatus() {
            try {
                const res = await fetch('/api/cluster/status');
                clusterData = await res.json();
                renderUI(clusterData);
                drawRing();
            } catch (err) {
                console.error("Telemetry fetch failed:", err);
            }
        }

        async function triggerRepair() {
            try {
                await fetch('/api/cluster/repair_all', { method: 'POST' });
                showToast("Auto-Repair triggered: self-healing from clean donor replicas!");
                fetchStatus();
            } catch (err) {
                showToast("Repair failed: " + err.message);
            }
        }

        async function triggerStopNode(nodeId) {
            try {
                await fetch(`/api/nodes/stop?node_id=${nodeId}`, { method: 'POST' });
                showToast(`Node '${nodeId}' stopped! Failover active.`);
                fetchStatus();
            } catch (err) {
                showToast("Error: " + err.message);
            }
        }

        async function triggerRestartNode(nodeId) {
            try {
                await fetch(`/api/demo/restart_node?node_id=${nodeId}`, { method: 'POST' });
                showToast(`Node '${nodeId}' revived and marked ONLINE!`);
                fetchStatus();
            } catch (err) {
                showToast("Error: " + err.message);
            }
        }

        async function triggerCorrupt(nodeId) {
            try {
                await fetch(`/api/demo/corrupt?node_id=${nodeId}&key=dataset_100mb.bin`, { method: 'POST' });
                showToast(`Bit-rot injected into ${nodeId} replica!`);
                fetchStatus();
            } catch (err) {
                showToast("Error: " + err.message);
            }
        }

        async function triggerRebalance() {
            try {
                await fetch('/api/cluster/rebalance', { method: 'POST' });
                showToast("Cluster rebalancing completed across all active nodes!");
                fetchStatus();
            } catch (err) {
                showToast("Error: " + err.message);
            }
        }

        function renderUI(data) {
            // Metrics
            document.getElementById('val-nodes').innerText = `${data.summary.online_nodes} / ${data.summary.total_nodes}`;
            document.getElementById('rack-sub').innerText = `${data.summary.total_nodes} Total Nodes (${data.summary.online_nodes} Online)`;
            
            const healthEl = document.getElementById('val-health');
            const pillEl = document.getElementById('status-pill');
            const isHealthy = data.summary.cluster_health === 'HEALTHY';
            healthEl.innerText = data.summary.cluster_health;
            healthEl.style.color = isHealthy ? 'var(--accent-emerald)' : 'var(--accent-amber)';
            pillEl.innerText = isHealthy ? 'QUORUM HEALTHY' : 'REDUNDANCY DEGRADED';
            pillEl.style.color = isHealthy ? 'var(--accent-emerald)' : 'var(--accent-amber)';

            // Server Blades
            const rack = document.getElementById('nodes-rack');
            rack.innerHTML = '';
            for (const [nid, info] of Object.entries(data.nodes)) {
                const isOnline = info.status === 'ONLINE';
                const card = document.createElement('div');
                card.className = `blade-chassis ${isOnline ? 'online' : 'dead'}`;
                
                const pillsHtml = (info.keys || []).map(k => `<span class="blade-pill">${k}</span>`).join('') || '<span style="color: var(--text-muted); font-size: 11px;">Empty Node</span>';
                
                card.innerHTML = `
                    <div class="blade-head">
                        <div class="blade-id">
                            <span class="status-beacon ${isOnline ? 'online' : 'dead'}"></span>
                            ${nid}
                        </div>
                        <span style="font-size: 11px; font-weight: 700; color: ${isOnline ? 'var(--accent-emerald)' : 'var(--accent-rose)'}; font-family: 'JetBrains Mono';">${info.status}</span>
                    </div>
                    <div class="blade-endpoint">Port ${info.port} &bull; ${info.disk_used_mb || 0} MB Allocated</div>
                    <div class="gauge-track">
                        <div class="gauge-fill" style="width: ${Math.min(100, Math.max(8, ((info.disk_used_mb || 0) / 100) * 100))}%;"></div>
                    </div>
                    <div class="blade-pills">
                        ${pillsHtml}
                    </div>
                `;
                rack.appendChild(card);
            }

            // Matrix Table
            const tbody = document.getElementById('matrix-tbody');
            const objs = Object.entries(data.objects);
            if (objs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No objects in catalog</td></tr>';
            } else {
                tbody.innerHTML = '';
                for (const [k, obj] of objs) {
                    const healthyNodes = (obj.replicas || []).filter(nid => data.nodes[nid] && data.nodes[nid].status === 'ONLINE');
                    const ok = healthyNodes.length >= obj.rf;
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td style="font-family: 'JetBrains Mono'; font-weight: 600;">${k}</td>
                        <td>${(obj.size / (1024*1024)).toFixed(2)} MB</td>
                        <td>RF=${obj.rf}</td>
                        <td><span class="rep-badge ${ok ? 'rep-healthy' : 'rep-degraded'}">${healthyNodes.length}/${obj.rf} REPLICAS</span></td>
                        <td>
                            ${(obj.replicas || []).map(nid => {
                                const on = data.nodes[nid] && data.nodes[nid].status === 'ONLINE';
                                return `<span style="font-family: 'JetBrains Mono'; margin-right: 6px; color: ${on ? 'var(--accent-cyan)' : 'var(--accent-rose)'}; font-weight: 600;">[${nid}]</span>`;
                            }).join('')}
                        </td>
                        <td style="font-family: 'JetBrains Mono'; font-size: 11px; color: var(--text-secondary);" title="${obj.sha256}">${(obj.sha256 || '').substring(0, 14)}...</td>
                    `;
                    tbody.appendChild(row);
                }
            }

            // Live Terminal Event Log
            if (data.recent_events && data.recent_events.length > 0) {
                const term = document.getElementById('terminal-logs');
                term.innerHTML = '';
                for (const evt of data.recent_events) {
                    const row = document.createElement('div');
                    row.className = 'terminal-line';
                    let badge = '<span class="t-info">[INFO]</span>';
                    if (evt.level === 'OK') badge = '<span class="t-ok">[OK]</span>';
                    if (evt.level === 'WARN') badge = '<span class="t-warn">[WARN]</span>';
                    
                    row.innerHTML = `
                        <span class="t-time">[${evt.time}]</span>
                        ${badge}
                        <span>${evt.message}</span>
                    `;
                    term.appendChild(row);
                }
                term.scrollTop = term.scrollHeight;
            }
        }

        // Draw Interactive Circular Hash Ring Canvas
        function drawRing() {
            const canvas = document.getElementById('ringCanvas');
            if (!canvas || !clusterData) return;
            const ctx = canvas.getContext('2d');
            const w = canvas.width;
            const h = canvas.height;
            const cx = w / 2;
            const cy = h / 2;
            const radius = 100;

            ctx.clearRect(0, 0, w, h);

            // Ring track
            ctx.beginPath();
            ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
            ctx.lineWidth = 3;
            ctx.stroke();

            const nodeEntries = Object.entries(clusterData.nodes);
            const totalNodes = nodeEntries.length;
            if (totalNodes === 0) return;

            // Draw nodes on the ring
            nodeEntries.forEach(([nid, info], i) => {
                const angle = (i / totalNodes) * 2 * Math.PI - Math.PI / 2;
                const nx = cx + radius * Math.cos(angle);
                const ny = cy + radius * Math.sin(angle);
                const isOnline = info.status === 'ONLINE';

                // Node outer glow
                ctx.beginPath();
                ctx.arc(nx, ny, 16, 0, 2 * Math.PI);
                ctx.fillStyle = isOnline ? 'rgba(16, 185, 129, 0.2)' : 'rgba(244, 63, 94, 0.2)';
                ctx.fill();

                // Node circle
                ctx.beginPath();
                ctx.arc(nx, ny, 10, 0, 2 * Math.PI);
                ctx.fillStyle = isOnline ? '#10b981' : '#f43f5e';
                ctx.fill();
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // Node Label
                ctx.font = '10px "JetBrains Mono"';
                ctx.fillStyle = isOnline ? '#94a3b8' : '#fda4af';
                ctx.textAlign = 'center';
                const labelRadius = radius + 24;
                const lx = cx + labelRadius * Math.cos(angle);
                const ly = cy + labelRadius * Math.sin(angle) + 4;
                ctx.fillText(nid, lx, ly);
            });
        }

        // Auto-poll every 1.5 seconds
        setInterval(fetchStatus, 1500);
        fetchStatus();
    </script>
</body>
</html>
"""
