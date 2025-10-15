# 🎯 System Prompts - Enhanced for Software Development

## Overview

Each persona has been optimized with detailed, structured system prompts that provide:
- **Clear instructions** on what to do and how
- **Checklists and frameworks** for consistent quality
- **Output formatting guidelines** for predictable responses
- **Context-specific knowledge** relevant to .NET development

---

## 🧑‍💻 dev-agent (Code Implementation)

### Key Improvements:
1. **Core Principles Section**: SOLID, security, performance, containerization
2. **Code Quality Requirements**: Naming, method size, documentation standards
3. **Generation Guidelines**: Complete code, no placeholders, proper error handling
4. **Structured Output**: Approach → Code → Explanation → Testing

### What Makes It Better:
- ✅ Explicitly requires **complete, compilable code** (no `// TODO` comments)
- ✅ Mandates **XML documentation** for public APIs
- ✅ Enforces **nullable reference types** and explicit null handling
- ✅ Requires **explanation of trade-offs** after code
- ✅ Suggests **testing approaches** proactively

### Example Capabilities:
- Generate REST API controllers with full CRUD operations
- Implement authentication/authorization with JWT
- Create EF Core repositories with best practices
- Build async services with proper error handling

---

## 🏗️ arch-agent (Architecture & Design)

### Key Improvements:
1. **Architectural Expertise**: DDD, CQRS, Event Sourcing, Cloud-native
2. **Decision Framework**: First-principles, explicit trade-offs (CAP, consistency models)
3. **Deployment Knowledge**: K8s patterns, service mesh, observability
4. **Structured Output**: 7-step format from analysis to success metrics

### What Makes It Better:
- ✅ Uses **first-principles reasoning** instead of cargo-culting
- ✅ Presents **2-3 options with pros/cons** before recommending
- ✅ Generates **Mermaid diagrams** automatically for visual clarity
- ✅ Includes **risk analysis** and **mitigation strategies**
- ✅ Defines **SLIs/SLOs** for measurable success

### Example Capabilities:
- Design microservices architecture with service boundaries
- Evaluate database strategies (SQL vs NoSQL, sharding, replication)
- Plan API gateway and service mesh implementations
- Create observability stack (metrics, logs, traces)

---

## 🧪 test-agent (Testing & QA)

### Key Improvements:
1. **Test Pyramid Strategy**: 70% unit, 20% integration, 10% e2e
2. **Comprehensive Coverage**: Happy paths, edges, errors, concurrency, security
3. **Framework Specifics**: xUnit, Moq, FluentAssertions, TestContainers
4. **Quality Standards**: AAA pattern, naming conventions, independence

### What Makes It Better:
- ✅ Follows **test pyramid** for optimal test distribution
- ✅ Uses **TestContainers** for realistic integration tests
- ✅ Enforces **proper naming**: `MethodName_Scenario_ExpectedBehavior`
- ✅ Includes **security tests** (SQL injection, XSS, auth bypasses)
- ✅ Suggests **additional test scenarios** proactively

### Example Capabilities:
- Generate unit tests with Moq for dependency isolation
- Create integration tests with TestContainers (databases, Redis, etc.)
- Build E2E tests for critical user workflows
- Test concurrency and race conditions

---

## 🗂️ plan-agent (Detailed Planning)

### Key Improvements:
1. **8-Section Structure**: From executive summary to risk analysis
2. **Functional Requirements**: User stories with Given-When-Then acceptance criteria
3. **Non-Functional Requirements**: Performance, scalability, security (with metrics!)
4. **Technical Approach**: Stack, DB schema, API contracts, containers
5. **Implementation Roadmap**: Phased with DoD and dependencies

### What Makes It Better:
- ✅ Uses **specific, measurable metrics** (e.g., "API responds in <200ms p95")
- ✅ Includes **DevOps pipeline** design in planning
- ✅ Provides **task breakdown with estimates** and DoD
- ✅ Identifies **risks with mitigation strategies**
- ✅ Defines **observable success criteria**

### Example Capabilities:
- Create comprehensive spec for new microservices
- Plan authentication/authorization implementation
- Design data migration strategies
- Specify monitoring and alerting requirements

---

## ⚡ plan-lite-agent (Quick Planning)

### Key Improvements:
1. **5-Part Quick Spec**: Goal, Scope, Requirements, Tasks, Metrics
2. **Concise Format**: Max 300 words, bullet points
3. **Action-Oriented**: Developer can start immediately
4. **Priority-Focused**: Tasks ordered by importance

### What Makes It Better:
- ✅ **Under 300 words** - respects developer time
- ✅ Uses **checkbox format** for task tracking
- ✅ Includes **time estimates** per task
- ✅ Specifies **Definition of Done** for each task
- ✅ Clear **success metrics** (1-3 only)

### Example Capabilities:
- Quick sprint planning for user stories
- Break down features into daily tasks
- Create agile task cards with acceptance criteria
- Rapid feature scoping

---

## 🔀 orch-agent (Request Router)

### Key Improvements:
1. **Persona Directory**: Clear description of each persona's role
2. **Routing Logic**: Analyze intent → Select specific persona → Justify
3. **Examples Provided**: Shows routing decisions for common requests
4. **Concise Responses**: Under 50 words

### What Makes It Better:
- ✅ **Explicit routing format**: "Route to: [persona] - Reason: [why]"
- ✅ Includes **routing examples** in system prompt
- ✅ Selects **most specific** persona for the task
- ✅ Keeps responses **under 50 words**

### Example Capabilities:
- Analyze vague requests and route to appropriate persona
- Suggest correct agent for debugging vs development
- Route architecture questions vs implementation tasks

---

## 👁️ review-agent (Code Review)

### Key Improvements:
1. **5-Category Checklist**: Security, Performance, Maintainability, Reliability, Best Practices
2. **Detailed Security Review**: SQL injection, XSS, auth/authz, sensitive data
3. **Performance Analysis**: N+1, async/await, LINQ efficiency, memory leaks
4. **SOLID Evaluation**: Explicit check for each principle
5. **Structured Output**: Severity → Location → Problem → Impact → Fix → Why

### What Makes It Better:
- ✅ **Systematic checklist** covering 30+ common issues
- ✅ **Severity ratings**: Critical/High/Medium/Low with priority guidance
- ✅ Provides **corrected code examples** for each issue
- ✅ Explains **why** the fix matters (educational)
- ✅ **Summary with issue counts** at the end

### Example Capabilities:
- Detect SQL injection vulnerabilities
- Identify N+1 query problems in EF Core
- Find SOLID principle violations
- Spot concurrency issues (race conditions, deadlocks)

---

## 🐛 debug-agent (Debugging)

### Key Improvements:
1. **Systematic Methodology**: Gather info → Check common pitfalls → Root cause
2. **Common Pitfall Categories**: Async/await, EF Core, DI, Concurrency, Memory, Docker
3. **Root Cause Focus**: Explain WHY (not just WHAT)
4. **7-Section Output**: Analysis → Root Cause → Why → Reproduction → Fix → Verification → Prevention

### What Makes It Better:
- ✅ **Comprehensive pitfall database** covering .NET-specific issues
- ✅ Explains **mechanism** behind errors (educational)
- ✅ Provides **minimal reproduction example**
- ✅ Includes **verification steps** to confirm fix
- ✅ Suggests **prevention strategies** for future

### Example Capabilities:
- Debug async/await deadlocks
- Trace EF Core lazy loading exceptions
- Identify dependency injection lifetime issues
- Analyze Docker environment misconfigurations

---

## ♻️ refactor-agent (Code Improvement)

### Key Improvements:
1. **Code Smell Taxonomy**: 5 categories (Bloaters, OO Abusers, Change Preventers, Dispensables, Couplers)
2. **Design Pattern Library**: Creational, Structural, Behavioral, Architectural patterns
3. **SOLID Violation Detection**: Specific fixes for each principle
4. **Before/After Format**: Clear comparison with benefits explained

### What Makes It Better:
- ✅ **Comprehensive code smell detection** (20+ smells)
- ✅ Suggests **appropriate design patterns** with rationale
- ✅ Shows **metrics improvement** (e.g., "Complexity reduced from 15 to 5")
- ✅ Explains **benefits** of each refactoring
- ✅ Includes **testing strategy** to preserve behavior

### Example Capabilities:
- Extract methods from long functions
- Apply Repository pattern to data access
- Introduce Strategy pattern for algorithm selection
- Split god classes into cohesive components

---

## 📝 docs-agent (Documentation)

### Key Improvements:
1. **6 Documentation Types**: API, Architecture, Setup, User guides, Troubleshooting, Code comments
2. **Standards Framework**: Clarity, Completeness, Maintainability
3. **Markdown Formatting**: Code blocks, tables, admonitions, Mermaid diagrams
4. **XML Documentation**: Complete template with examples

### What Makes It Better:
- ✅ **Type-specific formats** for each documentation category
- ✅ **OpenAPI/Swagger compatible** API documentation
- ✅ Generates **Mermaid diagrams** for architecture
- ✅ Uses **admonitions** (⚠️ Warning, 💡 Tip, ℹ️ Note)
- ✅ Includes **working code examples**

### Example Capabilities:
- Generate OpenAPI/Swagger documentation
- Create architecture diagrams (sequence, component, deployment)
- Write setup guides with troubleshooting
- Build comprehensive API references

---

## 📊 Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Length** | 1-2 sentences | 30-50 lines with structure |
| **Specificity** | Generic instructions | Detailed checklists and frameworks |
| **Output Format** | Undefined | Structured with clear sections |
| **Education** | Minimal | Explains WHY and principles |
| **Consistency** | Variable | Predictable due to templates |
| **Actionability** | Sometimes vague | Always actionable |

---

## 🎯 Impact on Output Quality

### Before (Generic):
```
User: "Review this code"
Agent: "This code has some issues with error handling and performance."
```

### After (Structured):
```
User: "Review this code"
Agent:
## [CRITICAL] SQL Injection Vulnerability
**Location**: Line 45, UserRepository.GetUserByName
**Problem**: Using string concatenation in SQL query
**Impact**: Attacker can execute arbitrary SQL commands
**Fix**: 
```csharp
// Before
var query = $"SELECT * FROM Users WHERE Name = '{name}'";

// After
var query = "SELECT * FROM Users WHERE Name = @name";
command.Parameters.AddWithValue("@name", name);
```
**Why**: Parameterized queries prevent SQL injection by treating input as data, not code.
```

---

## 🚀 Usage Tips

1. **Be Specific in Requests**: The more context you provide, the better the output
2. **Follow Suggested Formats**: Agents will naturally follow their structured formats
3. **Iterate**: Use output from one agent as input to another (e.g., plan → dev → review → test)
4. **Educational Mode**: Agents explain WHY, not just WHAT - great for learning

---

## 🔄 Continuous Improvement

These prompts can be further customized based on:
- Your team's specific coding standards
- Additional design patterns you use
- Custom architecture patterns
- Organization-specific security requirements

To modify: Edit the `PERSONAS` dictionary in `setup_ollama_local.py` and recreate the persona with `--create`.

---

**Last Updated**: October 2025  
**Version**: 4.0 (Enhanced System Prompts)
