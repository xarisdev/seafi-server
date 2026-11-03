from enum import Enum

class EnumAdsSourceId(int, Enum):
    OPENL = 1
    OPENH = 2

class EnumAdsOwner(str, Enum):
    AGENT = "agent"
    OWNER = "owner"
    ANY = "any"

class EnumAdsType(str, Enum):
    RENT = "rent"
    SELL = "sell"