# Project Athena - AI Development Guide

**Drug Intelligence Knowledge Graph API**

This file helps Claude Code understand the project structure, conventions, and workflows for efficient development.

---

## 🎯 Project Overview

**Purpose:** REST API providing access to a drug intelligence knowledge graph powered by Neo4j
**Tech Stack:** Python 3.12, Neo4j, HTTP Server
**Status:** Phase 1 Complete (Basic lookup), Phase 2 Planning (Pathway analysis)
**Priority:** High

---

## 📁 Project Structure

```
athena/
├── api/
│   └── server.py          # Main REST API server
├── data/                  # Neo4j data imports
├── scripts/               # Utility scripts
├── venv/                  # Python virtual environment
└── CLAUDE.md             # This file
```

---

## 🔧 Development Environment

### Local Setup
```bash
cd ~/Projects/athena

# Activate venv
source venv/bin/activate

# Install dependencies
pip install neo4j

# Run server
python api/server.py
```

### Server Deployment
- **Location:** lab-server:/home/vibhavaggarwal/athena
- **Service:** `systemctl status athena-api`
- **Port:** 8080
- **Neo4j:** localhost:7687

---

## 🚀 Workflow for Claude Code

### Making Changes
```bash
# 1. Navigate to project
cd ~/Projects/athena

# 2. Read current code
cat api/server.py

# 3. Make changes using Edit tool

# 4. Test locally
python api/server.py &
curl http://localhost:8080/health

# 5. Commit
git add .
git commit -m "feat: description"

# 6. Deploy
~/Projects/.meta/deploy.sh deploy athena
```

### Common Tasks

**Add New Endpoint:**
1. Read `server.py` to understand pattern
2. Add new route in `do_GET()` method
3. Implement handler method (e.g., `_handle_new_feature()`)
4. Add Cypher query if needed
5. Test with curl
6. Deploy

**Optimize Query:**
1. Locate query in `_handle_*()` method
2. Use Neo4j patterns (MATCH, WITH, RETURN)
3. Test query performance
4. Update code
5. Deploy

**Add Neo4j Data:**
1. Create script in `scripts/`
2. Use Neo4j driver connection
3. Batch insert for performance
4. Update API to expose new data

---

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/stats` | GET | Database statistics |
| `/molecule/{cid}` | GET | Get molecule by CID |
| `/molecule/search?name=X` | GET | Search molecules |
| `/suggest?disorder=X` | GET | Treatment suggestions (Phase 2) |

---

## 🔍 Code Patterns

### Neo4j Connection
```python
driver = Neo4jConnection.get_driver()
with driver.session() as session:
    result = session.run("MATCH ...", params)
    data = [dict(record) for record in result]
```

### Error Handling
```python
try:
    # Operation
except Exception as e:
    self._send_json({"error": str(e)}, 500)
```

### Response Format
```python
self._send_json({
    "data": result,
    "status": "success"
}, 200)
```

---

## 🧪 Testing

### Manual Testing
```bash
# Health check
curl http://localhost:8080/health

# Stats
curl http://localhost:8080/stats

# Search
curl "http://localhost:8080/molecule/search?name=aspirin"

# Get by CID
curl http://localhost:8080/molecule/2244
```

### Production Testing
```bash
ssh lab-server "curl http://localhost:8080/health"
```

---

## 🚨 Common Issues

### Issue: Neo4j Connection Failed
**Solution:** Check if Neo4j is running
```bash
ssh lab-server "systemctl status neo4j"
```

### Issue: Import Error
**Solution:** Activate venv first
```bash
source venv/bin/activate
```

### Issue: Port Already in Use
**Solution:** Kill existing process
```bash
lsof -ti:8080 | xargs kill -9
```

---

## 📝 Code Standards

### Commit Messages
- `feat:` - New feature (e.g., new endpoint)
- `fix:` - Bug fix
- `refactor:` - Code improvement
- `perf:` - Performance optimization
- `docs:` - Documentation update

### Code Style
- Use environment variables for config
- Clear function names (`_handle_*`, `_get_*`)
- Error handling in all endpoints
- CORS headers for browser access
- Meaningful log messages

---

## 🎯 Phase 2 Roadmap

### Planned Features
1. **Pathway Analysis**
   - Drug-target-disease relationships
   - Multi-hop graph traversal
   - Visualization endpoints

2. **Advanced Search**
   - Similarity search
   - Compound structure search
   - Property-based filters

3. **Caching**
   - Redis integration
   - Query result caching
   - Improve response time

---

## 🔗 Dependencies

### Python Packages
```
neo4j==5.x
```

### System Requirements
- Python 3.12+
- Neo4j 5.x running
- 512MB RAM minimum

---

## 📚 Useful Cypher Queries

### Get Node Count
```cypher
MATCH (m:Molecule)
RETURN count(m)
```

### Search by Name
```cypher
MATCH (m:Molecule)
WHERE toLower(m.name) CONTAINS toLower($name)
RETURN m
LIMIT 20
```

### Get Statistics
```cypher
MATCH (m:Molecule)
WHERE m.weight IS NOT NULL
RETURN count(m) as total,
       avg(toFloat(m.weight)) as avg_weight
```

---

## 🤖 Claude Code Optimization Tips

1. **Always read the file before editing** - Understand context
2. **Test queries in Neo4j browser first** - Validate Cypher
3. **Use existing patterns** - Follow `_handle_*` convention
4. **Keep changes focused** - One feature per commit
5. **Deploy incrementally** - Test each change

---

## 📞 Quick Commands

```bash
# Start development
cd ~/Projects/athena && source venv/bin/activate

# Run server
python api/server.py

# Deploy
~/Projects/.meta/deploy.sh deploy athena

# Check logs
ssh lab-server "journalctl -u athena-api -f"

# Neo4j browser
ssh lab-server -L 7474:localhost:7474 -L 7687:localhost:7687
# Then open http://localhost:7474
```

---

**Last Updated:** 2026-01-17
**Maintained by:** Claude Code
