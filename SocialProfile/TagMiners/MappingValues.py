LASTFM_TO_MCARS_MAP = {
    "concert->rock": ["punk", "pop rock", "alternative", "pop punk", "metal", "metalcore", "deathcore",
                      "hardcore", "post-hardcore", "screamo"],
    "concert->techno": ["house","deep","deep house","minimal", "edm","dance","electronic","goa","psytrance","trance","psychedelic trance"],
    "concert->hip-hop": ["pop", "hip hop", "rap"],
    "concert->classique": ["classic","classical","composers","piano"]
}


MOVIEDB_TO_MCARS_MAP = {
    "cinema->action" : ["action","adventure","crime","war","western"],
    "cinema->thriller" : ["thriller","mystery","crime","drama","horror"],
    "cinema->romance" : ["drama","romance"],
    "cinema->comedie" : ["comedy","family"]
}



EVENT_KEYWORDS = {
    "soiree" : [
        "soirée", "dj", "danse", "musique", "boite", "shot", "night", "party", "nocturne", "musicien", "club"
    ],

    "automobiles" : [
        "voiture" "camion", "automobile", "circuit", "course", "moto", "moteur", "tableau", "bord", "roue", "auto"
    ],

    "salon->livre" : [
        "salon", "livre", "lire", "lecture", "magazine", "bande", "dessiner", "compte", "roman", "litterature", "écrivain"

    ],

    "exposition->peintures" : [
        "exposition" "peintures", "tableau", "couleur", "art", "huile", "pinceau", "vernissage", "visiteur", "expo"
    ],


    "exposition->culturelle" : [
        "exposition" "culturelle", "culture", "région", "vernissage", "visiteur", "expo"
    ]
}

LINK_TO_MCARS = {
    "soundcloud": ["soiree"],
    "deezer": ["soiree"],
    "spotify": ["soiree"],
}