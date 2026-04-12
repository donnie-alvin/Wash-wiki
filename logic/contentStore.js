const fs = require("node:fs");
const path = require("node:path");

const CONTENT_DIR = path.join(__dirname, "..", "content");
const MODULE_FILES = [
  "water_safety.json",
  "handwashing.json",
  "sanitation.json",
  "disease_prevention.json",
];

function loadModule(filename) {
  const filePath = path.join(CONTENT_DIR, filename);
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function loadAllIntents() {
  return MODULE_FILES.flatMap(loadModule);
}

module.exports = {
  CONTENT_DIR,
  MODULE_FILES,
  loadModule,
  loadAllIntents,
};
