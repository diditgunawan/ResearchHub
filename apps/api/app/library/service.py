import csv
import io
import json
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.library.models import LibraryItem, ImportBatch, DedupCandidate
from app.works.models import Work, Author, WorkAuthor
from app.library.parsers.ris_parser import parse_ris_text
from app.library.parsers.bibtex_parser import parse_bibtex_text
from app.library.parsers.csv_parser import parse_csv_text
from app.core.errors import NotFoundError, BadRequestError, ConflictError


class LibraryService:
    @staticmethod
    async def add_to_library(
        db: AsyncSession,
        project_id: str,
        work_id: str,
        user_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> LibraryItem:
        """LIB-005: Idempotently add a work to a project library."""
        # Verify work exists
        work = (await db.execute(select(Work).where(Work.id == work_id))).scalar_one_or_none()
        if not work:
            raise NotFoundError(f"Work '{work_id}' not found", code="WORK_NOT_FOUND")

        # Check existing
        stmt = select(LibraryItem).where(
            LibraryItem.project_id == project_id,
            LibraryItem.work_id == work_id,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            return existing

        item = LibraryItem(
            project_id=project_id,
            work_id=work_id,
            added_by=user_id,
            user_notes=notes,
        )
        db.add(item)
        await db.flush()

        # ADR-011: Embed-on-add discipline - compute or index chunks only when entering project scope
        from app.synthesis.service import SynthesisService
        await SynthesisService.get_or_create_chunks(db, work)

        return item

    @staticmethod
    async def list_items(
        db: AsyncSession,
        project_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """LIB-015: Server-side paginated library listing."""
        count_stmt = select(func.count(LibraryItem.id)).where(LibraryItem.project_id == project_id)
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(LibraryItem, Work)
            .join(Work, LibraryItem.work_id == Work.id)
            .where(LibraryItem.project_id == project_id)
            .order_by(LibraryItem.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()

        results = []
        for lib_item, work in rows:
            results.append({
                "id": lib_item.id,
                "project_id": lib_item.project_id,
                "work_id": work.id,
                "doi": work.doi,
                "title": work.title,
                "abstract": work.abstract,
                "year": work.year,
                "venue": work.venue,
                "user_notes": lib_item.user_notes,
                "added_at": lib_item.created_at,
            })

        return results, total

    @staticmethod
    async def import_text(
        db: AsyncSession,
        project_id: str,
        user_id: str,
        format_type: str,
        content: str,
    ) -> ImportBatch:
        """LIB-001 & LIB-004: Execute format-specific parsing and import with full parse report."""
        fmt = format_type.lower()
        if fmt == "ris":
            parsed = parse_ris_text(content)
        elif fmt == "bibtex":
            parsed = parse_bibtex_text(content)
        elif fmt == "csv":
            parsed = parse_csv_text(content)
        else:
            raise BadRequestError(f"Unsupported import format '{format_type}'. Expected ris, bibtex, or csv.")

        records = parsed.get("records", [])
        imported_count = 0

        for r in records:
            # Check or create work by DOI / title
            work = None
            if r.get("doi"):
                work = (await db.execute(select(Work).where(Work.doi == r["doi"]))).scalar_one_or_none()
            if not work and r.get("title"):
                work = (await db.execute(select(Work).where(Work.title == r["title"]))).scalar_one_or_none()

            if not work:
                work = Work(
                    doi=r.get("doi"),
                    title=r["title"],
                    abstract=r.get("abstract"),
                    year=r.get("year"),
                    venue=r.get("venue"),
                    work_type=r.get("work_type", "article"),
                )
                db.add(work)
                await db.flush()

                # Add authors
                for idx, auth_name in enumerate(r.get("authors", [])):
                    auth = (await db.execute(select(Author).where(Author.name == auth_name))).scalar_one_or_none()
                    if not auth:
                        auth = Author(name=auth_name)
                        db.add(auth)
                        await db.flush()
                    wa = WorkAuthor(work_id=work.id, author_id=auth.id, position=idx + 1)
                    db.add(wa)
                await db.flush()

            # Add to project library
            await LibraryService.add_to_library(db, project_id, work.id, user_id)
            imported_count += 1

        batch = ImportBatch(
            project_id=project_id,
            source=fmt,
            total_count=len(records) + parsed.get("skipped", 0),
            imported_count=imported_count,
            skipped_count=parsed.get("skipped", 0),
            status="completed",
            report_json={
                "imported": imported_count,
                "skipped": parsed.get("skipped", 0),
                "errors": parsed.get("errors", []),
            },
        )
        db.add(batch)
        await db.flush()
        return batch

    @staticmethod
    async def export_library(
        db: AsyncSession,
        project_id: str,
        format_type: str,
    ) -> str:
        """LIB-009: Export library in BibTeX, RIS, or CSV format."""
        stmt = (
            select(Work)
            .join(LibraryItem, Work.id == LibraryItem.work_id)
            .where(LibraryItem.project_id == project_id)
            .order_by(Work.year.desc().nullslast(), Work.title.asc())
        )
        works = (await db.execute(stmt)).scalars().all()

        fmt = format_type.lower()
        if fmt == "bibtex":
            output = []
            for w in works:
                cite_key = f"ref_{w.id[:8]}"
                entry = [
                    f"@article{{{cite_key},",
                    f'  title = "{{{w.title}}}",',
                ]
                if w.year:
                    entry.append(f"  year = {{{w.year}}},")
                if w.venue:
                    entry.append(f'  journal = "{{{w.venue}}}",')
                if w.doi:
                    entry.append(f"  doi = {{{w.doi}}},")
                if w.abstract:
                    entry.append(f'  abstract = "{{{w.abstract}}}",')
                entry.append("}\n")
                output.append("\n".join(entry))
            return "\n".join(output)

        elif fmt == "ris":
            output = []
            for w in works:
                entry = [
                    "TY  - JOUR",
                    f"TI  - {w.title}",
                ]
                if w.year:
                    entry.append(f"PY  - {w.year}")
                if w.venue:
                    entry.append(f"JO  - {w.venue}")
                if w.doi:
                    entry.append(f"DO  - {w.doi}")
                if w.abstract:
                    entry.append(f"AB  - {w.abstract}")
                entry.append("ER  -\n")
                output.append("\n".join(entry))
            return "\n".join(output)

        elif fmt == "csv":
            out = io.StringIO()
            writer = csv.writer(out)
            writer.writerow(["Title", "Year", "Venue", "DOI", "Abstract"])
            for w in works:
                writer.writerow([w.title, w.year or "", w.venue or "", w.doi or "", w.abstract or ""])
            return out.getvalue()

        else:
            raise BadRequestError(f"Unsupported export format '{format_type}'. Expected bibtex, ris, or csv.")
