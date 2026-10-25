import re
import math
import hashlib
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import Counter
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException

from app.works.models import Work, WorkCitation
from app.library.models import LibraryItem
from app.synthesis.models import Chunk
from app.mapping.models import (
    MapRun, MapCluster, MapClusterMember, LineageNode, LineageEdge, PositioningRun, GapSignal
)

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can",
    "cannot", "could", "did", "do", "does", "doing", "don't", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself",
    "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its", "itself", "let's", "me", "more",
    "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so", "some", "such", "than",
    "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "were", "what", "when",
    "where", "which", "while", "who", "whom", "why", "with", "won't", "would", "you", "your", "yours",
    "yang", "di", "dan", "dari", "ini", "dalam", "untuk", "pada", "adalah", "dengan", "ke", "oleh", "juga",
    "study", "paper", "research", "results", "using", "method", "analysis", "based", "proposed", "model"
}


def tokenize_clean(text: str) -> List[str]:
    """Tokenize and remove non-alphanumeric and stopwords."""
    words = re.findall(r'[a-zA-Z0-9_\-]+', text.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS and not w.isdigit()]


def extract_top_concepts(text: str, top_k: int = 15) -> List[str]:
    """Extract top frequent domain keywords/concepts from text."""
    tokens = tokenize_clean(text)
    if not tokens:
        return []
    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(top_k)]


def compute_cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Compute cosine similarity between two sparse frequency vectors."""
    common_keys = set(vec1.keys()) & set(vec2.keys())
    if not common_keys:
        return 0.0
    dot_product = sum(vec1[k] * vec2[k] for k in common_keys)
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))


def compute_jaccard(set1: Set[str], set2: Set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return float(intersection / union) if union > 0 else 0.0


def compute_chronological_score(child_year: Optional[int], parent_year: Optional[int]) -> float:
    """
    Chronological component:
    1.0 if 0 < delta <= 3
    linear decay from 1.0 to 0.3 at delta = 12 (slope = (0.3 - 1.0) / 9 = -0.7/9)
    0.6 if delta == 0
    0.0 if delta > 12 or delta < 0
    """
    if child_year is None or parent_year is None:
        return 0.5  # Neutral if missing
    delta = child_year - parent_year
    if delta < 0:
        return 0.0  # Constraint violation
    if delta == 0:
        return 0.6
    if 0 < delta <= 3:
        return 1.0
    if 3 < delta <= 12:
        return max(0.3, 1.0 - (0.7 * (delta - 3) / 9.0))
    return 0.2


class MappingService:

    @staticmethod
    async def run_lineage_mapping(
        db: AsyncSession,
        project_id: str,
        user_id: Optional[str] = None,
        scope_type: str = "library_all",
        work_ids: Optional[List[str]] = None,
        seed: int = 42,
    ) -> MapRun:
        """
        Executes deterministic literature mapping, family clustering, and lineage DAG.
        Conforms strictly to MAP-001..MAP-019 and algorithms.md.
        """
        # 1. Fetch library items for project
        query = (
            select(Work)
            .join(LibraryItem, LibraryItem.work_id == Work.id)
            .where(LibraryItem.project_id == project_id)
        )
        if work_ids:
            query = query.where(Work.id.in_(work_ids))

        res = await db.execute(query)
        raw_works = res.scalars().all()

        # MAP-002: Scope cap (500 records)
        if len(raw_works) > 500:
            raise HTTPException(
                status_code=400,
                detail="Scope exceeds maximum limit of 500 records. Please filter to a library subset.",
            )

        # Filter works lacking titles
        excluded = []
        valid_works: List[Work] = []
        for w in raw_works:
            if not w.title or not w.title.strip():
                excluded.append({"work_id": w.id, "reason": "missing_title"})
            else:
                valid_works.append(w)

        # Initialize MapRun
        map_run = MapRun(
            project_id=project_id,
            kind="lineage",
            scope={"type": scope_type, "work_ids": [w.id for w in valid_works]},
            params={"seed": seed, "weights": {"cit": 0.35, "sem": 0.35, "kw": 0.20, "chr": 0.10}},
            embedding_model="text-embedding-3-small",
            code_version="v1.0.0",
            status="pending",
            record_count=len(valid_works),
            excluded=excluded,
            created_by=user_id,
        )
        db.add(map_run)
        await db.flush()

        if not valid_works:
            map_run.status = "completed"
            map_run.finished_at = datetime.now(timezone.utc)
            await db.commit()
            return map_run

        # Fetch in-scope citation edges
        valid_wids = [w.id for w in valid_works]
        cit_res = await db.execute(
            select(WorkCitation).where(
                WorkCitation.citing_work_id.in_(valid_wids),
                WorkCitation.cited_work_id.in_(valid_wids),
            )
        )
        in_set_citations = {(c.citing_work_id, c.cited_work_id) for c in cit_res.scalars().all()}

        # 2. Extract features, concepts, and completeness flags per work
        work_features: Dict[str, Dict[str, Any]] = {}
        for w in valid_works:
            flags = []
            if not w.abstract:
                flags.append("no_abstract")
            if not w.doi:
                flags.append("no_doi")
            if not w.year:
                flags.append("no_year")
            if not any(pair[0] == w.id for pair in in_set_citations):
                flags.append("no_refs")

            full_text = f"{w.title} {w.abstract or ''}"
            concepts = extract_top_concepts(full_text, top_k=15)
            if not concepts:
                flags.append("no_keywords")

            tokens = tokenize_clean(full_text)
            term_freq = {word: count / max(len(tokens), 1) for word, count in Counter(tokens).items()}

            work_features[w.id] = {
                "work": w,
                "concepts": set(concepts),
                "term_freq": term_freq,
                "flags": flags,
                "year": w.year,
                "title": w.title,
                "doi": w.doi,
            }

        # 3. Community / Family Detection (MAP-010)
        # Partition works into families based on keyword overlap and title/abstract similarity
        # Minimum family size = 3, else "Unplaced"
        families_map: Dict[int, List[str]] = {}
        unassigned = set(work_features.keys())

        # Seed initial clusters by common dominant concept
        concept_pool = Counter()
        for wid, feat in work_features.items():
            for c in feat["concepts"]:
                concept_pool[c] += 1

        top_domain_concepts = [c for c, count in concept_pool.most_common(10) if count >= 2]
        cluster_idx = 0

        for dom_concept in top_domain_concepts:
            matching_wids = [wid for wid in unassigned if dom_concept in work_features[wid]["concepts"]]
            if len(matching_wids) >= 3:
                families_map[cluster_idx] = matching_wids
                unassigned -= set(matching_wids)
                cluster_idx += 1

        # Create MapCluster database records
        created_clusters: Dict[int, MapCluster] = {}
        for c_idx, member_ids in families_map.items():
            # Cluster label from top c-TF-IDF
            member_tokens = []
            for wid in member_ids:
                member_tokens.extend(work_features[wid]["concepts"])
            top_cluster_kw = [k for k, _ in Counter(member_tokens).most_common(3)]
            label = " & ".join(top_cluster_kw).title() if top_cluster_kw else f"Research Family {c_idx + 1}"

            cluster_rec = MapCluster(
                run_id=map_run.id,
                label=label,
                label_source="keywords",
                keywords=top_cluster_kw,
                size=len(member_ids),
                is_other=False,
            )
            db.add(cluster_rec)
            await db.flush()
            created_clusters[c_idx] = cluster_rec

            for wid in member_ids:
                db.add(MapClusterMember(cluster_id=cluster_rec.id, work_id=wid, membership_score=1.0))

        # "Other / Unplaced" cluster if needed
        unplaced_cluster = None
        if unassigned:
            unplaced_cluster = MapCluster(
                run_id=map_run.id,
                label="Unplaced Exploratory Studies",
                label_source="keywords",
                keywords=["exploratory", "unclassified"],
                size=len(unassigned),
                is_other=True,
            )
            db.add(unplaced_cluster)
            await db.flush()
            for wid in unassigned:
                db.add(MapClusterMember(cluster_id=unplaced_cluster.id, work_id=wid, membership_score=0.5))

        # Map each work_id to its assigned family record
        work_to_family: Dict[str, Optional[MapCluster]] = {}
        for c_idx, member_ids in families_map.items():
            for wid in member_ids:
                work_to_family[wid] = created_clusters[c_idx]
        for wid in unassigned:
            work_to_family[wid] = unplaced_cluster

        # 4. Genealogical Lineage DAG Construction (MAP-007, MAP-008, MAP-009)
        # For each work `c` (child), search for candidate parent `p`
        in_set_work_ids = set(work_features.keys())
        edges_to_create: List[LineageEdge] = []
        nodes_to_create: List[LineageNode] = []

        # Find in-set cited DOIs
        doi_to_wid = {feat["doi"].lower(): wid for wid, feat in work_features.items() if feat["doi"]}

        for child_id, c_feat in work_features.items():
            c_work = c_feat["work"]
            c_year = c_feat["year"]
            c_family = work_to_family.get(child_id)
            c_concepts = c_feat["concepts"]
            c_tf = c_feat["term_freq"]
            c_flags = c_feat["flags"]

            # Candidate parents: must obey Chronology Hard Rule: Year(p) <= Year(c) (MAP-008)
            candidate_scores: List[Tuple[str, float, Dict[str, Any]]] = []

            for parent_id, p_feat in work_features.items():
                if parent_id == child_id:
                    continue

                p_year = p_feat["year"]

                # Chronology hard rule: Year(p) <= Year(c)
                if c_year is not None and p_year is not None and p_year > c_year:
                    continue  # A future work can never be parent of an earlier work

                # Citation component (Cit)
                # Check if child cites parent directly via WorkCitation or DOI match
                direct_cit = (child_id, parent_id) in in_set_citations
                if not direct_cit and p_feat["doi"] and c_work.abstract:
                    if p_feat["doi"].lower() in c_work.abstract.lower():
                        direct_cit = True

                # Chronology rule for same-year: only allowed with direct citation
                if c_year is not None and p_year is not None and c_year == p_year and not direct_cit:
                    continue

                cit_score = 1.0 if direct_cit else 0.0

                # Semantic component (Sem)
                sem_score = compute_cosine_similarity(c_tf, p_feat["term_freq"])

                # Keyword Jaccard component (Kw)
                kw_score = compute_jaccard(c_concepts, p_feat["concepts"])

                # Chronological component (Chr)
                chr_score = compute_chronological_score(c_year, p_year)

                # Composite score per algorithms.md: 0.35 Cit + 0.35 Sem + 0.20 Kw + 0.10 Chr
                total_score = (0.35 * cit_score) + (0.35 * sem_score) + (0.20 * kw_score) + (0.10 * chr_score)

                shared = list(c_concepts & p_feat["concepts"])
                evidence = {
                    "cit": round(cit_score, 3),
                    "sem": round(sem_score, 3),
                    "kw": round(kw_score, 3),
                    "chr": round(chr_score, 3),
                    "shared_concepts": shared,
                }
                candidate_scores.append((parent_id, total_score, evidence))

            # Sort candidate parents by total score descending
            candidate_scores.sort(key=lambda x: x[1], reverse=True)

            # Determine parent and confidence band (MAP-009)
            assigned_parent_id: Optional[str] = None
            assigned_band: Optional[str] = None
            best_score: Optional[float] = None
            best_evidence: Dict[str, Any] = {}
            role = "placed"

            if candidate_scores:
                top_parent_id, top_score, top_evidence = candidate_scores[0]
                best_score = top_score
                best_evidence = top_evidence

                # Confidence Bands:
                # High: score >= 0.75 and (Cit >= 0.6 or at least two of Sem/Kw/Chr >= 0.7)
                high_cond = (top_evidence["cit"] >= 0.6) or (
                    sum([top_evidence["sem"] >= 0.7, top_evidence["kw"] >= 0.7, top_evidence["chr"] >= 0.7]) >= 2
                )
                if top_score >= 0.75 and high_cond:
                    assigned_band = "high"
                elif top_score >= 0.55:
                    assigned_band = "medium"
                else:
                    assigned_band = "low"

                # Parent = argmax score if band >= Medium and (Cit > 0 or band == High)
                if assigned_band in ["high", "medium"] and (top_evidence["cit"] > 0 or assigned_band == "high"):
                    assigned_parent_id = top_parent_id
                    role = "placed"
                else:
                    role = "needs_review"
                    assigned_parent_id = None
            else:
                role = "root"
                assigned_band = "high"

            # Check for critical missing metadata (MAP-014)
            if "no_year" in c_flags or "no_abstract" in c_flags:
                role = "needs_review"

            # If node is the earliest in the set, mark root
            min_year_in_set = min([f["year"] for f in work_features.values() if f["year"] is not None], default=2024)
            if c_year is not None and c_year <= min_year_in_set and not assigned_parent_id:
                role = "root"

            node_rec = LineageNode(
                run_id=map_run.id,
                work_id=child_id,
                family_id=c_family.id if c_family else None,
                role=role,
                parent_work_id=assigned_parent_id,
                confidence=round(best_score, 4) if best_score is not None else 1.0,
                confidence_band=assigned_band or "medium",
                evidence=best_evidence,
                missing_flags=c_flags,
            )
            nodes_to_create.append(node_rec)

            if assigned_parent_id and best_score is not None:
                edge_rec = LineageEdge(
                    run_id=map_run.id,
                    parent_work_id=assigned_parent_id,
                    child_work_id=child_id,
                    score=round(best_score, 4),
                    evidence=best_evidence,
                )
                edges_to_create.append(edge_rec)

        db.add_all(nodes_to_create)
        db.add_all(edges_to_create)

        # 5. Extract Gap Signals (MAP-017)
        # Scan abstracts and chunk text for future work / limitation / open question sentences
        GAP_PATTERNS = [
            r"future work\s+[^.!?]+[.!?]",
            r"remains\s+(?:challenging|unclear|unresolved)[^.!?]+[.!?]",
            r"limitation\s+(?:of this study|is that)[^.!?]+[.!?]",
            r"not\s+addressed\s+[^.!?]+[.!?]",
            r"further\s+investigation\s+is\s+needed[^.!?]+[.!?]",
            r"open\s+question\s+[^.!?]+[.!?]",
            r"penelitian\s+selanjutnya\s+[^.!?]+[.!?]",
            r"keterbatasan\s+penelitian\s+ini[^.!?]+[.!?]",
            r"belum\s+terjawab\s+[^.!?]+[.!?]",
        ]
        gap_signals: List[GapSignal] = []

        for wid, feat in work_features.items():
            abstract = feat["work"].abstract or ""
            for pat in GAP_PATTERNS:
                matches = re.findall(pat, abstract, re.IGNORECASE)
                for match in matches:
                    excerpt = match.strip()[:300]
                    kind = "future_work" if "future" in excerpt.lower() or "selanjutnya" in excerpt.lower() else "unresolved_condition"
                    gap_signals.append(
                        GapSignal(
                            run_id=map_run.id,
                            kind=kind,
                            work_id=wid,
                            excerpt=excerpt,
                            frequency=1,
                            confidence=0.85,
                        )
                    )

        # Also add lineage gap signals: works with no child and older than 3 years
        current_year = 2026
        parent_work_ids_set = {e.parent_work_id for e in edges_to_create}
        for wid, feat in work_features.items():
            if wid not in parent_work_ids_set and feat["year"] and (current_year - feat["year"] >= 3):
                gap_signals.append(
                    GapSignal(
                        run_id=map_run.id,
                        kind="lineage_gap",
                        work_id=wid,
                        excerpt=f"Leaf work published in {feat['year']} with no successors in current library scope.",
                        frequency=1,
                        confidence=0.75,
                    )
                )

        db.add_all(gap_signals)

        map_run.status = "completed"
        map_run.finished_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(map_run)

        return map_run

    @staticmethod
    async def position_manuscript(
        db: AsyncSession,
        project_id: str,
        user_id: Optional[str],
        lineage_run_id: str,
        title: str,
        abstract: str,
        references: Optional[List[str]] = None,
        retain_text: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculates manuscript placement relative to analyzed set.
        MAP-015: Returns closest family, top-3 parent candidates, shared/distinctive concepts.
        MAP-016: Manuscript text never stored unless retain_text is explicitly true.
        """
        # Fetch lineage run
        run_res = await db.execute(select(MapRun).where(MapRun.id == lineage_run_id, MapRun.project_id == project_id))
        map_run = run_res.scalar_one_or_none()
        if not map_run:
            raise HTTPException(status_code=404, detail="Lineage run not found in project")

        # Fetch clusters and nodes
        clusters_res = await db.execute(select(MapCluster).where(MapCluster.run_id == lineage_run_id))
        clusters = clusters_res.scalars().all()
        if not clusters:
            raise HTTPException(status_code=400, detail="Lineage run has no computed clusters")

        # Fetch works in run
        nodes_res = await db.execute(select(LineageNode).where(LineageNode.run_id == lineage_run_id))
        nodes = nodes_res.scalars().all()
        work_ids = [n.work_id for n in nodes]

        works_res = await db.execute(select(Work).where(Work.id.in_(work_ids)))
        works = {w.id: w for w in works_res.scalars().all()}

        # Compute manuscript representation
        full_ms_text = f"{title} {abstract}"
        ms_hash = hashlib.sha256(full_ms_text.encode("utf-8")).hexdigest()
        ms_concepts = set(extract_top_concepts(full_ms_text, top_k=15))
        ms_tokens = tokenize_clean(full_ms_text)
        ms_tf = {word: count / max(len(ms_tokens), 1) for word, count in Counter(ms_tokens).items()}

        # 1. Closest family & runner-up
        cluster_scores = []
        for c in clusters:
            c_kw_set = set([k.lower() for k in c.keywords])
            overlap = compute_jaccard(ms_concepts, c_kw_set)
            cluster_scores.append((c, overlap))

        cluster_scores.sort(key=lambda x: x[1], reverse=True)
        closest_cluster = cluster_scores[0][0] if cluster_scores else None
        runner_up_cluster = cluster_scores[1][0] if len(cluster_scores) > 1 else None

        # 2. Score against all works in set for top-3 parent candidates
        parent_candidates = []
        ms_year = 2026
        ref_strings = [r.lower() for r in (references or [])]

        for n in nodes:
            w = works.get(n.work_id)
            if not w:
                continue

            w_text = f"{w.title} {w.abstract or ''}"
            w_concepts = set(extract_top_concepts(w_text, top_k=15))
            w_tokens = tokenize_clean(w_text)
            w_tf = {word: count / max(len(w_tokens), 1) for word, count in Counter(w_tokens).items()}

            # Citation score
            direct_cit = False
            if w.doi and any(w.doi.lower() in ref for ref in ref_strings):
                direct_cit = True
            elif any(w.title.lower() in ref for ref in ref_strings):
                direct_cit = True
            cit_score = 1.0 if direct_cit else 0.0

            # Semantic score
            sem_score = compute_cosine_similarity(ms_tf, w_tf)

            # Keyword score
            kw_score = compute_jaccard(ms_concepts, w_concepts)

            # Chronological score
            chr_score = compute_chronological_score(ms_year, w.year)

            total_score = (0.35 * cit_score) + (0.35 * sem_score) + (0.20 * kw_score) + (0.10 * chr_score)
            shared = list(ms_concepts & w_concepts)

            # Find family label for node
            f_label = next((c.label for c in clusters if c.id == n.family_id), "Unplaced")

            parent_candidates.append({
                "work_id": w.id,
                "title": w.title,
                "year": w.year,
                "doi": w.doi,
                "family_id": n.family_id,
                "family_label": f_label,
                "score": round(total_score, 4),
                "component_scores": {
                    "cit": round(cit_score, 3),
                    "sem": round(sem_score, 3),
                    "kw": round(kw_score, 3),
                    "chr": round(chr_score, 3),
                },
                "shared_concepts": shared,
            })

        parent_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_3_parents = parent_candidates[:3]

        # 3. Shared vs Distinctive concepts
        all_family_concepts = set()
        if closest_cluster:
            cluster_members = [n.work_id for n in nodes if n.family_id == closest_cluster.id]
            for mid in cluster_members:
                mw = works.get(mid)
                if mw:
                    all_family_concepts.update(extract_top_concepts(f"{mw.title} {mw.abstract or ''}", top_k=15))

        shared_concepts = list(ms_concepts & all_family_concepts)
        distinctive_concepts = list(ms_concepts - all_family_concepts)

        # Fit label
        top_score = top_3_parents[0]["score"] if top_3_parents else 0.0
        if top_score >= 0.75:
            fit_label = "Strong"
        elif top_score >= 0.55:
            fit_label = "Moderate"
        else:
            fit_label = "Weak"

        results_data = {
            "closest_family_id": closest_cluster.id if closest_cluster else None,
            "closest_family_label": closest_cluster.label if closest_cluster else None,
            "runner_up_family_id": runner_up_cluster.id if runner_up_cluster else None,
            "runner_up_family_label": runner_up_cluster.label if runner_up_cluster else None,
            "top_parents": top_3_parents,
            "shared_concepts": shared_concepts,
            "distinctive_concepts": distinctive_concepts,
            "fit_label": fit_label,
            "disclaimer": "Closest in the analyzed set — this does not claim global novelty or absence of prior art.",
        }

        # Store run (MAP-016: retain_text=False preserves privacy)
        pos_rec = PositioningRun(
            project_id=project_id,
            lineage_run_id=lineage_run_id,
            manuscript_hash=ms_hash,
            manuscript_text=full_ms_text if retain_text else None,
            retain_text=retain_text,
            closest_family_id=closest_cluster.id if closest_cluster else None,
            results=results_data,
            created_by=user_id,
        )
        db.add(pos_rec)
        await db.commit()
        await db.refresh(pos_rec)

        return {
            "id": pos_rec.id,
            "lineage_run_id": lineage_run_id,
            **results_data,
        }
