const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const { MODULE_FILES, CONTENT_DIR, loadAllIntents } = require("../logic/contentStore");

const EXPECTED_MODULES = {
  "water_safety.json": 20,
  "handwashing.json": 5,
  "sanitation.json": 7,
  "disease_prevention.json": 7,
};

const ALLOWED_TOPICS = new Set([
  "Water Safety",
  "Handwashing",
  "Sanitation",
  "Disease Prevention",
]);

function assertLocalizedString(value, fieldName) {
  assert.equal(typeof value, "object", `${fieldName} must be an object`);
  assert.equal(typeof value.en, "string", `${fieldName}.en must be a string`);
  assert.equal(typeof value.shona, "string", `${fieldName}.shona must be a string`);
  assert.ok(value.en.trim().length > 0, `${fieldName}.en must not be empty`);
  assert.ok(value.shona.trim().length > 0, `${fieldName}.shona must not be empty`);
}

function assertLocalizedArray(value, fieldName) {
  assert.equal(typeof value, "object", `${fieldName} must be an object`);
  assert.ok(Array.isArray(value.en), `${fieldName}.en must be an array`);
  assert.ok(Array.isArray(value.shona), `${fieldName}.shona must be an array`);
  assert.ok(value.en.length >= 3, `${fieldName}.en must have at least 3 items`);
  assert.ok(value.shona.length >= 3, `${fieldName}.shona must have at least 3 items`);
  value.en.forEach((item, index) => {
    assert.equal(typeof item, "string", `${fieldName}.en[${index}] must be a string`);
    assert.ok(item.trim().length > 0, `${fieldName}.en[${index}] must not be empty`);
  });
  value.shona.forEach((item, index) => {
    assert.equal(typeof item, "string", `${fieldName}.shona[${index}] must be a string`);
    assert.ok(item.trim().length > 0, `${fieldName}.shona[${index}] must not be empty`);
  });
}

test("all required module files exist and contain arrays", () => {
  for (const filename of MODULE_FILES) {
    const filePath = path.join(CONTENT_DIR, filename);
    assert.ok(fs.existsSync(filePath), `${filename} should exist`);
    const payload = JSON.parse(fs.readFileSync(filePath, "utf8"));
    assert.ok(Array.isArray(payload), `${filename} should contain a top-level array`);
    assert.equal(payload.length, EXPECTED_MODULES[filename], `${filename} should contain the expected number of intents`);
  }
});

test("all intents follow the expected schema and bilingual requirements", () => {
  const allIntents = loadAllIntents();
  const ids = new Set();

  for (const intent of allIntents) {
    assert.equal(typeof intent.intent_id, "string", "intent_id must be a string");
    assert.ok(intent.intent_id.length > 0, "intent_id must not be empty");
    assert.ok(!ids.has(intent.intent_id), `duplicate intent_id: ${intent.intent_id}`);
    ids.add(intent.intent_id);

    assert.ok(ALLOWED_TOPICS.has(intent.topic), `${intent.intent_id} has an invalid topic`);
    assertLocalizedString(intent.canonical_question, `${intent.intent_id}.canonical_question`);
    assertLocalizedArray(intent.sample_variations, `${intent.intent_id}.sample_variations`);
    assertLocalizedString(intent.answer_short, `${intent.intent_id}.answer_short`);

    if (intent.answer_steps !== null) {
      assert.equal(typeof intent.answer_steps, "object", `${intent.intent_id}.answer_steps must be an object or null`);
      assert.ok(Array.isArray(intent.answer_steps.en), `${intent.intent_id}.answer_steps.en must be an array`);
      assert.ok(Array.isArray(intent.answer_steps.shona), `${intent.intent_id}.answer_steps.shona must be an array`);
      assert.ok(intent.answer_steps.en.length > 0, `${intent.intent_id}.answer_steps.en must not be empty`);
      assert.ok(intent.answer_steps.shona.length > 0, `${intent.intent_id}.answer_steps.shona must not be empty`);
    }

    if (intent.answer_warning !== null) {
      assertLocalizedString(intent.answer_warning, `${intent.intent_id}.answer_warning`);
    }

    if (intent.follow_up_question !== null) {
      assertLocalizedString(intent.follow_up_question, `${intent.intent_id}.follow_up_question`);
    }

    assert.ok(Array.isArray(intent.tags), `${intent.intent_id}.tags must be an array`);
    assert.ok(intent.tags.length >= 4, `${intent.intent_id}.tags should contain broad matching keywords`);
    for (const tag of intent.tags) {
      assert.equal(typeof tag, "string", `${intent.intent_id}.tags entries must be strings`);
      assert.ok(tag.trim().length > 0, `${intent.intent_id}.tags entries must not be empty`);
    }
  }
});
