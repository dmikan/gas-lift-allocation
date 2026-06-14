def merge_pdf_appendices(
    base_pdf_bytes: bytes,
    has_constrained: bool,
    has_global: bool,
    constrained_results,
    well_results,
    global_results,
) -> bytes:
    """Pass-through: charts are already embedded inline; no appendix pages needed."""
    return base_pdf_bytes
