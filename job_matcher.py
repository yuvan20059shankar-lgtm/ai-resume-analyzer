"""
Job Matcher Module
Vectorizes resume text and job descriptions using TF-IDF and calculates cosine similarity
scores to rank job roles from highest to lowest match.
Also computes exact skill coverage and gap analysis for each role.
"""

import os
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def resolve_job_data_path(filename: str = "job_roles.csv") -> str:
    """Finds the job roles CSV in common relative directories."""
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


class JobMatcher:
    """
    Computes TF-IDF vectorization and cosine similarity between a candidate resume
    and known job profiles, combined with hard-skill coverage metrics.
    """

    def __init__(self, job_data_path: Optional[str] = None):
        self.job_data_path = job_data_path or resolve_job_data_path("job_roles.csv")
        self.job_df = self._load_job_data()
        self._prepare_corpus()

    def _load_job_data(self) -> pd.DataFrame:
        """Loads and prepares the job roles dataframe."""
        if not os.path.exists(self.job_data_path):
            raise FileNotFoundError(
                f"Job roles dataset not found at {self.job_data_path}. "
                "Ensure data/job_roles.csv exists."
            )
        df = pd.read_csv(self.job_data_path)
        required_cols = {"role", "required_skills", "description"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Job roles CSV must contain at least: {required_cols}")

        df["required_skills_list"] = df["required_skills"].apply(
            lambda s: [skill.strip() for skill in str(s).split(",") if skill.strip()]
        )
        if "optional_skills" in df.columns:
            df["optional_skills_list"] = df["optional_skills"].apply(
                lambda s: [skill.strip() for skill in str(s).split(",") if skill.strip()] if pd.notna(s) else []
            )
        else:
            df["optional_skills_list"] = [[] for _ in range(len(df))]

        return df

    def _prepare_corpus(self):
        """Prepares combined text representations for TF-IDF training."""
        self.corpus = []
        for _, row in self.job_df.iterrows():
            skills_txt = " ".join(row["required_skills_list"])
            opt_skills_txt = " ".join(row["optional_skills_list"])
            text = f"{row['role']} {row.get('category', '')} {skills_txt} {opt_skills_txt} {row['description']}"
            self.corpus.append(text)

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=5000,
        )
        self.job_tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def match_resume(
        self,
        resume_text: str,
        extracted_skills: List[str],
        target_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Matches resume text against all job roles.

        Args:
            resume_text: Cleaned or raw resume text.
            extracted_skills: List of technical skills extracted from resume.
            target_role: Optional role name to highlight.

        Returns:
            Dict containing rankings, scores, and target role analysis.
        """
        if not resume_text:
            return {
                "rankings": [],
                "target_role_match": None,
                "top_role": None,
            }

        # TF-IDF Cosine Similarity
        candidate_vector = self.vectorizer.transform([resume_text])
        cos_similarities = cosine_similarity(candidate_vector, self.job_tfidf_matrix)[0]

        extracted_set = {s.lower() for s in extracted_skills}

        results = []
        for idx, row in self.job_df.iterrows():
            role_name = row["role"]
            required_skills = row["required_skills_list"]
            optional_skills = row["optional_skills_list"]

            matched_req = [
                s for s in required_skills if s.lower() in extracted_set
            ]
            missing_req = [
                s for s in required_skills if s.lower() not in extracted_set
            ]
            matched_opt = [
                s for s in optional_skills if s.lower() in extracted_set
            ]

            req_coverage = (
                len(matched_req) / len(required_skills) if required_skills else 0.0
            )

            # Raw TF-IDF Cosine Score (0.0 to 1.0)
            raw_tfidf = float(cos_similarities[idx])

            # Composite Score: Balanced combination of TF-IDF semantic relevance & hard-skill overlap
            composite_score = (0.50 * req_coverage) + (0.50 * raw_tfidf)
            match_percentage = round(composite_score * 100, 1)
            tfidf_percentage = round(raw_tfidf * 100, 1)
            skill_percentage = round(req_coverage * 100, 1)

            result_item = {
                "role": role_name,
                "category": row.get("category", "General"),
                "experience_level": row.get("experience_level", "Mid-Level"),
                "summary": row.get("summary", ""),
                "description": row.get("description", ""),
                "match_percentage": match_percentage,
                "tfidf_score": round(raw_tfidf, 4),
                "tfidf_percentage": tfidf_percentage,
                "skill_coverage_percentage": skill_percentage,
                "required_skills": required_skills,
                "optional_skills": optional_skills,
                "matched_skills": matched_req,
                "missing_skills": missing_req,
                "matched_optional_skills": matched_opt,
                "total_required": len(required_skills),
                "total_matched": len(matched_req),
            }
            results.append(result_item)

        # Sort descending by match_percentage
        ranked_roles = sorted(results, key=lambda x: x["match_percentage"], reverse=True)

        target_analysis = None
        if target_role:
            target_match = next((r for r in ranked_roles if r["role"].lower() == target_role.lower()), None)
            if target_match:
                target_analysis = target_match

        return {
            "rankings": ranked_roles,
            "target_role_match": target_analysis,
            "top_role": ranked_roles[0] if ranked_roles else None,
            "df_rankings": pd.DataFrame(ranked_roles),
        }

    def get_all_roles(self) -> List[str]:
        """Returns list of all available job role names."""
        return self.job_df["role"].tolist()

    def get_role_details(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Returns metadata for a specific role."""
        match = self.job_df[self.job_df["role"].str.lower() == role_name.lower()]
        if match.empty:
            return None
        row = match.iloc[0]
        return {
            "role": row["role"],
            "category": row.get("category", ""),
            "required_skills": row["required_skills_list"],
            "optional_skills": row.get("optional_skills_list", []),
            "experience_level": row.get("experience_level", ""),
            "summary": row.get("summary", ""),
            "description": row.get("description", ""),
        }
