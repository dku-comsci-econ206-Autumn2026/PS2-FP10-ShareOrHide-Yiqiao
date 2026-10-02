export const ACTIONS = ["M", "P", "F"];

export function stateKey(mechanism, congestion, ownType, rivalType, ownAction, rivalAction) {
  return [mechanism, congestion, ownType, rivalType, ownAction, rivalAction].join("|");
}

export function lookupRecord(data, mechanism, congestion, ownType, rivalType, ownAction, rivalAction) {
  const key = stateKey(mechanism, congestion, ownType, rivalType, ownAction, rivalAction);
  const record = data.state_index[key];
  if (!record) throw new Error(`Missing validated model state: ${key}`);
  return record;
}

export function newSoloState(scenario) {
  return {
    phase: "baseline",
    congestion: scenario.congestion,
    ownType: scenario.ownType,
    rivalType: scenario.rivalType,
    baselineAction: null,
    ccarAction: null,
    auction: null,
  };
}

export function resetSoloState(scenario) {
  return newSoloState(scenario);
}

export function peerPrivateView(state) {
  if (!["baseline_A", "baseline_B", "ccar_A", "ccar_B"].includes(state.phase)) {
    throw new Error("Peer state is not a private decision turn");
  }
  const operator = state.phase.endsWith("_A") ? "A" : "B";
  const mechanism = state.phase.startsWith("ccar") ? "ccar" : "baseline";
  return {
    operator,
    mechanism,
    congestion: state.congestion,
    ownType: state.types[operator],
    otherType: "Unknown",
    otherAction: "Hidden until both submit",
  };
}

export function lockPeerChoice(state, action) {
  const view = peerPrivateView(state);
  const updated = structuredClone(state);
  updated[`${view.mechanism}Choices`][view.operator] = action;
  updated.phase = view.operator === "A" ? `${view.mechanism}_handoff` : `${view.mechanism}_reveal`;
  return updated;
}

export function secondPriceOutcome(values, bids) {
  const names = Object.keys(bids);
  if (!names.length || names.some((name) => !(name in values))) {
    throw new Error("Values and bids must name the same eligible operators");
  }
  for (const name of names) {
    if (!Number.isFinite(values[name]) || !Number.isFinite(bids[name]) || values[name] < 0 || bids[name] < 0) {
      throw new Error("Values and bids must be finite and nonnegative");
    }
  }
  const ranked = [...names].sort((a, b) => bids[b] - bids[a] || a.localeCompare(b));
  const winner = ranked[0];
  const payment = ranked.length > 1 ? bids[ranked[1]] : 0;
  const efficientWinner = [...names].sort((a, b) => values[b] - values[a] || a.localeCompare(b))[0];
  return {
    winner,
    payment,
    winnerUtility: values[winner] - payment,
    participantUtility: winner === "Participant" ? values.Participant - payment : 0,
    efficientWinner,
    allocationEfficient: winner === efficientWinner,
  };
}
