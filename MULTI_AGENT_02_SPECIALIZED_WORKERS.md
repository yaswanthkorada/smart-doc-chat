# 👥 Part 2: Specialized Worker Agents

## Researcher, Analyst, Coder, Critic, and Synthesizer

**Learning Time:** 12-14 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Part 1 (Orchestration Patterns)

---

## 🎯 Learning Objectives

By the end of this guide, you'll be able to:
- ✅ Design 5 specialized agent types with distinct capabilities
- ✅ Create expert system prompts and personas
- ✅ Build specialized tool sets for each agent
- ✅ Implement a Critic agent for quality control
- ✅ Optimize LLM selection per agent (GPT-4 vs 3.5 vs local)
- ✅ Integrate specialized agents into your Document Analysis project

---

## 📚 The Problem: Generalist vs Specialist Agents

### Current Approach: One Agent Does Everything

```python
# Your current single agent
agent = Agent(
    role="Document Assistant",
    goal="Answer questions about documents",
    tools=[search, retrieve, analyze, calculate, format],
    backstory="You are a helpful AI assistant"
)

# Issues:
# ❌ Mediocre at everything, expert at nothing
# ❌ No depth in any specific domain
# ❌ Can't leverage specialized tools effectively
# ❌ No quality control or peer review
# ❌ Doesn't know when to hand off to another agent
```

### Real Example from Your Project

**User Query:** *"Analyze Q3 2024 financial report and create a trend visualization"*

**Single Agent Output (Current):**
```
Agent: "I found the Q3 2024 report. Revenue was $5.2M. 
Here's a basic chart: [generic matplotlib code]"

Quality: 65%
Issues:
- Missed key insights (growth %, comparisons)
- Basic visualization (no interactivity)
- No validation (could be wrong)
- Generic analysis (not domain-expert level)
```

**Multi-Specialist Agent Output (Target):**
```
Researcher Agent: "Retrieved Q3 2024 financial report (127 pages). 
Key sections: Revenue p.12, Costs p.34, Growth metrics p.89."

Analyst Agent: "Deep analysis:
- Revenue: $5.2M (+18% vs Q2, +45% YoY)
- Margins improved from 32% → 37%
- Top growth drivers: Enterprise deals (+120%), Renewals (+8%)"

Coder Agent: "Created interactive Plotly dashboard:
- Revenue trend line (Q1-Q4)
- Growth breakdown by segment
- Margin analysis chart
[Production-ready Python code]"

Critic Agent: "Quality review:
✅ Revenue figures verified against source (p.12)
✅ Calculations correct (manually verified +18%)
✅ Chart accurately represents data
⚠️ Minor issue: Missing Q4 forecast data (not in document)
Overall Quality: 95%"

Quality: 95%
Benefits:
✅ Deep insights from domain expert (Analyst)
✅ Production-quality code (Coder specialist)
✅ Verified accuracy (Critic validation)
✅ Comprehensive analysis
```

---

## 🔬 Agent #1: Researcher Agent (RAG Specialist)

### Purpose
**Expert retrieval and information extraction.** This agent is a master at navigating large document sets, finding relevant information, and extracting structured data.

### Capabilities
- ✅ Semantic search across documents
- ✅ Table extraction from PDFs
- ✅ Section-by-section navigation
- ✅ Citation management
- ✅ Multi-document synthesis

---

### Implementation

```python
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from utils.agent_tools import DocumentAnalyzerTool

class ResearcherAgent:
    """
    Specialized agent for document retrieval and extraction
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # Specialized tools for research
        self.tools = [
            self.create_search_tool(),
            self.create_extract_table_tool(),
            self.create_summarize_section_tool(),
            self.create_find_citations_tool()
        ]
        
        # Use cost-effective model (research doesn't need GPT-4)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Cheaper, good for retrieval
            temperature=0  # Deterministic for research
        )
        
        # Create agent with expert persona
        self.agent = Agent(
            role="Senior Research Analyst",
            goal="Find and extract precise information from documents efficiently",
            backstory="""You are a meticulous research analyst with 15 years of experience 
            in document analysis. You excel at:
            - Quickly navigating large document sets (100+ pages)
            - Finding exact information with proper citations
            - Extracting structured data from tables and charts
            - Distinguishing between facts and opinions
            - Knowing when information is NOT in the documents (avoiding hallucination)
            
            Your motto: "If it's not in the documents, say so. Never make up information."
            """,
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False  # Researcher doesn't delegate
        )
    
    def create_search_tool(self):
        """Semantic search across user's documents"""
        from langchain.tools import Tool
        from utils.agent_rag_engine import AgenticRAGEngine
        
        rag_engine = AgenticRAGEngine(user_id=self.user_id)
        
        def search_documents(query: str) -> str:
            """
            Search across all user documents using semantic search
            Args:
                query: Search query
            Returns:
                Relevant document excerpts with citations
            """
            results = rag_engine.retrieve(query, top_k=5)
            
            # Format with citations
            formatted = []
            for i, doc in enumerate(results, 1):
                formatted.append(f"""
[{i}] {doc.metadata.get('filename', 'Unknown')} (page {doc.metadata.get('page', 'N/A')}):
{doc.page_content}
                """)
            
            return "\n".join(formatted)
        
        return Tool(
            name="search_documents",
            description="Search across all user documents. Use this for finding relevant information.",
            func=search_documents
        )
    
    def create_extract_table_tool(self):
        """Extract tables from PDFs"""
        from langchain.tools import Tool
        
        def extract_table(document_name: str, page_number: int) -> str:
            """
            Extract table data from a specific page
            Args:
                document_name: Name of the document
                page_number: Page number containing the table
            Returns:
                Extracted table as CSV format
            """
            # Implementation using your DocumentAnalyzerTool
            tool = DocumentAnalyzerTool()
            result = tool.extract_tables(document_name, page_number)
            return result
        
        return Tool(
            name="extract_table",
            description="Extract table data from a specific page in a document. Returns CSV format.",
            func=extract_table
        )
    
    def create_summarize_section_tool(self):
        """Summarize specific document sections"""
        from langchain.tools import Tool
        
        def summarize_section(document_name: str, section_heading: str) -> str:
            """
            Get a summary of a specific section
            Args:
                document_name: Name of the document
                section_heading: Heading of the section (e.g., "Revenue Analysis")
            Returns:
                Concise summary of that section
            """
            # Find section and summarize
            # Implementation details...
            return f"Summary of {section_heading} in {document_name}"
        
        return Tool(
            name="summarize_section",
            description="Get a summary of a specific section from a document",
            func=summarize_section
        )
    
    def create_find_citations_tool(self):
        """Find exact citations for claims"""
        from langchain.tools import Tool
        
        def find_citation(claim: str) -> str:
            """
            Find the exact location where a claim is supported
            Args:
                claim: The statement to verify
            Returns:
                Document name, page number, and exact quote
            """
            # Search for supporting evidence
            # Implementation details...
            return f"Citation for: {claim}"
        
        return Tool(
            name="find_citation",
            description="Find exact citation (document, page, quote) supporting a claim",
            func=find_citation
        )
    
    def research(self, query: str) -> str:
        """
        Execute research task
        """
        task = Task(
            description=f"""
            Research the following query using the available documents:
            
            {query}
            
            Requirements:
            1. Search thoroughly across all relevant documents
            2. Extract precise information with citations
            3. If information involves tables, extract them
            4. Provide document name and page number for each finding
            5. If information is NOT found, explicitly state "Not found in documents"
            
            Do NOT make up information. Only report what you find.
            """,
            agent=self.agent,
            expected_output="Detailed research findings with citations"
        )
        
        from crewai import Crew
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        return result


# Usage
researcher = ResearcherAgent(user_id="user_1")

# Research query
findings = researcher.research("What was Q3 2024 revenue?")

print(findings)
```

**Output:**
```
🔍 Researcher Agent: Searching documents...

Research Findings:

[1] Q3_2024_Financial_Report.pdf (page 12):
"Total revenue for Q3 2024 was $5.2 million, representing an 18% 
increase from Q2 2024 ($4.4M) and a 45% year-over-year increase 
from Q3 2023 ($3.6M)."

[2] Q3_2024_Financial_Report.pdf (page 34):
Revenue breakdown by segment:
- Enterprise: $3.1M (60%)
- SMB: $1.4M (27%)
- Individual: $0.7M (13%)

Table extracted from page 34:
Segment,Q3 2024,Q2 2024,Growth
Enterprise,$3.1M,$1.4M,+121%
SMB,$1.4M,$1.3M,+8%
Individual,$0.7M,$0.7M,0%

Citations:
- Document: Q3_2024_Financial_Report.pdf
- Pages: 12, 34
- Confidence: High (exact quotes found)
```

---

### Pro-Tip: Researcher Agent Best Practices

```python
class ExpertResearcher(ResearcherAgent):
    """
    Enhanced researcher with best practices
    """
    
    def research_with_validation(self, query: str) -> dict:
        """
        Research with automatic validation
        """
        # Step 1: Initial research
        findings = self.research(query)
        
        # Step 2: Validate citations
        validated_findings = self._validate_citations(findings)
        
        # Step 3: Calculate confidence
        confidence = self._calculate_confidence(validated_findings)
        
        return {
            'findings': validated_findings,
            'confidence': confidence,
            'sources': self._extract_sources(validated_findings)
        }
    
    def _validate_citations(self, findings: str) -> str:
        """
        Verify that all citations actually exist
        """
        # Use find_citation tool to verify each claim
        # Implementation details...
        return findings
    
    def _calculate_confidence(self, findings: str) -> float:
        """
        Calculate confidence based on:
        - Number of sources
        - Directness of quotes
        - Consistency across sources
        """
        # Check if multiple sources agree
        num_sources = findings.count('[')
        has_direct_quotes = '"' in findings
        
        if num_sources >= 3 and has_direct_quotes:
            return 0.95  # High confidence
        elif num_sources >= 2:
            return 0.80  # Medium confidence
        else:
            return 0.60  # Low confidence
```

---

## 📊 Agent #2: Analyst Agent (Domain Expert)

### Purpose
**Deep analysis and insights.** This agent excels at interpreting data, identifying trends, performing calculations, and providing expert-level analysis.

### Capabilities
- ✅ Statistical analysis
- ✅ Trend identification
- ✅ Comparative analysis
- ✅ Financial calculations
- ✅ Anomaly detection

---

### Implementation

```python
class AnalystAgent:
    """
    Domain expert for data analysis and insights
    """
    
    def __init__(self):
        # Specialized analysis tools
        self.tools = [
            self.create_calculate_tool(),
            self.create_compare_tool(),
            self.create_trend_analysis_tool(),
            self.create_anomaly_detection_tool()
        ]
        
        # Use GPT-4 for complex reasoning
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Need strong reasoning
            temperature=0
        )
        
        # Create agent with domain expertise
        self.agent = Agent(
            role="Senior Data Analyst",
            goal="Provide deep, expert-level analysis of data with actionable insights",
            backstory="""You are a seasoned data analyst with 15 years of experience in 
            financial analysis, having worked at top consulting firms (McKinsey, BCG).
            
            Your expertise:
            - Statistical analysis (correlation, regression, significance testing)
            - Financial metrics (growth rates, margins, ratios)
            - Trend identification (seasonality, cyclicality, anomalies)
            - Comparative analysis (benchmarking, cohort analysis)
            - Predictive insights (forecasting, scenario planning)
            
            Your analysis is:
            - Quantitative (numbers and percentages, not vague terms)
            - Insightful (WHY things happen, not just WHAT)
            - Actionable (recommendations, not just observations)
            - Honest (acknowledge limitations and uncertainties)
            """,
            tools=self.tools,
            llm=self.llm,
            verbose=True
        )
    
    def create_calculate_tool(self):
        """Perform calculations on data"""
        from langchain.tools import Tool
        import pandas as pd
        import numpy as np
        
        def calculate_metrics(data: str, metric_type: str) -> str:
            """
            Calculate metrics from data
            Args:
                data: CSV-formatted data
                metric_type: Type of metric (growth, average, percentage, etc.)
            Returns:
                Calculated metric with explanation
            """
            try:
                # Parse CSV data
                from io import StringIO
                df = pd.read_csv(StringIO(data))
                
                if metric_type == "growth":
                    # Calculate growth rate
                    if len(df) >= 2:
                        initial = df.iloc[0].values[1]  # First value
                        final = df.iloc[-1].values[1]   # Last value
                        growth = ((final - initial) / initial) * 100
                        return f"Growth: {growth:.1f}% (from {initial} to {final})"
                
                elif metric_type == "average":
                    values = df.iloc[:, 1].values
                    avg = np.mean(values)
                    return f"Average: {avg:.2f}"
                
                elif metric_type == "trend":
                    # Simple linear regression
                    x = np.arange(len(df))
                    y = df.iloc[:, 1].values
                    slope = np.polyfit(x, y, 1)[0]
                    
                    if slope > 0:
                        return f"Upward trend: +{slope:.2f} per period"
                    else:
                        return f"Downward trend: {slope:.2f} per period"
                
                return "Calculation complete"
            
            except Exception as e:
                return f"Error in calculation: {str(e)}"
        
        return Tool(
            name="calculate_metrics",
            description="Calculate metrics (growth, average, trend) from CSV data",
            func=calculate_metrics
        )
    
    def create_compare_tool(self):
        """Compare two datasets"""
        from langchain.tools import Tool
        
        def compare_datasets(data1: str, data2: str, comparison_type: str) -> str:
            """
            Compare two datasets
            Args:
                data1: First dataset (CSV)
                data2: Second dataset (CSV)
                comparison_type: Type of comparison (difference, ratio, etc.)
            Returns:
                Comparison results with insights
            """
            # Implementation for comparing datasets
            # Calculate differences, ratios, statistical significance
            return f"Comparison: {comparison_type} analysis"
        
        return Tool(
            name="compare_datasets",
            description="Compare two datasets (e.g., Q3 vs Q4, 2023 vs 2024)",
            func=compare_datasets
        )
    
    def create_trend_analysis_tool(self):
        """Identify trends in time-series data"""
        from langchain.tools import Tool
        
        def analyze_trend(data: str) -> str:
            """
            Analyze trends in time-series data
            Args:
                data: Time-series data (CSV with date column)
            Returns:
                Trend analysis (direction, strength, seasonality)
            """
            # Implement trend analysis
            # Use statsmodels for decomposition
            return "Trend analysis: ..."
        
        return Tool(
            name="analyze_trend",
            description="Analyze trends in time-series data (direction, seasonality, strength)",
            func=analyze_trend
        )
    
    def create_anomaly_detection_tool(self):
        """Detect anomalies in data"""
        from langchain.tools import Tool
        
        def detect_anomalies(data: str, threshold: float = 2.0) -> str:
            """
            Detect anomalies using statistical methods
            Args:
                data: Dataset (CSV)
                threshold: Number of standard deviations for anomaly (default 2.0)
            Returns:
                List of anomalies with explanations
            """
            # Implement anomaly detection
            # Use z-score or IQR method
            return "Anomalies detected: ..."
        
        return Tool(
            name="detect_anomalies",
            description="Detect statistical anomalies in data (outliers, unusual patterns)",
            func=detect_anomalies
        )
    
    def analyze(self, data: str, analysis_type: str = "comprehensive") -> str:
        """
        Perform analysis on data
        """
        task = Task(
            description=f"""
            Perform {analysis_type} analysis on this data:
            
            {data}
            
            Requirements:
            1. Calculate key metrics (growth, averages, trends)
            2. Identify notable patterns or anomalies
            3. Provide insights (WHY these patterns exist)
            4. Give actionable recommendations
            5. Be quantitative (use numbers, not vague terms like "slightly")
            
            Format your analysis as:
            📊 Key Metrics:
            - Metric 1: X (interpretation)
            - Metric 2: Y (interpretation)
            
            📈 Trends & Patterns:
            - Pattern 1 (significance)
            - Pattern 2 (significance)
            
            💡 Insights:
            - Insight 1 (WHY this matters)
            - Insight 2 (implications)
            
            🎯 Recommendations:
            - Recommendation 1 (action to take)
            - Recommendation 2 (priority level)
            """,
            agent=self.agent,
            expected_output="Expert-level analysis with actionable insights"
        )
        
        from crewai import Crew
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        return result


# Usage with Researcher's findings
researcher = ResearcherAgent(user_id="user_1")
analyst = AnalystAgent()

# Step 1: Researcher finds data
revenue_data = researcher.research("Extract revenue data for Q1-Q4 2024")

# Step 2: Analyst analyzes it
analysis = analyst.analyze(revenue_data, analysis_type="comprehensive")

print(analysis)
```

**Output:**
```
📊 Key Metrics:
- Q3 2024 Revenue: $5.2M (base)
- Q2 to Q3 Growth: +18% (+$0.8M)
- YoY Growth (Q3 2023 → Q3 2024): +45% (+$1.6M)
- Average quarterly growth (Q1-Q4): +15.2%

📈 Trends & Patterns:
- Accelerating growth: Q1 (+8%), Q2 (+12%), Q3 (+18%), Q4 (+22% projected)
- Enterprise segment driving growth: +121% in Q3 (from $1.4M to $3.1M)
- SMB segment stable: +8% growth (healthy but not exceptional)
- Individual segment flat: 0% growth (potential concern)

💡 Insights:
- Enterprise focus paying off: 60% of revenue now from Enterprise (was 32% in Q1)
- Product-market fit achieved in Enterprise: 121% growth is exceptional
- SMB growth lagging: May indicate pricing or feature gap
- Individual segment needs attention: Zero growth suggests churn = new signups

🎯 Recommendations:
1. Double down on Enterprise: Hire 2-3 enterprise AEs (HIGH priority)
2. Investigate SMB friction: Why only +8% when Enterprise is +121%? (MEDIUM)
3. Consider sunsetting Individual tier: 13% of revenue, 0% growth, high support cost (LOW)
4. Forecast Q4 conservatively: $6.3-6.5M range (+22% assumes trend continues)
```

---

## 💻 Agent #3: Coder Agent (Technical Specialist)

### Purpose
**Generate production-quality code.** This agent creates Python scripts, SQL queries, visualizations, and data transformations.

### Capabilities
- ✅ Data visualization (Plotly, Matplotlib)
- ✅ SQL query generation
- ✅ Python scripts
- ✅ API integrations
- ✅ Data transformations

---

### Implementation

```python
class CoderAgent:
    """
    Technical specialist for code generation
    """
    
    def __init__(self):
        # Coding tools
        self.tools = [
            self.create_python_executor(),
            self.create_sql_generator(),
            self.create_chart_generator()
        ]
        
        # Use GPT-4 for complex code
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2  # Slightly creative for code
        )
        
        self.agent = Agent(
            role="Senior Software Engineer",
            goal="Generate production-quality, well-documented code",
            backstory="""You are a senior software engineer with 10 years of experience 
            in Python, data visualization, and API development.
            
            Your code is:
            - Clean and readable (follows PEP 8)
            - Well-documented (docstrings and comments)
            - Error-handled (try/except where needed)
            - Production-ready (not prototype code)
            - Efficient (optimized for performance)
            
            You specialize in:
            - Data visualization (Plotly for interactive charts)
            - SQL query generation (optimized, safe from injection)
            - Python scripting (pandas, numpy, data processing)
            - API integrations (RESTful, authentication)
            """,
            tools=self.tools,
            llm=self.llm,
            verbose=True
        )
    
    def create_chart_generator(self):
        """Generate interactive charts"""
        from langchain.tools import Tool
        
        def generate_chart(data: str, chart_type: str, title: str) -> str:
            """
            Generate Plotly chart code
            Args:
                data: CSV data
                chart_type: Type (bar, line, scatter, pie)
                title: Chart title
            Returns:
                Python code to generate the chart
            """
            code = f"""
import plotly.graph_objects as go
import pandas as pd
from io import StringIO

# Load data
data = '''{data}'''
df = pd.read_csv(StringIO(data))

# Create {chart_type} chart
fig = go.Figure()

# Add trace
fig.add_trace(go.{"Bar" if chart_type == "bar" else "Scatter"}(
    x=df.iloc[:, 0],
    y=df.iloc[:, 1],
    name=df.columns[1]
))

# Update layout
fig.update_layout(
    title="{title}",
    xaxis_title=df.columns[0],
    yaxis_title=df.columns[1],
    template="plotly_white",
    hovermode="x unified"
)

# Show chart
fig.show()

# Or save to HTML
fig.write_html("chart.html")
"""
            return code
        
        return Tool(
            name="generate_chart",
            description="Generate Plotly chart code (bar, line, scatter, pie)",
            func=generate_chart
        )
    
    def create_python_executor(self):
        """Execute Python code safely"""
        from langchain.tools import Tool
        
        def execute_python(code: str) -> str:
            """
            Execute Python code in a safe environment
            Args:
                code: Python code to execute
            Returns:
                Execution result or error
            """
            # Use restricted execution environment
            # Implementation details...
            return "Code executed successfully"
        
        return Tool(
            name="execute_python",
            description="Execute Python code safely and return results",
            func=execute_python
        )
    
    def create_sql_generator(self):
        """Generate SQL queries"""
        from langchain.tools import Tool
        
        def generate_sql(description: str, schema: str) -> str:
            """
            Generate SQL query from natural language
            Args:
                description: Query description in natural language
                schema: Database schema (tables and columns)
            Returns:
                SQL query
            """
            # Generate SQL using LLM
            # Implementation details...
            return "SELECT * FROM ..."
        
        return Tool(
            name="generate_sql",
            description="Generate SQL query from natural language description",
            func=generate_sql
        )
    
    def generate_code(self, request: str, data: str = None) -> str:
        """
        Generate code based on request
        """
        task = Task(
            description=f"""
            Generate production-quality Python code for:
            
            {request}
            
            {"Data provided:" + data if data else ""}
            
            Requirements:
            1. Write clean, readable code (PEP 8)
            2. Add docstrings and comments
            3. Include error handling (try/except)
            4. Make it production-ready (not prototype)
            5. Add usage example at the end
            
            Format:
            ```python
            # [Code here]
            ```
            
            Usage:
            [How to run the code]
            """,
            agent=self.agent,
            expected_output="Production-quality Python code with documentation"
        )
        
        from crewai import Crew
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        return result


# Usage
coder = CoderAgent()

# Step 1: Analyst provides data
revenue_data = """
Quarter,Revenue
Q1 2024,$4.0M
Q2 2024,$4.4M
Q3 2024,$5.2M
Q4 2024,$6.1M
"""

# Step 2: Coder creates visualization
chart_code = coder.generate_code(
    request="Create an interactive bar chart showing revenue growth with trend line",
    data=revenue_data
)

print(chart_code)
```

**Output:**
```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from io import StringIO
import numpy as np

def create_revenue_chart(data: str) -> go.Figure:
    """
    Create interactive revenue growth chart with trend line
    
    Args:
        data: CSV string with Quarter and Revenue columns
    
    Returns:
        Plotly Figure object
    """
    try:
        # Load data
        df = pd.read_csv(StringIO(data))
        
        # Convert revenue to numeric (remove $ and M)
        df['Revenue_Numeric'] = df['Revenue'].str.replace('$', '').str.replace('M', '').astype(float)
        
        # Calculate trend line
        x = np.arange(len(df))
        y = df['Revenue_Numeric'].values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        trend = p(x)
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add bar chart (revenue)
        fig.add_trace(
            go.Bar(
                x=df['Quarter'],
                y=df['Revenue_Numeric'],
                name='Revenue',
                marker_color='rgb(55, 83, 109)',
                text=df['Revenue'],
                textposition='auto',
                hovertemplate='%{x}<br>Revenue: %{text}<extra></extra>'
            )
        )
        
        # Add trend line
        fig.add_trace(
            go.Scatter(
                x=df['Quarter'],
                y=trend,
                name='Trend',
                mode='lines',
                line=dict(color='red', width=3, dash='dash'),
                hovertemplate='Trend: $%{y:.1f}M<extra></extra>'
            )
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Revenue Growth Trend (2024)',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Quarter',
            yaxis_title='Revenue (Millions $)',
            template='plotly_white',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None


# Usage
revenue_data = """
Quarter,Revenue
Q1 2024,$4.0M
Q2 2024,$4.4M
Q3 2024,$5.2M
Q4 2024,$6.1M
"""

fig = create_revenue_chart(revenue_data)

# Show interactive chart
fig.show()

# Or save to HTML
fig.write_html("revenue_growth.html")

# Or save as static image
# fig.write_image("revenue_growth.png")  # Requires kaleido
```

---

## 🔍 Agent #4: Critic Agent (Quality Control)

### Purpose
**Quality assurance and validation.** This agent reviews other agents' work, checks for hallucinations, verifies calculations, and ensures accuracy.

### Capabilities
- ✅ Hallucination detection
- ✅ Citation verification
- ✅ Calculation validation
- ✅ Logical consistency checking
- ✅ Quality scoring

---

### Implementation

```python
class CriticAgent:
    """
    Quality control agent that reviews other agents' work
    """
    
    def __init__(self):
        # Verification tools
        self.tools = [
            self.create_citation_checker(),
            self.create_calculation_verifier(),
            self.create_hallucination_detector()
        ]
        
        # Use GPT-4 for careful review
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0
        )
        
        self.agent = Agent(
            role="Quality Assurance Specialist",
            goal="Ensure accuracy, detect hallucinations, and validate all claims",
            backstory="""You are a meticulous QA specialist with obsessive attention to detail.
            You've spent 20 years catching errors that others miss.
            
            Your approach:
            - Skeptical by default (prove it's correct, don't assume)
            - Check every claim against source material
            - Verify all calculations manually
            - Look for logical inconsistencies
            - Flag anything that "seems too good to be true"
            
            Your motto: "Trust, but verify. Actually, just verify."
            
            You are NOT afraid to reject work that doesn't meet standards.
            Better to delay than to deliver something wrong.
            """,
            tools=self.tools,
            llm=self.llm,
            verbose=True
        )
    
    def create_citation_checker(self):
        """Verify that citations are accurate"""
        from langchain.tools import Tool
        
        def check_citation(claim: str, citation: str) -> str:
            """
            Verify that a citation supports a claim
            Args:
                claim: The statement being made
                citation: The source (document, page, quote)
            Returns:
                Verification result (VALID, INVALID, PARTIAL)
            """
            # Load the cited document and check if claim is supported
            # Implementation details...
            return "Citation verification: VALID"
        
        return Tool(
            name="check_citation",
            description="Verify that a citation accurately supports a claim",
            func=check_citation
        )
    
    def create_calculation_verifier(self):
        """Verify mathematical calculations"""
        from langchain.tools import Tool
        
        def verify_calculation(calculation: str) -> str:
            """
            Verify a mathematical calculation
            Args:
                calculation: Description of the calculation (e.g., "Growth from $5.2M to $6.1M")
            Returns:
                Verification result with correct value if wrong
            """
            # Parse and verify calculation
            # Implementation details...
            return "Calculation verified: CORRECT"
        
        return Tool(
            name="verify_calculation",
            description="Verify mathematical calculations for correctness",
            func=verify_calculation
        )
    
    def create_hallucination_detector(self):
        """Detect hallucinated information"""
        from langchain.tools import Tool
        
        def detect_hallucination(claim: str, source_documents: str) -> str:
            """
            Check if a claim is supported by source documents
            Args:
                claim: Statement to verify
                source_documents: Available source material
            Returns:
                GROUNDED, HALLUCINATION, or UNCERTAIN
            """
            # Check if claim appears in source documents
            # Use NLI model for semantic checking
            # Implementation details...
            return "Hallucination check: GROUNDED"
        
        return Tool(
            name="detect_hallucination",
            description="Detect if a claim is hallucinated (not in source documents)",
            func=detect_hallucination
        )
    
    def review(self, work_to_review: str, source_documents: str = None) -> dict:
        """
        Review another agent's work
        """
        task = Task(
            description=f"""
            Review the following work for quality and accuracy:
            
            {work_to_review}
            
            {"Source documents available:" + source_documents if source_documents else ""}
            
            Check for:
            1. ✅ Hallucinations: Are all claims supported by sources?
            2. ✅ Citation accuracy: Do citations actually support the claims?
            3. ✅ Calculation errors: Are all numbers correct?
            4. ✅ Logical consistency: Does the reasoning make sense?
            5. ✅ Completeness: Are there obvious gaps?
            
            Provide your review as:
            
            🔍 QUALITY REVIEW
            
            ✅ What's Good:
            - [List strengths]
            
            ⚠️ Issues Found:
            - [List problems with severity: HIGH, MEDIUM, LOW]
            
            📊 Quality Score: X/10
            
            🎯 Decision: APPROVE / REQUEST_REVISION / REJECT
            
            💡 Recommendations:
            - [Specific improvements needed]
            """,
            agent=self.agent,
            expected_output="Comprehensive quality review with decision"
        )
        
        from crewai import Crew
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        # Parse result
        decision = "APPROVE" if "APPROVE" in result else "REQUEST_REVISION"
        
        return {
            'review': result,
            'decision': decision,
            'requires_revision': decision == "REQUEST_REVISION"
        }


# Usage: Multi-agent workflow with Critic
researcher = ResearcherAgent(user_id="user_1")
analyst = AnalystAgent()
critic = CriticAgent()

# Step 1: Researcher finds data
data = researcher.research("What was Q3 2024 revenue?")

# Step 2: Analyst analyzes
analysis = analyst.analyze(data)

# Step 3: Critic reviews
review = critic.review(
    work_to_review=analysis,
    source_documents=data
)

if review['decision'] == 'APPROVE':
    print("✅ Work approved!")
    print(analysis)
else:
    print("⚠️ Revision needed:")
    print(review['review'])
    
    # Analyst revises based on feedback
    revised_analysis = analyst.analyze(data + "\n\nCritic feedback: " + review['review'])
    print("\n📝 Revised analysis:")
    print(revised_analysis)
```

**Output:**
```
🔍 QUALITY REVIEW

✅ What's Good:
- All revenue figures cited with specific page numbers (p.12, p.34)
- Growth calculations are mathematically correct (+18%, +45%)
- Analysis provides actionable insights (Enterprise focus, SMB investigation)
- Recommendations are prioritized (HIGH, MEDIUM, LOW)
- Quantitative analysis (specific percentages, not vague terms)

⚠️ Issues Found:
- MEDIUM: Q4 projection ($6.3-6.5M, +22%) is not from source documents (should be labeled as "projected" or "estimated")
- LOW: Individual segment churn rate claim ("churn = new signups") is inferred, not directly stated in documents

📊 Quality Score: 9/10

🎯 Decision: APPROVE (with minor note)

💡 Recommendations:
- Clearly label Q4 projection as "Estimated based on trend" to avoid implying it's from documents
- Rephrase Individual segment observation as "0% growth suggests potential churn issue (hypothesis, not confirmed)"

Overall: Excellent work. Minor labeling improvements needed but not blocking.
```

---

## 🧩 Agent #5: Synthesizer Agent (Final Assembly)

### Purpose
**Combine multi-agent outputs into coherent final answer.** This agent takes results from all other agents and creates a unified, user-friendly response.

### Implementation

```python
class SynthesizerAgent:
    """
    Synthesizes outputs from multiple agents into final answer
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        
        self.agent = Agent(
            role="Executive Synthesizer",
            goal="Combine multi-agent findings into a clear, comprehensive answer",
            backstory="""You are an executive communication specialist. You excel at taking 
            complex, multi-source information and distilling it into clear, actionable insights.
            
            Your outputs are:
            - Structured (headings, bullet points, tables)
            - Comprehensive (incorporates all agent findings)
            - User-friendly (avoids jargon, explains concepts)
            - Executive-level (suitable for C-suite presentation)
            """,
            tools=[],
            llm=self.llm,
            verbose=True
        )
    
    def synthesize(self, agent_outputs: dict) -> str:
        """
        Combine outputs from all agents
        
        Args:
            agent_outputs: Dictionary with keys 'researcher', 'analyst', 'coder', 'critic'
        """
        task = Task(
            description=f"""
            Synthesize the following multi-agent outputs into a comprehensive final answer:
            
            🔍 Researcher Findings:
            {agent_outputs.get('researcher', 'N/A')}
            
            📊 Analyst Insights:
            {agent_outputs.get('analyst', 'N/A')}
            
            💻 Coder Output:
            {agent_outputs.get('coder', 'N/A')}
            
            🔍 Critic Review:
            {agent_outputs.get('critic', 'N/A')}
            
            Create a final answer that:
            1. Starts with a direct answer to the user's question
            2. Provides key findings (from Researcher and Analyst)
            3. Includes visualizations if generated (from Coder)
            4. Acknowledges any limitations noted by Critic
            5. Ends with recommendations
            
            Format:
            ## Answer
            [Direct answer]
            
            ## Key Findings
            - Finding 1
            - Finding 2
            
            ## Visualizations
            [Code or link to charts]
            
            ## Recommendations
            - Recommendation 1
            - Recommendation 2
            """,
            agent=self.agent,
            expected_output="Comprehensive, user-friendly final answer"
        )
        
        from crewai import Crew
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        return result


# Complete multi-agent workflow
def multi_agent_query(user_query: str, user_id: str):
    """
    Execute complete multi-agent workflow
    """
    print(f"\n{'='*60}")
    print(f"MULTI-AGENT WORKFLOW: {user_query}")
    print(f"{'='*60}\n")
    
    # Initialize all agents
    researcher = ResearcherAgent(user_id=user_id)
    analyst = AnalystAgent()
    coder = CoderAgent()
    critic = CriticAgent()
    synthesizer = SynthesizerAgent()
    
    # Step 1: Research
    print("📚 Step 1: Research Phase...")
    research_findings = researcher.research(user_query)
    
    # Step 2: Analysis
    print("\n📊 Step 2: Analysis Phase...")
    analysis = analyst.analyze(research_findings)
    
    # Step 3: Code generation (if needed)
    print("\n💻 Step 3: Code Generation...")
    if "visualiz" in user_query.lower() or "chart" in user_query.lower():
        code = coder.generate_code("Create visualization", research_findings)
    else:
        code = "No visualization requested"
    
    # Step 4: Quality review
    print("\n🔍 Step 4: Quality Review...")
    review = critic.review(
        work_to_review=f"Research: {research_findings}\n\nAnalysis: {analysis}",
        source_documents=research_findings
    )
    
    # Step 5: Synthesis
    print("\n🧩 Step 5: Synthesis...")
    final_answer = synthesizer.synthesize({
        'researcher': research_findings,
        'analyst': analysis,
        'coder': code,
        'critic': review['review']
    })
    
    print(f"\n{'='*60}")
    print("FINAL ANSWER:")
    print(f"{'='*60}\n")
    print(final_answer)
    
    return final_answer


# Test
result = multi_agent_query(
    user_query="Analyze Q3 2024 revenue and create a trend visualization",
    user_id="user_1"
)
```

---

## 📊 Agent Comparison & Optimization

### LLM Selection Strategy

| Agent | Model | Cost/1K tokens | Why? |
|-------|-------|----------------|------|
| **Researcher** | GPT-4o-mini | $0.00015 | Simple retrieval, high volume |
| **Analyst** | GPT-4o | $0.0025 | Complex reasoning needed |
| **Coder** | GPT-4o | $0.0025 | Quality code generation |
| **Critic** | GPT-4o | $0.0025 | Careful validation |
| **Synthesizer** | GPT-4o | $0.0025 | Executive-level writing |

**Cost Optimization:**
- Use GPT-4o-mini for Researcher (80% of queries)
- Use GPT-4o for complex reasoning (20% of queries)
- **Total savings: 40% vs all-GPT-4**

---

## 🎓 Exercises

1. **Build a Researcher**: Create a ResearcherAgent with 3 custom tools
2. **Design an Analyst**: Implement calculation and trend analysis tools
3. **Create a Critic**: Build hallucination detection logic
4. **Complete Workflow**: Chain all 5 agents together
5. **Optimize Costs**: Replace appropriate agents with GPT-4o-mini

---

## 📚 Next Steps

**Next:** [Part 3: Inter-Agent Communication →](MULTI_AGENT_03_COMMUNICATION.md)

Learn how agents share state, hand off tasks, and maintain context.

---

*Created specifically for your Smart Document Chat multi-agent project*  
*Last Updated: January 11, 2026*
