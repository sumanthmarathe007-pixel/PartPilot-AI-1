from __future__ import annotations


def maximum_unique_assignment(candidate_map: dict[str, list[str]]) -> dict[str, str]:
    """Maximum-cardinality matching for small batches (six requests, twelve parts).

    candidate_map maps request_id -> ordered list of already-safe part_ids.
    The list order expresses preference (e.g. recent-stock/low-verification first).
    Every part can be assigned to at most one request.
    """
    # Requests with fewer candidates are processed first to protect constrained tickets.
    request_order = sorted(candidate_map, key=lambda rid: (len(candidate_map[rid]), rid))
    part_to_request: dict[str, str] = {}

    def augment(request_id: str, seen_parts: set[str]) -> bool:
        for part_id in candidate_map.get(request_id, []):
            if part_id in seen_parts:
                continue
            seen_parts.add(part_id)
            previous_request = part_to_request.get(part_id)
            if previous_request is None or augment(previous_request, seen_parts):
                part_to_request[part_id] = request_id
                return True
        return False

    for request_id in request_order:
        augment(request_id, set())

    return {request_id: part_id for part_id, request_id in part_to_request.items()}
