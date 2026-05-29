"""Create English-only copy of 50091136.ipynb (strip Chinese markdown)."""
import json
import re
from copy import deepcopy

SRC = "50091136.ipynb"
DST = "50091136_en.ipynb"

CJK_PATTERN = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")


def cjk_count(text: str) -> int:
    return len(CJK_PATTERN.findall(text))


def latin_word_count(text: str) -> int:
    return len(re.findall(r"[a-zA-Z]{2,}", text))


def has_english_heading(text: str) -> bool:
    return bool(re.search(r"^#{1,6}\s+.*[a-zA-Z]{3,}", text, re.MULTILINE))


def is_chinese_leading(text: str) -> bool:
    t = text.strip()
    m_cjk = re.search(r"[\u4e00-\u9fff]", t)
    m_eng = re.search(r"[a-zA-Z]{3,}", t)
    if not m_cjk:
        return False
    return m_eng is None or m_cjk.start() < m_eng.start()


def chinese_ratio(text: str) -> float:
    cjk = cjk_count(text)
    lat = len(re.findall(r"[a-zA-Z]", text))
    return cjk / (cjk + lat + 1)


def is_chinese_only_markdown(text: str) -> bool:
    """Standalone Chinese companion cells (duplicate sections or intro blurbs)."""
    t = text.strip()
    if not t:
        return False
    cjk = cjk_count(t)
    if cjk == 0:
        return False

    if re.match(r"^#{1,6}\s*[\u4e00-\u9fff]", t):
        return True

    if re.search(r"\|\s*列名\s*\|", t) or re.search(r"\|\s*缺失\s*\(", t):
        return True
    if re.search(r"\|\s*剔除理由\s*\|", t):
        return True

    if is_chinese_leading(t) and not has_english_heading(t):
        return True

    words = latin_word_count(t)
    if cjk >= 20 and words < 12:
        return True
    if cjk >= 30 and chinese_ratio(t) > 0.28 and not has_english_heading(t):
        return True

    return False


def remove_cjk_chars(text: str) -> str:
    """Final pass: strip CJK and fullwidth punctuation from English markdown."""
    lines_out: list[str] = []
    for line in text.splitlines():
        if not CJK_PATTERN.search(line):
            lines_out.append(line.rstrip())
            continue

        cleaned = CJK_PATTERN.sub("", line)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        if len(re.findall(r"[a-zA-Z]", cleaned)) < 25:
            continue
        if "****" in cleaned:
            continue
        words = re.findall(r"[a-zA-Z]{3,}", cleaned)
        if len(words) < 8 and not cleaned.endswith("."):
            continue
        lines_out.append(cleaned.rstrip())

    text = "\n".join(lines_out)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = []
    for line in text.splitlines():
        if re.sub(r"[\s\W_]", "", line):
            lines.append(line.rstrip())
        elif not line.strip():
            lines.append("")
    text = "\n".join(lines).strip()
    return text


def strip_chinese_lines(text: str) -> str:
    """Remove Chinese lines/paragraphs from bilingual markdown cells."""
    paragraphs = re.split(r"\n\n+", text)
    kept_paras: list[str] = []

    for para in paragraphs:
        cjk = cjk_count(para)
        lat = len(re.findall(r"[a-zA-Z]", para))
        if cjk >= 6 and lat < max(cjk * 0.55, 12):
            continue

        lines = para.splitlines()
        kept_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                kept_lines.append(line)
                continue

            cjk_l = cjk_count(line)
            lat_l = len(re.findall(r"[a-zA-Z]", line))

            if re.match(r"^#{1,6}\s*[\u4e00-\u9fff]", stripped):
                continue
            if cjk_l >= 2 and lat_l < max(cjk_l * 0.55, 6):
                continue

            kept_lines.append(line)

        cleaned = "\n".join(kept_lines).strip()
        if cleaned:
            kept_paras.append(cleaned)

    merged = "\n\n".join(kept_paras)
    return remove_cjk_chars(merged)


def main() -> None:
    with open(SRC, encoding="utf-8") as f:
        nb = json.load(f)

    out_cells = []
    removed = 0
    stripped = 0

    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            out_cells.append(cell)
            continue

        text = "".join(cell.get("source", []))
        if is_chinese_only_markdown(text):
            removed += 1
            continue

        new_text = strip_chinese_lines(text)
        if cjk_count(new_text) > 0:
            if is_chinese_leading(new_text) and not has_english_heading(new_text):
                removed += 1
                continue
            if cjk_count(new_text) >= 8 and chinese_ratio(new_text) > 0.22:
                removed += 1
                continue

        if new_text != text:
            stripped += 1

        if not new_text.strip():
            removed += 1
            continue

        new_cell = deepcopy(cell)
        new_cell["source"] = [new_text] if not new_text.endswith("\n") else [new_text]
        out_cells.append(new_cell)

    nb_out = deepcopy(nb)
    nb_out["cells"] = out_cells

    with open(DST, "w", encoding="utf-8") as f:
        json.dump(nb_out, f, ensure_ascii=False, indent=1)

    # Validation
    remaining_cjk = 0
    for cell in out_cells:
        if cell["cell_type"] == "markdown":
            remaining_cjk += cjk_count("".join(cell.get("source", [])))

    print(f"Wrote {DST}")
    print(f"Cells: {len(nb['cells'])} -> {len(out_cells)} (removed {removed} markdown)")
    print(f"Stripped Chinese from {stripped} mixed markdown cells")
    print(f"Remaining CJK in markdown: {remaining_cjk}")


if __name__ == "__main__":
    main()
