# Vague 5 — nouveau record marginal, aucune promotion

29 octobre 2026 — branche `gpt-wave5-causal-research-20261029`.

## Décision

**H atteint 1,459078700 de Sharpe net**, contre **1,457654704 pour R1** et **1,444733301 pour V3**. Le gain contre R1 est de **0,001423996**. C'est le meilleur chiffre observé, pas une amélioration future établie : le seuil de gain de 0,005 fixé avant les essais n'est pas atteint, les intervalles de confiance incluent zéro et la seconde moitié est légèrement moins bonne que R1.

Aucun candidat n'est promu. V3 reste intact ; R1 reste le comparateur de recherche précédent, sans garantie de supériorité future. Ni `main`, ni `v2-factor-risk`, ni `handoff_v3` n'ont été modifiés. Rien n'a été soumis.

## Protocole

Le plan complet a été enregistré avant les nouvelles expériences : commit `09cbdc7614c8148869acc6d98e18598e3208a376`, fichier `research/wave5/PLAN_20261029.md`. Le workflow E2E a été écrit et commité localement avant l'implémentation ; son lancement initial échoue volontairement avant l'existence du module. Ce log et l'historique local sont conservés. Les copies distantes ont été publiées ensuite et vérifiées contre les fichiers exécutés.

Le budget était de trois candidats primaires et deux ablations. Aucun réglage de paramètres, recherche de seed ou sélection de fenêtre après les résultats. Les combinaisons conditionnelles H+P et E+un autre modèle n'ont pas été lancées : leurs critères préenregistrés ne sont pas remplis. Un diagnostic ex-post a été déplacé hors de la politique avant les scores primaires, sans modifier ses prévisions ; les tests construits ont été rejoués ensuite.

Les quinze années ont déjà été examinées dans le projet. Elles sont des données de développement exposées, pas un nouveau holdout. Le brief autorise leur utilisation pour régler les paramètres, mais interdit le lookahead. La procédure limite le surapprentissage ; elle ne peut pas en certifier l'absence.

## Tous les résultats

Scorer fourni inchangé, frais complets, 3 526 observations, lignes 253 à 3778 en indexation zéro. La poche marché reste fixée à 0,05 dans tous les cas.

| Variante | Sharpe net | Écart contre R1 | Bêta mesuré | Frais annuels |
|---|---:|---:|---:|---:|
| V3 / B0 | 1,444733301 | −0,012921403 | 0,102977520 | 0,253792495 % |
| R1 reproduit | 1,457654704 | — | 0,101730411 | 0,251456226 % |
| **H : risque multihorizon, GLM Gamma** | **1,459078700** | **+0,001423996** | **0,101867919** | **0,255694880 %** |
| P : primes liées à la volatilité factorielle | 1,362461743 | −0,095192960 | 0,101873416 | 0,264917529 % |
| E : coûts autour des positions réelles | 1,446072144 | −0,011582559 | 0,102941091 | 0,242315697 % |
| A_pool : correction R1 commune à tous les titres | 1,457204898 | −0,000449806 | 0,101681548 | 0,249736408 % |
| A_cross : correction R1 relative, moyenne normalisée | 1,445304520 | −0,012350184 | 0,103024581 | 0,255531158 % |

Les ablations sont explicatives, pas des candidats autonomes de déploiement dans ce plan. Tous les essais, perdants compris, sont conservés.

## Ce que H apprend

H conserve les prévisions de rendement F2, le risque factoriel, l'optimiseur, les limites et la poche marché de V3. Il modifie uniquement la variance spécifique fournie aux livres virtuel et négocié.

Ses trois variables sont les estimations exponentielles de variance résiduelle de demi-vies 5, 21 et 63 jours, divisées par l'estimation V3, bornées puis transformées en logarithmes. Un GLM Gamma à lien logarithmique apprend le carré du résidu suivant divisé par la variance disponible avant ce résidu.

Paramètres fixes : `alpha=1`, `max_iter=300`, `tol=1e-8`, réentraînement tous les 126 jours, une observation journalière sur cinq dans les 504 jours précédents, labels à partir de la ligne 64. Il n'y a ni validation aléatoire ni early stopping. La correction finale est `0.5 + 0.5 * clip(prediction, 0.5, 2)`, donc comprise entre 0,75 et 1,5. Chaque label utilisé pour prévoir la ligne t est antérieur à t ; les variables d'une paire précèdent son label d'un jour.

H a trois coefficients plus un intercept par ajustement. Le calcul complet des prévisions prend **8,01 secondes**, contre **42,78 secondes pour R1**. Le rééquilibrage intégré prend **10,00 ms par appel** en moyenne, avec un thread BLAS/OpenMP. La projection linéaire du forecast est d'environ **53,4 secondes par siècle**, sans qu'un siècle ait effectivement été simulé. Les replays primaires n'utilisent pas un cache pour masquer le coût du rééquilibrage.

## La découverte utile : d'où vient le gain de R1 ?

A_pool remplace les 1 000 corrections de risque de R1 par leur moyenne transversale du même jour. Il conserve **96,52 % de l'écart de Sharpe observé entre R1 et V3**. A_cross retire la composante commune et conserve les corrections relatives entre titres : son score retombe presque à V3.

Cela soutient l'interprétation suivante : le bénéfice historique de R1 vient surtout d'une correction commune du risque, plutôt que d'une amélioration importante du classement des risques individuels. Ce n'est pas une décomposition causale du profit. A_pool calcule toujours les sorties du booster avant d'en prendre la moyenne ; nous n'avons pas démontré qu'une règle sans ML le remplacerait à performance identique.

La question de recherche devient donc l'identification de cet état commun du risque, plutôt que l'ajout de capacité à un modèle par titre. Cette piste n'a pas été transformée après coup en nouveaux essais dans cette vague.

## Diagnostics : risque, signal et coûts

La variation moyenne de QLIKE contre V3, calculée sur les carrés des résidus de notre modèle factoriel, vaut **+0,008992403 pour R1** et **−0,005405510 pour H** ; une valeur plus basse est meilleure. H améliore ce diagnostic agrégé, mais pas chaque période : sa dernière période est à +0,004861975 contre V3. Le proxy est un carré de résidu estimé, pas la variance latente véritable du générateur inconnu. Ce diagnostic ne prouve ni une meilleure covariance complète ni une amélioration du Sharpe futur.

P réduit l'IC moyen de 0,014878908 à 0,014550598 et le Sharpe des IC journaliers de 1,26650 à 1,19707, alors que son erreur quadratique moyenne diminue très légèrement. Son Sharpe de portefeuille chute. Une petite amélioration d'une perte prédictive globale ne suffit donc pas.

E réduit les frais de V3 de 0,25379 % à 0,24232 % par an et améliore son Sharpe de 0,001338844, avec des gains dans les trois périodes. Il centre la pénalité de transaction sur les positions réellement détenues, diminuées de la poche fixe, plutôt que sur le livre interne dérivé séparément. Son gain reste sous le seuil de 0,005 autorisant une combinaison : aucun E+R1 ou E+H n'a été testé.

## Incertitude

Les périodes sont [253,2016), [2016,3024) et [3024,3779).

| Période | R1 | H | H moins R1 |
|---|---:|---:|---:|
| Première | 1,208886297 | 1,212578042 | +0,003691745 |
| Deuxième | 1,853270193 | 1,843355899 | −0,009914294 |
| Troisième | 1,633864838 | 1,645160900 | +0,011296061 |

Sur la seconde moitié, H est inférieur à R1 de 0,000793670. Le bootstrap apparié circulaire utilise 3 000 tirages, seed 20261030, avec les mêmes indices pour comparer H/P/E à R1.

| Taille des blocs | Intervalle à 95 % du gain H moins R1 |
|---|---|
| 21 jours | [−0,012862530 ; +0,015477422] |
| 63 jours | [−0,012140813 ; +0,014944614] |
| 126 jours | [−0,011472704 ; +0,014118162] |

Tous incluent zéro. À 63 jours, le test unilatéral bootstrap centré donne p=0,42619 pour H ; après correction Holm sur les trois candidats, p ajusté=1,0. Cette correction couvre uniquement cette vague, pas l'ensemble des essais du projet. La proportion de tirages positifs n'est pas une probabilité de succès futur.

H satisfait les critères QLIKE, bêta, temps et logiciel, mais pas le gain minimal ni les critères statistiques préenregistrés. **Aucune promotion et aucun changement du seuil après les résultats.**

## Vérifications et provenance

Les cinq fichiers V3 requis sont identiques octet pour octet aux empreintes Git du dépôt : `strategy.py`, `engine.py`, `allocator.py`, `policy.py`, `__init__.py`. La réserve de la vague précédente sur les copies abrégées est donc levée pour ces fichiers précis. Cela ne constitue pas une revue indépendante par un autre agent ni un clone complet du dépôt.

V3 reproduit le score publié à 2,35×10⁻¹³ près. Ses quatre colonnes économiques journalières correspondent exactement aux preuves de la vague 4. R1 reproduit son score et ses colonnes économiques avec un écart de zéro.

**96 assertions E2E passent**, avec une erreur maximale de zéro dans les comparaisons : 45 sur données construites, 17 par candidat primaire sur les données réelles. Les premières couvrent les coupures 127/252/378, les préfixes 379/400, les redémarrages, les données nulles et les limites. Les secondes couvrent les préfixes 379/630/2016, les mutations de rendements seuls, de caractéristiques seules et conjointes aux lignes 630/2016, ainsi que les redémarrages. Une reconstruction indépendante de la dérive des positions, des rendements et des frais est comparée au scorer sur les préfixes contrôlés.

Chaque replay complet R1/H/P/E/A_pool/A_cross produit 7 054 certificats d'allocation avec statut `ok`. Le plafond brut externe ne s'active pas. Aucun NaN ni aucune ruine observée. Les tests établissent la causalité sur les cas exécutés, pas une absence de surapprentissage ou une garantie sur tout futur possible.

Le scorer original a pour SHA-256 `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`. Les empreintes des sources et sorties, les résultats journaliers, les coefficients, les logs, les commandes et l'historique local sont archivés. Les CSV sources et les gros tenseurs de prévisions/positions ne sont pas redistribués ; leurs empreintes permettent de vérifier une reproduction.

Aucun échec dans les replays enregistrés. Le lancement intentionnel avant implémentation est conservé. Deux voies de téléchargement direct indisponibles ont été contournées par une récupération du texte via le connecteur, vérifiée par les empreintes Git. Aucun agent indépendant n'a été utilisé.

## Références méthodologiques

Patton (2011), *Volatility forecast comparison using imperfect volatility proxies*, DOI 10.1016/j.jeconom.2010.03.034 : motivation pour QLIKE, pas validation sur notre marché. Documentation officielle scikit-learn, *GammaRegressor* : GLM Gamma à lien logarithmique. Gârleanu et Pedersen, NBER w15205 : motivation pour traiter explicitement positions et coûts ; leur solution à coûts quadratiques n'est pas revendiquée comme solution à notre problème à coûts linéaires.

**Bilan : un record historique marginal et une meilleure compréhension de R1, mais pas de nouvel alpha établi.**
