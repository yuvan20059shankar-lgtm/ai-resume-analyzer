"""
Skill Extractor Module
Scans cleaned text against a controlled skill dictionary to extract matched technical skills.
Groups extracted skills by category (programming, databases, ML, cloud, tools) and
computes occurrence statistics.
"""

import os
import re
from typing import Dict, List, Any, Optional
import pandas as pd


def resolve_data_path(filename: str = "skill_dictionary.csv") -> str:
    """
    Finds the skill dictionary CSV in common relative directories.
    """
    candidates = [
        os.path.join(os.path.dirname(__file__), "data", filename),
        os.path.join(os.path.dirname(__file__), "..", "data", filename),
        os.path.join(os.getcwd(), "data", filename),
        os.path.join(os.getcwd(), "ai resume analyzer", "data", filename),
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return os.path.abspath(candidates[0])


class SkillExtractor:
    """
    High-accuracy technical skill extractor utilizing controlled vocabulary
    and regex-based boundary matching.
    """

    def __init__(self, dict_path: Optional[str] = None):
        self.dict_path = dict_path or resolve_data_path("skill_dictionary.csv")
        self.skill_df = self._load_dictionary()
        self._compiled_patterns = self._build_patterns()

    def _load_dictionary(self) -> pd.DataFrame:
        """Loads and validates the skill dictionary CSV."""
        if not os.path.exists(self.dict_path):
            raise FileNotFoundError(
                f"Skill dictionary not found at {self.dict_path}. "
                "Ensure data/skill_dictionary.csv exists."
            )
        df = pd.read_csv(self.dict_path)
        required_cols = {"skill", "category"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Skill dictionary must contain columns: {required_cols}")
        if "aliases" not in df.columns:
            df["aliases"] = ""
        df["aliases"] = df["aliases"].fillna("")
        if "description" not in df.columns:
            df["description"] = ""
        df["description"] = df["description"].fillna("")
        return df

    def _build_patterns(self) -> List[Dict[str, Any]]:
        """
        Builds compiled regex patterns for each canonical skill and its aliases.
        Handles edge cases for C++, C#, .NET, and single-letter languages (R, C).
        """
        patterns = []
        for _, row in self.skill_df.iterrows():
            canonical = row["skill"].strip()
            category = str(row["category"]).strip().lower()
            aliases_str = str(row["aliases"]).strip()
            description = str(row.get("description", "")).strip()

            terms = [canonical.lower()]
            if aliases_str:
                aliases = [a.strip().lower() for a in aliases_str.split("|") if a.strip()]
                terms.extend(aliases)

            # Deduplicate while preserving order
            seen = set()
            clean_terms = []
            for t in terms:
                if t not in seen:
                    seen.add(t)
                    clean_terms.append(t)

            # Compile regex for terms
            compiled_regexes = []
            for t in clean_terms:
                # Handle special technical symbols like C++, C#, .NET
                if t in ["c++", "cpp"]:
                    # Match c++ with whitespace or punctuation boundary
                    regex = re.compile(r"(?:^|[\s,;/()\[\]])c\+\+(?:$|[\s,;/()\[\]])", re.IGNORECASE)
                elif t in ["c#", "csharp"]:
                    regex = re.compile(r"(?:^|[\s,;/()\[\]])c\#(?:$|[\s,;/()\[\]])", re.IGNORECASE)
                elif t in [".net", "dotnet"]:
                    regex = re.compile(r"(?:^|[\s,;/()\[\]])\.net(?:$|[\s,;/()\[\]])", re.IGNORECASE)
                elif t in ["r", "c", "go"]:
                    # Strict word boundary for single-character or short words
                    regex = re.compile(rf"(?<![a-zA-Z0-9_]){re.escape(t)}(?![a-zA-Z0-9_])", re.IGNORECASE)
                else:
                    escaped = re.escape(t)
                    regex = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
                compiled_regexes.append(regex)

            patterns.append({
                "skill": canonical,
                "category": category,
                "description": description,
                "regexes": compiled_regexes,
            })
        return patterns

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Scans cleaned text and extracts matched skills, categories, and frequencies.

        Args:
            text: Cleaned text string.

        Returns:
            Dict containing:
              - matched_skills: List of canonical skill names found
              - skills_by_category: Dict[category, List[skill_names]]
              - skill_counts: Dict[canonical_skill, count]
              - skill_details: List of dicts with skill, category, count, description
              - total_found: int
              - category_counts: Dict[category, int]
        """
        if not text or not isinstance(text, str):
            return {
                "matched_skills": [],
                "skills_by_category": {},
                "skill_counts": {},
                "skill_details": [],
                "total_found": 0,
                "category_counts": {},
            }

        matched_skills = []
        skill_counts = {}
        skill_details = []
        skills_by_category: Dict[str, List[str]] = {
            "programming": [],
            "databases": [],
            "ml": [],
            "cloud": [],
            "tools": [],
        }

        # Check each skill pattern against text
        for item in self._compiled_patterns:
            canonical = item["skill"]
            category = item["category"]
            description = item["description"]
            total_hits = 0

            for rgx in item["regexes"]:
                hits = len(rgx.findall(text))
                total_hits += hits

            if total_hits > 0:
                matched_skills.append(canonical)
                skill_counts[canonical] = total_hits
                skill_details.append({
                    "skill": canonical,
                    "category": category,
                    "count": total_hits,
                    "description": description,
                })
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(canonical)

        category_counts = {
            cat: len(skills) for cat, skills in skills_by_category.items()
        }

        return {
            "matched_skills": matched_skills,
            "skills_by_category": skills_by_category,
            "skill_counts": skill_counts,
            "skill_details": skill_details,
            "total_found": len(matched_skills),
            "category_counts": category_counts,
        }


# Module level convenience function
_GLOBAL_EXTRACTOR: Optional[SkillExtractor] = None


def extract_skills_from_text(text: str, dict_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience wrapper for extracting skills without managing the class lifecycle."""
    global _GLOBAL_EXTRACTOR
    if _GLOBAL_EXTRACTOR is None or dict_path is not None:
        _GLOBAL_EXTRACTOR = SkillExtractor(dict_path=dict_path)
    return _GLOBAL_EXTRACTOR.extract_skills(text)
