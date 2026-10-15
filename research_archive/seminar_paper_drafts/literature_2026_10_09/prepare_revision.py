"""Prepare the literature revision without overwriting the original draft."""
from pathlib import Path
import json,re

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
source=(BASE/'source/01_main_paper.md').read_text()
intro=(HERE/'source/expanded_introduction.md').read_text().strip()
source=re.sub(r'## 1 Introduction\n.*?(?=## 2 Original study and replication)',intro+'\n\n',source,flags=re.S)
source=source.replace('Reference draft prepared on October 7 2026','Reference draft revised on October 9 2026')
source=source.replace('the baseline-controlled post-test total coefficient is 0.173 with standard error 0.087 in 1,760 source records.','the Panel A post-test total specification with child baseline-test controls gives a coefficient of 0.173 with standard error 0.087 in 1,760 source records.')
source=source.replace('This reference draft was generated with OpenAI Codex on October 7, 2026.','This reference draft was generated with OpenAI Codex on October 7, 2026, and its literature discussion was expanded on October 9, 2026 using the Tel Aviv University library catalogue and verified journal articles.')
refs='''## References

Banerjee, Abhijit V., Shawn Cole, Esther Duflo, and Leigh Linden. 2007. "Remedying Education: Evidence from Two Randomized Experiments in India." Quarterly Journal of Economics 122 (3): 1235-1264. https://doi.org/10.1162/qjec.122.3.1235.

Cameron, A. Colin, Jonah B. Gelbach, and Douglas L. Miller. 2008. "Bootstrap-Based Improvements for Inference with Clustered Errors." Review of Economics and Statistics 90 (3): 414-427. https://doi.org/10.1162/rest.90.3.414.

Cilliers, Jacobus, Ibrahim Kasirye, Clare Leaver, Pieter Serneels, and Andrew Zeitlin. 2018. "Pay for Locally Monitored Performance? A Welfare Analysis for Teacher Attendance in Ugandan Primary Schools." Journal of Public Economics 167: 69-90. https://doi.org/10.1016/j.jpubeco.2018.04.010.

Duflo, Esther, Pascaline Dupas, and Michael Kremer. 2011. "Peer Effects, Teacher Incentives, and the Impact of Tracking: Evidence from a Randomized Evaluation in Kenya." American Economic Review 101 (5): 1739-1774. https://doi.org/10.1257/aer.101.5.1739.

Duflo, Esther, Rema Hanna, and Stephen P. Ryan. 2012. "Incentives Work: Getting Teachers to Come to School." American Economic Review 102 (4): 1241-1278. https://doi.org/10.1257/aer.102.4.1241. Includes the official supplemental appendix and erratum linked from the journal page.

Glewwe, Paul, Nauman Ilias, and Michael Kremer. 2010. "Teacher Incentives." American Economic Journal: Applied Economics 2 (3): 205-227. https://doi.org/10.1257/app.2.3.205.

Guerrero, Gabriela, Juan León, Mayli Zapata, and Santiago Cueto. 2013. "Getting Teachers Back to the Classroom. A Systematic Review on What Works to Improve Teacher Attendance in Developing Countries." Journal of Development Effectiveness 5 (4): 466-488. https://doi.org/10.1080/19439342.2013.864695.

Holm, Sture. 1979. "A Simple Sequentially Rejective Multiple Test Procedure." Scandinavian Journal of Statistics 6 (2): 65-70. https://www.jstor.org/stable/4615733.

Kremer, Michael, Nazmul Chaudhury, F. Halsey Rogers, Karthik Muralidharan, and Jeffrey Hammer. 2005. "Teacher Absence in India: A Snapshot." Journal of the European Economic Association 3 (2-3): 658-667. https://doi.org/10.1162/jeea.2005.3.2-3.658.

Linden, Leigh L., and Gauri Kartini Shastry. 2012. "Grain Inflation: Identifying Agent Discretion in Response to a Conditional School Nutrition Program." Journal of Development Economics 99 (1): 128-138. https://doi.org/10.1016/j.jdeveco.2011.11.002.

Muralidharan, Karthik, and Venkatesh Sundararaman. 2011. "Teacher Performance Pay: Experimental Evidence from India." Journal of Political Economy 119 (1): 39-77. https://doi.org/10.1086/659655.

### Data source

Duflo, Esther, Rema Hanna, and Stephen P. Ryan. 2019. "Replication Data for Incentives Work Getting Teachers to Come to School." Version 1. American Economic Association and Inter-university Consortium for Political and Social Research. Original data publication 2012; distribution date October 11, 2019. https://doi.org/10.3886/E112523V1. This dataset citation records empirical provenance and is separate from the peer-reviewed literature.

'''
source=re.sub(r'## References\n.*?(?=\[\[PAGEBREAK\]\]\n\n## Appendix A)',refs,source,flags=re.S)
(HERE/'source/01_main_paper_literature_expanded.md').write_text(source)

registry=json.loads((HERE/'source/tau_catalog_records.json').read_text())
guide=(HERE/'source/literature_guide.md').read_text()
def tau_link(match):
    key=match.group(1)
    r=registry['records'][key]
    return 'https://tau.primo.exlibrisgroup.com/nde/fulldisplay?vid=972TAU_INST%3ANDE&lang=he&docid='+r['docid']+'&context=PC&adaptor=Primo%20Central'
guide=re.sub(r'TAU_RECORD:([a-z0-9]+)',tau_link,guide)
guide=guide.replace('# Literature guide: baseline writing and operational NFE departure','# Literature guide for attendance incentives and baseline writing')
guide=guide.replace('The `[TAU catalogue]` links are placeholders for the parent task\'s Primo records.','Every article has a verified TAU catalogue record and a journal-version citation. Nine substantive articles are cited in the expanded paper; nine relevant alternatives are summarized here but omitted from its bibliography. Two retained methods articles are listed separately.')
guide=guide.replace('## Main reading set','## 1 Articles included in the paper').replace('## Reserve reading set','## 2 Relevant articles omitted from the paper').replace('## Synthesis for the seminar paper','## 3 Overall synthesis').replace('## Retained methods references','## 4 Retained methods references').replace('## Data provenance, separate from the literature','## 5 Data provenance').replace('## Screening boundaries and exclusions','## 6 Search scope and peer review screening')
guide=guide.replace('its abstract is the verified reading depth here.','the final published article was read, including its initial-pretest heterogeneity results.').replace('The publisher abstract is the verified depth unless TAU access supplies the full article; it should support motivation and interpretation, not a mechanism claim about the Rajasthan program.','The final published article was read, including its teacher-response and initial-achievement results. It supports motivation and interpretation without identifying a mechanism for the Rajasthan departure pattern.')
guide=guide.replace('https://academic.oup.com/qje/article-abstract/122/3/1235/1879525?login=false','https://www.povertyactionlab.org/sites/default/files/research-paper/6%20Computer-Assisted%20Learning%20Project%20with%20Pratham%20in%20India%2007.pdf')
guide=guide.replace('https://www.aeaweb.org/articles/pdf/doi/10.1257/aer.101.5.1739','https://www.povertyactionlab.org/sites/default/files/research-paper/39%20Peer%20Effects%2C%20Teacher%20Incentives%2C%20and%20the%20Impact%20of%20Tracking%20Project.pdf')
guide=guide.replace('[Full text / access check]','[Published text or access page]').replace('[Full text](https://academic.oup.com/jeea/article/3/2-3/658/2281517)','[Publisher abstract](https://academic.oup.com/jeea/article-abstract/3/2-3/658/2281517)')
guide=guide.replace('(JPE%202011)','%28JPE%202011%29')
guide=guide.replace('The Kenyan randomized tracking study shows that grouping students can help lower-achieving pupils when teachers can tailor instruction to their level, while high-achieving peers produce a positive direct effect.','The Kenyan randomized tracking study finds gains across the initial-achievement distribution. The authors interpret the pattern as consistent with peer effects and teachers adapting instruction to pupil level.')
guide=guide.replace('[Full text](https://direct.mit.edu/rest/article-pdf/90/3/414/1614600/rest.90.3.414.pdf)','[Publisher access page](https://direct.mit.edu/rest/article/90/3/414/57731/Bootstrap-Based-Improvements-for-Inference-with)')
guide=guide.replace('a standard external peer-review process for every article was not verified.','article-type-specific peer-review evidence for these solicited pieces was not verified.')
guide += '''

The catalogue search began with "teacher attendance incentives" and its peer-review filter, followed by title searches for the candidates identified through article references and related-reading links. Title searches reset the filter, so the journal, year and review badge were checked for each record. Working papers and journal versions can appear together; only the final journal publication counts in the accepted set. This guide summarizes every relevant candidate that received substantive screening in this bounded scan. Incidental unrelated search hits are not part of that cohort.

The user signed in to TAU during the search. ScienceDirect then identified Tel Aviv University and exposed Cilliers et al. (2018) in full, including the article body and appendices. A TAU route to Banerjee et al. (2007) reached JSTOR institutional authentication, but its reader did not display readable pages in that attempt; the public J-PAL copy of the final journal article supplied the text instead. Institutional availability is therefore not treated as proof that a full article was read.

### Reading depth and publication status

The final published text was read for Duflo, Hanna, and Ryan; Guerrero et al.; Cilliers et al.; Glewwe et al.; Muralidharan and Sundararaman; Banerjee et al. (2007); Duflo, Dupas, and Kremer (2011); Linden and Shastry; Banerjee, Duflo, and Glennerster; de Ree et al.; Mbiti et al.; Evans and Popova; and Singh. Duflo, Dupas, and Kremer (2015) was assessed from publisher article sections. Kremer et al., Burde and Linden, and Ganimian and Murnane are summarized from verified publisher abstracts. Fryer is assessed from the final publisher abstract plus a clearly labeled earlier author manuscript; detailed manuscript interpretations are not presented as separately verified final-version findings. Cameron and Holm are retained for their published methods and bibliographic records. Reading a published abstract does not change the article's peer-review status, but it limits the detail of the assessment.

Seventeen of the eighteen education articles displayed a TAU peer-review badge. The Evans and Popova journal record did not display that badge; its journal-version DOI and the World Bank Research Observer's explicit peer-review policy supplied independent verification. The method records also displayed review badges. Journal policies corroborate the publication process; historical referee reports for each individual article are not claimed to have been inspected.

### Verified journal review policies

- [American Economic Review editorial policy](https://www.aeaweb.org/journals/aer/editorial-policy) and [American Economic Journal Applied Economics policy](https://www.aeaweb.org/journals/app/editorial-policy) identify single-blind peer review.
- [Quarterly Journal of Economics policy](https://academic.oup.com/qje/pages/Policies), [Journal of Political Economy author instructions](https://www.journals.uchicago.edu/journals/jpe/instruct), and [Journal of the European Economic Association author guidance](https://academic.oup.com/jeea/pages/Author_Guidelines) document their referee processes.
- [Journal of Public Economics author guide](https://www.sciencedirect.com/journal/journal-of-public-economics/publish/guide-for-authors) identifies single-anonymized review with independent expert assessment. [Journal of Development Economics publisher information](https://shop.elsevier.com/journals/subjects/social-sciences-and-humanities/economics-and-finance/economic-development-technological-change-and-growth) documents refereed manuscripts.
- [Journal of Development Effectiveness journal information](https://www.tandfonline.com/rjde), [Economic Journal instructions](https://academic.oup.com/ej/pages/General_Instructions), and [Journal of Labor Economics author instructions](https://www.journals.uchicago.edu/journals/jole/instruct) document peer or outside review.
- [World Bank Research Observer publication information](https://academic.oup.com/wbro/pages/why-submit) explicitly identifies peer review. [AERA publications policy](https://www.aera.net/Publications/Publications-FAQs) identifies a double-blind reviewer panel for its journals, including Review of Educational Research.
- For the methods articles, [Review of Economics and Statistics guidelines](https://direct.mit.edu/rest/pages/submission-guidelines) document its reviewer process and [Scandinavian Journal of Statistics author guidance](https://onlinelibrary.wiley.com/page/journal/14679469/homepage/forauthors.html) explicitly identifies peer review.

The [Journal of Economic Perspectives editorial policy](https://www.aeaweb.org/journals/jep/editorial-policy) describes solicited articles and editorial review. Article-type-specific peer-review evidence for these two pieces was not verified. "Missing in Action" offers cross-country descriptive absence evidence; "Addressing Absence" reviews monitoring and implementation. Both are excluded from the accepted peer-reviewed set here. Their publication status is not upgraded by a general catalogue badge.
'''
(HERE/'source/literature_guide_final.md').write_text(guide)
print(json.dumps({'main_words':len(source.split()),'introduction_words':len(intro.split()),'guide_words':len(guide.split()),'tau_records':len(registry['records'])}))
