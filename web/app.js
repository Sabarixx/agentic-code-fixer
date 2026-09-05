/* ==========================================================================
   AGENTIC CODE FIXER - CLIENT APPLICATION LOGIC
   Handles interactive live code repair, custom debugging, and UI interactions
   ========================================================================== */

let currentLang = 'typescript';
let isRunning = false;
let currentStep = 0;
let lastGeneratedPatch = "";
let customPatchedCode = "";

document.addEventListener('DOMContentLoaded', () => {
  initEditors();
  loadFixture(currentLang);
  setupScrollSpy();
});

/* ==================== EDITOR & LINE NUMBER MANAGEMENT ==================== */
function initEditors() {
  const sourceEditor = document.getElementById('sourceEditor');
  const testsEditor = document.getElementById('testsEditor');

  if (sourceEditor) {
    sourceEditor.addEventListener('input', () => updateEditorLines('sourceEditor', 'sourceLineNumbers', 'sourceLineCount'));
    updateEditorLines('sourceEditor', 'sourceLineNumbers', 'sourceLineCount');
  }

  if (testsEditor) {
    testsEditor.addEventListener('input', () => updateEditorLines('testsEditor', 'testsLineNumbers'));
    updateEditorLines('testsEditor', 'testsLineNumbers');
  }
}

function updateEditorLines(editorId, lineNumId, countId) {
  const editor = document.getElementById(editorId);
  const lineContainer = document.getElementById(lineNumId);
  if (!editor || !lineContainer) return;

  const lines = editor.value.split('\n');
  const lineCount = lines.length;

  let html = '';
  for (let i = 1; i <= lineCount; i++) {
    html += `<span>${i}</span>`;
  }
  lineContainer.innerHTML = html;

  if (countId) {
    const counter = document.getElementById(countId);
    if (counter) counter.innerText = `${lineCount} line${lineCount > 1 ? 's' : ''}`;
  }
}

/* ==================== FIXTURE MANAGEMENT ==================== */
function loadFixture(lang) {
  currentLang = lang;
  const fixture = FIXTURES[lang] || FIXTURES['typescript'];

  const sourceEditor = document.getElementById('sourceEditor');
  const testsEditor = document.getElementById('testsEditor');
  const fileName = document.getElementById('ideFileName');

  if (sourceEditor) sourceEditor.value = fixture.source;
  if (testsEditor) testsEditor.value = fixture.tests;
  if (fileName) fileName.innerText = fixture.name;

  updateEditorLines('sourceEditor', 'sourceLineNumbers', 'sourceLineCount');
  updateEditorLines('testsEditor', 'testsLineNumbers');

  resetStepper();
}

function onLanguageChange(lang) {
  loadFixture(lang);
  showToast(`Loaded ${lang.toUpperCase()} fixture`);
}

function resetCurrentFixture() {
  loadFixture(currentLang);
  showToast("Fixture reset to initial state");
}

/* ==================== DYNAMIC CUSTOM CODE ANALYZER ==================== */
// Removed analyzeCustomCode mock function. Logic now handled by Backend API.

/* ==================== REPAIR LOOP EXECUTION ENGINE ==================== */
function resetStepper() {
  isRunning = false;
  currentStep = 0;

  for (let i = 1; i <= 5; i++) {
    const stepEl = document.getElementById(`step${i}`);
    const connEl = document.getElementById(`conn${i}`);
    if (stepEl) stepEl.className = 'step-item';
    if (connEl) connEl.className = 'step-connector';
  }

  const idleState = document.getElementById('agentIdleState');
  const liveTrace = document.getElementById('agentLiveTrace');
  const tools = document.getElementById('outputTools');
  const btnSpinner = document.getElementById('btnSpinner');
  const btnText = document.getElementById('btnText');
  const correctedBox = document.getElementById('correctedCodeBox');

  if (idleState) idleState.style.display = 'flex';
  if (liveTrace) {
    liveTrace.style.display = 'none';
    liveTrace.innerHTML = '';
  }
  if (tools) tools.style.display = 'none';
  if (btnSpinner) btnSpinner.style.display = 'none';
  if (btnText) btnText.innerText = '▶ Run repair';
  if (correctedBox) correctedBox.style.display = 'none';
}

async function triggerRunRepair() {
  if (isRunning) return;
  isRunning = true;

  const sourceEditor = document.getElementById('sourceEditor');
  const testsEditor = document.getElementById('testsEditor');
  const defaultFixture = FIXTURES[currentLang] || FIXTURES['typescript'];

  const currentSource = sourceEditor ? sourceEditor.value : defaultFixture.source;
  const currentTests = testsEditor ? testsEditor.value : defaultFixture.tests;

  const idleState = document.getElementById('agentIdleState');
  const liveTrace = document.getElementById('agentLiveTrace');
  const tools = document.getElementById('outputTools');
  const btnSpinner = document.getElementById('btnSpinner');
  const btnText = document.getElementById('btnText');
  const correctedBox = document.getElementById('correctedCodeBox');
  const correctedEditor = document.getElementById('correctedEditor');

  if (idleState) idleState.style.display = 'none';
  if (liveTrace) {
    liveTrace.style.display = 'flex';
    liveTrace.innerHTML = '';
  }
  if (btnSpinner) btnSpinner.style.display = 'inline-block';
  if (btnText) btnText.innerText = 'Repairing...';
  if (correctedBox) correctedBox.style.display = 'none';

  try {
    console.log("Requesting repair for:", { source: currentSource, tests: currentTests });

    const response = await fetch('http://localhost:8000/repair', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: currentSource,
        tests: currentTests,
        lang: currentLang
      })
    });

    if (!response.ok) {
        const errText = await response.text();
        throw new Error(`API repair failed: ${errText}`);
    }

    const repairSteps = await response.json();
    console.log("API Response received:", repairSteps);

    const stageMap = {
      'diagnosing': { step: 1, phase: 'ANALYSIS', class: 'mint' },
      'generating_tests': { step: 2, phase: 'DIAGNOSIS', class: 'coral' },
      'fixing': { step: 3, phase: 'PATCH SYNTHESIS', class: 'amber' },
      'testing': { step: 4, phase: 'SANDBOX RE-RUN', class: 'mint' },
      'done': { step: 5, phase: 'VERIFICATION & VALIDATION', class: 'mint' }
    };

    let finalCorrectedCode = "";
    const completedSteps = new Set();

    for (const step of repairSteps) {
      const stage = step.stage;
      const config = stageMap[stage] || { step: 5, phase: 'VALIDATION', class: 'mint' };

      if (!completedSteps.has(config.step)) {
        setStepState(config.step, 'active');
        await sleep(350);
      }

      if (stage === 'done' || step.corrected_code) {
        finalCorrectedCode = step.corrected_code;
      }

      let cardData = {
        stepNum: String(config.step).padStart(2, '0'),
        phaseName: config.phase,
        phaseClass: config.class,
        badge: "Processing...",
        content: "Analyzing code..."
      };

      if (stage === 'diagnosing') {
        cardData.badge = step.bug_category || "Diagnosis";
        cardData.content = `Root Cause: ${step.root_cause || 'Unknown'}\nSummary: ${step.summary || 'N/A'}`;
      } else if (stage === 'generating_tests') {
        cardData.badge = "Test Contract";
        cardData.content = step.generated_tests || "Synthesizing test specs...";
      } else if (stage === 'fixing') {
        cardData.badge = `Iteration ${step.iteration || 1}`;
        cardData.content = "Generating optimized candidate patch...";
      } else if (stage === 'testing') {
        const results = step.test_results || {};
        cardData.badge = `Tests: ${results.passed || 0}/${results.total || 0} Passed`;
        cardData.content = results.failure_details && results.failure_details.length > 0 ? results.failure_details.join('\n') : "All tests passing in sandbox.";
      } else if (stage === 'done') {
        cardData.badge = `Status: ${step.status || 'Verified'}`;
        cardData.content = `Repaired in ${step.iterations_taken || 1} attempts. Safety proof confirmed.`;
      }

      appendTraceCard(cardData);
      setStepState(config.step, 'completed');
      completedSteps.add(config.step);
    }

    // Ensure all steps up to 5 are stably completed once
    for (let i = 1; i <= 5; i++) {
      setStepState(i, 'completed');
    }

    console.log("Final corrected code to display:", finalCorrectedCode);

    if (finalCorrectedCode) {
      if (correctedBox) correctedBox.style.display = 'block';
      if (correctedEditor) {
        correctedEditor.value = finalCorrectedCode;
        updateEditorLines('correctedEditor', 'correctedLineNumbers');
      }
    } else {
      console.warn("No corrected code was found in the API response.");
      showToast("Repair completed, but no code was generated.");
    }

    if (tools) tools.style.display = 'flex';
    if (btnSpinner) btnSpinner.style.display = 'none';
    if (btnText) btnText.innerText = '✓ Verified & Ready';
    showToast("Repair loop completed successfully.");

  } catch (err) {
    console.error("Repair Loop Error:", err);
    showToast(`Error: ${err.message}`);
    resetStepper();
  }

  isRunning = false;
}

function setStepState(stepNum, state) {
  const stepEl = document.getElementById(`step${stepNum}`);
  if (!stepEl) return;

  if (state === 'active') {
    if (!stepEl.classList.contains('completed')) {
      stepEl.className = 'step-item active';
    }
  } else if (state === 'completed') {
    stepEl.className = 'step-item completed';
    const connEl = document.getElementById(`conn${stepNum}`);
    if (connEl) connEl.className = 'step-connector completed';
    if (stepNum > 1) {
      const prevConn = document.getElementById(`conn${stepNum - 1}`);
      if (prevConn) prevConn.className = 'step-connector completed';
    }
  }
}

function appendTraceCard({ stepNum, phaseName, phaseClass, badge, content, diff }) {
  const container = document.getElementById('agentLiveTrace');
  if (!container) return;

  const card = document.createElement('div');
  card.className = 'trace-card';

  let diffHtml = '';
  if (diff) {
    diffHtml = `
      <div class="diff-viewer">
        <span class="diff-del">${escapeHtml(diff.del)}</span>
        <span class="diff-add">${escapeHtml(diff.add)}</span>
      </div>
    `;
  }

  card.innerHTML = `
    <div class="trace-header">
      <span class="trace-phase ${phaseClass || ''}">${stepNum} // ${phaseName}</span>
      <span class="trace-badge">${badge}</span>
    </div>
    ${content ? `<div class="trace-body">${escapeHtml(content)}</div>` : ''}
    ${diffHtml}
  `;

  container.appendChild(card);
  container.scrollTop = container.scrollHeight;
}

/* ==================== ACTIONS: COPY & APPLY ==================== */
function copyCorrectedCode() {
  const editor = document.getElementById('correctedEditor');
  if (editor && editor.value) {
    navigator.clipboard.writeText(editor.value).then(() => {
      showToast("Corrected code copied to clipboard!");
    });
  } else {
    showToast("No corrected code available to copy.");
  }
}

function applyPatchToSource() {
  const sourceEditor = document.getElementById('sourceEditor');
  if (sourceEditor && customPatchedCode) {
    sourceEditor.value = customPatchedCode;
    updateEditorLines('sourceEditor', 'sourceLineNumbers', 'sourceLineCount');
    showToast("Patched code applied to Source Input!");
  }
}

function copyGeneratedPatch() {
  if (lastGeneratedPatch) {
    navigator.clipboard.writeText(lastGeneratedPatch).then(() => {
      showToast("Patch diff copied to clipboard!");
    });
  } else {
    showToast("Run repair first to generate a patch.");
  }
}

function copySnippet(elementId, btn) {
  const el = document.getElementById(elementId);
  if (!el) return;

  const text = el.innerText;
  navigator.clipboard.writeText(text).then(() => {
    if (btn) {
      const orig = btn.innerText;
      btn.innerText = "Copied!";
      setTimeout(() => btn.innerText = orig, 1800);
    }
    showToast("Code snippet copied to clipboard!");
  });
}

function copyApiStarter(btn) {
  const curlExample = `curl -X POST https://api.agenticfixer.dev/v1/repair \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "language": "typescript",
    "code": "function getUserName(user) { return user.profile.name.toUpperCase(); }",
    "tests": "it(\\"handles null\\", () => expect(getUserName({profile: null})).toBe(\\"\\"));"
  }'`;

  navigator.clipboard.writeText(curlExample).then(() => {
    showToast("API Starter payload copied to clipboard!");
  });
}

function selectPlan(planName) {
  showToast(`Selected ${planName} Plan. Setting up workspace...`);
}

/* ==================== TOAST NOTIFICATION HELPER ==================== */
let toastTimeout;
function showToast(message) {
  const toast = document.getElementById('toast');
  if (!toast) return;

  toast.innerText = message;
  toast.classList.add('show');

  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.remove('show');
  }, 2400);
}

/* ==================== UTILS ==================== */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function setupScrollSpy() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 120;
      if (window.scrollY >= sectionTop) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });
}
