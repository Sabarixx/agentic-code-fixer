"""
Refined CSS styles for Agentic Code Fixer.
Matches reference design with grid hero, polished buttons, zero-glitch navbar, and sleek cards.
"""

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Reset & Base */
*, *::before, *::after {
    box-sizing: border-box;
}

html, body, [class*="st-"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Global link reset: remove all default underlines & browser styling */
a, a:visited, a:hover, a:active, a:focus,
[data-testid="stMarkdownContainer"] a,
[data-testid="stMarkdownContainer"] a:visited,
[data-testid="stMarkdownContainer"] a:hover,
[data-testid="stMarkdownContainer"] a:active,
[data-testid="stMarkdownContainer"] a:focus {
    text-decoration: none !important;
    color: inherit;
}

/* Background & Streamlit Container */
.stApp {
    background-color: #f3eee6 !important;
    background-image: 
        linear-gradient(rgba(215, 207, 192, 0.35) 1px, transparent 1px),
        linear-gradient(90deg, rgba(215, 207, 192, 0.35) 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
    color: #12181c !important;
}

/* Clean Header Removal */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    display: none !important;
}

.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1220px !important;
}

#MainMenu, footer { visibility: hidden !important; }

/* ==================== TOP NAVIGATION ==================== */
.hero-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0 2rem 0;
    margin-bottom: 2rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.nav-brand-logo {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    font-weight: 800;
    font-size: 1.15rem;
    letter-spacing: -0.02em;
    color: #12181c;
    text-decoration: none !important;
}

.logo-badge {
    width: 32px;
    height: 32px;
    background: #12181c;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-weight: 800;
    font-size: 1.05rem;
    position: relative;
    box-shadow: 0 2px 5px rgba(0,0,0,0.15);
}

.logo-dot {
    position: absolute;
    top: -2px;
    right: -2px;
    width: 9px;
    height: 9px;
    background: #e25a38;
    border: 2px solid #f3eee6;
    border-radius: 50%;
}

.nav-center-menu {
    display: flex;
    gap: 0.8rem;
    font-weight: 600;
    font-size: 0.92rem;
    color: #4a555e;
}

.nav-right-actions {
    display: flex;
    align-items: center;
    gap: 1.2rem;
}

.nav-link-item {
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    color: #4a555e !important;
    cursor: pointer !important;
    text-decoration: none !important;
    padding: 0.45rem 0.85rem !important;
    border-radius: 8px !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
    display: inline-flex !important;
    align-items: center !important;
}

.nav-link-item:hover {
    color: #12181c !important;
    background-color: rgba(18, 24, 28, 0.06) !important;
    text-decoration: none !important;
}

.nav-link-item.enterprise-link {
    color: #12181c !important;
    font-weight: 600 !important;
}

.btn-start-fixing {
    background: #12181c !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.35rem !important;
    border-radius: 9999px !important;
    text-decoration: none !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    border: 1px solid transparent !important;
    box-shadow: 0 2px 8px rgba(18, 24, 28, 0.15) !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.btn-start-fixing:hover {
    transform: translateY(-1px) !important;
    background: #252e35 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(18, 24, 28, 0.25) !important;
    text-decoration: none !important;
}

.btn-start-fixing .arrow-icon {
    transition: transform 0.18s ease;
}

.btn-start-fixing:hover .arrow-icon {
    transform: translateX(3px);
}

/* ==================== FRONT PAGE HERO ==================== */
.hero-front-grid {
    display: grid;
    grid-template-columns: 1.15fr 0.95fr;
    gap: 3.5rem;
    align-items: center;
    padding: 1.5rem 0 4.5rem 0;
    position: relative;
}

.hero-tagline-wrap {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #0d6e6e;
    margin-bottom: 1.2rem;
}

.tag-red-dot {
    width: 8px;
    height: 8px;
    background: #0d6e6e;
    border-radius: 50%;
    display: inline-block;
}

.hero-display-heading {
    font-size: 4.5rem;
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.04em;
    color: #12181c;
    margin-bottom: 1.4rem;
}

.heading-proof-teal {
    color: #0d6e6e;
    display: block;
}

.hero-subtext {
    font-size: 1.15rem;
    line-height: 1.6;
    color: #4a555e;
    max-width: 520px;
    margin-bottom: 2.2rem;
}

.hero-cta-row {
    display: flex;
    align-items: center;
    gap: 1.4rem;
    margin-bottom: 2.8rem;
}

.btn-try-fixer {
    background: #0d6e6e !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.85rem 1.65rem !important;
    border-radius: 9999px !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.55rem !important;
    cursor: pointer !important;
    border: none !important;
    text-decoration: none !important;
    box-shadow: 0 4px 14px rgba(13, 110, 110, 0.25) !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.btn-try-fixer:hover {
    background: #0a5252 !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(13, 110, 110, 0.35) !important;
    text-decoration: none !important;
}

.btn-try-fixer .arrow-icon {
    transition: transform 0.18s ease;
}

.btn-try-fixer:hover .arrow-icon {
    transform: translateX(3px);
}

.link-understand-method {
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: #12181c !important;
    background: #ffffff !important;
    border: 1.5px solid #d4cebe !important;
    padding: 0.8rem 1.5rem !important;
    border-radius: 9999px !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    cursor: pointer !important;
    text-decoration: none !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.link-understand-method:hover {
    background: #fdfbf7 !important;
    border-color: #12181c !important;
    color: #12181c !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    text-decoration: none !important;
}

.hero-security-badges {
    display: flex;
    align-items: center;
    gap: 1.8rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    color: #4a555e;
    letter-spacing: 0.06em;
}

/* Floating Agent Trace Card (Right Side of Hero) */
.trace-preview-outer {
    position: relative;
    background: #ffffff;
    padding: 12px;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
    border: 1px solid #e5dfd2;
}

.trace-preview-inner {
    background: #0f2229;
    border-radius: 14px;
    padding: 1.6rem 1.6rem 2.5rem 1.6rem;
    color: #ffffff;
    position: relative;
}

.trace-preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #94a3b8;
    margin-bottom: 1.4rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 0.8rem;
}

.badge-reproducible {
    background: rgba(255, 255, 255, 0.06);
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    font-size: 0.68rem;
    color: #cbd5e1;
}

.trace-preview-step {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.85rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.step-left-info {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.step-num-mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #e59b56;
    font-weight: 700;
}

.step-main-title {
    font-weight: 700;
    font-size: 0.95rem;
    color: #ffffff;
}

.step-sub-mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 2px;
}

.step-check-icon {
    color: #2ec4b6;
    font-weight: 800;
    font-size: 1.1rem;
}

.time-stamp-right {
    position: absolute;
    bottom: 1.2rem;
    right: 1.6rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #e59b56;
    font-weight: 600;
}

.floating-confidence-pill {
    position: absolute;
    bottom: -18px;
    left: 24px;
    background: #ffffff;
    border: 1px solid #ded8c9;
    border-radius: 12px;
    padding: 0.6rem 1.1rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
}

.pill-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.pill-value {
    font-weight: 800;
    font-size: 0.98rem;
    color: #0d6e6e;
}

.pill-score {
    color: #64748b;
    font-weight: 600;
    font-size: 0.85rem;
}

/* ==================== SECTION 01: WORKSPACE ==================== */
.workspace-card-full {
    background: #0c1920;
    border: 1px solid #1a323d;
    border-radius: 16px 16px 0 0;
    padding: 3rem 3rem 1.5rem 3rem;
    color: #ffffff;
}

.section-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    display: block;
    margin-bottom: 0.8rem;
}

.section-tag.light { color: #5eead4; }
.section-tag.coral { color: #e25a38; }
.section-tag.mint { color: #5eead4; }

.hero-title-dark {
    font-size: 3.25rem;
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.035em;
    color: #ffffff;
}

.accent-mint { color: #5eead4; }

.hero-subtitle-dark {
    font-size: 1.05rem;
    line-height: 1.55;
    color: #94a3b8;
}

.ide-window-bar {
    background: #0d1a21;
    border: 1px solid #1a323d;
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    padding: 0.65rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.window-dots {
    display: flex;
    gap: 6px;
    align-items: center;
}

.window-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}

.dot-red { background: #ef4444; }
.dot-yellow { background: #eab308; }
.dot-green { background: #22c55e; }

.file-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #94a3b8;
    margin-left: 0.6rem;
}

/* ==================== STEPPER & VALIDATION ANIMATION ==================== */
@keyframes stepSuccessPulse {
    0% {
        transform: scale(0.94);
        box-shadow: 0 0 0 0 rgba(46, 196, 182, 0.6);
    }
    50% {
        transform: scale(1.06);
        box-shadow: 0 0 10px 2px rgba(46, 196, 182, 0.3);
    }
    100% {
        transform: scale(1);
        box-shadow: 0 0 0 0 rgba(46, 196, 182, 0);
    }
}

.stepper-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0e1e26;
    padding: 1.1rem 1.4rem;
    border-radius: 8px;
    border: 1px solid #1a323d;
    margin-bottom: 1.2rem;
}

.step-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.35rem;
}

.step-badge {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: #142833;
    border: 1px solid #1a323d;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    font-weight: 700;
    color: #64748b;
    transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease;
}

.step-node.active .step-badge {
    background: #e59b56;
    color: #0c181f;
    border-color: #e59b56;
    box-shadow: 0 0 10px rgba(229, 155, 86, 0.5);
    transform: scale(1.05);
}

.step-node.completed .step-badge {
    background: #2ec4b6;
    color: #0c181f;
    border-color: #2ec4b6;
    animation: stepSuccessPulse 0.4s cubic-bezier(0.16, 1, 0.3, 1) 1 normal forwards;
}

.step-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    color: #64748b;
    transition: color 0.25s ease;
}

.step-node.active .step-label { color: #e59b56; }
.step-node.completed .step-label { color: #2ec4b6; }

.step-line {
    flex: 1;
    height: 2px;
    background: #1a323d;
    margin: 0 0.5rem 1.2rem;
    transition: background-color 0.3s ease;
}

.step-line.completed { background: #2ec4b6; }

/* Trace Output Box */
.trace-card-box {
    background: #0c1a21;
    border: 1px solid #1a323d;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}

.trace-title-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.4rem;
}

.trace-step-tag {
    font-weight: 700;
    color: #2ec4b6;
}

.trace-step-tag.coral { color: #e25a38; }
.trace-step-tag.amber { color: #e59b56; }

.diff-del-line {
    color: #f87171;
    background: rgba(248, 113, 113, 0.12);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    display: block;
    margin-bottom: 3px;
}

.diff-add-line {
    color: #4ade80;
    background: rgba(74, 222, 128, 0.12);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    display: block;
}

/* Section 02 to 05 styling */
.light-heading {
    font-size: 3.25rem;
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.035em;
    color: #12181c;
    margin-bottom: 1rem;
}

.light-desc {
    font-size: 1.1rem;
    line-height: 1.55;
    color: #4a555e;
}

.method-grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    border-top: 1px solid #ded8c9;
    border-left: 1px solid #ded8c9;
    margin-top: 1.5rem;
    margin-bottom: 4rem;
}

.method-quad-card {
    padding: 2.2rem 2rem;
    border-right: 1px solid #ded8c9;
    border-bottom: 1px solid #ded8c9;
    background: #fdfbf7;
}

.method-num-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #e25a38;
    font-weight: 700;
    display: block;
    margin-bottom: 1.2rem;
}

.method-quad-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #12181c;
    margin-bottom: 0.6rem;
}

.method-quad-desc {
    font-size: 0.95rem;
    color: #4a555e;
    line-height: 1.55;
}

.link-docs-pill {
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.45rem !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    color: #12181c !important;
    background: #ffffff !important;
    border: 1.5px solid #ded8c9 !important;
    padding: 0.6rem 1.25rem !important;
    border-radius: 9999px !important;
    text-decoration: none !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
}

.link-docs-pill:hover {
    background: #fdfbf7 !important;
    border-color: #12181c !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    text-decoration: none !important;
}

.link-docs-pill .arrow {
    color: #e25a38;
    transition: transform 0.18s ease;
}

.link-docs-pill:hover .arrow {
    transform: translateX(3px);
}

.terminal-card-wrap {
    background: #0f1f26;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.12);
    margin-bottom: 4rem;
    border-bottom: 5px solid #e28e7c;
}

.terminal-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1.2rem;
    background: #0b181d;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #2ec4b6;
}

.terminal-code-body {
    padding: 1.4rem 1.6rem;
    color: #f1f5f9;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    line-height: 1.65;
}

.pricing-3-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin-top: 2rem;
    margin-bottom: 4rem;
}

.pricing-box {
    background: #fcfbfa;
    border: 1px solid #ded8c9;
    border-radius: 16px;
    padding: 2.2rem 1.8rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.pricing-box.featured {
    background: #dbece2;
    border: 1.5px solid #8ec0a4;
}

.price-big-text {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
    color: #12181c;
    margin: 0.8rem 0;
}

.price-sub {
    font-size: 0.88rem;
    color: #788590;
    font-weight: 400;
}

.price-feature-list {
    list-style: none;
    padding: 0;
    margin: 1.5rem 0 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    font-size: 0.94rem;
    color: #4a555e;
}

.price-feature-list li::before {
    content: "✓ ";
    color: #16a34a;
    font-weight: 800;
    margin-right: 0.5rem;
}

.badge-tag-most-used {
    background: #e25a38;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    float: right;
}

.btn-plan-outline {
    text-align: center;
    padding: 0.75rem 1.2rem;
    border: 1.5px solid #d4cebe;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.9rem;
    color: #12181c !important;
    background: #ffffff;
    cursor: pointer;
    text-decoration: none !important;
    display: block;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-plan-outline:hover {
    border-color: #12181c;
    background: #fdfbf7;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    text-decoration: none !important;
}

.btn-plan-featured {
    text-align: center;
    padding: 0.75rem 1.2rem;
    background: #0d6e6e;
    border: 1.5px solid #0d6e6e;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.9rem;
    color: #ffffff !important;
    cursor: pointer;
    text-decoration: none !important;
    display: block;
    box-shadow: 0 4px 14px rgba(13, 110, 110, 0.25);
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-plan-featured:hover {
    background: #0a5252;
    border-color: #0a5252;
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(13, 110, 110, 0.35);
    text-decoration: none !important;
}

/* ==================== SECTION 06: ENTERPRISE PERIMETER ==================== */
.enterprise-section-wrap {
    background-color: #0f676a;
    color: #ffffff;
    padding: 4.5rem 3.5rem;
    border-radius: 18px;
    margin-bottom: 3.5rem;
}

.enterprise-header-flex {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 3rem;
}

.enterprise-heading {
    font-size: 3.4rem;
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.035em;
    color: #ffffff;
    margin-bottom: 1.2rem;
}

.enterprise-desc {
    font-size: 1.05rem;
    line-height: 1.55;
    color: rgba(255, 255, 255, 0.85);
    max-width: 540px;
}

.enterprise-btn-pill {
    background: #e59b56 !important;
    color: #12181c !important;
    padding: 0.85rem 1.65rem !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    border-radius: 9999px !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.55rem !important;
    text-decoration: none !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2) !important;
    margin-top: 1rem !important;
    border: none !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.enterprise-btn-pill:hover {
    background: #f0aa44 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.28) !important;
    text-decoration: none !important;
}

.enterprise-btn-pill .arrow-icon {
    transition: transform 0.18s ease;
}

.enterprise-btn-pill:hover .arrow-icon {
    transform: translateX(3px);
}

.enterprise-3-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}

.enterprise-card-box {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 2rem 1.8rem;
}

.enterprise-icon-box {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    margin-bottom: 1.2rem;
    font-size: 1.1rem;
}

.enterprise-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.5rem;
}

.enterprise-text {
    font-size: 0.94rem;
    line-height: 1.5;
    color: rgba(255, 255, 255, 0.8);
}

/* ==================== FOOTER ==================== */
.footer-cream-wrap {
    background: #f3eee6;
    border-top: 1px solid #ded8c9;
    padding: 2.5rem 0 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.footer-center-links {
    display: flex;
    gap: 2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #55636e;
}

.footer-link-text {
    color: #55636e !important;
    text-decoration: none !important;
    transition: color 0.15s ease !important;
}

.footer-link-text:hover {
    color: #12181c !important;
    text-decoration: none !important;
}

/* Form input tweaks */
.stTextArea textarea {
    background-color: #091318 !important;
    color: #f1f5f9 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    border: 1px solid #1a323d !important;
    border-radius: 0 0 8px 8px !important;
}

.stButton>button {
    background-color: #e59b56 !important;
    color: #0c181f !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 9999px !important;
    padding: 0.65rem 1.4rem !important;
    box-shadow: 0 4px 12px rgba(229, 155, 86, 0.25) !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.stButton>button:hover {
    background-color: #f0aa44 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(229, 155, 86, 0.35) !important;
}

/* High contrast code styling */
pre, code, pre code, [data-testid="stMarkdownContainer"] pre, [data-testid="stMarkdownContainer"] code {
    color: #f8fafc !important;
    background-color: #050b0e !important;
}

pre *, code * {
    color: #f8fafc !important;
}

::selection {
    background: #0284c7 !important;
    color: #ffffff !important;
}

.corrected-code-full-wrap {
    margin-top: 2rem;
    margin-bottom: 2rem;
    background: #081318;
    border: 1.5px solid #2ec4b6;
    border-radius: 14px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
    overflow: hidden;
    width: 100%;
}

.corrected-code-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #0d1a21;
    padding: 0.85rem 1.4rem;
    border-bottom: 1px solid #1a323d;
}

.corrected-code-tag-title {
    color: #2ec4b6;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.corrected-code-badge-verified {
    background: rgba(46, 196, 182, 0.15);
    color: #5eead4;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    border: 1px solid rgba(46, 196, 182, 0.35);
}

.stCodeBlock {
    border-radius: 8px !important;
    border: 1px solid #1a323d !important;
    background-color: #050b0e !important;
}

.stCodeBlock pre, .stCodeBlock code, .stCodeBlock span {
    font-family: 'JetBrains Mono', monospace !important;
    color: #f8fafc !important;
}
"""
