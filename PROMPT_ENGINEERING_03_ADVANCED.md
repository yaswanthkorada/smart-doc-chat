# 🌳 Part 3: Advanced Strategies

## 📚 Chapter Overview

Master cutting-edge prompting techniques including Tree of Thoughts (ToT), Few-Shot Learning, Meta-prompting, and Multi-Agent orchestration for complex reasoning tasks.

**Time to Complete:** 12-15 hours  
**Difficulty:** ⭐⭐⭐⭐⭐ Expert  
**Prerequisites:** Parts 1-2 (Frameworks & Reasoning)

---

## 🌲 1. Tree of Thoughts (ToT)

### What is Tree of Thoughts?

**Definition:** An advanced prompting framework that explores multiple reasoning paths simultaneously, like a decision tree, and selects the best solution.

**Invented by:** Yao et al. (Princeton/Google DeepMind, 2023)  
**Key Paper:** [Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601)

### The Core Concept

Instead of following ONE chain of thought, explore MANY parallel thoughts and pick the best one.

```
Chain-of-Thought (Linear):
Question → Step 1 → Step 2 → Step 3 → Answer

Tree of Thoughts (Branching):
                    ┌─ Path A → Step A2 → Step A3 → Answer A
Question → Step 1 ──┼─ Path B → Step B2 → Step B3 → Answer B ✓ (Best!)
                    └─ Path C → Step C2 → Step C3 → Answer C
```

### When to Use ToT

✅ **Best For:**
- Complex strategic planning
- Multi-step optimization problems
- When multiple valid approaches exist
- High-stakes decisions requiring exploration

❌ **Not For:**
- Simple factual questions
- Real-time responses (ToT is slow)
- Budget-constrained projects (expensive)

### ToT Template

```python
# File: utils/prompts/tot_templates.py

TREE_OF_THOUGHTS_TEMPLATE = """
You are an expert problem solver using Tree of Thoughts methodology.

# TREE OF THOUGHTS PROTOCOL

## Phase 1: DECOMPOSE THE PROBLEM
Break down the complex question into key decision points.

## Phase 2: GENERATE THOUGHT BRANCHES
For each decision point, generate 3-5 different approaches.

## Phase 3: EVALUATE EACH BRANCH
Score each approach (0.0 to 1.0) based on:
- Feasibility
- Completeness
- Accuracy potential
- Resource efficiency

## Phase 4: PRUNE WEAK BRANCHES
Eliminate approaches with score < 0.6

## Phase 5: EXPAND PROMISING BRANCHES
Develop the top 2-3 approaches in detail

## Phase 6: SELECT BEST PATH
Choose the highest-scoring complete solution

# OUTPUT FORMAT

```json
{
  "problem_decomposition": {
    "main_question": "...",
    "decision_points": ["Decision 1", "Decision 2", "Decision 3"]
  },
  "thought_tree": {
    "decision_point_1": {
      "branch_a": {
        "approach": "...",
        "reasoning": "...",
        "score": 0.85,
        "pros": ["..."],
        "cons": ["..."]
      },
      "branch_b": {
        "approach": "...",
        "reasoning": "...",
        "score": 0.72,
        "pros": ["..."],
        "cons": ["..."]
      },
      "branch_c": {
        "approach": "...",
        "reasoning": "...",
        "score": 0.91,
        "pros": ["..."],
        "cons": ["..."]
      }
    }
  },
  "pruning_decisions": {
    "kept": ["branch_a", "branch_c"],
    "eliminated": ["branch_b"],
    "reason": "Branch B has lower feasibility score"
  },
  "expanded_paths": {
    "path_1": {
      "branches": ["branch_a → step2a → step3a"],
      "final_score": 0.88,
      "complete_solution": "..."
    },
    "path_2": {
      "branches": ["branch_c → step2c → step3c"],
      "final_score": 0.94,
      "complete_solution": "..."
    }
  },
  "best_solution": {
    "chosen_path": "path_2",
    "confidence": 0.94,
    "reasoning": "Path 2 has highest score and most comprehensive solution",
    "final_answer": "..."
  }
}
```

# EXAMPLE: DOCUMENT SEARCH STRATEGY

Question: "Find all documents mentioning pricing changes in 2024 and analyze their impact on revenue"

## Phase 1: Decompose
Decision Points:
1. How to search for pricing changes?
2. How to identify 2024-specific mentions?
3. How to link pricing to revenue data?

## Phase 2: Generate Branches

### Decision Point 1: Search Strategy
Branch A: Keyword search ("pricing", "price change", "cost adjustment")
- Score: 0.75
- Pro: Fast, simple
- Con: Might miss contextual mentions

Branch B: Semantic search + filtering
- Score: 0.88
- Pro: Catches contextual references
- Con: More computationally expensive

Branch C: Hybrid (keyword + semantic)
- Score: 0.92
- Pro: Best recall and precision
- Con: Most expensive

### Decision Point 2: Date Filtering
Branch A: Metadata-based (filter by upload date)
- Score: 0.70
- Con: Won't find "2024" mentioned in old documents

Branch B: Content-based (search for "2024" in text)
- Score: 0.85
- Pro: Finds mentions regardless of upload date

Branch C: Combined (metadata + content)
- Score: 0.95
- Pro: Most comprehensive

## Phase 3: Evaluate & Prune
Kept: Branch B & C for search, Branch C for date filtering
Eliminated: Branch A (too simplistic)

## Phase 4: Expand Best Path
Path: Hybrid search + Combined date filtering

Steps:
1. Keyword search: "pricing", "price", "cost" → 50 docs
2. Semantic search: "pricing changes" → 35 docs
3. Merge + deduplicate → 65 unique docs
4. Filter: metadata.year = 2024 OR content contains "2024" → 23 docs
5. Secondary search: "revenue" OR "sales" in these 23 docs
6. Cross-reference pricing mentions with revenue data

## Phase 5: Best Solution
Chosen Path: Hybrid search with combined filtering
Confidence: 0.94

Final Answer: "Found 23 documents with pricing changes in 2024. Analysis shows..."
"""
```

### Implementation

```python
# File: utils/agent_rag_engine.py

from typing import List, Dict, Tuple
import asyncio

class TreeOfThoughtsAgent:
    """
    Advanced reasoning agent using Tree of Thoughts
    """
    
    def __init__(self, llm, max_branches: int = 3, max_depth: int = 3):
        self.llm = llm
        self.max_branches = max_branches
        self.max_depth = max_depth
        self.thought_tree = {}
    
    async def solve_with_tot(self, question: str, context: str) -> Dict:
        """
        Solve complex problem using Tree of Thoughts
        """
        # Phase 1: Decompose problem
        decision_points = await self._decompose_problem(question)
        
        # Phase 2-3: Generate and evaluate branches
        thought_tree = await self._build_thought_tree(
            question, 
            context, 
            decision_points
        )
        
        # Phase 4: Prune weak branches
        pruned_tree = self._prune_branches(thought_tree, threshold=0.6)
        
        # Phase 5: Expand promising paths
        expanded_paths = await self._expand_best_paths(
            pruned_tree, 
            context
        )
        
        # Phase 6: Select best solution
        best_solution = self._select_best_solution(expanded_paths)
        
        return {
            "problem_decomposition": decision_points,
            "thought_tree": thought_tree,
            "pruned_tree": pruned_tree,
            "expanded_paths": expanded_paths,
            "best_solution": best_solution,
            "confidence": best_solution["score"]
        }
    
    async def _decompose_problem(self, question: str) -> List[str]:
        """Break down complex question into decision points"""
        prompt = f"""
Analyze this complex question and identify 3-5 key decision points:

Question: {question}

For each decision point, identify:
1. What needs to be decided?
2. What approaches are possible?

Output format:
["Decision point 1", "Decision point 2", ...]
"""
        response = await self.llm.generate(prompt)
        return self._parse_list(response)
    
    async def _build_thought_tree(
        self, 
        question: str, 
        context: str, 
        decision_points: List[str]
    ) -> Dict:
        """Generate and evaluate multiple branches"""
        tree = {}
        
        for dp_idx, decision_point in enumerate(decision_points):
            branches = await self._generate_branches(
                question, 
                context, 
                decision_point
            )
            
            # Evaluate each branch
            evaluated_branches = []
            for branch in branches:
                score = await self._evaluate_branch(branch, context)
                evaluated_branches.append({
                    "approach": branch["approach"],
                    "reasoning": branch["reasoning"],
                    "score": score,
                    "pros": branch.get("pros", []),
                    "cons": branch.get("cons", [])
                })
            
            tree[f"decision_point_{dp_idx + 1}"] = evaluated_branches
        
        return tree
    
    async def _generate_branches(
        self, 
        question: str, 
        context: str, 
        decision_point: str
    ) -> List[Dict]:
        """Generate multiple approaches for a decision point"""
        prompt = f"""
For this decision point, generate {self.max_branches} different approaches:

Question: {question}
Context: {context}
Decision Point: {decision_point}

For each approach, provide:
1. Approach description
2. Reasoning
3. Pros
4. Cons

Output {self.max_branches} distinct approaches.
"""
        response = await self.llm.generate(prompt)
        return self._parse_branches(response)
    
    async def _evaluate_branch(self, branch: Dict, context: str) -> float:
        """Score a branch (0.0 to 1.0)"""
        prompt = f"""
Evaluate this approach on a scale of 0.0 to 1.0:

Approach: {branch['approach']}
Reasoning: {branch['reasoning']}
Context: {context}

Scoring criteria:
- Feasibility (0-0.25)
- Completeness (0-0.25)
- Accuracy potential (0-0.25)
- Resource efficiency (0-0.25)

Return only a number between 0.0 and 1.0.
"""
        response = await self.llm.generate(prompt)
        return float(response.strip())
    
    def _prune_branches(self, tree: Dict, threshold: float) -> Dict:
        """Remove low-scoring branches"""
        pruned = {}
        
        for decision_point, branches in tree.items():
            kept_branches = [
                branch for branch in branches 
                if branch["score"] >= threshold
            ]
            pruned[decision_point] = kept_branches
        
        return pruned
    
    async def _expand_best_paths(self, pruned_tree: Dict, context: str) -> List[Dict]:
        """Develop top branches into complete solutions"""
        paths = []
        
        # Get all combinations of top branches
        top_branches = self._get_top_branch_combinations(pruned_tree)
        
        for branch_combo in top_branches[:3]:  # Expand top 3 paths
            expanded = await self._expand_path(branch_combo, context)
            paths.append(expanded)
        
        return paths
    
    async def _expand_path(self, branches: List[Dict], context: str) -> Dict:
        """Fully develop a path into a complete solution"""
        prompt = f"""
Develop this reasoning path into a complete solution:

Chosen Branches:
{self._format_branches(branches)}

Context: {context}

Provide:
1. Step-by-step execution plan
2. Expected outcomes at each step
3. Complete final answer
4. Confidence score (0.0 to 1.0)
"""
        response = await self.llm.generate(prompt)
        return self._parse_expanded_path(response)
    
    def _select_best_solution(self, expanded_paths: List[Dict]) -> Dict:
        """Choose the highest-scoring complete solution"""
        best = max(expanded_paths, key=lambda x: x.get("score", 0))
        return best


# Usage Example
tot_agent = TreeOfThoughtsAgent(llm=my_llm, max_branches=3, max_depth=3)

result = await tot_agent.solve_with_tot(
    question="Find all pricing changes in 2024 and analyze impact on revenue",
    context=retrieved_documents
)

print(f"Best Solution: {result['best_solution']['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Explored {len(result['thought_tree'])} decision points")
```

### ToT vs Other Methods

| Method | Reasoning Paths | Accuracy | Cost | Speed |
|--------|----------------|----------|------|-------|
| **Basic** | 1 | 70% | $ | Fast |
| **CoT** | 1 (linear) | 80% | $$ | Medium |
| **ReAct** | 1 (with tools) | 85% | $$$ | Medium |
| **ToT** | Multiple (tree) | 90-95% | $$$$ | Slow |

---

## 🎯 2. Few-Shot Learning

### What is Few-Shot Learning?

**Definition:** Teaching the LLM by example - provide 2-10 example inputs/outputs to guide its behavior.

### The Power of Examples

**Zero-Shot (No Examples):**
```
Prompt: "Extract key metrics from this text."
Result: Inconsistent format, misses important data
```

**Few-Shot (With Examples):**
```
Prompt: "Extract key metrics from this text.

Example 1:
Input: 'Q1 revenue was $2.5M with 120 customers'
Output: {'revenue': 2.5, 'customers': 120, 'period': 'Q1'}

Example 2:
Input: 'Q2 sales reached $3.2M, up 15% YoY'
Output: {'revenue': 3.2, 'growth_yoy': 15, 'period': 'Q2'}

Now extract from: 'Q3 revenue hit $4.1M with 200 customers'"
Result: {'revenue': 4.1, 'customers': 200, 'period': 'Q3'} ✓
```

### Few-Shot Template

```python
# File: utils/prompts/few_shot_templates.py

FEW_SHOT_TEMPLATE = """
You are a {role}. Learn from these examples and apply the same pattern.

# TASK DESCRIPTION
{task_description}

# EXAMPLES

{examples}

# YOUR TURN

Input: {input}
Output:
"""

# Example for Document Metadata Extraction
FEW_SHOT_METADATA_EXTRACTION = """
You are a metadata extraction specialist. Learn from these examples:

# TASK: Extract structured metadata from document descriptions

# EXAMPLES

Example 1:
Input: "Financial Report Q3 2024.pdf - uploaded on 2024-11-15, 45 pages, contains revenue analysis"
Output:
{
  "filename": "Financial Report Q3 2024.pdf",
  "upload_date": "2024-11-15",
  "page_count": 45,
  "content_type": "financial_report",
  "period": "Q3 2024",
  "topics": ["revenue", "analysis"]
}

Example 2:
Input: "Marketing Strategy 2025.docx - uploaded 2024-12-01, 23 pages, includes competitor analysis and pricing"
Output:
{
  "filename": "Marketing Strategy 2025.docx",
  "upload_date": "2024-12-01",
  "page_count": 23,
  "content_type": "strategy_document",
  "period": "2025",
  "topics": ["marketing", "competitor_analysis", "pricing"]
}

Example 3:
Input: "Sales Data Jan-Mar.xlsx - uploaded 2024-04-05, 12 sheets, regional breakdown and targets"
Output:
{
  "filename": "Sales Data Jan-Mar.xlsx",
  "upload_date": "2024-04-05",
  "sheet_count": 12,
  "content_type": "data_spreadsheet",
  "period": "Q1",
  "topics": ["sales", "regional_data", "targets"]
}

# YOUR TURN

Input: {new_input}
Output:
"""
```

### Creating Effective Few-Shot Examples

#### 1. Example Selection Strategy

```python
# File: utils/prompts/few_shot_builder.py

class FewShotExampleSelector:
    """Intelligently select examples for few-shot learning"""
    
    def __init__(self, example_bank: List[Dict]):
        self.example_bank = example_bank
    
    def select_examples(
        self, 
        query: str, 
        num_examples: int = 3,
        strategy: str = "semantic_similarity"
    ) -> List[Dict]:
        """
        Select most relevant examples for the query
        
        Strategies:
        - random: Random selection
        - semantic_similarity: Most similar to query
        - diverse: Maximize diversity
        - difficulty: Match complexity level
        """
        if strategy == "random":
            return self._random_selection(num_examples)
        
        elif strategy == "semantic_similarity":
            return self._semantic_selection(query, num_examples)
        
        elif strategy == "diverse":
            return self._diverse_selection(num_examples)
        
        elif strategy == "difficulty":
            return self._difficulty_matched_selection(query, num_examples)
    
    def _semantic_selection(self, query: str, num_examples: int) -> List[Dict]:
        """Select examples most similar to the query"""
        # Calculate semantic similarity between query and each example
        similarities = []
        for example in self.example_bank:
            similarity = self._calculate_similarity(query, example["input"])
            similarities.append((similarity, example))
        
        # Sort by similarity and take top N
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [ex for _, ex in similarities[:num_examples]]
    
    def _diverse_selection(self, num_examples: int) -> List[Dict]:
        """Select diverse examples covering different patterns"""
        selected = []
        remaining = self.example_bank.copy()
        
        # Select first example randomly
        selected.append(remaining.pop(0))
        
        # Select subsequent examples that are most different
        while len(selected) < num_examples and remaining:
            max_min_distance = -1
            best_candidate = None
            
            for candidate in remaining:
                # Find minimum distance to already selected examples
                min_distance = min(
                    self._calculate_distance(candidate, sel)
                    for sel in selected
                )
                
                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_candidate = candidate
            
            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
        
        return selected
    
    def _difficulty_matched_selection(self, query: str, num_examples: int) -> List[Dict]:
        """Select examples matching query complexity"""
        query_difficulty = self._estimate_difficulty(query)
        
        # Find examples with similar difficulty
        matched = []
        for example in self.example_bank:
            ex_difficulty = self._estimate_difficulty(example["input"])
            diff = abs(query_difficulty - ex_difficulty)
            matched.append((diff, example))
        
        # Sort by difficulty match
        matched.sort(key=lambda x: x[0])
        return [ex for _, ex in matched[:num_examples]]
    
    def _estimate_difficulty(self, text: str) -> float:
        """Estimate text complexity (0.0 to 1.0)"""
        # Simple heuristics
        word_count = len(text.split())
        avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)
        comma_count = text.count(',')
        
        # Normalize and combine
        difficulty = (
            min(word_count / 100, 1.0) * 0.4 +
            min(avg_word_length / 10, 1.0) * 0.3 +
            min(comma_count / 10, 1.0) * 0.3
        )
        
        return difficulty


# Usage Example
example_bank = [
    {"input": "Simple revenue question", "output": "...", "difficulty": 0.3},
    {"input": "Complex multi-document comparison...", "output": "...", "difficulty": 0.9},
    # ... more examples
]

selector = FewShotExampleSelector(example_bank)

# Get examples similar to user's query
relevant_examples = selector.select_examples(
    query="Compare Q2 and Q3 revenue across all regions",
    num_examples=3,
    strategy="semantic_similarity"
)
```

#### 2. Few-Shot Prompt Builder

```python
# File: utils/prompts/few_shot_builder.py

class FewShotPromptBuilder:
    """Build few-shot prompts dynamically"""
    
    def __init__(self, example_selector: FewShotExampleSelector):
        self.example_selector = example_selector
    
    def build_prompt(
        self,
        task_description: str,
        input_text: str,
        num_examples: int = 3,
        example_strategy: str = "semantic_similarity"
    ) -> str:
        """Build complete few-shot prompt"""
        
        # Select relevant examples
        examples = self.example_selector.select_examples(
            query=input_text,
            num_examples=num_examples,
            strategy=example_strategy
        )
        
        # Format examples
        formatted_examples = self._format_examples(examples)
        
        # Build prompt
        prompt = f"""
{task_description}

# EXAMPLES (Learn from these)

{formatted_examples}

# YOUR TURN

Input: {input_text}
Output:
"""
        return prompt
    
    def _format_examples(self, examples: List[Dict]) -> str:
        """Format examples in a clear structure"""
        formatted = []
        
        for i, example in enumerate(examples, 1):
            formatted.append(f"""
Example {i}:
Input: {example['input']}
Output: {example['output']}
""")
        
        return "\n".join(formatted)
    
    def build_adaptive_prompt(
        self,
        task_description: str,
        input_text: str,
        previous_attempts: List[Dict] = None
    ) -> str:
        """
        Build adaptive few-shot prompt that learns from mistakes
        """
        # Start with standard examples
        examples = self.example_selector.select_examples(input_text, num_examples=2)
        
        # Add counter-examples if previous attempts failed
        if previous_attempts:
            for attempt in previous_attempts:
                examples.append({
                    "input": attempt["input"],
                    "output_wrong": attempt["output"],
                    "output_correct": attempt["expected"],
                    "explanation": attempt["error_reason"]
                })
        
        # Format with corrections
        formatted_examples = self._format_examples_with_corrections(examples)
        
        prompt = f"""
{task_description}

# EXAMPLES (Learn what to do and what NOT to do)

{formatted_examples}

# YOUR TURN

Input: {input_text}
Output:
"""
        return prompt
    
    def _format_examples_with_corrections(self, examples: List[Dict]) -> str:
        """Format examples showing correct and incorrect patterns"""
        formatted = []
        
        for i, example in enumerate(examples, 1):
            if "output_wrong" in example:
                # Show mistake and correction
                formatted.append(f"""
Example {i} (with correction):
Input: {example['input']}
❌ Wrong: {example['output_wrong']}
✓ Correct: {example['output_correct']}
Reason: {example['explanation']}
""")
            else:
                # Show correct example
                formatted.append(f"""
Example {i}:
Input: {example['input']}
✓ Output: {example['output']}
""")
        
        return "\n".join(formatted)


# Usage in Your RAG System
class FewShotRAGAgent:
    """RAG agent with few-shot learning"""
    
    def __init__(self, llm, example_bank):
        self.llm = llm
        self.example_selector = FewShotExampleSelector(example_bank)
        self.prompt_builder = FewShotPromptBuilder(self.example_selector)
    
    async def query_with_few_shot(self, question: str, context: str) -> str:
        """Answer query using few-shot learning"""
        
        # Build few-shot prompt
        prompt = self.prompt_builder.build_prompt(
            task_description="Answer questions about documents with citations",
            input_text=f"Question: {question}\nContext: {context}",
            num_examples=3,
            example_strategy="semantic_similarity"
        )
        
        # Generate response
        response = await self.llm.generate(prompt)
        
        return response
```

### Few-Shot for Your Document System

```python
# File: utils/prompts/document_few_shot_examples.py

DOCUMENT_QA_EXAMPLES = [
    {
        "input": {
            "question": "What was the Q3 revenue?",
            "context": "Q3 2024 financial results: Revenue reached $4.2M, up from $3.8M in Q2. [report.pdf, p.3]"
        },
        "output": {
            "answer": "Q3 revenue was $4.2 million. [Source: report.pdf, page 3]",
            "confidence": 0.98,
            "reasoning": "Direct fact stated in financial report"
        },
        "difficulty": 0.2
    },
    {
        "input": {
            "question": "Calculate the revenue growth rate from Q2 to Q3",
            "context": "Q3 revenue: $4.2M [report.pdf, p.3]. Q2 revenue: $3.8M [report.pdf, p.2]"
        },
        "output": {
            "answer": "Revenue grew by 10.53% from Q2 to Q3, increasing from $3.8M to $4.2M. [Sources: report.pdf, pages 2-3]",
            "confidence": 0.95,
            "reasoning": "Calculation: ((4.2 - 3.8) / 3.8) × 100 = 10.53%",
            "calculation_shown": true
        },
        "difficulty": 0.5
    },
    {
        "input": {
            "question": "Compare pricing strategies across all proposals",
            "context": "Proposal A: Tiered pricing with 3 tiers [proposal_a.pdf]. Proposal B: Flat rate per user [proposal_b.pdf]. Proposal C: Usage-based pricing [proposal_c.pdf]"
        },
        "output": {
            "answer": """Pricing Strategy Comparison:

**Proposal A (Tiered Pricing):**
- 3 pricing tiers based on features
- Suitable for diverse customer segments
[Source: proposal_a.pdf]

**Proposal B (Flat Rate):**
- Single price per user
- Simple and predictable
[Source: proposal_b.pdf]

**Proposal C (Usage-Based):**
- Pay for what you use
- Scales with customer needs
[Source: proposal_c.pdf]

**Recommendation:** Proposal A offers best flexibility for market segmentation.""",
            "confidence": 0.88,
            "reasoning": "Compared all three proposals across key dimensions",
            "sources": ["proposal_a.pdf", "proposal_b.pdf", "proposal_c.pdf"]
        },
        "difficulty": 0.8
    }
]

# Usage
example_bank = DOCUMENT_QA_EXAMPLES
selector = FewShotExampleSelector(example_bank)
prompt_builder = FewShotPromptBuilder(selector)

# Build prompt for new query
prompt = prompt_builder.build_prompt(
    task_description="Answer document questions accurately with citations",
    input_text="What's the profit margin in Q3?",
    num_examples=2,
    example_strategy="difficulty"  # Match complexity
)
```

---

## 🎭 3. Meta-Prompting

### What is Meta-Prompting?

**Definition:** Using one LLM call to generate or improve prompts for another LLM call.

**Concept:** The LLM writes its own instructions!

### Meta-Prompting Template

```python
# File: utils/prompts/meta_prompting.py

META_PROMPT_GENERATOR = """
You are a prompt engineering expert. Your job is to write optimal prompts for other LLMs.

# TASK
Generate a high-quality prompt for this task: {task_description}

# REQUIREMENTS
The generated prompt should:
1. Be clear and specific
2. Include relevant context
3. Specify output format
4. Include quality criteria
5. Provide examples if helpful

# PROMPT ENGINEERING BEST PRACTICES
- Use the CO-STAR framework when appropriate
- Include step-by-step instructions for complex tasks
- Specify constraints and boundaries
- Add hallucination prevention measures
- Include confidence scoring

# OUTPUT
Generate the complete prompt below:

---GENERATED PROMPT START---

[Your generated prompt here]

---GENERATED PROMPT END---
"""

class MetaPrompter:
    """Generate optimized prompts dynamically"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def generate_prompt(self, task_description: str, context: Dict = None) -> str:
        """Generate an optimized prompt for a task"""
        
        meta_prompt = META_PROMPT_GENERATOR.format(
            task_description=task_description
        )
        
        if context:
            meta_prompt += f"\n\n# ADDITIONAL CONTEXT\n{context}"
        
        # LLM generates the prompt
        generated_prompt = await self.llm.generate(meta_prompt)
        
        # Extract the prompt
        prompt = self._extract_generated_prompt(generated_prompt)
        
        return prompt
    
    async def improve_prompt(self, original_prompt: str, feedback: str) -> str:
        """Improve an existing prompt based on feedback"""
        
        improvement_prompt = f"""
You are a prompt optimization expert. Improve this prompt based on the feedback.

# ORIGINAL PROMPT
{original_prompt}

# FEEDBACK
{feedback}

# YOUR TASK
Rewrite the prompt to address the feedback while maintaining its core purpose.

# OUTPUT
Improved prompt:
"""
        
        improved = await self.llm.generate(improvement_prompt)
        return improved
    
    async def adapt_prompt_to_user(
        self, 
        base_prompt: str, 
        user_profile: Dict
    ) -> str:
        """Adapt prompt based on user expertise level"""
        
        adaptation_prompt = f"""
Adapt this prompt for a user with this profile:

# BASE PROMPT
{base_prompt}

# USER PROFILE
- Expertise Level: {user_profile.get('expertise', 'intermediate')}
- Domain: {user_profile.get('domain', 'general')}
- Preferences: {user_profile.get('preferences', {})}

# YOUR TASK
Adjust the prompt's:
1. Technical language (match expertise level)
2. Domain-specific examples
3. Output format (match preferences)

# OUTPUT
Adapted prompt:
"""
        
        adapted = await self.llm.generate(adaptation_prompt)
        return adapted


# Usage Example
meta_prompter = MetaPrompter(llm=my_llm)

# Generate prompt for a new task
task = "Extract key financial metrics from quarterly reports"
generated_prompt = await meta_prompter.generate_prompt(task)

# Use the generated prompt
result = await llm.generate(generated_prompt.format(input=user_query))

# If results aren't good, improve the prompt
feedback = "The generated prompt misses expense data. Include operating expenses."
improved_prompt = await meta_prompter.improve_prompt(generated_prompt, feedback)
```

### Self-Improving Prompts

```python
# File: utils/prompts/self_improving_prompts.py

class SelfImprovingPromptSystem:
    """Prompts that improve themselves based on performance"""
    
    def __init__(self, llm):
        self.llm = llm
        self.prompt_history = []
        self.performance_history = []
    
    async def execute_with_improvement(
        self,
        initial_prompt: str,
        test_cases: List[Dict],
        max_iterations: int = 5
    ) -> Dict:
        """
        Execute prompt and iteratively improve it based on results
        """
        current_prompt = initial_prompt
        best_prompt = initial_prompt
        best_score = 0.0
        
        for iteration in range(max_iterations):
            print(f"\n=== Iteration {iteration + 1} ===")
            
            # Test current prompt
            score, errors = await self._test_prompt(current_prompt, test_cases)
            
            print(f"Score: {score:.2f}")
            
            # Track history
            self.prompt_history.append(current_prompt)
            self.performance_history.append(score)
            
            # Update best
            if score > best_score:
                best_score = score
                best_prompt = current_prompt
            
            # If perfect, stop
            if score >= 0.95:
                print("✓ Achieved target performance!")
                break
            
            # Generate improved version
            current_prompt = await self._improve_based_on_errors(
                current_prompt,
                errors
            )
        
        return {
            "best_prompt": best_prompt,
            "best_score": best_score,
            "iterations": len(self.prompt_history),
            "improvement": best_score - self.performance_history[0],
            "history": {
                "prompts": self.prompt_history,
                "scores": self.performance_history
            }
        }
    
    async def _test_prompt(
        self,
        prompt: str,
        test_cases: List[Dict]
    ) -> Tuple[float, List[Dict]]:
        """Test prompt against test cases"""
        correct = 0
        errors = []
        
        for test_case in test_cases:
            # Format prompt with test input
            formatted_prompt = prompt.format(**test_case["input"])
            
            # Get LLM response
            response = await self.llm.generate(formatted_prompt)
            
            # Check correctness
            expected = test_case["expected_output"]
            if self._is_correct(response, expected):
                correct += 1
            else:
                errors.append({
                    "input": test_case["input"],
                    "expected": expected,
                    "got": response,
                    "error_type": self._classify_error(response, expected)
                })
        
        score = correct / len(test_cases)
        return score, errors
    
    async def _improve_based_on_errors(
        self,
        current_prompt: str,
        errors: List[Dict]
    ) -> str:
        """Generate improved prompt based on errors"""
        
        error_analysis = self._analyze_errors(errors)
        
        improvement_prompt = f"""
Improve this prompt to fix these issues:

# CURRENT PROMPT
{current_prompt}

# ERROR ANALYSIS
{error_analysis}

# COMMON ERRORS
{self._format_errors(errors[:3])}  # Show top 3 errors

# YOUR TASK
Rewrite the prompt to fix these errors. Maintain the core functionality but add:
1. Clearer instructions where there's confusion
2. Better examples for edge cases
3. Stronger constraints to prevent mistakes

# OUTPUT
Improved prompt:
"""
        
        improved = await self.llm.generate(improvement_prompt)
        return improved
    
    def _analyze_errors(self, errors: List[Dict]) -> str:
        """Analyze error patterns"""
        error_types = {}
        for error in errors:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        analysis = "Error Breakdown:\n"
        for error_type, count in error_types.items():
            percentage = (count / len(errors)) * 100
            analysis += f"- {error_type}: {count} ({percentage:.1f}%)\n"
        
        return analysis


# Usage Example
test_cases = [
    {
        "input": {"question": "What's Q3 revenue?", "context": "Q3 revenue: $4.2M"},
        "expected_output": "Q3 revenue was $4.2 million."
    },
    {
        "input": {"question": "Calculate growth rate", "context": "Q2: $3.8M, Q3: $4.2M"},
        "expected_output": "Growth rate: 10.53%"
    },
    # ... more test cases
]

improver = SelfImprovingPromptSystem(llm=my_llm)

result = await improver.execute_with_improvement(
    initial_prompt="Answer this question: {question}\nContext: {context}",
    test_cases=test_cases,
    max_iterations=5
)

print(f"Best Prompt:\n{result['best_prompt']}")
print(f"Best Score: {result['best_score']}")
print(f"Improvement: +{result['improvement']*100:.1f}%")
```

---

## 🤝 4. Multi-Agent Orchestration

### What is Multi-Agent Orchestration?

**Definition:** Coordinating multiple specialized AI agents to solve complex tasks through collaboration.

**Your Project Already Uses This!** Your RAG system has:
- Retrieval Agent
- Generation Agent
- Ingestion Agent

Let's make them even better with advanced orchestration patterns.

### Advanced Multi-Agent Patterns

```python
# File: utils/agent_orchestration.py

from crewai import Agent, Task, Crew, Process
from typing import List, Dict

class AdvancedMultiAgentOrchestrator:
    """
    Orchestrate multiple specialized agents with advanced patterns
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.agents = self._create_specialized_agents()
    
    def _create_specialized_agents(self) -> Dict[str, Agent]:
        """Create a team of specialized agents"""
        
        agents = {
            # Analyst: Understands user intent
            "analyst": Agent(
                role="Query Analyst",
                goal="Understand user intent and decompose complex queries",
                backstory="""You're an expert at understanding what users really want.
                You break down complex questions into simpler sub-questions.""",
                llm=self.llm,
                verbose=True
            ),
            
            # Retriever: Finds relevant information
            "retriever": Agent(
                role="Information Retriever",
                goal="Find the most relevant documents for each sub-question",
                backstory="""You're a research specialist who knows how to find information
                efficiently. You use semantic search and filtering expertly.""",
                llm=self.llm,
                verbose=True,
                tools=[search_tool, filter_tool]
            ),
            
            # Validator: Checks information quality
            "validator": Agent(
                role="Information Validator",
                goal="Verify information accuracy and detect hallucinations",
                backstory="""You're a fact-checker who ensures all information is
                accurate and properly sourced. You catch mistakes others miss.""",
                llm=self.llm,
                verbose=True
            ),
            
            # Synthesizer: Combines information
            "synthesizer": Agent(
                role="Information Synthesizer",
                goal="Combine multiple pieces of information into coherent answers",
                backstory="""You're a master at taking disparate information and
                weaving it into clear, comprehensive answers.""",
                llm=self.llm,
                verbose=True
            ),
            
            # Critic: Reviews final output
            "critic": Agent(
                role="Quality Critic",
                goal="Review and improve the final answer",
                backstory="""You're a perfectionist who reviews work and suggests
                improvements. You ensure the highest quality output.""",
                llm=self.llm,
                verbose=True
            )
        }
        
        return agents
    
    async def execute_sequential(self, question: str) -> Dict:
        """
        Sequential execution: Analyst → Retriever → Synthesizer → Critic
        """
        # Task 1: Analyze query
        analyze_task = Task(
            description=f"Analyze this question and break it into sub-questions: {question}",
            agent=self.agents["analyst"],
            expected_output="List of sub-questions with search strategies"
        )
        
        # Task 2: Retrieve information
        retrieve_task = Task(
            description="Find relevant information for each sub-question",
            agent=self.agents["retriever"],
            expected_output="Retrieved documents with relevance scores",
            context=[analyze_task]  # Depends on analyze_task
        )
        
        # Task 3: Synthesize answer
        synthesize_task = Task(
            description="Create comprehensive answer from retrieved information",
            agent=self.agents["synthesizer"],
            expected_output="Complete answer with citations",
            context=[retrieve_task]
        )
        
        # Task 4: Critique and improve
        critique_task = Task(
            description="Review answer for accuracy, completeness, and clarity",
            agent=self.agents["critic"],
            expected_output="Improved final answer",
            context=[synthesize_task]
        )
        
        # Execute crew
        crew = Crew(
            agents=[
                self.agents["analyst"],
                self.agents["retriever"],
                self.agents["synthesizer"],
                self.agents["critic"]
            ],
            tasks=[analyze_task, retrieve_task, synthesize_task, critique_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result
    
    async def execute_hierarchical(self, question: str) -> Dict:
        """
        Hierarchical execution: Manager delegates to specialists
        """
        # Create manager agent
        manager = Agent(
            role="Project Manager",
            goal="Coordinate specialists to answer complex questions",
            backstory="""You're an experienced manager who delegates tasks to
            the right specialists and ensures quality results.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True  # Key: Can delegate to other agents
        )
        
        # Manager's task
        manager_task = Task(
            description=f"""
Answer this complex question: {question}

You have access to these specialists:
- Query Analyst: Breaks down complex questions
- Information Retriever: Finds relevant documents
- Information Validator: Checks accuracy
- Information Synthesizer: Combines information
- Quality Critic: Reviews final output

Delegate appropriately and coordinate their work to produce the best answer.
""",
            agent=manager,
            expected_output="Final answer coordinated through specialists"
        )
        
        # Execute with hierarchical process
        crew = Crew(
            agents=[
                manager,
                self.agents["analyst"],
                self.agents["retriever"],
                self.agents["validator"],
                self.agents["synthesizer"],
                self.agents["critic"]
            ],
            tasks=[manager_task],
            process=Process.hierarchical,
            manager_llm=self.llm,
            verbose=True
        )
        
        result = crew.kickoff()
        return result
    
    async def execute_parallel(self, question: str) -> Dict:
        """
        Parallel execution: Multiple agents work simultaneously
        """
        # Create parallel tasks
        tasks = []
        
        # Task 1: Semantic search
        semantic_task = Task(
            description=f"Perform semantic search for: {question}",
            agent=self.agents["retriever"],
            expected_output="Semantically similar documents"
        )
        tasks.append(semantic_task)
        
        # Task 2: Keyword search (parallel)
        keyword_task = Task(
            description=f"Perform keyword search for: {question}",
            agent=self.agents["retriever"],
            expected_output="Keyword-matched documents"
        )
        tasks.append(keyword_task)
        
        # Task 3: Related questions (parallel)
        related_task = Task(
            description=f"Find related questions for: {question}",
            agent=self.agents["analyst"],
            expected_output="List of related questions"
        )
        tasks.append(related_task)
        
        # Task 4: Synthesize all results
        synthesize_task = Task(
            description="Combine results from all searches",
            agent=self.agents["synthesizer"],
            expected_output="Comprehensive answer",
            context=[semantic_task, keyword_task, related_task]
        )
        tasks.append(synthesize_task)
        
        # Execute crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            process=Process.sequential,  # Tasks with no dependencies run in parallel
            verbose=True
        )
        
        result = crew.kickoff()
        return result
    
    async def execute_debate(self, question: str) -> Dict:
        """
        Debate mode: Agents discuss and reach consensus
        """
        # Create debater agents with different perspectives
        optimist = Agent(
            role="Optimistic Analyst",
            goal="Find positive insights and opportunities",
            backstory="You focus on positive aspects and opportunities",
            llm=self.llm
        )
        
        pessimist = Agent(
            role="Critical Analyst",
            goal="Identify risks and challenges",
            backstory="You focus on potential problems and risks",
            llm=self.llm
        )
        
        realist = Agent(
            role="Balanced Analyst",
            goal="Provide balanced, objective analysis",
            backstory="You weigh both positives and negatives objectively",
            llm=self.llm
        )
        
        # Debate tasks
        optimist_task = Task(
            description=f"Analyze from optimistic perspective: {question}",
            agent=optimist,
            expected_output="Optimistic analysis"
        )
        
        pessimist_task = Task(
            description=f"Analyze from critical perspective: {question}",
            agent=pessimist,
            expected_output="Critical analysis"
        )
        
        synthesis_task = Task(
            description="Synthesize both perspectives into balanced answer",
            agent=realist,
            expected_output="Balanced final answer",
            context=[optimist_task, pessimist_task]
        )
        
        # Execute debate
        crew = Crew(
            agents=[optimist, pessimist, realist],
            tasks=[optimist_task, pessimist_task, synthesis_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result


# Usage Example
orchestrator = AdvancedMultiAgentOrchestrator(llm=my_llm)

# Sequential execution (best for most cases)
result = await orchestrator.execute_sequential(
    "Compare Q2 and Q3 revenue across all regions and identify trends"
)

# Hierarchical execution (complex coordinated tasks)
result = await orchestrator.execute_hierarchical(
    "Analyze all financial documents and provide investment recommendation"
)

# Parallel execution (multiple independent searches)
result = await orchestrator.execute_parallel(
    "Find all mentions of pricing changes in 2024"
)

# Debate mode (need multiple perspectives)
result = await orchestrator.execute_debate(
    "Should we expand to the European market based on these documents?"
)
```

---

## 💡 5. Pro Tips from a Senior AI Architect

### Tip #1: When Each Strategy Shines

```python
# Decision Matrix
def choose_advanced_strategy(task_characteristics: Dict) -> str:
    """
    Choose the right advanced strategy based on task
    """
    complexity = task_characteristics.get("complexity", "medium")
    has_examples = task_characteristics.get("has_examples", False)
    needs_exploration = task_characteristics.get("needs_exploration", False)
    needs_collaboration = task_characteristics.get("needs_collaboration", False)
    
    if needs_exploration and complexity == "high":
        return "tree_of_thoughts"  # Explore multiple solutions
    
    elif has_examples and complexity == "medium":
        return "few_shot"  # Learn from examples
    
    elif needs_collaboration:
        return "multi_agent"  # Coordinate specialists
    
    elif task_characteristics.get("needs_self_improvement", False):
        return "meta_prompting"  # Generate optimal prompts
    
    else:
        return "cot"  # Default to Chain-of-Thought


# Examples:
choose_advanced_strategy({
    "complexity": "high",
    "needs_exploration": True
})  # → "tree_of_thoughts"

choose_advanced_strategy({
    "complexity": "medium",
    "has_examples": True
})  # → "few_shot"

choose_advanced_strategy({
    "needs_collaboration": True
})  # → "multi_agent"
```

### Tip #2: Cost Management for Advanced Strategies

```python
# File: utils/optimization/advanced_cost_manager.py

class AdvancedCostManager:
    """Manage costs for expensive advanced strategies"""
    
    COST_MULTIPLIERS = {
        "basic": 1,
        "cot": 3,
        "react": 5,
        "few_shot": 2,
        "tot": 15,  # Very expensive!
        "multi_agent": 10,
        "meta_prompting": 4
    }
    
    def estimate_tot_cost(
        self,
        max_branches: int,
        max_depth: int,
        base_cost: float
    ) -> float:
        """
        Estimate Tree of Thoughts cost
        
        Formula: base_cost × (branches^depth) × evaluation_factor
        """
        total_nodes = sum(max_branches ** d for d in range(1, max_depth + 1))
        evaluation_cost = total_nodes * 0.5  # Each node needs evaluation
        
        return base_cost * (total_nodes + evaluation_cost)
    
    def optimize_tot_budget(
        self,
        budget: float,
        base_cost: float
    ) -> Dict[str, int]:
        """
        Find optimal branches and depth for budget
        """
        best_config = {"branches": 2, "depth": 2}
        best_value = 0
        
        for branches in range(2, 6):
            for depth in range(2, 5):
                cost = self.estimate_tot_cost(branches, depth, base_cost)
                
                if cost <= budget:
                    # Value = exploration power
                    value = branches * depth
                    if value > best_value:
                        best_value = value
                        best_config = {"branches": branches, "depth": depth}
        
        return best_config
    
    def estimate_multi_agent_cost(
        self,
        num_agents: int,
        num_rounds: int,
        base_cost: float
    ) -> float:
        """
        Estimate multi-agent orchestration cost
        """
        # Each agent in each round
        total_calls = num_agents * num_rounds
        
        # Add coordination overhead (manager calls)
        coordination_calls = num_rounds * 0.5
        
        return base_cost * (total_calls + coordination_calls)


# Usage
cost_manager = AdvancedCostManager()

# Plan ToT within budget
budget = 5.00  # $5 budget
base_cost = 0.05  # $0.05 per LLM call

optimal_config = cost_manager.optimize_tot_budget(budget, base_cost)
print(f"Optimal ToT config for ${budget}: {optimal_config}")
# Output: {"branches": 3, "depth": 3}

# Estimate before running
estimated_cost = cost_manager.estimate_tot_cost(
    max_branches=3,
    max_depth=3,
    base_cost=0.05
)
print(f"Estimated cost: ${estimated_cost:.2f}")
```

### Tip #3: Caching for Few-Shot Examples

```python
# File: utils/optimization/example_cache.py

import hashlib
from typing import List, Dict
import json

class FewShotExampleCache:
    """Cache few-shot examples to avoid recomputation"""
    
    def __init__(self):
        self.cache = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get_examples(
        self,
        query: str,
        num_examples: int,
        strategy: str
    ) -> List[Dict]:
        """Get cached examples or compute new ones"""
        
        # Create cache key
        cache_key = self._create_cache_key(query, num_examples, strategy)
        
        # Check cache
        if cache_key in self.cache:
            self.hit_count += 1
            print(f"✓ Cache hit! (Hit rate: {self.hit_rate():.1%})")
            return self.cache[cache_key]
        
        # Cache miss - would compute here
        self.miss_count += 1
        return None
    
    def store_examples(
        self,
        query: str,
        num_examples: int,
        strategy: str,
        examples: List[Dict]
    ):
        """Store examples in cache"""
        cache_key = self._create_cache_key(query, num_examples, strategy)
        self.cache[cache_key] = examples
    
    def _create_cache_key(
        self,
        query: str,
        num_examples: int,
        strategy: str
    ) -> str:
        """Create unique cache key"""
        key_data = f"{query}|{num_examples}|{strategy}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "hits": self.hit_count,
            "misses": self.miss_count,
            "hit_rate": self.hit_rate(),
            "cache_size": len(self.cache)
        }
```

---

## 🧪 6. Hands-On Exercises

### Exercise 1: Implement Tree of Thoughts

**Task:** Add ToT reasoning for complex multi-document analysis.

```python
# TODO: Implement in utils/agent_rag_engine.py

# 1. Create TreeOfThoughtsAgent class
# 2. Implement branch generation (3 branches per decision point)
# 3. Add scoring mechanism
# 4. Test with complex query
# 5. Compare accuracy vs standard CoT

# Test Query:
# "Should we expand to Europe based on market analysis docs?"
```

### Exercise 2: Build Few-Shot Example Bank

**Task:** Create a bank of 20+ few-shot examples for your domain.

```python
# File: utils/prompts/example_bank.py

EXAMPLE_BANK = [
    {
        "input": {...},
        "output": {...},
        "difficulty": 0.5,
        "category": "factual_extraction"
    },
    # TODO: Add 20+ examples covering:
    # - Simple fact extraction
    # - Calculations
    # - Comparisons
    # - Summaries
    # - Multi-document analysis
]
```

### Exercise 3: Create Specialized Agent Team

**Task:** Build a team of 5 specialized agents for your document system.

```python
# Agents to create:
# 1. Query Decomposer
# 2. Document Searcher
# 3. Fact Checker
# 4. Answer Synthesizer
# 5. Quality Reviewer

# Test with orchestration patterns
```

---

## 🎓 Key Takeaways

✅ **Tree of Thoughts (ToT)**
- Explores multiple reasoning paths
- Best for complex strategic decisions
- 90-95% accuracy but expensive
- Use when stakes are high

✅ **Few-Shot Learning**
- Learn from 2-10 examples
- Dramatically improves consistency
- Example selection matters
- Cost-effective accuracy boost

✅ **Meta-Prompting**
- LLM writes better prompts
- Self-improving systems
- Adaptive to user needs
- Saves prompt engineering time

✅ **Multi-Agent Orchestration**
- Coordinate specialized agents
- Sequential, parallel, hierarchical modes
- Debate for multiple perspectives
- Your project already uses this!

---

## 🚀 What's Next?

You've mastered advanced strategies! Ready for:

👉 **Part 4**: [Prompt Optimization](PROMPT_ENGINEERING_04_OPTIMIZATION.md)
- DSPy (Programmatic prompt optimization)
- Prompt compression techniques
- A/B testing frameworks
- Performance tuning

---

## 📋 Checklist

- [ ] Understand Tree of Thoughts (ToT)
- [ ] Implement ToT for complex tasks
- [ ] Build few-shot example bank (20+ examples)
- [ ] Implement example selection strategies
- [ ] Create meta-prompting system
- [ ] Build specialized agent team
- [ ] Test multi-agent orchestration patterns
- [ ] Measure performance improvements
- [ ] Optimize costs for advanced strategies

---

**Congratulations! You're now an advanced prompt engineering expert! 🌳✨**

*Next: [Part 4 - Prompt Optimization](PROMPT_ENGINEERING_04_OPTIMIZATION.md)*
