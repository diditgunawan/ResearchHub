# Privacy Notice & Data Protection Policy (ETH-011, QAS-022)

**Last Updated:** October 2026  
**Compliance Standards:** Indonesian Personal Data Protection Law (UU No. 27/2022 - UU PDP), EU General Data Protection Regulation (GDPR), Taiwan PDPA, and COPE Research Ethics.

---

## 1. Scope & Lawful Basis of Processing
ResearchForge provides an academic evidence synthesis, literature screening, and journal matching platform for scholarly researchers. We process personal and confidential research data under the following lawful bases:
- **Contractual Necessity (UU PDP Art. 20(2)(b) / GDPR Art. 6(1)(b))**: Provision of user accounts, magic-link session management, and project tenancy.
- **Legitimate Academic & Research Interests (GDPR Art. 6(1)(f))**: Grounded citation extraction, PRISMA 2020 flow computation, and scientific consensus verification.
- **Explicit Consent (UU PDP Art. 20(2)(a) / GDPR Art. 6(1)(a))**: Optional submission of unpublished draft manuscripts for journal fit matching and positioning analysis.

---

## 2. Data Classification & Security Controls

| Data Category | Representative Data | Processing Environment | Retention & Deletion Policy |
|---|---|---|---|
| **Public Academic Metadata** | Paper titles, abstracts, DOIs, publication years, author names | Shared read-only cache; OpenAlex/Crossref indexed | Persistent public cache; updated semi-annually |
| **Confidential Project Data** | Screening decisions, exclusion notes, PICO criteria, custom collections | Project-scoped database tables with strict tenant RBAC | Retained for the project lifecycle; purged 30 days after tenant deletion |
| **Highly Confidential Manuscripts** | Draft PDF uploads, working abstracts submitted to Journal Matcher | In-memory tokenization only; `retain_text=false` default | Zero persistent disk storage; vectors purged immediately upon session completion |
| **Identity & Authentication** | User email address, ephemeral magic tokens, session cookies | PII isolated table; Bcrypt/Argon2 hashing | Magic links expire in 15 minutes; session tokens expire in 7 days |

---

## 3. Strict Non-Training & Anti-Fabrication Guarantee
1. **Zero LLM Training on User Data**: User research notes, screening decisions, and unpublished draft manuscripts are **never** used to train, fine-tune, or adapt artificial intelligence models.
2. **Deterministic Retrieval Grounding**: All generative claim extractions require explicit chunk citations with verifiable DOIs. Hallucinated synthetic claims are strictly rejected by the Sufficiency Gate.
3. **No Cross-Tenant Information Disclosure**: Every database query is strictly partitioned by `project_id` and verified through RBAC middleware (`owner`, `reviewer`, `viewer`).

---

## 4. Data Subject Rights & Regional Compliance
Users hold full rights to access, rectify, export, and erase their personal data:
- **Right to Erasure (Right to be Forgotten)**: Deleting a project triggers a cascading purge of all associated library items, screening decisions, and extracted RAG vectors within 30 days.
- **Data Portability**: Users can export their entire evidence library, screening audit logs, and PRISMA flows in standard formats (RIS, BibTeX, JSON, CSV).
- **Indonesian UU PDP Compliance**: Sovereign data residency options available; Data Protection Officer (DPO) contact provided at `dpo@researchforge.io`.
