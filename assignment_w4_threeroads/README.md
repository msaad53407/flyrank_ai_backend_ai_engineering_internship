# Week 4 · Assignment — Three Roads: Choose Your Stack with AI

This assignment evaluates three potential technical stack architectures under strict boundary constraints ($0 cost, free hosting, rapid build timeline, and dynamic media display).

---

## 🛑 Boundary Constraints

1. **Cost Constraint:** $0 / Free Tier infrastructure only.
2. **Proficiency:** Python (FastAPI), SQL, HTML5, Vanilla CSS, Docker, JavaScript.
3. **Functional Requirements:** Static portfolio pages, interactive REST API demos, code blocks, terminal logs.
4. **Build Timeline:** Must deploy within 2 weeks without maintenance overhead.

---

## 🛣️ The Three Roads (Architecture Options)

| Metric | Road 1: Static HTML/CSS/JS (GitHub Pages) | Road 2: Next.js + Tailwind (Vercel) | Road 3: FastAPI Backend + Vite SPA |
|---|---|---|---|
| **Hosting Cost** | $0 (GitHub Pages) | $0 (Vercel Free) | $0 (Render / Render Free Tier) |
| **Complexity** | Low (Zero dependencies, fast load) | Medium (React hydration, npm packages) | High (Requires active server infrastructure) |
| **Maintenance** | Zero maintenance | Moderate (Dependency updates) | High (Database sleeping / cold starts) |
| **Suitability** | **Perfect for initial static proof** | Great for SSR blogs | Overkill for static portfolio site |

---

## 💡 Chosen Stack Rationale

**Selected Architecture:** **Road 1 — Vanilla HTML5 / Modern CSS / GitHub Pages**

### Justification:
1. **Zero Maintenance & Instant Load:** Static HTML/CSS hosted on GitHub Pages has zero build step failures, zero cold starts, and loads instantly across all devices.
2. **Focus on Code Proof:** The backend engineering proof resides inside our open-source GitHub repositories (`assignment_2`, `assignment_3`, `assignment_fl04`). A lightweight static site keeps the focus entirely on code artifacts and live terminal outputs.
3. **No Over-Engineering:** Building a complex SSR app to render a 4-page portfolio violates the core engineering principle of choosing the simplest tool for the job.
