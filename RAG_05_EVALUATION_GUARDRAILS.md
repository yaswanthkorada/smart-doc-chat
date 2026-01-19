# 📄 Part 5: Evaluation & Guardrails (RAGAS)

**Level:** Advanced  
**Time:** 8-10 hours  
**Prerequisites:** Parts 1-4 (Complete RAG pipeline)

---

## 🎯 Learning Objectives

By the end of this module, you'll be able to:
- [ ] Measure RAG quality with **RAGAS framework** (Faithfulness, Relevance, Precision, Recall)
- [ ] Implement **hallucination detection** and prevention
- [ ] Build **context filtering** guardrails
- [ ] Create **LLM-as-a-Judge** evaluation system
- [ ] Set up **production monitoring** and alerting
- [ ] Track **cost and performance** metrics
- [ ] Build a **golden test set** for continuous evaluation

---

## ❌ The Problem: How Do You Know Your RAG Works?

### Without Evaluation

```python
# Your RAG system
answer = rag_system.query("What was Q3 revenue?")
print(answer)
# Output: "Q3 revenue was $5.2M"

# Questions:
# ❓ Is this answer correct?
# ❓ Is it based on the retrieved documents?
# ❓ Did we retrieve the right documents?
# ❓ Are we hallucinating?
# ❓ How does quality change over time?

→ No way to know! ❌
```

### Common Issues in Production

1. **Hallucinations**: LLM makes up facts not in documents
2. **Poor Retrieval**: Wrong documents retrieved
3. **Incomplete Answers**: Missing key information
4. **Citation Errors**: Sources cited incorrectly
5. **Silent Degradation**: Quality degrades over time without notice

---

## ✅ Solution: RAGAS Evaluation Framework

**RAGAS** = **R**etrieval **A**ugmented **G**eneration **A**ssessment

### The 4 Core Metrics

```
┌─────────────────────────────────────────────────────────┐
│                    RAGAS Metrics                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. FAITHFULNESS (Context → Answer)                    │
│     Is the answer grounded in retrieved context?       │
│     Score: 0.0 - 1.0  (Target: > 0.90)                │
│                                                         │
│  2. ANSWER RELEVANCY (Question → Answer)               │
│     Does the answer address the question?              │
│     Score: 0.0 - 1.0  (Target: > 0.85)                │
│                                                         │
│  3. CONTEXT PRECISION (Question → Context)             │
│     Are retrieved documents relevant?                  │
│     Score: 0.0 - 1.0  (Target: > 0.80)                │
│                                                         │
│  4. CONTEXT RECALL (Ground Truth → Context)            │
│     Did retrieval find all necessary info?             │
│     Score: 0.0 - 1.0  (Target: > 0.85)                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation: RAGAS Evaluation

### Step 1: Install RAGAS

```bash
pip install ragas
pip install datasets
```

### Step 2: Basic RAGAS Evaluation

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset

# Prepare evaluation dataset
eval_data = {
    "question": [
        "What was Q3 2024 revenue?",
        "Who is the CEO?",
        "What are the key growth drivers?",
        # ... more questions
    ],
    "contexts": [
        # For each question, list of retrieved document chunks
        [
            "Q3 2024 revenue was $5.2M, up 15% from Q2...",
            "The third quarter showed strong performance...",
        ],
        [
            "John Smith has been CEO since 2020...",
        ],
        [
            "Key growth drivers include enterprise expansion...",
            "International revenue increased 25%...",
        ],
        # ...
    ],
    "answer": [
        # Generated answers
        "Q3 2024 revenue was $5.2M, representing 15% growth from Q2.",
        "John Smith is the CEO.",
        "Key growth drivers are enterprise expansion and international growth.",
        # ...
    ],
    "ground_truth": [
        # Optional: Expected answers for context_recall
        "Q3 2024 revenue was $5.2M",
        "John Smith",
        "Enterprise expansion and international growth",
        # ...
    ]
}

# Create dataset
dataset = Dataset.from_dict(eval_data)

# Evaluate
results = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,        # Is answer grounded in context?
        answer_relevancy,    # Does answer address question?
        context_precision,   # Are retrieved docs relevant?
        context_recall       # Did retrieval find everything needed?
    ]
)

# Print results
print(f"Faithfulness: {results['faithfulness']:.3f}")
print(f"Answer Relevancy: {results['answer_relevancy']:.3f}")
print(f"Context Precision: {results['context_precision']:.3f}")
print(f"Context Recall: {results['context_recall']:.3f}")

# Expected output:
# Faithfulness: 0.920
# Answer Relevancy: 0.880
# Context Precision: 0.850
# Context Recall: 0.870
```

### Step 3: Production RAGAS Evaluation

```python
from typing import List, Dict
from dataclasses import dataclass
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
import pandas as pd

@dataclass
class RAGResponse:
    """Single RAG query-response"""
    question: str
    contexts: List[str]
    answer: str
    ground_truth: str = None  # Optional
    metadata: Dict = None

class ProductionRAGEvaluator:
    """
    Production-grade RAG evaluation
    """
    
    def __init__(self, target_scores: Dict[str, float] = None):
        self.target_scores = target_scores or {
            "faithfulness": 0.90,
            "answer_relevancy": 0.85,
            "context_precision": 0.80,
        }
        self.evaluation_history = []
    
    def evaluate_response(self, response: RAGResponse) -> Dict:
        """
        Evaluate a single RAG response
        """
        # Prepare dataset
        eval_data = {
            "question": [response.question],
            "contexts": [response.contexts],
            "answer": [response.answer],
        }
        
        if response.ground_truth:
            eval_data["ground_truth"] = [response.ground_truth]
        
        dataset = Dataset.from_dict(eval_data)
        
        # Evaluate
        metrics = [faithfulness, answer_relevancy, context_precision]
        results = evaluate(dataset=dataset, metrics=metrics)
        
        # Check if passes thresholds
        passes = self._check_thresholds(results)
        
        # Log
        self.evaluation_history.append({
            "timestamp": pd.Timestamp.now(),
            "question": response.question,
            **results,
            "passes": passes
        })
        
        return {
            "scores": results,
            "passes": passes,
            "issues": self._identify_issues(results)
        }
    
    def evaluate_batch(self, responses: List[RAGResponse]) -> pd.DataFrame:
        """
        Evaluate multiple responses
        """
        eval_data = {
            "question": [r.question for r in responses],
            "contexts": [r.contexts for r in responses],
            "answer": [r.answer for r in responses],
        }
        
        if all(r.ground_truth for r in responses):
            eval_data["ground_truth"] = [r.ground_truth for r in responses]
        
        dataset = Dataset.from_dict(eval_data)
        
        # Evaluate
        results = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevancy, context_precision]
        )
        
        # Create results DataFrame
        df = pd.DataFrame({
            "question": eval_data["question"],
            "faithfulness": results["faithfulness"],
            "answer_relevancy": results["answer_relevancy"],
            "context_precision": results["context_precision"],
        })
        
        # Add pass/fail
        df["passes"] = df.apply(
            lambda row: all([
                row["faithfulness"] >= self.target_scores["faithfulness"],
                row["answer_relevancy"] >= self.target_scores["answer_relevancy"],
                row["context_precision"] >= self.target_scores["context_precision"],
            ]),
            axis=1
        )
        
        return df
    
    def _check_thresholds(self, results: Dict) -> bool:
        """Check if scores meet thresholds"""
        for metric, threshold in self.target_scores.items():
            if metric in results and results[metric] < threshold:
                return False
        return True
    
    def _identify_issues(self, results: Dict) -> List[str]:
        """Identify specific quality issues"""
        issues = []
        
        if results.get("faithfulness", 1.0) < self.target_scores["faithfulness"]:
            issues.append("HALLUCINATION_RISK: Answer not fully grounded in context")
        
        if results.get("answer_relevancy", 1.0) < self.target_scores["answer_relevancy"]:
            issues.append("RELEVANCE_ISSUE: Answer doesn't address question well")
        
        if results.get("context_precision", 1.0) < self.target_scores["context_precision"]:
            issues.append("RETRIEVAL_ISSUE: Retrieved documents not relevant enough")
        
        return issues
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        if not self.evaluation_history:
            return {}
        
        df = pd.DataFrame(self.evaluation_history)
        
        return {
            "total_evaluations": len(df),
            "pass_rate": df["passes"].mean(),
            "avg_faithfulness": df["faithfulness"].mean(),
            "avg_answer_relevancy": df["answer_relevancy"].mean(),
            "avg_context_precision": df["context_precision"].mean(),
            "low_quality_count": (~df["passes"]).sum()
        }


# Usage
evaluator = ProductionRAGEvaluator(target_scores={
    "faithfulness": 0.90,
    "answer_relevancy": 0.85,
    "context_precision": 0.80
})

# Evaluate single response
response = RAGResponse(
    question="What was Q3 2024 revenue?",
    contexts=[
        "Q3 2024 revenue was $5.2M, up 15% from Q2.",
        "The third quarter showed strong performance."
    ],
    answer="Q3 2024 revenue was $5.2M, growing 15% from Q2.",
    ground_truth="Q3 2024 revenue was $5.2M"
)

result = evaluator.evaluate_response(response)

print(f"Scores: {result['scores']}")
print(f"Passes: {result['passes']}")
print(f"Issues: {result['issues']}")

# Evaluate batch
responses = [...]  # List of RAGResponse objects
results_df = evaluator.evaluate_batch(responses)

print("\nBatch Results:")
print(results_df)

print("\nSummary:")
print(evaluator.get_summary_stats())
```

---

## 🛡️ Implementation: Hallucination Detection

### Method 1: LLM-as-a-Judge

```python
from langchain_openai import ChatOpenAI
from typing import Dict

class HallucinationDetector:
    """
    Detect hallucinations using LLM-as-a-Judge
    """
    
    def __init__(self, llm=None):
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0)
    
    def detect(self, question: str, context: str, answer: str) -> Dict:
        """
        Detect if answer contains hallucinations
        
        Returns:
            - has_hallucination: bool
            - confidence: float (0-1)
            - explanation: str
            - hallucinated_claims: List[str]
        """
        detection_prompt = f"""
        You are a fact-checker. Evaluate if the answer contains hallucinations.
        
        Context (Source Documents):
        {context}
        
        Question: {question}
        
        Answer to Evaluate:
        {answer}
        
        Task:
        1. Identify EVERY claim in the answer
        2. For each claim, check if it's supported by the context
        3. Mark unsupported claims as hallucinations
        
        Respond in this format:
        HALLUCINATION: YES/NO
        CONFIDENCE: 0.0-1.0
        EXPLANATION: Brief explanation
        HALLUCINATED_CLAIMS:
        - Claim 1 (if any)
        - Claim 2 (if any)
        """
        
        response = self.llm.invoke(detection_prompt).content
        
        # Parse response
        has_hallucination = "YES" in response.split('\n')[0]
        
        # Extract confidence
        confidence_line = [l for l in response.split('\n') if 'CONFIDENCE' in l]
        confidence = float(confidence_line[0].split(':')[1].strip()) if confidence_line else 0.5
        
        # Extract explanation
        explanation_line = [l for l in response.split('\n') if 'EXPLANATION' in l]
        explanation = explanation_line[0].split(':', 1)[1].strip() if explanation_line else ""
        
        # Extract hallucinated claims
        claims_section = response.split('HALLUCINATED_CLAIMS:')
        hallucinated_claims = []
        if len(claims_section) > 1:
            claims_text = claims_section[1].strip()
            hallucinated_claims = [
                line.strip('- ').strip()
                for line in claims_text.split('\n')
                if line.strip()
            ]
        
        return {
            "has_hallucination": has_hallucination,
            "confidence": confidence,
            "explanation": explanation,
            "hallucinated_claims": hallucinated_claims
        }


# Usage
detector = HallucinationDetector()

context = "Q3 2024 revenue was $5.2M, up 15% from Q2."
question = "What was Q3 revenue and growth rate?"
answer = "Q3 2024 revenue was $5.2M with 15% growth. The CEO announced plans to expand to Europe."

result = detector.detect(question, context, answer)

print(f"Has Hallucination: {result['has_hallucination']}")
print(f"Confidence: {result['confidence']}")
print(f"Explanation: {result['explanation']}")
print(f"Hallucinated Claims: {result['hallucinated_claims']}")

# Output:
# Has Hallucination: True
# Confidence: 0.95
# Explanation: Answer includes Europe expansion which is not in context
# Hallucinated Claims: ['The CEO announced plans to expand to Europe']
```

### Method 2: NLI (Natural Language Inference) Model

```python
from transformers import pipeline
from typing import List, Dict

class NLIHallucinationDetector:
    """
    Use NLI model for hallucination detection (faster, cheaper than LLM)
    """
    
    def __init__(self):
        # Load NLI model (Microsoft DeBERTa)
        self.nli_model = pipeline(
            "text-classification",
            model="microsoft/deberta-large-mnli"
        )
    
    def detect(self, context: str, answer: str) -> Dict:
        """
        Detect hallucinations using NLI
        
        NLI labels:
        - ENTAILMENT: Answer is supported by context ✅
        - CONTRADICTION: Answer contradicts context ❌
        - NEUTRAL: Answer is not addressed by context ⚠️
        """
        # Split answer into claims (sentences)
        claims = self._extract_claims(answer)
        
        hallucinated_claims = []
        neutral_claims = []
        
        for claim in claims:
            # Check if claim is entailed by context
            result = self.nli_model(f"{context} [SEP] {claim}")[0]
            
            label = result['label']
            score = result['score']
            
            if label == "CONTRADICTION" and score > 0.7:
                hallucinated_claims.append({
                    "claim": claim,
                    "label": label,
                    "confidence": score
                })
            elif label == "NEUTRAL" and score > 0.7:
                neutral_claims.append({
                    "claim": claim,
                    "label": label,
                    "confidence": score
                })
        
        has_hallucination = len(hallucinated_claims) > 0
        
        return {
            "has_hallucination": has_hallucination,
            "hallucinated_claims": hallucinated_claims,
            "neutral_claims": neutral_claims,  # May or may not be hallucinations
            "total_claims": len(claims)
        }
    
    def _extract_claims(self, text: str) -> List[str]:
        """Split text into claims (simple sentence splitting)"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]


# Usage
nli_detector = NLIHallucinationDetector()

context = "Q3 2024 revenue was $5.2M, up 15% from Q2."
answer = "Q3 2024 revenue was $5.2M with 15% growth. The CEO announced plans to expand to Europe."

result = nli_detector.detect(context, answer)

print(f"Has Hallucination: {result['has_hallucination']}")
print(f"Hallucinated Claims: {result['hallucinated_claims']}")
print(f"Neutral Claims: {result['neutral_claims']}")
```

---

## 🔒 Implementation: Context Filtering Guardrails

### Relevance-Based Filtering

```python
from typing import List, Tuple
from langchain.schema import Document
from langchain_openai import ChatOpenAI

class ContextFilter:
    """
    Filter low-quality contexts before generation
    """
    
    def __init__(self, llm=None, relevance_threshold: float = 0.7):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.relevance_threshold = relevance_threshold
    
    def filter(
        self,
        question: str,
        contexts: List[Document],
        method: str = "llm"  # "llm" or "embedding"
    ) -> List[Document]:
        """
        Filter contexts by relevance
        """
        if method == "llm":
            return self._filter_with_llm(question, contexts)
        else:
            return self._filter_with_embeddings(question, contexts)
    
    def _filter_with_llm(
        self,
        question: str,
        contexts: List[Document]
    ) -> List[Document]:
        """
        Filter using LLM relevance scoring
        """
        filtered = []
        
        for doc in contexts:
            relevance_score = self._calculate_relevance_llm(question, doc.page_content)
            
            if relevance_score >= self.relevance_threshold:
                doc.metadata["relevance_score"] = relevance_score
                filtered.append(doc)
            else:
                print(f"Filtered out (score {relevance_score:.2f}): {doc.page_content[:50]}...")
        
        print(f"Filtered: {len(contexts)} → {len(filtered)} documents")
        return filtered
    
    def _calculate_relevance_llm(self, question: str, context: str) -> float:
        """
        Calculate relevance score using LLM
        """
        prompt = f"""
        Rate the relevance of this context to the question on a scale of 0.0 to 1.0.
        
        Question: {question}
        
        Context: {context[:500]}
        
        Scoring:
        - 1.0: Directly answers the question
        - 0.7-0.9: Highly relevant, contains useful information
        - 0.4-0.6: Somewhat relevant, tangentially related
        - 0.0-0.3: Not relevant
        
        Return ONLY a number between 0.0 and 1.0.
        """
        
        try:
            response = self.llm.invoke(prompt).content.strip()
            score = float(response)
            return max(0.0, min(1.0, score))
        except:
            return 0.5  # Default
    
    def _filter_with_embeddings(
        self,
        question: str,
        contexts: List[Document]
    ) -> List[Document]:
        """
        Filter using embedding similarity
        """
        from langchain_openai import OpenAIEmbeddings
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Embed question
        question_embedding = embeddings.embed_query(question)
        
        # Embed contexts
        context_texts = [doc.page_content for doc in contexts]
        context_embeddings = embeddings.embed_documents(context_texts)
        
        # Calculate similarities
        similarities = cosine_similarity(
            [question_embedding],
            context_embeddings
        )[0]
        
        # Filter
        filtered = []
        for doc, similarity in zip(contexts, similarities):
            if similarity >= self.relevance_threshold:
                doc.metadata["relevance_score"] = float(similarity)
                filtered.append(doc)
        
        print(f"Filtered: {len(contexts)} → {len(filtered)} documents")
        return filtered


# Usage
context_filter = ContextFilter(
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
    relevance_threshold=0.7
)

# Retrieved documents
retrieved_docs = [
    Document(page_content="Q3 2024 revenue was $5.2M..."),
    Document(page_content="Company history dates back to 1990..."),  # Irrelevant
    Document(page_content="Q3 showed 15% growth..."),
]

# Filter
filtered_docs = context_filter.filter(
    question="What was Q3 2024 revenue?",
    contexts=retrieved_docs,
    method="llm"
)

# Use filtered docs for generation
context = '\n\n'.join([doc.page_content for doc in filtered_docs])
```

---

## 📊 Implementation: Production Monitoring

### Real-Time Quality Dashboard

```python
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go

class RAGMonitor:
    """
    Production monitoring for RAG system
    """
    
    def __init__(self):
        self.query_log = []
        self.alerts = []
    
    def log_query(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        metrics: Dict,
        latency: float,
        cost: float
    ):
        """
        Log a query and its metrics
        """
        self.query_log.append({
            "timestamp": datetime.now(),
            "question": question,
            "answer": answer,
            "num_contexts": len(contexts),
            "faithfulness": metrics.get("faithfulness", 0),
            "answer_relevancy": metrics.get("answer_relevancy", 0),
            "context_precision": metrics.get("context_precision", 0),
            "latency": latency,
            "cost": cost
        })
        
        # Check for alerts
        self._check_alerts(metrics)
    
    def _check_alerts(self, metrics: Dict):
        """
        Check if metrics trigger alerts
        """
        alerts = []
        
        if metrics.get("faithfulness", 1.0) < 0.80:
            alerts.append({
                "timestamp": datetime.now(),
                "type": "HALLUCINATION_RISK",
                "severity": "HIGH",
                "message": f"Faithfulness dropped to {metrics['faithfulness']:.2f}"
            })
        
        if metrics.get("context_precision", 1.0) < 0.70:
            alerts.append({
                "timestamp": datetime.now(),
                "type": "RETRIEVAL_DEGRADATION",
                "severity": "MEDIUM",
                "message": f"Context precision dropped to {metrics['context_precision']:.2f}"
            })
        
        self.alerts.extend(alerts)
        
        for alert in alerts:
            print(f"🚨 ALERT [{alert['severity']}]: {alert['message']}")
    
    def get_dashboard_data(self, hours: int = 24) -> Dict:
        """
        Get dashboard data for last N hours
        """
        if not self.query_log:
            return {}
        
        df = pd.DataFrame(self.query_log)
        
        # Filter by time
        cutoff = datetime.now() - timedelta(hours=hours)
        df = df[df["timestamp"] >= cutoff]
        
        if len(df) == 0:
            return {}
        
        # Calculate statistics
        stats = {
            "total_queries": len(df),
            "avg_faithfulness": df["faithfulness"].mean(),
            "avg_answer_relevancy": df["answer_relevancy"].mean(),
            "avg_context_precision": df["context_precision"].mean(),
            "avg_latency": df["latency"].mean(),
            "p95_latency": df["latency"].quantile(0.95),
            "total_cost": df["cost"].sum(),
            "avg_cost_per_query": df["cost"].mean(),
            "low_quality_rate": (
                (df["faithfulness"] < 0.80) | 
                (df["answer_relevancy"] < 0.80)
            ).mean(),
        }
        
        return {
            "stats": stats,
            "timeseries": df,
            "alerts": self.alerts[-10:]  # Last 10 alerts
        }
    
    def plot_quality_trends(self, hours: int = 24):
        """
        Plot quality metrics over time
        """
        dashboard_data = self.get_dashboard_data(hours)
        
        if not dashboard_data:
            print("No data to plot")
            return
        
        df = dashboard_data["timeseries"]
        
        # Create subplots
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["faithfulness"],
            name="Faithfulness",
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["answer_relevancy"],
            name="Answer Relevancy",
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["context_precision"],
            name="Context Precision",
            mode='lines+markers'
        ))
        
        # Add threshold lines
        fig.add_hline(y=0.80, line_dash="dash", line_color="red",
                     annotation_text="Quality Threshold")
        
        fig.update_layout(
            title=f"RAG Quality Metrics (Last {hours} hours)",
            xaxis_title="Time",
            yaxis_title="Score",
            yaxis_range=[0, 1],
            hovermode='x unified'
        )
        
        fig.show()
    
    def generate_report(self, hours: int = 24) -> str:
        """
        Generate text report
        """
        dashboard_data = self.get_dashboard_data(hours)
        
        if not dashboard_data:
            return "No data available"
        
        stats = dashboard_data["stats"]
        
        report = f"""
        ╔══════════════════════════════════════════════════╗
        ║         RAG SYSTEM HEALTH REPORT                 ║
        ║         Last {hours} Hours                            ║
        ╚══════════════════════════════════════════════════╝
        
        📊 QUERY STATISTICS
        ─────────────────────────────────────────────────
        Total Queries: {stats['total_queries']}
        Low Quality Rate: {stats['low_quality_rate']:.1%}
        
        📈 QUALITY METRICS
        ─────────────────────────────────────────────────
        Avg Faithfulness:     {stats['avg_faithfulness']:.3f}  {'✅' if stats['avg_faithfulness'] >= 0.80 else '❌'}
        Avg Answer Relevancy: {stats['avg_answer_relevancy']:.3f}  {'✅' if stats['avg_answer_relevancy'] >= 0.80 else '❌'}
        Avg Context Precision:{stats['avg_context_precision']:.3f}  {'✅' if stats['avg_context_precision'] >= 0.80 else '❌'}
        
        ⚡ PERFORMANCE METRICS
        ─────────────────────────────────────────────────
        Avg Latency:     {stats['avg_latency']:.2f}s
        P95 Latency:     {stats['p95_latency']:.2f}s
        
        💰 COST METRICS
        ─────────────────────────────────────────────────
        Total Cost:      ${stats['total_cost']:.2f}
        Avg Cost/Query:  ${stats['avg_cost_per_query']:.4f}
        
        🚨 RECENT ALERTS
        ─────────────────────────────────────────────────
        """
        
        alerts = dashboard_data["alerts"]
        if alerts:
            for alert in alerts[-5:]:
                report += f"\n  [{alert['severity']}] {alert['message']}"
        else:
            report += "\n  No recent alerts ✅"
        
        return report


# Usage
monitor = RAGMonitor()

# Log queries (integrate into your RAG pipeline)
import time

start = time.time()
question = "What was Q3 revenue?"
answer = rag_system.query(question)
latency = time.time() - start

# Evaluate with RAGAS
metrics = evaluator.evaluate_response(RAGResponse(
    question=question,
    contexts=retrieved_contexts,
    answer=answer
))

# Log
monitor.log_query(
    question=question,
    answer=answer,
    contexts=retrieved_contexts,
    metrics=metrics["scores"],
    latency=latency,
    cost=0.05  # Calculated cost
)

# View dashboard
print(monitor.generate_report(hours=24))

# Plot trends
monitor.plot_quality_trends(hours=24)
```

---

## 🧪 Implementation: Golden Test Set

### Creating a Golden Test Set

```python
from typing import List, Dict
import json

class GoldenTestSetBuilder:
    """
    Build and manage golden test set for RAG evaluation
    """
    
    def __init__(self, filepath: str = "golden_testset.json"):
        self.filepath = filepath
        self.test_cases = self._load_test_cases()
    
    def add_test_case(
        self,
        question: str,
        expected_answer: str,
        relevant_doc_ids: List[str],
        category: str = "general",
        difficulty: str = "medium"
    ):
        """
        Add a test case to golden set
        """
        test_case = {
            "id": len(self.test_cases) + 1,
            "question": question,
            "expected_answer": expected_answer,
            "relevant_doc_ids": relevant_doc_ids,
            "category": category,
            "difficulty": difficulty
        }
        
        self.test_cases.append(test_case)
        self._save_test_cases()
    
    def run_evaluation(self, rag_system) -> pd.DataFrame:
        """
        Run RAG system on golden test set
        """
        results = []
        
        for test_case in self.test_cases:
            # Get RAG response
            response = rag_system.query(test_case["question"])
            
            # Evaluate
            eval_result = evaluator.evaluate_response(RAGResponse(
                question=test_case["question"],
                contexts=response["contexts"],
                answer=response["answer"],
                ground_truth=test_case["expected_answer"]
            ))
            
            results.append({
                "id": test_case["id"],
                "question": test_case["question"],
                "category": test_case["category"],
                "difficulty": test_case["difficulty"],
                "faithfulness": eval_result["scores"]["faithfulness"],
                "answer_relevancy": eval_result["scores"]["answer_relevancy"],
                "passes": eval_result["passes"]
            })
        
        return pd.DataFrame(results)
    
    def _load_test_cases(self) -> List[Dict]:
        """Load test cases from file"""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _save_test_cases(self):
        """Save test cases to file"""
        with open(self.filepath, 'w') as f:
            json.dump(self.test_cases, f, indent=2)


# Usage
test_builder = GoldenTestSetBuilder()

# Add test cases
test_builder.add_test_case(
    question="What was Q3 2024 revenue?",
    expected_answer="Q3 2024 revenue was $5.2M",
    relevant_doc_ids=["financial_report_2024.pdf:page_15"],
    category="financial",
    difficulty="easy"
)

test_builder.add_test_case(
    question="Compare Q3 2024 vs Q3 2023 revenue and explain growth drivers",
    expected_answer="Q3 2024 revenue ($5.2M) increased 27% vs Q3 2023 ($4.1M). Growth driven by enterprise expansion (+$800K) and international markets (+$200K).",
    relevant_doc_ids=["financial_report_2024.pdf:page_15", "financial_report_2023.pdf:page_12"],
    category="financial",
    difficulty="hard"
)

# Run evaluation
results_df = test_builder.run_evaluation(rag_system)

print(results_df)
print(f"\nPass Rate: {results_df['passes'].mean():.1%}")
```

---

## 💡 Pro Tips from a Senior AI Engineer

### Tip #1: Start Small with Golden Test Set

```python
# Start with 20-30 high-quality test cases
# Categories:
# - 10 easy (single fact lookup)
# - 10 medium (multi-fact, same document)
# - 10 hard (comparison, multi-document, reasoning)

# Expand gradually as you find edge cases
```

### Tip #2: Automate Regression Testing

```python
# Run golden test set after every change

def ci_cd_test():
    """Run in CI/CD pipeline"""
    results = test_builder.run_evaluation(rag_system)
    pass_rate = results['passes'].mean()
    
    if pass_rate < 0.80:
        raise Exception(f"Quality regression! Pass rate: {pass_rate:.1%}")
    
    print(f"✅ Quality check passed: {pass_rate:.1%}")
```

### Tip #3: Monitor Cost Trends

```python
# Track cost per query over time
# Alert if costs spike unexpectedly

if daily_avg_cost > baseline_cost * 1.5:
    alert("Cost increased 50%! Investigate.")
```

### Tip #4: Create User Feedback Loop

```python
# Log user satisfaction
def log_user_feedback(query_id: str, satisfied: bool):
    """
    Track which queries users are satisfied with
    Add low-satisfaction queries to golden test set
    """
    pass
```

---

## ✅ Complete Evaluation Pipeline

```python
class CompleteeRAGEvaluationPipeline:
    """
    End-to-end evaluation pipeline
    """
    
    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.ragas_evaluator = ProductionRAGEvaluator()
        self.hallucination_detector = HallucinationDetector()
        self.context_filter = ContextFilter()
        self.monitor = RAGMonitor()
        self.golden_test = GoldenTestSetBuilder()
    
    def query_with_evaluation(self, question: str) -> Dict:
        """
        Query with full evaluation pipeline
        """
        import time
        start = time.time()
        
        # Step 1: Retrieve contexts
        contexts = self.rag_system.retrieve(question, k=10)
        
        # Step 2: Filter contexts
        filtered_contexts = self.context_filter.filter(question, contexts)
        
        # Step 3: Generate answer
        answer = self.rag_system.generate(question, filtered_contexts)
        
        latency = time.time() - start
        
        # Step 4: Evaluate with RAGAS
        ragas_result = self.ragas_evaluator.evaluate_response(RAGResponse(
            question=question,
            contexts=[doc.page_content for doc in filtered_contexts],
            answer=answer
        ))
        
        # Step 5: Detect hallucinations
        context_text = '\n\n'.join([doc.page_content for doc in filtered_contexts])
        hallucination_result = self.hallucination_detector.detect(
            question, context_text, answer
        )
        
        # Step 6: Log to monitor
        self.monitor.log_query(
            question=question,
            answer=answer,
            contexts=[doc.page_content for doc in filtered_contexts],
            metrics=ragas_result["scores"],
            latency=latency,
            cost=self._calculate_cost(question, answer, filtered_contexts)
        )
        
        return {
            "answer": answer,
            "quality_scores": ragas_result["scores"],
            "hallucination_check": hallucination_result,
            "num_contexts": len(filtered_contexts),
            "latency": latency,
            "passes_quality_check": ragas_result["passes"]
        }


# Usage
pipeline = CompleteRAGEvaluationPipeline(rag_system)

result = pipeline.query_with_evaluation("What was Q3 2024 revenue?")

print(f"Answer: {result['answer']}")
print(f"Quality Scores: {result['quality_scores']}")
print(f"Hallucination Risk: {result['hallucination_check']['has_hallucination']}")
print(f"Passes Check: {result['passes_quality_check']}")
```

---

## ✅ Exercises

### Exercise 1: Set Up RAGAS Evaluation
1. Create golden test set with 20 questions
2. Evaluate your current RAG system
3. Identify top 3 quality issues

### Exercise 2: Implement Hallucination Detection
1. Add LLM-as-a-Judge hallucination detector
2. Test with answers containing hallucinations
3. Measure false positive/negative rates

### Exercise 3: Build Monitoring Dashboard
1. Implement RAGMonitor class
2. Log 100 queries
3. Generate quality report

---

## 🎓 Congratulations!

You've completed the Advanced RAG Mastery curriculum! 🎉

### What You've Learned

1. ✅ **Part 1**: Semantic chunking, parent-document retrieval
2. ✅ **Part 2**: Hybrid search (BM25 + Vector), reranking
3. ✅ **Part 3**: ReAct agents, self-RAG, corrective RAG
4. ✅ **Part 4**: Multi-query, HyDE, query decomposition
5. ✅ **Part 5**: RAGAS evaluation, hallucination detection, monitoring

### Next Steps

1. **Implement** these techniques in your Smart Document Chat project
2. **Measure** improvements with RAGAS
3. **Monitor** quality in production
4. **Iterate** based on real user feedback

### Your New RAG System

```
Before: Basic RAG (60% quality, high hallucinations)
After: Advanced Agentic RAG (90% quality, < 5% hallucinations)

- 40% better retrieval recall
- 60% reduction in hallucinations
- Self-correcting agent loops
- Production-ready monitoring
```

---

*Part of the Advanced RAG Mastery series for Smart Document Chat*  
*Last Updated: January 11, 2026*
