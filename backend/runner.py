"""One job per child process. No uploaded content is imported or executed."""

import hashlib
import json
import logging
import os
import sys
import time
import zipfile

from backend.config import settings
from backend.database import Job, SessionLocal
from backend.security import seal, unseal
from backend.storage import job_directory
from fileshield.archives import analyze_archive
from fileshield.detection import detect_file
from fileshield.hashing import compute_hashes
from fileshield.images import FORMATS, image_metadata, transform_image
from fileshield.pdf import analyze_pdf, rewrite_pdf
from fileshield.protection import protect_file
from fileshield.scanning import scan_file


logger = logging.getLogger("fileshield.worker")


def analyze(path: str, filename: str, declared: str) -> dict:
    detection = detect_file(path, filename, declared)
    report = {"file": detection, "hashes": compute_hashes(path)}
    mime = detection["detected_mime"]
    if mime.startswith("image/"):
        report["metadata"] = image_metadata(path)
    elif mime == "application/pdf":
        report["pdf"] = analyze_pdf(path)
    elif mime in {"application/zip", "application/gzip", "application/x-tar"}:
        report["archive"] = analyze_archive(path)
    report["public_release"] = {
        "file_type": "verified" if detection["parser_validated"] else "signature_only",
        "warnings": detection["warnings"],
        "recommendation": "Review findings and sanitize before release; this is not a safety certification",
    }
    return report


def execute_job(identifier: str):
    settings.validate()
    with SessionLocal() as database:
        job = database.get(Job, identifier)
        if not job or job.status != "processing" or job.expires <= time.time():
            return
        names, declared = json.loads(job.filenames), json.loads(job.declared_mimes)
        options, operation = unseal(job.options), job.operation
    directory = job_directory(identifier)
    inputs = [directory / f"input-{index}.bin" for index in range(len(names))]
    output_name, report = None, {}
    try:
        scans = []
        for path in inputs:
            scan = scan_file(str(path), settings.clamav_host) if settings.require_scan else {
                "status": "not_scanned", "message": "Development-only: antivirus disabled"}
            scans.append(scan)
            if scan["status"] not in {"clean", "not_scanned"}:
                raise ValueError("Malware scan blocked processing")
        if operation in {"analyze", "release", "metadata", "archives", "hash", "compare", "scan"}:
            if operation in {"hash", "compare"}:
                report = {"files": [compute_hashes(str(path)) for path in inputs]}
                if operation == "compare":
                    report["identical"] = report["files"][0]["sha256"] == report["files"][1]["sha256"]
                if options.get("expected_sha256"):
                    report["integrity_verified"] = report["files"][0]["sha256"] == options["expected_sha256"].lower()
            elif operation == "scan":
                report = {}
            else:
                report = {"files": [analyze(str(path), names[index], declared[index]) for index, path in enumerate(inputs)]}
        elif operation in {"sanitize", "images", "batch"}:
            results, generated = [], []
            for index, path in enumerate(inputs):
                detection = detect_file(str(path), names[index], declared[index])
                if detection["warnings"]:
                    raise ValueError("Resolve file-type mismatch before processing")
                if operation == "sanitize" and detection["detected_mime"] == "application/pdf":
                    output_name = "output.pdf"
                    results.append(rewrite_pdf([str(path)], str(directory / output_name)))
                else:
                    extension = FORMATS[options["output_format"]][1]
                    output_name = f"output-{index}{extension}"
                    image_options = {key: options[key] for key in ("output_format", "width", "height", "quality", "rotation", "crop", "dpi")}
                    results.append(transform_image(str(path), str(directory / output_name), **image_options))
                generated.append(output_name)
            report = {"files": results}
            if operation == "batch":
                output_name = "output.zip"
                with zipfile.ZipFile(directory / output_name, "x", zipfile.ZIP_STORED) as archive:
                    for name in generated:
                        archive.write(directory / name, arcname=name)
                for name in generated:
                    (directory / name).unlink()
        elif operation == "pdf":
            output_name = "output.pdf"
            report = rewrite_pdf([str(path) for path in inputs], str(directory / output_name),
                                 pages=options["pages"], rotation=options["rotation"], password=options["password"])
        elif operation in {"protect", "decrypt"}:
            output_name = "output.bin" if operation == "decrypt" else "output.fshield"
            if not options["password"]:
                raise ValueError("A password is required")
            report = protect_file(str(inputs[0]), str(directory / output_name), options["password"], operation == "decrypt")
        else:
            raise ValueError("Unsupported operation")
        report["scans"] = scans
        if output_name:
            output = directory / output_name
            if output.stat().st_size > 25 * 1024 * 1024:
                raise ValueError("Output exceeds size limit")
            if settings.require_scan:
                scan = scan_file(str(output), settings.clamav_host)
                report["output_scan"] = scan
                if scan["status"] != "clean":
                    raise ValueError("Output malware scan failed")
            report["output_hashes"] = compute_hashes(str(output))
        encoded = json.dumps(report, default=str)
        if len(encoded.encode()) > 256 * 1024:
            raise ValueError("Report exceeds bounded storage limit")
        with SessionLocal() as database:
            job = database.get(Job, identifier)
            job.status, job.report, job.output_name = "completed", encoded, output_name
            job.options = seal({})
            database.commit()
        logger.info(json.dumps({"event": "job_completed", "job_id": identifier, "operation": operation}))
    except Exception:
        for path in directory.glob("output*"):
            path.unlink(missing_ok=True)
        with SessionLocal() as database:
            job = database.get(Job, identifier)
            job.status, job.error, job.options = "failed", "Processing rejected or failed; no output released", seal({})
            database.commit()
        logger.warning(json.dumps({"event": "processing_rejected", "job_id": identifier}))
    finally:
        for path in inputs:
            path.unlink(missing_ok=True)


def resource_limits():
    if os.name == "posix":
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (settings.process_timeout, settings.process_timeout + 1))
        resource.setrlimit(resource.RLIMIT_AS, (768 * 1024 * 1024, 768 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024, 100 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    resource_limits()
    execute_job(sys.argv[1])