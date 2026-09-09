"""
Comprehensive Geographical Data Dictionary for India
Contains All States, Union Territories, Hill Stations, Districts, Tehsils, Towns, Cities, and Villages
"""

INDIA_GEO_DATA = {
    "Andhra Pradesh": {
        "Anantapur": ["Anantapur City", "Dharmavaram", "Guntakal", "Hindupur", "Kadiri", "Tadipatri", "Penukonda", "Rayadurg", "Uravakonda", "Kalyandurg"],
        "Chittoor": ["Chittoor Town", "Tirupati", "Madanapalle", "Punganur", "Srikalahasti", "Nagari", "Palamaner", "Pileru", "Kuppam", "Puttoor"],
        "East Godavari": ["Kakinada", "Rajahmundry", "Amalapuram", "Samalkot", "Peddapuram", "Tuni", "Pithapuram", "Mandapeta", "Ramachandrapuram", "Razole"],
        "Guntur": ["Guntur City", "Tenali", "Narasaraopet", "Bapatla", "Mangalagiri", "Ponnur", "Repalle", "Sattenapalle", "Macherla", "Vinukonda"],
        "Krishna": ["Vijayawada", "Machilipatnam", "Gudivada", "Jaggayyapeta", "Nuzvid", "Nandigama", "Pedana", "Vuyyuru", "Kanchikacherla", "Avanigadda"],
        "Kurnool": ["Kurnool City", "Nandyal", "Adoni", "Yemmiganur", "Dhone", "Allagadda", "Nandikotkur", "Atmakur", "Banaganapalle", "Pattikonda"],
        "Prakasam": ["Ongole", "Chirala", "Markapur", "Kandukur", "Giddalur", "Kanigiri", "Podili", "Addanki", "Cumbum", "Darsi"],
        "Srikakulam": ["Srikakulam Town", "Palasa", "Amadalavalasa", "Narasannapeta", "Rajam", "Ichchapuram", "Tekkali", "Sompeta", "Hiramandalam", "Ponduru"],
        "Visakhapatnam": ["Visakhapatnam City", "Anakapalle", "Bheemunipatnam", "Gajuwaka", "Narsipatnam", "Chodavaram", "Yelamanchili", "Araku Valley (Hill Station)", "Paderu", "Subbavaram"],
        "Vizianagaram": ["Vizianagaram Town", "Bobbili", "Parvathipuram", "Salur", "Rajam", "Cheepurupalli", "Gajapathinagaram", "Srungavarapukota", "Kurupam", "Kothavalasa"],
        "West Godavari": ["Eluru", "Tadepalligudem", "Bhimavaram", "Tanuku", "Palakollu", "Narsapuram", "Jangareddigudem", "Kovvur", "Nidadavole", "Chintalapudi"],
        "YSR Kadapa": ["Kadapa City", "Proddatur", "Rayachoti", "Pulivendula", "Badvel", "Jammalamadugu", "Rajampet", "Kodur", "Mydukur", "Kamalapuram"]
    },
    "Arunachal Pradesh": {
        "Tawang": ["Tawang Town (Hill Station)", "Jang", "Lumla", "Mukto", "Zemithang"],
        "West Kameng": ["Bomdila (Hill Station)", "Dirang", "Rupa", "Bhalukpong", "Singchung"],
        "Lower Subansiri": ["Ziro (Hill Station)", "Hapoli", "Yachuli", "Raga"],
        "Papum Pare": ["Itanagar (Capital)", "Naharlagun", "Doimukh", "Nirjuli", "Yupia"]
    },
    "Assam": {
        "Cachar": ["Silchar", "Lakhipur", "Sonai", "Katigorah", "Dholai Village", "Udharbond", "Barkhola", "Bikrampur"],
        "Darrang": ["Mangaldoi", "Kharupetia", "Sipajhar", "Dalgaon", "Kalaigaon", "Patharighat", "Burha Village"],
        "Dima Hasao": ["Haflong (Hill Station)", "Mahur", "Maibang", "Umrangso", "Harangajao"],
        "Dibrugarh": ["Dibrugarh Town", "Tinsukia Road", "Chabua", "Naharkatia", "Namrup", "Moranhat", "Duliajan", "Tengakhat"],
        "Kamrup Metropolitan": ["Guwahati City", "Dispur", "North Guwahati", "Chandrapur", "Sonapur", "Azara", "Khanapara", "Beltola"],
        "Nagaon": ["Nagaon Town", "Hojai", "Lanka", "Kharupetia", "Raha Village", "Koliabor", "Samaguri", "Doboka"],
        "Sonitpur": ["Tezpur", "Dhekiajuli", "Biswanath Chariali", "Gohpur", "Jamugurihat", "Rangapara", "Bcharia", "Balipara"]
    },
    "Bihar": {
        "Bhagalpur": ["Bhagalpur City", "Naugachhia", "Sultanganj", "Kahalgaon", "Bihpur", "Sabour", "Colgong", "Pirpainti"],
        "Gaya": ["Gaya City", "Bodh Gaya", "Sherghati", "Tekari", "Manpur", "Imamganj", "Belaganj", "Wazirganj"],
        "Muzaffarpur": ["Muzaffarpur City", "Kanti", "Motipur", "Marwan", "Sakra", "Baruraj", "Sahebganj", "Kurhani"],
        "Patna": ["Patna City", "Danapur", "Phulwari Sharif", "Fatwah", "Masaurhi", "Barh", "Bikram", "Mokama", "Bihta", "Paliganj"],
        "Purnia": ["Purnia City", "Kasba", "Banmankhi", "Dhamdaha", "Baisa Village", "Amour", "Baisi", "Krityanand Nagar"],
        "Rohtas": ["Sasaram", "Dehri", "Bikramganj", "Nokha", "Chenari", "Sheosagar", "Kargahar", "Nasriganj"]
    },
    "Delhi NCR": {
        "Central Delhi": ["Connaught Place", "Karol Bagh", "Paharganj", "Daryaganj", "Rajendra Nagar", "Civil Lines South", "Patel Nagar"],
        "East Delhi": ["Laxmi Nagar", "Mayur Vihar", "Preet Vihar", "Shahdara", "Patparganj", "Gita Colony", "I.P. Extension", "Anand Vihar"],
        "New Delhi": ["Chanakyapuri", "Vasant Vihar", "Lodi Road", "Barakhamba", "RK Puram", "Mandi House", "Khan Market", "Sarojini Nagar"],
        "North Delhi": ["Civil Lines", "Kashmere Gate", "Model Town", "Sadabazar", "Timarpur", "Gulabi Bagh", "Shakti Nagar", "Vijay Nagar"],
        "North East Delhi": ["Seelampur", "Yamuna Vihar", "Karawal Nagar", "Nand Nagri", "Dilshad Garden", "Gokulpuri", "Shahdara North", "Mustafabad"],
        "North West Delhi": ["Rohini", "Pitampura", "Shalimar Bagh", "Kanjhawala", "Narela", "Bawana", "Ashok Vihar", "Mangolpuri"],
        "South Delhi": ["Saket", "Hauz Khas", "Greater Kailash", "Malviya Nagar", "Mehrauli", "Green Park", "Chhattarpur", "Vasant Kunj South"],
        "South East Delhi": ["Lajpat Nagar", "Okhla", "Nehru Place", "Kalka Mandir", "Badarpur", "Jamia Nagar", "Sarita Vihar", "Govindpuri"],
        "South West Delhi": ["Dwarka", "Vasant Kunj", "Najafgarh", "Palam", "Bijwasan", "Kapashere", "Mahipalpur", "Chhawla"],
        "West Delhi": ["Rajouri Garden", "Punjabi Bagh", "Janakpuri", "Tilak Nagar", "Paschim Vihar", "Vikas Puri", "Uttam Nagar", "Kirti Nagar"],
        "Gurugram (NCR)": ["DLF Phase 1-5", "Cyber City", "Sohna Road", "Manesar", "Sector 14-56", "Palam Vihar", "Golf Course Road", "Badshahpur"],
        "Noida (NCR)": ["Sector 15-137", "Greater Noida", "Noida Extension", "Dadri", "Jewar", "Surajpur", "Kasna", "Knowledge Park"]
    },
    "Himachal Pradesh (Hill State - Landslide Prone)": {
        "Shimla": ["Shimla City (Hill Station)", "Kufri", "Mashobra", "Narkanda", "Chail", "Rampur Bushahr", "Theog", "Rohru", "Jubbal", "Kotkhai"],
        "Kullu": ["Kullu Town", "Manali (Hill Station)", "Solang Valley", "Kasol", "Naggar", "Banjar", "Anni", "Nirmand"],
        "Kangra": ["Dharamshala (Hill Station)", "McLeod Ganj", "Palampur", "Kangra Town", "Nurpur", "Jawali", "Dehra Gopipur", "Baijnath"],
        "Solan": ["Solan Town", "Kasauli (Hill Station)", "Chail Road", "Kandaghat", "Arki", "Nalagarh", "Baddi"],
        "Chamba": ["Dalhousie (Hill Station)", "Chamba Town", "Khajjiar", "Bharmour", "Pangi", "Salooni", "Chowari"],
        "Mandi": ["Mandi City", "Sundernagar", "Jogindernagar", "Sarkaghat", "Karsog", "Pandoh", "Padhar"],
        "Lahaul and Spiti": ["Keylong", "Kaza", "Tabo", "Udaipur Lahaul", "Sissu", "Jispa"]
    },
    "Jammu & Kashmir & Ladakh (Landslide Prone)": {
        "Srinagar": ["Srinagar City", "Dal Lake Belt", "Hazratbal", "Nishat", "Shalimar", "Lal Chowk"],
        "Anantnag": ["Pahalgam (Hill Station)", "Anantnag Town", "Bijbehara", "Kokernag", "Verinag", "Mattan"],
        "Baramulla": ["Gulmarg (Hill Station)", "Baramulla Town", "Sopore", "Pattan", "Tangmarg", "Uri Landslide Zone"],
        "Ganderbal": ["Sonamarg (Hill Station)", "Ganderbal Town", "Kangan", "Gund"],
        "Leh (Ladakh)": ["Leh Town (High Altitude)", "Nubra Valley", "Diskit", "Pangong Belt", "Khardung La Route"],
        "Kargil (Ladakh)": ["Kargil Town", "Drass (Coldest Zone)", "Zanskar", "Sanku"]
    },
    "Karnataka": {
        "Bagalkot": ["Bagalkot Town", "Badami", "Ilkal", "Jamkhandi", "Mudhol", "Hunagund", "Guledgudda", "Bilgi"],
        "Ballari": ["Ballari City", "Hosapete", "Kampli", "Siruguppa", "Sandur", "Kudligi", "Kurugodu"],
        "Belagavi": ["Belagavi City", "Gokak", "Chikkodi", "Bailhongal", "Athani", "Khanapur", "Sankeshwar", "Ramdurg", "Saundatti"],
        "Bengaluru Rural": ["Dharmapuri Road", "Devanahalli", "Doddaballapura", "Hosakote", "Nelamangala", "Vijayapura Rural"],
        "Bengaluru Urban": ["Indiranagar", "Koramangala", "Whitefield", "Jayanagar", "Electronic City", "Yelahanka", "Marathahalli", "BTM Layout", "Hebbal", "Rajajinagar", "Malleshwaram", "Banashankari"],
        "Chikmagalur (Hill Station Zone)": ["Chikmagalur Town (Hill Station)", "Kudremukh", "Mullayanagiri Slope", "Bababudangiri", "Kadur", "Tarikere", "Mudigere", "Sringeri", "Koppa"],
        "Kodagu (Coorg - Landslide Prone)": ["Madikeri (Hill Station)", "Somwarpet", "Virajpet", "Kushalnagar", "Gonikoppal", "Bhagamandala Slope", "Talakaveri"],
        "Dakshina Kannada": ["Mangaluru City", "Bantwal", "Puttur", "Belthangady", "Sullia", "Moodabidri", "Kadaba"],
        "Mysuru": ["Mysuru City", "Nanjangud", "Hunsur", "KR Nagar", "T Narasipura", "Periyapatna", "H D Kote", "Saragur"],
        "Shivamogga": ["Shivamogga City", "Bhadravathi", "Sagara", "Shikaripura", "Thirthahalli", "Hosangar", "Soraba"]
    },
    "Kerala (Hilly & Landslide Prone)": {
        "Idukki (Severe Landslide Zone)": ["Munnar (Hill Station)", "Devikulam", "Kattappana", "Adimali", "Nedumkandam", "Peermade", "Cheruthoni", "Rajamala", "Vagamon (Hill Station)"],
        "Wayanad (Severe Landslide Zone)": ["Kalpetta (Hill Station)", "Meppadi (Landslide Zone)", "Chooralmala Slope", "Mundakkai Village", "Vythiri", "Sulthan Bathery", "Lakkidi", "Mananthavady"],
        "Ernakulam": ["Kochi City", "Aluva", "Angamaly", "Perumbavoor", "Muvattupuzha", "Tripunithura", "Kalamassery", "Kothamangalam", "North Paravur"],
        "Pathanamthitta": ["Pathanamthitta Town", "Tiruvalla", "Adoor", "Ranni", "Pandalam", "Kozhencherry", "Sabarimala Slope Zone"],
        "Thiruvananthapuram": ["Thiruvananthapuram City", "Ponmudi (Hill Station)", "Neyyattinkara", "Attingal", "Varkala", "Nedumangad"]
    },
    "Maharashtra": {
        "Ahmednagar": ["Ahmednagar City", "Rahata", "Shirdi", "Sangamner", "Kopargaon", "Shrirampur", "Rahuri", "Nevasa", "Pathardi", "Parner", "Akole"],
        "Kolhapur": ["Kolhapur City", "Ichalkaranji", "Kagal", "Jaysingpur", "Gadhinglaj", "Radhanagari", "Panhala (Hill Station)", "Shahuwadi"],
        "Mumbai City": ["Marine Lines", "Colaba", "Fort", "Dadra", "Byculla", "Worli", "Dharavi", "Girgaon", "Parel", "Sion", "Wadala"],
        "Mumbai Suburban": ["Andheri West", "Bandra East", "Borivali", "Goregaon", "Juhu", "Malad", "Kurla", "Ghatkopar", "Mulund", "Chembur", "Powai"],
        "Nashik": ["Nashik City", "Malegaon", "Sinnar", "Igatpuri (Hill Station)", "Trimbakeshwar", "Satana", "Kalwan"],
        "Navi Mumbai": ["Vashi", "Nerul", "Belapur", "Kharghar", "Panvel", "Airoli", "Ghansoli", "Seawoods", "Kamothe"],
        "Pune (Ghats & Landslide Prone)": ["Shivajinagar", "Lonavala (Hill Station)", "Khandala (Hill Station)", "Lavasa", "Kothrud", "Hadapsar", "Pimpri-Chinchwad", "Baramati", "Bhor Ghat"],
        "Raigad (Ghats & Landslide Prone)": ["Alibag", "Matheran (Hill Station)", "Mahad (Irshalwadi Slope Zone)", "Karjat", "Mangaon", "Roha", "Pen", "Khopoli"],
        "Ratnagiri": ["Ratnagiri Town", "Chiplun", "Khed", "Rajapur", "Guhagar", "Dapoli (Hill Station)"],
        "Satara (Ghats & Landslide Prone)": ["Satara City", "Mahabaleshwar (Hill Station)", "Panchgani (Hill Station)", "Karad", "Wai", "Patan Satara", "Koregaon"],
        "Sindhudurg": ["Sawantwadi", "Amboli (Hill Station - High Rainfall)", "Malvan", "Kankavli", "Vengurla", "Kudal"],
        "Thane": ["Thane City", "Kalyan-Dombivli", "Bhiwandi", "Ulhasnagar", "Ambernath", "Murbad", "Shahapur Ghat Zone"]
    },
    "Meghalaya (High Rainfall & Landslide Prone)": {
        "East Khasi Hills": ["Shillong (Capital Hill Station)", "Cherrapunji / Sohra (Extreme Rain)", "Mawsynram (Highest Rainfall Zone)", "Pynursla", "Smit"],
        "West Jaintia Hills": ["Jowai", "Dawki", "Amlarem", "Thadlaskein"],
        "Ri-Bhoi": ["Nongpoh", "Umsning", "Byrnihat"],
        "West Garo Hills": ["Tura", "Phulbari", "Dalu", "Rongram"]
    },
    "Odisha": {
        "Balasore": ["Balasore Town", "Bhadrak Border", "Jaleswar", "Soro", "Nilagiri"],
        "Cuttack": ["Cuttack City", "Choudwar", "Banki", "Athagarh", "Salepur"],
        "Ganjam": ["Berhampur City", "Chhatrapur", "Hinjilicut", "Aska", "Bhanjanagar", "Gopalpur"],
        "Koraput (Hilly Zone)": ["Koraput Town (Hill Station)", "Jeypore", "Sunabeda", "Damanjodi", "Semiliguda"],
        "Puri": ["Puri City", "Konark", "Nimapada", "Pipili", "Kakatpur"]
    },
    "Rajasthan": {
        "Sirohi (Hill Station Zone)": ["Mount Abu (Hill Station)", "Sirohi Town", "Abu Road", "Sheoganj", "Reodar"],
        "Jaipur": ["Jaipur City", "Sanganer", "Amer", "Chomu", "Bagru", "Kotputli"],
        "Udaipur": ["Udaipur City", "Salumbar", "Fatehnagar", "Mavli", "Gogunda"]
    },
    "Sikkim (Severe Landslide Prone Hill State)": {
        "East Sikkim": ["Gangtok (Capital Hill Station)", "Ranipool", "Singtam", "Rongli", "Pakyong"],
        "West Sikkim": ["Pelling (Hill Station)", "Geyzing", "Soreng", "Yuksom", "Dentam"],
        "North Sikkim (Severe Landslides)": ["Lachung (Hill Station)", "Lachen", "Mangan", "Chungthang", "Dzongu"],
        "South Sikkim": ["Namchi (Hill Station)", "Ravangla", "Jorethang", "Melli"]
    },
    "Tamil Nadu": {
        "Nilgiris (Severe Landslide Zone)": ["Ooty / Udhagamandalam (Hill Station)", "Coonoor (Hill Station)", "Kotagiri (Hill Station)", "Gudalur", "Wellington", "Manjoor"],
        "Dindigul (Hill Station Zone)": ["Kodaikanal (Hill Station)", "Dindigul Town", "Palani", "Oddanchatram", "Nattam"],
        "Chennai": ["Mylapore", "T. Nagar", "Velachery", "Adyar", "Anna Nagar", "Tambaram", "Avadi"],
        "Coimbatore": ["Coimbatore City", "Pollachi", "Valparai (Hill Station)", "Mettupalayam", "Sulur"]
    },
    "Uttarakhand (Severe Landslide Prone Hill State)": {
        "Dehradun": ["Mussoorie (Hill Station)", "Dehradun City", "Rishikesh", "Vikasnagar", "Chakrata (Hill Station)", "Clement Town"],
        "Nainital": ["Nainital (Hill Station)", "Haldwani", "Ramnagar", "Bhowali", "Bhimtal", "Mukteshwar (Hill Station)"],
        "Almora": ["Almora Town (Hill Station)", "Ranikhet (Hill Station)", "Kausani (Hill Station)", "Dwarahat", "Chaukhutia"],
        "Chamoli (Severe Landslide Zone)": ["Joshimath (Landslide Subsidence Zone)", "Gopeshwar", "Badrinath Route", "Auli (Hill Station)", "Karnaprayag", "Pipalkoti"],
        "Uttarkashi": ["Uttarkashi Town", "Barkot", "Gangotri Route", "Yamunotri Route", "Purola"],
        "Pithoragarh": ["Pithoragarh Town", "Dharchula (Landslide Zone)", "Didihat", "Munsiyari (Hill Station)", "Berinag"],
        "Tehri Garhwal": ["New Tehri", "Dhanaulti (Hill Station)", "Narendra Nagar", "Chamba Tehri", "Devprayag"]
    },
    "West Bengal": {
        "Darjeeling (Severe Landslide Prone Hill District)": [
            "Darjeeling Town (Hill Station)", "Kalimpong (Hill Station)", "Kurseong (Hill Station)", 
            "Mirik (Hill Station)", "Sukhiapokhri", "Ghoom (High Altitude)", "Lava", "Lolegaon", 
            "Pedong", "Rimbick", "Bijanbari", "Sukna Slope Zone"
        ],
        "Jalpaiguri (Dooars & Foothills)": ["Jalpaiguri Town", "Dhupguri", "Malbazar", "Mainaguri", "Banarhat", "Nagrakata Foothills", "Matiali"],
        "Kolkata": ["Salt Lake City", "Park Circus", "Alipore", "Tollygunge", "Dum Dum", "Behala", "Jadavpur", "Garia", "Bhowanipore"],
        "North 24 Parganas": [
            "Habra", "Ashoknagar", "Barasat", "Barrackpore", "Bidhannagar (Salt Lake)", "Rajarhat / New Town", "Madhyamgram", 
            "Bangaon", "Basirhat", "Kanchrapara", "Naihati", "Bhatpara", "Panihati", "Khardaha", "Halisahar", "Garulia", 
            "North Barrackpore", "Titagarh", "Kamarhati", "Baranagar", "New Barrackpore", "Deganga", "Baduria", "Gaighata", 
            "Amdanga", "Minakhan", "Haroa", "Hingalganj", "Hasnabad", "Swarupnagar", "Sandeshkhali"
        ],
        "South 24 Parganas": [
            "Canning Village", "Diamond Harbour", "Kakdwip", "Baruipur", "Sonarpur", "Gosaba Island", "Bhangar", 
            "Kulpi", "Namkhana", "Budge Budge", "Pujali", "Maheshtala", "Bishnupur S24P", "Magrahat", "Jaynagar", 
            "Mathurapur", "Basanti", "Patharpratima", "Sagar Island"
        ]
    }
}

FACILITY_TYPES = [
    "School",
    "College",
    "Hospital",
    "Community Center",
    "Stadium",
    "Building"
]
