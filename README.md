# Vývoj mezd zaměstnanců

Zdroj tabulky https://claude.ai/artifact/64W1HEPC1wCGVqer5Dy1qg („Vývoj mezd zaměstnanců").
Data se berou ze složky PERSONALISTIKA na Google Drive
(`https://drive.google.com/drive/folders/10mfzRgqwpTo5jvh4svvpXLTDOpZIbGzy`).
Jednou měsíčně ji projde časovaná úloha v Claude Code (cloud), viz `ROUTINE.md`.

## Co kde je

| Soubor | K čemu |
|---|---|
| `template.html` | stránka tabulky (vzhled, přehled, roky, stránka „K ověření"); data se vkládají místo `/*DATA*/[]` |
| `data/employees.json` | **jediný zdroj dat**: zaměstnanci, události (mzdy, dodatky, MD, ukončení), body k ověření |
| `data/state.json` | čas posledního úspěšného běhu (`last_run`), od něj se hledají změny na Drive |
| `scripts/build.py` | ověří data a složí `out/vyvoj-mezd.html` |
| `ROUTINE.md` | zadání rutiny v cloudu |

`python scripts/build.py` → `out/vyvoj-mezd.html` (složka `out/` se necommituje).

**Aktuální data jsou na větvi `claude/mzdy-data`**, ne v `main` – cloud do `main` pushovat nesmí.
Před ruční úpravou dat lokálně: `git fetch && git checkout origin/claude/mzdy-data -- data`.

## Datový model (`data/employees.json`)

Pole zaměstnanců:

```json
{"name": "Příjmení (Rodné) Jméno", "start": "2018-09-07", "end": null,
 "status": null, "events": [...], "issues": ["text bodu k ověření", ...]}
```

- `end` – poslední den PP (ISO datum) nebo `null`.
- `status` – krátký štítek do Přehledu: `"ukončeno dohodou"`, `"mateřská / rodičovská"`,
  `"DPP (hodinová odměna)"`, `"doba určitá do 31. 12. 2027"` … nebo `null`.
  Slovo „mateřsk" zbarví štítek fialově a započte do MD/RD.

Událost (`events[]`):

```json
{"from": "2025-01-01", "salary": 43300, "hours": 40, "position": null,
 "doc": "Dodatek č. 1", "fileId": "<Drive file id>", "note": null,
 "kind": null, "added": null}
```

- `salary` – měsíční hrubá mzda v Kč (číslo), jinak `null`. Pohyblivé složky a prémie se nezapisují.
- `hours` – týdenní úvazek v hodinách, jen když ho dokument uvádí; jinak `null` (platí předchozí).
- `kind` (nepovinné; když chybí, odvodí se):
  - `"pay"` – má mzdu (odvozeno automaticky z `salary`),
  - `"leave"` – nástup na mateřskou / rodičovskou (doc obsahuje „Mateřsk" nebo „PPM"),
  - `"end"` – konec PP (doc obsahuje „Ukončení"/„rozvázání"),
  - `"dpp"` – DPP místo PP,
  - `"info"` – dokument bez vlivu na mzdu (GDPR, místo výkonu práce, dovolená…).
    **Vždy nastav `"kind": "info"` a `"added": true`** u dokumentů, které nemění mzdu ani stav,
    jinak by mohly stav přepsat (např. nepodepsaná výpověď).
- `note` – krátká poznámka; u nepodepsaných konceptů napiš „nepodepsaný koncept".
- `fileId` – id souboru na Drive (stránka z něj dělá odkaz). Bez dokumentu `null`.

Body k ověření (`issues[]`) jsou volný text. Stránka si k nim drží stav a poznámky v databázi
artefaktu (kolekce `checks`, id = hash `jméno|text`) – **změna textu bodu = nový bod**
(stav i poznámka u starého textu se ztratí), proto texty existujících bodů neměň.

## Pravidla

- Drive je **jen ke čtení**. Nikdy neotvírej soubor „hesla k výplatnici.xlsx".
- Do dat nikdy nepiš rodná čísla, data narození, adresy, e-maily, bankovní údaje
  ani zdravotní informace. Rodné listy, oddací listy, OP a lékařské posudky neotevírej.
- Složky mimo zaměstnance neprocházej: „AAA Roční personální dokumentace", „Mzdové listy …",
  „Potvrzení o zdanitelných příjmech …", „Prohlášení poplatníka …", „Alžbětky adresář …".
- „AAA UKONČENÉ PP" jen pro zaměstnance, kteří už v tabulce jsou (přesun složky = ukončení PP).
  Jiné ukončené zaměstnance nepřidávej.
