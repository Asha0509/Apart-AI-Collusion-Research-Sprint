# Citation verification

Checked 2026-10-24 (IST) by Claude Code. Sources: PRD.md §2 ("We do NOT claim" table, "Must cite"), §4 Definitions box, §9 legal context, and `starter/literature/`.
Method: every arXiv ID was resolved with the arXiv MCP (`get_abstract`; full-text search where the abstract did not settle the claim). Non-arXiv items were checked against the publisher, repository, court or DOJ page. Quotes are verbatim from the abstract unless marked "(full text)".

Legend: **Verified** = the ID resolves and title/authors match the PRD's reference. **Supports** = the source backs the specific claim the PRD makes about it.

## 1. Reference table

| # | PRD reference (claimed ID) | Verified? | Exact title | Authors | Year | Venue | Claim PRD attributes | Supports? | Evidence (quote) | URL |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Fish 2404.00806 | yes | Algorithmic Collusion by Large Language Models | Sara Fish, Yannai A. Gonczarowski, Ran I. Shorrer | 2024 | arXiv preprint (econ.GN) | "Mid-run reset is new" is already shown; also the source of the price-based ("lenient") definition | yes (full text; abstract alone only partly) | (full text) "our simulation can be reset to any point in the middle of an already-completed run ... This allows us to counterfactually modify an agent's plans and insights at any period". Definition (full text, quoting Abada et al.): "Algorithmic collusion is when supracompetitive outcomes are produced by learning algorithms without human design to produce those outcomes." | https://arxiv.org/abs/2404.00806 |
| 2 | Tran & Yu 2610.28787 | yes | Is Anyone Enforcing the Cartel? What Reinforcement Learning Teaches LLM Agents in Markets | Hieu Tran, Hong Yu | 2026 | arXiv preprint (cs.CL) | "First forced-deviation test for LLMs"; forced-cut audit | partly | "We introduce an audit that tests enforcement by forcing a member to cheat in counterfactual copies of a market". Says "introduce", not "first". Arslan et al. 2609.35402 (submitted earlier, 28 Sep 2026) already uses "a forced-deviation probe", and Fish 2404.00806 already resets runs and perturbs them off-path. Write "Tran & Yu introduce an enforcement audit", not "first". | https://arxiv.org/abs/2610.28787 |
| 3 | Luo 2602.17203 | yes | Algorithmic Collusion at Test Time: A Meta-game Design and Evaluation | Yuhong Luo, Daniel Schoepflin, Xintong Wang | 2026 | arXiv preprint (cs.MA) | History shapes LLM pricing | yes (full text; abstract partly) | Abstract: agents "possessing pretrained policies ... combines a pretrained, initial policy with an in-game adaptation rule". (full text) "LLM-based agents can demonstrate adaptive behavior guided by pre-game history: policies that exhibit greater collusion during pre-game interactions tend to sustain or re-establish collusion" | https://arxiv.org/abs/2602.17203 |
| 4 | Bichler 2610.21711 | yes | How language model agents reshape price competition | Martin Bichler, Philip Hierhager, Kassian Köck, Fabian Pieroth | 2026 | arXiv preprint (cs.GT) | History shapes LLM pricing | yes | "Agents that post one price every period from raw market histories that include rival prices can sustain supracompetitive regimes in self-play. Agents that ... emit probability distributions from summarized histories of their own profits instead move toward the competitive region" | https://arxiv.org/abs/2610.21711 |
| 5 | Lee 2610.11256 | yes | Who Leads and Who Collects: Algorithmic Collusion in Markets of Heterogeneous Language Models | Jun Yeong Lee | 2026 | arXiv preprint (econ.GN) | Provider matters | yes | "Four language models from four providers ... Collusion is a property of the model: Claude and Gemini markets reach 72 to 79 percent of the monopoly rent, DeepSeek markets 24 percent, and GPT markets none" | https://arxiv.org/abs/2610.11256 |
| 6 | Keppo 2603.20281 | yes | On the Fragility of AI Agent Collusion | Jussi Keppo, Yuze Li, Gerry Tsoukalas, Nuo Yuan | 2026 | arXiv preprint (cs.GT) | Heterogeneity matters; price-based ("lenient") definition | yes | "We show that collusion is fragile under the heterogeneity typical of real deployments." Definition (full text): "tacit collusion enforcement proceeds by targeting conduct, not cognition. Outcome measurement ... is the policy-relevant quantity" | https://arxiv.org/abs/2603.20281 |
| 7 | Garra 2609.13037 | yes | Mitigating Emergent Collusion in LLM Pricing Agents | Abdullah Garra | 2026 | arXiv preprint (cs.GT) | Entrants lower prices | yes | "The active entrant produces the strongest effect, pushing both prompts below the appropriate random-entrant Nash benchmark." | https://arxiv.org/abs/2609.13037 |
| 8 | Goppelsroeder 2009 / MPRA 14707 | yes | Entry in Collusive Markets: An Experimental Study | Marie Goppelsroeder | 2009 | MPRA Paper No. 14707 | Informed newcomers imitate | yes | "collusion is indeed easier to sustain in the latter case than in groups starting large" (the latter case = the entrant is known to be informed about the group's history). The abstract also reports that entrants tend to imitate their group's behaviour (paraphrased; the page was not quoted in full). | https://mpra.ub.uni-muenchen.de/14707/ |
| 9 | Eschenbaum (OpenReview BztUFukcBry) | yes, with caveat | Robust Algorithmic Collusion | Workshop version: Nicolas Eschenbaum, Philipp Zahn. arXiv version 2201.00345: Nicolas Eschenbaum, Filip Mellgren, Philipp Zahn | 2021 (NeurIPS workshop) / 2022 (arXiv) | NeurIPS 2021 Workshop on Political Economy of Reinforcement Learning Systems (PERLS), poster; arXiv 2201.00345 | Must cite; no specific claim (repo: collusion breaks when agents are rematched) | yes | arXiv abstract: "We find that in testing environments collusion consistently breaks down. Instead, we observe static Nash play." The NeurIPS virtual page maps forum ID BztUFukcBry to this poster. OpenReview itself blocked automated access, so its author list was confirmed only through the NeurIPS page. | https://openreview.net/forum?id=BztUFukcBry ; https://neurips.cc/virtual/2021/49120 ; https://arxiv.org/abs/2201.00345 |
| 10 | Goyal & Ray 2609.05339 | yes | Does Your Agent's Memory Survive a Model Upgrade? A Controlled Study of Memory Portability | Ankit Goyal, Jaideep Ray | 2026 | arXiv preprint (cs.AI) | Notes transfer poorly across models | partly | "compressed NOTES exhibit high model coupling, with accuracy shifting asymmetrically by +9.91 or −13.28 percentage points depending on the specific migration direction". The shift depends on direction: one direction gains. The setting is factual-recall memory with two open-weight models under 10B, not strategy. Write "natural-language notes are model-coupled; transfer depends on direction", not "transfer poorly". | https://arxiv.org/abs/2609.05339 |
| 11 | Wang 2605.16746 | yes | State Contamination in Memory-Augmented LLM Agents | Yian Wang, Agam Goyal, Yuen Chen, Hari Sundaram | 2026 | arXiv preprint (cs.AI) | Already uses the term "memory laundering" | yes | "We study a failure mode we call memory laundering" | https://arxiv.org/abs/2605.16746 |
| 12 | Xu 2607.29167 | yes | Memory Provenance Laundering in LLM Agents: A Non-Amplification Firewall for Persistent Memory | Jinghan Xu, Yiyong Xiao, Wanru Shao, Hankai Liu, Xinjin Li | 2026 | arXiv preprint (cs.CR) | Term clash ("memory laundering") | yes (the term is "memory provenance laundering") | "We identify memory provenance laundering" | https://arxiv.org/abs/2607.29167 |
| 13 | Calvano AER 2020 | yes | Artificial Intelligence, Algorithmic Pricing, and Collusion | Emilio Calvano, Giacomo Calzolari, Vincenzo Denicolò, Sergio Pastorello | 2020 | American Economic Review 110(10): 3267–97, doi:10.1257/aer.20190623 | Reward–punishment ("strict") definition | yes | "The high prices are sustained by collusive strategies with a finite phase of punishment followed by a gradual return to cooperation." | https://www.aeaweb.org/articles?id=10.1257/aer.20190623 |
| 14 | Riemer 2608.18078 | yes | Position: Collusion Risks Among AI Reasoning Agents Justify Certification Requirements for Making Market Decisions | Matthew Riemer, Tommaso Tosato, Amin Memarian, Maximilian Puelma Touzel, Glen Berseth, Irina Rish, Guillaume Dumas | 2026 | arXiv preprint (cs.AI), position paper | Successor certification as a mitigation | partly | "should be required to obtain behavioral certification before making decisions that affect economic markets". It proposes certification in general, not certification of a successor after a model swap. Applying it to swaps is our extension. Anomaly: arXiv reports the published date as 2026-05-29, while ID 2608 implies August 2026. Check the arXiv page before finalising the year. | https://arxiv.org/abs/2608.18078 |
| 15 | Arslan et al. 2026 (repo Q1.2 list) | yes | Persistent Partners Raise Prices Among Learning Agents | Paul-Peter Arslan, Yubin Kim, Xiao Xiao | 2026 | arXiv 2609.35402 (cs.LG) | Listed in the repo Q1.2 reading list (confirmed in `starter/literature/README.md`) | n/a (no specific claim) | "Keeping the same partner raises the level of profits ... by 0.27 of the gap between competitive and monopoly profit" | https://arxiv.org/abs/2609.35402 |
| 16 | Werner 2026 (repo Q1.2 list) | yes | Algorithmic and Human Collusion | Tobias Werner | 2026 | The Economic Journal (advance article), doi:10.1093/ej/ueag013 | Listed in the repo Q1.2 reading list (confirmed) | n/a (no specific claim) | The DOI resolves to the Economic Journal page titled "Algorithmic and Human Collusion". Author and year are confirmed through the Southampton eprint (510359) and the author's Maynooth profile. The abstract was not quoted from the publisher page because the fetch was truncated. | https://doi.org/10.1093/ej/ueag013 |
| 17 | Harrington (Definitions box) | yes | Developing Competition Law for Collusion by Autonomous Artificial Agents | Joseph E. Harrington, Jr. | 2018 | Journal of Competition Law & Economics 14(3): 331–363, doi:10.1093/joclec/nhy016 | Reward–punishment ("strict") definition | partly (abstract); yes through the repo definitions table | Abstract: "offers a path toward making collusion by autonomous artificial agents unlawful". The reward–punishment definition comes from `starter/literature/definitions/README.md` ("firms using strategies embodying a reward-punishment scheme ..."). The full text is paywalled and was not read. Check a quote in the PDF before using one. | https://academic.oup.com/jcle/article/14/3/331/5292366 |
| 18 | Rose et al. (Definitions box, "Coordination only") | yes | Detecting Multi-Agent Collusion Through Multi-Agent Interpretability | Aaron Rose, Carissa Cullen, Sahar Abdelnabi, Philip Torr, Brandon Gary Kaplowitz, Christian Schroeder de Witt | 2026 | arXiv 2604.01151 (cs.AI) | "Coordination only" category | partly; frame it carefully | (full text, §4.3) "agents must actively communicate, whether explicitly or implicitly, to collude. Otherwise, the agents are just coordinating or cooperating." Rose et al. define collusion as communication plus harmful action. They do **not** define "coordination-only collusion"; they classify tacit coordination as *not* collusion. Write "coordination without communication, which Rose et al. would not call collusion". | https://arxiv.org/abs/2604.01151 |
| 19 | RealPage DOJ settlement, 12-month data rule | yes | Justice Department Requires RealPage to End the Sharing of Competitively Sensitive Information and Alignment of Pricing Among Competitors (press release) | U.S. Department of Justice, Office of Public Affairs | 2025 (24 Nov) | DOJ press release; *United States v. RealPage, Inc.*, No. 1:24-cv-00710 (M.D.N.C.), proposed final judgment | 12-month data rule | yes | "limiting model training to historic or backward-looking nonpublic data that has been aged for at least 12 months". The judgment was *proposed* (Tunney Act); entry was not confirmed, so call it a "proposed consent judgment". | https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and |
| 20 | *Gibson v. Cendyn* | yes | *Gibson v. Cendyn Group, LLC*, No. 24-3576 (9th Cir. Aug. 15, 2025) (published opinion, Bea, J.) | — | 2025 | U.S. Court of Appeals for the Ninth Circuit | Legal analogy | yes | (slip op. summary) "plaintiffs failed to state a claim under Section 1 of the Sherman Act by alleging that competing hotels independently purchased licenses for software that provided pricing recommendations" | https://cdn.ca9.uscourts.gov/datastore/opinions/2025/08/15/24-3576.pdf |
| 21 | *Cornish-Adebiyi v. Caesars* (3rd Cir. 2026) | yes | *Cornish-Adebiyi v. Caesars Entertainment, Inc.*, No. 24-3006 (3d Cir. 2026) (precedential) | — | 2026 | U.S. Court of Appeals for the Third Circuit | Legal analogy | yes | Caption, docket number and "PRECEDENTIAL" read from the slip opinion. Law-firm alerts (Covington, Arnold & Porter, Morgan Lewis) give the decision date as 29 July 2026 and the outcome as reversing dismissal. I did not read that from the opinion text, so check the date and holding in the slip opinion before writing pin cites. | https://www2.ca3.uscourts.gov/opinarch/243006p.pdf |
| 22 | Repo `literature/definitions/` | yes (file exists) | `starter/literature/definitions/README.md`: definitions of collusion in 139 papers, each broken into 18 components, plus a clustering | Sprint organisers (pre-existing repo, see PREEXISTING.md) | 2026 | Repository file | Source of the three-way definitions box | yes | Line 5: "two main families: economics definitions based on prices and AI-safety definitions based on unwanted, covert coordination". Cite it as the repo, not as a paper. | `starter/literature/definitions/README.md` |

### Definition sources in the repo's `starter/literature/definitions/README.md`
Each row was cross-checked against the primary source above.

| Definition family (PRD box) | Repo row (README line) | Primary source verified |
|---|---|---|
| Price-based (lenient) | Fish et al. 2024 (l.32): "Supracompetitive outcomes produced by learning algorithms 'without human design'" | #1 (full-text quote matches) |
| Price-based (lenient) | Keppo et al. 2026 (l.35): "prices in (Nash, monopoly] sustained by grim-trigger punishment; 'conduct, not cognition'" | #6. Note that the repo row also mentions grim-trigger punishment, so Keppo is not purely price-based. Their *measurement* is outcome-based (price convergence and elevation). |
| Reward–punishment (strict) | Harrington 2018 (l.128): "strategies embodying a reward-punishment scheme ...; intent, communication and agreement not needed" | #17 (metadata verified; definition only in the repo table) |
| Reward–punishment (strict) | Calvano et al. 2020a (l.79): "Supracompetitive prices sustained in equilibrium by a reward–punishment scheme" | #13 |
| Coordination only | Rose et al. 2026 (l.42): "Communication (direct or indirect) **plus** harmful action; tacit coordination without communication is *not* collusion" | #18 (full text matches) |
| (also relevant) | Eschenbaum et al. 2022 (l.44): "Tacit algorithmic collusion: collusion index M plus reward–punishment policies" | #9 |

## 2. BibTeX (verified entries only)

```bibtex
@misc{fish2024algorithmic,
  title         = {Algorithmic Collusion by Large Language Models},
  author        = {Fish, Sara and Gonczarowski, Yannai A. and Shorrer, Ran I.},
  year          = {2024},
  eprint        = {2404.00806},
  archivePrefix = {arXiv},
  primaryClass  = {econ.GN}
}

@misc{tran2026enforcing,
  title         = {Is Anyone Enforcing the Cartel? What Reinforcement Learning Teaches {LLM} Agents in Markets},
  author        = {Tran, Hieu and Yu, Hong},
  year          = {2026},
  eprint        = {2610.28787},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL}
}

@misc{luo2026testtime,
  title         = {Algorithmic Collusion at Test Time: A Meta-game Design and Evaluation},
  author        = {Luo, Yuhong and Schoepflin, Daniel and Wang, Xintong},
  year          = {2026},
  eprint        = {2602.17203},
  archivePrefix = {arXiv},
  primaryClass  = {cs.MA}
}

@misc{bichler2026reshape,
  title         = {How language model agents reshape price competition},
  author        = {Bichler, Martin and Hierhager, Philip and K{\"o}ck, Kassian and Pieroth, Fabian},
  year          = {2026},
  eprint        = {2610.21711},
  archivePrefix = {arXiv},
  primaryClass  = {cs.GT}
}

@misc{lee2026wholeads,
  title         = {Who Leads and Who Collects: Algorithmic Collusion in Markets of Heterogeneous Language Models},
  author        = {Lee, Jun Yeong},
  year          = {2026},
  eprint        = {2610.11256},
  archivePrefix = {arXiv},
  primaryClass  = {econ.GN}
}

@misc{keppo2026fragility,
  title         = {On the Fragility of {AI} Agent Collusion},
  author        = {Keppo, Jussi and Li, Yuze and Tsoukalas, Gerry and Yuan, Nuo},
  year          = {2026},
  eprint        = {2603.20281},
  archivePrefix = {arXiv},
  primaryClass  = {cs.GT}
}

@misc{garra2026mitigating,
  title         = {Mitigating Emergent Collusion in {LLM} Pricing Agents},
  author        = {Garra, Abdullah},
  year          = {2026},
  eprint        = {2609.13037},
  archivePrefix = {arXiv},
  primaryClass  = {cs.GT}
}

@techreport{goppelsroeder2009entry,
  title       = {Entry in Collusive Markets: An Experimental Study},
  author      = {Goppelsroeder, Marie},
  year        = {2009},
  institution = {University Library of Munich},
  type        = {MPRA Paper},
  number      = {14707},
  url         = {https://mpra.ub.uni-muenchen.de/14707/}
}

@inproceedings{eschenbaum2021robust,
  title     = {Robust Algorithmic Collusion},
  author    = {Eschenbaum, Nicolas and Zahn, Philipp},
  year      = {2021},
  booktitle = {NeurIPS 2021 Workshop on Political Economy of Reinforcement Learning Systems (PERLS)},
  url       = {https://openreview.net/forum?id=BztUFukcBry}
}

@misc{eschenbaum2022robust,
  title         = {Robust Algorithmic Collusion},
  author        = {Eschenbaum, Nicolas and Mellgren, Filip and Zahn, Philipp},
  year          = {2022},
  eprint        = {2201.00345},
  archivePrefix = {arXiv},
  primaryClass  = {econ.GN}
}

@misc{goyal2026memory,
  title         = {Does Your Agent's Memory Survive a Model Upgrade? A Controlled Study of Memory Portability},
  author        = {Goyal, Ankit and Ray, Jaideep},
  year          = {2026},
  eprint        = {2609.05339},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI}
}

@misc{wang2026state,
  title         = {State Contamination in Memory-Augmented {LLM} Agents},
  author        = {Wang, Yian and Goyal, Agam and Chen, Yuen and Sundaram, Hari},
  year          = {2026},
  eprint        = {2605.16746},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI}
}

@misc{xu2026provenance,
  title         = {Memory Provenance Laundering in {LLM} Agents: A Non-Amplification Firewall for Persistent Memory},
  author        = {Xu, Jinghan and Xiao, Yiyong and Shao, Wanru and Liu, Hankai and Li, Xinjin},
  year          = {2026},
  eprint        = {2607.29167},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CR}
}

@article{calvano2020artificial,
  title   = {Artificial Intelligence, Algorithmic Pricing, and Collusion},
  author  = {Calvano, Emilio and Calzolari, Giacomo and Denicol{\`o}, Vincenzo and Pastorello, Sergio},
  journal = {American Economic Review},
  volume  = {110},
  number  = {10},
  pages   = {3267--3297},
  year    = {2020},
  doi     = {10.1257/aer.20190623}
}

@misc{riemer2026position,
  title         = {Position: Collusion Risks Among {AI} Reasoning Agents Justify Certification Requirements for Making Market Decisions},
  author        = {Riemer, Matthew and Tosato, Tommaso and Memarian, Amin and Puelma Touzel, Maximilian and Berseth, Glen and Rish, Irina and Dumas, Guillaume},
  year          = {2026},
  eprint        = {2608.18078},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI}
}

@misc{arslan2026persistent,
  title         = {Persistent Partners Raise Prices Among Learning Agents},
  author        = {Arslan, Paul-Peter and Kim, Yubin and Xiao, Xiao},
  year          = {2026},
  eprint        = {2609.35402},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG}
}

@article{werner2026algorithmic,
  title   = {Algorithmic and Human Collusion},
  author  = {Werner, Tobias},
  journal = {The Economic Journal},
  year    = {2026},
  doi     = {10.1093/ej/ueag013},
  note    = {Advance article}
}

@article{harrington2018developing,
  title   = {Developing Competition Law for Collusion by Autonomous Artificial Agents},
  author  = {Harrington, Jr., Joseph E.},
  journal = {Journal of Competition Law \& Economics},
  volume  = {14},
  number  = {3},
  pages   = {331--363},
  year    = {2018},
  doi     = {10.1093/joclec/nhy016}
}

@misc{rose2026detecting,
  title         = {Detecting Multi-Agent Collusion Through Multi-Agent Interpretability},
  author        = {Rose, Aaron and Cullen, Carissa and Abdelnabi, Sahar and Torr, Philip and Kaplowitz, Brandon Gary and Schroeder de Witt, Christian},
  year          = {2026},
  eprint        = {2604.01151},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI}
}

@misc{doj2025realpage,
  title        = {Justice Department Requires {RealPage} to End the Sharing of Competitively Sensitive Information and Alignment of Pricing Among Competitors},
  author       = {{U.S. Department of Justice, Office of Public Affairs}},
  year         = {2025},
  month        = nov,
  howpublished = {Press release, 24 November 2025},
  url          = {https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and}
}

@misc{gibson2025cendyn,
  title        = {Gibson v. Cendyn Group, LLC, No. 24-3576},
  author       = {{U.S. Court of Appeals for the Ninth Circuit}},
  year         = {2025},
  howpublished = {Opinion filed 15 August 2025},
  url          = {https://cdn.ca9.uscourts.gov/datastore/opinions/2025/08/15/24-3576.pdf}
}

@misc{cornishadebiyi2026caesars,
  title        = {Cornish-Adebiyi v. Caesars Entertainment, Inc., No. 24-3006},
  author       = {{U.S. Court of Appeals for the Third Circuit}},
  year         = {2026},
  howpublished = {Precedential opinion},
  url          = {https://www2.ca3.uscourts.gov/opinarch/243006p.pdf}
}
```

## 3. UNVERIFIED / DO NOT CITE (as currently worded)

No reference failed to resolve: all 22 exist and match. The items below are **claims or details** that must not go into the report as the PRD currently words them.

1. **"Tran & Yu: first forced-deviation test for LLMs."** The paper says "introduce", not "first". Arslan et al. 2609.35402 (earlier) uses a forced-deviation probe, including an exploratory LLM extension, and Fish et al. 2404.00806 already perturbs runs off-path. Do not write "first".
2. **"Goyal & Ray: notes transfer poorly across models."** The effect depends on direction (+9.91 / −13.28 pp), was measured on factual-recall memory with two models under 10B, and covers no strategic state. Cite it as "notes are model-coupled", not "transfer poorly".
3. **"Coordination only (Rose et al.)" as a type of collusion.** Rose et al. say coordination without communication is *not* collusion. Frame it as their exclusion, not their definition.
4. **Riemer 2608.18078 year and "successor certification".** The year is inconsistent (published 2026-05-29 vs ID 2608); check it on arXiv. The paper proposes behavioural certification, not *successor* certification. Attribute "successor" to us.
5. **Harrington 2018 definition quote.** Metadata is verified, but the full text is paywalled and was not read. Do not put a direct quote in the report until it is checked against the PDF. Paraphrase through the repo table only.
6. **Cornish-Adebiyi date and holding.** The 29 July 2026 date and the "reversed dismissal" outcome come from law-firm alerts, not from the opinion text I read. Check both in the slip opinion before stating them.
7. **RealPage "settlement".** It is a *proposed* final judgment (24 Nov 2025). Court entry was not confirmed, so do not call it final or entered.
8. **Eschenbaum author list.** The OpenReview/NeurIPS 2021 workshop version has 2 authors (Eschenbaum, Zahn), the arXiv version 3 (adds Mellgren). Cite the version you mean; do not mix them.
9. **Werner 2026 abstract content.** Only title, author, journal, year and DOI are verified. Do not attribute findings to it without reading the article.
