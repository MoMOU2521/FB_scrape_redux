# db.services.enter_all.py
def build_building_candidates(post_json):
    """
    Collect building names already available from extraction.
    Does not call AI.
    """
    building = post_json.get("building", {})

    candidates = []

    for source, name in [
        ("original", building.get("building_name")),
        ("standardized", building.get("building_name_standardized")),
    ]:
        if name:
            name = name.strip()

            if name and name not in [c["name"] for c in candidates]:
                candidates.append(
                    {
                        "source": source,
                        "name": name,
                    }
                )

    return candidates
