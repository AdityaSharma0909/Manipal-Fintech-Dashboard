from __future__ import annotations

from onboarding_v2.constants import ApplicationStage
from onboarding_v2.models import ApplicationStageSnapshot, JewelleryItem


def merge_payload(existing: dict, incoming: dict) -> dict:
    if not isinstance(existing, dict):
        return incoming

    def _merge_dict(base: dict, update: dict) -> dict:
        result = dict(base)
        for key, value in update.items():
            if value is None or value == "":
                continue
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = _merge_dict(result.get(key, {}), value)
            else:
                result[key] = value
        return result

    return _merge_dict(existing, incoming)


def merge_gold_payload(existing: dict, incoming: dict) -> dict:
    if not isinstance(existing, dict):
        return incoming
    merged = dict(existing)
    # Merge top-level packet fields
    for key, value in incoming.items():
        if key == "items":
            continue
        if value is not None and value != "":
            merged[key] = value

    existing_items = list(existing.get("items") or [])
    incoming_items = list(incoming.get("items") or [])
    if not existing_items:
        merged["items"] = incoming_items
        return merged
    # If incoming does not specify indices, treat as full replacement
    has_index = False
    for it in incoming_items:
        if isinstance(it, dict) and (it.get("item_index") or it.get("index")):
            has_index = True
            break
    if not has_index:
        merged["items"] = incoming_items
        return merged

    # Build positions for existing items by type
    type_positions: dict[str, list[int]] = {}
    for idx, item in enumerate(existing_items):
        if not isinstance(item, dict):
            continue
        t = item.get("type_of_jewellery")
        if not t:
            continue
        type_positions.setdefault(t, []).append(idx)

    def _merge_item(base: dict, update: dict) -> dict:
        result = dict(base) if isinstance(base, dict) else {}
        for k, v in update.items():
            if k == "metadata" and isinstance(v, dict):
                prev = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
                result["metadata"] = {**prev, **v}
                continue
            if v is not None and v != "":
                result[k] = v
        return result

    for item in incoming_items:
        if not isinstance(item, dict):
            continue
        t = item.get("type_of_jewellery")
        idx_value = item.get("item_index") or item.get("index")
        target_pos = None
        if t and idx_value:
            positions = type_positions.get(t, [])
            try:
                idx_num = int(idx_value)
            except Exception:
                idx_num = None
            if idx_num and idx_num > 0 and idx_num <= len(positions):
                target_pos = positions[idx_num - 1]

        if target_pos is None:
            # No explicit index; if type exists, update first occurrence, else append
            if t and type_positions.get(t):
                existing_items[type_positions[t][0]] = _merge_item(existing_items[type_positions[t][0]], item)
            else:
                existing_items.append(item)
                if t:
                    type_positions.setdefault(t, []).append(len(existing_items) - 1)
        else:
            existing_items[target_pos] = _merge_item(existing_items[target_pos], item)

    merged["items"] = existing_items
    return merged


def resolve_jewellery_item_index(application, jewellery_type: str) -> int:
    count = 0
    try:
        gold_snapshot = application.stage_snapshots.get(stage=ApplicationStage.GOLD)
        gold_payload = gold_snapshot.payload if isinstance(gold_snapshot.payload, dict) else {}
        for item in gold_payload.get("items") or []:
            if isinstance(item, dict) and item.get("type_of_jewellery") == jewellery_type:
                count += 1
    except ApplicationStageSnapshot.DoesNotExist:
        pass

    if count == 0:
        count = JewelleryItem.objects.filter(
            packet__application=application, type_of_jewellery=jewellery_type
        ).count()

    return count + 1
