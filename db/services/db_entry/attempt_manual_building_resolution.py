# db.services.db_entry.attempt_manual_building_resolution.py
from ai import transliterate_pipeline

from db.services.posts.processing import mark_review_building
from db.services.db_entry._search_buildings_fuzzy import _search_buildings_fuzzy
from db.services.db_entry.resolve_building_candidates import resolve_building_candidates
from db.services.db_entry.build_building_candidates import build_building_candidates
from db.services.db_entry.finalize_entry import finalize_entry

from db.db_supabase import get_session
from db.services.shared.building_alias import add_building_alias


async def attempt_manual_building_resolution(row, post_json, transliterate_ai):
    """
    Building recovery pipeline:

    1. Try original + standardized exact matches
    2. Generate AI transliteration candidate
    3. Try all candidates exact match
    4. Fuzzy search
    5. User confirmation
    6. Alias handling
    7. Enter DB
    """

    candidates = build_building_candidates(post_json)

    # --------------------------------------------------------
    # Stage 1: deterministic lookup
    # --------------------------------------------------------
    async with get_session() as db:
        result = await resolve_building_candidates(
            db,
            [c["name"] for c in candidates],
        )

    if result:
        building_id, matched_name = result

        print(f"[EXACT MATCH] row={row['id']} name='{matched_name}'")

        return await finalize_entry(row, post_json, building_id=building_id)

    # --------------------------------------------------------
    # Stage 2: AI transliteration
    # --------------------------------------------------------
    validated, error = transliterate_pipeline.run_processing(
        transliterate_ai,
        row["text"],
    )

    print(
        "[TRANSLITERATE RESULT]"
        f"\nbest_guess: \n{getattr(validated, 'best_guess_name', None) if validated else None}"
    )

    if not error and validated and validated.best_guess_name:
        ai_name = validated.best_guess_name.strip()

        if ai_name and ai_name not in [c["name"] for c in candidates]:
            candidates.append(
                {
                    "source": "transliteration",
                    "name": ai_name,
                }
            )

    if not candidates:
        print(f"[NO_USABLE_NAME] row={row['id']}")

        mark_review_building(row["id"])
        return False

    # --------------------------------------------------------
    # Stage 3: deterministic lookup again
    # --------------------------------------------------------
    async with get_session() as db:
        result = await resolve_building_candidates(
            db,
            [c["name"] for c in candidates],
        )

    if result:
        building_id, matched_name = result

        print(f"[EXACT MATCH] row={row['id']} name='{matched_name}'")

        return await finalize_entry(row, post_json, building_id=building_id)

    # --------------------------------------------------------
    # Stage 4: select fuzzy search name
    # --------------------------------------------------------
    if len(candidates) == 1:
        search_name = candidates[0]["name"]

    else:
        print("\n[BUILDING NAME OPTIONS]")

        for i, c in enumerate(candidates, start=1):
            print(f"  {i}. {c['source']}: {c['name']}")

        choice = input(f"Select search name (1-{len(candidates)}): ").strip()

        if choice not in [str(i) for i in range(1, len(candidates) + 1)]:
            mark_review_building(row["id"])
            return False

        search_name = candidates[int(choice) - 1]["name"]

    # --------------------------------------------------------
    # Stage 5: fuzzy search
    # --------------------------------------------------------
    async with get_session() as db:
        fuzzy_candidates = await _search_buildings_fuzzy(
            db,
            search_name,
        )

    if not fuzzy_candidates:
        print(f"[NO_CANDIDATES] \nrow={row['id']} " f"search_name='{search_name}'")

        mark_review_building(row["id"])
        return False

    print(f"\n[BUILDING MATCH]\nrow={row['id']}\n" f"search_name='{search_name}'")

    for i, c in enumerate(fuzzy_candidates, start=1):
        print(f"  {i}. id={c.id} " f"name='{c.building_name}' " f"score={c.score:.3f}")

    print("  0. None of these — send to manual review")

    choice = input(f"Select match (0-{len(fuzzy_candidates)}): ").strip()

    if choice == "0" or choice not in [
        str(i) for i in range(1, len(fuzzy_candidates) + 1)
    ]:
        mark_review_building(row["id"])
        return False

    picked = fuzzy_candidates[int(choice) - 1]

    # --------------------------------------------------------
    # Stage 6: alias
    # --------------------------------------------------------
    # Fuzzy score is trigram similarity, not string equality (1.000 can still
    # differ by punctuation/case). The automatic lookup is lower(trim(x)) ==,
    # so decide on that.
    picked_norm = picked.building_name.strip().lower()

    alias_candidates = [
        c["name"] for c in candidates if c["name"].strip().lower() != picked_norm
    ]

    if alias_candidates:
        print("\n[ALIAS OPTIONS]")

        for i, alias in enumerate(alias_candidates, start=1):
            print(f"  {i}. {alias}")

        print("  0. No alias")

        alias_choice = input(
            f"Select alias to save (0-{len(alias_candidates)}): "
        ).strip()

        if alias_choice in [str(i) for i in range(1, len(alias_candidates) + 1)]:
            await add_building_alias(
                picked.id,
                alias_candidates[int(alias_choice) - 1],
            )

    return await finalize_entry(row, post_json, building_id=picked.id)
