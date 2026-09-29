"""
backend/data/tamil_calendar_data.py — Tamil Calendar Dataset & Coimbatore Occasion Registry.

Contains authentic Tamil calendar months, Subha Muhurtham (சுப முகூர்த்த நாட்கள் - Auspicious Marriage Dates),
major Tamil festivals (பண்டிகைகள்), and temple car / public occasions with predefined bottleneck corridors.
"""
from typing import List, Dict, Any

TAMIL_MONTHS = [
    {"id": "CHITHIRAI", "tamil": "சித்திரை", "english": "Chithirai", "period": "Mid Apr – Mid May"},
    {"id": "VAIKASI",   "tamil": "வைகாசி",   "english": "Vaikasi",   "period": "Mid May – Mid Jun"},
    {"id": "AANI",      "tamil": "ஆனி",      "english": "Aani",      "period": "Mid Jun – Mid Jul"},
    {"id": "AADI",      "tamil": "ஆடி",      "english": "Aadi",      "period": "Mid Jul – Mid Aug"},
    {"id": "AVANI",     "tamil": "ஆவணி",     "english": "Avani",     "period": "Mid Aug – Mid Sep"},
    {"id": "PURATTASI", "tamil": "புரட்டாசி", "english": "Purattasi", "period": "Mid Sep – Mid Oct"},
    {"id": "AIPPASI",   "tamil": "ஐப்பசி",   "english": "Aippasi",   "period": "Mid Oct – Mid Nov"},
    {"id": "KARTHIGAI", "tamil": "கார்த்திகை", "english": "Karthigai", "period": "Mid Nov – Mid Dec"},
    {"id": "MARGAZHI",  "tamil": "மார்கழி",  "english": "Margazhi",  "period": "Mid Dec – Mid Jan"},
    {"id": "THAI",      "tamil": "தை",       "english": "Thai",      "period": "Mid Jan – Mid Feb"},
    {"id": "MASI",      "tamil": "மாசி",      "english": "Masi",      "period": "Mid Feb – Mid Mar"},
    {"id": "PANGUNI",   "tamil": "பங்குனி",   "english": "Panguni",   "period": "Mid Mar – Mid Apr"},
]

# 💍 Subha Muhurtham Dates (சுப முகூர்த்த நாட்கள் - Auspicious Marriage Dates)
SUBHA_MUHURTHAM_DATES: List[Dict[str, Any]] = [
    {
        "id": "muh_2026_09_11",
        "title": "Avani Subha Muhurtham (ஆவணி சுப முகூர்த்தம்)",
        "tamil_title": "ஆவணி 26 - வளர்பிறை முகூர்த்தம்",
        "category": "MARRIAGE",
        "tamil_month": "AVANI",
        "date": "2026-09-11",
        "muhurtham_time": "காலை 06:00 - 07:30 (Morning)",
        "tithi": "Shukla Paksha Dashami (வளர்பிறை)",
        "nakshatram": "Uthiradam (உத்திராடம்)",
        "venue_name": "Avinashi Road & Peelamedu Kalyana Mandapam Belt",
        "road_name": "Avinashi Road Arterial (NH-544)",
        "lat": 11.0244,
        "lng": 77.0028,
        "expected_crowd": 5500,
        "impact_level": "HIGH",
        "affected_corridors": ["Avinashi Road", "Peelamedu", "Hopes College", "Lakshmi Mills"],
        "description": "Massive marriage hall concentration along Avinashi Road and Goldwins corridor. Heavy morning and evening reception traffic."
    },
    {
        "id": "muh_2026_09_14",
        "title": "Avani Valarpirai Muhurtham (ஆவணி சுப முகூர்த்தம்)",
        "tamil_title": "ஆவணி 29 - சுப முகூர்த்தம்",
        "category": "MARRIAGE",
        "tamil_month": "AVANI",
        "date": "2026-09-14",
        "muhurtham_time": "காலை 09:00 - 10:30 (Morning)",
        "tithi": "Shukla Paksha Trayodashi",
        "nakshatram": "Thiruvonam (திருவோணம்)",
        "venue_name": "Trichy Road & Singanallur Marriage Halls",
        "road_name": "Trichy Road (SH-17)",
        "lat": 10.9995,
        "lng": 77.0090,
        "expected_crowd": 4800,
        "impact_level": "HIGH",
        "affected_corridors": ["Trichy Road", "Ramanathapuram", "Singanallur Junction", "Ondipudur"],
        "description": "Simultaneous wedding ceremonies across 18+ wedding halls. Major vehicular surge between Ramanathapuram and Singanallur."
    },
    {
        "id": "muh_2026_09_18",
        "title": "Avani Special Muhurtham (ஆவணி முகூர்த்தம்)",
        "tamil_title": "ஆவணி 32 - சுப முகூர்த்த நாள்",
        "category": "MARRIAGE",
        "tamil_month": "AVANI",
        "date": "2026-09-18",
        "muhurtham_time": "காலை 06:15 - 07:45 (Morning)",
        "tithi": "Krishna Paksha Ashtami",
        "nakshatram": "Rohini (ரோகிணி)",
        "venue_name": "Mettupalayam Road & Thudiyalur Mandapams",
        "road_name": "Mettupalayam Road (NH-181)",
        "lat": 11.0450,
        "lng": 76.9450,
        "expected_crowd": 4200,
        "impact_level": "MEDIUM",
        "affected_corridors": ["Mettupalayam Road", "Saibaba Colony", "Thudiyalur", "Kavundampalayam"],
        "description": "Morning marriage surge connecting Saibaba Colony to Thudiyalur marriage convention centres."
    },
    {
        "id": "muh_2026_10_22",
        "title": "Aippasi Subha Muhurtham (ஐப்பசி சுப முகூர்த்தம்)",
        "tamil_title": "ஐப்பசி 05 - சுப முகூர்த்த நாள்",
        "category": "MARRIAGE",
        "tamil_month": "AIPPASI",
        "date": "2026-10-22",
        "muhurtham_time": "காலை 06:00 - 07:30 (Morning)",
        "tithi": "Shukla Paksha Ekadashi",
        "nakshatram": "Uthiram (உத்திரம்)",
        "venue_name": "Pollachi Road & Eachanari Marriage Conventions",
        "road_name": "Pollachi Main Road (NH-83)",
        "lat": 10.9380,
        "lng": 76.9690,
        "expected_crowd": 5000,
        "impact_level": "HIGH",
        "affected_corridors": ["Pollachi Road", "Eachanari", "Kurichi", "Sundarapuram"],
        "description": "High auspicious wedding date with ceremonies scheduled from Eachanari junction to Malumichampatti."
    },
    {
        "id": "muh_2026_11_12",
        "title": "Karthigai Subha Muhurtham (கார்த்திகை சுப முகூர்த்தம்)",
        "tamil_title": "கார்த்திகை 02 - சுப முகூர்த்தம்",
        "category": "MARRIAGE",
        "tamil_month": "KARTHIGAI",
        "date": "2026-11-12",
        "muhurtham_time": "காலை 09:00 - 10:30 (Morning)",
        "tithi": "Shukla Paksha Dwitiya",
        "nakshatram": "Anusham (அனுஷம்)",
        "venue_name": "Avinashi Road & Peelamedu Convention Centers",
        "road_name": "Avinashi Road (NH-544)",
        "lat": 11.0280,
        "lng": 77.0150,
        "expected_crowd": 6000,
        "impact_level": "HIGH",
        "affected_corridors": ["Avinashi Road", "Peelamedu", "KMCH Junction", "Chitra Airport"],
        "description": "Peak auspicious wedding date in Karthigai month. Major bottleneck near airport junction and SITRA."
    },
    {
        "id": "muh_2027_01_25",
        "title": "Thai Subha Muhurtham (தை சுப முகூர்த்தம்)",
        "tamil_title": "தை 12 - தை மாத சுப முகூர்த்தம்",
        "category": "MARRIAGE",
        "tamil_month": "THAI",
        "date": "2027-01-25",
        "muhurtham_time": "காலை 06:00 - 07:30 (Morning)",
        "tithi": "Shukla Paksha Saptami",
        "nakshatram": "Revathi (ரேவதி)",
        "venue_name": "Sathy Road & Ganapathy Kalyana Mandapams",
        "road_name": "Sathy Main Road (NH-209)",
        "lat": 11.0360,
        "lng": 76.9850,
        "expected_crowd": 4800,
        "impact_level": "HIGH",
        "affected_corridors": ["Sathy Road", "Ganapathy", "Athipalayam Junction", "Saravanampatti"],
        "description": "Thai month auspicious wedding season launch with 20+ weddings around Ganapathy and Saravanampatti."
    },
    {
        "id": "muh_2027_02_15",
        "title": "Masi Subha Muhurtham (மாசி சுப முகூர்த்தம்)",
        "tamil_title": "மாசி 03 - சுப முகூர்த்த நாள்",
        "category": "MARRIAGE",
        "tamil_month": "MASI",
        "date": "2027-02-15",
        "muhurtham_time": "காலை 09:15 - 10:45 (Morning)",
        "tithi": "Shukla Paksha Navami",
        "nakshatram": "Mirugaseerisham (மிருகசீரிஷம்)",
        "venue_name": "RS Puram & DB Road Community Halls",
        "road_name": "DB Road, RS Puram",
        "lat": 11.0094,
        "lng": 76.9458,
        "expected_crowd": 4000,
        "impact_level": "MEDIUM",
        "affected_corridors": ["DB Road", "RS Puram", "Cowley Brown Road", "Thadagam Road"],
        "description": "Prominent community marriages in RS Puram causing parking spillover onto DB Road and Thadagam Road."
    },
    {
        "id": "muh_2027_03_18",
        "title": "Panguni Uthira Muhurtham (பங்குனி உத்திர முகூர்த்தம்)",
        "tamil_title": "பங்குனி 04 - உத்திர சுப முகூர்த்தம்",
        "category": "MARRIAGE",
        "tamil_month": "PANGUNI",
        "date": "2027-03-18",
        "muhurtham_time": "காலை 06:00 - 07:30 (Morning)",
        "tithi": "Shukla Paksha Ekadashi",
        "nakshatram": "Uthiram (உத்திரம்)",
        "venue_name": "Avinashi Road & Trichy Road Belt",
        "road_name": "Avinashi Road (NH-544)",
        "lat": 11.0244,
        "lng": 77.0028,
        "expected_crowd": 6500,
        "impact_level": "CRITICAL",
        "affected_corridors": ["Avinashi Road", "Trichy Road", "Gandhipuram", "Peelamedu"],
        "description": "Panguni Uthiram is the most auspicious marriage day of the year. Hundreds of halls booked simultaneously."
    }
]

# 🪔 Major Tamil Festivals (பண்டிகைகள்)
TAMIL_FESTIVALS: List[Dict[str, Any]] = [
    {
        "id": "fest_deepavali_2026",
        "title": "Deepavali Festival Shopping & Celebrations (தீபாவளி திருநாள்)",
        "tamil_title": "தீபாவளி பண்டிகை & கடைவீதி கூட்டம்",
        "category": "FESTIVAL",
        "tamil_month": "AIPPASI",
        "date": "2026-11-08",
        "timing": "முழு நாள் (All Day)",
        "venue_name": "Town Hall, Cross Cut Road & Gandhipuram Markets",
        "road_name": "Cross Cut Road & Raja Street",
        "lat": 11.0168,
        "lng": 76.9558,
        "expected_crowd": 25000,
        "impact_level": "CRITICAL",
        "affected_corridors": ["Cross Cut Road", "Town Hall", "100 Feet Road", "Gandhipuram Central", "Oppanakara Street"],
        "description": "Huge festive market rush. Severe traffic congestion on Cross Cut Road, Raja Street, and Gandhipuram bus terminus."
    },
    {
        "id": "fest_karthigai_2026",
        "title": "Karthigai Deepam Festival (கார்த்திகை தீபம்)",
        "tamil_title": "கார்த்திகை மகா தீபம்",
        "category": "FESTIVAL",
        "tamil_month": "KARTHIGAI",
        "date": "2026-11-23",
        "timing": "மாலை 05:00 - 10:00 (Evening)",
        "venue_name": "Marudhamalai Subramaniya Swamy Temple & City Temples",
        "road_name": "Marudhamalai Main Road",
        "lat": 11.0450,
        "lng": 76.8520,
        "expected_crowd": 18000,
        "impact_level": "HIGH",
        "affected_corridors": ["Marudhamalai Road", "Vadavalli", "Lawley Road", "Thondamuthur Road"],
        "description": "Thousands of devotees climb Marudhamalai hill temple for lighting of Mahadeepam. Traffic queued from Lawley Road."
    },
    {
        "id": "fest_pongal_2027",
        "title": "Thai Pongal & Harvest Festival (தைப்பொங்கல் திருநாள்)",
        "tamil_title": "உழவர் திருநாள் & தைப்பொங்கல்",
        "category": "FESTIVAL",
        "tamil_month": "THAI",
        "date": "2027-01-14",
        "timing": "முழு நாள் (All Day)",
        "venue_name": "Coimbatore City & Agricultural Belt",
        "road_name": "Ukkadam & Singanallur Bus Corridors",
        "lat": 10.9892,
        "lng": 76.9613,
        "expected_crowd": 30000,
        "impact_level": "CRITICAL",
        "affected_corridors": ["Ukkadam Bypass", "Singanallur Bus Stand", "Pollachi Highway", "Gandhipuram SETC"],
        "description": "Major inter-district holiday travel outward rush. Bus stands jammed with passengers returning to villages."
    },
    {
        "id": "fest_kaanum_pongal_2027",
        "title": "Kaanum Pongal Sightseeing Rush (காணும் பொங்கல்)",
        "tamil_title": "காணும் பொங்கல் சுற்றுலா கூட்டம்",
        "category": "FESTIVAL",
        "tamil_month": "THAI",
        "date": "2027-01-16",
        "timing": "மதியம் 01:00 - இரவு 09:00 (Afternoon-Night)",
        "venue_name": "VOC Park, Kovai Kutralam & Perur Padithurai",
        "road_name": "Siruvani Road & Avinashi Road",
        "lat": 11.0020,
        "lng": 76.9720,
        "expected_crowd": 22000,
        "impact_level": "HIGH",
        "affected_corridors": ["VOC Park (Avinashi Rd)", "Siruvani Road", "Perur Road", "Race Course"],
        "description": "Public outing and family gatherings at VOC Park Zoo and Kovai Kutralam picnic spots. Heavy parking overflow."
    },
    {
        "id": "fest_puthandu_2027",
        "title": "Tamil New Year Day (தமிழ்ப்புத்தாண்டு - சித்திரை 1)",
        "tamil_title": "சித்திரை 1 - தமிழ்ப் புத்தாண்டு",
        "category": "FESTIVAL",
        "tamil_month": "CHITHIRAI",
        "date": "2027-04-14",
        "timing": "காலை 05:00 - மதியம் 01:00 (Morning)",
        "venue_name": "Perur, Eachanari & Koniamman Temples",
        "road_name": "Perur Main Road & Raja Street",
        "lat": 10.9700,
        "lng": 76.9150,
        "expected_crowd": 20000,
        "impact_level": "HIGH",
        "affected_corridors": ["Perur Main Road", "Town Hall", "Pollachi Road (Eachanari)"],
        "description": "Devotees throng all major temples across the city for Vishu Kani darshan and special poojas."
    },
    {
        "id": "fest_aadi_perukku_2027",
        "title": "Aadi Perukku River Festival (ஆடிப் பெருக்கு)",
        "tamil_title": "ஆடி 18 - ஆடிப்பெருக்கு விழா",
        "category": "FESTIVAL",
        "tamil_month": "AADI",
        "date": "2027-08-03",
        "timing": "காலை 06:00 - மாலை 04:00 (Daytime)",
        "venue_name": "Noyyal River Banks & Perur Padithurai",
        "road_name": "Perur Main Road",
        "lat": 10.9680,
        "lng": 76.9180,
        "expected_crowd": 15000,
        "impact_level": "MEDIUM",
        "affected_corridors": ["Perur Padithurai", "Sundakkamuthur Road", "Ukkadam-Perur Link"],
        "description": "Traditional poojas along the Noyyal River at Perur Padithurai. Heavy vehicular density on narrow Perur roads."
    },
    {
        "id": "fest_vinayagar_2027",
        "title": "Vinayagar Chaturthi & Idol Procession (விநாயகர் சதுர்த்தி)",
        "tamil_title": "விநாயகர் சதுர்த்தி ஊர்வலம்",
        "category": "FESTIVAL",
        "tamil_month": "AVANI",
        "date": "2027-09-04",
        "timing": "மதியம் 02:00 - இரவு 09:00 (Procession)",
        "venue_name": "Raja Street, Town Hall to Kurichi Kulam",
        "road_name": "Town Hall to Ukkadam / Kurichi Road",
        "lat": 10.9950,
        "lng": 76.9600,
        "expected_crowd": 28000,
        "impact_level": "CRITICAL",
        "affected_corridors": ["Town Hall", "Raja Street", "Oppanakara Street", "Ukkadam Big Tank", "Kurichi Lake"],
        "description": "Grand Vinayagar idol immersion procession. Major arterial roads barricaded with dedicated diversion routes."
    }
]

# 🛕 Temple Car Festivals & Special Occasions (கோவில் தேர்த் திருவிழாக்கள் & விசேஷங்கள்)
TEMPLE_OCCASIONS: List[Dict[str, Any]] = [
    {
        "id": "occ_koniamman_ther",
        "title": "Arulmigu Koniamman Temple Ther Thiruvizha (கோனியம்மன் தேர் திருவிழா)",
        "tamil_title": "மாசி மாதக் கோனியம்மன் மகா தேரோட்டம்",
        "category": "TEMPLE_OCCASION",
        "tamil_month": "MASI",
        "date": "2027-03-03",
        "timing": "மதியம் 01:30 - இரவு 08:30 (Car Procession)",
        "venue_name": "Raja Street, Town Hall & Oppanakara Street",
        "road_name": "Raja Street & Vysial Street",
        "lat": 10.9950,
        "lng": 76.9600,
        "expected_crowd": 40000,
        "impact_level": "CRITICAL",
        "affected_corridors": ["Raja Street (Complete Choke)", "Oppanakara Street", "Town Hall", "Mill Road", "Big Bazaar St"],
        "description": "Coimbatore's biggest heritage temple car festival. Raja Street and surrounding 2 km arterial core completely closed for vehicular traffic."
    },
    {
        "id": "occ_perur_ther",
        "title": "Perur Pateeswarar Temple Car Festival (பேரூர் பட்டீஸ்வரர் தேரோட்டம்)",
        "tamil_title": "பங்குனி உத்திரப் பேரூர் தேரோட்டம்",
        "category": "TEMPLE_OCCASION",
        "tamil_month": "PANGUNI",
        "date": "2027-03-24",
        "timing": "காலை 07:00 - மதியம் 02:00 (Car Pulling)",
        "venue_name": "Four Ratha Streets of Perur Temple",
        "road_name": "Perur Main Road",
        "lat": 10.9720,
        "lng": 76.9140,
        "expected_crowd": 25000,
        "impact_level": "CRITICAL",
        "affected_corridors": ["Perur Main Road", "Siruvani Main Road", "Telungupalayam", "Selvapuram"],
        "description": "Ancient Shiva temple chariot festival. Perur Car streets blocked. Traffic diverted via Selvapuram and Kovaipudur bypass."
    },
    {
        "id": "occ_marudhamalai_thaipoosam",
        "title": "Marudhamalai Thai Poosam Thiruvizha (மருதமலை தைப்பூசத் திருவிழா)",
        "tamil_title": "தைப்பூசத் தேரோட்டம் & காவடி ஊர்வலம்",
        "category": "TEMPLE_OCCASION",
        "tamil_month": "THAI",
        "date": "2027-01-22",
        "timing": "காலை 04:00 - நள்ளிரவு (All Day & Night)",
        "venue_name": "Marudhamalai Murugan Hill Temple",
        "road_name": "Vadavalli to Marudhamalai Road",
        "lat": 11.0450,
        "lng": 76.8520,
        "expected_crowd": 35000,
        "impact_level": "CRITICAL",
        "affected_corridors": ["Marudhamalai Main Road", "Vadavalli Junction", "Lawley Road Junction", "Thondamuthur Road"],
        "description": "Massive foot procession (Padayatra) and Kavadi carriers occupying Vadavalli-Marudhamalai Road. Private vehicles restricted."
    },
    {
        "id": "occ_isha_shivaratri",
        "title": "Isha Maha Shivaratri Global Night Gathering (ஈஷா மகா சிவராத்திரி)",
        "tamil_title": "மகா சிவராத்திரி விழா & இரவு விழிப்பு",
        "category": "TEMPLE_OCCASION",
        "tamil_month": "MASI",
        "date": "2027-03-06",
        "timing": "மாலை 04:00 - விடியற்காலை 06:00 (Overnight)",
        "venue_name": "Isha Yoga Center, Velliangiri Foothills",
        "road_name": "Siruvani Road & Thondamuthur Main Road",
        "lat": 10.9730,
        "lng": 76.7400,
        "expected_crowd": 120000,
        "impact_level": "CRITICAL",
        "affected_corridors": ["Siruvani Road", "Thondamuthur", "Alandurai", "Perur Road", "Vadavalli-Thondamuthur Link"],
        "description": "Over 1.2 lakh devotees and tourists travel via Siruvani Road. Severe 15-km gridlock on Thondamuthur road without bypass."
    },
    {
        "id": "occ_eachanari_chathurthi",
        "title": "Eachanari Vinayagar Temple Car Special Pooja (ஈச்சனாரி விசேஷம்)",
        "tamil_title": "ஈச்சனாரி விநாயகர் சிறப்பு பூஜை & கூட்டம்",
        "category": "TEMPLE_OCCASION",
        "tamil_month": "AVANI",
        "date": "2027-09-05",
        "timing": "காலை 05:00 - இரவு 09:00",
        "venue_name": "Eachanari Vinayagar Temple, Pollachi Highway",
        "road_name": "Pollachi Main Road (NH-83)",
        "lat": 10.9380,
        "lng": 76.9690,
        "expected_crowd": 16000,
        "impact_level": "HIGH",
        "affected_corridors": ["Pollachi Road", "Kurichi", "SIDCO Industrial Area", "Sundarapuram"],
        "description": "Highway temple on Pollachi Road causes massive spillover parking and lane reductions on NH-83."
    }
]


def get_all_tamil_calendar_events(category: str = None, month: str = None) -> List[Dict[str, Any]]:
    """
    Returns unified list of Tamil Calendar events with optional category and month filter.
    """
    all_events = []
    
    # Tag and compile
    for item in SUBHA_MUHURTHAM_DATES:
        all_events.append({**item, "event_type": "MARRIAGE", "category_label": "Subha Muhurtham (சுப முகூர்த்தம்)"})
        
    for item in TAMIL_FESTIVALS:
        all_events.append({**item, "event_type": "FESTIVAL", "category_label": "Tamil Festival (பண்டிகை)"})
        
    for item in TEMPLE_OCCASIONS:
        all_events.append({**item, "event_type": "PUBLIC_EVENT", "category_label": "Temple Car & Occasion (தேர்த் திருவிழா)"})
        
    # Apply category filter
    if category and category.upper() != "ALL":
        all_events = [e for e in all_events if e.get("category", "").upper() == category.upper() or e.get("event_type", "").upper() == category.upper()]
        
    # Apply month filter
    if month and month.upper() != "ALL":
        all_events = [e for e in all_events if e.get("tamil_month", "").upper() == month.upper()]
        
    # Sort chronologically
    all_events.sort(key=lambda x: x.get("date", ""))
    return all_events
