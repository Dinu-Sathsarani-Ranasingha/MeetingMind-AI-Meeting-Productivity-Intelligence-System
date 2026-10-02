"""
MeetingMind AI - Action Item Extractor
=======================================
Extracts action items, owners, and deadlines from raw meeting notes.
Uses rule-based NLP with NLTK + regex patterns.
"""

import re
import nltk
from datetime import datetime

# ── Download required NLTK data (silent) ────────────────────────────────────
for pkg in ["punkt", "punkt_tab", "stopwords", "averaged_perceptron_tagger"]:
    nltk.download(pkg, quiet=True)


# ── Action Trigger Patterns ──────────────────────────────────────────────────
# These are phrases that signal an action item in meeting notes

ACTION_TRIGGERS = [
    # Assignment patterns
    r"\b(will|shall|must|should|needs? to|has to|have to)\b",
    r"\b(assigned to|assign to|action for|action item|todo|to.do)\b",
    r"\b(please|kindly)\s+\w+",
    r"\b(follow up|follow-up|followup)\b",
    r"\b(responsible for|in charge of|owns?)\b",
    r"\b(going to|planning to|intends? to)\b",
    r"\b(agreed to|committed to|promised to)\b",
    r"\b(take care of|handle|deal with|look into|check on)\b",
    r"\b(prepare|create|build|develop|write|send|share|update|review|fix|test|deploy)\b",
    r"\b(schedule|arrange|coordinate|organise|organize)\b",
]

ACTION_PATTERN = re.compile("|".join(ACTION_TRIGGERS), re.IGNORECASE)

# ── Deadline Patterns ────────────────────────────────────────────────────────
DEADLINE_PATTERNS = [
    r"\b(by|before|due|until|no later than)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\b(by|before|due|until)\s+(\d{1,2}[\/\-]\d{1,2}([\/\-]\d{2,4})?)\b",
    r"\b(by|before|due)\s+(end of (day|week|month|sprint|quarter))\b",
    r"\b(this|next)\s+(week|monday|tuesday|wednesday|thursday|friday|month|sprint)\b",
    r"\b(tomorrow|today|tonight|asap|immediately|urgent)\b",
    r"\b(q[1-4]|q[1-4]\s*\d{4})\b",
    r"\b(\d{1,2}(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)\b",
    r"\b(in\s+\d+\s+(days?|weeks?|hours?))\b",
]

DEADLINE_PATTERN = re.compile("|".join(DEADLINE_PATTERNS), re.IGNORECASE)

# ── Owner Patterns ───────────────────────────────────────────────────────────
# Detect names assigned as owners in meeting text

OWNER_PREFIXES = [
    r"(?:assigned to|action for|owner[:\s]+|responsible[:\s]+|@)\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",
    r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+(?:will|shall|must|should|needs? to|has to|is going to|agreed to)",
    r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*:\s*(?:will|to|please)",
]

OWNER_PATTERN = re.compile("|".join(OWNER_PREFIXES))

# ── Common words that look like names but aren't ────────────────────────────
NOT_NAMES = {
    "The", "This", "That", "These", "Those", "We", "They", "He", "She", "It",
    "Team", "Everyone", "All", "Please", "Management", "Engineering", "Product",
    "Design", "Marketing", "Finance", "Leadership", "Backend", "Frontend",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "June", "July", "August",
    "September", "October", "November", "December", "Next", "This", "Last",
}


def clean_sentence(text: str) -> str:
    """Remove extra whitespace and normalize text."""
    return re.sub(r"\s+", " ", text.strip())


def extract_owner(sentence: str) -> str | None:
    """Extract the person responsible for an action item."""
    for pattern in OWNER_PREFIXES:
        match = re.search(pattern, sentence)
        if match:
            # Get the first non-None group
            name = next((g for g in match.groups() if g), None)
            if name and name.strip() not in NOT_NAMES and len(name.strip()) > 1:
                return name.strip()
    return None


def extract_deadline(sentence: str) -> str | None:
    """Extract any deadline or due date from the sentence."""
    match = DEADLINE_PATTERN.search(sentence)
    if match:
        return clean_sentence(match.group(0))
    return None


def is_action_item(sentence: str) -> bool:
    """Return True if the sentence contains an action item signal."""
    return bool(ACTION_PATTERN.search(sentence))


def extract_action_items(meeting_text: str) -> list[dict]:
    """
    Main function: extract all action items from raw meeting notes.

    Returns a list of dicts:
        {
            "task":     str   — the full action item sentence,
            "owner":    str | None — person responsible,
            "deadline": str | None — due date/time,
            "priority": str   — "High" | "Medium" | "Low"
        }
    """
    # Split into sentences
    try:
        sentences = nltk.sent_tokenize(meeting_text)
    except Exception:
        # Fallback: split on punctuation
        sentences = re.split(r"[.!?\n]+", meeting_text)

    action_items = []
    seen = set()

    for sentence in sentences:
        sentence = clean_sentence(sentence)
        if len(sentence) < 10:
            continue

        if is_action_item(sentence):
            # Deduplicate similar sentences
            key = sentence.lower()[:60]
            if key in seen:
                continue
            seen.add(key)

            owner = extract_owner(sentence)
            deadline = extract_deadline(sentence)
            priority = _classify_priority(sentence, deadline)

            action_items.append({
                "task": sentence,
                "owner": owner,
                "deadline": deadline,
                "priority": priority,
            })

    return action_items


def _classify_priority(sentence: str, deadline: str | None) -> str:
    """Classify action item priority based on urgency signals."""
    urgent_words = r"\b(urgent|asap|immediately|critical|blocker|block|today|tonight|emergency)\b"
    low_words = r"\b(eventually|sometime|when possible|nice to have|optional|consider)\b"

    if re.search(urgent_words, sentence, re.IGNORECASE):
        return "High"
    if deadline and re.search(r"\b(today|tonight|asap|tomorrow)\b", deadline, re.IGNORECASE):
        return "High"
    if re.search(low_words, sentence, re.IGNORECASE):
        return "Low"
    return "Medium"
