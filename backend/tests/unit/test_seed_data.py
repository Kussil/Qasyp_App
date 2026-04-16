import json
import re
from pathlib import Path


def load_profiles():
    data_path = Path(__file__).parent.parent.parent / "app" / "data" / "demo_profiles.json"
    with open(data_path) as f:
        return json.load(f)


def test_demo_profiles_buyer_supplier_balance():
    profiles = load_profiles()
    buyers = [p for p in profiles if p["role"] == "BUYER"]
    suppliers = [p for p in profiles if p["role"] == "SUPPLIER"]
    assert len(buyers) == 10, f"Expected 10 buyers, got {len(buyers)}"
    assert len(suppliers) == 10, f"Expected 10 suppliers, got {len(suppliers)}"


def test_demo_profiles_industry_coverage():
    profiles = load_profiles()
    industries = {p["industry_sector"] for p in profiles}
    assert len(industries) >= 5, f"Expected at least 5 industries, got {industries}"


def test_demo_profiles_region_diversity():
    profiles = load_profiles()
    all_regions = set()
    for p in profiles:
        all_regions.update(p.get("operating_regions", []))
    assert len(all_regions) >= 5, f"Expected at least 5 regions, got {all_regions}"


def test_demo_profiles_bin_format():
    profiles = load_profiles()
    for p in profiles:
        assert re.match(r"^[0-9]{12}$", p["bin"]), f"Invalid BIN for {p['company_name']}: {p['bin']}"


def test_demo_profiles_valid_schema():
    profiles = load_profiles()
    required = [
        "company_name", "bin", "legal_entity_type", "vat_registered",
        "industry_sector", "business_scope", "role", "operating_regions", "demo",
    ]
    for p in profiles:
        for field in required:
            assert field in p, f"Missing field '{field}' in profile id={p.get('id')}"
        assert p["demo"] is True
        assert p["role"] in ("BUYER", "SUPPLIER")
        assert len(p["bin"]) == 12


def test_demo_profiles_total_count():
    profiles = load_profiles()
    assert len(profiles) == 20, f"Expected 20 profiles, got {len(profiles)}"
