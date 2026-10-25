# Academic Integrity, AI Ethics & Publication Disclosure Policy (ETH-001..ETH-015)

**Standards Alignment:** Committee on Publication Ethics (COPE), International Committee of Medical Journal Editors (ICMJE), WAME AI Guidelines, and Indonesian National Research and Innovation Agency (BRIN) Scientific Ethics.

---

## 1. Principles of Computational Literature Synthesis

ResearchForge adheres to strict integrity principles to ensure AI-assisted academic workflows remain transparent, verifiable, and free of algorithmic delusion:

1. **Zero Citation Fabrication**:
   Every claim synthesized by ResearchForge must cite a verified digital object identifier (DOI) and verbatim excerpt from real scholarly literature. Generation of plausible-sounding but synthetic DOIs or non-existent authors is treated as a critical system fault and mathematically blocked by the verification gate.
2. **Sufficiency Gate Refusal Policy**:
   If a research query retrieves fewer than **3 distinct, peer-reviewed sources**, the synthesis engine explicitly refuses to generate summary claims, outputting an RFC 7807 problem detail with code `INSUFFICIENT_EVIDENCE`.
3. **Immutable Screening Ledger**:
   Dual blind screening decisions are recorded in an append-only log. Reviewers cannot inspect each other's verdicts until both have submitted their assessments, guaranteeing unbiased inter-rater reliability measured via Cohen's Kappa ($\kappa$).
4. **Retraction Watch Integration**:
   Every imported reference is continuously cross-checked against live Retraction Watch and Crossref status feeds. Retracted or flagged publications are immediately highlighted with prominent warning banners.

---

## 2. Bilingual AI Usage Disclosure Policy

In accordance with ICMJE and COPE recommendations, authors utilizing ResearchForge must include an unambiguous statement of AI assistance in their manuscript methodology or acknowledgments. ResearchForge auto-generates bilingual disclosure statements:

### English Standard Disclosure (ICMJE & Elsevier Aligned)
> *"Declaration of Generative AI and AI-assisted Technologies in the Writing Process: During the preparation of this work, the author(s) used ResearchForge (powered by grounded retrieval and semantic ranking) in order to systematically screen candidate literature, evaluate inter-reviewer agreement (Cohen's kappa), and map epistemological lineage. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article."*

### Indonesian Standard Disclosure (SINTA & BRIN Aligned)
> *"Pernyataan Penggunaan Kecerdasan Buatan (AI) dalam Proses Penelitian: Selama penyusunan karya ini, penulis menggunakan ResearchForge (didukung oleh temu kembali berbasis bukti terverifikasi dan pemeringkatan semantik) untuk menyaring literatur secara sistematis, mengevaluasi kesepakatan antar-penelaah (Cohen's kappa), dan memetakan silsilah epistemologis. Setelah menggunakan perangkat ini, penulis memeriksa dan menyunting seluruh konten secara mandiri dan bertanggung jawab penuh atas substansi artikel yang dipublikasikan."*

---

## 3. Epistemological Lineage Invariants

To avoid distorted scientific narratives and historical revisionism, the Genealogical Lineage DAG engine enforces strict mathematical and epistemological rules:
- **Strict Chronological Arrow of Time**:
  A paper published in year $Y_1$ can **never** be designated as the intellectual descendant of a paper published in year $Y_2$ if $Y_1 < Y_2$. All directed edges $(p, c)$ satisfy:
  $$\text{Year}(p) \le \text{Year}(c)$$
- **Non-Novelty Disclaimers**:
  When positioning a new manuscript relative to prior art, ResearchForge explicitly prints:
  > *"Positioned relative to the analyzed corpus only — this does not constitute a legal or global claim of novelty or absence of prior art."*
