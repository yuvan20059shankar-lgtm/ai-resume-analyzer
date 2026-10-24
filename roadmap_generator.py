"""
Roadmap Generator Module
Compares candidate skills against target job requirements, identifies the skill gap,
and dynamically generates an actionable 4-week learning roadmap.
"""

from typing import Dict, List, Any, Optional

# Curated learning resources and task suggestions for common technical skills
SKILL_KNOWLEDGE_BASE = {
    "python": {
        "topics": "Data structures, OOP, list comprehensions, decorators, generators, virtual environments",
        "action": "Build a modular CLI tool or data pipeline applying clean code principles.",
        "resources": "Official Python Docs (docs.python.org), Real Python tutorials.",
    },
    "sql": {
        "topics": "Complex JOINs, Window Functions (ROW_NUMBER, RANK, LEAD, LAG), CTEs, Indexing, Query Optimization",
        "action": "Solve 15 LeetCode Medium SQL problems and analyze schema execution plans.",
        "resources": "Mode Analytics SQL Tutorial, PostgreSQL Documentation.",
    },
    "pandas": {
        "topics": "DataFrame manipulation, groupby aggregations, merging, handling missing values, time-series",
        "action": "Perform exploratory data analysis (EDA) on a 500k-row Kaggle dataset.",
        "resources": "Pandas official user guide, Kaggle Pandas micro-course.",
    },
    "numpy": {
        "topics": "Vectorization, broadcasting, matrix multiplication, array indexing and slicing",
        "action": "Implement gradient descent and matrix transformations from scratch without loops.",
        "resources": "NumPy Quickstart guide, Stanford CS231n Python/NumPy tutorial.",
    },
    "scikit-learn": {
        "topics": "Pipelines, ColumnTransformer, Cross-validation, Hyperparameter tuning (GridSearch/RandomizedSearch)",
        "action": "Train, evaluate, and serialize a classification pipeline with ROC-AUC analysis.",
        "resources": "Scikit-Learn documentation & user guide.",
    },
    "pytorch": {
        "topics": "Tensors, autograd, custom Dataset/DataLoader, nn.Module, training loops, GPU acceleration",
        "action": "Build and train a convolutional or transformer model with custom loss functions.",
        "resources": "PyTorch 60-Minute Blitz, Deep Learning with PyTorch Book.",
    },
    "tensorflow": {
        "topics": "Keras Sequential & Functional APIs, tf.data pipelines, Callbacks, TensorBoard",
        "action": "Implement transfer learning using a pre-trained ResNet or MobileNet.",
        "resources": "TensorFlow Core tutorials (tensorflow.org/tutorials).",
    },
    "power bi": {
        "topics": "Data modeling, Star Schema, DAX measures (CALCULATE, FILTER, RELATED), Interactive visuals",
        "action": "Create an executive KPI dashboard with drill-down and dynamic cross-filtering.",
        "resources": "Microsoft Learn Power BI learning path, Enterprise DNA.",
    },
    "tableau": {
        "topics": "Calculated fields, Level of Detail (LOD) expressions, parameters, dashboard actions",
        "action": "Build a Tableau Public portfolio dashboard with storytelling elements.",
        "resources": "Tableau Free Training Videos, Workout Wednesday challenges.",
    },
    "docker": {
        "topics": "Dockerfile creation, multi-stage builds, docker-compose, volume mounting, port mapping",
        "action": "Containerize a full-stack Streamlit/FastAPI model inference service.",
        "resources": "Docker getting-started documentation, Docker for Data Science guides.",
    },
    "kubernetes": {
        "topics": "Pods, Deployments, Services, ConfigMaps, Ingress, HPA (Horizontal Pod Autoscaling)",
        "action": "Deploy a containerized ML app to a local Minikube cluster with health checks.",
        "resources": "Kubernetes.io interactive tutorials, Mumshad Mannambeth CKA materials.",
    },
    "llms": {
        "topics": "Prompt engineering, tokenization, temperature/top-p, RAG architectures, model quantization",
        "action": "Build an interactive document Q&A assistant using an open-source LLM or API.",
        "resources": "DeepLearning.AI Short Courses on LLMs, Hugging Face LLM Course.",
    },
    "langchain": {
        "topics": "Chains, PromptTemplates, Document Loaders, Text Splitters, VectorStores, Retrieval QA, Agents",
        "action": "Develop a multi-source RAG chatbot with source citation and chat history memory.",
        "resources": "LangChain Python Documentation, Harrison Chase LangChain tutorials.",
    },
    "hugging face": {
        "topics": "Hugging Face Hub, Transformers pipeline, AutoModel, AutoTokenizer, Datasets, PEFT/LoRA",
        "action": "Fine-tune a lightweight BERT or DistilBERT model for multi-class text classification.",
        "resources": "Hugging Face NLP Course (huggingface.co/learn/nlp-course).",
    },
    "opencv": {
        "topics": "Image transformations, contour detection, morphological operations, Haar cascades, video stream processing",
        "action": "Build a real-time web-cam object detector or facial feature tracker.",
        "resources": "OpenCV-Python tutorials (docs.opencv.org), PyImageSearch.",
    },
    "computer vision": {
        "topics": "CNNs, YOLOv8 object detection, semantic segmentation (Mask R-CNN), data augmentation",
        "action": "Train a custom YOLOv8 model on custom labeled bounding boxes using Roboflow.",
        "resources": "Ultralytics YOLO Docs, Stanford CS231n Computer Vision course.",
    },
    "nlp": {
        "topics": "TF-IDF, Word2Vec, GloVe, self-attention mechanisms, Transformer encoders, NER, Sentiment Analysis",
        "action": "Build an end-to-end resume or article summarization engine with BLEU/ROUGE metrics.",
        "resources": "Jurafsky & Martin Speech and Language Processing, Stanford CS224N.",
    },
    "aws": {
        "topics": "S3, EC2, IAM roles & policies, Lambda, ECS, SageMaker endpoints and model registry",
        "action": "Deploy an inference API on AWS Lambda or SageMaker behind an API Gateway.",
        "resources": "AWS Skill Builder, Stephane Maarek AWS Certified Solutions Architect courses.",
    },
    "git": {
        "topics": "Branching strategies (GitFlow), rebasing vs merging, cherry-pick, conflict resolution, GitHub Actions",
        "action": "Configure a GitHub Action workflow to lint code and run pytest on every pull request.",
        "resources": "Pro Git Book (git-scm.com/book), GitHub Skills tutorials.",
    },
    "mlflow": {
        "topics": "Tracking experiments, logging parameters & metrics, Model Registry, artifact storage",
        "action": "Instrument a model training script with MLflow tracking and register the best artifact.",
        "resources": "MLflow official documentation (mlflow.org/docs).",
    },
}

DEFAULT_TOPIC = {
    "topics": "Core syntax, architecture principles, standard libraries, hands-on tutorials",
    "action": "Complete a focused mini-project building an end-to-end prototype on GitHub.",
    "resources": "Official documentation and top-rated GitHub community awesome-lists.",
}


def generate_learning_roadmap(
    target_role: str,
    extracted_skills: List[str],
    required_skills: List[str],
    optional_skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generates a targeted 4-week learning roadmap based on identified skill gaps.

    Args:
        target_role: Name of target career path.
        extracted_skills: List of skills extracted from candidate resume.
        required_skills: Required skills for target role.
        optional_skills: Optional bonus skills for target role.

    Returns:
        Dict with keys:
          - target_role
          - total_required
          - matched_skills
          - missing_skills
          - match_rate_pct
          - weeks: List of 4 week plan objects
          - summary
    """
    extracted_lower = {s.lower() for s in extracted_skills}
    matched = [s for s in required_skills if s.lower() in extracted_lower]
    missing = [s for s in required_skills if s.lower() not in extracted_lower]

    match_rate = round((len(matched) / len(required_skills)) * 100, 1) if required_skills else 100.0

    # Distribute missing skills across 4 weeks
    weeks = []
    
    if missing:
        # Partition missing skills into up to 3 study chunks (leaving week 4 for integration & capstone)
        chunks: List[List[str]] = [[], [], []]
        for idx, skill in enumerate(missing):
            chunks[idx % 3].append(skill)

        # Week 1: Foundations & Core Deficits
        w1_skills = chunks[0] if chunks[0] else missing[:1]
        weeks.append({
            "week_number": 1,
            "theme": "Foundations & Core Prerequisites",
            "target_skills": w1_skills,
            "focus_areas": [
                f"{s}: {_get_info(s)['topics']}" for s in w1_skills
            ],
            "action_items": [
                _get_info(s)["action"] for s in w1_skills
            ],
            "recommended_resources": [
                f"{s}: {_get_info(s)['resources']}" for s in w1_skills
            ],
            "milestone": f"Demonstrate working knowledge of {', '.join(w1_skills)} through unit-tested code exercises.",
        })

        # Week 2: Intermediate Frameworks & Applied Workflows
        w2_skills = chunks[1] if chunks[1] else (missing[1:2] if len(missing) > 1 else w1_skills)
        weeks.append({
            "week_number": 2,
            "theme": "Deep Dive & Applied Domain Tooling",
            "target_skills": w2_skills,
            "focus_areas": [
                f"{s}: {_get_info(s)['topics']}" for s in w2_skills
            ],
            "action_items": [
                _get_info(s)["action"] for s in w2_skills
            ],
            "recommended_resources": [
                f"{s}: {_get_info(s)['resources']}" for s in w2_skills
            ],
            "milestone": f"Construct an integrated pipeline combining {', '.join(w2_skills)} with your existing skill set.",
        })

        # Week 3: Advanced Concepts & System Integration
        w3_skills = chunks[2] if chunks[2] else (missing[2:3] if len(missing) > 2 else w2_skills)
        weeks.append({
            "week_number": 3,
            "theme": "Advanced Systems & Production Readiness",
            "target_skills": w3_skills,
            "focus_areas": [
                f"{s}: {_get_info(s)['topics']}" for s in w3_skills
            ],
            "action_items": [
                _get_info(s)["action"] for s in w3_skills
            ],
            "recommended_resources": [
                f"{s}: {_get_info(s)['resources']}" for s in w3_skills
            ],
            "milestone": f"Benchmark and containerize your implementations of {', '.join(w3_skills)}.",
        })

        # Week 4: Capstone Project, Portfolio & Interview Readiness
        weeks.append({
            "week_number": 4,
            "theme": "End-to-End Capstone Project & Career Launch",
            "target_skills": missing,
            "focus_areas": [
                f"Full-stack integration for {target_role}",
                "System architecture design and README documentation",
                "Technical interview questions and STAR-format behavioral pitch",
            ],
            "action_items": [
                f"Build a showcase portfolio project addressing {target_role} responsibilities incorporating {', '.join(missing[:3])}.",
                "Publish a clean GitHub repository with architectural diagrams, automated tests, and live demo link.",
                "Conduct 2 technical mock interviews focusing on data structures, algorithms, and domain design.",
            ],
            "recommended_resources": [
                "GitHub Readme Templates (github.com/othneildrew/Best-README-Template)",
                "System Design Primer (github.com/donnemartin/system-design-primer)",
                f"Top {target_role} interview questions and technical walkthroughs",
            ],
            "milestone": f"Live deployable project proving readiness for {target_role} job interviews.",
        })

    else:
        # Full coverage: Generate Advanced Mastery Roadmap
        weeks = [
            {
                "week_number": 1,
                "theme": "High-Performance System Architecture & Profiling",
                "target_skills": required_skills[:3],
                "focus_areas": [
                    "Memory management, latency optimization, and async execution",
                    "Benchmarking inference times and database query execution plans",
                ],
                "action_items": [
                    "Profile an existing project using cProfile or PyTorch profiler to eliminate compute bottlenecks.",
                ],
                "recommended_resources": [
                    "High Performance Python (O'Reilly)",
                    "Clean Code & Architectural Design Patterns in Python",
                ],
                "milestone": "Demonstrate 2x latency reduction on a core pipeline.",
            },
            {
                "week_number": 2,
                "theme": "Cloud Infrastructure, MLOps & Orchestration",
                "target_skills": ["Docker", "Kubernetes", "AWS"] if "Docker" not in required_skills else required_skills[2:5],
                "focus_areas": [
                    "Containerization, automated CI/CD pipelines, and health checks",
                    "Automated model registry and experiment tracking",
                ],
                "action_items": [
                    "Deploy an automated GitHub Actions CI/CD pipeline with unit testing and Docker container publishing.",
                ],
                "recommended_resources": [
                    "Production Ready Machine Learning Guides",
                    "Full Stack Deep Learning Course (fullstackdeeplearning.com)",
                ],
                "milestone": "Zero-downtime automated deployment pipeline.",
            },
            {
                "week_number": 3,
                "theme": "Scalable Capstone Production Showcase",
                "target_skills": required_skills,
                "focus_areas": [
                    f"Architecting an enterprise-grade solution tailored to {target_role}",
                    "Writing comprehensive architectural documentation and user manuals",
                ],
                "action_items": [
                    "Build and publicly deploy a flagship application with interactive UI and authenticated API endpoints.",
                ],
                "recommended_resources": [
                    "Design Patterns: Elements of Reusable Object-Oriented Software",
                ],
                "milestone": "Production deployment with live URL and comprehensive README.",
            },
            {
                "week_number": 4,
                "theme": "Staff/Senior Technical Interview Mastery",
                "target_skills": ["System Design", "Coding", "Behavioral Pitch"],
                "focus_areas": [
                    "System design walkthroughs (Scalability, Caching, Sharding, Microservices)",
                    "Behavioral storytelling using the STAR method (Situation, Task, Action, Result)",
                ],
                "action_items": [
                    "Record a 5-minute video walkthrough of your portfolio project highlighting business metrics.",
                    "Complete 5 end-to-end mock technical architecture interviews.",
                ],
                "recommended_resources": [
                    "Cracking the Coding Interview & Designing Data-Intensive Applications",
                ],
                "milestone": "Candidate is fully prepared for senior technical loops and offers.",
            },
        ]

    return {
        "target_role": target_role,
        "total_required": len(required_skills),
        "matched_skills": matched,
        "missing_skills": missing,
        "match_rate_pct": match_rate,
        "weeks": weeks,
        "summary": (
            f"You possess {len(matched)} of {len(required_skills)} required skills ({match_rate}% match) for {target_role}. "
            f"Focus on the {len(missing)} missing skills during this structured 4-week acceleration plan."
            if missing
            else f"Outstanding! You match 100% of the required skills for {target_role}. Follow this 4-week mastery roadmap to reach elite interview readiness."
        ),
    }


def _get_info(skill_name: str) -> Dict[str, str]:
    """Helper to retrieve curated information for a skill name."""
    s_clean = skill_name.lower().strip()
    return SKILL_KNOWLEDGE_BASE.get(s_clean, DEFAULT_TOPIC)


def roadmap_to_markdown(roadmap_data: Dict[str, Any]) -> str:
    """Formats the roadmap dictionary into a clean Markdown document for download."""
    lines = [
        f"# 4-Week Learning Roadmap: {roadmap_data['target_role']}",
        f"**Skill Match:** {roadmap_data['match_rate_pct']}% | "
        f"**Matched Skills:** {len(roadmap_data['matched_skills'])} | "
        f"**Target Skills to Learn:** {len(roadmap_data['missing_skills'])}",
        "",
        f"> {roadmap_data['summary']}",
        "",
        "---",
        "",
    ]

    for week in roadmap_data["weeks"]:
        lines.append(f"## Week {week['week_number']}: {week['theme']}")
        lines.append(f"**Target Skills:** {', '.join(week['target_skills'])}")
        lines.append("")
        lines.append("### Focus Areas")
        for f in week["focus_areas"]:
            lines.append(f"- {f}")
        lines.append("")
        lines.append("### Practical Action Items")
        for a in week["action_items"]:
            lines.append(f"- [ ] {a}")
        lines.append("")
        lines.append("### Recommended Resources")
        for r in week["recommended_resources"]:
            lines.append(f"- {r}")
        lines.append("")
        lines.append(f"**Weekly Milestone:** {week['milestone']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)
