import re

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from ...enums.advertisement import EnumAdsOwner

LALAFO_BASE_URL = "https://lalafo.kg"
KYRGYZSTAN_OWNER_URL = (
    f"{LALAFO_BASE_URL}/kyrgyzstan/kvartiry/arenda-kvartir/"
    "dolgosrochnaya-arenda-kvartir/owner"
)
KYRGYZSTAN_AGENT_URL = (
    f"{LALAFO_BASE_URL}/kyrgyzstan/kvartiry/arenda-kvartir/"
    "dolgosrochnaya-arenda-kvartir/agent/real-estate-agency"
)
BISHKEK_RENT_URL = f"{LALAFO_BASE_URL}/bishkek/kvartiry/arenda-kvartir"

_LISTING_ID_PATTERN = re.compile(r"-id-(\d+)(?:\D|$)")
_KGS_PRICE_PATTERN = re.compile(r"(\d[\d\s\u00a0,.]*)\s*(?:KGS|сом)", re.IGNORECASE)
_PUBLISHED_AT_PATTERN = re.compile(
    r"\b(\d{2})\.(\d{2})\.(\d{4})\s*/\s*(\d{2}):(\d{2})\b"
)
_KYRGYZSTAN_TIMEZONE = timezone(timedelta(hours=6))


@dataclass(frozen=True)
class LalafoSource:
    key: str
    url: str
    owner: EnumAdsOwner


LALAFO_SOURCES = (
    LalafoSource("general-owner", KYRGYZSTAN_OWNER_URL, EnumAdsOwner.OWNER),
    LalafoSource("general-agency", KYRGYZSTAN_AGENT_URL, EnumAdsOwner.AGENT),
    LalafoSource("general-capital", BISHKEK_RENT_URL, EnumAdsOwner.ANY),
)


@dataclass(frozen=True)
class LalafoListing:
    ads_id: str
    url: str
    title: str
    price: int | None
    city: str
    owner: EnumAdsOwner
    published_at: datetime | None


@dataclass(frozen=True)
class ParsedLalafoPage:
    listings: list[LalafoListing]
    next_page_url: str | None


def _text(node: Tag | None) -> str:
    if node is None:
        return ""
    return " ".join(node.get_text(" ", strip=True).split())


def _listing_city(url: str, article: Tag) -> str:
    path_parts = [part for part in urlparse(url).path.split("/") if part]
    if "ads" in path_parts:
        city_index = path_parts.index("ads") - 1
        if city_index >= 0 and path_parts[city_index] != "kyrgyzstan":
            return path_parts[city_index].lower()

    category_label = _text(article.select_one('[data-component="lf-ad-tile-horizontal-header"]')).lower()
    for caption in article.select('[data-component="lf-caption"]'):
        value = _text(caption)
        if value and not _PUBLISHED_AT_PATTERN.search(value) and not _KGS_PRICE_PATTERN.search(value):
            if value.lower() not in {"vip", "top", "premium"} and value.lower() not in category_label:
                return value.lower()
    return "kyrgyzstan"


def _published_at(article: Tag) -> datetime | None:
    for caption in article.select('[data-component="lf-caption"]'):
        match = _PUBLISHED_AT_PATTERN.search(_text(caption))
        if match is None:
            continue
        day, month, year, hour, minute = map(int, match.groups())
        try:
            return datetime(year, month, day, hour, minute, tzinfo=_KYRGYZSTAN_TIMEZONE)
        except ValueError:
            return None
    return None


def _listing_from_article(article: Tag, owner: EnumAdsOwner) -> LalafoListing | None:
    links = article.select('a[href*="/ads/"]')
    if not links:
        return None

    link = next(
        (candidate for candidate in links if candidate.select_one('p[data-component="lf-subheading"]')),
        links[0],
    )
    href = str(link.get("href", ""))
    id_match = _LISTING_ID_PATTERN.search(urlparse(href).path)
    title = _text(link.select_one('p[data-component="lf-subheading"]')) or _text(link)
    if id_match is None or not title:
        return None

    absolute_url = urljoin(LALAFO_BASE_URL, href)
    price_match = _KGS_PRICE_PATTERN.search(_text(article))
    price = None
    if price_match is not None:
        digits = re.sub(r"\D", "", price_match.group(1))
        price = int(digits) if digits else None

    return LalafoListing(
        ads_id=id_match.group(1),
        url=absolute_url,
        title=title,
        price=price,
        city=_listing_city(absolute_url, article),
        owner=owner,
        published_at=_published_at(article),
    )


def _next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    current_query = parse_qs(urlparse(current_url).query)
    current_page = int(current_query.get("page", ["1"])[0])
    candidates: list[tuple[int, str]] = []

    for link in soup.select('a[href]'):
        href = str(link.get("href", ""))
        absolute_url = urljoin(current_url, href)
        parsed = urlparse(absolute_url)
        if parsed.netloc and parsed.netloc != urlparse(LALAFO_BASE_URL).netloc:
            continue
        page_values = parse_qs(parsed.query).get("page", [])
        if not page_values:
            continue
        try:
            page_number = int(page_values[0])
        except ValueError:
            continue
        if page_number > current_page:
            candidates.append((page_number, absolute_url))

    if not candidates:
        return None
    return min(candidates, key=lambda candidate: candidate[0])[1]


def parse_lalafo_page(
    html: str,
    *,
    source_owner: EnumAdsOwner = EnumAdsOwner.ANY,
    page_url: str = LALAFO_BASE_URL,
) -> ParsedLalafoPage:
    soup = BeautifulSoup(html, "lxml")
    listings_by_id: dict[str, LalafoListing] = {}

    for article in soup.select('article[data-component="lf-ad-tile-horizontal"]'):
        listing = _listing_from_article(article, source_owner)
        if listing is not None:
            listings_by_id.setdefault(listing.ads_id, listing)

    return ParsedLalafoPage(
        listings=list(listings_by_id.values()),
        next_page_url=_next_page_url(soup, page_url),
    )