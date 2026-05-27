import difflib

NEIGHBORHOODS = {

    # ─────────────────────────────────────────────────────────────────
    # OAHU — WINDWARD
    # ─────────────────────────────────────────────────────────────────

    "Kailua": {
        "island": "Oahu",
        "region": "Windward",
        "vibe": "Kailua is Oahu's most beloved beach town — walkable, charming, and fiercely local. It attracts a mix of longtime kamaaina families, remote workers, military officers, and mainlanders chasing the quintessential Hawaii lifestyle without the tourist crush. The vibe is relaxed but upscale, with boutique shops, acclaimed restaurants, and a strong paddling and cycling culture.",
        "lifestyle": "Mornings start with sunrise swims at Kailua Beach or early runs on the flat beachside path. Days revolve around the beach, Lanikai Pillbox hike, kayaking to the Mokulua islands, and the small-town main street with local cafes and farmers markets. Evenings are quiet — this is not a nightlife town, and residents love it that way.",
        "nearby": ["Kailua Beach Park", "Lanikai Beach", "Mokulua Islands", "Pali Highway", "Kaneohe Bay", "Whole Foods Kailua", "Kailua Town Center"],
        "beaches": ["Kailua Beach", "Lanikai Beach", "Kalama Beach Park"],
        "commute": "Over the Pali Highway to Honolulu — typically 30-45 min in light traffic, 50-75 min during morning rush. Likelike Highway is an alternate route. No rail service; car-dependent.",
        "market_notes": "Highly desirable and consistently appreciating. Fee simple dominates with some leasehold pockets. HOAs are present but not pervasive. Flood zone exposure near the beach and canal areas — buyers should review FEMA maps carefully. Demand from military (MCBH is next door), remote workers, and second-home buyers. Inventory is perpetually tight, driving strong seller conditions.",
        "keywords": ["beach town", "walkable", "Lanikai", "paddling", "bike-friendly", "kamaaina", "windward"],
        "aliases": ["Kai Lua", "Kailua Oahu", "Kailua Town", "Kailua Beach Town", "Kailua-Oahu"]
    },

    "Lanikai": {
        "island": "Oahu",
        "region": "Windward",
        "vibe": "Lanikai is one of the most exclusive residential pockets in Hawaii — a small grid of streets tucked between the Ko'olau Mountains and what many call the most beautiful beach in America. It's purely residential, extremely private, and home to a small community of longtime residents and wealthy second-home owners.",
        "lifestyle": "Life here centers entirely on the beach — morning swims, kayaking to the Moku Nui and Moku Iki islands, and the famous Pillbox hike above. There are no commercial amenities within Lanikai itself; residents walk or bike to Kailua Town for everything. Privacy and beauty are the trade: no hotels, no tourists who know where they're going.",
        "nearby": ["Lanikai Pillbox Trail", "Mokulua Islands", "Kailua Beach Park", "Kailua Town", "MCBH Kaneohe Bay"],
        "beaches": ["Lanikai Beach", "Kailua Beach"],
        "commute": "Same as Kailua — Pali or Likelike to Honolulu, 35-75 min depending on traffic. Narrow residential streets make getting in and out slower than it looks on a map.",
        "market_notes": "Among the most expensive per-square-foot real estate on Oahu. Mostly fee simple, older single-family homes on small lots. Flood zone risk is real — mandatory flood insurance adds cost. No vacation rental permits — strong community resistance to STR activity. Buyers are typically cash or near-cash, often second-home purchasers. Very low inventory, very slow turnover.",
        "keywords": ["exclusive", "luxury", "private", "beach", "second home", "pillbox", "Mokulua"],
        "aliases": ["Lanikai Beach", "Lanikai Kailua", "Lanikai Oahu", "La Ni Kai"]
    },

    "Kaneohe": {
        "island": "Oahu",
        "region": "Windward",
        "vibe": "Kaneohe is Windward Oahu's largest town — lush, green, and family-oriented without the tourist cachet of Kailua. It's a working community with a strong military presence (MCBH borders it), good schools, and a genuine neighborhood feel. The bay is one of the most beautiful in Hawaii and largely protected from development.",
        "lifestyle": "Kaneohe life is suburban and outdoor-focused — hiking in the Ko'olau foothills, fishing and kayaking on the bay, and weekend trips to Kualoa Ranch. It's quieter and more affordable than Kailua, which draws families who want space, good schools, and nature access without the premium price tag.",
        "nearby": ["Kaneohe Bay", "He'eia State Park", "Kualoa Ranch", "Valley of the Temples", "MCBH Kaneohe Bay", "Ho'omaluhia Botanical Garden"],
        "beaches": ["Kaneohe Bay (no swim beach)", "Kailua Beach (nearby)"],
        "commute": "H-3 freeway access to downtown Honolulu — typically 25-40 min. One of the better commutes from Windward. Also accessible via Likelike Highway.",
        "market_notes": "More affordable than Kailua with a mix of fee simple and leasehold. Flood risk in low-lying areas near the bay. Strong military rental demand from MCBH families. Larger lot sizes than Kailua. HOAs present in newer subdivisions. Value-driven buyers find better space-to-price ratios here.",
        "keywords": ["family", "military", "lush", "bay", "affordable", "schools", "Ko'olau"],
        "aliases": ["Kane'ohe", "Kaneohe Oahu", "Kaneohe Town", "Kaneoh"]
    },

    "Waimanalo": {
        "island": "Oahu",
        "region": "Windward",
        "vibe": "Waimanalo is the most rural and authentically Hawaiian community on the Windward side — agricultural lands, taro farms, and a deeply rooted Native Hawaiian population. It's raw, real, and beautiful with a 3.5-mile stretch of white sand beach that rivals anything in Hawaii.",
        "lifestyle": "Life here is unhurried and community-centered. Residents keep horses, grow food, and gather at the beach. It's not a place for amenities or nightlife — the nearest grocery is in Kailua. The beach is almost always uncrowded despite being stunning. Strong local identity; newcomers are welcomed but should come with respect.",
        "nearby": ["Waimanalo Beach Park", "Makapuu Lookout", "Sea Life Park", "Bellows Beach", "Kailua Town"],
        "beaches": ["Waimanalo Beach", "Bellows Beach (military/public weekends)", "Sherwood Forest Beach"],
        "commute": "35-55 min to Honolulu via H-3 or Pali. Limited public transit. Car essential.",
        "market_notes": "Many parcels in Waimanalo are on Hawaiian Home Lands — not available for general purchase. Fee simple inventory is limited and turns over rarely. Agricultural zoning affects some parcels. Buyers must verify zoning and land status carefully. Flood and hurricane risk is moderate. Strong community resistance to outside development.",
        "keywords": ["rural", "Hawaiian", "agricultural", "beach", "horses", "taro", "local"],
        "aliases": ["Waimanalo Beach", "Waimanalo Valley", "Waimānalo"]
    },

    # ─────────────────────────────────────────────────────────────────
    # OAHU — EAST HONOLULU
    # ─────────────────────────────────────────────────────────────────

    "Hawaii Kai": {
        "island": "Oahu",
        "region": "East Honolulu",
        "vibe": "Hawaii Kai is a master-planned marina community that feels like an upscale Southern California suburb dropped into a Hawaii bay. It's family-friendly, boat-owning, and comfortable — not flashy but consistently desirable. Strong school district, safe streets, and a self-contained lifestyle make it a top choice for families.",
        "lifestyle": "Weekend life revolves around the marina — paddleboarding, kayaking, and boating straight from your backyard if you have a waterfront lot. Hanauma Bay and Sandy Beach are minutes away. The Koko Marina Center handles most daily needs. Mornings are quiet and residential; the pace is decidedly suburban.",
        "nearby": ["Hanauma Bay", "Sandy Beach", "Koko Marina Center", "Koko Head Crater Trail", "Makapu'u Lighthouse", "Costco Hawaii Kai"],
        "beaches": ["Sandy Beach", "Hanauma Bay", "Makapu'u Beach"],
        "commute": "H-1 to downtown Honolulu — 20-35 min in light traffic, 45-65 min during morning rush. One of the longer east-side commutes but consistent.",
        "market_notes": "Heavy mix of fee simple and leasehold — buyers must check each listing carefully. Leasehold renegotiation risk is real and has historically shocked buyers. Marina frontage commands significant premium. HOAs are common and active. Good school district (Kaiser, Kalani) drives family demand. Flood risk in low marina areas. Strong appreciation over time.",
        "keywords": ["marina", "family", "boats", "Koko Head", "suburban", "schools", "leasehold risk"],
        "aliases": ["HI Kai", "Hawaii Kai Oahu", "Koko Marina", "Hawaii-Kai", "HawaiiKai"]
    },

    "Aina Haina": {
        "island": "Oahu",
        "region": "East Honolulu",
        "vibe": "Aina Haina is a quiet, residential valley between Hawaii Kai and Kahala — understated, convenient, and family-oriented. It lacks the prestige of Kahala or the amenities of Hawaii Kai but offers solid value and easy freeway access in a low-key suburban setting.",
        "lifestyle": "A purely residential neighborhood — families come here for the schools, the relative affordability, and the quick freeway access. Small neighborhood shopping center handles daily needs. Hiking access into the valleys behind the neighborhood.",
        "nearby": ["Aina Haina Shopping Center", "Kahala Mall", "Niu Valley", "Hawaii Kai", "Kahala"],
        "beaches": ["Niu Beach", "Kahala Beach (nearby)"],
        "commute": "H-1 west to Honolulu — 15-25 min, one of the more convenient East Honolulu commutes.",
        "market_notes": "Good value relative to Kahala and Hawaii Kai. Mix of fee simple and leasehold. Older housing stock, mostly 1960s-80s builds. Steady appreciation. Less competitive than Kailua or Kahala but consistent demand from families and professionals.",
        "keywords": ["residential", "family", "value", "East Honolulu", "freeway access"],
        "aliases": ["Aina Haina Oahu", "'Āina Haina", "Ainahaina"]
    },

    "Kahala": {
        "island": "Oahu",
        "region": "East Honolulu",
        "vibe": "Kahala is old Honolulu money — quiet tree-lined streets, large lots, and some of the most valuable residential real estate on the island. It's the address of Honolulu's established wealthy families, away from the tourist scene but minutes from everything. Understated luxury, not showy.",
        "lifestyle": "Mornings at Kahala Beach, evenings at the Kahala Hotel. Life is unhurried and private. Residents are typically established professionals, executives, and old-island families. Kahala Mall is steps away for daily errands. No tourist scene, no congestion.",
        "nearby": ["Kahala Hotel & Resort", "Kahala Mall", "Diamond Head", "Waialae Country Club", "Aina Haina"],
        "beaches": ["Kahala Beach", "Diamond Head Beach (nearby)"],
        "commute": "10-20 min to downtown Honolulu on H-1 — one of the better proximity-to-downtown ratios on the island.",
        "market_notes": "Predominantly fee simple, large lots, very low inventory. Among the most stable and expensive markets on Oahu. Strong cash buyer pool. Waialae Country Club golf course adjacency adds value. Very little new construction — mostly older homes with renovation potential. Buyers compete hard when listings come available.",
        "keywords": ["luxury", "established", "large lots", "fee simple", "old money", "quiet", "private"],
        "aliases": ["Kahala Oahu", "Kahala Honolulu", "Ka Hala"]
    },

    "Diamond Head": {
        "island": "Oahu",
        "region": "East Honolulu",
        "vibe": "Diamond Head neighborhoods wrap around the base of the iconic crater — a mix of older estates, mid-century homes, and newer builds with dramatic crater and ocean views. Prestigious address with proximity to Waikiki but none of its chaos.",
        "lifestyle": "Iconic morning hikes up Diamond Head Crater, surfing at Cliffs surf break and Kaimana Beach, and easy walking to the museum strip. A culturally rich residential area with a strong sense of place tied to the landmark itself.",
        "nearby": ["Diamond Head State Monument", "Kapiolani Park", "Waikiki", "Honolulu Museum of Art", "Kaimana Beach Hotel"],
        "beaches": ["Kaimana Beach", "Kapiolani Beach", "Diamond Head Beach"],
        "commute": "5-15 min to downtown Honolulu. Excellent central location.",
        "market_notes": "Premium address with ocean and crater views commanding top dollar. Mix of fee simple and leasehold. Some historic designation protections. Vacation rental restrictions in residential zones. Moderate earthquake and tsunami zone awareness needed. High demand, low inventory.",
        "keywords": ["views", "crater", "iconic", "prestigious", "surfing", "Kapiolani Park"],
        "aliases": ["Diamond Head Honolulu", "Diamond Head Oahu", "Punchbowl area", "Le'ahi"]
    },

    # ─────────────────────────────────────────────────────────────────
    # OAHU — CENTRAL HONOLULU
    # ─────────────────────────────────────────────────────────────────

    "Manoa": {
        "island": "Oahu",
        "region": "Central Honolulu",
        "vibe": "Manoa is Honolulu's beloved academic valley — lush, cool, and intellectually alive as home to UH Manoa. The neighborhood is a genuine community with long-term residents, professors, families, and renters. The valley's microclimate means frequent rain showers and impossibly green landscapes.",
        "lifestyle": "Hiking Manoa Falls on weekday mornings before the crowds. Coffee at local cafes near UH. Family dinners in a neighborhood that still feels like it has roots. The pace is less frenetic than urban Honolulu but highly walkable to campus.",
        "nearby": ["University of Hawaii at Manoa", "Manoa Falls Trail", "Lyon Arboretum", "Punahou School", "Manoa Marketplace"],
        "beaches": ["Ala Moana Beach (nearby)", "Waikiki (nearby)"],
        "commute": "10-20 min to downtown Honolulu. Excellent access via surface streets and H-1.",
        "market_notes": "Strong rental demand from UH faculty and graduate students. Mix of owner-occupied homes and investment rentals. Older housing stock. Flood risk in low-lying sections (Manoa Stream flooding history). Fee simple dominant. Good long-term appreciation driven by constrained supply and academic demand.",
        "keywords": ["university", "green", "valley", "hiking", "academic", "rental demand", "rain"],
        "aliases": ["Manoa Valley", "Manoa Honolulu", "Mānoa"]
    },

    "Nuuanu": {
        "island": "Oahu",
        "region": "Central Honolulu",
        "vibe": "Nuuanu is one of Honolulu's oldest and most historically significant neighborhoods — where Hawaiian royalty built summer retreats and where the Battle of Nu'uanu ended Hawaiian kingdom resistance in 1795. It's cool, tree-canopied, and architecturally rich with historic bungalows and estates.",
        "lifestyle": "A quiet residential valley above the downtown bustle. Residents prize the cooler temperatures, the historic character, and the easy access to both downtown and the Pali. Weekend hikes to Judd Trail or the Pali Lookout. A contemplative, history-conscious community.",
        "nearby": ["Nuuanu Pali Lookout", "Royal Mausoleum", "Oahu Cemetery", "Judd Memorial Trail", "Downtown Honolulu"],
        "beaches": ["Downtown waterfront (no swim beach)", "Ala Moana (nearby)"],
        "commute": "5-10 min to downtown Honolulu — one of the best commute locations on Oahu.",
        "market_notes": "Historically stable, architecturally significant properties. Many homes are older and need updating. Fee simple dominant. Some historic designation restrictions. Cool microclimate can mean moisture/mold considerations. Good long-term value for buyers who understand the older housing stock.",
        "keywords": ["historic", "cool", "trees", "royalty", "architecture", "downtown access"],
        "aliases": ["Nu'uanu", "Nuuanu Valley", "Nuuanu Honolulu", "Nuanu"]
    },

    "Punchbowl": {
        "island": "Oahu",
        "region": "Central Honolulu",
        "vibe": "Punchbowl is a tight-knit residential neighborhood built around the rim and slopes of Puowaina crater. It's working-class Honolulu with deep roots — many families have been here for generations. The National Memorial Cemetery of the Pacific is here, lending a quiet solemnity to the neighborhood.",
        "lifestyle": "Dense urban living on sloping streets with valley views. Walking distance to downtown and the medical corridor. A neighborhood for people who want central Honolulu living without Kakaako prices.",
        "nearby": ["National Memorial Cemetery of the Pacific", "Queen's Medical Center", "Downtown Honolulu", "Makiki", "Nuuanu"],
        "beaches": ["Ala Moana Beach (nearby)"],
        "commute": "5-10 min to downtown Honolulu. Excellent centrality.",
        "market_notes": "Affordable relative to nearby Makiki and Nuuanu. Older housing stock, compact lots. Some leasehold. Strong rental demand from medical workers at Queen's and Straub. Flood zone not a primary concern at elevation. Buyers often include investors and first-time buyers seeking central location value.",
        "keywords": ["central", "historic", "affordable", "medical", "compact", "working-class"],
        "aliases": ["Punchbowl Crater", "Punchbowl Honolulu", "Puowaina", "Tantalus-Punchbowl"]
    },

    "Makiki": {
        "island": "Oahu",
        "region": "Central Honolulu",
        "vibe": "Makiki is a dense mid-Honolulu neighborhood popular with young professionals and longtime residents who want urban walkability with more space than Kakaako or Waikiki. It climbs the lower slopes of Tantalus and transitions from mid-rise condos at its base to older single-family homes uphill.",
        "lifestyle": "Urban-adjacent — walk to downtown or Ala Moana, then retreat uphill for quiet evenings. Makiki District Park and easy Tantalus trail access. A transit-friendly location.",
        "nearby": ["Makiki District Park", "Round Top Drive", "Tantalus Crater", "Ala Moana Center", "Downtown Honolulu"],
        "beaches": ["Ala Moana Beach (nearby)"],
        "commute": "10-15 min to downtown. Good TheBus access. Very central.",
        "market_notes": "Mix of condos, older single-family, and some multifamily. Leasehold condos present — check land tenure. Renters and young professionals dominate demand. Older building stock means deferred maintenance risk. Good investment market. Moderate appreciation, stable demand.",
        "keywords": ["urban", "young professionals", "walkable", "condos", "central", "Tantalus access"],
        "aliases": ["Makiki Honolulu", "Makiki Heights", "Makiki Valley"]
    },

    "Tantalus": {
        "island": "Oahu",
        "region": "Central Honolulu",
        "vibe": "Tantalus is Honolulu's hidden mountain enclave — a winding road through dense jungle with panoramic city and ocean views. It's for buyers who want maximum privacy, dramatic scenery, and the feeling of living in a cloud forest 10 minutes from downtown.",
        "lifestyle": "Misty mornings above the clouds with city views below. Hiking the Tantalus-Round Top trail system. Dramatic light shows when clouds roll through. Very limited neighbors and zero commercialism. Steep, winding single-lane road is the trade-off.",
        "nearby": ["Pu'u Ualaka'a State Park", "Round Top Drive", "Makiki", "Downtown Honolulu"],
        "beaches": ["Ala Moana (15-20 min away)"],
        "commute": "20-30 min to downtown despite proximity — the winding single-lane road is the bottleneck. Not suitable for frequent commuters.",
        "market_notes": "Very low inventory, high prices for the right parcels. Fog and moisture make mold and building maintenance a real concern. Access road concerns (single lane, steep) affect insurability and resale pool. Cash buyers or buyers who understand the unique challenges. Views and privacy are the value drivers.",
        "keywords": ["mountain", "jungle", "views", "private", "cloud forest", "panoramic", "secluded"],
        "aliases": ["Tantalus Oahu", "Round Top", "Tantalus Crater", "Tantalus Drive"]
    },

    "Kakaako": {
        "island": "Oahu",
        "region": "Urban Honolulu",
        "vibe": "Kakaako is Honolulu's urban renaissance district — where industrial warehouses gave way to glass-tower condos, artisan food halls, and the city's most vibrant street art scene. It's where young professionals, tech workers, and urban lifestyle seekers land in Honolulu. Dense, walkable, and rapidly evolving.",
        "lifestyle": "Walk to work downtown or Ala Moana. Morning surf at Ala Moana Beach Park across the street. Weekend farmers markets and the Ward Village lifestyle. The energy here is highest in Honolulu — restaurants, galleries, coffee shops, and retail all within blocks.",
        "nearby": ["Ward Village", "Ala Moana Center", "Ala Moana Beach Park", "Downtown Honolulu", "Blaisdell Center"],
        "beaches": ["Ala Moana Beach Park"],
        "commute": "Walking distance to downtown. Rail station access. Best urban connectivity on Oahu.",
        "market_notes": "High-rise condo market dominated by Howard Hughes Corporation's Ward Village development. Mostly fee simple in newer towers. HOA fees are substantial — buyers must underwrite these carefully. Strong appreciation in new builds. Some older leasehold buildings in the district. Very active investor and second-home buyer pool. Vacation rental restrictions apply in residential towers.",
        "keywords": ["urban", "condos", "Ward Village", "walkable", "young professionals", "street art", "rail"],
        "aliases": ["Kaka'ako", "Kakaako Honolulu", "Ward Village", "Kakaako District", "Kakako"]
    },

    "Ala Moana": {
        "island": "Oahu",
        "region": "Urban Honolulu",
        "vibe": "Ala Moana is Honolulu's most central and walkable district — anchored by the world's largest open-air mall, fronted by a magnificent beach park, and filled with high-rise condos housing a cosmopolitan mix of locals, expats, and global buyers.",
        "lifestyle": "Walk across the street for surfing, swimming, and sunset picnics at the beach park. Walk the other direction to the country's largest open-air mall. No car needed for daily life. Dense urban living at its most convenient in Hawaii.",
        "nearby": ["Ala Moana Center", "Ala Moana Beach Park", "Kakaako", "Downtown Honolulu", "Magic Island"],
        "beaches": ["Ala Moana Beach Park", "Magic Island Lagoon"],
        "commute": "15 min to downtown. Rail access. Very walkable.",
        "market_notes": "High-rise condos at multiple price points. Mix of fee simple and leasehold — critical to check. HOA fees vary widely. Strong rental demand and vacation rental activity (where permitted). Global buyer pool including Japan-based investors. Stable long-term appreciation. Some older buildings with deferred maintenance.",
        "keywords": ["central", "walkable", "condo", "beach", "global buyers", "urban", "mall"],
        "aliases": ["Ala Moana Honolulu", "Ala Moana Beach", "Ala-Moana"]
    },

    "Waikiki": {
        "island": "Oahu",
        "region": "Urban Honolulu",
        "vibe": "Waikiki is Hawaii's most famous address — the global icon of Hawaii tourism. For residents (and there are many), it means living in the middle of a constant international festival, with legendary surf, world-class restaurants, and a sunset that never disappoints. Not for everyone, but for the right buyer, it's extraordinary.",
        "lifestyle": "Sunrise surf at Queens or Canoes. Coffee with views of Diamond Head. Evenings with live Hawaiian music at beachfront bars. It's vibrant, crowded, and always alive. Residents learn to flow with the tourist rhythm rather than against it.",
        "nearby": ["Waikiki Beach", "Diamond Head", "Kapiolani Park", "Honolulu Zoo", "International Market Place", "Duke Kahanamoku Statue"],
        "beaches": ["Waikiki Beach", "Fort DeRussy Beach", "Kuhio Beach"],
        "commute": "15-20 min to downtown Honolulu. Rail connection. But traffic in/out of Waikiki can be slow.",
        "market_notes": "Extremely active vacation rental market — many units are legal short-term rentals (check zoning). Heavy mix of fee simple and leasehold. HOA fees can be very high. Older building stock in much of Waikiki. Global investor and second-home buyer pool. Values fluctuate with tourism trends. Tsunami zone considerations for ground-floor and low-floor units.",
        "keywords": ["tourism", "vacation rental", "surf", "luxury", "global buyers", "Diamond Head", "iconic"],
        "aliases": ["Waikiki Beach", "Waikiki Honolulu", "Waikīkī", "Waikiki Oahu"]
    },

    "Downtown Honolulu": {
        "island": "Oahu",
        "region": "Urban Honolulu",
        "vibe": "Downtown Honolulu is the government, finance, and legal heart of Hawaii. Historic buildings share blocks with modern towers, and the waterfront Aloha Tower area is being revitalized. It's more work than play, but residential conversion is happening as Kakaako and rail investment make downtown living more attractive.",
        "lifestyle": "Walkable to government offices, courts, and finance. The Chinatown arts scene is blocks away. Lunch at the waterfront. Very urban, not a typical residential neighborhood but growing its residential base.",
        "nearby": ["Aloha Tower Marketplace", "Chinatown", "Hawaii State Capitol", "Punchbowl", "Kakaako"],
        "beaches": ["Ala Moana Beach (nearby)"],
        "commute": "This IS downtown — zero commute for downtown workers.",
        "market_notes": "Limited residential inventory. Mix of historic buildings and newer condos. Rail central station nearby drives future value. Some buildings still industrial-to-residential conversions. Buyer profile is urban professional or investor. Flood zone concerns near the waterfront.",
        "keywords": ["urban core", "government", "historic", "Chinatown", "waterfront", "rail", "revitalization"],
        "aliases": ["Downtown Honolulu", "Honolulu Downtown", "Downtown", "Chinatown adjacent"]
    },

    "Kapiolani": {
        "island": "Oahu",
        "region": "Central Honolulu",
        "vibe": "Kapiolani is a dense urban neighborhood anchored by the 300-acre Kapiolani Regional Park — Oahu's most beloved public greenspace. It sits between Waikiki and Diamond Head, attracting young professionals, athletes, and residents who want park life without tourist zone prices.",
        "lifestyle": "Morning jogs and weekend picnics in Kapiolani Park, summer concerts at the Waikiki Shell, and the Honolulu Zoo next door. Walk to Waikiki for dinner, retreat to the park for space. Very urban and walkable.",
        "nearby": ["Kapiolani Regional Park", "Waikiki Shell", "Honolulu Zoo", "Aquarium", "Waikiki", "Diamond Head"],
        "beaches": ["Kaimana Beach (Kapiolani end)", "Waikiki Beach"],
        "commute": "10-20 min to downtown Honolulu. Excellent transit and biking.",
        "market_notes": "Mix of condos and older apartment buildings. Some leasehold. Strong rental demand from young professionals and medical workers. Vacation rental restrictions in residential zones. Waikiki adjacency adds value without full Waikiki prices. Park-facing units command a premium.",
        "keywords": ["park", "urban", "walkable", "Waikiki adjacent", "young professionals", "athletes", "condos"],
        "aliases": ["Kapiolani Park area", "Kapiolani Honolulu", "Kapi'olani", "Kapiolani neighborhood"]
    },

    "Kaimuki": {
        "island": "Oahu",
        "region": "East Honolulu",
        "vibe": "Kaimuki is one of Honolulu's most beloved urban neighborhoods — a walkable grid of bungalows and historic homes anchored by Waialae Avenue's nationally recognized restaurant row. It's where chefs, creatives, and families who want real Honolulu neighborhood life choose to live.",
        "lifestyle": "Saturday morning at the Kaimuki Farmers Market, dinner at one of the dozen acclaimed Waialae Avenue restaurants, and a walk through quiet residential streets. It has the energy of a neighborhood that figured itself out — not trendy, just right.",
        "nearby": ["Waialae Avenue", "Kaimuki Community Park", "Diamond Head", "Kahala Mall", "Chaminade University"],
        "beaches": ["Kaimana Beach", "Kahala Beach (nearby)"],
        "commute": "10-20 min to downtown Honolulu.",
        "market_notes": "Strong demand, low inventory. Mix of older single-family bungalows and small condos. Fee simple dominant. Buyers compete for character homes that rarely come to market. Strong appreciation. Excellent school options. Favored by families and professionals who want urban living with neighborhood feel.",
        "keywords": ["restaurants", "walkable", "bungalows", "community", "food scene", "families", "character homes"],
        "aliases": ["Kaimuki Honolulu", "Kaimuki Oahu", "Waialae-Kaimuki", "Kai Muki"]
    },

    # ─────────────────────────────────────────────────────────────────
    # OAHU — LEEWARD / EWA
    # ─────────────────────────────────────────────────────────────────

    "Ewa Beach": {
        "island": "Oahu",
        "region": "Ewa Plain",
        "vibe": "Ewa Beach is where Honolulu families go when they want space, new construction, and a beach lifestyle at prices that don't require two tech salaries. It's one of the fastest-growing communities in Hawaii — master-planned subdivisions, young families, and a rapidly building commercial district.",
        "lifestyle": "Suburban family life — new parks, new schools, community pools, and a growing restaurant scene. Beach access at Oneula and White Plains. Morning walks through manicured planned community streets. A long commute is the accepted trade for the space and newness.",
        "nearby": ["Oneula Beach Park", "White Plains Beach", "First Wind Solar Farm", "Ewa Town Center", "Ka Makana Alii Mall"],
        "beaches": ["Oneula Beach Park", "White Plains Beach"],
        "commute": "H-1 to Honolulu — 35-60 min in light traffic, can exceed 75 min in rush hour. Among the longer commutes on Oahu. Rail extension is planned.",
        "market_notes": "New construction dominates. Fee simple with active HOAs. Some areas still developing. Builder warranties and newer construction standard. Rail to extend here eventually — future value catalyst. Good for first-time buyers priced out of central Honolulu. Strong appreciation in recent years driven by demand migration from more expensive areas.",
        "keywords": ["new construction", "suburban", "family", "affordable", "master-planned", "young families", "growth"],
        "aliases": ["Ewa Beach Oahu", "'Ewa Beach", "Ewa Plain", "Ewa"]
    },

    "Kapolei": {
        "island": "Oahu",
        "region": "Ewa Plain",
        "vibe": "Kapolei is Oahu's 'second city' — a planned urban center on the Leeward side with its own employment base, government services, and growing retail. It's less bedroom community than Ewa Beach, more a self-contained city for Leeward Oahu.",
        "lifestyle": "Car-based urban life on the sunny, dry side of the island. The University of Hawaii West Oahu campus creates a youthful energy. Ko Olina resort area is minutes away for weekend beach days.",
        "nearby": ["Ko Olina", "UH West Oahu", "Ka Makana Alii Mall", "Kapolei Regional Park", "Wet 'N' Wild Hawaii"],
        "beaches": ["Ko Olina Lagoons (nearby)", "White Plains Beach"],
        "commute": "H-1 to Honolulu — 35-60+ min depending on traffic. Dry, sunny side of island means consistent weather but long freeway commute.",
        "market_notes": "Growing job base reducing pure bedroom-community status. Mix of older and newer housing. Rail terminus location adds future value. More established than Ewa Beach. Affordable relative to town. Strong rental demand from UH students and Leeward workers.",
        "keywords": ["second city", "leeward", "sunny", "affordable", "university", "rail terminus", "growing"],
        "aliases": ["Kapolei Oahu", "Kapolei City", "Ko Olina adjacent"]
    },

    "Ko Olina": {
        "island": "Oahu",
        "region": "Leeward",
        "vibe": "Ko Olina is a luxury resort enclave on Oahu's driest, sunniest coast — home to Disney's Aulani, Four Seasons, and Marriott resorts wrapped around four man-made lagoons. Residential here means living in a resort setting permanently.",
        "lifestyle": "Lagoon swimming, golf at Ko Olina Golf Club, sunset dinners at resort restaurants, and a lifestyle that feels permanently on vacation. Very quiet, very manicured, and entirely insulated from the rest of Oahu.",
        "nearby": ["Aulani Disney Resort", "Four Seasons Ko Olina", "Ko Olina Golf Club", "Ko Olina Marina", "Kapolei"],
        "beaches": ["Ko Olina Lagoon 1-4 (man-made)", "Tracks Beach (nearby surf)"],
        "commute": "40-60+ min to Honolulu on H-1. This is resort living — buyers typically work remotely or are retired/second-home.",
        "market_notes": "HOA fees are among the highest on Oahu due to resort amenities. Vacation rental rules vary by complex — some allow STR, others don't. Strong appreciation in resort-adjacent units. International and mainland second-home buyer pool. Fee simple dominant in newer developments. Some leasehold in older sections.",
        "keywords": ["resort", "luxury", "lagoon", "Disney", "vacation rental", "golf", "sunny"],
        "aliases": ["Ko'Olina", "KoOlina", "Ko Olina Resort", "Kohina", "Ko-Olina"]
    },

    "Waipahu": {
        "island": "Oahu",
        "region": "Central Oahu",
        "vibe": "Waipahu is a historically working-class plantation town that has transitioned into one of Oahu's most diverse multicultural communities. It's affordable, authentic, and well-positioned on the rail corridor.",
        "lifestyle": "Dense multicultural neighborhood life — Filipino, Samoan, and Pacific Islander communities predominate. Local food scene is excellent and authentic. Pearl Harbor and Aloha Stadium are nearby.",
        "nearby": ["Waipahu Cultural Garden Park", "Pearl Harbor", "Aloha Stadium site", "Rail Station (planned)"],
        "beaches": ["Pearl Harbor waterfront (no swim beach)"],
        "commute": "H-1 to Honolulu — 20-35 min. Rail station access planned.",
        "market_notes": "Affordable entry point on Oahu. Older housing stock. Investment opportunity as rail corridor appreciates. Mix of fee simple and leasehold. Strong rental demand. Buyers often first-time or investors.",
        "keywords": ["affordable", "multicultural", "plantation history", "rail corridor", "diverse"],
        "aliases": ["Waipahu Oahu", "Waipahu Town", "Wai Pahu"]
    },

    "Pearl City": {
        "island": "Oahu",
        "region": "Central Oahu",
        "vibe": "Pearl City is a solid, established suburban community on Pearl Harbor's shore — practical, family-oriented, and well-connected. Not flashy, but consistently reliable with good schools, shopping, and transit access.",
        "lifestyle": "Suburban family life with Costco, Target, and Pearlridge Mall meeting all shopping needs. Aiea Bowl and neighborhood parks for recreation. Working families who want central island location without Honolulu prices.",
        "nearby": ["Pearlridge Center", "Pearl Harbor", "Aiea", "Stadium area", "H-1 freeway"],
        "beaches": ["No direct beach access", "Ewa Beach (20 min)"],
        "commute": "H-1 to Honolulu — 15-25 min. Very good freeway access.",
        "market_notes": "Solid value, consistent appreciation. Fee simple dominant. Active HOAs in newer developments. Good school district. Strong family and military rental demand. Some leasehold in older sections. Pearlridge area has some commercial-adjacent residential.",
        "keywords": ["suburban", "family", "central", "practical", "schools", "Pearl Harbor"],
        "aliases": ["Pearl City Oahu", "Pearl Harbor area", "Pearlcity"]
    },

    "Aiea": {
        "island": "Oahu",
        "region": "Central Oahu",
        "vibe": "Aiea is a central Oahu community straddling Pearl Harbor and the H-1 corridor — practical, affordable, and well-positioned for island-wide commuting. It lacks the cachet of Honolulu neighborhoods but delivers solid value.",
        "lifestyle": "Workhorse suburb. Pearlridge Mall shopping, Keaiwa Heiau State Recreation Area hiking, and quick freeway access anywhere. Family-oriented, quiet residential.",
        "nearby": ["Keaiwa Heiau State Recreation Area", "Pearlridge Center", "Pearl City", "Stadium area", "H-1/H-2 interchange"],
        "beaches": ["No direct beach access"],
        "commute": "H-1 to Honolulu — 15-20 min. Excellent central island position.",
        "market_notes": "Affordable relative to Honolulu. Mix of older homes and some newer subdivisions. Fee simple and leasehold both present. Stable appreciation. Good for buyers prioritizing square footage and value over prestige.",
        "keywords": ["affordable", "central", "practical", "Pearl Harbor adjacent", "hiking access"],
        "aliases": ["Aiea Oahu", "'Aiea", "Aiea Heights"]
    },

    "Salt Lake": {
        "island": "Oahu",
        "region": "Central Oahu",
        "vibe": "Salt Lake is a dense urban residential area adjacent to Honolulu's airport corridor — compact, diverse, and very well-connected. A genuine local neighborhood with mostly mid-rise and single-family housing catering to working families.",
        "lifestyle": "Urban density with good TheBus access. Moanalua Gardens is a landmark park. Airport proximity means noise is a factor for some units. Korean and Filipino community hubs nearby.",
        "nearby": ["Moanalua Gardens", "Salt Lake District Park", "Honolulu International Airport", "H-1 freeway", "Tripler Medical Center"],
        "beaches": ["Ala Moana Beach (15 min)"],
        "commute": "10-15 min to downtown Honolulu. Airport-corridor location excellent for frequent travelers.",
        "market_notes": "Affordable condos and homes. Airport noise is a consideration and disclosed. Mix of fee simple and leasehold. Strong rental demand from airport workers, military, and medical staff at Tripler. Stable if unspectacular appreciation. Good investment market.",
        "keywords": ["urban", "affordable", "diverse", "airport adjacent", "transit", "condo"],
        "aliases": ["Salt Lake Honolulu", "Salt Lake Oahu", "Moanalua area"]
    },

    "Moanalua": {
        "island": "Oahu",
        "region": "Central Oahu",
        "vibe": "Moanalua is a quiet neighborhood tucked between Salt Lake and Tripler — calmer and more residential than its neighbors, with the famous Moanalua Gardens as its landmark. Mostly single-family with a stable, established community.",
        "lifestyle": "Quiet suburban living with excellent freeway access. Moanalua Gardens is beloved for its Japanese garden and banyan trees. Close to Tripler creates medical community presence.",
        "nearby": ["Moanalua Gardens", "Tripler Army Medical Center", "Salt Lake", "H-1/H-3 junction"],
        "beaches": ["No direct beach access"],
        "commute": "10-15 min to downtown Honolulu.",
        "market_notes": "Stable, understated market. Some military and medical buyer profile. Fee simple dominant in single-family. Solid schools. Not a high-growth area but consistent value.",
        "keywords": ["quiet", "residential", "Moanalua Gardens", "military adjacent", "stable"],
        "aliases": ["Moanalua Valley", "Moanalua Honolulu"]
    },

    # ─────────────────────────────────────────────────────────────────
    # OAHU — NORTH SHORE
    # ─────────────────────────────────────────────────────────────────

    "Mililani": {
        "island": "Oahu",
        "region": "Central Oahu",
        "vibe": "Mililani is central Oahu's premier master-planned community — clean, orderly, family-centered, and consistently ranked among the best places to live in Hawaii. It was built from scratch in the 1960s-80s and still has the infrastructure and community feel of a thoughtfully designed suburb.",
        "lifestyle": "Community recreation centers, swim meets, youth sports, and neighborhood block parties. Mililani Town Center for daily needs. Good schools are the defining draw. Quiet, safe, and community-oriented.",
        "nearby": ["Mililani Town Center", "Mililani Golf Club", "Wahiawa", "Schofield Barracks", "Mililani Mauka"],
        "beaches": ["No direct beach access — central island location"],
        "commute": "H-2 to H-1 to Honolulu — 25-40 min. Good freeway access but traffic on H-1 is the variable.",
        "market_notes": "Active HOA with dues and community rules. Fee simple dominant. Strong school district drives family demand. One of the most liquid markets on Oahu outside metro Honolulu. Consistent appreciation. Mililani Mauka (newer section) commands slight premium over Mililani Town.",
        "keywords": ["master-planned", "family", "schools", "community", "HOA", "central Oahu", "safe"],
        "aliases": ["Mililani Oahu", "Mililani Town", "Mililani Mauka"]
    },

    "Wahiawa": {
        "island": "Oahu",
        "region": "Central Oahu",
        "vibe": "Wahiawa is a working-class central plateau town surrounded by pineapple fields and military installations. It's unpretentious, affordable, and deeply local — not a destination but a genuine community with its own character.",
        "lifestyle": "Schofield Barracks and Wheeler Army Airfield create a strong military community presence. Downtown Wahiawa has local diners and shops. Kole Kole Pass and Wahiawa Botanical Garden for outdoor time.",
        "nearby": ["Schofield Barracks", "Wheeler Army Airfield", "Wahiawa Botanical Garden", "Lake Wilson", "Dole Plantation"],
        "beaches": ["No direct beach access — North Shore is 15 min"],
        "commute": "H-2 to H-1 to Honolulu — 30-45 min.",
        "market_notes": "Most affordable markets on Oahu. Strong military rental demand from Schofield. Older housing stock. Investment properties prevalent. Fee simple and leasehold both present. Limited appreciation potential versus metro areas but solid rental yields.",
        "keywords": ["affordable", "military", "central", "pineapple", "working-class", "investment"],
        "aliases": ["Wahiawa Oahu", "Wahiawa Town", "Wahiawa Heights"]
    },

    "Haleiwa": {
        "island": "Oahu",
        "region": "North Shore",
        "vibe": "Haleiwa is the soul of Oahu's North Shore — a historic surf town with wooden storefronts, art galleries, shave ice shops, and a laid-back energy that feels untouched by time. Surfers, artists, and those fleeing urban life build their lives here.",
        "lifestyle": "Mornings checking the surf at Ali'i Beach, afternoons at Matsumoto's Shave Ice, evenings at a farm-to-table dinner. The pace is deliberately slow and the culture deeply surf-rooted. November through February brings world-class surfing action to the neighborhood.",
        "nearby": ["Haleiwa Ali'i Beach Park", "Matsumoto Shave Ice", "Waimea Bay", "Sunset Beach", "North Shore Marketplace"],
        "beaches": ["Haleiwa Beach Park", "Ali'i Beach Park"],
        "commute": "H-2 to H-1 to Honolulu — 45-65 min. Many North Shore residents work locally or remotely to avoid this commute.",
        "market_notes": "Desirable but limited inventory. Mix of older single-family homes, some newer builds, and agricultural parcels. Vacation rental market active where permitted. Buyers are typically remote workers, surf industry professionals, and second-home seekers. Flood zone risk near Anahulu River. Agricultural zoning on some parcels limits development.",
        "keywords": ["surf town", "historic", "shave ice", "artists", "laid-back", "remote workers", "North Shore"],
        "aliases": ["Hale'iwa", "Haleiwa Town", "Haleiwa North Shore", "Haleiwa Oahu"]
    },

    "Sunset Beach": {
        "island": "Oahu",
        "region": "North Shore",
        "vibe": "Sunset Beach is the quietest, most residential stretch of the North Shore — home to the famous Sunset Beach surf break but otherwise a small rural community of surfers, families, and people who chose the end of the road over the city.",
        "lifestyle": "Watching winter swells from your yard, fishing at Shark's Cove, and stargazing on truly dark nights. Grocery runs require driving to Haleiwa or Kahuku. The lifestyle trade is extreme peace for extreme remoteness.",
        "nearby": ["Sunset Beach Park", "Banzai Pipeline (Ehukai Beach)", "Shark's Cove", "Pupukea", "Haleiwa"],
        "beaches": ["Sunset Beach", "Banzai Pipeline (Ehukai)", "Shark's Cove"],
        "commute": "50-70 min to Honolulu. North Shore residents typically work locally or remotely.",
        "market_notes": "Tight inventory. Mix of older beachfront cottages and newer homes. Beachfront properties among the most desirable (and expensive) on Oahu despite remoteness. Vacation rental market where permitted. Flood zone near beach. Buyers typically surfers, remote workers, second-home seekers.",
        "keywords": ["surf", "remote", "beachfront", "peaceful", "rural", "Pipeline", "world-class waves"],
        "aliases": ["Sunset Beach Oahu", "Sunset Beach North Shore", "Sunset"]
    },

    "Pupukea": {
        "island": "Oahu",
        "region": "North Shore",
        "vibe": "Pupukea sits on the hillside above Sunset Beach — slightly elevated, cooler than the beach, and home to a mix of longtime residents, surfers, and people who found paradise here and never left. Shark's Cove snorkeling is world-famous.",
        "lifestyle": "Hiking Pupukea trails, snorkeling at Shark's Cove, watching surfers from the bluff. More rural and uphill than beachside North Shore.",
        "nearby": ["Shark's Cove", "Three Tables", "Pupukea Beach Park", "BYU-Hawaii (nearby in Laie)", "Waimea Bay"],
        "beaches": ["Shark's Cove", "Three Tables", "Sunset Beach (nearby)"],
        "commute": "50-70 min to Honolulu.",
        "market_notes": "Similar to Sunset Beach but with more elevation. Some larger lots. Vacation rental demand. Views can be spectacular from upper elevations. Older housing stock mixed with newer custom builds.",
        "keywords": ["surf", "snorkeling", "elevated", "rural", "North Shore", "Shark's Cove"],
        "aliases": ["Pupukea North Shore", "Pūpūkea", "Pupukea Hills"]
    },

    "Waimea Valley": {
        "island": "Oahu",
        "region": "North Shore",
        "vibe": "The residential areas around Waimea Bay are among the most coveted on the North Shore — historic, beautiful, and home to one of Hawaii's most famous surf venues. Waimea Valley itself is a botanical garden and cultural site.",
        "lifestyle": "Living with Waimea Bay visible from your property — watching 30-foot winter swells from shore, cliff jumping in summer. Very local, very surf-cultural.",
        "nearby": ["Waimea Bay Beach Park", "Waimea Valley", "Haleiwa", "Sunset Beach"],
        "beaches": ["Waimea Bay"],
        "commute": "45-65 min to Honolulu.",
        "market_notes": "Extremely coveted, very limited inventory. Properties near Waimea Bay are generational assets. Buyers compete fiercely. Vacation rental restrictions in some areas. Beachfront and bay-view properties carry dramatic premiums.",
        "keywords": ["Waimea Bay", "surf", "historic", "coveted", "limited inventory", "North Shore"],
        "aliases": ["Waimea", "Waimea Bay area", "Waimea Oahu", "Waimea North Shore"]
    },

    "Laie": {
        "island": "Oahu",
        "region": "North Shore",
        "vibe": "Laie is a predominantly Latter-day Saint community on Oahu's far North Shore — home to BYU-Hawaii and the Polynesian Cultural Center. It's clean, family-oriented, tight-knit, and quite different in character from the surf culture elsewhere on the North Shore.",
        "lifestyle": "BYU-Hawaii campus life, Polynesian Cultural Center performances, and a community built around faith and family. Laie Beach is beautiful and uncrowded. Grocery access requires driving to Kaneohe or Kahuku.",
        "nearby": ["BYU-Hawaii", "Polynesian Cultural Center", "Laie Hawaii Temple", "Laie Beach", "Kahuku"],
        "beaches": ["Laie Beach Park", "Hukilau Beach"],
        "commute": "60-80 min to Honolulu — one of the longer Oahu commutes.",
        "market_notes": "Unique community with values-aligned buyer profile. Demand from BYU faculty and staff creates stable rental market. Limited inventory, slow turnover. Fee simple dominant. Affordable relative to Kailua and North Shore surf towns.",
        "keywords": ["LDS", "BYU-Hawaii", "family", "community", "faith-based", "Polynesian", "affordable"],
        "aliases": ["La'ie", "Laie Oahu", "Laie Town", "BYU Hawaii area"]
    },

    "Hauula": {
        "island": "Oahu",
        "region": "Windward North",
        "vibe": "Hauula is a small, rural windward community between Laie and Kaneohe — authentic local Hawaii with limited amenities but beautiful beaches and a deep sense of place.",
        "lifestyle": "Small beach town living. Hauula Loop Trail and Ma'akua Ridge Trail. Quiet, local, and unhurried.",
        "nearby": ["Hauula Beach Park", "Ma'akua Ridge Trail", "Punaluu", "Laie", "Kahuku"],
        "beaches": ["Hauula Beach Park", "Punaluu Beach Park"],
        "commute": "50-70 min to Honolulu.",
        "market_notes": "Affordable rural windward option. Older housing stock. Some Hawaiian Home Lands in the area. Low inventory, slow turnover. Buyers are typically locals or remote workers seeking rural lifestyle.",
        "keywords": ["rural", "local", "affordable", "windward", "hiking", "beach"],
        "aliases": ["Ha'ula", "Hauula Oahu", "Hauula Beach"]
    },

    "Kahuku": {
        "island": "Oahu",
        "region": "North Shore",
        "vibe": "Kahuku is the end of the road on Oahu's northeastern tip — a former sugar plantation town now known for shrimp trucks, a growing aquaculture industry, and some of the most peaceful and undeveloped land on the island.",
        "lifestyle": "Shrimp trucks, long empty beaches, and rural agricultural land. Romer Shrimp Farm, James Campbell Wildlife Refuge, and Turtle Bay are the landmarks. Very remote, very quiet.",
        "nearby": ["Turtle Bay Resort", "James Campbell National Wildlife Refuge", "Kahuku Shrimp Trucks", "Laie"],
        "beaches": ["Kahuku Beach", "Turtle Bay Beach"],
        "commute": "65-80 min to Honolulu — most remote community on Oahu.",
        "market_notes": "Very affordable, very limited amenities. Agricultural land is available. Turtle Bay Resort drives some vacation rental and luxury residential. Remote workers discovering the area. Flood zone and coastal erosion risk on some beachfront parcels.",
        "keywords": ["remote", "rural", "agricultural", "shrimp", "Turtle Bay", "end of the road"],
        "aliases": ["Kahuku Oahu", "Kahuku Town", "Turtle Bay area"]
    },

    # ─────────────────────────────────────────────────────────────────
    # MAUI
    # ─────────────────────────────────────────────────────────────────

    "Lahaina": {
        "island": "Maui",
        "region": "West Maui",
        "vibe": "Lahaina is Maui's historic heart — a former whaling port and Hawaiian royal capital that became the island's most vibrant town. The August 2023 wildfire devastated much of historic Lahaina, and the community is in active recovery and rebuilding. It remains deeply significant to Maui's identity.",
        "lifestyle": "Pre-fire: Front Street with galleries, restaurants, and the famous banyan tree. Post-fire: community-led rebuilding with fierce debate about who Lahaina will be rebuilt for. Buyers engaging here now are participating in a historic recovery.",
        "nearby": ["Kaanapali Beach (north)", "Lahaina Harbor", "West Maui Mountains", "Olowalu"],
        "beaches": ["Puamana Beach", "Lahaina Beach", "Kaanapali (nearby)"],
        "commute": "30-45 min to Kahului on Honoapiilani Highway. Road congestion and single-point-of-failure routing is a known issue.",
        "market_notes": "Unique post-fire market — significant rebuilding happening. Insurance, permitting, and community planning dominate conversations. Some parcels cleared and for sale. Strong long-term recovery value expected but near-term uncertainty is high. Buyers must understand they're entering a recovery market.",
        "keywords": ["historic", "recovery", "wildfire", "Front Street", "whaling port", "rebuilding", "community"],
        "aliases": ["Lahaina Town", "Lahaina Maui", "Front Street Lahaina", "Lāhainā"]
    },

    "Kaanapali": {
        "island": "Maui",
        "region": "West Maui",
        "vibe": "Kaanapali is Maui's original resort destination — a 3-mile crescent of gold sand beach lined with major resort hotels, condos, and the Whalers Village mall. It's pure luxury Hawaii beach lifestyle for buyers and investors.",
        "lifestyle": "Resort-everything: morning snorkeling at Black Rock, day at the pool, sunset cocktails on the beach. The Kaanapali Beach Walk connects it all. World-class in its category.",
        "nearby": ["Whalers Village", "Hyatt Regency Maui", "Marriott Maui Ocean Club", "Black Rock (Pu'u Keka'a)", "Kaanapali Golf Courses"],
        "beaches": ["Kaanapali Beach", "Pu'u Keka'a (Black Rock)"],
        "commute": "30 min to Kahului. Resort workers often commute from more affordable areas.",
        "market_notes": "Heavy vacation rental market — most units have legal STR permits. HOA fees are substantial. Mix of fee simple and leasehold — check carefully. Strong appreciation tied to tourism health. International and mainland second-home buyer pool. Condo market dominates.",
        "keywords": ["resort", "vacation rental", "luxury", "beach", "condos", "Black Rock", "tourism"],
        "aliases": ["Ka'anapali", "Kaanapali Beach", "K-anapali", "Kaanapali Resort", "Kanapali"]
    },

    "Kapalua": {
        "island": "Maui",
        "region": "West Maui",
        "vibe": "Kapalua is the quieter, more exclusive alternative to Kaanapali — a secluded resort at Maui's northwest tip with two world-class golf courses, the Ritz-Carlton, and a more intimate feel. It attracts buyers seeking privacy and prestige over party and pool bars.",
        "lifestyle": "Ritz-Carlton mornings, Kapalua Bay swims, world-class golf, and whale watching from elevated ocean-view properties. The PGA Tour's Sentry Tournament of Champions is held here. Intimate and refined.",
        "nearby": ["Ritz-Carlton Kapalua", "Kapalua Golf (Plantation/Bay Courses)", "Kapalua Bay Beach", "D.T. Fleming Beach", "Napili Bay"],
        "beaches": ["Kapalua Bay Beach", "D.T. Fleming Beach"],
        "commute": "35-45 min to Kahului. Many buyers are retired or remote.",
        "market_notes": "Top tier pricing on Maui. Residential within the resort boundary subject to resort fees and HOA. Very limited inventory. Ritz-Carlton residences and standalone luxury homes. Strong second-home and investor demand. Cash buyers predominate. STR-friendly in resort zones.",
        "keywords": ["luxury", "Ritz-Carlton", "golf", "private", "resort", "whales", "exclusive"],
        "aliases": ["Kapalua Maui", "Kapalua Resort", "Kapalua Bay"]
    },

    "Napili": {
        "island": "Maui",
        "region": "West Maui",
        "vibe": "Napili is the affordable alternative on the West Maui coast — beautiful Napili Bay, older condo complexes, and a friendly community of repeat visitors who have become part-time residents. Less manicured than Kapalua, more authentic feel.",
        "lifestyle": "Simple beach life — snorkeling at Napili Bay, sunsets, and local restaurants. The Bay Club and other condos are full of people who discovered Napili decades ago and never stopped coming back.",
        "nearby": ["Napili Bay", "Kapalua", "Kahana", "Napili Market", "Honokohau Bay"],
        "beaches": ["Napili Bay", "Kapalua Bay (adjacent)"],
        "commute": "35-45 min to Kahului.",
        "market_notes": "Older condo stock with strong rental history. STR permits grandfathered in many buildings. Good value entry point for West Maui. Some buildings restricting STR due to county rules. Leasehold prevalent in older buildings — critical to check. Strong repeat-visitor rental demand.",
        "keywords": ["bay", "affordable", "condo", "snorkeling", "vacation rental", "authentic", "repeat visitors"],
        "aliases": ["Napili Bay", "Napili Maui", "Napili-Honokowai", "Napili Kai"]
    },

    "Kahului": {
        "island": "Maui",
        "region": "Central Maui",
        "vibe": "Kahului is Maui's commercial and transportation hub — airport, harbor, Costco, and big-box retail all land here. It's practical, affordable, and essential but nobody comes to Maui for Kahului. Residents here prioritize value and centrality over lifestyle cachet.",
        "lifestyle": "Costco runs, flights in and out, and easy access to all parts of the island. Kanaha Beach Park is an unexpected gem for windsurfers. The real lifestyle is access — to everything else.",
        "nearby": ["Kahului Airport (OGG)", "Kahului Harbor", "Kanaha Beach Park", "Maui Arts & Cultural Center", "Queen Kaahumanu Center"],
        "beaches": ["Kanaha Beach Park"],
        "commute": "Central Maui — 15-20 min to almost anywhere on island.",
        "market_notes": "Most affordable Maui market. Older housing stock and commercial-adjacent residential. Flood zone risk in low-lying harbor areas. Good investment rental market due to airport proximity. First-time buyer and local worker profile.",
        "keywords": ["hub", "affordable", "central", "airport", "practical", "local workers", "windsurfing"],
        "aliases": ["Kahului Maui", "Kahului Town", "Maui Airport area"]
    },

    "Wailuku": {
        "island": "Maui",
        "region": "Central Maui",
        "vibe": "Wailuku is Maui's county seat — a historic valley town with genuine character, an emerging arts and foodie scene in its Market Street district, and the feel of old Hawaii that most of the island has lost. Locals love it; tourists mostly skip it.",
        "lifestyle": "Morning coffee at a local cafe on Market Street, hiking the Waihe'e Ridge Trail, weekend Swap Meet at the War Memorial. An authentic working town that has a growing creative community without the resort overlay.",
        "nearby": ["Iao Valley State Monument", "Kepaniwai Park", "Wailuku Market Street", "Maui Tropical Plantation", "Kahului"],
        "beaches": ["Kanaha Beach (nearby in Kahului)"],
        "commute": "15-20 min to most of Maui.",
        "market_notes": "Most affordable residential market in Maui with genuine community character. Older housing stock, Plantation-era homes. Fee simple dominant. Strong local and workforce buyer demand. Investors find good yields. Iao Valley flood risk in lower sections.",
        "keywords": ["historic", "local", "affordable", "county seat", "Market Street", "authentic", "Iao Valley"],
        "aliases": ["Wailuku Maui", "Wailuku Town", "Wailuku Valley"]
    },

    "Kihei": {
        "island": "Maui",
        "region": "South Maui",
        "vibe": "Kihei is South Maui's affordable beach town — miles of decent beaches, dry sunny weather year-round, and a no-frills surf and beach lifestyle. It's where locals and budget-conscious buyers access South Maui's best weather without Wailea prices.",
        "lifestyle": "Morning yoga at Kalama Park, surfing at Cove Park, and sunset dinners at one of a dozen solid beach restaurants. Less polished than Wailea but more alive with a genuine community.",
        "nearby": ["Kalama Park", "Cove Park", "Kamaole Beach Parks I/II/III", "Kihei Town Center", "Wailea"],
        "beaches": ["Kamaole Beach Parks I-III", "Cove Park Beach", "Charley Young Beach"],
        "commute": "25-35 min to Kahului.",
        "market_notes": "Broad price range from affordable condos to beachfront homes. Mix of STR-permitted and residential. Leasehold present in some older complexes. Strong vacation rental demand. North Kihei more affordable, South Kihei (near Wailea) more expensive. Good first-time buyer market at north end. Active, competitive market.",
        "keywords": ["beach town", "affordable", "sunny", "surf", "condos", "vacation rental", "South Maui"],
        "aliases": ["Kihei Maui", "South Kihei", "North Kihei", "Kihei Town"]
    },

    "Wailea": {
        "island": "Maui",
        "region": "South Maui",
        "vibe": "Wailea is Maui's luxury resort corridor — a master-planned community of five-star resorts, championship golf courses, and some of the most exclusive residential real estate in the state. Wailea's beaches are consistently rated among the best in the world.",
        "lifestyle": "Four Seasons and Grand Wailea pool days, morning snorkeling at Wailea Beach, evening dinners at Spago. Residents live the resort life 365 days a year. Golf at three world-class courses. Whale watching is exceptional November through April.",
        "nearby": ["Four Seasons Maui", "Grand Wailea", "Wailea Beach Walk", "Shops at Wailea", "Wailea Golf Club"],
        "beaches": ["Wailea Beach", "Ulua Beach", "Mokapu Beach", "Polo Beach"],
        "commute": "30-40 min to Kahului. Most residents are retired or remote.",
        "market_notes": "Top of the Maui market — luxury condos, penthouses, and custom estates. Mostly fee simple in newer developments. Very strong STR market within resort designations. HOA fees are high. International and mainland second-home buyer pool. Limited inventory, high demand, strong appreciation. Cash transactions common. Leasehold possible in older sections.",
        "keywords": ["luxury", "resort", "world-class beaches", "golf", "whales", "Four Seasons", "exclusive"],
        "aliases": ["Wailea Maui", "Wailea Resort", "Wailea-Makena", "Wailea Beach"]
    },

    "Makena": {
        "island": "Maui",
        "region": "South Maui",
        "vibe": "Makena is where Maui runs out of road — raw lava fields, ancient Hawaiian fishponds, and the famous Big Beach (Oneloa). Beyond the Makena Resort sits La Perouse Bay and the end of the highway. Very exclusive, very limited residential.",
        "lifestyle": "Ultimate seclusion. Big Beach on weekdays feels like the end of the world (in a beautiful way). Some luxury estates and the Makena Golf & Beach Club. Far from everything.",
        "nearby": ["Oneloa Beach (Big Beach)", "Little Beach (Pu'u Olai)", "Ahihi-Kinau Natural Area Reserve", "La Perouse Bay", "Makena Golf & Beach Club"],
        "beaches": ["Oneloa Beach (Big Beach)", "Little Beach"],
        "commute": "35-45 min to Kahului. Very remote.",
        "market_notes": "Extremely limited inventory. Luxury estates and large parcels. Lava zone considerations. Fee simple. Very strong appreciation for what's available. Buyers are typically ultra-high-net-worth with remote lifestyle preference.",
        "keywords": ["secluded", "luxury", "Big Beach", "end of the road", "lava fields", "raw Hawaii"],
        "aliases": ["Makena Maui", "Big Beach area", "Makena-Wailea", "La Perouse area"]
    },

    "Haiku": {
        "island": "Maui",
        "region": "Upcountry / North Shore Maui",
        "vibe": "Haiku is the gateway to Maui's lush North Shore and Upcountry — a verdant, artistic community of growers, surfers, wellness practitioners, and people who came for a year and stayed for life. It's counter-culture, community-minded, and spectacularly beautiful.",
        "lifestyle": "Morning fog burning off over jungle hills. Coffee from your own trees. Weekly gatherings at the Haiku Marketplace. Road to Hana starts here. Hookipa windsurfing and kiteboarding nearby.",
        "nearby": ["Hookipa Beach", "Haiku Marketplace", "Twin Falls", "Paia Town", "Road to Hana start"],
        "beaches": ["Hookipa Beach", "Paia Bay (nearby)"],
        "commute": "25-35 min to Kahului.",
        "market_notes": "Rural agricultural zoning on many parcels. Mix of farms, homes on ag land, and standard residential. Water catchment systems common — buyers must understand off-grid infrastructure. Fee simple dominant. Strong demand from mainland lifestyle buyers. Vacation rentals regulated in agricultural zones. Older permits and accessory dwellings require due diligence.",
        "keywords": ["rural", "artistic", "jungle", "lush", "agriculture", "Road to Hana", "community"],
        "aliases": ["Ha'iku", "Haiku Maui", "Haiku-Pauwela", "Haiku Town"]
    },

    "Paia": {
        "island": "Maui",
        "region": "North Shore Maui",
        "vibe": "Paia is Maui's hippest small town — a one-street wonder with boutiques, health food restaurants, surf shops, and an energy that attracts a global creative class while retaining its roots as a former plantation town.",
        "lifestyle": "Acai bowls at Paia Bay Coffee, shopping on Baldwin Avenue, surfing at Hookipa or Paia Bay. Yoga studios outnumber convenience stores. The mix of visiting digital nomads and longtime locals creates a buzzy, unique energy.",
        "nearby": ["Hookipa Beach Park", "Paia Bay", "Haiku", "Kahului", "Baldwin Beach"],
        "beaches": ["Paia Bay", "Baldwin Beach Park", "Hookipa Beach"],
        "commute": "20-25 min to Kahului.",
        "market_notes": "Small housing inventory in town — mostly older single-family and a few condos. Strong STR demand but regulation is tightening. Fee simple dominant. Premium prices for the town character and North Shore access. Buyers are creative class, wellness industry, surf industry.",
        "keywords": ["hip", "surf", "boutique", "creative", "community", "North Shore", "digital nomads"],
        "aliases": ["Pa'ia", "Paia Town", "Paia Maui", "Paia Bay area"]
    },

    "Makawao": {
        "island": "Maui",
        "region": "Upcountry Maui",
        "vibe": "Makawao is Maui's paniolo (cowboy) town — a charming Upcountry community with wooden storefronts, rodeo culture, art galleries, and a distinctive character that feels nothing like beach Maui. Cool temperatures, green pastures, and a creative local community.",
        "lifestyle": "Horseback riding at sunrise, coffee and pastries at Komoda Store, hiking the Makawao Forest Reserve. The 4th of July rodeo is a beloved local tradition. Upcountry life is slower, cooler, and genuinely community-rooted.",
        "nearby": ["Makawao Forest Reserve", "Komoda Store & Bakery", "Hui No'eau Visual Arts Center", "Pukalani", "Paia"],
        "beaches": ["Hookipa (15 min away)"],
        "commute": "25-35 min to Kahului.",
        "market_notes": "Desirable Upcountry community with limited inventory. Mix of residential and agricultural parcels. Fee simple dominant. Some agricultural land subject to restrictions. Cooler climate a selling point for mainland buyers. Vacation rental restrictions tighter in residential zones. Strong demand, low supply.",
        "keywords": ["upcountry", "paniolo", "cowboy", "art", "cool", "horses", "community"],
        "aliases": ["Makawao Maui", "Makawao Town", "Upcountry Makawao"]
    },

    "Pukalani": {
        "island": "Maui",
        "region": "Upcountry Maui",
        "vibe": "Pukalani is the practical commercial hub of Upcountry Maui — the Safeway, gas station, and services that the surrounding Upcountry towns depend on. Residential here offers Upcountry access without full rural isolation.",
        "lifestyle": "More suburban than Makawao or Kula. Shopping center access, golf at Pukalani Country Club, and easy access to the rest of Upcountry.",
        "nearby": ["Pukalani Terrace Center", "Pukalani Country Club", "Makawao", "Kula", "Kahului"],
        "beaches": ["30 min to coast"],
        "commute": "25-30 min to Kahului.",
        "market_notes": "More affordable than Makawao or Kula. Standard residential subdivisions. Good value for Upcountry access. HOAs in some subdivisions. Fee simple dominant.",
        "keywords": ["upcountry", "practical", "golf", "affordable", "hub", "residential"],
        "aliases": ["Pukalani Maui", "Pukalani Upcountry"]
    },

    "Kula": {
        "island": "Maui",
        "region": "Upcountry Maui",
        "vibe": "Kula is the most desirable Upcountry community — rolling protea farms, Maui onion fields, and sweeping views of the ocean and West Maui Mountains from 2,000-3,000 feet elevation. It's where Maui's most sought-after Upcountry estates are found.",
        "lifestyle": "Cool mornings in your garden, fresh Maui onions and strawberries from neighboring farms, and panoramic sunset views over the Central Valley. Haleakala summit is 30 minutes up. A gentleman-farmer lifestyle that is genuinely attainable.",
        "nearby": ["Kula Botanical Garden", "Ali'i Kula Lavender Farm", "Haleakala National Park entrance", "Surfing Goat Dairy", "Makawao"],
        "beaches": ["30-40 min to South or North Maui beaches"],
        "commute": "25-35 min to Kahului.",
        "market_notes": "Most desirable Upcountry market with strong demand and limited inventory. Mix of residential and agricultural parcels. Views and elevation are primary value drivers. Fee simple dominant. Water is available but ag land may rely on catchment systems. Strong mainlander and second-home demand. Vacation rental restrictions in residential zones.",
        "keywords": ["farms", "views", "elevation", "protea", "Maui onion", "prestigious", "upcountry"],
        "aliases": ["Kula Maui", "Kula Upcountry", "Lower Kula", "Upper Kula"]
    },

    "Upcountry Maui": {
        "island": "Maui",
        "region": "Upcountry Maui",
        "vibe": "Upcountry is a collective term for the communities on Haleakala's slopes — Makawao, Kula, Pukalani, Haiku, and surrounding areas. Cool temperatures, pastoral landscapes, working farms, and a self-sufficient community ethos define this zone.",
        "lifestyle": "Growing lavender, protea, or Maui onions. Watching sunrise from Haleakala summit. Cool evening bonfires. Life at 2,000-4,000 feet elevation is genuinely different from beach Maui.",
        "nearby": ["Haleakala National Park", "Kula Botanical Garden", "Ali'i Kula Lavender Farm", "Surfing Goat Dairy"],
        "beaches": ["30-45 min to coast"],
        "commute": "Variable by sub-area — 20-45 min to Kahului.",
        "market_notes": "Agricultural land abundant with ag exemptions and restrictions. Water availability is a key issue — some areas on catchment. Mix of residential and farm lots. Fee simple dominant. Strong demand from mainland lifestyle buyers seeking rural Hawaii.",
        "keywords": ["farms", "cool", "Haleakala", "lavender", "pastoral", "elevation", "rural"],
        "aliases": ["Upcountry", "Kula", "Upcountry Maui area"]
    },

    "Hana": {
        "island": "Maui",
        "region": "East Maui",
        "vibe": "Hana is the most remote and sacred community in Maui — 52 miles and 620 curves from Kahului on the Road to Hana. It's what Hawaii was before tourism. A deeply Native Hawaiian community with black sand beaches, waterfalls, and a pace of life measured in tides, not minutes.",
        "lifestyle": "Growing taro, picking fruit, and living off the land. The Hana coast is breathtaking and the community is guarded — newcomers must come with deep respect. Waimoku Falls, Hamoa Beach, and Ohe'o Gulch are right there.",
        "nearby": ["Hana Bay", "Waimoku Falls (Pipiwai Trail)", "Hamoa Beach", "Ohe'o Gulch (Seven Sacred Pools)", "Koki Beach"],
        "beaches": ["Hamoa Beach", "Koki Beach", "Red Sand Beach (Ka'aliki)"],
        "commute": "2+ hours to Kahului on the Road to Hana — many Hana residents fly out of Hana Airport for faster access.",
        "market_notes": "Very limited inventory. Properties are generational — rarely sold. When they come available, strong demand from privacy-seeking buyers. Many properties on leased land or with complex history. Road access is a real consideration for emergency services. No real estate agent should oversell this lifestyle — buyers must understand the true remoteness.",
        "keywords": ["remote", "sacred", "Native Hawaiian", "waterfalls", "Road to Hana", "end of the road", "raw Hawaii"],
        "aliases": ["Hana Maui", "Road to Hana", "East Maui", "Hana Town"]
    },

    "Lanai City": {
        "island": "Lanai",
        "region": "Lanai",
        "vibe": "Lanai City is the only town on the island of Lanai — a charming, sleepy plantation-era community built around Dole pineapple operations and now anchored by two Four Seasons resorts. The entire island is privately held by Larry Ellison (98%).",
        "lifestyle": "Leisurely small-town life at 1,700 feet elevation. Dole Park gatherings, Four Seasons dining, and the quietest, most uncrowded experience in Hawaii. The whole island has fewer than 4,000 residents.",
        "nearby": ["Four Seasons Lanai (Manele Bay)", "Four Seasons Lodge at Koele", "Dole Park", "Hulopoe Bay", "Shipwreck Beach"],
        "beaches": ["Hulopoe Bay", "Shipwreck Beach", "Polihua Beach"],
        "commute": "Ferry to Lahaina or fly — Lanai is an island. No commute to Honolulu is realistic.",
        "market_notes": "Unique market — 98% of the island is Larry Ellison's company. Residential parcels for sale are extremely rare. When available, demand from ultra-wealthy privacy seekers. Very limited supply fundamentally.",
        "keywords": ["private island", "Ellison", "Four Seasons", "plantation", "quiet", "exclusive", "Dole"],
        "aliases": ["Lanai", "Lanai Oahu", "Lana'i City", "Lanai Island"]
    },

    "Molokai": {
        "island": "Molokai",
        "region": "Molokai",
        "vibe": "Molokai is the most authentically Hawaiian island remaining — no traffic lights, no fast food, and a Native Hawaiian majority who have successfully resisted large-scale resort development. It's raw, real, and fiercely protective of its culture and land.",
        "lifestyle": "Hunting deer in the mountains, fishing off the world's longest fringing reef, watching the sun set with the most dramatic sea cliffs on earth at Kalaupapa. Life here is deeply connected to the land and sea.",
        "nearby": ["Kalaupapa National Historical Park", "Papohaku Beach", "Halawa Valley", "Palaau State Park"],
        "beaches": ["Papohaku Beach", "Kepuhi Beach", "Halawa Beach"],
        "commute": "Island access by air or ferry from Maui. No off-island commute is practical.",
        "market_notes": "Very limited for-sale inventory. Strong community resistance to outside development. Hawaiian Home Lands cover significant portions of the island — not available for general purchase. Values are moderate relative to other islands. Buyers must come understanding and respecting the community's values.",
        "keywords": ["authentic", "Native Hawaiian", "undeveloped", "fishing", "sea cliffs", "remote", "cultural"],
        "aliases": ["Moloka'i", "Molokai Island", "Kaunakakai"]
    },

    # ─────────────────────────────────────────────────────────────────
    # KAUAI
    # ─────────────────────────────────────────────────────────────────

    "Lihue": {
        "island": "Kauai",
        "region": "East Kauai",
        "vibe": "Lihue is Kauai's commercial hub — the airport, government offices, Costco, and Walmart are all here. It's the practical center of island life without the scenic romance of other Kauai areas. Kalapaki Beach is a pleasant surprise in the middle of it all.",
        "lifestyle": "Urban (by Kauai standards) — shopping, services, and logistics. Kalapaki Beach for afternoon swims. Gateway to the island rather than destination.",
        "nearby": ["Lihue Airport (LIH)", "Kalapaki Beach", "Marriott Kauai", "Grove Farm Homestead", "Costco Kauai"],
        "beaches": ["Kalapaki Beach"],
        "commute": "Central island — 20-30 min to most of Kauai.",
        "market_notes": "Most affordable Kauai entry point. Older housing stock. Mix of residential and commercial-adjacent. Good investment rental market. Strong workforce housing demand. Flood zone considerations near Nawiliwili Harbor.",
        "keywords": ["hub", "affordable", "airport", "practical", "central", "government"],
        "aliases": ["Lihue Kauai", "Lihue Town", "Lihu'e", "Nawiliwili"]
    },

    "Poipu": {
        "island": "Kauai",
        "region": "South Kauai",
        "vibe": "Poipu is Kauai's premier resort destination — sunny South Shore beaches, luxury hotels, and world-class snorkeling. It's the most polished and resort-complete area on the island. The monk seal hauled out on Poipu Beach is a daily celebrity.",
        "lifestyle": "Morning snorkeling with sea turtles at Poipu Beach, afternoon at the Grand Hyatt Kauai pool, sunset cocktails at the Shops at Kukuiula. The South Shore gets the most sun on Kauai — critical given the island's famous rain.",
        "nearby": ["Poipu Beach Park", "Grand Hyatt Kauai", "Spouting Horn", "Shops at Kukuiula", "Koloa Town"],
        "beaches": ["Poipu Beach", "Brennecke's Beach", "Mahaulepu Beach"],
        "commute": "25-35 min to Lihue.",
        "market_notes": "Strong vacation rental market with legal permits in many buildings. Fee simple dominant in newer developments. HOAs active and costly. Top Kauai market with strong appreciation. International and mainland second-home buyers. Limited beachfront inventory.",
        "keywords": ["resort", "sunny", "vacation rental", "luxury", "snorkeling", "monk seals", "South Shore"],
        "aliases": ["Po'ipu", "Poipu Kauai", "Poipu Beach", "Poipu Resort"]
    },

    "Koloa": {
        "island": "Kauai",
        "region": "South Kauai",
        "vibe": "Koloa is Hawaii's oldest sugar plantation town — a charming historic town that anchors the South Shore with character and community that Poipu lacks. Old Koloa Town's wooden storefronts, restaurants, and historic mill make it the social hub of South Kauai.",
        "lifestyle": "Morning coffee in Old Koloa Town, afternoon at Poipu Beach, evening farm-to-table dinners. More residential and community-connected than the resort corridor.",
        "nearby": ["Old Koloa Town", "Koloa Mill ruins", "Poipu", "Lawai", "Spouting Horn"],
        "beaches": ["Poipu Beach (nearby)"],
        "commute": "25-30 min to Lihue.",
        "market_notes": "Mix of historic homes, newer subdivisions, and agricultural land. More affordable than Poipu. Fee simple dominant. Vacation rental restrictions in residential zones. Good family and local resident market.",
        "keywords": ["historic", "plantation", "community", "affordable", "South Kauai", "Koloa Town"],
        "aliases": ["Koloa Kauai", "Old Koloa Town", "Koloa Town", "Ko Loa"]
    },

    "Lawai": {
        "island": "Kauai",
        "region": "South Kauai",
        "vibe": "Lawai is a quiet, semi-rural South Kauai community tucked into a valley — more residential and affordable than Poipu, with the famous Allerton Garden as its landmark. Community-oriented with a slower pace.",
        "lifestyle": "Rural valley living with easy South Shore beach access. Allerton Garden tours. Local neighborhood feel.",
        "nearby": ["National Tropical Botanical Garden (Allerton)", "Koloa", "Poipu", "Kalaheo"],
        "beaches": ["Poipu Beach (10-15 min)"],
        "commute": "25-30 min to Lihue.",
        "market_notes": "Affordable South Kauai option. Mix of older homes and some newer builds. Agricultural land available. Fee simple dominant. Good value for families and workers serving the resort area.",
        "keywords": ["rural", "valley", "affordable", "botanical garden", "South Kauai", "quiet"],
        "aliases": ["Lawai Kauai", "Lawai Valley", "La Wai"]
    },

    "Kalaheo": {
        "island": "Kauai",
        "region": "South Kauai",
        "vibe": "Kalaheo is an elevated South Kauai community with beautiful valley views, cooler temperatures than the coast, and a genuine local neighborhood character. Kukuiolono Park and Golf Course is a beloved community asset.",
        "lifestyle": "Cooler, elevated living with valley and canyon views. Kukuiolono golf (free to residents). Easy access to South Shore beaches. A genuine local community.",
        "nearby": ["Kukuiolono Park & Golf Course", "Poipu", "Waimea Canyon (west)", "Hanapepe"],
        "beaches": ["Poipu Beach (20 min)"],
        "commute": "30-35 min to Lihue.",
        "market_notes": "Affordable for Kauai. Mix of residential and some agricultural land. Fee simple dominant. Strong local buyer demand. Views add value. Vacation rental restrictions in residential zones.",
        "keywords": ["elevated", "views", "affordable", "local", "golf", "cooler", "South Kauai"],
        "aliases": ["Kalaheo Kauai", "Kalaheo Town"]
    },

    "Hanapepe": {
        "island": "Kauai",
        "region": "West Kauai",
        "vibe": "Hanapepe bills itself as Kauai's 'biggest little town' — a former plantation community with a lively Friday art night scene, salt ponds, and a historic wooden swinging bridge. It's charming, slightly faded, and very real.",
        "lifestyle": "Friday art nights on Hanapepe Road, salt harvesting at the Hawaiian Salt Ponds, and access to the Westside's rugged landscape. A community reclaiming its identity through arts.",
        "nearby": ["Hanapepe Salt Ponds", "Hanapepe Swinging Bridge", "Waimea", "Ele'ele", "Port Allen"],
        "beaches": ["Salt Pond Beach Park", "Glass Beach (Port Allen)"],
        "commute": "35-45 min to Lihue.",
        "market_notes": "Affordable West Side Kauai. Older housing stock. Investment opportunity in a community with growing arts identity. Flood zone near river. Agricultural land common. Good for buyers who want authentic Kauai without tourist-corridor prices.",
        "keywords": ["art", "historic", "plantation", "salt ponds", "affordable", "authentic", "West Side"],
        "aliases": ["Hanapepe Kauai", "Hanapepe Town", "Hanappe"]
    },

    "Waimea": {
        "island": "Kauai",
        "region": "West Kauai",
        "vibe": "Waimea is the westernmost town of significance on Kauai — a historic port where Captain Cook first landed in Hawaii, at the mouth of the river that carves Waimea Canyon. It's the gateway to one of the state's most dramatic landscapes.",
        "lifestyle": "Day trips up to Waimea Canyon and Kokee State Park. Waimea Town Celebration in February. A quiet, historic community serving the Westside.",
        "nearby": ["Waimea Canyon State Park", "Kokee State Park", "Waimea Plantation Cottages", "Polihale Beach"],
        "beaches": ["Waimea Beach", "Polihale State Park (30 min west)"],
        "commute": "45-55 min to Lihue.",
        "market_notes": "Most affordable area on Kauai. Some historic properties with renovation potential. Agricultural and ranch land abundant. Limited services and remote feel. Buyer profile is typically local workers, investors, or buyers seeking maximum affordability.",
        "keywords": ["historic", "canyon", "affordable", "remote", "Captain Cook", "gateway", "plantation"],
        "aliases": ["Waimea Kauai", "Waimea Canyon area", "Waimea Town"]
    },

    "Princeville": {
        "island": "Kauai",
        "region": "North Shore Kauai",
        "vibe": "Princeville is a planned resort community on Kauai's breathtaking North Shore — 9,000 acres of clifftop development above Hanalei Bay with views that are simply unmatched in Hawaii. It's the North Shore's luxury hub.",
        "lifestyle": "Morning at the St. Regis Princeville, golf on the Prince or Makai courses overlooking the bay, afternoon snorkeling at Hideaways or Queen's Bath (carefully), sunset from the clifftop. If the views are the priority, this is the neighborhood.",
        "nearby": ["St. Regis Princeville", "Prince Golf Course", "Makai Golf Club", "Hanalei", "Anini Beach"],
        "beaches": ["Hideaways Beach", "Pali Ke Kua Beach", "Anini Beach (nearby)"],
        "commute": "45-60 min to Lihue. North Shore road is narrow and can flood/close in winter.",
        "market_notes": "Premium pricing for views and North Shore access. Mix of condos and single-family. HOAs active. STR permits in resort zones; residential zones more restricted. Road closure risk in winter is real — affects rental availability and emergency access. Strong mainland and international second-home demand.",
        "keywords": ["luxury", "views", "North Shore", "golf", "St. Regis", "clifftop", "Hanalei Bay views"],
        "aliases": ["Princeville Kauai", "Princeville Resort", "North Shore Princeville"]
    },

    "Hanalei": {
        "island": "Kauai",
        "region": "North Shore Kauai",
        "vibe": "Hanalei is the crown jewel of Kauai — a taro-farming valley cradled by cathedral mountains, fronting the most dramatic bay in Hawaii. It's small, sacred, and deeply protected by a community determined to keep it real. This is what paradise actually looks like.",
        "lifestyle": "Waking up to Na Pali cloud shadows on the valley. Surfing Hanalei Bay. Taro poi for lunch. The farmers market. Kayaking the Hanalei River. Life here is the Hawaii everyone imagines before they arrive.",
        "nearby": ["Hanalei Bay Beach", "Hanalei National Wildlife Refuge", "Wai'oli Mission Church", "Anini Beach", "Kilauea"],
        "beaches": ["Hanalei Bay", "Anini Beach", "Black Pot Beach Park"],
        "commute": "45-55 min to Lihue. The one-lane bridge is a bottleneck and the road floods in heavy rain — sometimes for days.",
        "market_notes": "Among the most coveted and limited markets in Hawaii. Very low inventory, very high demand. Mix of older plantation homes and newer custom builds. Agricultural land with complex permit history. Vacation rental rules strict — long-standing permits grandfathered. Road closure risk in winter adds complexity. Cash buyers common. Buyers who buy here rarely sell.",
        "keywords": ["iconic", "bay", "taro", "mountains", "sacred", "limited inventory", "paradise", "Na Pali"],
        "aliases": ["Hanalei Kauai", "Hanalei Bay", "Hanalei Town", "Hanalei Valley"]
    },

    "Kilauea": {
        "island": "Kauai",
        "region": "North Shore Kauai",
        "vibe": "Kilauea is a small North Shore town best known for the Kilauea Lighthouse and a growing organic farm and food scene. It's the affordable entry point to the North Shore lifestyle — less dramatic than Hanalei but genuinely lovely.",
        "lifestyle": "Farmers market Saturdays, lighthouse birding, and quick North Shore beach access. Kong Lung Historic Market Center. A growing food and arts scene.",
        "nearby": ["Kilauea Lighthouse National Wildlife Refuge", "Kong Lung Center", "Anini Beach", "Princeville", "Hanalei"],
        "beaches": ["Anini Beach (nearby)", "Kilauea Bay (fishing, no swim)"],
        "commute": "35-45 min to Lihue.",
        "market_notes": "More affordable than Hanalei and Princeville. Mix of residential and agricultural. Fee simple dominant. Good value for North Shore lifestyle. Vacation rental restrictions in residential zones. Growing buyer interest from mainland lifestyle seekers.",
        "keywords": ["lighthouse", "organic", "affordable", "North Shore", "farms", "community"],
        "aliases": ["Kilauea Kauai", "Kilauea Town", "Kilauea Lighthouse area"]
    },

    "Kapaa": {
        "island": "Kauai",
        "region": "East Kauai",
        "vibe": "Kapaa is the Coconut Coast's main town — the longest stretch of shops, restaurants, and services on Kauai outside of Lihue. It has more energy and walkability than anywhere on the island, a thriving local food scene, and the beloved Ke Ala Hele Makalae coastal path.",
        "lifestyle": "Morning bike rides on the coastal path, farmers markets, and a restaurant scene that punches above its size. Kapaa is where Kauai's young professional and creative class lives. Enough hustle to feel alive, enough Hawaii to not feel mainland.",
        "nearby": ["Kapaa Beach Park", "Ke Ala Hele Makalae path", "Coconut Marketplace", "Wailua River", "Opaekaa Falls"],
        "beaches": ["Kapaa Beach", "Kealia Beach"],
        "commute": "15-20 min to Lihue.",
        "market_notes": "Good value for walkable Kauai living. Mix of condos, older homes, and newer subdivisions. Strong rental demand. Coconut Coast traffic can be frustrating. Flood zone near river and coast. Fee simple dominant. Strong appreciation as Kauai overall has appreciated significantly.",
        "keywords": ["walkable", "coastal path", "food scene", "community", "Coconut Coast", "affordable", "biking"],
        "aliases": ["Kapa'a", "Kapaa Kauai", "Kapaa Town", "Coconut Coast", "Kapa'a Town"]
    },

    "Wailua": {
        "island": "Kauai",
        "region": "East Kauai",
        "vibe": "Wailua is a residential area south of Kapaa centered around the sacred Wailua River — one of the most historically significant rivers in Hawaii, lined with ancient heiau. It's quieter and more suburban than Kapaa.",
        "lifestyle": "Kayaking the Wailua River to Fern Grotto. Opaekaa Falls and the Wailua Heritage Trail. Quiet suburban living with East Side access.",
        "nearby": ["Wailua River State Park", "Opaekaa Falls", "Fern Grotto", "Kapaa", "Lydgate Beach"],
        "beaches": ["Lydgate Beach Park", "Kapaa Beach (nearby)"],
        "commute": "15-20 min to Lihue.",
        "market_notes": "Mix of residential and some resort-adjacent commercial. Flood zone near river is significant — buyers must review carefully. Fee simple dominant. Good value relative to South Shore.",
        "keywords": ["river", "heiau", "sacred", "kayaking", "residential", "East Side"],
        "aliases": ["Wailua Kauai", "Wailua Homesteads", "Wailua River area"]
    },

    "Anahola": {
        "island": "Kauai",
        "region": "North East Kauai",
        "vibe": "Anahola is a rural North East Kauai community with a significant Native Hawaiian population and Hawaiian Home Lands. It's quiet, agricultural, and a genuine local community — not a real estate destination but important to understand.",
        "lifestyle": "Local Hawaiian community life. Anahola Beach is stunning and lightly visited. Agricultural roots.",
        "nearby": ["Anahola Beach", "Kilauea", "Kapaa"],
        "beaches": ["Anahola Beach"],
        "commute": "25-30 min to Lihue.",
        "market_notes": "Mix of fee simple (limited) and Hawaiian Home Lands (not available for general purchase). Very limited for-sale inventory in fee simple sections. Buyers must carefully verify land tenure.",
        "keywords": ["rural", "Native Hawaiian", "Hawaiian Home Lands", "quiet", "agricultural"],
        "aliases": ["Anahola Kauai", "Anahola Beach area"]
    },

    "Kokee": {
        "island": "Kauai",
        "region": "West Kauai Highlands",
        "vibe": "Kokee is not a residential community — it's a state park at 4,000 feet above Waimea Canyon. State cabins are available for rent but no real estate market exists. It's included here because agents sometimes get questions about Kokee.",
        "lifestyle": "Cloud forest hiking, birdwatching for endangered Hawaiian birds, and dramatic canyon views. Kokee Lodge restaurant. A getaway, not a neighborhood.",
        "nearby": ["Waimea Canyon", "Na Pali Coast (Kalalau Trail access)", "Kokee Lodge", "Koke'e Natural History Museum"],
        "beaches": ["None — 4,000 ft elevation"],
        "commute": "45-60 min to Lihue on winding mountain road.",
        "market_notes": "No private real estate available — entirely state park land. Agents should clarify this clearly if clients ask about 'buying in Kokee.'",
        "keywords": ["state park", "cloud forest", "canyon", "birdwatching", "no real estate", "hiking"],
        "aliases": ["Koke'e", "Kokee State Park", "Kokee Kauai"]
    },

    # ─────────────────────────────────────────────────────────────────
    # BIG ISLAND — KONA SIDE
    # ─────────────────────────────────────────────────────────────────

    "Kailua-Kona": {
        "island": "Big Island",
        "region": "West Hawaii",
        "vibe": "Kailua-Kona is the Big Island's western hub — a historic Hawaiian fishing village turned vibrant resort and residential town. It's the commercial and social center of West Hawaii with a walkable downtown, excellent restaurants, and world-famous ironman/triathlete energy.",
        "lifestyle": "Morning manta ray dives off the pier, afternoon coffee tours, triathlete training runs at the pier, and evening happy hours on Ali'i Drive. Sunny and warm year-round. The Big Island's most accessible and complete lifestyle.",
        "nearby": ["Kailua Pier", "Ali'i Drive", "Magic Sands Beach", "Kona Coffee farms", "Hulihee Palace"],
        "beaches": ["Magic Sands (La'aloa Beach)", "Kahalu'u Beach Park", "White Sands Beach"],
        "commute": "Central West Hawaii — 15-30 min to most Kona area destinations. 2+ hrs to Hilo.",
        "market_notes": "Active residential and vacation rental market. Mix of condos on Ali'i Drive (many STR-permitted) and single-family above town. Some leasehold in older condo complexes. Lava zone designations vary — Zone 4-6 in this area, lower risk. HOAs active in resort areas. Strong appreciation over time.",
        "keywords": ["triathlon", "ironman", "coffee", "fishing", "resort", "walkable", "manta rays"],
        "aliases": ["Kona", "Kailua Kona", "Kona Town", "Kailua-Kona Big Island", "Ali'i Drive area"]
    },

    "Keauhou": {
        "island": "Big Island",
        "region": "West Hawaii",
        "vibe": "Keauhou is the quieter, more residential extension of Kona — a planned community south of downtown Kailua-Kona with a shopping center, golf courses, and more spacious lots. Popular with retirees and families who want the Kona climate with less downtown bustle.",
        "lifestyle": "Golf at Kona Country Club, snorkeling at Kahalu'u (world-class and very close), and the Keauhou Shopping Center for daily needs. Quieter and more planned than Kona town.",
        "nearby": ["Kahalu'u Beach Park", "Kona Country Club", "Keauhou Shopping Center", "Kailua-Kona", "Kealakekua Bay"],
        "beaches": ["Kahalu'u Beach Park", "White Sands Beach (nearby)"],
        "commute": "10-15 min to Kailua-Kona town.",
        "market_notes": "Strong retiree and second-home market. Mix of condos and single-family. HOAs active. Lava zone 4-5. Good value relative to oceanfront Kona. Kahalu'u Beach proximity drives condo values.",
        "keywords": ["golf", "retirees", "planned community", "snorkeling", "Kahalu'u", "suburban"],
        "aliases": ["Keauhou Kona", "Keauhou Big Island", "Keauhou-Kona"]
    },

    "Captain Cook": {
        "island": "Big Island",
        "region": "South Kona",
        "vibe": "Captain Cook is the commercial hub of the South Kona coffee belt — a real working community with grocery stores and gas stations serving the surrounding farms. Kealakekua Bay, where Captain Cook died, is right below.",
        "lifestyle": "Coffee farming life in the hills. Access to the extraordinary snorkeling at Kealakekua Bay. Napo'opo'o road down to the bay for kayak snorkeling tours. Real community, not tourism.",
        "nearby": ["Kealakekua Bay State Historical Park", "City of Refuge (Pu'uhonua o Honaunau)", "Kona coffee farms", "Honaunau"],
        "beaches": ["Napo'opo'o Beach (boat/kayak access for snorkeling at Kealakekua)"],
        "commute": "20-25 min to Kailua-Kona town.",
        "market_notes": "Agricultural and residential mix. Lava zone varies. Some parcels with coffee farm income potential. Cooler climate at elevation. Older housing stock. Good value for buyers wanting South Kona lifestyle. Vacation rentals on ag land require careful permitting review.",
        "keywords": ["coffee", "South Kona", "farms", "Kealakekua Bay", "elevation", "agricultural"],
        "aliases": ["Captain Cook Big Island", "South Kona", "Kealakekua area", "Kealakekua"]
    },

    "Holualoa": {
        "island": "Big Island",
        "region": "North Kona Uplands",
        "vibe": "Holualoa is an artists' village perched above Kailua-Kona in the coffee belt — galleries, cafes, and a creative community enjoying spectacular coastal views from 1,400 feet elevation. It's where Kona's cultural and artistic life concentrates.",
        "lifestyle": "Morning gallery hopping on Mamalahoa Highway, coffee from your neighbor's farm, and sweeping ocean views over morning clouds. Cooler and more contemplative than the coast below.",
        "nearby": ["Holualoa Village galleries", "Kailua-Kona (10 min down)", "Kona coffee belt", "Donkey Mill Art Center"],
        "beaches": ["15-20 min to coastal Kona beaches"],
        "commute": "15-20 min to Kailua-Kona. Winding uphill road.",
        "market_notes": "Mix of residential and coffee farm parcels. Views add significant value. Older homes on larger lots. Limited inventory. Buyers typically artists, creative professionals, coffee farmers, and those wanting coastal views without coastal prices.",
        "keywords": ["artists", "galleries", "coffee", "views", "elevation", "creative", "village"],
        "aliases": ["Holualoa Kona", "Holualoa Big Island", "Kona coffee country"]
    },

    "Waimea": {
        "island": "Big Island",
        "region": "North Hawaii",
        "vibe": "Waimea (also called Kamuela) is the Big Island's paniolo (cowboy) country — a ranching community at 2,700 feet elevation with stunning Parker Ranch pastures, cooler temperatures, and a growing foodie scene. One of the best quality-of-life spots on the island.",
        "lifestyle": "Parker Ranch horseback riding, Saturday morning farmers market, and excellent restaurants fueled by local beef and farm produce. A sophisticated small town. Clear nights make it excellent for astronomy.",
        "nearby": ["Parker Ranch", "Mauna Kea (30 min)", "Kohala Coast (30 min)", "Waimea-Kohala Airport", "Kohala Mountain Road"],
        "beaches": ["30-45 min to Kohala Coast beaches"],
        "commute": "30-45 min to Kona or Hilo — accessible from both coasts.",
        "market_notes": "Strong demand, limited supply. Mix of residential and ranch/agricultural land. Fee simple dominant. Cooler climate drives demand from buyers who can't tolerate Kona heat. Strong local and transplant community. Parker Ranch land leases a consideration in some areas.",
        "keywords": ["ranch", "paniolo", "cool", "elevation", "foodie", "farming", "astronomy"],
        "aliases": ["Waimea Big Island", "Kamuela", "Waimea-Kamuela", "Parker Ranch area"]
    },

    "Kohala Coast": {
        "island": "Big Island",
        "region": "North Kohala",
        "vibe": "The Kohala Coast is the Big Island's luxury resort corridor — a stretch of stunning white sand beaches carved from black lava with the Mauna Kea, Fairmont Orchid, Four Seasons Hualalai, and Waikoloa Beach Resort anchoring world-class residential and resort development.",
        "lifestyle": "Golf on championship courses with ocean and volcano views, manta ray night dives off Keauhou, and the Mauna Kea Beach Hotel's Monday luau. The driest, sunniest part of the Big Island. Whales visible from fairways November through April.",
        "nearby": ["Mauna Kea Beach Hotel", "Fairmont Orchid", "Four Seasons Hualalai", "Waikoloa Beach Resort", "Puako"],
        "beaches": ["Mauna Kea Beach (Kauna'oa)", "Hapuna Beach", "Waikoloa Beach", "Anaeho'omalu Bay"],
        "commute": "30-40 min to Kailua-Kona. Private area — somewhat self-contained.",
        "market_notes": "Among the most expensive Big Island markets. Mix of resort condos, luxury homes, and large estates. HOA fees high in resort communities. Strong STR market in designated resort zones. Cash buyers common. Lava Zone 4-6 — lower risk. Water is a big issue — county water vs. private systems vs. catchment in different areas.",
        "keywords": ["luxury", "resort", "golf", "whales", "sunny", "lava coast", "Mauna Kea"],
        "aliases": ["Kohala Coast Big Island", "South Kohala", "Waikoloa", "Waikoloa Beach", "Kohala"]
    },

    "Hilo": {
        "island": "Big Island",
        "region": "East Hawaii",
        "vibe": "Hilo is the Big Island's other city — the county seat, the rainforest side, and arguably the most authentic and affordable urban Hawaii experience remaining. It rains a lot. The vegetation is impossibly lush. The farmers market is the best in the state. Locals wouldn't trade it.",
        "lifestyle": "Saturday morning Hilo Farmers Market (don't miss it), tide pool exploring at Richardson Beach, waterfalls in your backyard, and a genuine community that hasn't been priced out. University of Hawaii Hilo campus adds academic energy.",
        "nearby": ["Hilo Farmers Market", "Liliuokalani Gardens", "Rainbow Falls", "Akaka Falls (nearby)", "Wailoa River State Park"],
        "beaches": ["Richardson Beach Park", "Onekahakaha Beach Park"],
        "commute": "2+ hours to Kona — most Hilo residents live Hilo-centric lives.",
        "market_notes": "Most affordable Big Island market for comparable square footage. Older housing stock. Rain and humidity mean mold and maintenance are real concerns — due diligence on home condition essential. Strong UH Hilo rental demand. Flood zone risk near coast and streams. Tsunami zone considerations in low-lying areas.",
        "keywords": ["affordable", "lush", "rain", "farmers market", "rainforest", "university", "authentic"],
        "aliases": ["Hilo Big Island", "Hilo Hawaii", "Hilo Town", "East Hawaii"]
    },

    "Pahoa": {
        "island": "Big Island",
        "region": "Puna",
        "vibe": "Pahoa is Puna's funky, counterculture hub — a wooden-storefront town with a rainbow of alternative lifestyles, organic farms, and a community that came to live outside mainstream society. The 2018 Kilauea eruption reshaped the Puna landscape dramatically.",
        "lifestyle": "Off-grid living, raw superfoods, naked hot springs at Ahalanui (now covered by lava), and a creative community that asks fewer questions. Very local, very alternative, very real.",
        "nearby": ["Lava Tree State Monument", "Pahoa Village Road", "Nanawale Forest Reserve", "Leilani Estates (nearby)"],
        "beaches": ["Kehena Beach (clothing-optional)", "Isaac Hale Beach Park"],
        "commute": "45-60 min to Hilo. Remote from Kona.",
        "market_notes": "Very affordable but buyers must understand lava zone risk. Pahoa area is Lava Zone 1-2 — the highest risk designation. The 2018 eruption destroyed hundreds of homes in Leilani Estates nearby. Insurance is difficult to obtain or very expensive in the highest-risk zones. Water catchment systems common. Buyers must fully understand and accept volcanic risk.",
        "keywords": ["alternative", "countercultural", "lava risk", "affordable", "Puna", "organic", "remote"],
        "aliases": ["Pahoa Big Island", "Pahoa Town", "Pahoa Puna", "Lower Puna"]
    },

    "Volcano": {
        "island": "Big Island",
        "region": "Puna",
        "vibe": "Volcano Village is a misty, otherworldly community at 3,700 feet on the edge of Hawaii Volcanoes National Park. Lush tree fern forests, rare birds, and the ever-present smell of sulfur create an environment unlike any other in Hawaii.",
        "lifestyle": "Morning hikes in the national park before the tourists arrive, afternoons watching lava glow, evenings by the fire (necessary at this elevation). Small artistic community. Very quiet, very dramatic.",
        "nearby": ["Hawaii Volcanoes National Park", "Kilauea Iki Crater", "Thurston Lava Tube", "Volcano Winery", "Kilauea Military Camp"],
        "beaches": ["No beaches — inland, 3,700 ft elevation"],
        "commute": "45 min to Hilo. Very remote from Kona.",
        "market_notes": "Unique market — buyers are buying the experience, not the amenities. Lava Zone 1 designation means very difficult/expensive insurance. Older housing stock, often older construction. Some properties have VOG (volcanic air pollution) issues. Vacation rental market exists for park-adjacent visitors. Very limited inventory.",
        "keywords": ["volcano", "national park", "elevation", "misty", "lava", "unique", "remote", "birds"],
        "aliases": ["Volcano Village", "Volcano Hawaii", "Volcano Big Island", "Kilauea Village"]
    },

    "Leilani Estates": {
        "island": "Big Island",
        "region": "Puna",
        "vibe": "Leilani Estates was a quiet affordable Puna subdivision that became the epicenter of the 2018 Kilauea eruption — hundreds of homes were destroyed by lava flows from Fissure 8. Surviving sections are rebuilding but the neighborhood carries the weight of that history.",
        "lifestyle": "Affordable Puna living — jungle lots, warm weather, Puna's alternative community spirit. But the 2018 event changed the psychology of the neighborhood permanently.",
        "nearby": ["Pahoa", "Lanipuna Gardens", "Isaac Hale Beach Park", "Lava tree parks"],
        "beaches": ["Isaac Hale Beach (20 min)"],
        "commute": "50-60 min to Hilo.",
        "market_notes": "Lava Zone 1 — the highest volcanic risk designation in Hawaii. Insurance is extremely difficult and expensive. Many lots still have lava or are adjacent to lava fields from 2018. Buyers must fully understand and independently verify lava zone, insurance options, and the history of specific parcels. Some lots offer extraordinary value for buyers who accept the risk.",
        "keywords": ["lava zone 1", "eruption history", "affordable", "Puna", "volcanic risk", "2018 eruption"],
        "aliases": ["Leilani", "Leilani Puna", "Leilani Estates Big Island", "Leilani Estates Pahoa"]
    },

    "Puna": {
        "island": "Big Island",
        "region": "Puna",
        "vibe": "Puna is a district, not a single neighborhood — encompassing Pahoa, Leilani Estates, Hawaiian Beaches, Lanipuna, and other communities in the Big Island's most volcanic, most affordable, and most alternative-lifestyle zone.",
        "lifestyle": "Off-grid living, tropical agriculture, warm weather year-round, and a community that prizes independence. The geothermal energy plant is here. So is significant volcanic risk.",
        "nearby": ["Pahoa", "Leilani Estates", "Hilo", "Hawaii Volcanoes National Park"],
        "beaches": ["Kehena Beach", "Isaac Hale Beach"],
        "commute": "45-70 min to Hilo depending on sub-area.",
        "market_notes": "Affordable but lava zone risk varies dramatically — Zone 1 in some areas, Zone 3 in others. Buyers must research specific parcel lava zones. Insurance is the key due diligence item. Strong investment market for buyers who accept the risk.",
        "keywords": ["district", "affordable", "volcanic", "alternative", "off-grid", "geothermal", "lava zones"],
        "aliases": ["Lower Puna", "Puna District", "Puna Big Island"]
    },

    "Ocean View": {
        "island": "Big Island",
        "region": "Ka'u",
        "vibe": "Ocean View is one of the most affordable places to buy land and a home in Hawaii — large lots at 2,000 feet elevation on the dry southern Ka'u coast. The name is aspirational; most lots don't actually see the ocean. It's extremely remote and DIY.",
        "lifestyle": "True off-grid pioneer living. Water catchment. Long drives for groceries. Extraordinary stargazing. A community of people who value land ownership and independence above all else.",
        "nearby": ["South Point (Ka Lae)", "Naalehu", "Hawaii Volcanoes National Park (45 min)"],
        "beaches": ["South Point (no swim beach)", "Green Sand Beach (Papakolea — 2.5 mile walk)"],
        "commute": "60-75 min to Kona. 45-60 min to Pahoa. Very remote.",
        "market_notes": "Most affordable Big Island market. Lava Zone 3 — moderate risk, but older lava. Water catchment almost universal — no county water. Roads are paved main roads but interior roads can be unpaved. Buyers are typically buyers who want maximum land and affordability regardless of remoteness.",
        "keywords": ["affordable", "remote", "large lots", "off-grid", "elevation", "Ka'u", "water catchment"],
        "aliases": ["Ocean View Big Island", "Ocean View Estates", "Ka'u", "Oceanview"]
    },

    "Naalehu": {
        "island": "Big Island",
        "region": "Ka'u",
        "vibe": "Naalehu is the southernmost town in the United States — a small Ka'u plantation community with a bakery, hardware store, and post office. It's the service center for the remote Ka'u district.",
        "lifestyle": "Small-town rural Hawaii. The southernmost bakery in the US. South Point nearby. Punalu'u Black Sand Beach is 10 minutes away. Simple, honest, remote.",
        "nearby": ["Punalu'u Black Sand Beach", "South Point (Ka Lae)", "Whittington Beach Park", "Pahala"],
        "beaches": ["Punalu'u Black Sand Beach", "Whittington Beach Park"],
        "commute": "60-75 min to Kona. Ka'u residents live Ka'u-centric lives.",
        "market_notes": "Very affordable. Limited inventory. Agricultural and residential mix. Macadamia nut and sugarcane history. Buyers seeking true rural Big Island life at low cost.",
        "keywords": ["southernmost", "rural", "affordable", "Ka'u", "black sand", "remote", "plantation"],
        "aliases": ["Na'alehu", "Naalehu Big Island", "Naalehu Ka'u", "Ka'u District"]
    },

    "South Kona": {
        "island": "Big Island",
        "region": "South Kona",
        "vibe": "South Kona is the coffee and macadamia nut belt — a string of communities from Kealakekua to Honaunau on the slopes above the ocean. Lush, green, agricultural, and deeply community-rooted. City of Refuge is one of Hawaii's most sacred historical sites.",
        "lifestyle": "Coffee farm mornings, snorkeling at Kealakekua Bay by kayak, the farmers market, and the Pu'uhonua o Honaunau National Historical Park. South Kona is where people who love Hawaii's agricultural and cultural roots choose to live.",
        "nearby": ["Pu'uhonua o Honaunau NHP", "Kealakekua Bay", "Honaunau", "Captain Cook", "Kona Coffee farms"],
        "beaches": ["Two-Step at Honaunau", "Kealakekua Bay (kayak access)"],
        "commute": "20-30 min to Kailua-Kona town.",
        "market_notes": "Agricultural and residential mix. Coffee farm properties available with income potential. Cooler climate a selling point. Older homes on larger lots. Some off-grid infrastructure. Good value for buyers who understand agricultural lifestyle. Vacation rentals on ag land require careful permit review.",
        "keywords": ["coffee", "agriculture", "City of Refuge", "farming", "Kealakekua", "South Kona"],
        "aliases": ["South Kona Big Island", "Kona coffee belt", "Honaunau area", "Kealakekua-Honaunau"]
    },

    # ─────────────────────────────────────────────────────────────────
    # ISLAND-LEVEL PROFILES (used when no specific neighborhood given)
    # ─────────────────────────────────────────────────────────────────

    "Oahu": {
        "island": "Oahu",
        "region": "Statewide",
        "vibe": "Oahu is the Gathering Place — Hawaii's most populous and diverse island, home to Honolulu, the North Shore's world-class surf, the Windward Coast's lush beauty, and the suburban communities of Central and Leeward Oahu. It offers the most complete lifestyle infrastructure in Hawaii.",
        "lifestyle": "Urban professionals, military families, surf culture devotees, and multi-generational local families all find their place on Oahu. From the walkable energy of Kakaako to the rural quiet of Waimanalo, the island accommodates every lifestyle within 44 miles.",
        "nearby": ["Honolulu", "Waikiki", "North Shore", "Windward Coast", "Ewa Plain"],
        "beaches": ["Waikiki Beach", "Kailua Beach", "Sunset Beach", "Ala Moana Beach Park"],
        "commute": "Honolulu is the commercial center — most communities are 20-60 min from downtown depending on location.",
        "market_notes": "Hawaii's most liquid and competitive real estate market. Heavy mix of fee simple and leasehold across all property types — buyers must verify for every listing. Rail transit (HART) is transforming the Ewa and Pearl Harbor corridors. Flood zones, HOAs, and lava zones are less of a concern here than other islands, though coastal flood risk applies near beaches.",
        "keywords": ["Oahu", "Honolulu", "diverse", "military", "surf", "urban", "liquid market"],
        "aliases": ["O'ahu", "Oahu Island", "Honolulu area"]
    },

    "Maui": {
        "island": "Maui",
        "region": "Statewide",
        "vibe": "Maui is the Valley Isle — a diverse landscape spanning resort-lined beaches, coffee farms, world-class upcountry ranchland, and the dramatic Road to Hana. It consistently tops 'best island' lists and its real estate market reflects that desirability.",
        "lifestyle": "Three distinct lifestyle zones: resort West and South Maui for beach and golf living, Central Maui for practical family life, and Upcountry for agricultural and rural living. The 2023 Lahaina fire changed the island's character and is still reshaping its communities.",
        "nearby": ["Kaanapali", "Wailea", "Kihei", "Kahului", "Upcountry"],
        "beaches": ["Kaanapali Beach", "Wailea Beach", "Kamaole Beaches", "Hookipa Beach"],
        "commute": "Kahului is the island hub — 20-40 min from most communities.",
        "market_notes": "Second most expensive Hawaii real estate market after Honolulu metro. Strong vacation rental market in resort zones. Upcountry agricultural land with growing demand. Post-Lahaina fire recovery is reshaping West Maui values. Whale season (Nov-Apr) is a lifestyle premium that agents should reference for coastal properties.",
        "keywords": ["Maui", "resort", "upcountry", "whales", "Road to Hana", "Lahaina recovery"],
        "aliases": ["Maui Island", "Valley Isle", "Maui County"]
    },

    "Kauai": {
        "island": "Kauai",
        "region": "Statewide",
        "vibe": "Kauai is the Garden Isle — the most lush, most dramatic, and most intentionally underdeveloped of Hawaii's major islands. Na Pali Coast, Waimea Canyon, and Hanalei Bay are world-class natural landmarks. Growth is deliberately limited by geography and community values.",
        "lifestyle": "Kauai attracts buyers who prioritize natural beauty, privacy, and a slower pace over urban amenities. North Shore is iconic and expensive; South Shore is sunny and resort-complete; East Side is affordable and community-oriented; West Side is rural and authentic.",
        "nearby": ["Lihue", "Poipu", "Hanalei", "Kapaa", "Waimea Canyon"],
        "beaches": ["Hanalei Bay", "Poipu Beach", "Anini Beach", "Ke'e Beach"],
        "commute": "Lihue is the island center — 20-55 min from most communities. North Shore road closures in winter are a real consideration.",
        "market_notes": "Limited supply and strong demand drive consistently high values. North Shore properties among most coveted in state. Vacation rental rules are tightening island-wide — long-standing permits have value. Agricultural land abundant but subject to county restrictions. Water availability varies by area. Flood zone awareness important on North Shore and East Side.",
        "keywords": ["Kauai", "Na Pali", "Garden Isle", "lush", "North Shore", "dramatic", "limited supply"],
        "aliases": ["Kaua'i", "Kauai Island", "Garden Isle"]
    },

    "Big Island": {
        "island": "Big Island",
        "region": "Statewide",
        "vibe": "The Big Island of Hawaii is the youngest, largest, and most geologically active island — twice the size of all other Hawaii islands combined. It spans 11 of the world's 14 climate zones. Kona's sunny leeward coast and Hilo's lush rainy east side offer completely different lifestyles on the same island.",
        "lifestyle": "From the luxury resort corridor of the Kohala Coast to the off-grid lava fields of Puna, the Big Island accommodates every lifestyle archetype. Coffee farming, ranching, volcano watching, and world-class diving all happen here. Space is the defining feature — lot sizes and land values that simply don't exist on other islands.",
        "nearby": ["Kailua-Kona", "Hilo", "Waimea", "Kohala Coast", "Volcano"],
        "beaches": ["Hapuna Beach", "Kauna'oa Beach (Mauna Kea)", "Kahalu'u Beach", "Punalu'u Black Sand Beach"],
        "commute": "Two main population centers (Kona and Hilo) are 2+ hours apart. Most residents live on one side of the island.",
        "market_notes": "Most affordable Hawaii market for land and square footage, though Kohala Coast luxury competes with anywhere. Lava zone designations are critical to understand — Zone 1 (highest risk) in Puna, Zone 4-6 (lower risk) on most of Kona side. Insurance availability directly tied to lava zone. Water access varies — catchment systems common in rural areas. Largest inventory of any Hawaii island.",
        "keywords": ["Big Island", "Hawaii Island", "lava", "coffee", "Kona", "Hilo", "affordable land"],
        "aliases": ["Hawaii Island", "Hawaii Big Island", "Island of Hawaii", "Hawaii"]
    },

}


# ─────────────────────────────────────────────────────────────────
# LOOKUP AND FORMATTING FUNCTIONS
# ─────────────────────────────────────────────────────────────────

def get_neighborhood_context(neighborhood_input, island_input=None):
    """
    Returns the best matching neighborhood profile for the given input.
    Returns None if no confident match found.
    """
    if not neighborhood_input or not neighborhood_input.strip():
        return None

    query = neighborhood_input.strip()
    query_lower = query.lower()

    def matches_island(nb_data):
        if not island_input:
            return True
        return nb_data.get("island", "").lower() == island_input.strip().lower()

    candidates = {k: v for k, v in NEIGHBORHOODS.items() if matches_island(v)}

    # 1. Case-insensitive exact match on neighborhood name
    for name, data in candidates.items():
        if name.lower() == query_lower:
            return data

    # 2. Exact match on any alias
    for name, data in candidates.items():
        for alias in data.get("aliases", []):
            if alias.lower() == query_lower:
                return data

    # 3. Partial match — input contained in name or name contained in input
    for name, data in candidates.items():
        if query_lower in name.lower() or name.lower() in query_lower:
            return data

    # 4. Partial match on aliases
    for name, data in candidates.items():
        for alias in data.get("aliases", []):
            if query_lower in alias.lower() or alias.lower() in query_lower:
                return data

    # 5. Fuzzy match using difflib (catches misspellings)
    all_names = list(candidates.keys())
    fuzzy_matches = difflib.get_close_matches(query, all_names, n=1, cutoff=0.7)
    if fuzzy_matches:
        return candidates[fuzzy_matches[0]]

    # Fuzzy match on aliases too
    alias_map = {}
    for name, data in candidates.items():
        for alias in data.get("aliases", []):
            alias_map[alias] = data
    fuzzy_alias = difflib.get_close_matches(query, list(alias_map.keys()), n=1, cutoff=0.7)
    if fuzzy_alias:
        return alias_map[fuzzy_alias[0]]

    # 6. If island was specified and nothing found, try island-agnostic search
    if island_input:
        return get_neighborhood_context(neighborhood_input, island_input=None)

    return None


def format_neighborhood_for_prompt(neighborhood_data, neighborhood_name):
    """
    Returns a formatted string ready to inject directly into a Claude prompt.
    """
    if not neighborhood_data:
        return ""

    name = neighborhood_name or "This neighborhood"
    island = neighborhood_data.get("island", "Hawaii")
    region = neighborhood_data.get("region", "")
    vibe = neighborhood_data.get("vibe", "")
    lifestyle = neighborhood_data.get("lifestyle", "")
    nearby = neighborhood_data.get("nearby", [])
    beaches = neighborhood_data.get("beaches", [])
    commute = neighborhood_data.get("commute", "")
    market_notes = neighborhood_data.get("market_notes", "")

    nearby_str = ""
    if nearby:
        if len(nearby) == 1:
            nearby_str = f"Key nearby landmarks and amenities include {nearby[0]}."
        elif len(nearby) == 2:
            nearby_str = f"Key nearby landmarks and amenities include {nearby[0]} and {nearby[1]}."
        else:
            nearby_str = f"Key nearby landmarks and amenities include {', '.join(nearby[:-1])}, and {nearby[-1]}."

    beaches_str = ""
    if beaches and not any(phrase in beaches[0].lower() for phrase in ["no beach", "no direct", "none", "no swim"]):
        if len(beaches) == 1:
            beaches_str = f"The nearest beach is {beaches[0]}."
        else:
            beaches_str = f"Nearby beaches include {', '.join(beaches[:-1])}, and {beaches[-1]}."

    region_str = f" in the {region} area" if region else ""

    parts = [
        f"NEIGHBORHOOD CONTEXT:",
        f"{name} is located on {island}{region_str}.",
        vibe,
        lifestyle,
    ]
    if nearby_str:
        parts.append(nearby_str)
    if beaches_str:
        parts.append(beaches_str)
    if commute:
        parts.append(f"Commute: {commute}")
    if market_notes:
        parts.append(f"From a real estate perspective: {market_notes}")
    parts.append(
        "This context should be used to ground every output in the specific reality of this neighborhood. "
        "Reference these details naturally — do not list them robotically."
    )

    return "\n".join(parts)
