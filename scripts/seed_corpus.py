#!/usr/bin/env python3
"""Seed the database with the phrasal verbs corpus (Tiers 1, 2, 3)."""

import asyncio
import sys
from pathlib import Path

# Ensure app is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.expression import Expression

# Import all model modules so SQLAlchemy can resolve relationship string references
# (circular refs: Expression→UserMemory, UserMemory→User, etc.)
import app.models.user  # noqa: F401
import app.models.memory  # noqa: F401
import app.models.session  # noqa: F401
import app.models.mistake  # noqa: F401

# ─── TIER 1 — Ultra-fréquents ───

TIER1_GET = [
    ("get up", "se lever"),
    ("get down", "s'abaisser / déprimer"),
    ("get on", "monter dans / s'entendre avec"),
    ("get off", "descendre de / s'en tirer"),
    ("get out", "sortir / quitter"),
    ("get in", "entrer / rentrer"),
    ("get over", "surmonter / se remettre de"),
    ("get through", "traverser une épreuve / joindre qqn"),
    ("get away", "s'échapper"),
    ("get away with", "faire sans être puni"),
    ("get back", "revenir / récupérer"),
    ("get back to", "reprendre contact"),
    ("get along", "s'entendre avec qqn"),
    ("get around", "contourner / circuler"),
    ("get at", "vouloir dire / sous-entendre"),
    ("get by", "se débrouiller"),
    ("get rid of", "se débarrasser de"),
    ("get together", "se réunir"),
    ("get ahead", "progresser"),
    ("get behind", "prendre du retard"),
]

TIER1_TAKE = [
    ("take off", "décoller / enlever"),
    ("take on", "accepter / embaucher"),
    ("take out", "sortir / emmener"),
    ("take up", "commencer / occuper l'espace"),
    ("take down", "noter / démolir"),
    ("take over", "reprendre le contrôle"),
    ("take in", "comprendre / absorber / héberger"),
    ("take back", "reprendre / rétracter"),
    ("take away", "emporter / retirer"),
    ("take after", "ressembler à (parent)"),
    ("take apart", "démonter"),
    ("take care of", "s'occuper de"),
    ("take place", "avoir lieu"),
    ("take turn", "se relayer"),
    ("take it out on", "passer ses nerfs sur"),
]

TIER1_PUT = [
    ("put on", "mettre (vêtement) / allumer"),
    ("put off", "reporter / dégoûter"),
    ("put out", "éteindre / publier"),
    ("put up", "afficher / loger / construire"),
    ("put up with", "tolérer / supporter"),
    ("put down", "poser / noter / critiquer"),
    ("put back", "remettre en place"),
    ("put away", "ranger"),
    ("put aside", "mettre de côté"),
    ("put through", "connecter / faire subir"),
    ("put forward", "proposer"),
    ("put across", "communiquer / faire comprendre"),
]

TIER1_GO = [
    ("go on", "continuer / se passer"),
    ("go off", "exploser / sonner / se gâter"),
    ("go out", "sortir / s'éteindre"),
    ("go over", "réviser / vérifier"),
    ("go through", "traverser / vivre difficile"),
    ("go back", "retourner"),
    ("go ahead", "y aller / commencer"),
    ("go down", "descendre / baisser"),
    ("go up", "monter / augmenter"),
    ("go away", "partir"),
    ("go along with", "accepter / suivre"),
    ("go around", "circuler / suffire"),
    ("go without", "se passer de"),
    ("go under", "couler / faire faillite"),
]

TIER1_COME = [
    ("come up", "surgir / se présenter"),
    ("come up with", "trouver / inventer"),
    ("come across", "tomber sur / paraître"),
    ("come out", "sortir / être révélé"),
    ("come in", "entrer / arriver"),
    ("come on", "allez ! / progresser"),
    ("come off", "se détacher / réussir"),
    ("come back", "revenir"),
    ("come down", "descendre / baisser"),
    ("come over", "passer chez qqn / envahir"),
    ("come around", "changer d'avis / reprendre connaissance"),
    ("come through", "s'en sortir / arriver"),
    ("come from", "venir de"),
]

TIER1_MAKE = [
    ("make up", "inventer / se réconcilier"),
    ("make out", "déchiffrer / prétendre"),
    ("make off", "s'enfuir"),
    ("make up for", "compenser"),
    ("make do with", "se débrouiller avec"),
    ("make for", "se diriger vers"),
    ("make of", "penser de"),
    ("make it", "réussir / y arriver"),
]

# ─── TIER 2 — Très fréquents ───

TIER2_TURN = [
    ("turn on", "allumer"), ("turn off", "éteindre"),
    ("turn up", "augmenter / se pointer"), ("turn down", "refuser / baisser"),
    ("turn out", "s'avérer / se révéler"), ("turn back", "faire demi-tour"),
    ("turn around", "se retourner"), ("turn into", "se transformer en"),
    ("turn over", "retourner"), ("turn away", "refuser l'entrée"),
]

TIER2_LOOK = [
    ("look up", "chercher / admirer"), ("look down on", "mépriser"),
    ("look out", "faire attention"), ("look for", "chercher"),
    ("look after", "s'occuper de"), ("look into", "enquêter sur"),
    ("look forward to", "avoir hâte de"), ("look back", "regarder en arrière"),
    ("look over", "examiner"), ("look up to", "admirer"),
    ("look through", "parcourir"),
]

TIER2_BREAK = [
    ("break down", "tomber en panne / craquer"),
    ("break up", "rompre / séparer"),
    ("break out", "s'évader / éclater"),
    ("break in", "entrer par effraction"),
    ("break through", "percer / franchir"),
    ("break off", "se briser / interrompre"),
    ("break away", "se détacher / s'éloigner"),
    ("break into", "pénétrer par effraction"),
]

TIER2_GIVE = [
    ("give up", "abandonner"), ("give out", "distribuer / s'épuiser"),
    ("give in", "céder"), ("give away", "donner / révéler"),
    ("give back", "rendre"), ("give off", "dégager (odeur/fumée)"),
    ("give over", "arrêter / laisser la place"),
]

TIER2_RUN = [
    ("run out", "être à court de"), ("run into", "tomber sur qqn"),
    ("run away", "s'enfuir"), ("run over", "écraser / dépasser"),
    ("run through", "parcourir rapidement"), ("run up", "accumuler (dettes)"),
    ("run off", "s'enfuir / imprimer"), ("run down", "critiquer / épuiser"),
]

TIER2_BRING = [
    ("bring up", "évoquer / élever"), ("bring out", "faire ressortir"),
    ("bring back", "rapporter"), ("bring down", "faire tomber"),
    ("bring in", "introduire / rapporter"), ("bring off", "réussir"),
    ("bring about", "provoquer / causer"), ("bring forward", "avancer (date)"),
]

TIER2_HOLD = [
    ("hold on", "attendre / tenir bon"), ("hold up", "retenir / braquer"),
    ("hold back", "retenir / cacher"), ("hold out", "tenir le coup"),
    ("hold off", "reporter / retenir"), ("hold down", "maintenir / garder"),
    ("hold together", "tenir ensemble"),
]

TIER2_KEEP = [
    ("keep up", "maintenir / suivre"), ("keep on", "continuer"),
    ("keep out", "ne pas entrer"), ("keep back", "retenir / cacher"),
    ("keep away", "tenir à distance"), ("keep down", "réprimer / baisser"),
    ("keep up with", "suivre le rythme de"),
]

TIER2_SET = [
    ("set up", "installer / mettre en place"), ("set off", "partir / déclencher"),
    ("set out", "se mettre en route"), ("set back", "retarder / coûter"),
    ("set aside", "mettre de côté"), ("set in", "s'installer (pluie/hiver)"),
    ("set down", "poser / noter"),
]

# ─── TIER 3 — Fréquents ───

TIER3 = [
    # CALL
    ("call off", "annuler", "call"),
    ("call back", "rappeler", "call"),
    ("call on", "visiter / interpeller", "call"),
    ("call out", "dénoncer / appeler", "call"),
    ("call up", "appeler / mobiliser", "call"),
    # PICK
    ("pick up", "ramasser / apprendre", "pick"),
    ("pick out", "choisir", "pick"),
    ("pick on", "harceler", "pick"),
    ("pick apart", "décortiquer", "pick"),
    # PULL
    ("pull off", "réussir (qqch de difficile)", "pull"),
    ("pull out", "se retirer", "pull"),
    ("pull through", "s'en sortir", "pull"),
    ("pull up", "s'arrêter (voiture)", "pull"),
    ("pull down", "démolir", "pull"),
    # FALL
    ("fall out", "se disputer", "fall"),
    ("fall through", "échouer (plan)", "fall"),
    ("fall behind", "prendre du retard", "fall"),
    ("fall apart", "s'effondrer", "fall"),
    ("fall for", "tomber amoureux / se faire avoir", "fall"),
    # WORK
    ("work out", "résoudre / s'entraîner", "work"),
    ("work on", "travailler sur", "work"),
    ("work up", "développer / exciter", "work"),
    ("work through", "surmonter", "work"),
    # CUT
    ("cut off", "couper / isoler", "cut"),
    ("cut down", "réduire", "cut"),
    ("cut out", "supprimer / cesser", "cut"),
    ("cut back", "réduire les dépenses", "cut"),
    ("cut in", "interrompre", "cut"),
    # CARRY
    ("carry on", "continuer", "carry"),
    ("carry out", "exécuter / réaliser", "carry"),
    ("carry over", "reporter", "carry"),
    ("carry away", "emporter / enthousiasmer", "carry"),
    # SHOW
    ("show up", "se pointer / arriver", "show"),
    ("show off", "se vanter / faire étalage", "show"),
    ("show around", "faire visiter", "show"),
    ("show out", "raccompagner", "show"),
    # STAND
    ("stand up", "se lever / poser un lapin", "stand"),
    ("stand out", "se distinguer", "stand"),
    ("stand by", "soutenir / être prêt", "stand"),
    ("stand for", "représenter / signifier", "stand"),
    ("stand down", "se retirer / démissionner", "stand"),
    # PASS
    ("pass out", "s'évanouir / distribuer", "pass"),
    ("pass on", "transmettre", "pass"),
    ("pass by", "passer devant", "pass"),
    ("pass up", "laisser passer (opportunité)", "pass"),
]


def build_expressions() -> list[dict]:
    items = []

    def add(group, tier, verb_tag):
        for text, meaning in group:
            items.append({
                "text": text,
                "meaning": meaning,
                "tier": tier,
                "source": f"tier{tier}",
                "tags": ["phrasal_verb", verb_tag],
                "difficulty": 2 if tier == 1 else (3 if tier == 2 else 4),
                "part_of_speech": "phrasal verb",
            })

    add(TIER1_GET, 1, "get")
    add(TIER1_TAKE, 1, "take")
    add(TIER1_PUT, 1, "put")
    add(TIER1_GO, 1, "go")
    add(TIER1_COME, 1, "come")
    add(TIER1_MAKE, 1, "make")

    add(TIER2_TURN, 2, "turn")
    add(TIER2_LOOK, 2, "look")
    add(TIER2_BREAK, 2, "break")
    add(TIER2_GIVE, 2, "give")
    add(TIER2_RUN, 2, "run")
    add(TIER2_BRING, 2, "bring")
    add(TIER2_HOLD, 2, "hold")
    add(TIER2_KEEP, 2, "keep")
    add(TIER2_SET, 2, "set")

    for text, meaning, verb_tag in TIER3:
        items.append({
            "text": text,
            "meaning": meaning,
            "tier": 3,
            "source": "tier3",
            "tags": ["phrasal_verb", verb_tag],
            "difficulty": 4,
            "part_of_speech": "phrasal verb",
        })

    return items


async def seed():
    async with async_session_factory() as db:
        # Check if already seeded
        result = await db.execute(select(Expression).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded — skipping.")
            return

        expressions = build_expressions()
        expr_objects = [Expression(**e) for e in expressions]
        db.add_all(expr_objects)
        await db.commit()

    print(f"✅ Seeded {len(expressions)} phrasal verbs:")
    print(f"   Tier 1: 82  (get, take, put, go, come, make)")
    print(f"   Tier 2: 73  (turn, look, break, give, run, bring, hold, keep, set)")
    print(f"   Tier 3: 45  (call, pick, pull, fall, work, cut, carry, show, stand, pass)")


if __name__ == "__main__":
    asyncio.run(seed())
