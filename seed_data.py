"""Question data for the 10 Music Ability Assessment sets (transcribed from the PDF).

build_all() returns a flat list of question dicts ready to insert into the DB.
Options are written as "a|b|c" strings to keep this file readable.
"""


def L(s):
    return [x.strip() for x in s.split("|")]


YN = ["Correct", "Incorrect"]
SECTIONS = {1: "Q1 Basic", 2: "Q2 Intermediate", 3: "Q3 Music Enthusiast",
            4: "Q4 Professional", 5: "Q5 Producer Level"}

BASE = {
    "1.1": "What is the main emotional impression of this music excerpt?",
    "1.2": "What emotional impression does this music excerpt convey?",
    "1.3": "Which image or atmosphere does this music excerpt most closely evoke?",
    "1.4": "Which scenario is this music excerpt most suitable for?",
    "1.5": "At which second does the chorus first appear in this music excerpt?",
    "1.6": "Which scenario is this music excerpt most suitable for?",
    "1.7": "How would you describe this singer's vocal timbre?",
    "1.8": "What is the most prominent timbral characteristic of this vocal excerpt?",
    "1.9": "Which term best describes this voice?",
    "1.10": "What are the characteristics of this timbre?",
    "2.1": "Which top-level genre is this song most likely to belong to?",
    "2.2": "Which top-level genre is this song most likely to belong to?",
    "2.3": "Which top-level genre is this song most likely to belong to?",
    "2.4": "Which top-level genre is this song most likely to belong to?",
    "2.5": "In this audio, what is the main solo instrument?",
    "2.6": "In this audio, what is the most prominent instrument?",
    "2.7": "In this audio, what type of main solo instrument carries the melody?",
    "2.9": "Are there vocal harmonies in the music?",
    "3.1": "What is the time signature of this music excerpt?",
    "3.2": "What is the time signature of this music excerpt?",
    "3.3": "What is the tempo range of this music excerpt?",
    "3.4": "What is the tempo range of this music excerpt?",
    "3.5": "What is the most distinctive solo instrument in this music excerpt?",
    "3.6": "Which style does this rhythmic pattern most closely match?",
}

BESIDES = "In this audio, what is the most prominent instrument besides the drums?"
BEING = "In this audio, what is the main instrument being played?"

# ---- per-set option lists -------------------------------------------------
D = {}
D[1] = {
    "1.1": "dreamy, floating|sorrowful, grief-stricken|rousing, uplifting|calm, relaxed",
    "1.2": "romantic, flirtatious|frightening, oppressive|happy, fun|lonely, spacious",
    "1.3": "tech product launch|romantic confession|war / epic|nightclub dancing",
    "1.4": "beach vacation|tech product launch|horror / thriller|children's animation",
    "1.5": "3 sec|24 sec|44 sec|1:08",
    "1.6": "street basketball|yoga meditation|church service|family advertisement",
    "1.7": "full-bodied and powerful|clear and thin|breathy, gentle, and slightly husky|deep and rough",
    "1.8": "obvious falsetto|husky and thick|prominent nasal resonance|deep and rough",
    "1.9": "magnetic and warm|strong airy quality|sharp and piercing|obvious crying tone",
    "1.10": "strong grainy texture|childlike and youthful|airy, ethereal, and illusory|clear, bright, and soft",
    "2.1": "Electronic|Rap|Pop|Jazz|Classical|Rock",
    "2.2": "Rap|Jazz|Classical|Folk|Electronic|Rock",
    "2.3": "Electronic|Rock|Rap|Pop|Folk|Classical",
    "2.4": "Rap|Jazz|Classical|Folk|Electronic|Rock",
    "2.5": "Piano|Chinese guzheng|Acoustic guitar|Accordion",
    "2.6": "Organ|808 bass|Piano|Flute",
    "2.7": "Violin|Marimba|Brass section|808 bass",
    "3.1": "7/8|3/4|4/4|2/4",
    "3.2": "2/4|4/4|5/4|3/4",
    "3.3": "150+|40-60|60-80|100-120|120-150",
    "3.4": "150+|50-70|70-90|100-120|120-150",
    "3.5": "Chinese bamboo flute|Bandoneon accordion (Bandoneón)|steelpan|harmonica",
    "3.6": "Dance Pop|Disco|Trap|Metal Rock|Samba|House|UK Garage|Funk|Reggaeton|Jersey Club",
    "3.7": "Punk Rock|Post-rock|Grunge|Progressive Rock|Britpop|Hard Rock|Garage Rock",
    "3.9": "backing vocals|electric guitar|harmonica|flute|conga drums|sitar",
    "4.1": "Drop|Buildup|Chorus|Interlude",
    "4.4": "Synth Pad|Piano|Drums|Bass|Cello",
    "4.5": "Drum kit|Electronic drums|Piano|Woodwind section|Brass section|String section|Chinese erhu|Chinese dizi",
}
D[2] = {
    "1.1": "anxious, uneasy|warm, healing|solemn, dignified|playful, comic",
    "1.2": "mysterious, dark|calm, relaxed|angry, explosive|rousing, uplifting",
    "1.3": "sensual and flirtatious|cyberpunk night city|pastoral scenery|wedding entrance",
    "1.4": "high-intensity fitness workout|fashion advertisement|march|street skateboarding",
    "1.5": "13 sec|35 sec|44 sec|1:06",
    "1.6": "classical concert|street basketball / streetwear advertisement|yoga meditation|church service",
    "1.7": "rough and husky|prominent nasal resonance|airy, ethereal, and illusory|explosive and powerful",
    "1.8": "dreamy breathiness|clear and gentle|smoky and relaxed voice|full-bodied and low",
    "1.9": "breathy and dreamy|prominent nasal resonance|sharp and piercing|sensual and laid-back",
    "1.10": "obvious falsetto transition|full-bodied and powerful|magnetic and low|obvious bel canto technique",
    "2.1": "Jazz|Classical|Electronic|Rock|Rap|Pop",
    "2.2": "Jazz|Classical|Pop|Electronic|Rock|Rap",
    "2.3": "Electronic|Rock|Rap|Folk|Classical|Jazz",
    "2.4": "Jazz|Classical|Rock|Electronic|Rap|Pop",
    "2.5": "Guitar|Piano|Violin|Synthesizer",
    "2.6": "Piano|Harmonica|String section|Drum kit",
    "2.7": "Piano|Electric guitar|Synthesizer|Flute",
    "3.1": "4/4|3/4|7/8|5/4",
    "3.2": "5/4|3/4|2/4|4/4",
    "3.3": "120-140|50-70|70-90|90-120|140+",
    "3.4": "70-90|90-120|120-140|140+|50-70",
    "3.5": "steelpan|harmonica|mandolin|flute",
    "3.6": "Big band|Bebop|Disco|Blues Rock|2-step|Samba|Bossa Nova|Trap|Reggaeton|Afrobeat",
    "3.7": "House|Techno|Future Bass|Drum and Bass|Synth-pop|Trap|Ambient",
    "3.9": "electric guitar|synth piano|drum kit|808 drums|synth pad|synth bass",
    "4.1": "Pre-chorus|Outro|Chorus|Breakdown",
    "4.4": "Electric guitar|String section|Drums|Electric bass|Piano",
    "4.5": "Drum kit|Electronic drums|Acoustic guitar|electric bass|synth bass|synth arp|synth lead|synth guitar",
}
D[3] = {
    "1.1": "tense, uneasy|lonely, spacious|angry, explosive|lighthearted, cheerful",
    "1.2": "sorrowful, grief-stricken|playful, comic|mysterious, dark|rousing, uplifting",
    "1.3": "children's animation|luxury advertisement|sports competition|nature documentary",
    "1.4": "sleep aid / relaxation|retro bar|high-intensity fitness workout|being alone late at night",
    "1.5": "15 sec|28 sec|39 sec|1:01",
    "1.6": "family advertisement|classical concert|street basketball / streetwear advertisement|beauty advertisement",
    "1.7": "magnetic and warm|clear and thin|childlike and youthful|sharp and piercing",
    "1.8": "magnetic and warm|sharp and piercing|obvious crying tone|breathy and dreamy",
    "1.9": "smoky and relaxed voice|sharp and piercing|high, bright, and highly penetrating|childlike and youthful",
    "1.10": "breathy and dreamy|bright and powerful|low and sensual|silky and rounded",
    "2.1": "Electronic|Rock|Rap|Pop|Jazz|Classical",
    "2.2": "Jazz|Alternative/Indie|Electronic|Rock|Rap|Classical",
    "2.3": "Rock|Rap|Pop|Jazz|Classical|Electronic",
    "2.4": "Electronic|Rock|Rap|Pop|Folk|Classical",
    "2.5": "Harmonica|Saxophone|Violin|Celesta",
    "2.6": "Electric guitar|String section|Celesta|Harmonica",
    "2.7": "Acoustic piano|Synthesizer|Trumpet|Harp",
    "3.1": "4/4|3/4|7/8|6/8",
    "3.2": "2/4|3/4|4/4|5/4",
    "3.3": "90-120|120-140|160+|70-90|50-70",
    "3.4": "50-70|70-90|90-120|120-150|150+",
    "3.5": "saxophone|suona|mandolin|morin khuur (horsehead fiddle)",
    "3.6": "Reggaeton|Dancehall|Afrobeat|Trap|Dubstep|Bossa Nova|House|Swing|New Jack Swing|Samba",
    "3.7": "Grunge|Post-rock|Progressive Rock|Punk Rock|Britpop|Metalcore|Shoegaze",
    "3.9": "string section|drum kit|electric guitar|flute|brass section|acoustic guitar",
    "4.1": "Bridge|Post-chorus|Pre-chorus|Chorus",
    "4.4": "Acoustic guitar|Piano|Electronic drums|Synthesizer|Cello",
    "4.5": "Drums|Piano|Acoustic guitar|Electric guitar|Woodwind section|Brass section|Electric bass|String section",
}
D[4] = {
    "1.1": "mysterious, dark|lighthearted, cheerful|lonely, spacious|angry, explosive",
    "1.2": "lighthearted, cheerful|anxious, uneasy|solemn, dignified|dreamy, floating",
    "1.3": "being alone late at night|children's animation|high-intensity fitness workout|wedding entrance",
    "1.4": "war / epic|wedding entrance|street skateboarding|cyberpunk night city",
    "1.5": "9 sec|43 sec|1:01|1:30",
    "1.6": "racing trailer|beauty advertisement|sci-fi game menu|church service",
    "1.7": "husky, smoky voice|breathy and thin|youthful and bright|childlike and youthful",
    "1.8": "low and husky|metallic and bright|clear and soft|smoky and relaxed voice",
    "1.9": "clear, bright, and soft|full-bodied and low|high and bright|obvious crying tone",
    "1.10": "smoky and relaxed voice|bright and penetrating|full-bodied and low|breathy and slightly husky",
    "2.1": "Jazz|Classical|Rap|Electronic|Rock|Pop",
    "2.2": "Electronic|Rock|Rap|Pop|Classical|Jazz",
    "2.3": "Jazz|Classical|Rock|Electronic|Rap|Soul",
    "2.4": "Jazz|Classical|Electronic|Rock|Rap|Folk",
    "2.5": "Cello|Trumpet|Tuba|Pipa",
    "2.6": "Chinese sheng|Marimba|Electric bass|Organ",
    "2.7": "Clarinet|Saxophone|Electric guitar|String section",
    "3.1": "4/4|5/8|6/8|7/8",
    "3.2": "6/8|4/4|7/8|2/4",
    "3.3": "140+|70-90|50-70|90-120|120-140",
    "3.4": "70-90|120-150|150+|90-120|50-70",
    "3.5": "Bandoneon accordion (Bandoneón)|saxophone|flute|sitar",
    "3.6": "Bossa Nova|Funk|Reggae|Disco|Swing|Samba|Reggaeton|Blues Shuffle|Dancehall|Jersey Club",
    "3.7": "Folk Pop|Dream pop|Synth-pop|Dance-pop|City Pop|Britpop|Adult Contemporary",
    "3.9": "trumpet|drum kit|piano|flute|backing vocals|acoustic guitar",
    "4.1": "Post-chorus|Breakdown|Buildup|Intro",
    "4.4": "Electric guitar|Bass|Electronic drums|Saxophone|String section",
    "4.5": "Drum kit|Electronic drums|Piano|Trombone|synth bass|electric bass|Violin|Acoustic guitar",
}
D[5] = {
    "1.1": "mysterious, dark|lighthearted, cheerful|romantic, flirtatious|angry, explosive",
    "1.2": "relaxed, quiet|tense, suspenseful|warm, healing|lighthearted, cheerful",
    "1.3": "nightclub dancing|horror / thriller|nature documentary|street skateboarding",
    "1.4": "morning commute|horror / thriller|wedding entrance|nightclub party",
    "1.5": "11 sec|23 sec|34 sec|1:08",
    "1.6": "outdoor travel vlog|suspense drama opening|beauty advertisement|awards ceremony",
    "1.7": "warm and low|breathy and dreamy|metallic and bright|obvious nasal tone",
    "1.8": "obvious falsetto|husky and thick|childlike and youthful|clear and thin",
    "1.9": "low and husky|clear, bright, and soft|childlike and youthful|powerful",
    "1.10": "laid-back and relaxed|metallic and bright|obvious crying tone|full-bodied and powerful",
    "2.1": "Electronic|Rock|Rap|Jazz|Folk|Classical",
    "2.2": "Jazz|Classical|Rap|Electronic|Rock|Pop",
    "2.3": "Jazz|Classical|Rap|Electronic|Rock|Pop",
    "2.4": "Electronic|Rock|Classical|Jazz|Soul|Rap",
    "2.5": "Electric guitar|English horn|808 bass|Celesta",
    "2.6": "Accordion|Synthesizer|Saxophone|Harp",
    "2.7": "Acoustic piano|Guzheng|Accordion|Electric piano",
    "3.1": "6/8|7/8|3/4|4/4",
    "3.2": "5/4|4/4|2/4|3/4",
    "3.3": "70-90|120-140|140+|90-120|50-70",
    "3.4": "90-120|50-70|70-90|120-150|150+",
    "3.5": "sitar|mandolin|suona|Bandoneon accordion (Bandoneón)",
    "3.6": "Jersey Club|Drum and Bass|UK Garage|2-step|House|Trap|Reggaeton|Dancehall|Funk|Disco",
    "3.7": "Boom Bap|Trap|G-funk|Drill|Lo-fi Hip Hop|Grime|Jazz Rap",
    "3.9": "trumpet|electric guitar|piano|flute|string section|Double Bass",
    "4.1": "Hook|Bridge|Intro|Verse",
    "4.4": "Electric guitar|Brass section|Electronic drums|Synth bass|Whistle",
    "4.5": "Drum kit|Electronic drums|synth keyboard|Electric guitar|synth woodwinds|synth trombone|Violin|synth trumpet",
}
D[6] = {
    "1.1": "rousing, uplifting|relaxed, quiet|tense, suspenseful|happy, fun",
    "1.2": "rousing, uplifting|sad, lyrical|angry, explosive|playful, comic",
    "1.3": "war / epic|beach vacation|horror / thriller|yoga exercise",
    "1.4": "nature documentary|march|nightclub party|horror / thriller",
    "1.5": "3 sec|28 sec|55 sec|1:23",
    "1.6": "beauty advertisement|awards ceremony|racing trailer|outdoor travel vlog",
    "1.7": "breathy, gentle, and slightly husky|obvious crying tone|bright and powerful|laid-back and soft",
    "1.8": "breathy and dreamy|metallic and bright|deep and rough|obvious crying tone",
    "1.9": "sharp and piercing|warm and rounded|breathy and dreamy|deep and rough",
    "1.10": "childlike and youthful|low and husky|clear, bright, and soft|obvious falsetto",
    "2.1": "Classical|Jazz|Folk|Electronic|Rock|Rap",
    "2.2": "Jazz|Classical|Rock|Electronic|Rap|Folk",
    "2.3": "Jazz|Classical|Pop|Electronic|Rock|Rap",
    "2.4": "Pop|Classical|Jazz|Electronic|Rock|Rap",
    "2.5": "Flute|Electric guitar|Bass|Marimba",
    "2.6": "Saxophone|808 bass|Flute|Tuba",
    "2.7": "Harp|Chinese erhu|Trumpet|Acoustic piano",
    "3.1": "4/4|3/4|6/8|7/8",
    "3.2": "2/4|3/4|4/4|5/4",
    "3.3": "70-90|90-120|120-140|140+|50-70",
    "3.4": "50-70|90-120|120-150|150+|70-90",
    "3.5": "trumpet|suona|steelpan|shamisen",
    "3.6": "Bebop|Boogie|Disco|UK Garage|Reggaeton|New Jack Swing|Mambo|Trap|House|Jersey Club",
    "3.7": "Acid jazz|Smooth jazz|Fusion jazz|Bebop|Bossa Nova|Big band|Ragtime",
    "3.9": "trumpet|electric guitar|drum kit|flute|synthesizer|bass",
    "4.1": "Outro|Chorus|Breakdown|Post-chorus",
    "4.4": "pad|arp|Electronic drum kit|pluck|Synth bass",
    "4.5": "Electric guitar|Acoustic guitar|electric bass|Double bass|synth organ|Brass section|String section|Drums",
}
D[7] = {
    "1.1": "sorrowful, grief-stricken|relaxed, quiet|anxious, uneasy|lighthearted, cheerful",
    "1.2": "tense, suspenseful|happy, fun|sad, lyrical|angry, explosive",
    "1.3": "pastoral scenery|cyberpunk night city|press conference|sleep aid / relaxation",
    "1.4": "sports competition|retro bar|tech product launch|sleep aid / relaxation",
    "1.5": "6 sec|18 sec|31 sec|1:05",
    "1.6": "classical concert|family advertisement|suspense drama opening|street basketball / streetwear advertisement",
    "1.7": "low and sensual|obvious falsetto|husky, raspy distortion|bright and powerful",
    "1.8": "breathy, gentle, and slightly husky|full-bodied and powerful|metallic texture|silky and rounded",
    "1.9": "full-bodied and powerful|ethereal and sacred|hoarse|warm and rounded",
    "1.10": "airy, ethereal, and illusory|magnetic and warm|prominent nasal resonance|low and sensual",
    "2.1": "Jazz|Classical|Rap|Electronic|Rock|Pop",
    "2.2": "Electronic|Rock|Rap|Pop|Jazz|Classical",
    "2.3": "Jazz|Classical|Electronic|Rock|Rap|Pop",
    "2.4": "Electronic|Rock|Rap|Pop|Classical|Jazz",
    "2.5": "Chinese erhu|Trumpet|Chinese pipa|Chinese dizi",
    "2.6": "Chinese bamboo flute|Electric guitar|Chinese erhu|Trumpet",
    "2.7": "Acoustic piano|Harp|Brass section|808 bass",
    "3.1": "4/4|3/4|6/8|7/8",
    "3.2": "2/4|3/4|4/4|5/4",
    "3.3": "140+|90-120|50-70|70-90|120-140",
    "3.4": "90-120|150+|120-150|50-70|70-90",
    "3.5": "Bandoneon accordion (Bandoneón)|morin khuur (horsehead fiddle)|oud|saxophone",
    "3.6": "Bossa Nova|Reggae|Afrobeat|Disco|Trap|Tango|Swing|Dancehall|House|Blues Shuffle",
    "3.7": "Trap|Boom Bap|Hardcore-rap|Grime|Drill|Melodic rap|Cloud Rap",
    "3.9": "backing vocals|electric guitar|harmonica|flute|conga drums|sitar",
    "4.1": "Interlude|Breakdown|Drop|Chorus",
    "4.4": "Synth Pad|Piano|Drums|Bass|Cello",
    "4.5": "Drum kit|Electronic drums|Piano|Woodwind section|Brass section|String section|Chinese erhu|Chinese dizi",
}
D[8] = {
    "1.1": "relaxed, quiet|dreamy, floating|angry, explosive|warm, healing",
    "1.2": "happy, fun|solemn, dignified|anxious, uneasy|lonely, spacious",
    "1.3": "children's animation|suspenseful chase|solemn ceremony|being alone late at night",
    "1.4": "sports competition|nightclub party|sleep aid / relaxation|march",
    "1.5": "0 sec|17 sec|27 sec|36 sec",
    "1.6": "yoga meditation|street basketball / streetwear advertisement|outdoor travel vlog|suspense drama opening",
    "1.7": "high and operatic|obvious falsetto|low and sensual|husky and thick",
    "1.8": "breathy high register|full-bodied and powerful|sharp and thin|laid-back and relaxed",
    "1.9": "silky and rounded|hoarse|childlike and youthful|obvious falsetto",
    "1.10": "low and husky|airy, ethereal, and illusory|high, bright, and highly penetrating|laid-back and relaxed",
    "2.1": "Rock|Rap|Pop|Jazz|Alternative/Indie|Electronic",
    "2.2": "Electronic|Rock|Folk|Jazz|Classical|Rap",
    "2.3": "Rap|Jazz|Classical|Folk|Electronic|Rock",
    "2.4": "Jazz|Classical|Pop|Electronic|Rock|Rap",
    "2.5": "Piano|Cello|Trumpet|Synthesizer",
    "2.6": "Trumpet|Trombone|Erhu|Marimba",
    "2.7": "Shakuhachi|Flute|Organ|Acoustic guitar",
    "3.1": "4/4|3/4|6/8|7/8",
    "3.2": "2/4|3/4|4/4|5/4",
    "3.3": "90-120|120-140|140+|50-70|70-90",
    "3.4": "140+|50-70|70-90|90-120|120-140",
    "3.5": "guzheng|shamisen|flute|muted trumpet",
    "3.6": "Modern Rock|Blues Shuffle|Swing|Funk|Bossa Nova|Reggae|Boogie|Disco|Samba|Trap",
    "3.7": "Techno|House|Drum and Bass|UK Garage|Future Bass|Brostep|Trance",
    "3.9": "electric guitar|synth piano|drum kit|808 drums|synth pad|synth bass",
    "4.1": "Drop|Buildup|Chorus|Interlude",
    "4.4": "Electric guitar|String section|Drums|Electric bass|Piano",
    "4.5": "Drum kit|Electronic drums|Acoustic guitar|electric bass|synth bass|synth arp|synth lead|synth guitar",
}
D[9] = {
    "1.1": "tense, suspenseful|happy, excited|sad, lyrical|calm, relaxed",
    "1.2": "dreamy, floating|angry, explosive|funny, comic|tense, suspenseful",
    "1.3": "romantic date|tense suspense|nightclub dancing|pastoral scenery",
    "1.4": "children's animation|being alone late at night|war / epic|beach vacation",
    "1.5": "9 sec|28 sec|37 sec|55 sec",
    "1.6": "church choir event|yoga meditation|street basketball / streetwear advertisement|sci-fi game",
    "1.7": "full-bodied and low|childlike and youthful|strong grainy texture|deep and rough",
    "1.8": "husky and gritty|airy and ethereal|sharp and powerful|laid-back and relaxed",
    "1.9": "hoarse|full-bodied and low|silky and rounded|sharp and piercing",
    "1.10": "low and husky|clear, bright, and sweet|sharp and powerful|rough, smoky voice",
    "2.1": "Jazz|Classical|Pop|Electronic|Rock|Rap",
    "2.2": "Jazz|Classical|Electronic|Rock|Rap|Pop",
    "2.3": "Electronic|Rap|Pop|Jazz|Classical|Rock",
    "2.4": "Jazz|Classical|Rap|Electronic|Rock|Folk",
    "2.5": "Accordion|Synthesizer|Flute|Electric guitar",
    "2.6": "Acoustic guitar|Electric guitar|Saxophone|Organ",
    "2.7": "Synthesizer|Erhu|Trumpet|Marimba",
    "3.1": "4/4|3/4|6/8|7/8",
    "3.2": "5/4|4/4|2/4|3/4",
    "3.3": "90-120|140+|120-140|50-70|70-90",
    "3.4": "50-70|70-90|90-120|150+|120-150",
    "3.5": "harmonica|flute|sitar|banjo",
    "3.6": "Bossa Nova|Samba|Jersey Club|Reggae|Smooth jazz|Blues Rock|Funk|Tango|Ragtime|House",
    "3.7": "Smooth jazz|Bebop|Big band|Ragtime|Fusion jazz|Bossa Nova|Acid jazz",
    "3.9": "string section|drum kit|electric guitar|flute|brass section|acoustic guitar",
    "4.1": "Pre-chorus|Outro|Chorus|Breakdown",
    "4.4": "Acoustic guitar|Piano|Electronic drums|Synthesizer|Cello",
    "4.5": "Drums|Piano|Acoustic guitar|Electric guitar|Woodwind section|Brass section|Electric bass|String section",
}
D[10] = {
    "1.1": "warm, healing|anxious, uneasy|playful, comic|solemn, dignified",
    "1.2": "gentle, intimate|angry, explosive|relaxed, quiet|playful, comic",
    "1.3": "romantic confession|suspenseful chase|beach vacation|retro bar",
    "1.4": "street skateboarding|nature documentary|church service|romantic confession",
    "1.5": "2 sec|17 sec|30 sec|1:01",
    "1.6": "sci-fi game menu|classical concert|family advertisement|church service",
    "1.7": "warm and soft|magnetic and low|breathy with strong grain|childlike and youthful",
    "1.8": "husky and thick|clear, bright, and soft|breathy and dreamy|sharp and powerful",
    "1.9": "sharp and piercing|silky and rounded|obvious crying tone|low and husky",
    "1.10": "warm and powerful|dreamy and ethereal|gentle with nasal resonance|sharp with chest resonance",
    "2.1": "Electronic|Rock|Rap|Pop|Classical|Jazz",
    "2.2": "Electronic|Rock|Rap|Jazz|Classical|Pop",
    "2.3": "Pop|Alternative/Indie|Jazz|Electronic|Rock|Rap",
    "2.4": "Rock|Rap|Pop|Jazz|Classical|Electronic",
    "2.5": "Marimba|Accordion|Erhu|Bass",
    "2.6": "Synthesizer|Bass|String section|Accordion",
    "2.7": "Synthesizer|Accordion|Violin|Piano",
    "3.1": "4/4|3/4|7/8|6/8",
    "3.2": "3/4|5/4|4/4|2/4",
    "3.3": "50-70|70-90|90-120|120-140|140+",
    "3.4": "120-150|150+|70-90|50-70|90-120",
    "3.5": "banjo|saxophone|sitar|cello",
    "3.6": "Trance|House|Mambo|Tango|Bossa Nova|Funk|Disco|Samba|EDM|Trap",
    "3.7": "Grunge|Post-rock|Punk|Metalcore|Britpop|Blues rock|Shoegaze",
    "3.9": "trumpet|drum kit|piano|flute|backing vocals|acoustic guitar",
    "4.1": "Bridge|Post-chorus|Pre-chorus|Chorus",
    "4.4": "Electric guitar|Bass|Electronic drums|Saxophone|String section",
    "4.5": "Drum kit|Electronic drums|Piano|Trombone|synth bass|electric bass|Violin|Acoustic guitar",
}

# ---- per-set variations ----------------------------------------------------
# c28: chorus time in Q2.8 | q210: Q2.10 statement | genre: Q3.7 style | q41: time span
# for Q4.1 (None = no span) | q46: section asked in Q4.6 | v51/v52/v53: Q5.1-5.3 variants
# lv: Q3.9 says "lead vocal" (True) or "vocals" | sa44: Q4.4 says "select all" | ex: Q5.5 example
META = {
    1: dict(c28=41, q210="The entire piece uses only three arrangement elements: drum kit, bass, and vocals.",
            genre="rock", q41="5s to 25s", q46="Bridge", v51="guitar", v52="reverb", v53="strings", lv=True, sa44=False,
            ex="A sus 4", p={"2.7": "In this audio, what type of main solo instrument carries the melody besides the drums?"}),
    2: dict(c28=28, q210="The entire piece uses only three arrangement elements: vocals, drums, and synthesizer.",
            genre="electronic", q41="28s to 42s", q46="Bridge", v51="pad", v52="vocoder", v53="gA", lv=False, sa44=False,
            ex="D maj 9", p={"2.7": "In this audio, what type of main solo instrument carries the melody besides the drums?"}),
    3: dict(c28=37, q210="The entire piece uses only two arrangement elements: piano and vocals.",
            genre="rock", q41="31s to 44s", q46="Pre-chorus", v51="bass", v52="reverb", v53="gB", lv=False, sa44=True,
            ex="A sus 4", p={"2.6": BESIDES, "2.7": "In this audio, what type of instrument mainly carries the melody?"}),
    4: dict(c28=36, q210="The entire piece uses only two arrangement elements: piano and strings.",
            genre="pop", q41=None, q46="Pre-chorus", v51="pluck", v52="vocoder", v53="strings", lv=True, sa44=False,
            ex="D maj 9", p={}),
    5: dict(c28=47, q210="Aside from vocals, the entire piece uses only two arrangement elements: drums and piano.",
            genre="rap", q41="8s to 29s", q46="Pre-chorus", v51="guitar", v52="reverb", v53="gA", lv=True, sa44=False,
            ex="A sus 4", p={"2.5": BEING, "2.6": BESIDES}),
    6: dict(c28=28, q210="The entire piece uses only two arrangement elements: acoustic guitar and vocals.",
            genre="jazz", q41="24s to 36s", q46="Bridge", v51="pad", v52="vocoder", v53="gB", lv=False, sa44=False,
            ex="D maj 9", p={"2.6": BESIDES}),
    7: dict(c28=34, q210="The entire piece uses only three arrangement elements: drums, guitar, and synthesizer.",
            genre="rap", q41="27s to 47s", q46="Bridge", v51="bass", v52="reverb", v53="strings", lv=True, sa44=False,
            ex="A sus 4", p={"2.5": BEING, "2.6": "In this audio, what is the most prominent solo instrument besides the drums?",
                               "2.7": "In this audio, what type of solo instrument carries the melody?"}),
    8: dict(c28=16, q210="The entire piece uses only two arrangement elements: piano and drums.",
            genre="electronic", q41="5s to 25s", q46="Bridge", v51="pluck", v52="vocoder", v53="gA", lv=False, sa44=False,
            ex="D maj 9", p={"1.5": "At which second does the chorus appear in this music excerpt?"}),
    9: dict(c28=57, q210="The entire piece uses only two arrangement elements: guitar and strings.",
            genre="jazz", q41="28s to 42s", q46="Bridge", v51="guitar", v52="reverb", v53="gB", lv=False, sa44=True,
            ex="A sus 4", p={"1.3": "What mood does this music excerpt create?", "2.5": BEING, "2.6": BESIDES}),
    10: dict(c28=27, q210="The entire piece uses only two arrangement elements: harp and flute.",
             genre="rock", q41="31s to 44s", q46="Pre-chorus", v51="pad", v52="vocoder", v53="strings", lv=True, sa44=False,
             ex="D maj 9", p={"2.6": BESIDES}),
}

V51 = {
    "guitar": ("Listen to the electric-guitar timbre in the clip. Which professional description is the most accurate? (Headphones recommended.)",
               "single-coil electric guitar clean tone, clear attack and bright high frequencies|Humbucker overdrive electric guitar, thick mids and long sustain|Nylon-string guitar, soft attack and warm body resonance|Single-coil electric guitar + tremolo pedal, extremely grainy sound texture"),
    "pad": ("Listen to the background pad timbre in the clip. Which professional description is the most accurate? (Headphones recommended.)",
            "Short attack, strong and forceful attack transient|Slow attack, wide, and rich across the frequency spectrum|The base waveform is a sawtooth wave, with an obvious overdrive or distortion character|The base waveform is a square wave, sustained and forceful"),
    "bass": ("Listen to the bass timbre in the clip. Which professional description is the most accurate? (Headphones recommended.)",
             "Fretless acoustic bass, soft timbre|synth sub bass, round and weighty|distorted synth bass, prominent and full in the mid-high frequencies|P-Bass played with a pick, strong attack"),
    "pluck": ("Listen to the synth pluck timbre in the clip. Which professional description is the most accurate? (Headphones recommended.)",
              "Slow attack, wide and airy|Attack is zero or very short, short and percussive, with a filter envelope|Long decay, obvious metallic overtones, and a glassy attack|No release, dry timbre, and obvious sawtooth wave character"),
}
V52 = {
    "reverb": "Heavy reverb (Reverb)|Heavy delay (Delay)|obvious Auto-Tune|Compressor|Pitch-based effect (Pitch)|Side-chain compression",
    "vocoder": "Obvious vocoder processing is used|Heavy delay (Delay)|obvious Auto-Tune|Compressor|Pitch-based effect (Pitch)|Side-chain compression",
}
V53 = {
    "strings": ("Listen to this string section, and select all string techniques that appear. (Multiple choice)",
                "legato bowing|spiccato|fast bowing|pizzicato|tremolo|minor-second trill|major-second trill|staccato bowing"),
    "gA": ("Listen to the solo electric guitar in this piece, and select all correct descriptions. (Multiple choice)",
           "Overdrive is used|Wah pedal is used|clean tone, using only the amp head|Obvious reverb|Obvious delay|Whammy bar / bending is used|With a Tremolo effect|With a fuzz effect|With a Rotary effect"),
    "gB": ("Listen to the solo electric guitar in this piece, and select all correct descriptions. (Multiple choice)",
           "With an octaver effect|String bending is used during the solo|With a light reverb effect|With a heavy delay effect|Tapping is used during the solo|Extensive whammy-bar use during the solo|With a phaser effect|Fuzz effect is used|With a rotary effect"),
}

QUALS = ["maj", "min", "dim", "aug", "sus", "mM", "ø", "add", "/"]
SECT7 = ["intro", "verse", "chorus", "bridge", "interlude", "outro"]
SECT11 = ["intro", "verse", "chorus", "pre-chorus", "post-chorus", "bridge", "solo", "interlude", "breakdown", "outro"]

N39 = "Rule: Missing selections or incorrect selections receive no credit."
N44 = "Rule: Each correctly selected option receives 5 points; selecting any other incorrect option results in 0 points."
N53 = "Rule: Each correct option receives 5 points; selecting any incorrect option results in 0 points for this question."
N42 = ("Rule: Use two blanks: the first blank is the letter-name key, and the second blank is minor or major. "
       "Incorrect entries receive no credit; full correctness receives 10 points.")
N43 = ("Rule: For the first and third blanks, choose the letter-name key; for the second and fourth blanks, choose "
       "major or minor. Full correctness receives 10 points; otherwise, no credit.")
N47 = ("Rule: Each correctly marked structure time and name receives 2.5 points; incorrect markings receive no credit. "
       "Enter times as minute and second numbers. Structural options include intro, verse, chorus, bridge, interlude, and outro.")
N48 = ("Rule: All chords correct receives 2.5 points; all scale degrees correct receives 2.5 points. "
       "Separate each item with a comma, e.g., Dm,G,C (accuracy only needs to identify major and minor triads) and "
       "ii,V,I (uppercase for major triads, lowercase for minor triads); incorrect formatting receives no credit.")
N38 = ("Rule: Enter the minutes and seconds in the two blanks respectively. Full credit is awarded if both are correct; "
       "answers within ±2 seconds are accepted.")
N46 = "Answers within ±2 seconds receive credit."
N54 = ("(When there is an obvious electric-guitar solo, mark it as an electric-guitar solo; solos by other instruments do "
       "not need to be counted. When the tempo, beat, or instrumentation is clearly reduced, mark it as a breakdown. "
       "Section starts and ends should be based on the vocals.) Rule: Each correctly marked structure time and name "
       "receives 2 points; incorrect markings receive no credit. A time error within 2 seconds is considered correct.")


def build_set(n):
    m, d = META[n], D[n]
    qs = []

    def add(qid, qtype, prompt, note="", options=None, cfg=None, points=1.0, unit=0.0):
        sec = int(qid.split(".")[0])
        qs.append(dict(set_no=n, qid="Q" + qid, section=SECTIONS[sec], qtype=qtype, prompt=prompt, note=note,
                       options=options or [], cfg=cfg or {}, points=points, unit=unit, ord=len(qs)))

    def prompt(qid):
        return m["p"].get(qid, BASE.get(qid))

    for i in range(1, 11):
        add("1.%d" % i, "single", prompt("1.%d" % i), options=L(d["1.%d" % i]))
    for i in range(1, 5):
        add("2.%d" % i, "single", prompt("2.%d" % i), options=L(d["2.%d" % i]))
    for i in (5, 6, 7):
        add("2.%d" % i, "single", prompt("2.%d" % i), options=L(d["2.%d" % i]))
    add("2.8", "single", "After listening to the full audio, you think the chorus enters around %d±2 seconds." % m["c28"], options=YN)
    add("2.9", "single", prompt("2.9"), options=YN)
    add("2.10", "single", m["q210"], options=YN)
    for i in range(1, 7):
        add("3.%d" % i, "single", prompt("3.%d" % i), options=L(d["3.%d" % i]))
    add("3.7", "single", "This is a %s-style song. Select the specific subgenre:" % m["genre"], options=L(d["3.7"]))
    add("3.8", "time_mmss", "Listen to the excerpt (about 2 minutes long). When does the chorus start? Enter the minutes and seconds.",
        note=N38, cfg={"tol": 2})
    add("3.9", "multi", "(Multiple select) Excluding the %s, select the instruments that appear in the song." %
        ("lead vocal" if m["lv"] else "vocals"), note=N39, options=L(d["3.9"]), cfg={"mode": "all"})

    q41 = "Which structural term best describes the section from %s in this audio?" % m["q41"] if m["q41"] \
        else "Which structural term best describes this audio?"
    add("4.1", "single", q41, options=L(d["4.1"]))
    add("4.2", "fields", "What key is this audio in? (Accuracy only needs to distinguish major vs. minor.)", note=N42,
        cfg={"mode": "all", "fields": [{"label": "Key", "kind": "text", "ph": "e.g. C, F#, Bb"},
                                       {"label": "Mode (major/minor)", "kind": "select", "opts": ["major", "minor"]}]},
        points=10)
    add("4.3", "fields", "What key does the song modulate from and to?", note=N43,
        cfg={"mode": "all", "fields": [{"label": "From: Key", "kind": "text", "ph": "e.g. C"},
                                       {"label": "Mode", "kind": "select", "opts": ["major", "minor"]},
                                       {"label": "To: Key", "kind": "text", "ph": "e.g. D"},
                                       {"label": "Mode", "kind": "select", "opts": ["major", "minor"]}]}, points=10)
    sel = "select all arrangement elements you can hear." if m["sa44"] else "select the arrangement elements you can hear."
    add("4.4", "multi", "Excluding the lead vocal and backing vocals, %s (Multiple choice)" % sel, note=N44,
        options=L(d["4.4"]), cfg={"mode": "per_correct"}, unit=5)
    add("4.5", "multi", "Excluding the lead vocal and backing vocals, select the arrangement elements you can hear. (Multiple choice)",
        note=N44, options=L(d["4.5"]), cfg={"mode": "per_correct"}, unit=5)
    add("4.6", "time_sec", "At what second does the %s section appear in the song? Fill in the number of seconds. %s" %
        (m["q46"], N46), cfg={"tol": 2})
    add("4.7", "table", "Listen to the clip, mark the start time of each section, and correctly fill in the name of each section.",
        note=N47, cfg={"rows": 8, "names": SECT7, "tol": 2}, unit=2.5)
    add("4.8", "fields", "This song is built mainly around a four-chord loop. Fill in the chord names in order, then use Roman numerals to indicate this harmonic progression.",
        note=N48, cfg={"mode": "each", "fields": [{"label": "Chord names (in order)", "kind": "text", "ph": "Dm,G,C"},
                                                  {"label": "Roman-numeral scale degrees", "kind": "text", "cs": True, "ph": "ii,V,I"}]},
        unit=2.5)

    p51, o51 = V51[m["v51"]]
    add("5.1", "single", p51, options=L(o51))
    add("5.2", "multi", "(Multiple choice) Which effects are mainly used to process the vocal in this audio?",
        options=L(V52[m["v52"]]), cfg={"mode": "all"})
    p53, o53 = V53[m["v53"]]
    add("5.3", "multi", p53, note=N53, options=L(o53), cfg={"mode": "per_correct"}, unit=5)
    add("5.4", "table", "Listen to the clip, mark the start time of each section, and correctly fill in the name of each section.",
        note=N54, cfg={"rows": 11, "names": SECT11, "tol": 2}, unit=2)
    add("5.5", "chords", "Listen carefully to the chord progression in this music, and write the exact chord names, such as "
        "“Am7 - Gsus4 - F#m7b5”. Chord 7: %s." % m["ex"],
        note="Rule: Each fully correct chord receives 4 points; incorrect chords receive no credit. Each chord uses three "
             "blanks: the letter name (A–G, with optional # or b), the quality, and the number.",
        cfg={"roots": list("ABCDEFG"), "acc": True, "quals": QUALS,
             "nums": ["2", "3", "4", "5", "6", "7", "9", "11", "13", "b5", "b11", "b13", "/"], "max": 12}, unit=4)
    add("5.6", "chords", "You are now the music director of a band. Listen carefully to the harmonic progression in this music, "
        "then generate a functional harmony chart for your band using Arabic numerals to indicate scale degrees. "
        "Chord qualities must be accurate (e.g., 2min9-5/7-1maj7).",
        note="Rule: Each correctly marked harmony receives 2 points. The first blank is the scale-degree number, the second "
             "is the quality, the third is the number.",
        cfg={"roots": ["1", "b2", "2", "b3", "3", "4", "#4", "5", "b6", "6", "b7", "7"], "acc": False, "quals": QUALS,
             "nums": ["2", "4", "5", "6", "7", "9", "11", "13", "b5", "b9", "#9", "#11", "b13"], "max": 12}, unit=2)
    return qs


def build_all():
    out = []
    for n in range(1, 11):
        out.extend(build_set(n))
    return out


if __name__ == "__main__":
    allq = build_all()
    print(len(allq), "questions")
    for n in range(1, 11):
        print(n, sum(1 for q in allq if q["set_no"] == n))
