import {
  ACTIONS,
  lockPeerChoice,
  lookupRecord,
  newSoloState,
  peerPrivateView,
  resetSoloState,
  secondPriceOutcome,
} from "./js/logic.mjs";

const EVIDENCE = "This Space is an exploratory classroom decision exercise. Participant choices are not a representative sample of drone operators, firms, or the public. They do not establish how real operators would behave and do not validate the model's external accuracy.";
const MOTIVATIONS = [
  "Commercial privacy", "Traffic efficiency", "Expected payoff", "Reciprocity",
  "Fairness", "Competitive advantage", "Uncertainty about rival", "Other",
];
const ACTION_DESCRIPTIONS = {
  M: "Mandatory/basic information only; no additional commercially sensitive flight-intent detail.",
  P: "Next sector, coarse ETA, and approximate traffic volume.",
  F: "Richer planned route and timing information, with greater commercial exposure.",
};

let modelData = null;
let soloState = null;
let peerState = null;
let randomCounter = 0;

const $ = (selector) => document.querySelector(selector);
const actionName = (code) => modelData.labels.actions[code];
const typeName = (code) => modelData.labels.types[code];
const fmt = (value, digits = 3) => Number(value).toFixed(digits);

function seededRandom(seedText) {
  let seed;
  if (String(seedText ?? "").trim() === "") {
    const buffer = new Uint32Array(1);
    crypto.getRandomValues(buffer);
    seed = buffer[0] ^ (++randomCounter);
  } else {
    const raw = String(seedText);
    seed = 2166136261;
    for (let index = 0; index < raw.length; index += 1) {
      seed ^= raw.charCodeAt(index);
      seed = Math.imul(seed, 16777619);
    }
  }
  return () => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 4294967296;
  };
}

function pick(rng, values) {
  return values[Math.floor(rng() * values.length)];
}

function soloScenario(seedText) {
  const rng = seededRandom(seedText);
  return {
    congestion: pick(rng, ["Low", "Medium", "High"]),
    ownType: pick(rng, ["L", "H"]),
    rivalType: pick(rng, ["L", "H"]),
  };
}

function peerScenario(seedText) {
  const rng = seededRandom(seedText);
  return {
    phase: "baseline_A",
    congestion: pick(rng, ["Low", "Medium", "High"]),
    types: { A: pick(rng, ["L", "H"]), B: pick(rng, ["L", "H"]) },
    baselineChoices: {},
    ccarChoices: {},
    reflections: {},
  };
}

function actionButtons(scope) {
  return `<div class="choice-grid">${ACTIONS.map((action) => `
    <button class="choice-button" data-choice-scope="${scope}" data-action="${action}">
      <strong>${actionName(action)}</strong><span>${ACTION_DESCRIPTIONS[action]}</span>
    </button>`).join("")}</div>`;
}

function reflectionFields(prefix, prompt) {
  return `<div class="reflection-box">
    <strong>What motivated your choice? Select any that apply.</strong>
    <div class="checkbox-grid">${MOTIVATIONS.map((item, index) => `
      <label><input type="checkbox" name="${prefix}-motivation" value="${item}" id="${prefix}-m${index}">${item}</label>`).join("")}</div>
    <label>${prompt}<textarea id="${prefix}-reflection" aria-label="${prompt}"></textarea></label>
    <p class="privacy-note">This optional response stays in browser memory and is not submitted anywhere.</p>
  </div>`;
}

function scenarioMetrics(congestion, ownType, rivalLabel = "Unknown") {
  const d = modelData.labels.congestion[congestion];
  return `<div class="scenario-grid">
    <div class="metric"><span>Current congestion</span><strong>${congestion} (d = ${d})</strong></div>
    <div class="metric"><span>Your confidentiality sensitivity</span><strong>${typeName(ownType)}</strong></div>
    <div class="metric"><span>Rival confidentiality sensitivity</span><strong>${rivalLabel}</strong></div>
    <div class="metric"><span>Prior</span><strong>Pr(Low) = 50% · Pr(High) = 50%</strong></div>
  </div>`;
}

function strategyText(strategy) {
  return `Low-confidentiality type → ${actionName(strategy.L)}; High-confidentiality type → ${actionName(strategy.H)}`;
}

function firstBestText(profiles) {
  return profiles.map(([a, b]) => `A ${actionName(a)} / B ${actionName(b)}`).join("; ");
}

function payoffTable(mechanism, congestion, ownType, rivalType, rivalAction) {
  const rows = ACTIONS.map((action) => {
    const record = lookupRecord(modelData, mechanism, congestion, ownType, rivalType, action, rivalAction);
    return `<tr><td>${actionName(action)}</td><td class="number">${fmt(record.own_payoff)}</td></tr>`;
  }).join("");
  return `<div class="table-wrap"><table><thead><tr><th>Your action</th><th class="number">Your payoff</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function enableResults() {
  const button = document.querySelector('[data-tab="results"]');
  button.disabled = false;
  button.removeAttribute("title");
}

function disableResults() {
  const button = document.querySelector('[data-tab="results"]');
  button.disabled = true;
  button.title = "Complete a disclosure choice first";
}

function renderSoloChoice() {
  const workspace = $("#solo-workspace");
  workspace.innerHTML = `<article class="card private-card">
    <p class="eyebrow">Private scenario</p><h3>Round 1 — Baseline decision</h3>
    ${scenarioMetrics(soloState.congestion, soloState.ownType)}
    <p><strong>How much additional flight-intent information would you voluntarily disclose?</strong></p>
    <p class="privacy-note">Mandatory safety information remains available regardless of your choice.</p>
    ${actionButtons("solo-baseline")}
    ${reflectionFields("solo-baseline", "Why did you choose this disclosure level? (optional)")}
  </article>`;
}

function renderBaselineReveal() {
  const benchmark = modelData.benchmarks.baseline[soloState.congestion];
  const rivalAction = benchmark.strategy_B[soloState.rivalType];
  const record = lookupRecord(modelData, "baseline", soloState.congestion, soloState.ownType, soloState.rivalType, soloState.baselineAction, rivalAction);
  const workspace = $("#solo-workspace");
  workspace.innerHTML = `<article class="card reveal-card">
    <p class="eyebrow">Choice recorded · benchmark now revealed</p><h3>Baseline reveal</h3>
    <div class="metric-grid">
      <div class="metric"><span>Rival realized type</span><strong>${typeName(soloState.rivalType)}</strong></div>
      <div class="metric"><span>Rival benchmark action</span><strong>${actionName(rivalAction)}</strong></div>
      <div class="metric"><span>Your choice / payoff</span><strong>${actionName(soloState.baselineAction)} · ${fmt(record.own_payoff)}</strong></div>
      <div class="metric"><span>Realized social welfare</span><strong>${fmt(record.underlying_social_welfare)}</strong></div>
    </div>
    ${payoffTable("baseline", soloState.congestion, soloState.ownType, soloState.rivalType, rivalAction)}
    <div class="benchmark"><strong>Bayesian benchmark</strong><br>${strategyText(benchmark.strategy_A)}.<br>For your type: <strong>${actionName(record.baseline_bne_action_own)}</strong>.</div>
    <p><strong>Full-information first best:</strong> ${firstBestText(record.first_best_profiles)}<br>
      <strong>First-best welfare:</strong> ${fmt(record.first_best_welfare)} · <strong>Realized welfare gap:</strong> ${fmt(record.welfare_gap)}</p>
    <p class="privacy-note"><strong>Evidence boundary:</strong> ${EVIDENCE}</p>
  </article>
  <article class="card private-card">
    <p class="eyebrow">Mechanism comparison</p><h3>Round 2 — Congestion-Contingent Access Rule (CCAR)</h3>
    <p><strong>Mandatory safety information remains available to every operator.</strong> CCAR changes only enhanced non-safety coordination information such as richer congestion forecasts and rerouting support.</p>
    <p>At the validated Medium/High benchmark, Minimum disclosure receives α<sub>M</sub> = ${modelData.metadata.ccar_alpha_M}; Partial and Full receive full enhanced access. Low congestion has no restriction.</p>
    <p><strong>Under this rule, how much information would you disclose?</strong></p>
    ${actionButtons("solo-ccar")}
    ${reflectionFields("solo-ccar", "Why did CCAR change—or not change—your choice? (optional)")}
  </article>`;
}

function renderCCARReveal() {
  const baseline = modelData.benchmarks.baseline[soloState.congestion];
  const benchmark = modelData.benchmarks.ccar[soloState.congestion];
  const rivalAction = benchmark.strategy_B[soloState.rivalType];
  const record = lookupRecord(modelData, "ccar", soloState.congestion, soloState.ownType, soloState.rivalType, soloState.ccarAction, rivalAction);
  const levels = { M: 0, P: 1, F: 2 };
  const direction = levels[soloState.ccarAction] > levels[soloState.baselineAction] ? "increased" : levels[soloState.ccarAction] < levels[soloState.baselineAction] ? "decreased" : "stayed the same";
  const choiceCards = document.querySelectorAll("#solo-workspace .private-card");
  choiceCards.forEach((card) => card.remove());
  $("#solo-workspace").innerHTML += `<article class="card reveal-card">
    <p class="eyebrow">CCAR choice recorded</p><h3>CCAR comparison</h3>
    <p><strong>Mandatory safety information remains available to every operator.</strong> CCAR changes only enhanced non-safety coordination information.</p>
    <div class="metric-grid">
      <div class="metric"><span>Baseline choice</span><strong>${actionName(soloState.baselineAction)}</strong></div>
      <div class="metric"><span>CCAR choice</span><strong>${actionName(soloState.ccarAction)}</strong></div>
      <div class="metric"><span>Disclosure change</span><strong>${direction}</strong></div>
      <div class="metric"><span>CCAR payoff</span><strong>${fmt(record.own_payoff)}</strong></div>
    </div>
    ${payoffTable("ccar", soloState.congestion, soloState.ownType, soloState.rivalType, rivalAction)}
    <p><strong>Baseline benchmark for your type:</strong> ${actionName(baseline.strategy_A[soloState.ownType])}<br>
      <strong>CCAR benchmark for your type:</strong> ${actionName(benchmark.strategy_A[soloState.ownType])}<br>
      <strong>Underlying social welfare:</strong> ${fmt(record.underlying_social_welfare)}</p>
    <p>In the benchmark model, CCAR changes incentives in some parameter regions but not all.</p>
    <p class="privacy-note"><strong>Evidence boundary:</strong> ${EVIDENCE}</p>
  </article>
  <article class="card">
    <p class="eyebrow">Optional downstream application</p><h3>One commercial priority-access slot</h3>
    <p>Residual scarcity may remain even with better information. Emergency and public-safety flights are outside this auction. This is a bounded Week 5 application, not the main research contribution.</p>
    <button class="button primary" id="open-auction">Try priority-slot allocation</button>
    <div id="auction-workspace"></div>
  </article>
  <article class="card">
    <h3>Final reflection</h3>
    <label>What mattered most in your decision?<textarea aria-label="What mattered most in your decision?"></textarea></label>
    <label>Would a trusted partner change your choice?<textarea aria-label="Would a trusted partner change your choice?"></textarea></label>
    <p class="privacy-note">These optional reflections remain in memory only and are not interpreted automatically as scientific evidence.</p>
  </article>`;
}

function openAuction() {
  const scenarios = modelData.auction.session_scenarios;
  const rng = seededRandom(`${soloState.congestion}-${soloState.ownType}-${randomCounter++}`);
  const scenario = scenarios[Math.floor(rng() * scenarios.length)];
  soloState.auction = structuredClone(scenario);
  $("#auction-workspace").innerHTML = `<div class="card private-card">
    <h3>Your private priority value: ${scenario.values.Participant} normalized units</h3>
    <p>Rival bids remain hidden until submission. Setting: <strong>${scenario.setting}</strong>.</p>
    <label>Your sealed bid <input id="auction-bid" type="number" min="0" step="0.1" value="${scenario.values.Participant}"></label>
    <div class="inline-actions"><button class="button primary" id="submit-auction">Submit bid</button></div>
  </div>`;
}

function submitAuction() {
  const bid = Number($("#auction-bid").value);
  if (!Number.isFinite(bid) || bid < 0) return;
  const scenario = soloState.auction;
  const bids = { Participant: bid, ...scenario.rival_bids };
  const outcome = secondPriceOutcome(scenario.values, bids);
  const rows = Object.keys(bids).sort().map((name) => `<tr><td>${name}</td><td class="number">${fmt(scenario.values[name], 2)}</td><td class="number">${fmt(bids[name], 2)}</td></tr>`).join("");
  $("#auction-workspace").innerHTML = `<div class="card reveal-card"><h3>Priority-slot result</h3>
    <div class="table-wrap"><table><thead><tr><th>Operator</th><th class="number">Private value</th><th class="number">Bid</th></tr></thead><tbody>${rows}</tbody></table></div>
    <p><strong>Winner:</strong> ${outcome.winner}<br><strong>Second-highest payment:</strong> ${fmt(outcome.payment, 2)}<br>
      <strong>Your utility:</strong> ${fmt(outcome.participantUtility, 2)}<br><strong>Efficient winner:</strong> ${outcome.efficientWinner}<br>
      <strong>Efficient allocation:</strong> ${outcome.allocationEfficient ? "Yes" : "No"}</p>
    <p>Under the standard independent-private-values second-price benchmark, truthful bidding is weakly dominant. This does not extend automatically to common- or interdependent-value settings.</p></div>`;
}

function renderPeerTurn() {
  const view = peerPrivateView(peerState);
  $("#peer-workspace").innerHTML = `<article class="card private-card">
    <p class="eyebrow">Private screen · ${view.mechanism === "ccar" ? "CCAR" : "Baseline"}</p>
    <h3>Operator ${view.operator}</h3>
    ${scenarioMetrics(view.congestion, view.ownType)}
    ${view.mechanism === "ccar" ? "<p><strong>CCAR applies only to enhanced non-safety coordination information; mandatory safety information remains universal.</strong></p>" : ""}
    <p>Choose before seeing the other operator's type or action.</p>
    ${actionButtons("peer")}
    <label>What mattered most? (optional)<textarea id="peer-reflection" aria-label="Peer reflection"></textarea></label>
    <p class="privacy-note">This private reflection is never shown on the next operator's decision screen.</p>
  </article>`;
}

function renderHandoff(mechanism) {
  $("#peer-workspace").innerHTML = `<article class="card handoff-card">
    <p class="eyebrow">Neutral handoff</p><h3>Pass the screen to Operator B</h3>
    <p>Operator A's private type, choice, motivation, and payoff are hidden.</p>
    <button class="button primary" id="show-peer-b" data-mechanism="${mechanism}">Operator B: show my private prompt</button>
  </article>`;
}

function renderPeerReveal(mechanism) {
  const choices = peerState[`${mechanism}Choices`];
  const record = lookupRecord(modelData, mechanism, peerState.congestion, peerState.types.A, peerState.types.B, choices.A, choices.B);
  const benchmark = modelData.benchmarks[mechanism][peerState.congestion];
  $("#peer-workspace").innerHTML = `<article class="card reveal-card">
    <p class="eyebrow">Both choices recorded</p><h3>${mechanism === "ccar" ? "CCAR" : "Baseline"} peer reveal</h3>
    <div class="metric-grid">
      <div class="metric"><span>Operator A</span><strong>${typeName(peerState.types.A)} · ${actionName(choices.A)} · payoff ${fmt(record.own_payoff)}</strong></div>
      <div class="metric"><span>Operator B</span><strong>${typeName(peerState.types.B)} · ${actionName(choices.B)} · payoff ${fmt(record.rival_payoff)}</strong></div>
      <div class="metric"><span>Underlying welfare</span><strong>${fmt(record.underlying_social_welfare)}</strong></div>
      <div class="metric"><span>First-best welfare</span><strong>${fmt(record.first_best_welfare)}</strong></div>
    </div>
    <div class="benchmark"><strong>Bayesian benchmark</strong><br>Operator A: ${strategyText(benchmark.strategy_A)}.<br>Operator B: ${strategyText(benchmark.strategy_B)}.</div>
    <p><strong>Full-information first best:</strong> ${firstBestText(record.first_best_profiles)}</p>
    <p class="privacy-note"><strong>Evidence boundary:</strong> ${EVIDENCE}</p>
    ${mechanism === "baseline" ? '<button class="button primary" id="begin-peer-ccar">Begin peer CCAR round</button>' : '<h3>Peer reflection</h3><label>Did CCAR or trust change how you view the choices?<textarea aria-label="Peer final reflection"></textarea></label><p class="privacy-note">This response remains in browser memory only.</p>'}
  </article>`;
}

function renderModelResults() {
  $("#model-results").innerHTML = ["Low", "Medium", "High"].map((label) => {
    const baseline = modelData.benchmarks.baseline[label];
    const ccar = modelData.benchmarks.ccar[label];
    return `<article class="card result-card"><h3>${label} congestion</h3><div class="d">d = ${baseline.d}</div>
      <dl><dt>Baseline BNE</dt><dd>${strategyText(baseline.strategy_A)}</dd>
      <dt>CCAR BNE</dt><dd>${strategyText(ccar.strategy_A)}</dd>
      <dt>Expected BNE welfare</dt><dd>${fmt(baseline.expected_induced_underlying_welfare, 6)}</dd>
      <dt>Expected first best</dt><dd>${fmt(baseline.expected_first_best_welfare, 6)}</dd>
      <dt>Baseline welfare gap</dt><dd>${fmt(baseline.welfare_gap, 6)}</dd></dl></article>`;
  }).join("");
  const auction = modelData.auction;
  $("#auction-results").innerHTML = `<h3>Verified priority-slot benchmark</h3>
    <p>Values A=8, B=5, C=3, D=2; FCFS arrival B, C, A, D.</p>
    <ul><li>FCFS: ${auction.benchmark_example.fcfs.winner} wins; efficiency ${fmt(auction.benchmark_example.fcfs.allocative_efficiency, 3)}.</li>
    <li>Second price: ${auction.benchmark_example.second_price.winner} wins; payment ${fmt(auction.benchmark_example.second_price.payment, 0)}; winner utility ${fmt(auction.benchmark_example.second_price.winner_utility, 0)}; efficiency ${fmt(auction.benchmark_example.second_price.allocative_efficiency, 1)}.</li>
    <li>10,000-round FCFS mean efficiency: ${fmt(auction.monte_carlo.fcfs_mean_efficiency, 6)}.</li>
    <li>Truthful second-price mean efficiency: ${fmt(auction.monte_carlo.truthful_second_price_mean_efficiency, 6)}.</li></ul>
    <p>Emergency and public-safety flights are outside this commercial auction.</p>`;
  $("#provenance").textContent = `Economic source ${modelData.metadata.source_commit} · behavioral checkpoint ${modelData.metadata.behavioral_checkpoint} · parameter hash ${modelData.metadata.model_parameter_hash}`;
}

function activateTab(name) {
  document.querySelectorAll(".tab").forEach((button) => {
    const active = button.dataset.tab === name;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", String(active));
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    const active = panel.id === `tab-${name}`;
    panel.classList.toggle("is-active", active);
    panel.hidden = !active;
  });
}

document.addEventListener("click", (event) => {
  const tab = event.target.closest(".tab");
  if (tab && !tab.disabled) activateTab(tab.dataset.tab);

  if (event.target.id === "start-solo" || event.target.id === "new-solo") {
    const scenario = soloScenario($("#solo-seed").value);
    soloState = event.target.id === "new-solo" ? resetSoloState(scenario) : newSoloState(scenario);
    disableResults();
    renderSoloChoice();
  }
  const choice = event.target.closest("[data-choice-scope]");
  if (choice?.dataset.choiceScope === "solo-baseline") {
    soloState.baselineAction = choice.dataset.action;
    soloState.phase = "ccar";
    enableResults();
    renderBaselineReveal();
  } else if (choice?.dataset.choiceScope === "solo-ccar") {
    soloState.ccarAction = choice.dataset.action;
    soloState.phase = "complete";
    renderCCARReveal();
  } else if (choice?.dataset.choiceScope === "peer") {
    const mechanism = peerState.phase.startsWith("ccar") ? "ccar" : "baseline";
    const operator = peerState.phase.endsWith("_A") ? "A" : "B";
    peerState.reflections[`${mechanism}_${operator}`] = $("#peer-reflection")?.value ?? "";
    peerState = lockPeerChoice(peerState, choice.dataset.action);
    if (peerState.phase.endsWith("handoff")) renderHandoff(mechanism);
    else { enableResults(); renderPeerReveal(mechanism); }
  }

  if (event.target.id === "open-auction") openAuction();
  if (event.target.id === "submit-auction") submitAuction();
  if (event.target.id === "start-peer" || event.target.id === "new-peer") {
    peerState = peerScenario($("#peer-seed").value);
    disableResults();
    renderPeerTurn();
  }
  if (event.target.id === "show-peer-b") {
    const mechanism = event.target.dataset.mechanism;
    peerState.phase = `${mechanism}_B`;
    renderPeerTurn();
  }
  if (event.target.id === "begin-peer-ccar") {
    peerState.phase = "ccar_A";
    renderPeerTurn();
  }
});

async function initialize() {
  try {
    const response = await fetch("./data/validated_model_data.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Model data request failed (${response.status})`);
    modelData = await response.json();
    if (modelData.metadata.source_commit !== "791e12224576e5963fd5672f8f90acdcea5556a0") {
      throw new Error("Unexpected model-data provenance");
    }
    renderModelResults();
    const status = $("#load-status");
    status.textContent = `Validated model data ready · ${modelData.metadata.state_record_count} finite disclosure states`;
    status.classList.add("is-ready");
  } catch (error) {
    const status = $("#load-status");
    status.textContent = `Unable to load validated model data: ${error.message}`;
    status.classList.add("is-error");
    document.querySelectorAll("button").forEach((button) => { button.disabled = true; });
  }
}

document.querySelectorAll(".tab").forEach((button) => button.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") activateTab(button.dataset.tab);
}));

initialize();
