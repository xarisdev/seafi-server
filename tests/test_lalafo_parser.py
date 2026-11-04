from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.enums.advertisement import EnumAdsOwner
from src.integrations.lalafo.parser import parse_lalafo_page


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "lalafo_listing_page.html"


def test_parse_lalafo_listing_page():
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    page = parse_lalafo_page(
        html,
        source_owner=EnumAdsOwner.AGENT,
        page_url="https://lalafo.kg/kyrgyzstan/kvartiry/arenda-kvartir/agent/real-estate-agency",
    )

    assert len(page.listings) == 1
    listing = page.listings[0]
    assert listing.ads_id == "123456789"
    assert listing.url == "https://lalafo.kg/bishkek/ads/2-komnaty-id-123456789"
    assert listing.title == "2 комнаты, долгосрочная аренда"
    assert listing.price == 35000
    assert listing.city == "bishkek"
    assert listing.owner is EnumAdsOwner.AGENT
    assert listing.published_at == datetime(
        2026,
        11,
        3,
        20,
        10,
        tzinfo=timezone(timedelta(hours=6)),
    )
    assert page.next_page_url == "https://lalafo.kg/kyrgyzstan/kvartiry/arenda-kvartir?page=2"


def test_source_profile_assigns_owner_type():
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    page = parse_lalafo_page(html, source_owner=EnumAdsOwner.OWNER)

    assert page.listings[0].owner is EnumAdsOwner.OWNER


def test_parser_ignores_next_home_feed_data():
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    page = parse_lalafo_page(html)

    assert [listing.ads_id for listing in page.listings] == ["123456789"]


def test_city_falls_back_to_location_caption_when_url_has_country_slug():
    html = FIXTURE_PATH.read_text(encoding="utf-8").replace(
        "https://lalafo.kg/bishkek/ads/",
        "https://lalafo.kg/kyrgyzstan/ads/",
    )

    page = parse_lalafo_page(html)

    assert page.listings[0].city == "бишкек"