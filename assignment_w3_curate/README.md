# Week 3 · Assignment — Kill your darlings: Curate Your Images

This assignment audits visual assets, prioritizes authentic technical terminal captures over artificial AI mockups, and documents visual curation decisions.

---

## 📷 Curated Visual Assets Audit

| Asset Name | Asset Type | Purpose | Source / Method |
|---|---|---|---|
| **`terminal_docker_up.png`** | Real Capture | Live Docker Compose container logs & healthcheck | Real Terminal Screenshot |
| **`pytest_results.png`** | Real Capture | 100% passing unit test suite output | Real Terminal Screenshot |
| **`architecture_repo_pattern.png`** | Diagram | Repository Pattern class architecture | Mermaid.js Generated Diagram |
| **`headshot_developer.png`** | Real Photo | Professional developer profile representation | Real Photograph |
| **`slate_grid_texture.png`** | Background | Subtle dark slate grid hero background | AI Generated (Curated) |

---

## 🗑️ Rejection Notes & Curation Rationale

### Rejection Case 1: AI-Generated 3D Server Room Render
- **AI Generation Attempt:** Generated a flashy 3D futuristic glowing server room image for the database case study.
- **Why Rejected:** It looked like generic stock photography and communicated zero technical substance. An Engineering Lead wants to see real terminal outputs (`docker compose ps`, `pytest` logs) and SQL queries, not generic glowing server racks.
- **Decision:** Replaced with a real cropped terminal capture showing `tasks_postgres_db Up (healthy)` and HTTP response JSON.

### Rejection Case 2: AI-Generated Stylized Avatar
- **AI Generation Attempt:** Generated a futuristic cyber-style AI portrait avatar for the About section.
- **Why Rejected:** Undermined professional credibility and authentic human identity.
- **Decision:** Used a clear, professional photograph against a neutral background.
