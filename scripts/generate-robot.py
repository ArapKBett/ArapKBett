#!/usr/bin/env python3
"""
Generate an animated cyberpunk SVG robot with real GitHub data embedded.
Writes robot.svg to the repo root.
"""

import json
import os
import urllib.request
from collections import Counter
from datetime import datetime, timezone

USERNAME = "ArapKBett"
OUTPUT_PATH = "robot.svg"


def fetch_github_api(endpoint):
    """Fetch data from GitHub API with graceful error handling."""
    url = f"https://api.github.com/{endpoint}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": USERNAME,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
            return json.loads(raw.decode())
    except Exception as e:
        print(f"[!] API error for {endpoint}: {e}")
        return None


def fetch_repos_paginated():
    """Fetch repos in pages of 30 to avoid large response failures."""
    all_repos = []
    for page in range(1, 6):  # up to 150 repos
        batch = fetch_github_api(
            f"users/{USERNAME}/repos?per_page=30&page={page}&type=owner&sort=updated"
        )
        if not batch:
            break
        all_repos.extend(batch)
        if len(batch) < 30:
            break
    return all_repos


def get_github_data():
    """Fetch all required GitHub data."""
    user = fetch_github_api(f"users/{USERNAME}") or {}
    repos_raw = fetch_repos_paginated()

    public_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    following = user.get("following", 0)

    total_stars = 0
    total_forks = 0
    lang_counter = Counter()

    for repo in repos_raw:
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)
        lang = repo.get("language")
        if lang:
            lang_counter[lang] += 1

    top_langs = lang_counter.most_common(7)

    return {
        "public_repos": public_repos,
        "total_stars": total_stars,
        "followers": followers,
        "following": following,
        "total_forks": total_forks,
        "top_langs": top_langs,
    }


def make_lang_bars(top_langs):
    """Generate SVG elements for language bars in left panel."""
    if not top_langs:
        return ""
    max_count = max(c for _, c in top_langs) if top_langs else 1
    items = []
    y_start = 220
    bar_max_width = 130
    for i, (lang, count) in enumerate(top_langs):
        y = y_start + i * 30
        bar_w = int((count / max_count) * bar_max_width)
        bar_w = max(bar_w, 4)
        short = lang[:12]
        items.append(
            f'<text x="16" y="{y}" class="mono dim" font-size="9">{short}</text>'
        )
        items.append(
            f'<rect x="16" y="{y+4}" width="{bar_max_width}" height="6" rx="1" fill="#010d00" stroke="#006600" stroke-width="0.5"/>'
        )
        items.append(
            f'<rect x="16" y="{y+4}" width="{bar_w}" height="6" rx="1" fill="#00aa22"/>'
        )
        items.append(
            f'<text x="{16 + bar_max_width + 4}" y="{y+10}" class="mono dim" font-size="8">{count}</text>'
        )
    return "\n".join(items)


def make_stream_items():
    """Generate sliding tech stream items for right panel."""
    techs = [
        "Nmap", "Metasploit", "Burp Suite", "Wireshark", "Hashcat",
        "SQLMap", "John.Ripper", "Aircrack", "Volatility", "YARA",
        "Python3", "Docker", "Kubernetes", "Terraform", "Git",
    ]
    items = []
    for i, tech in enumerate(techs):
        delay = i * 0.8
        dur = 4.5 + (i % 3) * 0.7
        y = 68 + i * 27
        items.append(
            f'<g class="stream-row-{i}" style="animation: stream-item {dur:.1f}s ease-out {delay:.1f}s infinite;">'
            f'<rect x="640" y="{y}" width="240" height="18" rx="2" fill="#010d00" opacity="0.7"/>'
            f'<text x="650" y="{y+13}" class="mono primary" font-size="10">&gt;_ {tech}</text>'
            f'</g>'
        )
    return "\n".join(items)


def make_terminal_lines(data):
    """Build terminal text lines with real data."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "$ whoami",
        f"  {USERNAME}",
        "$ cat /sys/operative/ArapKBett.conf",
        "  [OPERATIVE] ArapKBett",
        "  [ROLE]      Cybersecurity Engineer",
        "  [BASE]      Kenya",
        "  [STATUS]    ACTIVE",
        "$ cat /sys/stats.json",
        f"  repos    : {data['public_repos']}",
        f"  stars    : {data['total_stars']}",
        f"  followers: {data['followers']}",
        f"  forks    : {data['total_forks']}",
        "$ ls /arsenal/",
        "  nmap  msf  burp  hashcat",
        "  yara  docker  k8s  tf",
        "$ systemctl status firewall",
        "  Active: running (armed)",
        "$ ping -c1 adversary.net",
        "  INTERCEPTED: packet nulled",
        f"$ last_sync: {now}",
        "  [OK] all systems nominal",
    ]
    return lines


def build_svg(data):
    """Build the complete SVG string."""
    term_lines = make_terminal_lines(data)
    # Duplicate for seamless scroll loop
    all_term_lines = term_lines + term_lines
    line_height = 14
    single_set_height = len(term_lines) * line_height
    total_term_height = single_set_height * 2

    term_text_items = []
    for i, line in enumerate(all_term_lines):
        y = 10 + i * line_height
        escaped = (
            line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )
        term_text_items.append(
            f'<text x="4" y="{y}" class="mono primary" font-size="8.5">{escaped}</text>'
        )
    term_text_block = "\n".join(term_text_items)

    lang_bars_svg = make_lang_bars(data["top_langs"])
    stream_svg = make_stream_items()

    # Stats table rows
    stats = [
        ("REPOS",     str(data["public_repos"])),
        ("STARS",     str(data["total_stars"])),
        ("FOLLOWERS", str(data["followers"])),
        ("FOLLOWING", str(data["following"])),
        ("FORKS",     str(data["total_forks"])),
    ]
    stats_rows = []
    for i, (label, val) in enumerate(stats):
        y = 80 + i * 22
        stats_rows.append(
            f'<text x="16" y="{y}" class="mono dim" font-size="9">{label}</text>'
            f'<text x="120" y="{y}" class="mono primary" font-size="9">{val}</text>'
        )
    stats_block = "\n".join(stats_rows)

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">
<defs>
  <style>
    .mono {{ font-family: 'Courier New', Courier, monospace; }}
    .primary {{ fill: #00ff41; }}
    .dim {{ fill: #006600; }}
    .accent {{ fill: #00aa22; }}
    .white {{ fill: #ccffcc; }}

    @keyframes blink {{
      0%, 49% {{ opacity: 1; }}
      50%, 100% {{ opacity: 0.1; }}
    }}
    @keyframes blink-slow {{
      0%, 70% {{ opacity: 1; }}
      71%, 100% {{ opacity: 0.15; }}
    }}
    @keyframes pulse-glow {{
      0%, 100% {{ opacity: 1; filter: url(#sglow); }}
      50% {{ opacity: 0.5; filter: url(#glow); }}
    }}
    @keyframes scanline {{
      0% {{ transform: translateY(0px); opacity: 0.06; }}
      100% {{ transform: translateY(500px); opacity: 0.06; }}
    }}
    @keyframes scroll-term {{
      0% {{ transform: translateY(0px); }}
      100% {{ transform: translateY(-{single_set_height}px); }}
    }}
    @keyframes stream-item {{
      0%   {{ opacity: 0;   transform: translateX(0px); }}
      10%  {{ opacity: 1;   transform: translateX(20px); }}
      80%  {{ opacity: 0.9; transform: translateX(200px); }}
      100% {{ opacity: 0;   transform: translateX(220px); }}
    }}
    @keyframes flicker {{
      0%, 95%, 100% {{ opacity: 1; }}
      96% {{ opacity: 0.7; }}
      97% {{ opacity: 1; }}
      98% {{ opacity: 0.5; }}
      99% {{ opacity: 1; }}
    }}
    @keyframes antenna-blink {{
      0%, 60% {{ fill: #00ff41; opacity: 1; }}
      61%, 100% {{ fill: #003300; opacity: 0.3; }}
    }}
    @keyframes seg-blink {{
      0%, 45% {{ fill: #00ff41; }}
      46%, 100% {{ fill: #003300; }}
    }}
  </style>

  <!-- Glow filter -->
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="2.5" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <!-- Strong glow filter -->
  <filter id="sglow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>

  <!-- Terminal clip -->
  <clipPath id="term-clip">
    <rect x="0" y="0" width="148" height="175"/>
  </clipPath>

  <!-- Background grid pattern -->
  <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#00ff41" stroke-width="0.15" opacity="0.2"/>
  </pattern>
</defs>

<!-- ── BACKGROUND ─────────────────────────────────────────── -->
<rect width="900" height="500" fill="#0d1117"/>
<rect width="900" height="500" fill="url(#grid)"/>

<!-- Scanline sweep -->
<rect x="0" y="-30" width="900" height="30" fill="#00ff41" opacity="0.04"
  style="animation: scanline 6s linear infinite;"/>

<!-- Panel dividers -->
<line x1="240" y1="0" x2="240" y2="500" stroke="#00ff41" stroke-width="0.5" opacity="0.4"/>
<line x1="630" y1="0" x2="630" y2="500" stroke="#00ff41" stroke-width="0.5" opacity="0.4"/>

<!-- ── HEADER BAR ──────────────────────────────────────────── -->
<rect x="0" y="0" width="900" height="34" fill="#010d00"/>
<rect x="0" y="33" width="900" height="1" fill="#00ff41" opacity="0.6"/>
<text x="16" y="22" class="mono primary" font-size="11" font-weight="bold"
  filter="url(#glow)">UNIT: ARAP-BOT v2.0 // CYBERSECURITY OPERATIVE</text>
<circle cx="850" cy="17" r="5" fill="#00ff41" style="animation: blink 1.2s step-end infinite;"/>
<circle cx="866" cy="17" r="5" fill="#00aa22" style="animation: blink 1.8s step-end 0.4s infinite;"/>
<circle cx="882" cy="17" r="5" fill="#006600" style="animation: blink 2.4s step-end 0.8s infinite;"/>

<!-- ── LEFT PANEL: SYS_TELEMETRY ──────────────────────────── -->
<rect x="0" y="34" width="240" height="466" fill="#010d00" opacity="0.6"/>
<text x="16" y="58" class="mono primary" font-size="10" font-weight="bold"
  filter="url(#glow)">SYS_TELEMETRY</text>
<line x1="8" y1="64" x2="232" y2="64" stroke="#00aa22" stroke-width="0.5"/>

<!-- Stats table -->
{stats_block}

<line x1="8" y1="196" x2="232" y2="196" stroke="#006600" stroke-width="0.5"/>

<!-- Language distribution label -->
<text x="16" y="212" class="mono accent" font-size="9">LANG_DISTRIBUTION</text>

<!-- Language bars -->
{lang_bars_svg}

<!-- Footer line -->
<line x1="8" y1="436" x2="232" y2="436" stroke="#006600" stroke-width="0.5"/>
<text x="16" y="452" class="mono dim" font-size="8">KERNEL: ARAP-OS v5.0</text>
<text x="16" y="464" class="mono dim" font-size="8">UPTIME: 99.97%</text>

<!-- ── CENTER ROBOT ────────────────────────────────────────── -->
<!-- Robot group centered at x=430 -->
<g transform="translate(430, 54)" style="animation: flicker 8s ease-in-out infinite;">

  <!-- Antenna base -->
  <rect x="-4" y="-38" width="8" height="30" rx="2" fill="#00aa22"/>
  <!-- Antenna arms -->
  <rect x="-28" y="-26" width="24" height="3" rx="1" fill="#006600"/>
  <rect x="4" y="-26" width="24" height="3" rx="1" fill="#006600"/>
  <circle cx="-28" cy="-24" r="4" fill="#00ff41" filter="url(#glow)"
    style="animation: antenna-blink 1.4s step-end infinite;"/>
  <circle cx="28" cy="-24" r="4" fill="#00ff41" filter="url(#glow)"
    style="animation: antenna-blink 1.4s step-end 0.7s infinite;"/>
  <!-- Antenna tip -->
  <circle cx="0" cy="-42" r="6" fill="#00ff41" filter="url(#sglow)"
    style="animation: antenna-blink 0.9s step-end infinite;"/>
  <circle cx="0" cy="-42" r="3" fill="#ccffcc"/>

  <!-- HEAD -->
  <rect x="-55" y="-8" width="110" height="76" rx="6" fill="#010d00" stroke="#00ff41"
    stroke-width="1.5" filter="url(#glow)"/>
  <!-- Head rivets -->
  <circle cx="-48" cy="-2" r="2" fill="#006600"/>
  <circle cx="48" cy="-2" r="2" fill="#006600"/>
  <circle cx="-48" cy="62" r="2" fill="#006600"/>
  <circle cx="48" cy="62" r="2" fill="#006600"/>

  <!-- Eyes -->
  <rect x="-42" y="8" width="32" height="18" rx="3" fill="#001a00" stroke="#00ff41"
    stroke-width="1" style="animation: blink-slow 3.5s step-end infinite;"/>
  <rect x="-38" y="11" width="24" height="12" rx="2" fill="#00ff41" filter="url(#sglow)"
    style="animation: blink-slow 3.5s step-end infinite;"/>
  <rect x="10" y="8" width="32" height="18" rx="3" fill="#001a00" stroke="#00ff41"
    stroke-width="1" style="animation: blink-slow 3.5s step-end 0.3s infinite;"/>
  <rect x="14" y="11" width="24" height="12" rx="2" fill="#00ff41" filter="url(#sglow)"
    style="animation: blink-slow 3.5s step-end 0.3s infinite;"/>

  <!-- Nose sensor -->
  <rect x="-5" y="33" width="10" height="6" rx="2" fill="#006600" stroke="#00aa22" stroke-width="0.8"/>
  <circle cx="0" cy="36" r="2" fill="#00ff41" style="animation: blink 2.1s step-end infinite;"/>

  <!-- Mouth bar - 8 segments -->
  <rect x="-42" y="50" width="84" height="10" rx="2" fill="#001a00" stroke="#006600" stroke-width="0.8"/>
  <rect x="-40" y="52" width="8" height="6" rx="1" fill="#00ff41"
    style="animation: seg-blink 0.6s step-end 0.0s infinite;"/>
  <rect x="-30" y="52" width="8" height="6" rx="1" fill="#00ff41"
    style="animation: seg-blink 0.6s step-end 0.1s infinite;"/>
  <rect x="-20" y="52" width="8" height="6" rx="1" fill="#00ff41"
    style="animation: seg-blink 0.6s step-end 0.2s infinite;"/>
  <rect x="-10" y="52" width="8" height="6" rx="1" fill="#00ff41"
    style="animation: seg-blink 0.6s step-end 0.3s infinite;"/>
  <rect x="2" y="52" width="8" height="6" rx="1" fill="#00ff41"
    style="animation: seg-blink 0.6s step-end 0.4s infinite;"/>
  <rect x="12" y="52" width="8" height="6" rx="1" fill="#00ff41"
    style="animation: seg-blink 0.6s step-end 0.5s infinite;"/>
  <rect x="22" y="52" width="8" height="6" rx="1" fill="#00ff41"
    style="animation: seg-blink 0.6s step-end 0.6s infinite;"/>
  <rect x="32" y="52" width="8" height="6" rx="1" fill="#00ff41"
    style="animation: seg-blink 0.6s step-end 0.7s infinite;"/>

  <!-- NECK -->
  <rect x="-18" y="68" width="36" height="22" rx="2" fill="#010d00" stroke="#006600" stroke-width="1"/>
  <!-- Neck parallel lines -->
  <line x1="-12" y1="72" x2="-12" y2="88" stroke="#00aa22" stroke-width="1.5"/>
  <line x1="-6"  y1="72" x2="-6"  y2="88" stroke="#00aa22" stroke-width="1.5"/>
  <line x1="0"   y1="72" x2="0"   y2="88" stroke="#00aa22" stroke-width="1.5"/>
  <line x1="6"   y1="72" x2="6"   y2="88" stroke="#00aa22" stroke-width="1.5"/>
  <line x1="12"  y1="72" x2="12"  y2="88" stroke="#00aa22" stroke-width="1.5"/>

  <!-- TORSO -->
  <rect x="-72" y="90" width="144" height="130" rx="8" fill="#010d00" stroke="#00ff41"
    stroke-width="1.5" filter="url(#glow)" style="animation: flicker 10s ease-in-out 2s infinite;"/>

  <!-- Chest terminal screen -->
  <rect x="-58" y="100" width="116" height="88" rx="4" fill="#000a00" stroke="#00aa22"
    stroke-width="1"/>
  <!-- Terminal content clip and scroll -->
  <g transform="translate(-56, 104)">
    <g clip-path="url(#term-clip)">
      <g style="animation: scroll-term {len(term_lines) * 0.7:.1f}s linear infinite;">
        {term_text_block}
      </g>
    </g>
  </g>

  <!-- Torso side vents (left) -->
  <rect x="-72" y="102" width="10" height="3" rx="1" fill="#006600"/>
  <rect x="-72" y="110" width="10" height="3" rx="1" fill="#006600"/>
  <rect x="-72" y="118" width="10" height="3" rx="1" fill="#006600"/>
  <rect x="-72" y="126" width="10" height="3" rx="1" fill="#006600"/>
  <!-- Torso side vents (right) -->
  <rect x="62" y="102" width="10" height="3" rx="1" fill="#006600"/>
  <rect x="62" y="110" width="10" height="3" rx="1" fill="#006600"/>
  <rect x="62" y="118" width="10" height="3" rx="1" fill="#006600"/>
  <rect x="62" y="126" width="10" height="3" rx="1" fill="#006600"/>

  <!-- Torso bottom strip -->
  <rect x="-58" y="196" width="116" height="18" rx="3" fill="#010d00" stroke="#006600"
    stroke-width="0.8"/>
  <rect x="-52" y="200" width="20" height="10" rx="2" fill="#00aa22" opacity="0.8"/>
  <rect x="-26" y="200" width="20" height="10" rx="2" fill="#006600"/>
  <rect x="0"   y="200" width="20" height="10" rx="2" fill="#00ff41"
    style="animation: blink 1.5s step-end infinite;"/>
  <rect x="26"  y="200" width="20" height="10" rx="2" fill="#006600"/>

  <!-- LEFT ARM -->
  <!-- Shoulder joint (left) -->
  <circle cx="-88" cy="108" r="14" fill="#010d00" stroke="#00ff41" stroke-width="1.5"
    filter="url(#sglow)" style="animation: pulse-glow 2s ease-in-out infinite;"/>
  <circle cx="-88" cy="108" r="8" fill="#00ff41" opacity="0.8"
    style="animation: pulse-glow 2s ease-in-out infinite;"/>
  <!-- Upper arm (left) -->
  <rect x="-106" y="120" width="22" height="65" rx="5" fill="#010d00" stroke="#00aa22"
    stroke-width="1"/>
  <!-- Elbow joint (left) -->
  <circle cx="-95" cy="192" r="9" fill="#010d00" stroke="#006600" stroke-width="1"/>
  <!-- Forearm (left) -->
  <rect x="-106" y="196" width="22" height="55" rx="5" fill="#010d00" stroke="#006600"
    stroke-width="1"/>
  <!-- Hand (left) -->
  <rect x="-110" y="250" width="30" height="16" rx="4" fill="#010d00" stroke="#00aa22"
    stroke-width="1"/>

  <!-- RIGHT ARM -->
  <!-- Shoulder joint (right) -->
  <circle cx="88" cy="108" r="14" fill="#010d00" stroke="#00ff41" stroke-width="1.5"
    filter="url(#sglow)" style="animation: pulse-glow 2s ease-in-out 1s infinite;"/>
  <circle cx="88" cy="108" r="8" fill="#00ff41" opacity="0.8"
    style="animation: pulse-glow 2s ease-in-out 1s infinite;"/>
  <!-- Upper arm (right) -->
  <rect x="84" y="120" width="22" height="65" rx="5" fill="#010d00" stroke="#00aa22"
    stroke-width="1"/>
  <!-- Elbow joint (right) -->
  <circle cx="95" cy="192" r="9" fill="#010d00" stroke="#006600" stroke-width="1"/>
  <!-- Forearm (right) -->
  <rect x="84" y="196" width="22" height="55" rx="5" fill="#010d00" stroke="#006600"
    stroke-width="1"/>
  <!-- Hand (right) -->
  <rect x="80" y="250" width="30" height="16" rx="4" fill="#010d00" stroke="#00aa22"
    stroke-width="1"/>

  <!-- HIP -->
  <rect x="-60" y="220" width="120" height="20" rx="4" fill="#010d00" stroke="#006600"
    stroke-width="1"/>
  <rect x="-50" y="224" width="40" height="12" rx="2" fill="#001a00" stroke="#006600"
    stroke-width="0.6"/>
  <rect x="10" y="224" width="40" height="12" rx="2" fill="#001a00" stroke="#006600"
    stroke-width="0.6"/>

  <!-- LEFT LEG -->
  <rect x="-54" y="240" width="38" height="75" rx="5" fill="#010d00" stroke="#00aa22"
    stroke-width="1"/>
  <!-- Knee joint (left) -->
  <rect x="-52" y="280" width="34" height="12" rx="3" fill="#001a00" stroke="#006600"
    stroke-width="0.8"/>
  <!-- Shin (left) -->
  <rect x="-50" y="315" width="30" height="50" rx="4" fill="#010d00" stroke="#006600"
    stroke-width="1"/>
  <!-- Foot (left) -->
  <rect x="-58" y="362" width="46" height="14" rx="4" fill="#010d00" stroke="#00aa22"
    stroke-width="1"/>

  <!-- RIGHT LEG -->
  <rect x="16" y="240" width="38" height="75" rx="5" fill="#010d00" stroke="#00aa22"
    stroke-width="1"/>
  <!-- Knee joint (right) -->
  <rect x="18" y="280" width="34" height="12" rx="3" fill="#001a00" stroke="#006600"
    stroke-width="0.8"/>
  <!-- Shin (right) -->
  <rect x="20" y="315" width="30" height="50" rx="4" fill="#010d00" stroke="#006600"
    stroke-width="1"/>
  <!-- Foot (right) -->
  <rect x="12" y="362" width="46" height="14" rx="4" fill="#010d00" stroke="#00aa22"
    stroke-width="1"/>

</g>
<!-- ── END ROBOT ───────────────────────────────────────────── -->

<!-- ── RIGHT PANEL: TECH_STREAM ──────────────────────────── -->
<rect x="630" y="34" width="270" height="466" fill="#010d00" opacity="0.6"/>
<text x="642" y="58" class="mono primary" font-size="10" font-weight="bold"
  filter="url(#glow)">TECH_STREAM // LIVE</text>
<line x1="638" y1="64" x2="892" y2="64" stroke="#00aa22" stroke-width="0.5"/>

<!-- Stream items - clipped to panel -->
<g>
  <clipPath id="stream-clip">
    <rect x="630" y="65" width="270" height="430"/>
  </clipPath>
  <g clip-path="url(#stream-clip)">
    {stream_svg}
  </g>
</g>

<!-- ── FOOTER BAR ─────────────────────────────────────────── -->
<rect x="0" y="480" width="900" height="20" fill="#010d00"/>
<rect x="0" y="480" width="900" height="1" fill="#00ff41" opacity="0.4"/>
<text x="16" y="494" class="mono dim" font-size="8">
  CONTACTS: bettarap254@gmail.com | github.com/ArapKBett | x.com/kp15_5 | arapbett.onrender.com
</text>
<text x="820" y="494" class="mono dim" font-size="8">SYNC: {now_str}</text>

</svg>"""

    return svg


def main():
    print("[*] Fetching GitHub data for robot SVG...")
    data = get_github_data()
    print(f"[+] Stats: repos={data['public_repos']}, stars={data['total_stars']}, "
          f"followers={data['followers']}, forks={data['total_forks']}")
    print(f"[+] Top langs: {data['top_langs']}")

    print("[*] Building SVG...")
    svg_content = build_svg(data)

    with open(OUTPUT_PATH, "w") as f:
        f.write(svg_content)
    print(f"[+] robot.svg written ({len(svg_content)} bytes)")


if __name__ == "__main__":
    main()
