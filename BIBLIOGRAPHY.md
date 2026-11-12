# Recommended bibliography

Readings for *Economic Networks Fundamentals: Nodes, Influence, and Applications in Machine Learning*.

## Start here: the four suggested readings

| Type | Reading | Why |
| --- | --- | --- |
| Book, introductory | Wilson, R. J. *Introduction to Graph Theory*. Pearson. | Notation, Euler, paths, trees: Part 1 in depth |
| Book chapter, diffusion | Shakarian, P., Bhatnagar, A., Aleali, A., Shaabani, E. and Guo, R. (2015). [The Independent Cascade and Linear Threshold Models](https://doi.org/10.1007/978-3-319-23105-1_4). Ch. 4 of *Diffusion in Social Networks*. Springer. | Word of mouth (the dean) and threshold contagion (bank runs) |
| Book, machine learning | Vapnik, V. N. (2000). *The Nature of Statistical Learning Theory*, 2nd ed. Springer. | The framing of Part 3: learning from data and when it generalises |
| Online course, graph neural networks | Ribeiro, A. [Graph Neural Networks](https://gnn.seas.upenn.edu/). University of Pennsylvania. | The advanced follow-up to Part 3 |

## To go further

- Barabási, A.-L. (2016). [*Network Science*](https://networksciencebook.com/). Cambridge University Press. Free online.
- Jackson, M. O. (2008). *Social and Economic Networks*. Princeton University Press.
- Stanford CS224W, [Machine Learning with Graphs](https://web.stanford.edu/class/cs224w/). Free lecture materials.
- Newman, M. (2018). *Networks*, 2nd ed. Oxford University Press.

## Part 1 · Nodes: structure and representation

**Cops and robbers**

- Olsen, A. (2023). [Cops and Robbers: A Game of Pursuit on Graphs](https://doi.org/10.1016/j.procs.2023.07.058). *Procedia Computer Science* 221, 434–441. *The examples in our game, with her labels.*
- Nowakowski, R. and Winkler, P. (1983). Vertex-to-vertex pursuit in a graph. *Discrete Mathematics* 43, 235–239. Quilliot, A. (1978), doctoral thesis, Université de Paris VI. *Cop-win = dismantlable.*
- Aigner, M. and Fromme, M. (1984). A game of cops and robbers. *Discrete Applied Mathematics* 8, 1–12. *Planar networks never need more than 3 cops.*
- Bonato, A. and Nowakowski, R. J. (2011). *The Game of Cops and Robbers on Graphs*. American Mathematical Society. *The textbook on the topic.*

**Euler and routing**

- Euler, L. (1741, dated 1736). Solutio problematis ad geometriam situs pertinentis. *Commentarii academiae scientiarum Petropolitanae* 8, 128–140.
- Edmonds, J. and Johnson, E. L. (1973). Matching, Euler tours and the Chinese postman. *Mathematical Programming* 5, 88–124.

**Shortest paths, search and decisions**

- Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik* 1, 269–271.
- Travers, J. and Milgram, S. (1969). An experimental study of the small world problem. *Sociometry* 32(4), 425–443.
- Russell, S. and Norvig, P. *Artificial Intelligence: A Modern Approach*, 4th ed. Pearson. *Search (uniform cost, A\*) and decision networks; also UC Berkeley CS188 notes.*
- Kempe, D., Kleinberg, J. and Tardos, É. (2003). Maximizing the spread of influence through a social network. *Proceedings of KDD*, 137–146.

**Centrality**

- Freeman, L. C. (1977). A set of measures of centrality based on betweenness. *Sociometry* 40(1), 35–41.
- Bonacich, P. (1987). Power and centrality: a family of measures. *American Journal of Sociology* 92(5), 1170–1182.
- Brin, S. and Page, L. (1998). The anatomy of a large-scale hypertextual web search engine. *Computer Networks and ISDN Systems* 30, 107–117.
- Krackhardt, D. (1990). Assessing the political landscape: structure, cognition, and power in organizations. *Administrative Science Quarterly* 35(2), 342–369. *The kite.*

## Part 2 · Influence: diffusion and contagion

**Hubs and trade**

- Tinbergen, J. (1962). *Shaping the World Economy*. Twentieth Century Fund. *The gravity model.*
- Anderson, J. E. and van Wincoop, E. (2003). Gravity with gravitas: a solution to the border puzzle. *American Economic Review* 93(1), 170–192.
- Barabási, A.-L. and Albert, R. (1999). [Emergence of scaling in random networks](https://doi.org/10.1126/science.286.5439.509). *Science* 286, 509–512.
- Albert, R., Jeong, H. and Barabási, A.-L. (2000). Error and attack tolerance of complex networks. *Nature* 406, 378–382.

**Contagion on networks**

- Kermack, W. O. and McKendrick, A. G. (1927). A contribution to the mathematical theory of epidemics. *Proceedings of the Royal Society A* 115, 700–721.
- Wang, Y., Chakrabarti, D., Wang, C. and Faloutsos, C. (2003). Epidemic spreading in real networks: an eigenvalue viewpoint. *Proceedings of SRDS*, 25–34. *The threshold β/γ > 1/λmax.*
- Pastor-Satorras, R. and Vespignani, A. (2001). Epidemic spreading in scale-free networks. *Physical Review Letters* 86, 3200–3203.
- Granovetter, M. (1978). Threshold models of collective behavior. *American Journal of Sociology* 83(6), 1420–1443.
- Centola, D. (2010). The spread of behavior in an online social network experiment. *Science* 329, 1194–1197.
- Banerjee, A., Chandrasekhar, A. G., Duflo, E. and Jackson, M. O. (2013). The diffusion of microfinance. *Science* 341.

**Dynamic networks**

- Holme, P. and Saramäki, J. (2012). Temporal networks. *Physics Reports* 519(3), 97–125.
- Gross, T., D'Lima, C. J. D. and Blasius, B. (2006). Epidemic dynamics on an adaptive network. *Physical Review Letters* 96, 208701.

**Spectral graphs**

- Fiedler, M. (1973). Algebraic connectivity of graphs. *Czechoslovak Mathematical Journal* 23(2), 298–305.

**Financial networks and crises**

- Allen, F. and Gale, D. (2000). Financial contagion. *Journal of Political Economy* 108(1), 1–33.
- Gai, P. and Kapadia, S. (2010). Contagion in financial networks. *Proceedings of the Royal Society A* 466, 2401–2423.
- Acemoglu, D., Ozdaglar, A. and Tahbaz-Salehi, A. (2015). Systemic risk and stability in financial networks. *American Economic Review* 105(2), 564–608.
- Eisenberg, L. and Noe, T. H. (2001). Systemic risk in financial systems. *Management Science* 47(2), 236–249.
- Battiston, S., Puliga, M., Kaushik, R., Tasca, P. and Caldarelli, G. (2012). DebtRank: too central to fail? *Scientific Reports* 2, 541.
- Diamond, D. W. and Dybvig, P. H. (1983). Bank runs, deposit insurance, and liquidity. *Journal of Political Economy* 91(3), 401–419.
- Gorton, G. and Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics* 104(3), 425–451.
- Caballero, R. J. and Simsek, A. (2013). Fire sales in a model of complexity. *Journal of Finance* 68(6), 2549–2587.
- Heider, F., Hoerova, M. and Holthausen, C. (2015). Liquidity hoarding and interbank market rates: the role of counterparty risk. *Journal of Financial Economics* 118(2), 336–354.
- Craig, B. and von Peter, G. (2014). Interbank tiering and money center banks. *Journal of Financial Intermediation* 23(3), 322–347.
- Shleifer, A. and Vishny, R. (2011). Fire sales in finance and macroeconomics. *Journal of Economic Perspectives* 25(1), 29–48.
- Basel Committee on Banking Supervision (2010, revised 2011). *Basel III: A global regulatory framework for more resilient banks and banking systems*. Bank for International Settlements.

**For the stories (non-technical)**

- Lewis, M. (2010). *The Big Short*. W. W. Norton.
- Financial Crisis Inquiry Commission (2011). *The Financial Crisis Inquiry Report*. US Government.
- Sorkin, A. R. (2009). *Too Big to Fail*. Viking.

## Part 3 · Applications: machine learning and useful notes

**Prediction on networks**

- Manski, C. F. (1993). Identification of endogenous social effects: the reflection problem. *Review of Economic Studies* 60(3), 531–542.
- Steglich, C., Snijders, T. A. B. and Pearson, M. (2010). Dynamic networks and behavior: separating selection from influence. *Sociological Methodology* 40, 329–393. *Uses the Glasgow school data from our lab.*
- Acemoglu, D., Carvalho, V. M., Ozdaglar, A. and Tahbaz-Salehi, A. (2012). The network origins of aggregate fluctuations. *Econometrica* 80(5), 1977–2016.

**Knowledge graphs and literature reviews**

- Hogan, A., Blomqvist, E., Cochez, M., et al. (2021). [Knowledge Graphs](https://doi.org/10.1145/3447772). *ACM Computing Surveys* 54(4), article 71. *The main reference for our knowledge-graph lab.*
- Bordes, A., Usunier, N., García-Durán, A., Weston, J. and Yakhnenko, O. (2013). Translating embeddings for modeling multi-relational data. *Advances in Neural Information Processing Systems* 26. *TransE.*
- Wohlin, C. (2014). Guidelines for snowballing in systematic literature studies and a replication in software engineering. *Proceedings of EASE*.
- Small, H. (1973). Co-citation in the scientific literature. *Journal of the American Society for Information Science* 24(4), 265–269.
- Kessler, M. M. (1963). Bibliographic coupling between scientific papers. *American Documentation* 14(1), 10–25.
- [OpenAlex](https://openalex.org/): free, open catalogue of research used by `kg_lab`.

**Planning the TFM**

- Kelley, J. E. and Walker, M. R. (1959). Critical-path planning and scheduling. *Proceedings of the Eastern Joint Computer Conference*, 160–173.

---

Links are given where they were checked; for the rest, search the title in Google Scholar or OpenAlex.
