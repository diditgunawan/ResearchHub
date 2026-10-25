# Sub-processors Register (ETH-011, QAS-022)

Authoritative register of third-party data processors engaged by ResearchForge for scholarly literature processing, vector embeddings, transactional authentication, and infrastructure hosting.

| Provider | Service Purpose | Data Transmitted | Data Center Region | Training Opt-out / Retention Guarantee | Terms & DPA Documentation | Verification Status |
|---|---|---|---|---|---|---|
| **Google Cloud / Vertex AI** | Grounded claim extraction, verification, & bilingual disclosures | Verbatim paper chunks & review queries | `us-central1`, `asia-southeast1` | Zero-retention enterprise tier; customer prompts are never used for foundation model training | [Google Cloud DPA](https://cloud.google.com/terms/data-processing-addendum) | **VERIFIED** |
| **OpenAlex (OurResearch)** | Scholarly literature metadata & citation graph lookups | Cleaned search queries & DOI strings | Global CDN (`us-east-1`) | Open data public catalog; zero personal identifiable data transmitted | [OpenAlex Terms](https://openalex.org/terms) | **VERIFIED** |
| **Crossref (PILA)** | DOI registration metadata, funder info, & retraction lookups | Target DOI identifiers | Global CDN (`us-east-1`) | Open scholarly metadata; zero user telemetry transmitted | [Crossref Policy](https://www.crossref.org/documentation/metadata-retrieval/) | **VERIFIED** |
| **PostgreSQL / pgvector (Self-Hosted / Managed)** | Relational entities, screening logs, and vector embeddings | Tenant projects, library items, 384-d semantic vectors | Sovereign local / VPC (`ap-southeast-3` Jakarta / EU Frankfurt) | Encrypted at rest (AES-256); strict tenant isolation via `project_id` foreign keys | Sovereign VPC Hosting | **VERIFIED** |
| **Transactional Mail (Postmark / SendGrid)** | Passwordless magic-link authentication delivery | User email address & single-use ephemeral token | Global edge | Ephemeral 15-minute TTL; email body logs automatically scrubbed after 7 days | GDPR & ISO 27001 Certified | **VERIFIED** |
