# 📊 Part 5: Evaluation & Metrics

## 📚 Chapter Overview

Master comprehensive evaluation techniques including LLM-as-a-Judge, RAGAS (RAG Assessment), custom metrics, and production monitoring to ensure your RAG system delivers consistent quality.

**Time to Complete:** 10-12 hours  
**Difficulty:** ⭐⭐⭐⭐⭐ Expert  
**Prerequisites:** Parts 1-4 (Complete curriculum)

---

## 🎯 Why Evaluation Matters

### The Measurement Problem

```
You can't improve what you don't measure!
```

**Without Evaluation:**
- ❌ No idea if changes improve quality
- ❌ Can't catch regressions
- ❌ User complaints are your only feedback
- ❌ Difficult to justify ROI

**With Evaluation:**
- ✅ Data-driven improvements
- ✅ Catch issues before users do
- ✅ Track quality over time
- ✅ Optimize cost/quality tradeoff

---

## 🤖 1. LLM-as-a-Judge

### What is LLM-as-a-Judge?

**Concept:** Use a powerful LLM (like GPT-4) to evaluate the quality of another LLM's outputs.

**Why It Works:**
- LLMs are good at nuanced evaluation
- Cheaper than human annotation
- Scalable to thousands of examples
- Can catch subtle quality issues

### Basic LLM-as-a-Judge Implementation

```python
# File: utils/evaluation/llm_judge.py

from typing import Dict, List
import json

class LLMJudge:
    """Use LLM to evaluate RAG system outputs"""
    
    def __init__(self, judge_llm, criteria: List[str] = None):
        """
        judge_llm: A powerful LLM (e.g., GPT-4) for evaluation
        criteria: List of evaluation criteria
        """
        self.judge_llm = judge_llm
        self.criteria = criteria or [
            "accuracy",
            "completeness",
            "relevance",
            "citation_quality",
            "clarity"
        ]
    
    async def evaluate_response(
        self,
        question: str,
        context: str,
        response: str,
        ground_truth: str = None
    ) -> Dict:
        """
        Evaluate a single response
        """
        evaluation_prompt = self._build_evaluation_prompt(
            question, context, response, ground_truth
        )
        
        # Get judge's evaluation
        judge_response = await self.judge_llm.generate(evaluation_prompt)
        
        # Parse evaluation
        evaluation = self._parse_evaluation(judge_response)
        
        return evaluation
    
    def _build_evaluation_prompt(
        self,
        question: str,
        context: str,
        response: str,
        ground_truth: str = None
    ) -> str:
        """Build prompt for judge"""
        
        prompt = f"""
You are an expert evaluator of AI-generated responses. Evaluate the quality of this response.

# QUESTION
{question}

# RETRIEVED CONTEXT
{context}

# AI RESPONSE TO EVALUATE
{response}
"""
        
        if ground_truth:
            prompt += f"""
# GROUND TRUTH (Expected Answer)
{ground_truth}
"""
        
        prompt += f"""
# EVALUATION CRITERIA

Evaluate the response on these criteria (score each 0-10):

1. **ACCURACY** (0-10)
   - Are all facts correct?
   - Is information properly sourced?
   - Any hallucinations or errors?

2. **COMPLETENESS** (0-10)
   - Does it fully answer the question?
   - Are all aspects addressed?
   - Any missing critical information?

3. **RELEVANCE** (0-10)
   - Is the response on-topic?
   - Does it directly address the question?
   - Any unnecessary information?

4. **CITATION QUALITY** (0-10)
   - Are sources properly cited?
   - Can claims be traced to context?
   - Correct citation format [filename, p.X]?

5. **CLARITY** (0-10)
   - Is the response clear and well-structured?
   - Easy to understand?
   - Good grammar and formatting?

# HALLUCINATION CHECK

Does the response contain ANY information NOT present in the context?
- YES (major issue) / MINOR (acceptable inference) / NO (all grounded)

# OUTPUT FORMAT

Provide your evaluation in JSON:

```json
{{
  "scores": {{
    "accuracy": 8,
    "completeness": 9,
    "relevance": 10,
    "citation_quality": 7,
    "clarity": 9
  }},
  "overall_score": 8.6,
  "hallucination": "NO",
  "strengths": ["List 2-3 strengths"],
  "weaknesses": ["List 2-3 weaknesses"],
  "recommendation": "PASS|FAIL|NEEDS_IMPROVEMENT",
  "detailed_feedback": "Explain your evaluation in 2-3 sentences"
}}
```
"""
        
        return prompt
    
    def _parse_evaluation(self, judge_response: str) -> Dict:
        """Parse judge's evaluation"""
        try:
            # Extract JSON from response
            json_match = judge_response.split("```json")[1].split("```")[0]
            evaluation = json.loads(json_match.strip())
            return evaluation
        except Exception as e:
            # Fallback parsing
            return {
                "error": f"Failed to parse evaluation: {str(e)}",
                "raw_response": judge_response
            }
    
    async def batch_evaluate(
        self,
        test_cases: List[Dict]
    ) -> Dict:
        """
        Evaluate multiple test cases
        
        test_cases: [
            {
                "question": "...",
                "context": "...",
                "response": "...",
                "ground_truth": "..." (optional)
            }
        ]
        """
        evaluations = []
        
        for i, test_case in enumerate(test_cases):
            print(f"Evaluating test case {i+1}/{len(test_cases)}")
            
            evaluation = await self.evaluate_response(
                question=test_case["question"],
                context=test_case["context"],
                response=test_case["response"],
                ground_truth=test_case.get("ground_truth")
            )
            
            evaluations.append({
                "test_case": test_case,
                "evaluation": evaluation
            })
        
        # Aggregate statistics
        stats = self._aggregate_statistics(evaluations)
        
        return {
            "evaluations": evaluations,
            "statistics": stats
        }
    
    def _aggregate_statistics(self, evaluations: List[Dict]) -> Dict:
        """Calculate aggregate statistics"""
        
        all_scores = {
            criterion: []
            for criterion in self.criteria
        }
        overall_scores = []
        recommendations = {"PASS": 0, "FAIL": 0, "NEEDS_IMPROVEMENT": 0}
        hallucinations = {"YES": 0, "MINOR": 0, "NO": 0}
        
        for eval_data in evaluations:
            evaluation = eval_data["evaluation"]
            
            # Collect scores
            if "scores" in evaluation:
                for criterion, score in evaluation["scores"].items():
                    if criterion in all_scores:
                        all_scores[criterion].append(score)
            
            if "overall_score" in evaluation:
                overall_scores.append(evaluation["overall_score"])
            
            if "recommendation" in evaluation:
                rec = evaluation["recommendation"]
                if rec in recommendations:
                    recommendations[rec] += 1
            
            if "hallucination" in evaluation:
                hall = evaluation["hallucination"]
                if hall in hallucinations:
                    hallucinations[hall] += 1
        
        # Calculate averages
        avg_scores = {
            criterion: sum(scores) / len(scores) if scores else 0
            for criterion, scores in all_scores.items()
        }
        
        avg_overall = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        return {
            "average_scores": avg_scores,
            "average_overall": avg_overall,
            "recommendations": recommendations,
            "hallucination_distribution": hallucinations,
            "total_evaluations": len(evaluations),
            "pass_rate": recommendations["PASS"] / len(evaluations) if evaluations else 0
        }


# Usage Example
judge = LLMJudge(judge_llm=gpt4_model)

# Single evaluation
evaluation = await judge.evaluate_response(
    question="What was Q3 revenue?",
    context="Q3 2024 revenue was $4.2M [report.pdf, p.3]",
    response="Q3 revenue was $4.2 million. [Source: report.pdf, page 3]",
    ground_truth="The revenue in Q3 2024 was $4.2 million."
)

print(f"Overall Score: {evaluation['overall_score']}/10")
print(f"Recommendation: {evaluation['recommendation']}")
print(f"Hallucination: {evaluation['hallucination']}")

# Batch evaluation
test_cases = [
    {
        "question": "What was Q3 revenue?",
        "context": "...",
        "response": "...",
        "ground_truth": "..."
    },
    # ... more test cases
]

batch_results = await judge.batch_evaluate(test_cases)

print(f"Average Overall Score: {batch_results['statistics']['average_overall']:.2f}")
print(f"Pass Rate: {batch_results['statistics']['pass_rate']:.1%}")
```

### Pairwise Comparison (A vs B)

```python
# File: utils/evaluation/pairwise_judge.py

class PairwiseJudge:
    """Compare two responses head-to-head"""
    
    def __init__(self, judge_llm):
        self.judge_llm = judge_llm
    
    async def compare_responses(
        self,
        question: str,
        context: str,
        response_a: str,
        response_b: str
    ) -> Dict:
        """
        Compare two responses - which is better?
        """
        comparison_prompt = f"""
You are an expert evaluator. Compare these two AI responses to the same question.

# QUESTION
{question}

# CONTEXT
{context}

# RESPONSE A
{response_a}

# RESPONSE B
{response_b}

# YOUR TASK

Compare the responses on:
1. Accuracy (which has more correct facts?)
2. Completeness (which answers more thoroughly?)
3. Citation quality (which cites sources better?)
4. Clarity (which is easier to understand?)

# OUTPUT FORMAT

```json
{{
  "winner": "A|B|TIE",
  "confidence": 0.85,
  "reasoning": "Explain why one is better",
  "scores_a": {{
    "accuracy": 8,
    "completeness": 7,
    "citation_quality": 9,
    "clarity": 8
  }},
  "scores_b": {{
    "accuracy": 9,
    "completeness": 9,
    "citation_quality": 7,
    "clarity": 8
  }},
  "vote_breakdown": {{
    "accuracy": "B",
    "completeness": "B",
    "citation_quality": "A",
    "clarity": "TIE"
  }}
}}
```
"""
        
        judge_response = await self.judge_llm.generate(comparison_prompt)
        comparison = self._parse_comparison(judge_response)
        
        return comparison


# Usage for A/B testing
pairwise_judge = PairwiseJudge(judge_llm=gpt4_model)

comparison = await pairwise_judge.compare_responses(
    question="What was Q3 revenue?",
    context=retrieved_context,
    response_a=prompt_v1_response,
    response_b=prompt_v2_response
)

print(f"Winner: {comparison['winner']}")
print(f"Confidence: {comparison['confidence']}")
```

---

## 📈 2. RAGAS: RAG Assessment

### What is RAGAS?

**RAGAS** = **R**etrieval **A**ugmented **G**eneration **A**ssessment

A specialized framework for evaluating RAG systems across multiple dimensions.

**Paper:** [RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217)

### Key RAGAS Metrics

1. **Context Precision**: Is retrieved context relevant?
2. **Context Recall**: Did retrieval find all necessary info?
3. **Faithfulness**: Is response grounded in context?
4. **Answer Relevancy**: Does answer address the question?

### Installing RAGAS

```bash
pip install ragas
```

### RAGAS Implementation

```python
# File: utils/evaluation/ragas_evaluator.py

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset
from typing import List, Dict

class RAGASEvaluator:
    """Comprehensive RAG evaluation using RAGAS"""
    
    def __init__(self, llm, embeddings):
        """
        llm: Language model for evaluation
        embeddings: Embedding model for semantic similarity
        """
        self.llm = llm
        self.embeddings = embeddings
        
        # Configure RAGAS metrics
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    
    def evaluate_rag_system(
        self,
        test_cases: List[Dict]
    ) -> Dict:
        """
        Evaluate RAG system comprehensively
        
        test_cases format:
        [
            {
                "question": "What was Q3 revenue?",
                "contexts": ["Q3 revenue was $4.2M [report.pdf, p.3]", ...],
                "answer": "Q3 revenue was $4.2 million...",
                "ground_truth": "The Q3 revenue was $4.2 million."
            }
        ]
        """
        # Convert to RAGAS dataset format
        dataset = Dataset.from_dict({
            "question": [tc["question"] for tc in test_cases],
            "contexts": [tc["contexts"] for tc in test_cases],
            "answer": [tc["answer"] for tc in test_cases],
            "ground_truth": [tc.get("ground_truth", "") for tc in test_cases]
        })
        
        # Run evaluation
        results = evaluate(
            dataset=dataset,
            metrics=self.metrics,
            llm=self.llm,
            embeddings=self.embeddings
        )
        
        # Process results
        return self._process_results(results)
    
    def _process_results(self, results) -> Dict:
        """Process and format RAGAS results"""
        
        return {
            "overall_scores": {
                "faithfulness": results["faithfulness"],
                "answer_relevancy": results["answer_relevancy"],
                "context_precision": results["context_precision"],
                "context_recall": results["context_recall"]
            },
            "aggregated_score": sum([
                results["faithfulness"],
                results["answer_relevancy"],
                results["context_precision"],
                results["context_recall"]
            ]) / 4,
            "detailed_results": results,
            "interpretation": self._interpret_scores(results)
        }
    
    def _interpret_scores(self, results: Dict) -> Dict:
        """Provide actionable interpretation"""
        
        interpretations = {}
        
        # Faithfulness
        if results["faithfulness"] < 0.7:
            interpretations["faithfulness"] = {
                "status": "NEEDS_IMPROVEMENT",
                "issue": "High hallucination rate",
                "recommendation": "Add stronger grounding instructions and self-reflection"
            }
        elif results["faithfulness"] < 0.85:
            interpretations["faithfulness"] = {
                "status": "ACCEPTABLE",
                "recommendation": "Consider adding citation verification"
            }
        else:
            interpretations["faithfulness"] = {
                "status": "EXCELLENT",
                "note": "Strong grounding in context"
            }
        
        # Answer Relevancy
        if results["answer_relevancy"] < 0.7:
            interpretations["answer_relevancy"] = {
                "status": "NEEDS_IMPROVEMENT",
                "issue": "Answers not addressing questions well",
                "recommendation": "Improve query understanding and prompt clarity"
            }
        
        # Context Precision
        if results["context_precision"] < 0.7:
            interpretations["context_precision"] = {
                "status": "NEEDS_IMPROVEMENT",
                "issue": "Retrieved context contains too much irrelevant info",
                "recommendation": "Improve retrieval relevance threshold or reranking"
            }
        
        # Context Recall
        if results["context_recall"] < 0.7:
            interpretations["context_recall"] = {
                "status": "NEEDS_IMPROVEMENT",
                "issue": "Missing important information in retrieval",
                "recommendation": "Increase number of retrieved chunks or improve search strategy"
            }
        
        return interpretations


# Usage Example
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI

evaluator = RAGASEvaluator(
    llm=OpenAI(model="gpt-4"),
    embeddings=OpenAIEmbeddings()
)

test_cases = [
    {
        "question": "What was the Q3 2024 revenue?",
        "contexts": [
            "Q3 2024 revenue reached $4.2M, up 10% from Q2. [report.pdf, p.3]",
            "The company saw strong growth in Q3. [report.pdf, p.1]"
        ],
        "answer": "Q3 2024 revenue was $4.2 million, representing 10% growth from Q2. [Source: report.pdf, page 3]",
        "ground_truth": "The Q3 2024 revenue was $4.2 million."
    },
    # ... more test cases
]

results = evaluator.evaluate_rag_system(test_cases)

print("RAGAS Evaluation Results:")
print(f"Faithfulness: {results['overall_scores']['faithfulness']:.3f}")
print(f"Answer Relevancy: {results['overall_scores']['answer_relevancy']:.3f}")
print(f"Context Precision: {results['overall_scores']['context_precision']:.3f}")
print(f"Context Recall: {results['overall_scores']['context_recall']:.3f}")
print(f"\nAggregated Score: {results['aggregated_score']:.3f}")

# Print interpretations
for metric, interpretation in results['interpretation'].items():
    print(f"\n{metric}: {interpretation['status']}")
    if 'recommendation' in interpretation:
        print(f"  → {interpretation['recommendation']}")
```

### Custom RAGAS Metrics

```python
# File: utils/evaluation/custom_ragas_metrics.py

from ragas.metrics.base import MetricWithLLM
from langchain.prompts import PromptTemplate

class CitationQuality(MetricWithLLM):
    """Custom metric: Evaluate citation quality"""
    
    name: str = "citation_quality"
    
    def __init__(self, llm):
        super().__init__(llm=llm)
    
    def _score(self, question: str, answer: str, contexts: List[str]) -> float:
        """
        Score citation quality (0.0 to 1.0)
        """
        prompt = f"""
Evaluate citation quality in this answer:

Question: {question}
Answer: {answer}
Available Contexts: {contexts}

Scoring criteria:
- All facts cited? (0.4 points)
- Correct citation format? (0.3 points)
- Citations traceable to context? (0.3 points)

Return score 0.0 to 1.0:
"""
        
        response = self.llm(prompt)
        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.0


class ResponseCompleteness(MetricWithLLM):
    """Custom metric: Check if answer is complete"""
    
    name: str = "response_completeness"
    
    def _score(self, question: str, answer: str, ground_truth: str = None) -> float:
        """Score how completely the answer addresses the question"""
        
        prompt = f"""
Rate how completely this answer addresses the question:

Question: {question}
Answer: {answer}
"""
        
        if ground_truth:
            prompt += f"\nExpected Answer: {ground_truth}"
        
        prompt += """
Score 0.0 to 1.0:
- 1.0 = Fully complete, all aspects addressed
- 0.7 = Mostly complete, minor gaps
- 0.5 = Partial answer
- 0.3 = Incomplete, major gaps
- 0.0 = Doesn't answer the question

Return only the score:
"""
        
        response = self.llm(prompt)
        try:
            return float(response.strip())
        except:
            return 0.0


# Usage with custom metrics
from ragas import evaluate

custom_metrics = [
    faithfulness,
    answer_relevancy,
    CitationQuality(llm=evaluation_llm),
    ResponseCompleteness(llm=evaluation_llm)
]

results = evaluate(
    dataset=test_dataset,
    metrics=custom_metrics,
    llm=llm,
    embeddings=embeddings
)
```

---

## 🎯 3. Custom Metrics for Your Domain

### Domain-Specific Metrics

```python
# File: utils/evaluation/custom_metrics.py

class DocumentRAGMetrics:
    """Custom metrics for document RAG system"""
    
    @staticmethod
    def calculate_citation_accuracy(response: str, context: str) -> float:
        """
        Check if all citations in response exist in context
        """
        import re
        
        # Extract citations from response
        citation_pattern = r'\[(.*?\.(?:pdf|docx|txt)),\s*p\.(\d+)\]'
        citations = re.findall(citation_pattern, response)
        
        if not citations:
            return 0.0  # No citations = poor quality
        
        # Check each citation
        correct_citations = 0
        for filename, page in citations:
            # Check if this source is in context
            if filename in context and f"p.{page}" in context:
                correct_citations += 1
        
        return correct_citations / len(citations)
    
    @staticmethod
    def calculate_numerical_accuracy(response: str, ground_truth: str) -> float:
        """
        Check if numerical values match exactly
        """
        import re
        
        # Extract numbers from both
        response_numbers = set(re.findall(r'\$?[\d,]+\.?\d*[MKB]?', response))
        truth_numbers = set(re.findall(r'\$?[\d,]+\.?\d*[MKB]?', ground_truth))
        
        if not truth_numbers:
            return 1.0  # No numbers to compare
        
        # Calculate overlap
        correct = len(response_numbers & truth_numbers)
        total = len(truth_numbers)
        
        return correct / total
    
    @staticmethod
    def calculate_response_length_appropriateness(
        question: str,
        response: str
    ) -> float:
        """
        Check if response length is appropriate for question complexity
        """
        # Simple question → short answer
        # Complex question → longer answer
        
        question_length = len(question.split())
        response_length = len(response.split())
        
        # Heuristic: response should be 2-10x question length
        ideal_min = question_length * 2
        ideal_max = question_length * 10
        
        if ideal_min <= response_length <= ideal_max:
            return 1.0
        elif response_length < ideal_min:
            # Too short
            return response_length / ideal_min
        else:
            # Too long
            return ideal_max / response_length
    
    @staticmethod
    def calculate_source_diversity(response: str) -> float:
        """
        Check if response uses multiple sources (better for comprehensive answers)
        """
        import re
        
        # Extract unique source files
        sources = set(re.findall(r'\[(.*?)\.(?:pdf|docx|txt),', response))
        
        # Score based on diversity
        if len(sources) == 0:
            return 0.0
        elif len(sources) == 1:
            return 0.5
        elif len(sources) == 2:
            return 0.75
        else:
            return 1.0


# Usage
metrics = DocumentRAGMetrics()

citation_accuracy = metrics.calculate_citation_accuracy(
    response="Q3 revenue was $4.2M [report.pdf, p.3]",
    context="Source: report.pdf, page 3 - Q3 revenue reached $4.2M"
)

numerical_accuracy = metrics.calculate_numerical_accuracy(
    response="Revenue grew by 10.53%",
    ground_truth="Growth rate was 10.53%"
)

print(f"Citation Accuracy: {citation_accuracy:.1%}")
print(f"Numerical Accuracy: {numerical_accuracy:.1%}")
```

---

## 📊 4. Production Monitoring

### Real-Time Quality Monitoring

```python
# File: utils/evaluation/production_monitor.py

import time
from typing import Dict, List
from datetime import datetime, timedelta
import json

class ProductionMonitor:
    """Monitor RAG system quality in production"""
    
    def __init__(self, alert_threshold: Dict = None):
        self.alert_threshold = alert_threshold or {
            "accuracy": 0.80,
            "hallucination_rate": 0.05,
            "avg_latency": 5.0,
            "error_rate": 0.01
        }
        
        self.metrics_buffer = []
        self.alerts = []
    
    def log_interaction(
        self,
        question: str,
        context: str,
        response: str,
        latency: float,
        success: bool,
        user_feedback: str = None
    ):
        """Log each interaction for monitoring"""
        
        # Quick quality checks
        has_citation = self._check_citation(response)
        possible_hallucination = self._detect_hallucination(response, context)
        
        interaction_log = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": response,
            "latency": latency,
            "success": success,
            "has_citation": has_citation,
            "possible_hallucination": possible_hallucination,
            "user_feedback": user_feedback
        }
        
        self.metrics_buffer.append(interaction_log)
        
        # Check for alerts
        self._check_alerts(interaction_log)
        
        # Periodic aggregation
        if len(self.metrics_buffer) >= 100:
            self._aggregate_and_report()
    
    def _check_citation(self, response: str) -> bool:
        """Quick check for citation presence"""
        import re
        return bool(re.search(r'\[.*?\.(?:pdf|docx|txt),\s*p\.\d+\]', response))
    
    def _detect_hallucination(self, response: str, context: str) -> bool:
        """Simple hallucination detection"""
        # Extract key phrases from response
        response_words = set(response.lower().split())
        context_words = set(context.lower().split())
        
        # If less than 60% overlap, possible hallucination
        overlap = len(response_words & context_words)
        overlap_ratio = overlap / len(response_words) if response_words else 0
        
        return overlap_ratio < 0.6
    
    def _check_alerts(self, interaction: Dict):
        """Check if alerts should be triggered"""
        
        # High latency alert
        if interaction["latency"] > self.alert_threshold["avg_latency"]:
            self.alerts.append({
                "type": "HIGH_LATENCY",
                "timestamp": interaction["timestamp"],
                "latency": interaction["latency"],
                "threshold": self.alert_threshold["avg_latency"]
            })
        
        # Missing citation alert
        if not interaction["has_citation"]:
            self.alerts.append({
                "type": "MISSING_CITATION",
                "timestamp": interaction["timestamp"],
                "question": interaction["question"]
            })
        
        # Possible hallucination alert
        if interaction["possible_hallucination"]:
            self.alerts.append({
                "type": "POSSIBLE_HALLUCINATION",
                "timestamp": interaction["timestamp"],
                "question": interaction["question"]
            })
    
    def _aggregate_and_report(self):
        """Aggregate metrics and generate report"""
        
        report = {
            "period": {
                "start": self.metrics_buffer[0]["timestamp"],
                "end": self.metrics_buffer[-1]["timestamp"]
            },
            "total_interactions": len(self.metrics_buffer),
            "metrics": {}
        }
        
        # Calculate metrics
        latencies = [m["latency"] for m in self.metrics_buffer]
        successes = [m["success"] for m in self.metrics_buffer]
        citations = [m["has_citation"] for m in self.metrics_buffer]
        hallucinations = [m["possible_hallucination"] for m in self.metrics_buffer]
        
        report["metrics"]["avg_latency"] = sum(latencies) / len(latencies)
        report["metrics"]["p95_latency"] = sorted(latencies)[int(len(latencies) * 0.95)]
        report["metrics"]["success_rate"] = sum(successes) / len(successes)
        report["metrics"]["citation_rate"] = sum(citations) / len(citations)
        report["metrics"]["hallucination_rate"] = sum(hallucinations) / len(hallucinations)
        
        # User feedback analysis
        positive_feedback = sum(
            1 for m in self.metrics_buffer
            if m.get("user_feedback") == "positive"
        )
        total_feedback = sum(
            1 for m in self.metrics_buffer
            if m.get("user_feedback") is not None
        )
        
        if total_feedback > 0:
            report["metrics"]["user_satisfaction"] = positive_feedback / total_feedback
        
        # Save report
        self._save_report(report)
        
        # Clear buffer
        self.metrics_buffer = []
    
    def _save_report(self, report: Dict):
        """Save report to file/database"""
        filename = f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"logs/quality_reports/{filename}", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Quality report saved: {filename}")
        print(f"Avg Latency: {report['metrics']['avg_latency']:.2f}s")
        print(f"Success Rate: {report['metrics']['success_rate']:.1%}")
        print(f"Hallucination Rate: {report['metrics']['hallucination_rate']:.1%}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get alerts from last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > cutoff
        ]
        
        return recent_alerts


# Usage in production
monitor = ProductionMonitor()

# In your query endpoint
@app.post("/query")
async def query_documents(query: ChatQuery):
    start_time = time.time()
    
    try:
        # Process query
        result = await rag_engine.query(
            question=query.question,
            user_id=query.user_id
        )
        
        latency = time.time() - start_time
        
        # Log for monitoring
        monitor.log_interaction(
            question=query.question,
            context=result.get("context", ""),
            response=result["answer"],
            latency=latency,
            success=True,
            user_feedback=None  # Will be updated when user provides feedback
        )
        
        return result
        
    except Exception as e:
        latency = time.time() - start_time
        
        monitor.log_interaction(
            question=query.question,
            context="",
            response=str(e),
            latency=latency,
            success=False
        )
        
        raise

# Check alerts
recent_alerts = monitor.get_recent_alerts(hours=24)
if recent_alerts:
    print(f"⚠️ {len(recent_alerts)} alerts in the last 24 hours")
```

---

## 💡 5. Pro Tips from a Senior AI Architect

### Tip #1: Build a Golden Test Set

```python
# File: utils/evaluation/golden_testset.py

GOLDEN_TESTSET = [
    {
        "id": "simple_fact_1",
        "difficulty": "easy",
        "question": "What was the Q3 2024 revenue?",
        "contexts": [
            "Q3 2024 revenue was $4.2M [report.pdf, p.3]"
        ],
        "ground_truth": "Q3 2024 revenue was $4.2 million.",
        "expected_citations": ["report.pdf, p.3"],
        "quality_criteria": {
            "must_include": ["$4.2", "Q3 2024"],
            "must_cite": True,
            "max_words": 50
        }
    },
    {
        "id": "calculation_1",
        "difficulty": "medium",
        "question": "What's the revenue growth rate from Q2 to Q3 2024?",
        "contexts": [
            "Q2 2024 revenue: $3.8M [report.pdf, p.2]",
            "Q3 2024 revenue: $4.2M [report.pdf, p.3]"
        ],
        "ground_truth": "Revenue grew by 10.53% from Q2 to Q3 2024.",
        "expected_calculation": "((4.2 - 3.8) / 3.8) * 100 = 10.53",
        "quality_criteria": {
            "must_include": ["10.53%", "growth"],
            "must_show_calculation": True,
            "must_cite": True
        }
    },
    {
        "id": "comparison_1",
        "difficulty": "hard",
        "question": "Compare pricing strategies across proposals A, B, and C",
        "contexts": [
            "Proposal A: Tiered pricing with 3 tiers [proposal_a.pdf, p.5]",
            "Proposal B: Flat rate per user at $50/month [proposal_b.pdf, p.3]",
            "Proposal C: Usage-based pricing [proposal_c.pdf, p.7]"
        ],
        "ground_truth": "Proposal A uses tiered pricing, B uses flat rate ($50/user/month), C uses usage-based.",
        "quality_criteria": {
            "must_include": ["tiered", "flat rate", "usage-based"],
            "must_compare_all_three": True,
            "must_cite": True,
            "min_words": 100
        }
    },
    # ... 50+ more test cases covering:
    # - Simple facts
    # - Calculations
    # - Comparisons
    # - Summaries
    # - Multi-document analysis
    # - Edge cases (no answer, ambiguous, contradictory)
]

# Test against golden set regularly
def run_golden_test():
    """Test system against golden test set"""
    results = []
    
    for test_case in GOLDEN_TESTSET:
        response = rag_system.query(test_case["question"])
        
        # Evaluate
        passed = check_quality_criteria(response, test_case["quality_criteria"])
        
        results.append({
            "test_id": test_case["id"],
            "passed": passed,
            "response": response
        })
    
    pass_rate = sum(r["passed"] for r in results) / len(results)
    
    return pass_rate

# Run on every deployment
pass_rate = run_golden_test()
if pass_rate < 0.90:
    print(f"⚠️ FAIL: Golden test pass rate {pass_rate:.1%} < 90%")
    sys.exit(1)
```

### Tip #2: Regression Testing

```python
# File: utils/evaluation/regression_testing.py

class RegressionTester:
    """Detect quality regressions before deployment"""
    
    def __init__(self):
        self.baseline_results = self._load_baseline()
    
    def test_for_regression(
        self,
        new_system,
        test_cases: List[Dict],
        threshold: float = 0.05
    ) -> Dict:
        """
        Test if new version regresses on quality
        
        threshold: Allow 5% degradation before failing
        """
        # Test new system
        new_results = self._evaluate_system(new_system, test_cases)
        
        # Compare to baseline
        regression_detected = False
        regressions = []
        
        for metric, new_score in new_results.items():
            baseline_score = self.baseline_results.get(metric, 0)
            
            degradation = baseline_score - new_score
            
            if degradation > threshold:
                regression_detected = True
                regressions.append({
                    "metric": metric,
                    "baseline": baseline_score,
                    "new": new_score,
                    "degradation": degradation
                })
        
        return {
            "regression_detected": regression_detected,
            "regressions": regressions,
            "new_results": new_results,
            "baseline_results": self.baseline_results
        }
    
    def update_baseline(self, new_results: Dict):
        """Update baseline after verified improvement"""
        self.baseline_results = new_results
        self._save_baseline(new_results)
```

### Tip #3: User Feedback Loop

```python
# File: api/routers/feedback.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class UserFeedback(BaseModel):
    interaction_id: str
    rating: int  # 1-5 stars
    feedback_text: str = None
    issue_type: str = None  # "incorrect", "incomplete", "unclear", "hallucination"

@router.post("/feedback")
async def submit_feedback(feedback: UserFeedback):
    """Collect user feedback for evaluation"""
    
    # Store feedback
    await db.store_feedback(feedback)
    
    # If negative feedback, flag for review
    if feedback.rating <= 2:
        await monitoring.flag_for_review(
            interaction_id=feedback.interaction_id,
            issue_type=feedback.issue_type,
            priority="high"
        )
    
    # Update metrics
    await metrics.update_user_satisfaction(feedback.rating)
    
    return {"status": "success", "message": "Thank you for your feedback!"}


# In your frontend
"""
After showing AI response, add feedback widget:

Was this answer helpful?
⭐⭐⭐⭐⭐ (1-5 stars)

If low rating:
What was the problem?
[ ] Incorrect information
[ ] Incomplete answer
[ ] Unclear explanation
[ ] Answer not from documents (hallucination)

[Submit Feedback]
"""
```

---

## 🎓 Key Takeaways

✅ **LLM-as-a-Judge**
- Use powerful LLM to evaluate outputs
- Scales better than human evaluation
- Pairwise comparison for A/B testing
- Track multiple quality dimensions

✅ **RAGAS Framework**
- Specialized for RAG evaluation
- 4 key metrics: Faithfulness, Relevance, Precision, Recall
- Detects retrieval and generation issues
- Create custom metrics for your domain

✅ **Custom Metrics**
- Domain-specific quality criteria
- Citation accuracy
- Numerical correctness
- Source diversity

✅ **Production Monitoring**
- Real-time quality tracking
- Alert on degradation
- User feedback loop
- Regression testing

---

## 🎉 Congratulations!

You've completed the entire **Prompt Engineering & Agentic Workflows** curriculum!

### What You've Mastered:

1. ✅ **Part 1**: CO-STAR & RISEN frameworks
2. ✅ **Part 2**: CoT, ReAct, Self-Reflection
3. ✅ **Part 3**: Tree of Thoughts, Few-Shot, Multi-Agent
4. ✅ **Part 4**: DSPy, Compression, A/B Testing
5. ✅ **Part 5**: LLM-as-Judge, RAGAS, Production Monitoring

### Your Next Steps:

1. **Implement** these techniques in your RAG system
2. **Measure** improvements with evaluation frameworks
3. **Iterate** based on data
4. **Monitor** quality in production
5. **Share** your learnings with the community

---

## 📋 Final Checklist

- [ ] Implement LLM-as-a-Judge evaluation
- [ ] Set up RAGAS metrics
- [ ] Create golden test set (50+ cases)
- [ ] Build production monitoring dashboard
- [ ] Add user feedback mechanism
- [ ] Set up regression testing
- [ ] Establish quality baselines
- [ ] Create alerting for degradation
- [ ] Document evaluation process
- [ ] Train team on evaluation tools

---

## 📚 Additional Resources

### Papers:
- [LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)
- [RAGAS Framework](https://arxiv.org/abs/2309.15217)
- [Evaluation of Text Generation](https://arxiv.org/abs/2303.18802)

### Tools:
- [RAGAS Library](https://github.com/explodinggradients/ragas)
- [LangSmith (Monitoring)](https://smith.langchain.com/)
- [W&B (Tracking)](https://wandb.ai/)

### Communities:
- [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA)
- [AI Stack Exchange](https://ai.stackexchange.com/)
- [LangChain Discord](https://discord.gg/langchain)

---

**🚀 You're now a Senior AI Architect in Prompt Engineering! Go build amazing RAG systems! 🎉**

*For questions or feedback, reach out to the community or create an issue in the repository.*
