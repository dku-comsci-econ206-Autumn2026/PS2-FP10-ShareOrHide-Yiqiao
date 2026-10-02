import test from "node:test";
import assert from "node:assert/strict";

import {
  lockPeerChoice,
  newSoloState,
  peerPrivateView,
  resetSoloState,
  secondPriceOutcome,
} from "../js/logic.mjs";

test("highest bid wins and second-highest bid sets payment", () => {
  const outcome = secondPriceOutcome(
    { Participant: 8, B: 5, C: 3, D: 2 },
    { Participant: 8, B: 5, C: 3, D: 2 },
  );
  assert.equal(outcome.winner, "Participant");
  assert.equal(outcome.payment, 5);
  assert.equal(outcome.winnerUtility, 3);
  assert.equal(outcome.participantUtility, 3);
  assert.equal(outcome.allocationEfficient, true);
});

test("participant loser utility is zero", () => {
  const outcome = secondPriceOutcome(
    { Participant: 4, B: 9, C: 3 },
    { Participant: 4, B: 9, C: 3 },
  );
  assert.equal(outcome.winner, "B");
  assert.equal(outcome.payment, 4);
  assert.equal(outcome.participantUtility, 0);
});

test("ties use the validated deterministic operator-id rule", () => {
  const outcome = secondPriceOutcome({ A: 7, B: 7 }, { A: 7, B: 7 });
  assert.equal(outcome.winner, "A");
  assert.equal(outcome.payment, 7);
});

test("peer handoff does not expose A private state to B", () => {
  let state = {
    phase: "baseline_A",
    congestion: "Medium",
    types: { A: "H", B: "L" },
    baselineChoices: {},
    ccarChoices: {},
    reflections: { baseline_A: "private A reasoning" },
  };
  state = lockPeerChoice(state, "P");
  assert.equal(state.phase, "baseline_handoff");
  state.phase = "baseline_B";
  const view = peerPrivateView(state);
  assert.deepEqual(view, {
    operator: "B",
    mechanism: "baseline",
    congestion: "Medium",
    ownType: "L",
    otherType: "Unknown",
    otherAction: "Hidden until both submit",
  });
  assert.equal("types" in view, false);
  assert.equal("baselineChoices" in view, false);
  assert.equal("reflections" in view, false);
});

test("new scenario reset clears reveal and auction state", () => {
  const original = newSoloState({ congestion: "Medium", ownType: "H", rivalType: "L" });
  original.phase = "complete";
  original.baselineAction = "P";
  original.ccarAction = "F";
  original.auction = { outcome: "old" };
  const reset = resetSoloState({ congestion: "Low", ownType: "L", rivalType: "H" });
  assert.equal(reset.phase, "baseline");
  assert.equal(reset.baselineAction, null);
  assert.equal(reset.ccarAction, null);
  assert.equal(reset.auction, null);
  assert.equal(reset.congestion, "Low");
});
