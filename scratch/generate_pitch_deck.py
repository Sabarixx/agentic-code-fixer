#!/usr/bin/env python3
"""
Agentic Code Fixer - Presentation Deck Generator
Generates an executive-grade, 16:9 widescreen PowerPoint presentation (.pptx)
with custom modern dark-mode styling, glassmorphic card layouts, vibrant accents,
metric badges, and structured technical diagrams.
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# -----------------------------------------------------------------------------
# DESIGN SYSTEM & COLOR PALETTE
# -----------------------------------------------------------------------------
# Backgrounds
COLOR_BG_DARK = RGBColor(12, 21, 26)         # #0C151A Deep Obsidian Slate
COLOR_CARD_BG = RGBColor(18, 31, 38)         # #121F26 Elevated Panel
COLOR_CARD_BORDER = RGBColor(30, 48, 58)     # #1E303A Subtle Card Border
COLOR_INNER_BOX = RGBColor(14, 25, 31)       # #0E191F Inner Code/Box Background

# Brand Accents
COLOR_TEAL = RGBColor(46, 196, 182)          # #2EC4B6 Primary Cyan Teal
COLOR_TEAL_MUTED = RGBColor(13, 110, 110)    # #0D6E6E Deep Teal
COLOR_VIOLET = RGBColor(139, 92, 246)        # #8B5CF6 LangGraph Purple
COLOR_AMBER = RGBColor(229, 155, 86)         # #E59B56 Socratic Duck Amber
COLOR_CORAL = RGBColor(226, 90, 56)          # #E25A38 Warning/Action Coral
COLOR_EMERALD = RGBColor(16, 185, 129)       # #10B981 Pass Emerald
COLOR_ROSE = RGBColor(244, 63, 94)           # #F43F5E Fail Rose

# Typography Colors
COLOR_TEXT_WHITE = RGBColor(248, 250, 252)   # #F8FAFC Heading White
COLOR_TEXT_SUBTLE = RGBColor(148, 163, 184)  # #94A3B8 Muted Silver
COLOR_TEXT_DIM = RGBColor(100, 116, 139)     # #64748B Darker Slate

FONT_HEADING = "Trebuchet MS"
FONT_BODY = "Segoe UI"
FONT_CODE = "Consolas"


def create_deck(output_path: str = "Agentic_Code_Fixer_Presentation.pptx"):
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = COLOR_BG_DARK

    def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1.2)
        else:
            shape.line.fill.background()
        return shape

    def add_badge(slide, left, top, width, height, text, bg_color, text_color=COLOR_TEXT_WHITE, font_size=11):
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        badge.fill.solid()
        badge.fill.fore_color.rgb = bg_color
        badge.line.fill.background()
        tf = badge.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = FONT_HEADING
        p.font.size = Pt(font_size)
        p.font.bold = True
        p.font.color.rgb = text_color
        p.alignment = PP_ALIGN.CENTER
        return badge

    def add_header(slide, category, title, subtitle=None):
        # Category Badge / Subtitle
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category.upper()
        p_c.font.name = FONT_HEADING
        p_c.font.size = Pt(11)
        p_c.font.bold = True
        p_c.font.color.rgb = COLOR_TEAL

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.7))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(26)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_TEXT_WHITE

        if subtitle:
            p_s = tf_t.add_paragraph()
            p_s.text = subtitle
            p_s.font.name = FONT_BODY
            p_s.font.size = Pt(13)
            p_s.font.color.rgb = COLOR_TEXT_SUBTLE
            p_s.space_before = Pt(4)

    # =========================================================================
    # SLIDE 1: HERO TITLE SLIDE
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)

    # Ambient Card Container
    add_card(slide1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), bg_color=COLOR_CARD_BG, border_color=COLOR_TEAL_MUTED)

    # Top Brand Pill
    add_badge(slide1, Inches(1.4), Inches(1.3), Inches(2.6), Inches(0.4), "⚡ AUTONOMOUS AI PIPELINE", COLOR_TEAL_MUTED, COLOR_TEXT_WHITE, 10)

    # Main Big Title
    title_box = slide1.shapes.add_textbox(Inches(1.4), Inches(1.9), Inches(10.5), Inches(1.8))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Agentic Code Fixer"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Closed-Loop Autonomous Code Generation, Execution & Self-Correction"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_TEAL
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "Turning failing test suites into verified, surgical AST patches with deterministic proof receipts."
    p3.font.name = FONT_BODY
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_TEXT_SUBTLE
    p3.space_before = Pt(8)

    # 4 Feature Badges at Bottom
    badges_data = [
        ("LANGGRAPH", "StateGraph Orchestration", COLOR_VIOLET),
        ("GROQ & GEMINI", "Sub-1.5s High Speed LLMs", COLOR_AMBER),
        ("SANDBOX RUNNER", "Isolated Zero-Leak Sandbox", COLOR_EMERALD),
        ("DUCK DEBUGGER", "3-Level Socratic AI Tutor", COLOR_CORAL),
    ]
    for i, (b_title, b_sub, b_col) in enumerate(badges_data):
        bx = Inches(1.4 + i * 2.65)
        by = Inches(4.7)
        add_card(slide1, bx, by, Inches(2.45), Inches(1.4), bg_color=COLOR_INNER_BOX, border_color=b_col)
        t_box = slide1.shapes.add_textbox(bx, by, Inches(2.45), Inches(1.4))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = b_title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = b_col
        p_s = tf.add_paragraph()
        p_s.text = b_sub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(11)
        p_s.font.color.rgb = COLOR_TEXT_SUBTLE
        p_s.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: THE PROBLEM (ONE-SHOT LLM PARADOX)
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "Industry Challenge & Context", "The 'One-Shot' LLM Paradox in Code Generation", "Why probabilistic AI coding assistants break in production environments.")

    # Left Card: Traditional Open-Loop
    add_card(slide2, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=COLOR_CARD_BG, border_color=COLOR_ROSE)
    add_badge(slide2, Inches(1.1), Inches(2.1), Inches(3.2), Inches(0.35), "❌ TRADITIONAL OPEN-LOOP LLMS", COLOR_ROSE, COLOR_TEXT_WHITE, 10)
    
    left_tb = slide2.shapes.add_textbox(Inches(1.1), Inches(2.6), Inches(5.1), Inches(3.9))
    tf_l = left_tb.text_frame
    tf_l.word_wrap = True
    
    points_l = [
        ("Probabilistic Guesswork", "LLMs guess code based on syntax statistics without executing or testing edge cases."),
        ("Cascading Regressions", "One-shot fixes rewrite entire files, accidentally deleting critical unaffected logic."),
        ("Hallucinated Interfaces", "Generates plausible-looking methods and types that crash at runtime."),
        ("60%+ Developer Triage Tax", "Engineers waste hours reviewing, executing, and manually debugging AI suggestions.")
    ]
    for i, (title, desc) in enumerate(points_l):
        p_head = tf_l.paragraphs[0] if i == 0 else tf_l.add_paragraph()
        p_head.text = f"• {title}"
        p_head.font.name = FONT_HEADING
        p_head.font.size = Pt(13)
        p_head.font.bold = True
        p_head.font.color.rgb = COLOR_TEXT_WHITE
        p_head.space_before = Pt(8) if i > 0 else Pt(0)
        
        p_body = tf_l.add_paragraph()
        p_body.text = f"  {desc}"
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(11)
        p_body.font.color.rgb = COLOR_TEXT_SUBTLE

    # Right Card: Agentic Closed-Loop
    add_card(slide2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=COLOR_CARD_BG, border_color=COLOR_EMERALD)
    add_badge(slide2, Inches(7.1), Inches(2.1), Inches(3.2), Inches(0.35), "✅ AGENTIC CLOSED-LOOP REPAIR", COLOR_EMERALD, COLOR_TEXT_WHITE, 10)
    
    right_tb = slide2.shapes.add_textbox(Inches(7.1), Inches(2.6), Inches(5.1), Inches(3.9))
    tf_r = right_tb.text_frame
    tf_r.word_wrap = True
    
    points_r = [
        ("Automated Feedback Loop", "Executes test contracts in isolated sandboxes; feeds real runtime errors back to LLM."),
        ("Surgical AST Invariant Diffs", "Only patches the exact failing logical lines while strictly preserving codebase structure."),
        ("Deterministic Proof Receipts", "Cryptographically verifies 100% test contract passage before proposing any patch."),
        ("Zero Hallucination Perimeter", "Guarantees zero-defect pull request readiness with high Bayesian confidence scores.")
    ]
    for i, (title, desc) in enumerate(points_r):
        p_head = tf_r.paragraphs[0] if i == 0 else tf_r.add_paragraph()
        p_head.text = f"• {title}"
        p_head.font.name = FONT_HEADING
        p_head.font.size = Pt(13)
        p_head.font.bold = True
        p_head.font.color.rgb = COLOR_TEXT_WHITE
        p_head.space_before = Pt(8) if i > 0 else Pt(0)
        
        p_body = tf_r.add_paragraph()
        p_body.text = f"  {desc}"
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(11)
        p_body.font.color.rgb = COLOR_TEXT_SUBTLE

    # =========================================================================
    # SLIDE 3: SYSTEM OVERVIEW & 3 CORE PILLARS
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "System Overview", "Three Core Engineering Pillars", "How Agentic Code Fixer delivers enterprise-grade code reliability.")

    pillars = [
        ("1. Multi-Agent StateGraph", "LangGraph-powered stateful cycle coordinating Planner, Coder, Sandbox Tester, and Refactor nodes in a deterministic state machine.", COLOR_VIOLET, ["Shared Typed Schema", "Conditional Branching", "Max Iteration Safeguards"]),
        ("2. Isolated Polyglot Sandbox", "Zero-leak sub-second ephemeral container runner supporting Python, JS/TS, Java, C++, Rust, and Go.", COLOR_TEAL, ["Sub-10s Timeouts", "Process Isolation", "Full stdout/stderr Capture"]),
        ("3. Socratic Duck Debugger", "Interactive 3-level pedagogical AI tutor with frustration detection and source-in = source-out language parity.", COLOR_AMBER, ["Conceptual → Implementation", "Sentiment & Mood Detection", "1-Click Agent Takeover"])
    ]

    for i, (title, desc, color, bullets) in enumerate(pillars):
        px = Inches(0.8 + i * 3.98)
        py = Inches(1.8)
        add_card(slide3, px, py, Inches(3.75), Inches(4.2), bg_color=COLOR_CARD_BG, border_color=color)
        add_badge(slide3, px + Inches(0.3), py + Inches(0.3), Inches(3.15), Inches(0.4), title, color, COLOR_TEXT_WHITE, 11)
        
        tb = slide3.shapes.add_textbox(px + Inches(0.3), py + Inches(0.9), Inches(3.15), Inches(3.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p_d = tf.paragraphs[0]
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_TEXT_SUBTLE
        
        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"✓  {b}"
            pb.font.name = FONT_HEADING
            pb.font.size = Pt(11)
            pb.font.bold = True
            pb.font.color.rgb = COLOR_TEXT_WHITE
            pb.space_before = Pt(8)

    # Bottom Banner Stat
    add_card(slide3, Inches(0.8), Inches(6.2), Inches(11.733), Inches(0.8), bg_color=COLOR_INNER_BOX, border_color=COLOR_TEAL_MUTED)
    tb_b = slide3.shapes.add_textbox(Inches(1.0), Inches(6.25), Inches(11.3), Inches(0.7))
    tf_b = tb_b.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "🎯 Benchmark Track Record: 40/40 Passing Unit Tests across All 8 Standard Computer Science Challenge Specs."
    p_b.font.name = FONT_HEADING
    p_b.font.size = Pt(13)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_TEAL

    # =========================================================================
    # SLIDE 4: LANGGRAPH ARCHITECTURE & STATE MACHINE
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "Pipeline Architecture", "LangGraph Multi-Agent State Machine", "Cyclic repair topology with bounded state transitions and failure escalation.")

    # Left: Flow Diagram
    add_card(slide4, Inches(0.8), Inches(1.8), Inches(6.2), Inches(5.1), bg_color=COLOR_CARD_BG, border_color=COLOR_VIOLET)
    add_badge(slide4, Inches(1.1), Inches(2.1), Inches(2.8), Inches(0.35), "STATE TRANSITION GRAPH", COLOR_VIOLET, COLOR_TEXT_WHITE, 10)

    steps = [
        ("1. START ➔ planner_node", "Parses problem spec, preconditions & invariant bounds.", COLOR_TEAL),
        ("2. coder_node", "Synthesizes surgical AST code patch from plan/errors.", COLOR_VIOLET),
        ("3. tester_node (Sandbox)", "Runs isolated pytest; captures exit code & stack trace.", COLOR_AMBER),
        ("4. Conditional Router", "If failed & retries < MAX ➔ Re-enter coder_node.", COLOR_CORAL),
        ("5. refactor_node ➔ END", "Optimizes complexity on pass; generates proof receipt.", COLOR_EMERALD),
    ]
    for idx, (st_t, st_d, st_c) in enumerate(steps):
        sy = Inches(2.6 + idx * 0.82)
        add_card(slide4, Inches(1.1), sy, Inches(5.6), Inches(0.7), bg_color=COLOR_INNER_BOX, border_color=st_c)
        st_box = slide4.shapes.add_textbox(Inches(1.2), sy + Inches(0.05), Inches(5.4), Inches(0.6))
        tf_s = st_box.text_frame
        tf_s.word_wrap = True
        ps1 = tf_s.paragraphs[0]
        ps1.text = st_t
        ps1.font.name = FONT_HEADING
        ps1.font.size = Pt(11)
        ps1.font.bold = True
        ps1.font.color.rgb = st_c
        ps2 = tf_s.add_paragraph()
        ps2.text = st_d
        ps2.font.name = FONT_BODY
        ps2.font.size = Pt(10)
        ps2.font.color.rgb = COLOR_TEXT_SUBTLE

    # Right: State Schema Definition
    add_card(slide4, Inches(7.3), Inches(1.8), Inches(5.2), Inches(5.1), bg_color=COLOR_CARD_BG, border_color=COLOR_TEAL_MUTED)
    add_badge(slide4, Inches(7.6), Inches(2.1), Inches(2.8), Inches(0.35), "AGENTSTATE SCHEMA", COLOR_TEAL_MUTED, COLOR_TEXT_WHITE, 10)
    
    tb_schema = slide4.shapes.add_textbox(Inches(7.6), Inches(2.6), Inches(4.6), Inches(4.1))
    tf_sc = tb_schema.text_frame
    tf_sc.word_wrap = True
    
    schema_fields = [
        ("spec: dict", "Target signature, docstring, constraints"),
        ("plan: str", "Structured step-by-step repair roadmap"),
        ("code: str", "Source candidate implementation"),
        ("test_results: dict", "Passed/failed counts, traces, stdout"),
        ("iteration_count: int", "Active retry counter (bound <= 3)"),
        ("status: StatusEnum", "idle | planning | coding | testing | refactoring | passed | failed"),
        ("confidence: float", "Bayesian confidence rating (0.00 - 1.00)")
    ]
    for i, (field, desc) in enumerate(schema_fields):
        pf = tf_sc.paragraphs[0] if i == 0 else tf_sc.add_paragraph()
        pf.text = f"• {field}"
        pf.font.name = FONT_CODE
        pf.font.size = Pt(11)
        pf.font.bold = True
        pf.font.color.rgb = COLOR_TEAL
        pf.space_before = Pt(6) if i > 0 else Pt(0)
        
        pd = tf_sc.add_paragraph()
        pd.text = f"   {desc}"
        pd.font.name = FONT_BODY
        pd.font.size = Pt(10)
        pd.font.color.rgb = COLOR_TEXT_SUBTLE

    # =========================================================================
    # SLIDE 5: DEEP DIVE: 4 CORE AGENT NODES
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5)
    add_header(slide5, "Modular Subsystems", "Deep Dive: Four Specialized Agent Nodes", "Each node operates with single-responsibility isolation and explicit contracts.")

    nodes_info = [
        ("1. Planner Node", "agent/nodes/planner.py", COLOR_TEAL, "Analyzes raw specification, extracts input/output types, algorithmic complexity bounds, and formulates step-by-step logic."),
        ("2. Coder Node", "agent/nodes/coder.py", COLOR_VIOLET, "Synthesizes code patches. On retry loops, processes stack trace lines and AST frames to fix failing assertions without breaking passing tests."),
        ("3. Tester Node", "agent/nodes/tester.py", COLOR_AMBER, "Invokes the isolated sandbox runner. Executes test suite, aggregates pass/fail counts, captures stdout/stderr, and determines next routing path."),
        ("4. Refactor Node", "agent/nodes/refactor.py", COLOR_EMERALD, "Optional post-verification pass. Enhances readability, docstrings, and algorithmic elegance with zero regression risk.")
    ]

    for i, (n_name, n_file, n_col, n_desc) in enumerate(nodes_info):
        col = i % 2
        row = i // 2
        nx = Inches(0.8 + col * 5.95)
        ny = Inches(1.8 + row * 2.6)
        add_card(slide5, nx, ny, Inches(5.7), Inches(2.4), bg_color=COLOR_CARD_BG, border_color=n_col)
        add_badge(slide5, nx + Inches(0.3), ny + Inches(0.25), Inches(2.2), Inches(0.35), n_name, n_col, COLOR_TEXT_WHITE, 11)
        
        fb = slide5.shapes.add_textbox(nx + Inches(2.6), ny + Inches(0.25), Inches(2.9), Inches(0.35))
        tf_f = fb.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = n_file
        p_f.font.name = FONT_CODE
        p_f.font.size = Pt(10)
        p_f.font.color.rgb = COLOR_TEXT_DIM

        tb_n = slide5.shapes.add_textbox(nx + Inches(0.3), ny + Inches(0.7), Inches(5.1), Inches(1.5))
        tf_n = tb_n.text_frame
        tf_n.word_wrap = True
        p_d = tf_n.paragraphs[0]
        p_d.text = n_desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_TEXT_SUBTLE

    # =========================================================================
    # SLIDE 6: SOCRATIC DUCK DEBUGGER
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6)
    add_header(slide6, "AI Pedagogical Tutor", "🦆 Socratic Duck Debugger", "Interactive 3-level progressive hint tutor with frustration detection.")

    duck_cards = [
        ("Level 1: Conceptual", "Broad theoretical context, algorithmic constraints, and general language semantics.", COLOR_TEAL, "Ask guiding questions: 'What data structure gives O(1) lookups?'"),
        ("Level 2: Structural", "Points to loop bounds, off-by-one indices, branch boundaries, and edge invariants.", COLOR_AMBER, "Highlights invariant: 'Consider what happens when the array has 1 element.'"),
        ("Level 3: Implementation", "Concrete directional cues targeting exact lines and logic constructs without giving it away.", COLOR_CORAL, "Concrete hint: 'Check the hash map key update order before returning.'")
    ]

    for i, (l_title, l_desc, l_col, l_ex) in enumerate(duck_cards):
        dx = Inches(0.8 + i * 3.98)
        dy = Inches(1.8)
        add_card(slide6, dx, dy, Inches(3.75), Inches(3.8), bg_color=COLOR_CARD_BG, border_color=l_col)
        add_badge(slide6, dx + Inches(0.3), dy + Inches(0.3), Inches(3.15), Inches(0.4), l_title, l_col, COLOR_TEXT_WHITE, 11)
        
        tb = slide6.shapes.add_textbox(dx + Inches(0.3), dy + Inches(0.9), Inches(3.15), Inches(2.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p_d = tf.paragraphs[0]
        p_d.text = l_desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_TEXT_SUBTLE
        
        p_e_title = tf.add_paragraph()
        p_e_title.text = "Example Guidance:"
        p_e_title.font.name = FONT_HEADING
        p_e_title.font.size = Pt(11)
        p_e_title.font.bold = True
        p_e_title.font.color.rgb = COLOR_TEXT_WHITE
        p_e_title.space_before = Pt(10)

        p_ex = tf.add_paragraph()
        p_ex.text = l_ex
        p_ex.font.name = FONT_BODY
        p_ex.font.size = Pt(11)
        p_ex.font.italic = True
        p_ex.font.color.rgb = l_col
        p_ex.space_before = Pt(3)

    # Bottom Special Features Banner
    add_card(slide6, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.2), bg_color=COLOR_INNER_BOX, border_color=COLOR_AMBER)
    tb_feat = slide6.shapes.add_textbox(Inches(1.0), Inches(5.85), Inches(11.3), Inches(1.1))
    tf_ft = tb_feat.text_frame
    tf_ft.word_wrap = True
    
    p_ft1 = tf_ft.paragraphs[0]
    p_ft1.text = "✨ Intelligent Adaptive Features:"
    p_ft1.font.name = FONT_HEADING
    p_ft1.font.size = Pt(12)
    p_ft1.font.bold = True
    p_ft1.font.color.rgb = COLOR_AMBER

    p_ft2 = tf_ft.add_paragraph()
    p_ft2.text = "• Frustration Detection: Automatically detects developer struggle and escalates hint depth.\n• Source-In = Source-Out: Responds strictly in the target language (Python, Java, TypeScript, Rust, Go, C++).\n• Seamless Escape Hatch: 1-Click 'I give up, let the Agent fix it! ⚡' handoff into the autonomous repair pipeline."
    p_ft2.font.name = FONT_BODY
    p_ft2.font.size = Pt(11)
    p_ft2.font.color.rgb = COLOR_TEXT_WHITE
    p_ft2.space_before = Pt(3)

    # =========================================================================
    # SLIDE 7: ISOLATED POLYGLOT SANDBOX RUNNER
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7)
    add_header(slide7, "Security & Execution Engine", "Ephemeral Polyglot Sandbox Runner", "Fast, secure, isolated test execution with strict resource boundaries.")

    # 4 Security/Performance Cards
    sandbox_features = [
        ("🔒 Zero-Leak Process Isolation", "Runs candidate code in ephemeral sub-processes detached from host environment with forbidden system call fences.", COLOR_EMERALD),
        ("⏱️ Sub-10s Hard Timeouts", "Enforces strict wall-clock timeout boundaries to neutralize infinite loops and algorithmic hangs immediately.", COLOR_CORAL),
        ("🌐 Polyglot Language Runtime", "Native test runners for Python (pytest), TypeScript/JavaScript (vitest/node), Java (junit), Rust (cargo test), and Go.", COLOR_TEAL),
        ("📊 Structured Diagnostics Capture", "Parses stdout, stderr, exit codes, and AST trace lines into standardized JSON diagnostic objects.", COLOR_VIOLET),
    ]

    for i, (title, desc, color) in enumerate(sandbox_features):
        col = i % 2
        row = i // 2
        sx = Inches(0.8 + col * 5.95)
        sy = Inches(1.8 + row * 2.5)
        add_card(slide7, sx, sy, Inches(5.7), Inches(2.3), bg_color=COLOR_CARD_BG, border_color=color)
        add_badge(slide7, sx + Inches(0.3), sy + Inches(0.25), Inches(4.0), Inches(0.35), title, color, COLOR_TEXT_WHITE, 11)
        
        tb = slide7.shapes.add_textbox(sx + Inches(0.3), sy + Inches(0.75), Inches(5.1), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p_d = tf.paragraphs[0]
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_TEXT_SUBTLE

    # Bottom Metric Bar
    add_card(slide7, Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.9), bg_color=COLOR_INNER_BOX, border_color=COLOR_TEAL_MUTED)
    tb_mb = slide7.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.8))
    tf_mb = tb_mb.text_frame
    p_mb = tf_mb.paragraphs[0]
    p_mb.text = "⚡ Real-World Performance: Average isolated test cycle execution completes in < 0.36 seconds."
    p_mb.font.name = FONT_HEADING
    p_mb.font.size = Pt(13)
    p_mb.font.bold = True
    p_mb.font.color.rgb = COLOR_TEAL

    # =========================================================================
    # SLIDE 8: PROOF RECEIPTS & DETERMINISTIC VERIFICATION
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8)
    add_header(slide8, "Verification & Trust", "Deterministic Proof Receipts & Confidence Scoring", "Bridging the enterprise trust gap with cryptographically verifiable execution traces.")

    # Left: Proof Receipt Box
    add_card(slide8, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.1), bg_color=COLOR_CARD_BG, border_color=COLOR_EMERALD)
    add_badge(slide8, Inches(1.1), Inches(2.1), Inches(3.0), Inches(0.35), "📜 SAMPLE PROOF RECEIPT", COLOR_EMERALD, COLOR_TEXT_WHITE, 10)

    receipt_tb = slide8.shapes.add_textbox(Inches(1.1), Inches(2.6), Inches(5.1), Inches(4.1))
    tf_rc = receipt_tb.text_frame
    tf_rc.word_wrap = True
    
    receipt_code = (
        "{\n"
        '  "status": "VERIFIED",\n'
        '  "iterations_used": 2,\n'
        '  "tests_passed": "5 / 5 (100%)",\n'
        '  "execution_time_ms": 348,\n'
        '  "confidence_score": 0.985,\n'
        '  "ast_churn": {\n'
        '    "lines_added": 3,\n'
        '    "lines_removed": 1,\n'
        '    "code_preservation": "94.2%"\n'
        "  },\n"
        '  "proof_hash": "sha256:7f8e3a2b1c4d9e0f...",\n'
        '  "signature": "AgenticFixer-v2.4-Audited"\n'
        "}"
    )
    p_rc = tf_rc.paragraphs[0]
    p_rc.text = receipt_code
    p_rc.font.name = FONT_CODE
    p_rc.font.size = Pt(11)
    p_rc.font.color.rgb = COLOR_TEAL

    # Right: Why Proof Receipts Matter
    add_card(slide8, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1), bg_color=COLOR_CARD_BG, border_color=COLOR_TEAL)
    add_badge(slide8, Inches(7.1), Inches(2.1), Inches(3.0), Inches(0.35), "ENTERPRISE VALUE", COLOR_TEAL, COLOR_TEXT_WHITE, 10)

    tb_rv = slide8.shapes.add_textbox(Inches(7.1), Inches(2.6), Inches(5.1), Inches(4.1))
    tf_rv = tb_rv.text_frame
    tf_rv.word_wrap = True

    proof_points = [
        ("Zero Human Triage Bottlenecks", "CI/CD pipelines can auto-merge patches that achieve 1.0 confidence proof receipts."),
        ("Audit Compliance & Traceability", "Every patch retains its full causal diagnostic trace, AST diff, and timestamp hash."),
        ("Surgical AST Invariant Protection", "Ensures minimal code churn (e.g. 94%+ preservation) avoiding style regressions."),
        ("Bayesian Invariant Scoring", "Multi-factor confidence scoring based on test complexity, boundary coverage, and execution stability.")
    ]
    for i, (title, desc) in enumerate(proof_points):
        p_h = tf_rv.paragraphs[0] if i == 0 else tf_rv.add_paragraph()
        p_h.text = f"✓ {title}"
        p_h.font.name = FONT_HEADING
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_TEXT_WHITE
        p_h.space_before = Pt(8) if i > 0 else Pt(0)
        
        p_b = tf_rv.add_paragraph()
        p_b.text = f"  {desc}"
        p_b.font.name = FONT_BODY
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = COLOR_TEXT_SUBTLE

    # =========================================================================
    # SLIDE 9: MULTI-SURFACE ECOSYSTEM & UI
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9)
    add_header(slide9, "Developer Experience", "Multi-Surface Accessible Interfaces", "Deploy and interact through whatever surface fits your workflow.")

    surfaces = [
        ("🖥️ Streamlit Workspace", "ui/app.py", COLOR_TEAL, "7-page aesthetic cream-grid design system with live LangGraph stepper, interactive diff inspector, and spec benchmarks."),
        ("⚡ Unified Web IDE", "ui/api_server.py", COLOR_VIOLET, "FastAPI + HTML5/JS standalone web IDE with Monaco editor, live test streaming, and Duck Debugger chat."),
        ("🛠️ CLI & CI/CD Runner", "main.py", COLOR_AMBER, "Headless execution pipeline for automated nightly regression fixing and GitHub Actions integration."),
        ("🌐 Live Cloud Production", "Render Deployment", COLOR_EMERALD, "Live, zero-setup production instance accessible globally at agentic-code-fixer.onrender.com.")
    ]

    for i, (s_name, s_file, s_col, s_desc) in enumerate(surfaces):
        col = i % 2
        row = i // 2
        sx = Inches(0.8 + col * 5.95)
        sy = Inches(1.8 + row * 2.6)
        add_card(slide9, sx, sy, Inches(5.7), Inches(2.4), bg_color=COLOR_CARD_BG, border_color=s_col)
        add_badge(slide9, sx + Inches(0.3), sy + Inches(0.25), Inches(2.8), Inches(0.35), s_name, s_col, COLOR_TEXT_WHITE, 11)
        
        fb = slide9.shapes.add_textbox(nx + Inches(3.2), sy + Inches(0.25), Inches(2.3), Inches(0.35))
        tf_f = fb.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = s_file
        p_f.font.name = FONT_CODE
        p_f.font.size = Pt(10)
        p_f.font.color.rgb = COLOR_TEXT_DIM

        tb_s = slide9.shapes.add_textbox(sx + Inches(0.3), sy + Inches(0.7), Inches(5.1), Inches(1.5))
        tf_s = tb_s.text_frame
        tf_s.word_wrap = True
        p_d = tf_s.paragraphs[0]
        p_d.text = s_desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_TEXT_SUBTLE

    # =========================================================================
    # SLIDE 10: BENCHMARK RESULTS & METRICS
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10)
    add_header(slide10, "Empirical Evaluation", "Curated Benchmark Suite: 40/40 Passing", "Tested against classical CS algorithms, data structure bugs, and edge cases.")

    # Table Card Container
    add_card(slide10, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.1), bg_color=COLOR_CARD_BG, border_color=COLOR_TEAL_MUTED)

    # Draw Table
    rows = 7
    cols = 5
    table_shape = slide10.shapes.add_table(rows, cols, Inches(1.1), Inches(2.1), Inches(11.133), Inches(4.5))
    table = table_shape.table

    col_widths = [Inches(2.5), Inches(2.2), Inches(2.8), Inches(1.8), Inches(1.833)]
    for idx, width in enumerate(col_widths):
        table.columns[idx].width = width

    headers = ["Benchmark Spec", "Algorithmic Domain", "Baseline Bug Type", "Repair Iterations", "Status"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_INNER_BOX
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEAL

    benchmarks = [
        ("spec_01_two_sum", "Hash Map / Arrays", "Off-by-one index boundary", "1 Cycle", "✅ Verified"),
        ("spec_02_lru_cache", "Doubly Linked List", "Pointer eviction memory leak", "2 Cycles", "✅ Verified"),
        ("spec_03_binary_search", "Divide & Conquer", "Integer overflow & midpoint", "1 Cycle", "✅ Verified"),
        ("spec_04_merge_intervals", "Sorting & Intervals", "Overlap boundary merge drop", "2 Cycles", "✅ Verified"),
        ("spec_05_valid_palindrome", "Two Pointers / RegEx", "Unicode & punctuation skip", "1 Cycle", "✅ Verified"),
        ("spec_06_to_08 (Trees/DP)", "Dynamic Prog & Trees", "Recursion base case & memo", "2 Cycles", "✅ Verified"),
    ]

    for i, row_data in enumerate(benchmarks):
        for j, val in enumerate(row_data):
            cell = table.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD_BG if i % 2 == 0 else COLOR_INNER_BOX
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY if j != 0 else FONT_CODE
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_EMERALD if "✅" in val else COLOR_TEXT_WHITE

    # =========================================================================
    # SLIDE 11: REAL-WORLD IMPACT & CI/CD
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11)
    add_header(slide11, "Production Deployment", "Enterprise Integration & Production Scenarios", "Bringing autonomous self-healing into real software engineering pipelines.")

    scenarios = [
        ("🤖 Autonomous CI/CD Bot", "Integrates directly into GitHub Actions or GitLab CI. When a test suite fails on a PR, the agent spins up, diagnoses the stack trace, and opens a verified patch PR.", COLOR_VIOLET),
        ("🧑‍💻 IDE Self-Repair Assistant", "Companion plugin inside VS Code & JetBrains IDEs. Instant inline patch generation with real-time test verification right under the cursor.", COLOR_TEAL),
        ("🎓 Interactive Coding Tutor", "Empowers engineering students and interview candidates with Socratic Duck guidance before handing off verified solutions.", COLOR_AMBER),
        ("🏢 Legacy Code Modernization", "Safely refactors legacy codebases to modern standards while guaranteeing zero behavior drift through strict test contract invariants.", COLOR_CORAL),
    ]

    for i, (title, desc, color) in enumerate(scenarios):
        col = i % 2
        row = i // 2
        sx = Inches(0.8 + col * 5.95)
        sy = Inches(1.8 + row * 2.5)
        add_card(slide11, sx, sy, Inches(5.7), Inches(2.3), bg_color=COLOR_CARD_BG, border_color=color)
        add_badge(slide11, sx + Inches(0.3), sy + Inches(0.25), Inches(3.8), Inches(0.35), title, color, COLOR_TEXT_WHITE, 11)
        
        tb = slide11.shapes.add_textbox(sx + Inches(0.3), sy + Inches(0.75), Inches(5.1), Inches(1.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p_d = tf.paragraphs[0]
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_TEXT_SUBTLE

    # =========================================================================
    # SLIDE 12: CONCLUSION & LIVE REPOSITORY
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12)

    add_card(slide12, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), bg_color=COLOR_CARD_BG, border_color=COLOR_TEAL)
    
    add_badge(slide12, Inches(1.4), Inches(1.3), Inches(3.0), Inches(0.4), "⚡ CONCLUSION & ROADMAP", COLOR_TEAL_MUTED, COLOR_TEXT_WHITE, 10)

    tb_c = slide12.shapes.add_textbox(Inches(1.4), Inches(1.9), Inches(10.5), Inches(1.5))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "The Future of AI Software Engineering"
    p_c1.font.name = FONT_HEADING
    p_c1.font.size = Pt(36)
    p_c1.font.bold = True
    p_c1.font.color.rgb = COLOR_TEXT_WHITE

    p_c2 = tf_c.add_paragraph()
    p_c2.text = "Autonomous, Closed-Loop, and Verifiably Correct."
    p_c2.font.name = FONT_HEADING
    p_c2.font.size = Pt(18)
    p_c2.font.bold = True
    p_c2.font.color.rgb = COLOR_TEAL
    p_c2.space_before = Pt(4)

    # 3 Summary Column Cards
    summary_cards = [
        ("🌐 Live Cloud App", "Try the live self-healing agent in browser:\nhttps://agentic-code-fixer.onrender.com/", COLOR_TEAL),
        ("📦 GitHub Repository", "Complete source, tests & benchmarks:\ngithub.com/Sabarixx/agentic-code-fixer", COLOR_VIOLET),
        ("📜 Open Source & MIT", "Freely extensible architecture for teams, CI bots, and agentic workflows.", COLOR_AMBER)
    ]

    for i, (stitle, sbody, scol) in enumerate(summary_cards):
        cx = Inches(1.4 + i * 3.55)
        cy = Inches(3.8)
        add_card(slide12, cx, cy, Inches(3.3), Inches(2.2), bg_color=COLOR_INNER_BOX, border_color=scol)
        
        t_box = slide12.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.2), Inches(2.9), Inches(1.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = stitle
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = scol
        
        p_b = tf.add_paragraph()
        p_b.text = sbody
        p_b.font.name = FONT_BODY
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = COLOR_TEXT_SUBTLE
        p_b.space_before = Pt(8)

    # Save presentation
    prs.save(output_path)
    print(f"[SUCCESS] Successfully generated presentation deck at: {output_path}")


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "Agentic_Code_Fixer_Presentation.pptx"
    create_deck(out_file)
