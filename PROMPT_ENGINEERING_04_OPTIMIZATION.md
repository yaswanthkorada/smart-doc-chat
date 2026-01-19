# ⚡ Part 4: Prompt Optimization & Compression

## 📚 Chapter Overview

Master cutting-edge optimization techniques including DSPy (programmatic prompt optimization), prompt compression, A/B testing, and performance tuning to reduce costs while maintaining quality.

**Time to Complete:** 10-12 hours  
**Difficulty:** ⭐⭐⭐⭐⭐ Expert  
**Prerequisites:** Parts 1-3 (All previous concepts)

---

## 🎯 Why Prompt Optimization Matters

### The Cost Problem

```python
# Your current system (example)
Monthly Queries: 100,000
Average Prompt Length: 2,000 tokens
Average Response: 500 tokens
Cost per 1M tokens (GPT-4): $30

Monthly Cost = (100,000 × 2,500 tokens / 1,000,000) × $30 = $7,500
Annual Cost = $90,000 💸
```

**What if you could:**
- ✅ Reduce prompt length by 50% → Save $45,000/year
- ✅ Improve accuracy by 15% → Reduce support tickets
- ✅ Decrease latency by 30% → Better user experience

---

## 🔬 1. DSPy: Programmatic Prompt Optimization

### What is DSPy?

**DSPy** (Declarative Self-improving Language Programs) is a framework from Stanford that treats prompts as **optimizable parameters**, like weights in neural networks.

**Key Paper:** [DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines](https://arxiv.org/abs/2310.03714)

### Traditional vs DSPy Approach

**Traditional (Manual):**
```python
# You write the prompt manually
prompt = """
You are a document analyzer. Answer questions accurately.
Use this context: {context}
Question: {question}
"""
# Hope it works well 🤞
```

**DSPy (Automated):**
```python
import dspy

# Define the signature (what you want)
class DocumentQA(dspy.Signature):
    """Answer questions about documents with citations"""
    context = dspy.InputField(desc="Retrieved document chunks")
    question = dspy.InputField(desc="User's question")
    answer = dspy.OutputField(desc="Answer with citations")

# DSPy automatically generates and optimizes the prompt! 🎉
```

### Installing DSPy

```bash
pip install dspy-ai
```

### Basic DSPy Implementation

```python
# File: utils/optimization/dspy_rag.py

import dspy
from typing import List, Dict

# Configure DSPy with your LLM
llm = dspy.OpenAI(
    model="gpt-4",
    api_key="your-api-key",
    max_tokens=500
)
dspy.settings.configure(lm=llm)

# Define signature (input/output specification)
class DocumentAnalyzer(dspy.Signature):
    """Analyze documents and answer questions with proper citations"""
    
    context: str = dspy.InputField(
        desc="Retrieved document chunks with metadata (filename, page)"
    )
    question: str = dspy.InputField(
        desc="User's question about the documents"
    )
    answer: str = dspy.OutputField(
        desc="Detailed answer with citations in format [filename, p.X]"
    )
    confidence: float = dspy.OutputField(
        desc="Confidence score between 0.0 and 1.0"
    )

# Create module using Chain of Thought
class RAGWithCoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_answer = dspy.ChainOfThought(DocumentAnalyzer)
    
    def forward(self, context, question):
        return self.generate_answer(context=context, question=question)

# Create module using ReAct
class RAGWithReAct(dspy.Module):
    def __init__(self, tools):
        super().__init__()
        self.react = dspy.ReAct(DocumentAnalyzer)
        self.tools = tools
    
    def forward(self, question):
        return self.react(
            question=question,
            tools=self.tools
        )

# Usage
rag_cot = RAGWithCoT()

result = rag_cot(
    context="Q3 2024 revenue was $4.2M [report.pdf, p.3]",
    question="What was Q3 revenue?"
)

print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")
```

### DSPy Optimization with Training Data

```python
# File: utils/optimization/dspy_optimizer.py

import dspy
from dspy.teleprompt import BootstrapFewShot, MIPRO
from typing import List, Dict

class DSPyOptimizer:
    """Optimize prompts using DSPy"""
    
    def __init__(self, llm):
        self.llm = llm
        dspy.settings.configure(lm=llm)
    
    def optimize_with_bootstrap(
        self,
        module: dspy.Module,
        training_data: List[Dict],
        metric_fn,
        max_bootstrapped_demos: int = 4
    ):
        """
        Optimize using Bootstrap Few-Shot
        
        This finds the best few-shot examples automatically!
        """
        # Convert training data to DSPy format
        trainset = [
            dspy.Example(
                context=ex["context"],
                question=ex["question"],
                answer=ex["expected_answer"]
            ).with_inputs("context", "question")
            for ex in training_data
        ]
        
        # Configure optimizer
        optimizer = BootstrapFewShot(
            metric=metric_fn,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=4
        )
        
        # Optimize!
        optimized_module = optimizer.compile(
            module,
            trainset=trainset
        )
        
        return optimized_module
    
    def optimize_with_mipro(
        self,
        module: dspy.Module,
        training_data: List[Dict],
        validation_data: List[Dict],
        metric_fn,
        num_candidates: int = 10
    ):
        """
        Optimize using MIPRO (Multi-prompt Instruction Proposal)
        
        This generates and tests multiple prompt variations!
        """
        # Prepare datasets
        trainset = self._prepare_dataset(training_data)
        valset = self._prepare_dataset(validation_data)
        
        # Configure MIPRO optimizer
        optimizer = MIPRO(
            metric=metric_fn,
            num_candidates=num_candidates,
            init_temperature=1.0
        )
        
        # Optimize with multiple iterations
        optimized_module = optimizer.compile(
            module,
            trainset=trainset,
            valset=valset,
            requires_permission_to_run=False
        )
        
        return optimized_module
    
    def _prepare_dataset(self, data: List[Dict]) -> List[dspy.Example]:
        """Convert data to DSPy format"""
        return [
            dspy.Example(
                context=ex["context"],
                question=ex["question"],
                answer=ex.get("expected_answer", ex.get("answer"))
            ).with_inputs("context", "question")
            for ex in data
        ]


# Define metric function
def accuracy_metric(example, prediction, trace=None):
    """
    Evaluate prediction accuracy
    """
    # Simple exact match
    if prediction.answer.strip().lower() == example.answer.strip().lower():
        return 1.0
    
    # Partial credit for similar answers
    similarity = calculate_similarity(prediction.answer, example.answer)
    return similarity


# Training data
training_data = [
    {
        "context": "Q3 2024 revenue was $4.2M [report.pdf, p.3]",
        "question": "What was Q3 revenue?",
        "expected_answer": "Q3 revenue was $4.2 million. [Source: report.pdf, page 3]"
    },
    {
        "context": "Q2: $3.8M, Q3: $4.2M [report.pdf, p.2-3]",
        "question": "What's the revenue growth rate?",
        "expected_answer": "Revenue grew by 10.53% from Q2 ($3.8M) to Q3 ($4.2M). [Source: report.pdf, pages 2-3]"
    },
    # ... 20+ more examples
]

# Optimize
optimizer = DSPyOptimizer(llm=my_llm)

base_module = RAGWithCoT()

optimized_module = optimizer.optimize_with_bootstrap(
    module=base_module,
    training_data=training_data,
    metric_fn=accuracy_metric,
    max_bootstrapped_demos=4
)

# Test optimized version
result = optimized_module(
    context="Q4 revenue: $5.1M [report.pdf, p.4]",
    question="What was Q4 revenue?"
)

print(f"Optimized Answer: {result.answer}")
```

### DSPy Assertion-based Validation

```python
# File: utils/optimization/dspy_assertions.py

import dspy
from dspy.primitives.assertions import assert_transform_module, backtrack_handler

class ValidatedDocumentQA(dspy.Module):
    """Document QA with built-in validation"""
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(DocumentAnalyzer)
    
    def forward(self, context, question):
        # Generate answer
        result = self.generate(context=context, question=question)
        
        # Assertion 1: Answer must contain citation
        dspy.Assert(
            self._has_citation(result.answer),
            "Answer must include source citation in format [filename, p.X]"
        )
        
        # Assertion 2: Confidence must be reasonable
        dspy.Assert(
            0.0 <= result.confidence <= 1.0,
            f"Confidence must be between 0 and 1, got {result.confidence}"
        )
        
        # Assertion 3: No hallucination (info must be in context)
        dspy.Suggest(
            self._verify_answer_in_context(result.answer, context),
            "Answer may contain information not in context",
            target_module=self.generate
        )
        
        return result
    
    def _has_citation(self, answer: str) -> bool:
        """Check if answer has proper citation"""
        import re
        citation_pattern = r'\[.*?\.(?:pdf|docx|txt),\s*p\.\d+\]'
        return bool(re.search(citation_pattern, answer))
    
    def _verify_answer_in_context(self, answer: str, context: str) -> bool:
        """Check if answer facts are in context"""
        # Extract key facts from answer (simplified)
        answer_words = set(answer.lower().split())
        context_words = set(context.lower().split())
        
        # At least 70% of answer words should be in context
        overlap = len(answer_words & context_words)
        return overlap / len(answer_words) >= 0.7


# Wrap module with assertion handling
validated_qa = assert_transform_module(
    ValidatedDocumentQA(),
    backtrack_handler
)

# Now assertions are enforced!
result = validated_qa(
    context="Q3 revenue: $4.2M [report.pdf, p.3]",
    question="What was Q3 revenue?"
)
```

---

## 🗜️ 2. Prompt Compression Techniques

### Why Compress Prompts?

**Benefits:**
- 💰 **Cost Savings:** 40-60% reduction in token usage
- ⚡ **Faster Response:** Less tokens = faster generation
- 📈 **Scale More:** Handle more queries with same budget

### Technique 1: Instruction Compression

**Before (Verbose):**
```python
prompt = """
You are a highly skilled document analysis expert with years of experience in 
extracting information from complex business documents. Your primary responsibility 
is to carefully read through the provided context and answer user questions with 
exceptional accuracy. You must always cite your sources properly using the format 
[filename, page number]. Never make up information that isn't present in the 
documents. If you're uncertain about something, you should acknowledge that 
uncertainty rather than guessing. Make sure your answers are clear, concise, 
and directly address what the user is asking about.

Context: {context}
Question: {question}

Please provide your answer below:
"""
# Token count: ~150 tokens
```

**After (Compressed):**
```python
prompt = """
Document analyzer. Answer questions using context. Format: [file, p.X]. Only use provided info.

Context: {context}
Q: {question}
A:
"""
# Token count: ~25 tokens (83% reduction!)
```

### Technique 2: Context Compression

```python
# File: utils/optimization/context_compressor.py

from typing import List, Dict
import re

class ContextCompressor:
    """Compress retrieved context while preserving key information"""
    
    def compress_chunks(
        self,
        chunks: List[Dict],
        max_tokens: int = 2000,
        strategy: str = "extractive"
    ) -> str:
        """
        Compress multiple chunks to fit token limit
        
        Strategies:
        - extractive: Keep most relevant sentences
        - abstractive: Summarize with LLM
        - hybrid: Combine both
        """
        if strategy == "extractive":
            return self._extractive_compression(chunks, max_tokens)
        elif strategy == "abstractive":
            return self._abstractive_compression(chunks, max_tokens)
        else:
            return self._hybrid_compression(chunks, max_tokens)
    
    def _extractive_compression(
        self,
        chunks: List[Dict],
        max_tokens: int
    ) -> str:
        """Keep most important sentences"""
        
        # Score sentences by importance
        scored_sentences = []
        for chunk in chunks:
            sentences = self._split_sentences(chunk["content"])
            for sentence in sentences:
                score = self._calculate_importance(
                    sentence,
                    chunk.get("relevance_score", 0.5)
                )
                scored_sentences.append((score, sentence, chunk["metadata"]))
        
        # Sort by importance
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        # Take top sentences until token limit
        compressed = []
        current_tokens = 0
        
        for score, sentence, metadata in scored_sentences:
            sentence_tokens = self._count_tokens(sentence)
            if current_tokens + sentence_tokens > max_tokens:
                break
            
            compressed.append({
                "text": sentence,
                "source": f"[{metadata['filename']}, p.{metadata['page']}]"
            })
            current_tokens += sentence_tokens
        
        # Format compressed context
        return self._format_compressed(compressed)
    
    def _abstractive_compression(
        self,
        chunks: List[Dict],
        max_tokens: int
    ) -> str:
        """Summarize using LLM"""
        
        # Combine all chunks
        full_context = "\n\n".join([
            f"{chunk['content']} [{chunk['metadata']['filename']}, p.{chunk['metadata']['page']}]"
            for chunk in chunks
        ])
        
        # Compression prompt
        compression_prompt = f"""
Compress this context to {max_tokens} tokens while preserving:
1. Key facts and figures
2. Source citations
3. Critical details

Context:
{full_context}

Compressed version:
"""
        
        compressed = self.llm.generate(compression_prompt)
        return compressed
    
    def _hybrid_compression(
        self,
        chunks: List[Dict],
        max_tokens: int
    ) -> str:
        """
        Combine extractive and abstractive
        
        1. Extract most relevant sentences (70% of budget)
        2. Summarize remaining content (30% of budget)
        """
        extractive_budget = int(max_tokens * 0.7)
        abstractive_budget = max_tokens - extractive_budget
        
        # Get top sentences
        key_sentences = self._extractive_compression(chunks, extractive_budget)
        
        # Summarize the rest
        remaining_chunks = self._get_remaining_content(chunks, key_sentences)
        if remaining_chunks:
            summary = self._abstractive_compression(
                remaining_chunks,
                abstractive_budget
            )
            return f"{key_sentences}\n\nAdditional context: {summary}"
        
        return key_sentences
    
    def _calculate_importance(self, sentence: str, relevance: float) -> float:
        """Score sentence importance"""
        # Heuristics:
        # 1. Contains numbers (likely important facts)
        # 2. Length (too short/long are less important)
        # 3. Relevance score from retrieval
        
        has_numbers = bool(re.search(r'\d', sentence))
        word_count = len(sentence.split())
        
        score = relevance * 0.6
        score += 0.2 if has_numbers else 0
        score += 0.2 if 10 <= word_count <= 30 else 0
        
        return score
    
    def _count_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        return re.split(r'[.!?]+', text)
    
    def _format_compressed(self, sentences: List[Dict]) -> str:
        """Format compressed sentences"""
        formatted = []
        for sent in sentences:
            formatted.append(f"{sent['text']} {sent['source']}")
        return "\n".join(formatted)


# Usage
compressor = ContextCompressor()

# Original context: 5000 tokens
retrieved_chunks = [...]  # Your retrieved chunks

# Compressed context: 2000 tokens (60% reduction)
compressed_context = compressor.compress_chunks(
    chunks=retrieved_chunks,
    max_tokens=2000,
    strategy="hybrid"
)

print(f"Original tokens: 5000")
print(f"Compressed tokens: {len(compressed_context) // 4}")
print(f"Savings: {(1 - len(compressed_context)/20000) * 100:.1f}%")
```

### Technique 3: Smart Truncation

```python
# File: utils/optimization/smart_truncator.py

class SmartTruncator:
    """Intelligently truncate prompts to fit context windows"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
    
    def truncate_prompt(
        self,
        system_prompt: str,
        context: str,
        question: str,
        preserve_priority: List[str] = ["question", "system_prompt", "context"]
    ) -> Dict[str, str]:
        """
        Truncate components to fit context window
        
        Priority order determines what to keep first
        """
        components = {
            "system_prompt": system_prompt,
            "context": context,
            "question": question
        }
        
        # Count tokens
        token_counts = {
            name: self._count_tokens(text)
            for name, text in components.items()
        }
        
        total_tokens = sum(token_counts.values())
        
        # If fits, return as-is
        if total_tokens <= self.max_tokens:
            return components
        
        # Need truncation
        available_tokens = self.max_tokens
        truncated = {}
        
        # Allocate tokens by priority
        for component_name in preserve_priority:
            component_text = components[component_name]
            component_tokens = token_counts[component_name]
            
            if component_tokens <= available_tokens:
                # Keep full component
                truncated[component_name] = component_text
                available_tokens -= component_tokens
            else:
                # Truncate this component
                if component_name == "context":
                    # Special handling for context (keep most relevant)
                    truncated[component_name] = self._truncate_context(
                        component_text,
                        available_tokens
                    )
                else:
                    # Simple truncation for other components
                    truncated[component_name] = self._truncate_text(
                        component_text,
                        available_tokens
                    )
                available_tokens = 0
                break
        
        return truncated
    
    def _truncate_context(self, context: str, max_tokens: int) -> str:
        """Truncate context preserving most important parts"""
        sentences = context.split('. ')
        
        # Keep sentences with numbers (likely important)
        priority_sentences = [s for s in sentences if re.search(r'\d', s)]
        other_sentences = [s for s in sentences if not re.search(r'\d', s)]
        
        # Start with priority sentences
        result = []
        current_tokens = 0
        
        for sentence in priority_sentences + other_sentences:
            sentence_tokens = self._count_tokens(sentence)
            if current_tokens + sentence_tokens > max_tokens:
                break
            result.append(sentence)
            current_tokens += sentence_tokens
        
        truncated = '. '.join(result)
        if not truncated.endswith('.'):
            truncated += '...'
        
        return truncated
    
    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """Simple text truncation"""
        words = text.split()
        target_words = max_tokens  # Rough estimate
        
        if len(words) <= target_words:
            return text
        
        return ' '.join(words[:target_words]) + '...'
    
    def _count_tokens(self, text: str) -> int:
        """Estimate tokens"""
        return len(text) // 4


# Usage
truncator = SmartTruncator(max_tokens=4000)

truncated_prompt = truncator.truncate_prompt(
    system_prompt=long_system_prompt,
    context=retrieved_context,  # 6000 tokens
    question=user_question,
    preserve_priority=["question", "system_prompt", "context"]
)

print(f"Truncated context: {len(truncated_prompt['context'])} chars")
```

---

## 📊 3. A/B Testing Framework

### Setting Up Prompt A/B Tests

```python
# File: utils/evaluation/ab_testing.py

from typing import List, Dict, Callable
import random
from datetime import datetime
import json

class PromptABTest:
    """A/B test different prompt versions"""
    
    def __init__(self, variants: Dict[str, str]):
        """
        variants: {"variant_a": prompt_a, "variant_b": prompt_b}
        """
        self.variants = variants
        self.results = {name: [] for name in variants.keys()}
    
    def run_test(
        self,
        test_queries: List[Dict],
        evaluation_metric: Callable,
        runs_per_variant: int = 100
    ) -> Dict:
        """
        Run A/B test on sample queries
        """
        print(f"Starting A/B test with {len(self.variants)} variants")
        print(f"Test queries: {len(test_queries)}")
        print(f"Runs per variant: {runs_per_variant}")
        
        # Test each variant
        for variant_name, prompt_template in self.variants.items():
            print(f"\nTesting variant: {variant_name}")
            
            variant_scores = []
            variant_times = []
            
            for i in range(runs_per_variant):
                # Random query
                query_data = random.choice(test_queries)
                
                # Format prompt
                prompt = prompt_template.format(**query_data["input"])
                
                # Execute
                start_time = datetime.now()
                response = self.llm.generate(prompt)
                end_time = datetime.now()
                
                # Evaluate
                score = evaluation_metric(
                    response,
                    query_data.get("expected_output")
                )
                
                # Track metrics
                variant_scores.append(score)
                variant_times.append((end_time - start_time).total_seconds())
                
                # Store result
                self.results[variant_name].append({
                    "query": query_data["input"],
                    "response": response,
                    "score": score,
                    "time_seconds": variant_times[-1]
                })
            
            # Variant summary
            avg_score = sum(variant_scores) / len(variant_scores)
            avg_time = sum(variant_times) / len(variant_times)
            
            print(f"  Avg Score: {avg_score:.3f}")
            print(f"  Avg Time: {avg_time:.2f}s")
        
        # Statistical analysis
        analysis = self._analyze_results()
        
        return analysis
    
    def _analyze_results(self) -> Dict:
        """Perform statistical analysis"""
        summary = {}
        
        for variant_name, results in self.results.items():
            scores = [r["score"] for r in results]
            times = [r["time_seconds"] for r in results]
            
            summary[variant_name] = {
                "mean_score": sum(scores) / len(scores),
                "median_score": sorted(scores)[len(scores) // 2],
                "min_score": min(scores),
                "max_score": max(scores),
                "std_dev": self._std_dev(scores),
                "mean_time": sum(times) / len(times),
                "total_runs": len(results)
            }
        
        # Determine winner
        best_variant = max(
            summary.items(),
            key=lambda x: x[1]["mean_score"]
        )
        
        summary["winner"] = {
            "variant": best_variant[0],
            "score": best_variant[1]["mean_score"]
        }
        
        # Statistical significance
        summary["statistical_significance"] = self._check_significance()
        
        return summary
    
    def _std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _check_significance(self) -> Dict:
        """Check if results are statistically significant"""
        # Simplified t-test
        variant_names = list(self.variants.keys())
        if len(variant_names) != 2:
            return {"test": "skipped", "reason": "Only works for 2 variants"}
        
        scores_a = [r["score"] for r in self.results[variant_names[0]]]
        scores_b = [r["score"] for r in self.results[variant_names[1]]]
        
        mean_a = sum(scores_a) / len(scores_a)
        mean_b = sum(scores_b) / len(scores_b)
        
        # Simple threshold check (p < 0.05 approximation)
        difference = abs(mean_a - mean_b)
        std_a = self._std_dev(scores_a)
        std_b = self._std_dev(scores_b)
        
        # If difference > 1.96 * pooled_std, likely significant
        pooled_std = ((std_a ** 2 + std_b ** 2) / 2) ** 0.5
        threshold = 1.96 * pooled_std / (len(scores_a) ** 0.5)
        
        is_significant = difference > threshold
        
        return {
            "test": "t-test (approximate)",
            "significant": is_significant,
            "difference": difference,
            "threshold": threshold,
            "confidence": "95%" if is_significant else "< 95%"
        }
    
    def export_results(self, filepath: str):
        """Export results to JSON"""
        with open(filepath, 'w') as f:
            json.dump({
                "variants": list(self.variants.keys()),
                "results": self.results,
                "analysis": self._analyze_results()
            }, f, indent=2)


# Usage Example
variant_a = """
You are a document analyzer. Answer questions accurately with citations.

Context: {context}
Question: {question}

Answer:
"""

variant_b = """
Document QA Agent. Cite sources [file, p.X]. Use only provided context.

Context: {context}
Q: {question}
A:
"""

test = PromptABTest({
    "verbose": variant_a,
    "compressed": variant_b
})

def accuracy_metric(response, expected):
    """Simple accuracy metric"""
    # Check if key facts are present
    return 1.0 if expected in response else 0.0

test_queries = [
    {
        "input": {"context": "...", "question": "..."},
        "expected_output": "..."
    },
    # ... more test queries
]

results = test.run_test(
    test_queries=test_queries,
    evaluation_metric=accuracy_metric,
    runs_per_variant=50
)

print(f"\nWinner: {results['winner']['variant']}")
print(f"Score: {results['winner']['score']:.3f}")
print(f"Significant: {results['statistical_significance']['significant']}")

# Export for analysis
test.export_results("ab_test_results.json")
```

---

## ⚡ 4. Performance Tuning

### Latency Optimization

```python
# File: utils/optimization/performance_tuner.py

import asyncio
import time
from typing import List, Dict

class PerformanceTuner:
    """Optimize prompt performance"""
    
    def __init__(self):
        self.metrics = []
    
    async def benchmark_prompt(
        self,
        prompt: str,
        num_runs: int = 10
    ) -> Dict:
        """Benchmark prompt performance"""
        
        latencies = []
        token_counts = []
        
        for i in range(num_runs):
            start = time.time()
            
            response = await self.llm.generate(prompt)
            
            end = time.time()
            latency = end - start
            
            latencies.append(latency)
            token_counts.append(self._count_tokens(response))
        
        return {
            "avg_latency": sum(latencies) / len(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "p95_latency": sorted(latencies)[int(len(latencies) * 0.95)],
            "avg_tokens": sum(token_counts) / len(token_counts),
            "total_runs": num_runs
        }
    
    async def optimize_batch_size(
        self,
        prompts: List[str],
        batch_sizes: List[int] = [1, 5, 10, 20]
    ) -> Dict:
        """Find optimal batch size for parallel processing"""
        
        results = {}
        
        for batch_size in batch_sizes:
            print(f"Testing batch size: {batch_size}")
            
            start = time.time()
            
            # Process in batches
            for i in range(0, len(prompts), batch_size):
                batch = prompts[i:i + batch_size]
                
                # Parallel execution
                await asyncio.gather(*[
                    self.llm.generate(prompt)
                    for prompt in batch
                ])
            
            end = time.time()
            total_time = end - start
            
            results[batch_size] = {
                "total_time": total_time,
                "throughput": len(prompts) / total_time,
                "avg_time_per_prompt": total_time / len(prompts)
            }
        
        # Find optimal
        optimal = max(results.items(), key=lambda x: x[1]["throughput"])
        
        return {
            "results": results,
            "optimal_batch_size": optimal[0],
            "optimal_throughput": optimal[1]["throughput"]
        }


# Usage
tuner = PerformanceTuner()

# Benchmark current prompt
benchmark = await tuner.benchmark_prompt(
    prompt=my_prompt,
    num_runs=10
)

print(f"Avg Latency: {benchmark['avg_latency']:.3f}s")
print(f"P95 Latency: {benchmark['p95_latency']:.3f}s")

# Find optimal batch size
batch_results = await tuner.optimize_batch_size(
    prompts=test_prompts,
    batch_sizes=[1, 5, 10, 20, 50]
)

print(f"Optimal batch size: {batch_results['optimal_batch_size']}")
print(f"Throughput: {batch_results['optimal_throughput']:.1f} prompts/sec")
```

---

## 💡 5. Pro Tips from a Senior AI Architect

### Tip #1: The 80/20 Rule for Compression

```python
# Focus compression efforts where they matter most

def analyze_prompt_composition(prompt: str) -> Dict:
    """Find where to compress"""
    
    components = {
        "system_instructions": extract_system_instructions(prompt),
        "examples": extract_examples(prompt),
        "context": extract_context(prompt),
        "question": extract_question(prompt)
    }
    
    token_usage = {
        name: count_tokens(text)
        for name, text in components.items()
    }
    
    total_tokens = sum(token_usage.values())
    
    # Find biggest contributors
    breakdown = {
        name: {
            "tokens": tokens,
            "percentage": (tokens / total_tokens) * 100
        }
        for name, tokens in token_usage.items()
    }
    
    # Recommend compression targets
    recommendations = []
    for name, stats in breakdown.items():
        if stats["percentage"] > 30:
            recommendations.append(f"⚠️ {name} uses {stats['percentage']:.1f}% of tokens - compress first!")
    
    return {
        "breakdown": breakdown,
        "recommendations": recommendations
    }

# Result might show:
# Context: 60% → Compress this first!
# System Instructions: 25% → Compress second
# Examples: 10% → Less critical
# Question: 5% → Leave as-is
```

### Tip #2: Gradual Compression Testing

```python
# Don't compress everything at once - test incrementally

compression_levels = [
    {"name": "baseline", "compression": 0},
    {"name": "light", "compression": 0.2},
    {"name": "medium", "compression": 0.4},
    {"name": "aggressive", "compression": 0.6}
]

results = []

for level in compression_levels:
    compressed_prompt = compressor.compress(
        original_prompt,
        reduction=level["compression"]
    )
    
    accuracy = test_accuracy(compressed_prompt)
    cost = calculate_cost(compressed_prompt)
    
    results.append({
        "level": level["name"],
        "accuracy": accuracy,
        "cost": cost,
        "cost_savings": 1 - (cost / baseline_cost)
    })
    
    # Stop if accuracy drops > 5%
    if accuracy < baseline_accuracy - 0.05:
        print(f"⚠️ Stopped at {level['name']} - accuracy dropped too much")
        break

# Find sweet spot
best_balance = max(
    results,
    key=lambda x: x["accuracy"] * (1 + x["cost_savings"])
)
```

---

## 🎓 Key Takeaways

✅ **DSPy**
- Automates prompt optimization
- Treats prompts as learnable parameters
- Bootstrap & MIPRO optimizers
- Assertion-based validation

✅ **Compression**
- 40-60% token reduction possible
- Extractive vs abstractive strategies
- Smart truncation preserves important info
- Test gradually to maintain quality

✅ **A/B Testing**
- Scientifically compare prompt versions
- Statistical significance matters
- Track latency and accuracy
- Iterate based on data

✅ **Performance Tuning**
- Benchmark before optimizing
- Find optimal batch sizes
- Monitor P95 latency
- Balance cost vs quality

---

## 🚀 What's Next?

Final part coming up:

👉 **Part 5**: [Evaluation & Metrics](PROMPT_ENGINEERING_05_EVALUATION.md)
- LLM-as-a-Judge
- RAGAS evaluation
- Custom metrics
- Production monitoring

---

## 📋 Checklist

- [ ] Understand DSPy framework
- [ ] Implement DSPy optimization
- [ ] Set up context compression
- [ ] Build A/B testing framework
- [ ] Benchmark current prompts
- [ ] Compress prompts by 40%+
- [ ] Find optimal batch size
- [ ] Deploy optimized prompts
- [ ] Monitor performance metrics

---

**Congratulations! You're now a prompt optimization expert! ⚡💰**

*Next: [Part 5 - Evaluation & Metrics](PROMPT_ENGINEERING_05_EVALUATION.md)*
