/* ==========================================================================
   AGENTIC CODE FIXER - CLIENT APPLICATION LOGIC
   Handles interactive live code repair, custom debugging, and UI interactions
   ========================================================================== */

let currentLang = 'typescript';
let isRunning = false;
let currentStep = 0;
let lastGeneratedPatch = "";
let customPatchedCode = "";
let activeFixtureSource = "";
let activeFixtureTests = "";
let activeFixtureName = "";

document.addEventListener('DOMContentLoaded', () => {
  initEditors();
  loadFixture(currentLang);
  setupScrollSpy();
});

function detectClientLanguage(code) {
  const clean = code.trim();
  if (!clean) return currentLang;
  
  if ((clean.includes('def ') || clean.includes('import ') || clean.includes('elif ') || clean.includes('print(')) && !clean.includes('function ') && !clean.includes('console.log')) {
    return 'python';
  }
  if (clean.includes('public static void main') || clean.includes('System.out.println') || clean.includes('public class ')) {
    return 'java';
  }
  if (clean.includes('fn ') || clean.includes('println!') || clean.includes('let mut ')) {
    return 'rust';
  }
  if (clean.includes('interface ') || clean.includes(': string') || clean.includes(': number') || clean.includes(': boolean')) {
    return 'typescript';
  }
  if (clean.includes('function ') || clean.includes('const ') || clean.includes('let ') || clean.includes('console.log')) {
    return 'javascript';
  }
  return currentLang;
}

/* ==================== EDITOR & LINE NUMBER MANAGEMENT ==================== */
function updateTestContractUI() {
  const testsEditor = document.getElementById('testsEditor');
  const indicator = document.getElementById('testsStatusIndicator');
  const badge = document.getElementById('testsFooterBadge');
  if (!testsEditor) return;

  const hasTests = testsEditor.value.trim().length > 0;
  if (indicator) {
    indicator.innerText = hasTests ? 'Contract Active' : 'Optional / Auto-Gen';
    indicator.className = hasTests ? 'status-indicator' : 'status-indicator inactive';
  }
  if (badge) {
    badge.innerText = hasTests ? 'Test contract attached' : 'Auto-synthesize tests';
  }
}

function clearTestsEditor() {
  const testsEditor = document.getElementById('testsEditor');
  if (testsEditor) {
    testsEditor.value = '';
    updateEditorLines('testsEditor', 'testsLineNumbers');
    updateTestContractUI();
    showToast('Tests cleared — agent will synthesize tailored tests');
  }
}

function handleSourceChange(sourceVal) {
  const fileName = document.getElementById('ideFileName');
  const testsEditor = document.getElementById('testsEditor');
  const extMap = { python: 'py', typescript: 'ts', javascript: 'js', rust: 'rs' };
  const ext = extMap[currentLang] || 'txt';

  const isMatchingFixture = activeFixtureSource && sourceVal.trim() === activeFixtureSource.trim();

  if (isMatchingFixture) {
    if (fileName && activeFixtureName) fileName.innerText = activeFixtureName;
  } else {
    // Custom user code
    if (fileName) fileName.innerText = `custom_code.${ext}`;

    // If the tests editor still holds the stale fixture tests, auto-clear it
    // so stale fixture tests (e.g. binary_search assertions) do not pollute the user's custom code!
    if (testsEditor && activeFixtureTests && testsEditor.value.trim() === activeFixtureTests.trim()) {
      testsEditor.value = '';
      updateEditorLines('testsEditor', 'testsLineNumbers');
      updateTestContractUI();
      showToast('Cleared fixture tests for custom code');
    }
  }
}

function initEditors() {
  const sourceEditor = document.getElementById('sourceEditor');
  const testsEditor = document.getElementById('testsEditor');
  const langSelect = document.getElementById('languageSelect');

  if (sourceEditor) {
    sourceEditor.addEventListener('input', () => {
      updateEditorLines('sourceEditor', 'sourceLineNumbers', 'sourceLineCount');
      const val = sourceEditor.value;
      const detected = detectClientLanguage(val);
      if (detected && detected !== currentLang) {
        currentLang = detected;
        if (langSelect) langSelect.value = detected;
      }
      handleSourceChange(val);
    });
    updateEditorLines('sourceEditor', 'sourceLineNumbers', 'sourceLineCount');
  }

  if (testsEditor) {
    testsEditor.addEventListener('input', () => {
      updateEditorLines('testsEditor', 'testsLineNumbers');
      updateTestContractUI();
    });
    updateEditorLines('testsEditor', 'testsLineNumbers');
    updateTestContractUI();
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

  activeFixtureSource = fixture.source;
  activeFixtureTests = fixture.tests;
  activeFixtureName = fixture.name;

  const sourceEditor = document.getElementById('sourceEditor');
  const testsEditor = document.getElementById('testsEditor');
  const fileName = document.getElementById('ideFileName');

  if (sourceEditor) sourceEditor.value = fixture.source;
  if (testsEditor) testsEditor.value = fixture.tests;
  if (fileName) fileName.innerText = fixture.name;

  updateEditorLines('sourceEditor', 'sourceLineNumbers', 'sourceLineCount');
  updateEditorLines('testsEditor', 'testsLineNumbers');
  updateTestContractUI();

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

/* ==================== PROGRESS BAR & CONCURRENCY CONTROLS ==================== */
function setProgressBar(active) {
  const progBar = document.getElementById('repairProgressBar');
  if (progBar) {
    if (active) progBar.classList.add('active');
    else progBar.classList.remove('active');
  }
}

function setConcurrencyLock(locked) {
  isRunning = locked;
  const repairBtn = document.getElementById('runRepairBtn');
  const duckBtn = document.getElementById('runDuckBtn');

  if (repairBtn) {
    repairBtn.disabled = locked;
  }

  if (duckBtn) {
    duckBtn.disabled = locked;
  }
}

/* ==================== REPAIR LOOP EXECUTION ENGINE ==================== */
function resetStepper() {
  setConcurrencyLock(false);
  setProgressBar(false);
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
  setConcurrencyLock(true);

  const sourceEditor = document.getElementById('sourceEditor');
  const testsEditor = document.getElementById('testsEditor');
  const defaultFixture = FIXTURES[currentLang] || FIXTURES['typescript'];

  const currentSource = sourceEditor ? sourceEditor.value : defaultFixture.source;
  let currentTests = testsEditor ? testsEditor.value : defaultFixture.tests;

  // Safeguard: If currentTests is identical to the current fixture's tests,
  // but the source code has been replaced with custom code, do not send the fixture's tests!
  if (defaultFixture && currentTests.trim() === defaultFixture.tests.trim() && currentSource.trim() !== defaultFixture.source.trim()) {
    currentTests = "";
  }

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
  if (tools) tools.style.display = 'none';

  setProgressBar(true);
  setStepState(1, 'active');

  const requestPayload = {
    code: currentSource,
    tests: currentTests,
    lang: currentLang
  };

  const stageMap = {
    'diagnosing': { step: 1, nextStep: 2, phase: 'ANALYSIS', class: 'mint' },
    'generating_tests': { step: 2, nextStep: 3, phase: 'DIAGNOSIS', class: 'coral' },
    'fixing': { step: 3, nextStep: 4, phase: 'PATCH SYNTHESIS', class: 'amber' },
    'testing': { step: 4, nextStep: 5, phase: 'SANDBOX RE-RUN', class: 'mint' },
    'done': { step: 5, nextStep: 5, phase: 'VERIFICATION & VALIDATION', class: 'mint' }
  };

  let finalCorrectedCode = "";
  const completedSteps = new Set();

  const handleStep = async (step) => {
    const stage = step.stage;
    const config = stageMap[stage] || { step: 5, nextStep: 5, phase: 'VALIDATION', class: 'mint' };

    if (stage === 'diagnosing') {
      setStepState(1, 'completed');
      setStepState(2, 'active');
      completedSteps.add(1);
    } else if (stage === 'generating_tests') {
      setStepState(2, 'completed');
      setStepState(3, 'active');
      completedSteps.add(2);
    } else if (stage === 'fixing') {
      setStepState(3, 'active');
    } else if (stage === 'testing') {
      setStepState(3, 'completed');
      setStepState(4, 'active');
      completedSteps.add(3);
    } else if (stage === 'done') {
      setStepState(4, 'completed');
      setStepState(5, 'completed');
      completedSteps.add(4);
      completedSteps.add(5);
    }

    if (step.corrected_code) {
      finalCorrectedCode = step.corrected_code;
      customPatchedCode = step.corrected_code;

      if (correctedBox) correctedBox.style.display = 'block';
      if (correctedEditor) {
        correctedEditor.value = step.corrected_code;
        updateEditorLines('correctedEditor', 'correctedLineNumbers');
      }
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
      if (step.edge_cases && step.edge_cases.length > 0) {
        cardData.content += `\nEdge Cases: ${step.edge_cases.join(', ')}`;
      }
    } else if (stage === 'generating_tests') {
      cardData.badge = "Test Contract";
      cardData.content = step.generated_tests || "Synthesizing test specs...";
    } else if (stage === 'fixing') {
      cardData.badge = `Iteration ${step.iteration || 1}`;
      cardData.content = "Generating candidate implementation patch...";
    } else if (stage === 'testing') {
      const results = step.test_results || {};
      const passed = results.passed || 0;
      const total = results.total || 0;
      cardData.badge = `Tests: ${passed}/${total} Passed`;
      cardData.content = results.failure_details && results.failure_details.length > 0
        ? results.failure_details.join('\n')
        : "All unit assertions passing in sandbox.";
    } else if (stage === 'done') {
      cardData.badge = `Status: ${step.status || 'Verified'}`;
      cardData.content = `Repaired in ${step.iterations_taken || 1} attempts. Safety proof confirmed.`;
      if (step.changelog && step.changelog.length > 0) {
        cardData.content += `\n\nChangelog:\n${step.changelog.map(c => `• ${c}`).join('\n')}`;
      }
    }

    appendTraceCard(cardData);
  };

  let connectionAttempts = 0;
  const maxAttempts = 2;
  let receivedAnyEvent = false;

  while (connectionAttempts < maxAttempts) {
    connectionAttempts++;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 65000);

    try {
      const streamUrl = `${getApiBaseUrl()}/repair/stream`;
      const response = await fetch(streamUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify(requestPayload),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Server returned HTTP ${response.status}: ${errText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let streamBuffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunkText = decoder.decode(value, { stream: true });
        streamBuffer += chunkText;

        const eventBlocks = streamBuffer.split('\n\n');
        streamBuffer = eventBlocks.pop() || '';

        for (const block of eventBlocks) {
          const lines = block.split('\n');
          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('data:')) {
              const rawData = trimmed.replace(/^data:\s*/, '').trim();
              if (rawData === '[DONE]') continue;

              try {
                const parsedStep = JSON.parse(rawData);
                receivedAnyEvent = true;
                await handleStep(parsedStep);
              } catch (parseErr) {
                console.warn("Could not parse SSE JSON line:", rawData, parseErr);
              }
            }
          }
        }
      }

      break;

    } catch (streamErr) {
      clearTimeout(timeoutId);
      console.warn(`SSE stream attempt ${connectionAttempts} failed:`, streamErr);

      if (connectionAttempts < maxAttempts && !receivedAnyEvent) {
        showToast("Network hiccup detected. Reconnecting stream automatically... ⚡");
        await sleep(1200);
      } else {
        setProgressBar(false);
        showToast(`Repair Stream Error: ${streamErr.message}`);
        setConcurrencyLock(false);
        if (btnSpinner) btnSpinner.style.display = 'none';
        if (btnText) btnText.innerText = '▶ Retry repair';
        return;
      }
    }
  }

  setProgressBar(false);

  for (let i = 1; i <= 5; i++) {
    setStepState(i, 'completed');
  }

  if (tools) tools.style.display = 'flex';
  if (btnSpinner) btnSpinner.style.display = 'none';
  if (btnText) btnText.innerText = '✓ Verified & Ready';

  setConcurrencyLock(false);
  showToast("Repair loop completed successfully.");
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

function getApiBaseUrl() {
  if (typeof window !== 'undefined' && window.location && (window.location.protocol === 'http:' || window.location.protocol === 'https:')) {
    // If running on a live web server or port 8000
    return window.location.origin;
  }
  return 'http://localhost:8000';
}

/* ==================== DUCK DEBUGGER LOGIC ==================== */
let duckSessionId = null;
let currentDuckLevel = 1;

function updateDuckLevelUI(level) {
  currentDuckLevel = level || 1;
  const badge = document.getElementById('duckLevelBadge');
  if (!badge) return;

  const levelNames = {
    1: 'Level 1: Conceptual',
    2: 'Level 2: Structural',
    3: 'Level 3: Implementation'
  };

  badge.innerText = levelNames[currentDuckLevel] || `Level ${currentDuckLevel}`;
  badge.className = `duck-level-badge level-${currentDuckLevel}`;
}

async function triggerDuckDebug() {
  const overlay = document.getElementById('duckChatOverlay');
  const messagesContainer = document.getElementById('duckChatMessages');

  if (!overlay) return;

  // Reset chat and open overlay
  messagesContainer.innerHTML = '';
  duckSessionId = null;
  updateDuckLevelUI(1);
  overlay.style.display = 'flex';

  appendDuckMessage('duck', "Quack! 🦆 I'm your Socratic debugging partner. I won't give you the answer right away, but I'll guide you step-by-step to discover the bug yourself.\n\nTake a look at your code and test suite. What do you think might be going wrong?", null);
}

function closeDuckChat() {
  const overlay = document.getElementById('duckChatOverlay');
  if (overlay) overlay.style.display = 'none';
}

function giveUpAndRepair() {
  closeDuckChat();
  showToast("Switching to Autonomous Multi-Agent Repair Loop... ⚡");
  triggerRunRepair();
}

function formatMarkdownSnippet(text) {
  if (!text) return '';
  // Basic markdown formatting: escape HTML, format code blocks, inline code, bold
  let safe = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Triple backticks code block
  safe = safe.replace(/```(?:[a-zA-Z0-9_-]+)?\n?([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  // Single backticks inline code
  safe = safe.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bold
  safe = safe.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // Newlines to <br> (outside pre tags)
  safe = safe.replace(/\n/g, '<br>');
  return safe;
}

function appendDuckMessage(role, text, criticMonologue = null) {
  const container = document.getElementById('duckChatMessages');
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${role}`;

  let htmlContent = formatMarkdownSnippet(text);

  if (role === 'duck' && criticMonologue) {
    htmlContent += `<div class="critic-monologue-box">💡 <em>Internal analysis:</em> ${formatMarkdownSnippet(criticMonologue)}</div>`;
  }

  bubble.innerHTML = htmlContent;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

function showDuckTypingIndicator() {
  const container = document.getElementById('duckChatMessages');
  if (!container) return null;

  const typingBubble = document.createElement('div');
  typingBubble.className = 'chat-bubble duck';
  typingBubble.id = 'duckTypingBubble';
  typingBubble.innerHTML = '<div class="duck-typing"><span></span><span></span><span></span></div>';
  container.appendChild(typingBubble);
  container.scrollTop = container.scrollHeight;
  return typingBubble;
}

function removeDuckTypingIndicator() {
  const typingBubble = document.getElementById('duckTypingBubble');
  if (typingBubble) typingBubble.remove();
}

function sendQuickPrompt(promptText) {
  const input = document.getElementById('duckChatInput');
  if (input) {
    input.value = promptText;
    sendMessageToDuck();
  }
}

async function sendMessageToDuck() {
  const input = document.getElementById('duckChatInput');
  const userMsg = input ? input.value.trim() : '';
  if (!userMsg) return;

  const sourceEditor = document.getElementById('sourceEditor');
  const testsEditor = document.getElementById('testsEditor');

  appendDuckMessage('user', userMsg);
  input.value = '';

  const sendBtn = document.getElementById('btnSendDuck');
  if (sendBtn) sendBtn.disabled = true;

  // Concurrency Guard
  setConcurrencyLock(true);
  showDuckTypingIndicator();

  let assistantBubble = null;
  let accumulatedText = "";
  let criticMonologue = null;

  try {
    const defaultFixture = FIXTURES[currentLang] || FIXTURES['typescript'];
    let testsToSend = testsEditor ? testsEditor.value : "";
    if (defaultFixture && testsToSend.trim() === defaultFixture.tests.trim() && sourceEditor && sourceEditor.value.trim() !== defaultFixture.source.trim()) {
      testsToSend = "";
    }

    const streamUrl = `${getApiBaseUrl()}/duck_chat/stream`;
    const response = await fetch(streamUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        session_id: duckSessionId,
        code: sourceEditor ? sourceEditor.value : "",
        tests: testsToSend,
        user_message: userMsg,
        language: currentLang
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Duck error (${response.status}): ${errText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let streamBuffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      streamBuffer += decoder.decode(value, { stream: true });
      const blocks = streamBuffer.split('\n\n');
      streamBuffer = blocks.pop() || '';

      for (const block of blocks) {
        const lines = block.split('\n');
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data:')) {
            const rawData = trimmed.replace(/^data:\s*/, '').trim();
            if (rawData === '[DONE]') continue;

            try {
              const data = JSON.parse(rawData);

              if (data.stage === 'pondering') {
                if (data.level) updateDuckLevelUI(data.level);
              } else if (data.stage === 'critic') {
                criticMonologue = data.critic_monologue;
              } else if (data.stage === 'chunk') {
                removeDuckTypingIndicator();

                // Incrementally stream chunk into bubble
                if (!assistantBubble) {
                  const container = document.getElementById('duckChatMessages');
                  assistantBubble = document.createElement('div');
                  assistantBubble.className = 'chat-bubble duck';
                  if (container) {
                    container.appendChild(assistantBubble);
                  }
                }

                accumulatedText += data.text;
                let html = formatMarkdownSnippet(accumulatedText);
                if (criticMonologue) {
                  html += `<div class="critic-monologue-box">💡 <em>Internal analysis:</em> ${formatMarkdownSnippet(criticMonologue)}</div>`;
                }
                assistantBubble.innerHTML = html;

                const container = document.getElementById('duckChatMessages');
                if (container) container.scrollTop = container.scrollHeight;

              } else if (data.stage === 'done') {
                duckSessionId = data.session_id;
                if (data.level) updateDuckLevelUI(data.level);

                if (!assistantBubble) {
                  removeDuckTypingIndicator();
                  appendDuckMessage('duck', data.response, data.critic_monologue);
                } else {
                  let finalHtml = formatMarkdownSnippet(data.response);
                  if (data.critic_monologue) {
                    finalHtml += `<div class="critic-monologue-box">💡 <em>Internal analysis:</em> ${formatMarkdownSnippet(data.critic_monologue)}</div>`;
                  }
                  assistantBubble.innerHTML = finalHtml;
                }

                if (data.is_solution_unlocked) {
                  showToast("🎉 Brilliant! You've identified the root cause! You can now run autonomous repair or apply your fix.");
                }
              } else if (data.stage === 'error') {
                throw new Error(data.error || "Unknown stream error");
              }
            } catch (pErr) {
              console.warn("Error parsing duck stream line:", rawData, pErr);
            }
          }
        }
      }
    }

  } catch (err) {
    removeDuckTypingIndicator();
    console.error("Duck Stream Error:", err);
    appendDuckMessage('duck', `*Quack*... I ran into an issue connecting to my brain: ${err.message}`);
    showToast(`Duck Error: ${err.message}`);
  } finally {
    removeDuckTypingIndicator();
    setConcurrencyLock(false);
    if (sendBtn) sendBtn.disabled = false;
    if (input) input.focus();
  }
}

