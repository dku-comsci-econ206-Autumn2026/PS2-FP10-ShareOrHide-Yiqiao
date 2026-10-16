#!/usr/bin/env python3
"""Validate the FP10 final release using structural, content, and provenance gates."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PDFINFO = Path("/Users/mickeyxiaoliuliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdfinfo")
PDFTOTEXT = Path("/Users/mickeyxiaoliuliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftotext")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pdf_info(path: Path) -> dict[str, str]:
    result = subprocess.run([PDFINFO, path], text=True, capture_output=True, check=True)
    return dict(
        line.split(":", 1) for line in result.stdout.splitlines() if ":" in line
    )


def pdf_text(path: Path, first: int, last: int) -> str:
    result = subprocess.run(
        [PDFTOTEXT, "-f", str(first), "-l", str(last), path, "-"],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


checks: list[dict[str, object]] = []


def check(name: str, passed: bool, evidence: str, manual: bool = False) -> None:
    checks.append(
        {
            "name": name,
            "status": "MANUAL VERIFICATION REQUIRED" if manual else ("PASS" if passed else "FAIL"),
            "evidence": evidence,
        }
    )


def main() -> int:
    canvas_files = [
        ROOT / "submission/final/Final-FP10-ShareOrHide.pdf",
        ROOT / "submission/final/Final-FP10-ShareOrHide-Overleaf-Source.zip",
        ROOT / "submission/final/Final-FP10-ShareOrHide-A0-Poster.pptx",
        ROOT / "submission/final/Final-FP10-ShareOrHide-A0-Poster.pdf",
    ]
    required = [
        *canvas_files,
        ROOT / "poster/final-poster.png",
    ]
    check("required artifacts", all(path.is_file() for path in required), "; ".join(str(p.relative_to(ROOT)) for p in required))

    paper = required[0]
    pinfo = pdf_info(paper)
    check("paper PDF opens", int(pinfo["Pages"].strip()) >= 6, f"{pinfo['Pages'].strip()} pages; {pinfo['Page size'].strip()}")
    first_two = pdf_text(paper, 1, 2)
    third = pdf_text(paper, 3, 3)
    required_parts = ["Background", "Motivation", "Application Scenario", "Research Question", "Method", "Results", "Intellectual Merits", "Practical Impacts", "Future Research Roadmap"]
    main_ok = all(part in first_two for part in required_parts) and "Author Notes" not in first_two and "Author Notes" in third
    check("two-page main paper", main_ok, "All eight named parts plus roadmap on pages 1–2; Author Notes begins page 3")

    source_zip = required[1]
    with zipfile.ZipFile(source_zip) as archive:
        names = set(archive.namelist())
        packed_paper_figures = {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in (
                "figures/ps2_teaser.tex",
                "figures/intellectual_merits_paper.tex",
                "figures/practical_impacts_paper.tex",
                "figures/research_roadmap_paper.tex",
            )
        }
    source_required = {
        "main.tex", "references.bib", "acmart.cls", "ACM-Reference-Format.bst",
        "sections/proposal.tex", "appendices/supporting.tex",
        "figures/welfare_comparison_paper.pdf", "figures/E_WEB_09.png", "figures/E_WEB_11.png", "figures/ps2_teaser.tex",
        "figures/intellectual_merits_paper.tex", "figures/practical_impacts_paper.tex",
        "figures/research_roadmap_paper.tex",
    }
    check("Overleaf source contents", source_required <= names, f"{len(names)} files; required sources present")
    canonical_paper_figures = {
        f"figures/{name}": sha256(ROOT / "paper/final/figures" / name)
        for name in (
            "ps2_teaser.tex", "intellectual_merits_paper.tex",
            "practical_impacts_paper.tex", "research_roadmap_paper.tex",
        )
    }
    check(
        "Overleaf paper-specific figure sources",
        canonical_paper_figures == packed_paper_figures,
        f"canonical={canonical_paper_figures}; packed={packed_paper_figures}",
    )

    poster_pptx = required[2]
    with zipfile.ZipFile(poster_pptx) as archive:
        presentation_xml = archive.read("ppt/presentation.xml").decode("utf-8")
        slide_names = [name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
        poster_xml = "".join(archive.read(name).decode("utf-8") for name in slide_names)
        media_hashes = {
            hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if name.startswith("ppt/media/")
        }
    size = re.search(r"<p:sldSz cx=\"(\d+)\" cy=\"(\d+)\"", presentation_xml)
    geometry_ok = bool(size and size.groups() == ("42804000", "30276000") and len(slide_names) == 1)
    check("poster geometry", geometry_ok, f"slides={len(slide_names)}, EMU={size.groups() if size else None}, nominal 1189×841 mm")
    check("poster acknowledgment and contribution", all(term in poster_xml for term in ("Full acknowledgments", "Yiqiao Liu", "Han Zhang", "Xinrong Sun", "Feiyu Li")), "Required named text found in editable slide XML")
    merits_png_hash = sha256(ROOT / "figures/final/intellectual_merits.png")
    check(
        "poster Intellectual Merits image",
        merits_png_hash in media_hashes,
        f"canonical PNG {merits_png_hash} embedded in editable PPTX",
    )

    geometry_report = json.loads(
        (ROOT / "outputs/final/intellectual_merits_geometry.json").read_text(encoding="utf-8")
    )
    check(
        "Intellectual Merits geometry",
        geometry_report["status"] == "PASS" and not geometry_report["failures"],
        f"cards={geometry_report['cardCount']}, connectors={geometry_report['connectorCount']}, failures={geometry_report['failures']}",
    )
    check(
        "Intellectual Merits connector whitespace",
        geometry_report["status"] == "PASS"
        and all(item["actual"] >= item["minimum"] for item in geometry_report["spacingMetrics"]),
        "; ".join(f"{item['id']}={item['actual']}px (min {item['minimum']}px)" for item in geometry_report["spacingMetrics"]),
    )

    arrow_report = json.loads(
        (ROOT / "outputs/final/section02_arrow_clarity.json").read_text(encoding="utf-8")
    )
    check(
        "Section 02 arrow-clarity containment",
        arrow_report["status"] == "PASS"
        and arrow_report["changedInsidePixels"] > 0
        and arrow_report["changedOutsidePixels"] == 0
        and arrow_report["maximumOutsideChannelDelta"] == 0
        and all(item["identical"] for item in arrow_report["protectedEvidence"].values()),
        f"changed inside={arrow_report['changedInsidePixels']} px; outside={arrow_report['changedOutsidePixels']} px; protected regions={arrow_report['protectedEvidence']}",
    )

    diff_report = json.loads(
        (ROOT / "outputs/final/poster_layout_rebalance.json").read_text(encoding="utf-8")
    )
    check(
        "poster global rebalance containment",
        diff_report["status"] == "PASS"
        and diff_report["changedOutsidePixels"] == 0
        and diff_report["maximumOutsideChannelDelta"] == 0
        and all(item["identical"] for item in diff_report["protectedEvidence"].values()),
        f"changed outside body={diff_report['changedOutsidePixels']} px; protected regions={diff_report['protectedEvidence']}",
    )
    check(
        "poster evidence-area rebalance",
        diff_report["layoutMetrics"]["afterColumnWidths"] == [1080, 1900, 1074]
        and diff_report["layoutMetrics"]["section02FigureAreaIncreaseRatio"] >= 0.29,
        f"columns={diff_report['layoutMetrics']['afterColumnWidths']}; Section 02 figure area increase={diff_report['layoutMetrics']['section02FigureAreaIncreaseRatio']:.1%}",
    )

    poster_pdf_info = pdf_info(required[3])
    check("poster PDF", poster_pdf_info["Pages"].strip() == "1", f"pages={poster_pdf_info['Pages'].strip()}, size={poster_pdf_info['Page size'].strip()}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check("README poster embed", "![Final presentation poster](poster/final-poster.png)" in readme, "Exact required embed present")
    check("README poster PDF link", "[Download the final poster PDF](poster/final-poster.pdf)" in readme, "Exact required link present")
    fallback = ROOT / "docs/assets/demo/behavioral-decision-lab-fallback.png"
    check("demo outage fallback", fallback.is_file() and "behavioral-decision-lab-fallback.png" in readme, f"{fallback.relative_to(ROOT)}; sha256={sha256(fallback) if fallback.is_file() else 'missing'}")

    for notebook in (ROOT / "notebooks/01_strategic_disclosure_game.ipynb", ROOT / "notebooks/02_priority_slot_allocation.ipynb"):
        try:
            json.loads(notebook.read_text(encoding="utf-8"))
            ok = True
        except (OSError, json.JSONDecodeError):
            ok = False
        check(f"valid notebook {notebook.name}", ok, str(notebook.relative_to(ROOT)))

    manifest = json.loads((ROOT / "outputs/final/release_manifest.json").read_text())
    check("model metadata", manifest["parameters"]["actions"] == ["M", "P", "F"] and manifest["robustness_counts"]["No effect on equilibrium set"] == 401, "Manifest action space and diagnostic counts verified")
    tested_commit = manifest["tested_commit"]
    check("tested commit recorded", bool(re.fullmatch(r"[0-9a-f]{40}", tested_commit)), tested_commit)
    poster_source_commit = manifest.get("poster_source_commit", "")
    check("frozen poster provenance", bool(re.fullmatch(r"[0-9a-f]{40}", poster_source_commit)) and poster_source_commit in poster_xml, "Unmodified poster retains its own validated source commit")
    check("release commit roles", manifest.get("validated_source_commit") == tested_commit and bool(re.fullmatch(r"[0-9a-f]{40}", manifest.get("source_commit_at_generation", ""))), "Validated source and artifact-generation source are recorded separately")

    canvas_text = (ROOT / "submission/final/canvas_text_entry.txt").read_text(encoding="utf-8")
    check("Canvas text uses main links", "/blob/main/" in canvas_text and "final/fp10-2026-release" not in canvas_text, "README, poster, and notebook URLs target main")
    check("Canvas text version", tested_commit in canvas_text and "Final release candidate" not in canvas_text, "Canvas text names the validated source commit and the current final correction")
    check("Canvas commit roles", all(label in canvas_text for label in ("Validated source commit:", "Artifact packaging commit:", "Published merge commit:")), "Canvas text distinguishes source, package, and published merge provenance")
    packaging_commit = manifest.get("artifact_packaging_commit", "")
    check("artifact packaging commit", bool(re.fullmatch(r"[0-9a-f]{40}", packaging_commit)) and packaging_commit in canvas_text, "Exact packaging commit is recorded in the manifest and Canvas entry")
    check("published merge status", manifest.get("published_merge_commit") is None and "Not yet merged" in canvas_text, "No merge commit is claimed before publication")

    manifest_artifacts = manifest.get("canvas_artifacts", {})
    artifacts_match = all(
        manifest_artifacts.get(path.name, {}).get("sha256") == sha256(path)
        and manifest_artifacts.get(path.name, {}).get("size_bytes") == path.stat().st_size
        for path in canvas_files
    )
    check("manifest Canvas hashes and sizes", artifacts_match, "All four Canvas artifacts match the manifest SHA-256 and byte size")
    verification_summary = manifest.get("verification_summary", {})
    test_totals = verification_summary.get("automated_tests", {})
    release_totals = verification_summary.get("final_release_validator", {})
    check("manifest verification counts", test_totals.get("total") == 70 and test_totals.get("failures") == 0 and release_totals.get("passed") == 39 and release_totals.get("failed") == 0 and release_totals.get("manual_confirmation_required") == 4, "Manifest records 70 passing tests and 39 validator passes, plus four human-only checks")

    source = (ROOT / "paper/final/appendices/supporting.tex").read_text(encoding="utf-8")
    appendices_ok = all(f"\\section{{{name}" in source for name in (
        "Technical Details and Reproducibility",
        "Cumulative Intellectual Development",
        "Open Source and Three Lens Inspiration",
        "Feedback Response and Revision Record",
        "Structured Abstract and Cumulative Proposal Map",
        "Retained PS2 Auction Artifact and Symposium Record",
        "Final Week Evidence and Final Release Audit",
    ))
    check("Appendices A–G", appendices_ok, "Seven required appendix section titles found")
    check("AI disclosure", "AI Use Disclosure" in source, "Appendix A.1 present")
    check("full acknowledgments", "Full Acknowledgments" in source and "Professor Luyao Zhang" in source, "Paper acknowledgment section present")
    check("official SDG icons in paper source", "figures/E_WEB_09.png" in names and "figures/E_WEB_11.png" in names, "Official Goal 9 and Goal 11 assets packaged")
    roadmap_source = (ROOT / "paper/final/figures/research_roadmap_paper.tex").read_text(encoding="utf-8")
    roadmap_fields = ("Question:", "Method/data:", "Potential collaborator:", "Progress criterion:", "Milestone:")
    roadmap_ok = all(roadmap_source.count(term) == 3 for term in roadmap_fields)
    check("roadmap five fields", roadmap_ok, "Each of the three Appendix G roadmap studies labels all five required fields")
    impact_source = (ROOT / "paper/final/figures/practical_impacts_paper.tex").read_text(encoding="utf-8")
    check("SDG target claims", "SDG target 9.1" in impact_source and "SDG target 11.2" in impact_source and "indirect, prospective" in impact_source, "Paper diagram labels targets 9.1 and 11.2 and qualifies 11.2 as indirect/prospective")
    check("Figure 1 evidence alignment", "baseline pure-BNE and full-information first-best welfare" in (ROOT / "paper/final/main.tex").read_text(encoding="utf-8"), "Caption describes two plotted welfare series and separates CCAR")
    check("license wording", "no additional project reuse license is asserted" in source, "No nonexistent root project license is claimed")
    check("AI model wording", "exact underlying model identifier not independently verified" in source, "Unverified model-family claim removed")

    check("visual and scientific quality", False, "Automated structure checks cannot establish scientific quality or visual legibility", manual=True)
    check("PowerPoint native rendering", False, "Open PPTX in Microsoft PowerPoint; test QR codes, links, fonts, and print preview", manual=True)
    check("author and Canvas confirmation", False, "Yiqiao Liu must review and upload the four required files", manual=True)
    check("hosted Colab and live Hugging Face interactions", False, "Local execution/source parity does not establish hosted notebook execution or human click-through", manual=True)

    report = {
        "schema_version": 1,
        "verification_date": date.today().isoformat(),
        "checks": checks,
        "canvas_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in canvas_files},
        "canvas_file_sizes": {str(path.relative_to(ROOT)): path.stat().st_size for path in canvas_files},
        "auxiliary_hashes": {str(required[-1].relative_to(ROOT)): sha256(required[-1])},
        "automated_passed": sum(c["status"] == "PASS" for c in checks),
        "automated_failed": sum(c["status"] == "FAIL" for c in checks),
        "manual_required": sum(c["status"] == "MANUAL VERIFICATION REQUIRED" for c in checks),
    }
    output = ROOT / "outputs/final/final_release_check.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if report["automated_failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
