
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="TP Intégrateur - Filtration")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def afficher_formulaire(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "resultat": None,
            "m0": 1000,
            "x0": 10,
            "p_ins": 2,
            "p_eau": 88,
            "temperature": 20
        }
    )


@app.post("/", response_class=HTMLResponse)
async def calculer_filtration(
    request: Request,
    m0: float = Form(...),
    x0: float = Form(...),
    p_ins: float = Form(...),
    p_eau: float = Form(...),
    temperature: float = Form(...)
):

    resultat = None
    erreur = None

    # Vérification des valeurs saisies
    if m0 <= 0:
        erreur = "Le débit du jus brut doit être supérieur à zéro."

    elif min(x0, p_ins, p_eau) < 0:
        erreur = "Les pourcentages ne peuvent pas être négatifs."

    elif max(x0, p_ins, p_eau) > 100:
        erreur = "Chaque pourcentage doit être inférieur ou égal à 100."

    elif abs(x0 + p_ins + p_eau - 100) > 0.01:
        erreur = "La somme des compositions doit être égale à 100 %."

    else:

        # 1. Masse des particules insolubles retenues
        m_residus = m0 * (p_ins / 100)

        # 2. Débit massique du filtrat
        m1 = m0 - m_residus

        # 3. Masse des matières solubles conservées
        masse_solubles = m0 * (x0 / 100)

        # 4. Masse d'eau dans le filtrat
        masse_eau = m0 * (p_eau / 100)

        # 5. Concentration finale en matières solubles
        x1 = (masse_solubles / m1) * 100 if m1 > 0 else 0

        # 6. Vérification de l'objectif de 40 %
        objectif = 40

        # Débit théorique après concentration à 40 %
        debit_concentre = masse_solubles / (objectif / 100)

        eau_a_evaporer = m1 - debit_concentre

        resultat = {
            "m0": round(m0, 2),
            "temperature": round(temperature, 2),
            "m_residus": round(m_residus, 2),
            "m1": round(m1, 2),
            "masse_solubles": round(masse_solubles, 2),
            "masse_eau": round(masse_eau, 2),
            "x1": round(x1, 2),
            "objectif": objectif,
            "debit_concentre": round(debit_concentre, 2),
            "eau_a_evaporer": round(eau_a_evaporer, 2),
            "atteint": x1 >= objectif
        }

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "resultat": resultat,
            "erreur": erreur,
            "m0": m0,
            "x0": x0,
            "p_ins": p_ins,
            "p_eau": p_eau,
            "temperature": temperature
        }
    )
