import re
from typing import Any, List, Optional, Dict

def _as_str(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""

def _as_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def _split_skill_text(text: str) -> List[str]:
    if not text:
        return []

    # Handle categorized skills like "Programming: Python, C++ | ML: TensorFlow, Torch"
    # Split by major separators first
    raw_chunks = re.split(r"[\n;|•]+", text)
    tokens: List[str] = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        # Handle colons aggressively: "Programming: Python" -> ["Programming", "Python"]
        # If multiple colons, split them all out
        if ":" in chunk:
            subparts = [p.strip() for p in re.split(r":", chunk) if p.strip()]
            # Process each subpart as if it was a chunk
            for subpart in subparts:
                # Further split by comma
                for piece in re.split(r",", subpart):
                    p = piece.strip(" .-\t\n")
                    if not p:
                        continue
                    # Remove common level-indicators
                    p = re.sub(r"\s*[(\[]?\b(beginner|intermediate|advanced|expert|proficient|expertly)\b[)\]]?\s*", "", p, flags=re.IGNORECASE).strip()
                    # Clean up hanging parentheses/brackets
                    p = p.replace("()", "").replace("[]", "").strip(" .-\t\n")
                    # Clean up multiple spaces
                    p = re.sub(r"\s+", " ", p)
                    if p and len(p) > 1:
                        tokens.append(p)
            continue

        # Regular chunk (no colon) - split by comma
        for piece in re.split(r",", chunk):
            p = piece.strip(" .-\t\n")
            if not p:
                continue
            p = re.sub(r"\s*[(\[]?\b(beginner|intermediate|advanced|expert|proficient|expertly)\b[)\]]?\s*", "", p, flags=re.IGNORECASE).strip()
            p = p.replace("()", "").replace("[]", "").strip(" .-\t\n")
            p = re.sub(r"\s+", " ", p)
            if p and len(p) > 1:
                tokens.append(p)

    # Deduplicate
    deduped: List[str] = []
    seen: set[str] = set()
    for token in tokens:
        key = token.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(token)

    return deduped

# Test cases for skills
skill_tests = [
    "Programming: Python, C++",
    "Systems & Signal Processing: RF signal processing, Doppler estimation, embedded Linux",
    "Scientific & Research Tools: NumPy, SciPy, OpenCV, Qiskit, PyTorch, TensorFlow",
    "Operating Systems: Linux (Ubuntu)",
    "Deep learning, model training and evaluation",
    "Python (expert), C++ (intermediate)",
    "Natural Language Processing; Computer Vision | Robotics"
]

print("--- Skill Parsing Tests ---")
for test in skill_tests:
    result = _split_skill_text(test)
    print(f"Input: {test}")
    print(f"Result: {result}")
    print()

# Test cases for education grades
print("--- Education Grade Normalization Tests ---")

def mock_normalize_edu(gpa_val):
    # Simplified logic from onboarding.py
    gpa = _as_float(gpa_val) if re.match(r"^[0-9.]+$", str(gpa_val or "")) else None
    desc = f"Grade: {gpa_val}" if not re.match(r"^[0-9.]+$", str(gpa_val or "")) and gpa_val else ""
    return gpa, desc

edu_tests = [
    "9.352",
    "O",
    "A+",
    "3.8/4.0",
    "95%"
]

for test in edu_tests:
    gpa, desc = mock_normalize_edu(test)
    print(f"Input: {test} -> GPA: {gpa}, Desc update: {desc}")
