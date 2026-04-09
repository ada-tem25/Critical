"""
Domain Registry for Critical — Fact-checking source classification.
Curated entries + Vera fact-checking & reliable media sources.
Regions: Europe + North America + International orgs.

Fields:
  reliability: "reference" | "established" | "oriented"
  category: institutional | academic | fact_checking | news_agency |
            press_general | press_economic | press_investigative |
            audiovisual | think_tank | encyclopedia
  region: ISO 3166-1 alpha-2 (FR, US, UK...) + INT, EU
  bias: neutral | center-left | center-right | left | right | far-left | far-right
"""


DOMAIN_REGISTRY: dict[str, dict] = {

    # ════════════════════════════════════════════════════════════
    # REFERENCE — Institutional
    # ════════════════════════════════════════════════════════════
    # EU
    "ecb.europa.eu":                                {"reliability": "reference", "category": "institutional", "region": "EU", "bias": "neutral"},
    "eea.europa.eu":                                {"reliability": "reference", "category": "institutional", "region": "EU", "bias": "neutral"},
    "europa.eu":                                    {"reliability": "reference", "category": "institutional", "region": "EU", "bias": "neutral"},
    "eurostat.ec.europa.eu":                        {"reliability": "reference", "category": "institutional", "region": "EU", "bias": "neutral"},
    # FR
    "ademe.fr":                                     {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "assemblee-nationale.fr":                       {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "banque-france.fr":                             {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "ccomptes.fr":                                  {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "conseil-constitutionnel.fr":                   {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "data.gouv.fr":                                 {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "drees.solidarites-sante.gouv.fr":              {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "economie.gouv.fr":                             {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "education.gouv.fr":                            {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "has-sante.fr":                                 {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "insee.fr":                                     {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "interieur.gouv.fr":                            {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "irsn.fr":                                      {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "legifrance.gouv.fr":                           {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "ofce.sciences-po.fr":                          {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "securite-sociale.fr":                          {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "senat.fr":                                     {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "service-public.fr":                            {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    "vie-publique.fr":                              {"reliability": "reference", "category": "institutional", "region": "FR", "bias": "neutral"},
    # INT
    "imf.org":                                      {"reliability": "reference", "category": "institutional", "region": "INT", "bias": "neutral"},
    "ipcc.ch":                                      {"reliability": "reference", "category": "institutional", "region": "INT", "bias": "neutral"},
    "oecd.org":                                     {"reliability": "reference", "category": "institutional", "region": "INT", "bias": "neutral"},
    "transparency.org":                             {"reliability": "reference", "category": "institutional", "region": "INT", "bias": "neutral"},
    "un.org":                                       {"reliability": "reference", "category": "institutional", "region": "INT", "bias": "neutral"},
    "unhcr.org":                                    {"reliability": "reference", "category": "institutional", "region": "INT", "bias": "neutral"},
    "unicef.org":                                   {"reliability": "reference", "category": "institutional", "region": "INT", "bias": "neutral"},
    "who.int":                                      {"reliability": "reference", "category": "institutional", "region": "INT", "bias": "neutral"},
    "worldbank.org":                                {"reliability": "reference", "category": "institutional", "region": "INT", "bias": "neutral"},

    # ════════════════════════════════════════════════════════════
    # REFERENCE — Academic & Scientific
    # ════════════════════════════════════════════════════════════
    # FR
    "cairn.info":                                   {"reliability": "reference", "category": "academic", "region": "FR", "bias": "neutral"},
    "hal.science":                                  {"reliability": "reference", "category": "academic", "region": "FR", "bias": "neutral"},
    "persee.fr":                                    {"reliability": "reference", "category": "academic", "region": "FR", "bias": "neutral"},
    "theses.fr":                                    {"reliability": "reference", "category": "academic", "region": "FR", "bias": "neutral"},
    # INT
    "bmj.com":                                      {"reliability": "reference", "category": "academic", "region": "INT", "bias": "neutral"},
    "jstor.org":                                    {"reliability": "reference", "category": "academic", "region": "INT", "bias": "neutral"},
    "nature.com":                                   {"reliability": "reference", "category": "academic", "region": "INT", "bias": "neutral"},
    "pnas.org":                                     {"reliability": "reference", "category": "academic", "region": "INT", "bias": "neutral"},
    "pubmed.ncbi.nlm.nih.gov":                      {"reliability": "reference", "category": "academic", "region": "INT", "bias": "neutral"},
    "scholar.google.com":                           {"reliability": "reference", "category": "academic", "region": "INT", "bias": "neutral"},
    "sciencedirect.com":                            {"reliability": "reference", "category": "academic", "region": "INT", "bias": "neutral"},
    "thelancet.com":                                {"reliability": "reference", "category": "academic", "region": "INT", "bias": "neutral"},

    # ════════════════════════════════════════════════════════════
    # REFERENCE — Fact-checking
    # ════════════════════════════════════════════════════════════
    # DE
    "br.de/nachrichten/faktenfuchs-faktencheck,QzSIzl3":{"reliability": "reference", "category": "fact_checking", "region": "DE", "bias": "neutral"},
    "correctiv.org":                                {"reliability": "reference", "category": "fact_checking", "region": "DE", "bias": "neutral"},
    "dpa-factchecking.com":                         {"reliability": "reference", "category": "fact_checking", "region": "DE", "bias": "neutral"},
    "faktencheck.afp.com":                          {"reliability": "reference", "category": "fact_checking", "region": "DE", "bias": "neutral"},
    # ES
    "maldita.es":                                   {"reliability": "reference", "category": "fact_checking", "region": "ES", "bias": "neutral"},
    "verificat.cat":                                {"reliability": "reference", "category": "fact_checking", "region": "ES", "bias": "neutral"},
    # EU
    "checkfirst.network":                           {"reliability": "reference", "category": "fact_checking", "region": "EU", "bias": "neutral"},
    "efcsn.com":                                    {"reliability": "reference", "category": "fact_checking", "region": "EU", "bias": "neutral"},
    # FR
    "cestvraica.com":                               {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "conspiracywatch.info":                         {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "defacto-observatoire.fr/Fact-checks":          {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "factuel.afp.com":                              {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "intox-detox.fr":                               {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "lanouvellerepublique.fr":                      {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "lemonde.fr/les-decodeurs":                     {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "lessurligneurs.eu":                            {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "liberation.fr/checknews":                      {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "pharmacomedicale.org":                         {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "presse.inserm.fr/le-canal-detox":              {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "sfpt-fr.org":                                  {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "neutral"},
    "tf1info.fr/actualite/les-verificateurs":       {"reliability": "reference", "category": "fact_checking", "region": "FR", "bias": "center"},
    # INT
    "climatefeedback.org":                          {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "dfrlab.org":                                   {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "factcheck.afp.com":                            {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "factoscope.fr":                                {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "fatabyyano.net":                               {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "healthfeedback.org":                           {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "info-res.org":                                 {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "infodemiology.com":                            {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "information.tv5monde.com/chronique/vrai-dire": {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "kyoto-u.ac.jp":                                {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "misbar.com":                                   {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "ovd.info":                                     {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "science.feedback.org":                         {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    "vaccineconfidence.org":                        {"reliability": "reference", "category": "fact_checking", "region": "INT", "bias": "neutral"},
    # IT
    "pagellapolitica.it":                           {"reliability": "reference", "category": "fact_checking", "region": "IT", "bias": "neutral"},
    # UK
    "factcheckni.org":                              {"reliability": "reference", "category": "fact_checking", "region": "UK", "bias": "neutral"},
    "fullfact.org":                                 {"reliability": "reference", "category": "fact_checking", "region": "UK", "bias": "neutral"},
    # US
    "aap.org":                                      {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "allsides.com":                                 {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "factcheck.org":                                {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "factstream.com":                               {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "hoax-slayer.net":                              {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "leadstories.com":                              {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "mediamatters.org":                             {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "newsguardrealitycheck.com":                    {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "politifact.com":                               {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "poynter.org/news/fact-checking":               {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "publications.aap.org":                         {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "publichealth.jhu.edu":                         {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},
    "snopes.com":                                   {"reliability": "reference", "category": "fact_checking", "region": "US", "bias": "neutral"},

    # ════════════════════════════════════════════════════════════
    # REFERENCE — News agencies
    # ════════════════════════════════════════════════════════════
    # DE
    "dpa.com":                                      {"reliability": "reference", "category": "news_agency", "region": "DE", "bias": "neutral"},
    # ES
    "efe.com":                                      {"reliability": "reference", "category": "news_agency", "region": "ES", "bias": "neutral"},
    # FR
    "afp.com":                                      {"reliability": "reference", "category": "news_agency", "region": "FR", "bias": "neutral"},
    # IT
    "ansa.it":                                      {"reliability": "reference", "category": "news_agency", "region": "IT", "bias": "neutral"},
    # UK
    "reuters.com":                                  {"reliability": "reference", "category": "news_agency", "region": "UK", "bias": "neutral"},
    # US
    "apnews.com":                                   {"reliability": "reference", "category": "news_agency", "region": "US", "bias": "neutral"},

    # ════════════════════════════════════════════════════════════
    # REFERENCE — Encyclopedias
    # ════════════════════════════════════════════════════════════
    # INT
    "britannica.com":                               {"reliability": "reference", "category": "encyclopedia", "region": "INT", "bias": "neutral"},
    "wikipedia.org":                                {"reliability": "reference", "category": "encyclopedia", "region": "INT", "bias": "neutral"},

    # ════════════════════════════════════════════════════════════
    # ESTABLISHED — General press
    # ════════════════════════════════════════════════════════════
    # BE
    "lalibre.be":                                   {"reliability": "established", "category": "press_general", "region": "BE", "bias": "center"},
    "lavenir.net":                                  {"reliability": "established", "category": "press_general", "region": "BE", "bias": "neutral"},
    "lesoir.be":                                    {"reliability": "established", "category": "press_general", "region": "BE", "bias": "center"},
    "medi-sphere.be":                               {"reliability": "established", "category": "press_general", "region": "BE", "bias": "neutral"},
    "nieuwsblad.be":                                {"reliability": "established", "category": "press_general", "region": "BE", "bias": "neutral"},
    "rtbf.be":                                      {"reliability": "established", "category": "press_general", "region": "BE", "bias": "center"},
    # CA
    "cbc.ca":                                       {"reliability": "established", "category": "press_general", "region": "CA", "bias": "center"},
    "ledevoir.com":                                 {"reliability": "established", "category": "press_general", "region": "CA", "bias": "center-left"},
    "nationalpost.com":                             {"reliability": "established", "category": "press_general", "region": "CA", "bias": "center-right"},
    "quebecscience.qc.ca":                          {"reliability": "established", "category": "press_general", "region": "CA", "bias": "neutral"},
    "theglobeandmail.com":                          {"reliability": "established", "category": "press_general", "region": "CA", "bias": "center"},
    "thestar.com":                                  {"reliability": "established", "category": "press_general", "region": "CA", "bias": "neutral"},
    # CH
    "laliberte.ch":                                 {"reliability": "established", "category": "press_general", "region": "CH", "bias": "neutral"},
    "lematin.ch":                                   {"reliability": "established", "category": "press_general", "region": "CH", "bias": "neutral"},
    "letemps.ch":                                   {"reliability": "established", "category": "press_general", "region": "CH", "bias": "center"},
    "swissinfo.ch":                                 {"reliability": "established", "category": "press_general", "region": "CH", "bias": "neutral"},
    "tdg.ch":                                       {"reliability": "established", "category": "press_general", "region": "CH", "bias": "neutral"},
    # DE
    "faz.net":                                      {"reliability": "established", "category": "press_general", "region": "DE", "bias": "center-right"},
    "spiegel.de":                                   {"reliability": "established", "category": "press_general", "region": "DE", "bias": "center-left"},
    "sueddeutsche.de":                              {"reliability": "established", "category": "press_general", "region": "DE", "bias": "center-left"},
    "zeit.de":                                      {"reliability": "established", "category": "press_general", "region": "DE", "bias": "center-left"},
    # ES
    "abc.es":                                       {"reliability": "established", "category": "press_general", "region": "ES", "bias": "center-right"},
    "busqueda.com.uy":                              {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "clarin.com":                                   {"reliability": "established", "category": "press_general", "region": "ES", "bias": "center-right"},
    "cooperativa.cl":                               {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "df.cl":                                        {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "elcomercio.com":                               {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "elespectador.com":                             {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "elmercurio.cl":                                {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "elmundo.es":                                   {"reliability": "established", "category": "press_general", "region": "ES", "bias": "center-right"},
    "elpais.com":                                   {"reliability": "established", "category": "press_general", "region": "ES", "bias": "center-left"},
    "elpais.com.uy":                                {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "eltiempo.com":                                 {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "eluniversal.com.mx":                           {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "excelsior.com.mx":                             {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "jornada.com.mx":                               {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "la-razon.com":                                 {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "larepublica.co":                               {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "larepublica.pe":                               {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "lavanguardia.com":                             {"reliability": "established", "category": "press_general", "region": "ES", "bias": "center"},
    "milenio.com":                                  {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "nacion.com":                                   {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "rpp.pe":                                       {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    "talcualdigital.com":                           {"reliability": "established", "category": "press_general", "region": "ES", "bias": "neutral"},
    # EU
    "euronews.com":                                 {"reliability": "established", "category": "press_general", "region": "EU", "bias": "center"},
    "europeanscientist.com":                        {"reliability": "established", "category": "press_general", "region": "EU", "bias": "neutral"},
    "voxeurop.eu":                                  {"reliability": "established", "category": "press_general", "region": "EU", "bias": "neutral"},
    # FR
    "20minutes.fr":                                 {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    "capital.fr":                                   {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center-right"},
    "challenges.fr":                                {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center-right"},
    "cieletespace.fr":                              {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "clepsy.fr":                                    {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "courrier-international.com":                   {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    "dna.fr":                                       {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "epsiloon.com":                                 {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "estrepublicain.fr":                            {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "exit.al":                                      {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "france3-regions.francetvinfo.fr":              {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "guichetdusavoir.org":                          {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "huffingtonpost.fr":                            {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center-left"},
    "la-croix.com":                                 {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    "lalsace.fr":                                   {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "laprovence.com":                               {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "larecherche.fr":                               {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "lavoixdunord.fr":                              {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "lci.fr":                                       {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    "leblob.fr":                                    {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "ledauphine.com":                               {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "lefigaro.fr":                                  {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center-right"},
    "legrandcontinent.eu":                          {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "lemessager.fr":                                {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "lemonde.fr":                                   {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center-left"},
    "leparisien.fr":                                {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    "lepoint.fr":                                   {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center-right"},
    "leprogres.fr":                                 {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "letudiant.fr":                                 {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "lexpress.fr":                                  {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    "liberation.fr":                                {"reliability": "established", "category": "press_general", "region": "FR", "bias": "left"},
    "lobs.com":                                     {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center-left"},
    "lopinion.fr":                                  {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center-right"},
    "marianne.net":                                 {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    "medecinesciences.org":                         {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "mnhn.fr":                                      {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "ouest-france.fr":                              {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    "pourlascience.fr":                             {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "sante.fr":                                     {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "sciencesetavenir.fr":                          {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "sudouest.fr":                                  {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    "telescopemag.fr":                              {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "trustmyscience.com":                           {"reliability": "established", "category": "press_general", "region": "FR", "bias": "neutral"},
    "tv5monde.com":                                 {"reliability": "established", "category": "press_general", "region": "FR", "bias": "center"},
    # INT
    "antiguaobserver.com":                          {"reliability": "established", "category": "press_general", "region": "INT", "bias": "neutral"},
    "borneobulletin.com.bn":                        {"reliability": "established", "category": "press_general", "region": "INT", "bias": "neutral"},
    "geo.fr":                                       {"reliability": "established", "category": "press_general", "region": "INT", "bias": "neutral"},
    "loopnews.com":                                 {"reliability": "established", "category": "press_general", "region": "INT", "bias": "neutral"},
    "thearabweekly.com":                            {"reliability": "established", "category": "press_general", "region": "INT", "bias": "neutral"},
    "theconversation.com":                          {"reliability": "established", "category": "press_general", "region": "INT", "bias": "neutral"},
    "theeastafrican.co.ke":                         {"reliability": "established", "category": "press_general", "region": "INT", "bias": "neutral"},
    # IT
    "corriere.it":                                  {"reliability": "established", "category": "press_general", "region": "IT", "bias": "center"},
    "ilmessaggero.it":                              {"reliability": "established", "category": "press_general", "region": "IT", "bias": "neutral"},
    "ilsole24ore.com":                              {"reliability": "established", "category": "press_general", "region": "IT", "bias": "center-right"},
    "lastampa.it":                                  {"reliability": "established", "category": "press_general", "region": "IT", "bias": "center"},
    "repubblica.it":                                {"reliability": "established", "category": "press_general", "region": "IT", "bias": "center-left"},
    # UK
    "independent.co.uk":                            {"reliability": "established", "category": "press_general", "region": "UK", "bias": "center-left"},
    "newscientist.com":                             {"reliability": "established", "category": "press_general", "region": "UK", "bias": "neutral"},
    "scotsman.com":                                 {"reliability": "established", "category": "press_general", "region": "UK", "bias": "neutral"},
    "telegraph.co.uk":                              {"reliability": "established", "category": "press_general", "region": "UK", "bias": "center-right"},
    "theguardian.com":                              {"reliability": "established", "category": "press_general", "region": "UK", "bias": "center-left"},
    "thenational.scot":                             {"reliability": "established", "category": "press_general", "region": "UK", "bias": "neutral"},
    "thetimes.co.uk":                               {"reliability": "established", "category": "press_general", "region": "UK", "bias": "center-right"},
    # US
    "axios.com":                                    {"reliability": "established", "category": "press_general", "region": "US", "bias": "center"},
    "cnn.com":                                      {"reliability": "established", "category": "press_general", "region": "US", "bias": "center-left"},
    "discovermagazine.com":                         {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "heart.org":                                    {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "huffpost.com":                                 {"reliability": "established", "category": "press_general", "region": "US", "bias": "center-left"},
    "latimes.com":                                  {"reliability": "established", "category": "press_general", "region": "US", "bias": "center-left"},
    "nationalgeographic.com":                       {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "nautil.us":                                    {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "nbcnews.com":                                  {"reliability": "established", "category": "press_general", "region": "US", "bias": "center-left"},
    "newsweek.com":                                 {"reliability": "established", "category": "press_general", "region": "US", "bias": "center"},
    "nytimes.com":                                  {"reliability": "established", "category": "press_general", "region": "US", "bias": "center-left"},
    "politico.com":                                 {"reliability": "established", "category": "press_general", "region": "US", "bias": "center"},
    "popsci.com":                                   {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "sciencenews.org":                              {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "scientificamerican.com":                       {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "smithsonianmag.com":                           {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "space.com":                                    {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "theverge.com":                                 {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "usatoday.com":                                 {"reliability": "established", "category": "press_general", "region": "US", "bias": "center"},
    "vox.com":                                      {"reliability": "established", "category": "press_general", "region": "US", "bias": "center-left"},
    "washingtonpost.com":                           {"reliability": "established", "category": "press_general", "region": "US", "bias": "center-left"},
    "wired.com":                                    {"reliability": "established", "category": "press_general", "region": "US", "bias": "neutral"},
    "wsj.com":                                      {"reliability": "established", "category": "press_general", "region": "US", "bias": "center-right"},

    # ════════════════════════════════════════════════════════════
    # ESTABLISHED — Economic & financial press
    # ════════════════════════════════════════════════════════════
    # FR
    "alternatives-economiques.fr":                  {"reliability": "established", "category": "press_economic", "region": "FR", "bias": "center-left"},
    "latribune.fr":                                 {"reliability": "established", "category": "press_economic", "region": "FR", "bias": "center-right"},
    "lesechos.fr":                                  {"reliability": "established", "category": "press_economic", "region": "FR", "bias": "center-right"},
    # UK
    "economist.com":                                {"reliability": "established", "category": "press_economic", "region": "UK", "bias": "center-right"},
    "ft.com":                                       {"reliability": "established", "category": "press_economic", "region": "UK", "bias": "center-right"},
    # US
    "bloomberg.com":                                {"reliability": "established", "category": "press_economic", "region": "US", "bias": "center"},

    # ════════════════════════════════════════════════════════════
    # ESTABLISHED — Investigative
    # ════════════════════════════════════════════════════════════
    # FR
    "disclose.ngo":                                 {"reliability": "established", "category": "press_investigative", "region": "FR", "bias": "neutral"},
    "mediapart.fr":                                 {"reliability": "established", "category": "press_investigative", "region": "FR", "bias": "left"},
    # INT
    "bellingcat.com":                               {"reliability": "established", "category": "press_investigative", "region": "INT", "bias": "neutral"},
    "forbiddenstories.org":                         {"reliability": "established", "category": "press_investigative", "region": "INT", "bias": "neutral"},
    "icij.org":                                     {"reliability": "established", "category": "press_investigative", "region": "INT", "bias": "neutral"},
    # US
    "propublica.org":                               {"reliability": "established", "category": "press_investigative", "region": "US", "bias": "center-left"},

    # ════════════════════════════════════════════════════════════
    # ESTABLISHED — Audiovisual
    # ════════════════════════════════════════════════════════════
    # DE
    "dw.com":                                       {"reliability": "established", "category": "audiovisual", "region": "DE", "bias": "center"},
    # EU
    "arte.tv":                                      {"reliability": "established", "category": "audiovisual", "region": "EU", "bias": "center"},
    # FR
    "france24.com":                                 {"reliability": "established", "category": "audiovisual", "region": "FR", "bias": "center"},
    "francetvinfo.fr":                              {"reliability": "established", "category": "audiovisual", "region": "FR", "bias": "center"},
    "radiofrance.fr":                               {"reliability": "established", "category": "audiovisual", "region": "FR", "bias": "center"},
    "rfi.fr":                                       {"reliability": "established", "category": "audiovisual", "region": "FR", "bias": "center"},
    "tf1info.fr":                                   {"reliability": "established", "category": "audiovisual", "region": "FR", "bias": "center"},
    # INT
    "aljazeera.com":                                {"reliability": "established", "category": "audiovisual", "region": "INT", "bias": "center"},
    # UK
    "bbc.co.uk":                                    {"reliability": "established", "category": "audiovisual", "region": "UK", "bias": "center"},
    "bbc.com":                                      {"reliability": "established", "category": "audiovisual", "region": "UK", "bias": "center"},
    # US
    "npr.org":                                      {"reliability": "established", "category": "audiovisual", "region": "US", "bias": "center"},
    "pbs.org":                                      {"reliability": "established", "category": "audiovisual", "region": "US", "bias": "center"},

    # ════════════════════════════════════════════════════════════
    # ORIENTED — Press
    # ════════════════════════════════════════════════════════════
    # FR
    "bastamag.net":                                 {"reliability": "oriented", "category": "press_general", "region": "FR", "bias": "left"},
    "bvoltaire.fr":                                 {"reliability": "oriented", "category": "press_general", "region": "FR", "bias": "far-right"},
    "humanite.fr":                                  {"reliability": "oriented", "category": "press_general", "region": "FR", "bias": "far-left"},
    "lejdd.fr":                                     {"reliability": "oriented", "category": "press_general", "region": "FR", "bias": "right"},
    "politis.fr":                                   {"reliability": "oriented", "category": "press_general", "region": "FR", "bias": "left"},
    "regards.fr":                                   {"reliability": "oriented", "category": "press_general", "region": "FR", "bias": "left"},
    "reporterre.net":                               {"reliability": "oriented", "category": "press_general", "region": "FR", "bias": "left"},
    "valeursactuelles.com":                         {"reliability": "oriented", "category": "press_general", "region": "FR", "bias": "far-right"},
    # US
    "breitbart.com":                                {"reliability": "oriented", "category": "press_general", "region": "US", "bias": "far-right"},
    "jacobin.com":                                  {"reliability": "oriented", "category": "press_general", "region": "US", "bias": "left"},

    # ════════════════════════════════════════════════════════════
    # ORIENTED — Audiovisual
    # ════════════════════════════════════════════════════════════
    # FR
    "cnews.fr":                                     {"reliability": "oriented", "category": "audiovisual", "region": "FR", "bias": "far-right"},
    # US
    "foxnews.com":                                  {"reliability": "oriented", "category": "audiovisual", "region": "US", "bias": "far-right"},

    # ════════════════════════════════════════════════════════════
    # ORIENTED — Think tanks
    # ════════════════════════════════════════════════════════════
    # FR
    "fondapol.org":                                 {"reliability": "oriented", "category": "think_tank", "region": "FR", "bias": "center-right"},
    "ifrap.org":                                    {"reliability": "oriented", "category": "think_tank", "region": "FR", "bias": "right"},
    "institut-montaigne.org":                       {"reliability": "oriented", "category": "think_tank", "region": "FR", "bias": "center-right"},
    "ires.fr":                                      {"reliability": "oriented", "category": "think_tank", "region": "FR", "bias": "center-left"},
    "jean-jaures.org":                              {"reliability": "oriented", "category": "think_tank", "region": "FR", "bias": "center-left"},
    "terra-nova.fr":                                {"reliability": "oriented", "category": "think_tank", "region": "FR", "bias": "center-left"},
}



# ══════════════════════════════════════════════════════════════════
# Domain list builders
# ══════════════════════════════════════════════════════════════════

def get_domains(
    reliability: list[str] | None = None,
    category: list[str] | None = None,
    region: list[str] | None = None,
) -> list[str]:
    """Build a domain list filtered by reliability, category, and/or region.
    All filters are AND-combined. None = no filter on that axis.
    Returns base domains only (strips subpaths), deduplicated."""
    domains = []
    for domain, meta in DOMAIN_REGISTRY.items():
        base = domain.split("/")[0]
        if (reliability is None or meta["reliability"] in reliability) \
           and (category is None or meta["category"] in category) \
           and (region is None or meta["region"] in region):
            if base not in domains:
                domains.append(base)
    return domains


def get_domain_meta(url: str) -> dict | None:
    """Look up a URL in the registry. Checks subpaths first, then base domain."""
    from urllib.parse import urlparse
    parsed = urlparse(url if url.startswith("http") else f"https://{url}")
    domain = (parsed.netloc or "").replace("www.", "").lower()
    path = parsed.path.strip("/")

    # Check subpath match first (e.g. "lemonde.fr/les-decodeurs")
    if path:
        for key in DOMAIN_REGISTRY:
            if "/" in key and domain == key.split("/")[0] and path.startswith(key.split("/", 1)[1]):
                return DOMAIN_REGISTRY[key]

    # Check base domain
    if domain in DOMAIN_REGISTRY:
        return DOMAIN_REGISTRY[domain]

    return None