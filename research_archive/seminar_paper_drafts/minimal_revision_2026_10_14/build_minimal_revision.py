from pathlib import Path
import json, hashlib, re, difflib, csv, subprocess
from zipfile import ZipFile
from lxml import etree
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT=Path('/Users/shayb/Downloads/112523-V1')
OUT=ROOT/'seminar_paper_drafts/minimal_revision_2026_10_14'
SOURCE=Path('/Users/shayb/.codex/attachments/53e7c588-1bdb-4295-8899-1e9d4bb647f0/Pasted text.txt')
TARGET=OUT/'07_Shay_Replication_and_Extension_Minimal_Revision_A4.docx'
protected=[SOURCE,ROOT/'seminar_paper_drafts/01_Main_Paper_Academic_Revision_A4.docx',ROOT/'seminar_paper_drafts/reviews_2026_10_14/06_Shay_Rewrite_Annotated_Review_A4.docx']
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
original=SOURCE.read_text().splitlines()
lines=original.copy()
changes=[]

def edit(line,old,new,why):
    assert old in lines[line-1],(line,old)
    lines[line-1]=lines[line-1].replace(old,new,1)
    changes.append({'source_line':line,'before':old,'after':new,'reason':why})

# Local corrections to the author's source; the surrounding wording remains intact.
edit(1,' (edited)','','Remove editor metadata from manuscript title.')
edit(2,lines[1],'','Remove editor metadata from manuscript body.')
edit(5,'study whether monitoring affects teacher absenteeism.','study whether camera monitoring and attendance-linked pay reduce teacher absenteeism and improve learning. They find about a 21-percentage-point reduction in teacher absence and a 0.17-standard-deviation gain in test scores.','State original question and headline findings before the selected replication.')
edit(5,'randomize schools to monitoring via photographs','randomize schools to a package of camera monitoring and attendance-linked pay','Identify the randomized package.')
edit(6,'the control group continued to receive surprise visits from researchers','researchers measured attendance through surprise visits in both treatment and control schools','Clarify research measurement in both arms.')
edit(7,'Duflo, Hanna and Ryan in a replication package (E112523V1) which consisted','Duflo, Hanna and Ryan (2019) in a replication package (E112523V1), which consists','Separate dataset provenance from the journal article.')
edit(7,'the paper’s Table 2 (which includes main results) and Table 10 (which reports effects on average departure)','the pooled all-teacher result in the paper’s original Table 2, Panel A, and all three departure rows in its Table 10','Limit replication claim to actually reproduced results.')
edit(7,'in Python.','in Python. Software and reproduction details appear in Appendix D.','Provide a concise reproducibility pointer to the existing full-paper appendix.')
edit(7,'continue with the extension on my own','add the extension described below','Avoid an implication of unassisted work.')
edit(8,'In Table 2,','In the original Table 2, Panel A,','Distinguish original tables from the new tables.')
edit(9,'I match the results in Table 2 of','I match the pooled result in the original Table 2, Panel A, of','Specify selected attendance replication.')
edit(9,'As in the original table, schools were open','In my reconstruction, schools were open','Distinguish finer reconstruction precision from the published values.')
edit(9,'with SEs clustered at the school level in parentheses, is 0.207, SE 0.030','with SEs clustered at the school level in parentheses, is 0.207 (0.030)','Align wording and SE display.')
edit(9,'I match all results','I match these published values','Do not claim reproduction of every Table 2 specification.')
edit(9,'[14.9, 26.6].','[14.9, 26.6] percentage points. Table 1 reports both the attendance and departure replications.','Supply CI units and refer to the actual replication exhibit.')
edit(9,'The 95% confidence interval is [14.9, 26.6] percentage points.','Expressed in percentage points, the 95% confidence interval is [14.9, 26.6].','Make the conversion from the probability-unit coefficient explicit.')
edit(10,'and report standard errors','and reports standard errors','Repair subject-verb agreement.')
edit(10,'select the last five times they were checked','select the latest up to five times they were checked','Account for incomplete observed histories.')
edit(10,'in those five instances','in those selected instances','Keep the rule consistent for children with fewer than five checks.')
edit(10,'then this child has left','then this child is classified as having departed under this rule','Qualify the operational endpoint.')
edit(10,'The dependent variables are (1) an indicator for departure and (2) an indicator for departure for which we know the child moved to a government school.','The dependent variables are (1) recorded departure, (2) a government-school marker among recorded departures, and (3) residual departure, equal to recorded departure minus the marker.','Include all three original Table 10 outcome rows.')
edit(11,'These files provide information on school id × child id and can be merged on to random checks using these identifiers and on to baseline data using these identifiers and random check time period = baseline.','I merge these roster files on to school random checks using school id and visit date, and on to child enrollment and baseline writing records using school id × child id.','Correct the implemented join keys.')
edit(11,'Although parts of this process are unclear to me,','Some attendance codes lack documented meanings, and the reason fields differ in type.','Identify actual ambiguities precisely.')
edit(11,'In many instances the departure reason is blank; I code these as having left but the destination unknown.','In many instances the reason is blank; a blank does not itself classify a child as departed or supply a government-school marker. The marker equals one for a child classified as departed with reason “2” in at least one selected record.','Separate attendance classification from reason markers.')
edit(11,'whether we know a child went to government school','the recorded government-school marker','Avoid claiming verified transfers.')
edit(11,'whether or not we know that a child went to a government school','whether the selected records contain a government-school reason marker','Define the recorded rather than independently verified endpoint.')
edit(12,'Treatment causes a statistically significant 8.4pp increase in departure, and a 10.1pp increase in departure to government schools.','Assignment to the bundled program causes a statistically significant 8.4-percentage-point increase in recorded departure (SE 4.1 points, p = .044), and a 10.1-point increase in the government-school marker (SE 3.5 points).','Retain supported significance while qualifying endpoints and showing uncertainty.')
edit(12,'a 10.1-point increase','a 10.1-percentage-point increase','Use explicit percentage-point units.')
edit(13,'−1.8 point change in residual departure.','−1.8-percentage-point change in residual departure (SE 3.1 points, p = .564).','Provide consistent units and uncertainty.')
edit(13,'all child-level reference values','the child-level departure indicators','Limit the matching claim to verified endpoints.')
edit(16,'children who were better prepared to enter government schools (as proxied by participating in the written baseline test)','children who were better prepared to enter government schools (with written baseline-test status used as a coarse preparation proxy)','Retain motivation while qualifying the proxy.')
edit(16,'whether writers and nonwriters differ in departures, regardless of whether those departures are due to entry to government schools or drop-out from education more broadly','whether the treatment effect on recorded departure differs between writers and nonwriters, with or without a government-school marker','State the interaction estimand and avoid an unobserved dropout claim.')
edit(17,'In Table 4, I estimate','I estimate','Remove inconsistent table number before the equation.')
edit(18,lines[17],r'Y_{is} = \alpha + \tau T_s + \beta W_{is} + \delta(T_s \times W_{is}) + \varepsilon_{is} \qquad (1)','Replace with the actual saturated model.')
for old,new in [('α_s + γ_sc + τ_isc + δ_isc','α + β + τ + δ'),('α_s + γ_sc','α + β'),('α_s + τ_isc','α + τ'),('α_s','α')]:
    edit(19,old,new,'Use common coefficients and the corrected four cell means.')
edit(19,'Y is an indicator for departure','Y is the binary outcome being analyzed','The same equation is fitted to each of the three defined outcomes.')
edit(19,'Standard errors clustered','School-clustered standard errors','Clarify the covariance calculation without a sentence fragment.')
edit(19,' at the school level','','Avoid repeating the clustering level.')
edit(19,'account for covariance with δ','account for covariance between τ and δ','Identify the variance of the writer linear combination.')
edit(20,'The table reports three different outcomes in Y.','I estimate the model for three different outcomes in Y.','Prepare for the later complete Table 3 exhibit.')
edit(20,'known to be attending a government school at follow-up','classified as departed and has a government-school reason marker in at least one selected record','Use the actual recorded government marker.')
edit(20,'follow-up-up 9,999 Rademacher randomization draws','use 9,999 school-level Rademacher wild-bootstrap-t draws','Correct the bootstrap procedure and typo.')
edit(20,'The table reports wild bootstrap p-values for τ + δ (the departure rate differential for “Writers” relative to “nonwriters”) adjusted for multiple hypothesis testing using the procedure of Holm (1979).','The null sets δ = 0 while leaving the treatment and writing main effects unrestricted. Table 3 reports p-values for δ, the writer-minus-nonwriter difference in treatment effects. I adjust the conventional school-clustered p-values across the three outcomes using Holm (1979), and report wild-bootstrap p-values separately.','Correct the tested coefficient and which p-values receive Holm adjustment.')
edit(40,'and Duflo, Hanna and Ryan (2012) report it as exploratory. ','','Remove the false attribution and sentence fragment.')
edit(40,'these children as high achievers','baseline writers as better prepared','Keep proxy language consistent.')
edit(40,', any more than residual departure is actually a residual category.','. Residual departure is an operational residual category, not a measure of educational dropout.','Correct the residual-category comparison.')
edit(43,lines[42],'','Remove the duplicated aggregate replication paragraph already covered in Section 2.')
edit(44,'based on their performance in a baseline test','by their baseline written-versus-oral test status','The extension uses the test protocol, not a score.')
edit(44,'tables 7 and 9 (E112523V1)','Tables 7 and 9','Use journal-table references rather than the dataset identifier.')
edit(44,'(table 7)','(Table 7)','Consistent table labeling.')
edit(44,'(table 9)','(Table 9)','Consistent table labeling.')
edit(44,'table 10 on leaving the center (E112523V1)','Table 10 on leaving the center','Use the original journal table as the reference.')
edit(45,lines[44],'','Remove repeated model, clustering, and bootstrap description already stated above.')
edit(46,'the original table’s coefficient','the original Table 10 average recorded-departure coefficient','Clarify the aggregate estimand and source table.')
edit(46,'an interaction analysis','group treatment effects from the interaction model','Columns 2–3 contain tau and tau+delta rather than two interactions.')
edit(46,'I leave out the two children in my sample of 2,195 who happened to be included in my replication of their reported average.','I leave out the two children with conflicting baseline writing records from the 2,197-child replication sample, leaving 2,195 for the interaction analysis.','Fix the sample arithmetic.')
edit(46,'I do not report the original coefficient and this new coefficient together because (a) they use slightly different samples, (b) the standard errors would not be comparable because these columns 2 and 3 are interactions, and (c) they are substantively different:','I report the estimates together with their sample sizes and school-clustered uncertainty. They use slightly different samples and answer different questions:','Remove the contradiction and false noncomparability claim.')
edit(46,'by performance on a baseline test','by baseline written-test status','Use the measured subgroup variable.')
edit(46,'Figure 1 graphs the results of columns 2–3.','Figure 1 graphs the results of columns 2–3 and their direct difference.','Explain the included coefficient plot.')
edit(47,'children who could write (“Writer” column)','baseline writers (“Writer” column)','Use child test-status labels.')
edit(47,'children who could not (“nonwriter” column)','baseline nonwriters (“Nonwriter” column)','Use child test-status labels.')
edit(47,'children who could not write as unaffected','baseline nonwriters as unaffected','Use child test-status labels.')
edit(47,'children who could write had a 21.1','baseline writers had a 21.1','Use child test-status labels.')
edit(47,'point larger effect','percentage-point larger effect','State interaction units.')
edit(47,'children who could not.','baseline nonwriters.','Use child test-status labels.')
edit(47,', as in the original paper','','Do not attribute the added bootstrap to the original article.')
edit(48,'This analysis says nothing about why or where these children went when they left:','The total-departure interaction does not establish why or where these children went when they left:','The recorded marker supplies some destination information, so avoid saying none exists.')
edit(48,'Treatment_i and Writer_i','school treatment and child baseline writing status','Use accurate variable levels.')
edit(48,'in table 3','in Table 3','Consistent table labeling.')
edit(48,'The interaction with baseline ability is much larger on Departure: residual than on Government school','The interaction with baseline writing status has a larger point estimate on Residual departure than on Government school','Avoid an untested contrast claim and an ability measure claim.')
edit(49,'Results do not contradict those reported in the original study’s table 7, which found that more hours of instruction due to more days that the school was open (Duflo, Hanna and Ryan (2012) table 7 (E112523V1)), because this table limits its analysis to children who stayed at the center and reports','Results do not contradict those reported in the original study’s Table 7, which found more hours of instruction because schools were open more often. Panel C limits its analysis to children who stayed at the center and reports','Repair sentence grammar and distinguish selected-stayer Panel C from the full table.')
edit(49,'the original table 9 finds that children who could take the written pretest had significantly higher gains in learning','the original Table 9 reports larger estimated learning gains among children who took the written pretest','The original article does not test equality of these subgroup learning effects.')
edit(49,'more hours of instruction','more days of instruction','Original Table 7 reports instruction days rather than hours.')
edit(49,'My results in table 2 extend the original study’s table 10','My results in Table 2 extend the original study’s Table 10','Consistent new-versus-original table references.')
edit(49,'tables 7 and 9.','Tables 7 and 9.','Consistent table labeling.')
edit(51,'Table 3 shows results for departure from baseline school and departure to government school','Table 3 shows interaction results for total recorded departure, the government-school marker, and residual departure','Identify all three interaction outcomes.')
edit(51,'Under these definitions, the first two sum to departure as coded originally.','Under these definitions, the government-marker and residual interaction point estimates sum to the total-departure interaction.','State the correct decomposition.')
edit(51,'writers were more likely to move into government schools','the treatment effect on the recorded government-school marker was larger for writers than nonwriters','The delta test compares two treatment effects.')
edit(51,'Departure without a government school flag includes all other departures, including missing.','Departure without a government-school flag includes all other recorded departures, including those with missing destination reasons.','Avoid implying missing reasons or attendance automatically create departure.')
edit(51,'such a pattern is not able to explain the difference between the groups','the imprecise marker interaction and missing destination records do not establish whether transfers explain the difference between the groups','Do not rule out transfers from a nonsignificant interaction.')
edit(52,'some have a coded reason for departure that does not appear in the available codebooks','some departure classifications involve undocumented attendance codes','Correct the type of ambiguous code.')
edit(52,'113 with unknown codes','113 whose departure classifications involve undocumented attendance codes','Keep the 113-case denominator but correct its meaning.')
edit(52,'region of baseline school','existing school-block/geographic indicators','Do not claim verified randomization strata.')
edit(52,'(to minimize the observations with fewer than five checks)','(to check dependence on the final January–February 2006 records, whose appended reason values become blank under the distributed Stata convention)','Correct the fixed endpoint rationale.')
edit(52,'children with departure coded in a way not in the codebooks','the 113 children with ambiguous attendance-based departure classifications','Correct the exclusion sensitivity.')
edit(52,'bounding relies on other observations in the sample','the algebraic ranges hold the other observations fixed and are not confidence intervals','Separate measurement ranges from sampling uncertainty.')
edit(53,'children in control (treatment) who went to schools run by nonwriters','baseline nonwriter children in control (treatment)','Writer/nonwriter is a child characteristic.')
edit(53,'children who went to schools run by writers','baseline writer children','Writer/nonwriter is a child characteristic.')
edit(53,'whether its principal was a writer','the child’s baseline writing status','Writer/nonwriter is not a principal characteristic.')
edit(53,'common treatment-proof measure of exiting education','treatment-independent measure of permanent educational exit','Clarify the observation-process limitation.')
edit(53,'A child not present in all five checks','A child absent at all selected checks','Specify zero attendance, including incomplete histories, rather than merely less-than-perfect attendance.')
edit(53,'across the sample chosen, the reason for departure is missing for 66.4% of observations','reason fields are blank in 7,112 of 10,707 selected open-school check records (66.4%)','Identify the check-level denominator, not a child-level proportion.')
edit(53,'children who went to schools run by writers than nonwriters','baseline writers than baseline nonwriters','Correct the final child-level conclusion.')

# Consistent author-date citations without altering the substantive prose.
for n in range(1,54):
    if 'Duflo, Hanna and Ryan' in lines[n-1]:
        old=lines[n-1]
        lines[n-1]=old.replace('Duflo, Hanna and Ryan','Duflo, Hanna, and Ryan')
        changes.append({'source_line':n,'before':old,'after':lines[n-1],'reason':'Consistent author-name punctuation.'})
    if '(Duflo, Hanna, and Ryan, 2012)' in lines[n-1]:
        edit(n,'(Duflo, Hanna, and Ryan, 2012)','(Duflo, Hanna, and Ryan 2012)','Consistent Chicago author-date citation.')
    if 'Cameron, Gelbach and Miller' in lines[n-1]:
        edit(n,'Cameron, Gelbach and Miller','Cameron, Gelbach, and Miller','Consistent author-name punctuation.')

OUT.mkdir(parents=True,exist_ok=True)
def read_csv(rel):
    with (ROOT/rel).open() as f: return list(csv.DictReader(f))
aggregate=read_csv('outputs/research_direction_audit/transition_table10_reproduction.csv')
groups=read_csv('outputs/scope_search_2026_09_22/transition/transition_scope_group_effects.csv')
groups=[r for r in groups if r['outcome']=='drop']
models=read_csv('outputs/scope_search_2026_09_22/transition/transition_scope_model_results.csv')
models=[r for r in models if r['specification']=='primary_consensus_no_fe']
attendance=json.loads((ROOT/'seminar_paper_drafts/source/attendance_recheck.json').read_text())
boots={out:json.loads((ROOT/f'outputs/scope_search_2026_09_22/transition/{file}_wildbootstrap_summary.json').read_text()) for out,file in [('drop','drop'),('drop2','drop2')]}
assert len(groups)==2 and len(models)==3 and len(aggregate)==3
assert all(int(r['n'])==2195 and int(r['schools'])==111 for r in models)

# Plot reads only the saved results; it does not refit or change the study.
plot_rows=[(groups[0]['treatment_effect'],groups[0]['ci_low'],groups[0]['ci_high']),
           (groups[1]['treatment_effect'],groups[1]['ci_low'],groups[1]['ci_high']),
           (models[0]['estimate'],models[0]['ci_low'],models[0]['ci_high'])]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="480" viewBox="0 0 1400 480"><rect width="1400" height="480" fill="white"/><g font-family="Times New Roman,serif" font-size="28" fill="black">']
x=lambda value: 510+(value+10)/57*810
svg.append(f'<line x1="{x(0)}" x2="{x(0)}" y1="40" y2="310" stroke="#777" stroke-width="1.5"/>')
for y,label,(est,lo,hi) in zip([80,180,280],['Baseline nonwriters','Baseline writers','Difference between effects'],plot_rows):
    est,lo,hi=[100*float(v) for v in (est,lo,hi)]
    svg.append(f'<text x="475" y="{y+9}" text-anchor="end">{label}</text>')
    svg.append(f'<line x1="{x(lo)}" x2="{x(hi)}" y1="{y}" y2="{y}" stroke="black" stroke-width="3"/>')
    for endpoint in [lo,hi]:svg.append(f'<line x1="{x(endpoint)}" x2="{x(endpoint)}" y1="{y-10}" y2="{y+10}" stroke="black" stroke-width="3"/>')
    svg.append(f'<circle cx="{x(est)}" cy="{y}" r="7" fill="black"/><text x="{x(hi)+14}" y="{y+9}">{est:.1f}</text>')
svg.append('<line x1="510" x2="1320" y1="350" y2="350" stroke="black" stroke-width="1.5"/>')
for tick in [-10,0,10,20,30,40]:
    svg.append(f'<line x1="{x(tick)}" x2="{x(tick)}" y1="350" y2="358" stroke="black"/><text x="{x(tick)}" y="394" text-anchor="middle">{tick}</text>')
svg.append('<text x="915" y="450" text-anchor="middle">Effect on recorded departure (percentage points)</text></g></svg>')
(OUT/'figure_1.svg').write_text(''.join(svg))
node='/Users/shayb/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
js="const sharp=require('/Users/shayb/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp'); sharp(process.argv[1]).png().toFile(process.argv[2]).catch(e=>{console.error(e.message);process.exit(1)});"
subprocess.run([node,'-e',js,str(OUT/'figure_1.svg'),str(OUT/'figure_1.png')],check=True)

doc=Document()
sec=doc.sections[0]
sec.page_width,sec.page_height=Cm(21),Cm(29.7)
sec.left_margin,sec.right_margin=Cm(2.2),Cm(2.2)
sec.top_margin,sec.bottom_margin=Cm(2),Cm(2)
sec.footer_distance=Cm(.85)
normal=doc.styles['Normal']
normal.font.name='Times New Roman'; normal.font.size=Pt(12)
normal.font.color.rgb=RGBColor(0,0,0)
normal.paragraph_format.line_spacing=1.5
normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.widow_control=True
for name,size in [('Title',16),('Heading 1',14),('Heading 2',12)]:
    st=doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size)
    st.font.color.rgb=RGBColor(0,0,0)
    st._element.get_or_add_rPr().rFonts.set(qn('w:ascii'),'Times New Roman')
    st._element.rPr.rFonts.set(qn('w:hAnsi'),'Times New Roman')
    ppr=st._element.find(qn('w:pPr'))
    if ppr is not None:
        for border in list(ppr.findall(qn('w:pBdr'))): ppr.remove(border)
for style in ['Caption']:
    doc.styles[style].font.name='Times New Roman'
    doc.styles[style].font.size=Pt(12)
    doc.styles[style].font.color.rgb=RGBColor(0,0,0)
    doc.styles[style].paragraph_format.line_spacing=1.15
    doc.styles[style].paragraph_format.keep_with_next=True
footer=sec.footer.paragraphs[0];footer.alignment=2
f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');footer._p.append(f)
doc.core_properties.title='Replication and Extension'
doc.core_properties.author='Shay'
doc.core_properties.subject='Minimal corrections to the author supplied Sections 2 and 3'

def paragraph(text):
    return doc.add_paragraph(text)

def caption(text):
    p=doc.add_paragraph(style='Caption');p.add_run(text).bold=True;return p

def table(headers,rows,widths):
    tb=doc.add_table(rows=1,cols=len(headers));tb.alignment=WD_TABLE_ALIGNMENT.CENTER
    tb.autofit=False
    for c,w in zip(tb.columns,widths):c.width=Cm(w)
    for j,value in enumerate(headers):tb.rows[0].cells[j].text=value
    for row in rows:
        cells=tb.add_row().cells
        for j,value in enumerate(row):cells[j].text=str(value)
    for i,row in enumerate(tb.rows):
        rp=row._tr.get_or_add_trPr();rp.append(OxmlElement('w:cantSplit'))
        if i==0:rp.append(OxmlElement('w:tblHeader'))
        for j,cell in enumerate(row.cells):
            cell.width=Cm(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcp=cell._tc.get_or_add_tcPr()
            margins=OxmlElement('w:tcMar')
            for tag,value in [('top',75),('bottom',75),('left',65),('right',65)]:
                e=OxmlElement('w:'+tag);e.set(qn('w:w'),str(value));e.set(qn('w:type'),'dxa');margins.append(e)
            tcp.append(margins)
            if i==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'ECECEC');tcp.append(sh)
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing=1.1;p.paragraph_format.space_after=Pt(1)
                p.paragraph_format.keep_with_next=i<len(tb.rows)-1
                p.alignment=0 if j==0 else 1
                for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(12);r.bold=i==0
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','bottom','left','right','insideH','insideV']:
        el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
    tb._tbl.tblPr.append(borders)
    return tb

def notes(text):
    p=paragraph(text);p.paragraph_format.line_spacing=1.15;p.paragraph_format.space_before=Pt(4)
    return p

def mr(text):
    r=OxmlElement('m:r');t1=OxmlElement('m:t');t1.text=text;r.append(t1);return r

def sub(base,index):
    n=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(mr(base));n.append(e)
    s=OxmlElement('m:sub');s.append(mr(index));n.append(s);return n

def equation():
    p=paragraph('');p.paragraph_format.keep_together=True;p.paragraph_format.keep_with_next=True
    om=OxmlElement('m:oMath')
    for node in [sub('Y','is'),mr(' = α + τ '),sub('T','s'),mr(' + β '),sub('W','is'),mr(' + δ ('),sub('T','s'),mr(' × '),sub('W','is'),mr(') + '),sub('ε','is'),mr('     (1)')]:om.append(node)
    p._p.append(om)

def replication_table():
    caption('Table 1 Replication of original Table 2 Panel A and Table 10')
    rows=[['School open','2 Panel A','0.21 (0.03)',f'{attendance["estimate"]:.3f} ({attendance["se"]:.3f})','3,071']]
    labels={'drop':'Recorded departure','gov':'Government-school marker','drop2':'Residual departure'}
    for r in aggregate:
        rows.append([labels[r['outcome']],'10',f'{float(r["reference_csv_coef_rounded"]):.2f} ({float(r["reference_csv_se_rounded"]):.2f})',f'{float(r["estimate"]):.3f} ({float(r["se_clustered"]):.3f})','2,197'])
    table(['Outcome','Original table','Published effect (SE)','Replicated effect (SE)','N'],rows,[4.8,2,3.7,3.7,2.4])
    notes('Notes: Effects and standard errors are in probability units; 0.01 equals one percentage point. The attendance row is the pooled all-teacher result in original Table 2, Panel A (3,071 visits, 113 schools). The departure rows reproduce all three original Table 10 rows (2,197 children, 111 schools). Recorded departure means zero recoded attendance over the latest up to five open-school checks. The government-school marker requires recorded departure and reason “2” in a selected record; residual departure is the remainder. Standard errors are clustered by school. No significance stars are used. Source: Duflo, Hanna, and Ryan (2012) and the reconstructed Version 1 data.')

def group_table():
    caption('Table 2 Extension of original Table 10 by baseline writing status')
    a=aggregate[0]
    critical=(float(models[0]['ci_high'])-float(models[0]['estimate']))/float(models[0]['se_clustered'])
    lo=float(a['estimate'])-critical*float(a['se_clustered']);hi=float(a['estimate'])+critical*float(a['se_clustered'])
    table(['Recorded departure','Average (1)','Nonwriter (2)','Writer (3)'],[
        ['Treatment effect',f'{100*float(a["estimate"]):.1f}',*[f'{100*float(g["treatment_effect"]):.1f}' for g in groups]],
        ['Clustered SE',f'{100*float(a["se_clustered"]):.1f}',*[f'{100*float(g["se_clustered"]):.1f}' for g in groups]],
        ['95% confidence interval',f'[{100*lo:.1f}, {100*hi:.1f}]',*[f'[{100*float(g["ci_low"]):.1f}, {100*float(g["ci_high"]):.1f}]' for g in groups]],
        ['Children','2,197','1,798','397']], [6.4,3.2,3.5,3.5])
    notes('Notes: Effects, standard errors, and intervals are in percentage points. Column 1 repeats the aggregate 2,197-child replication in 111 schools. Columns 2–3 are τ and τ + δ from equation (1), fitted to 2,195 children in 111 schools after excluding two conflicting baseline-writing records. Writer/nonwriter describes the child’s baseline written-versus-oral test protocol. Covariance estimates are clustered by school; intervals use 110 degrees of freedom. The writer SE accounts for covariance between τ and δ. No significance stars are used.')

def figure():
    caption('Figure 1 Recorded departure effects and their difference by baseline writing status')
    p=paragraph('');p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(OUT/'figure_1.png'),width=Cm(16.6))
    notes('Notes: Points show τ for baseline nonwriters, τ + δ for baseline writers, and δ for their direct difference from equation (1). Bars show 95% confidence intervals based on school-clustered SEs, with 110 degrees of freedom. All estimates use 2,195 children in 111 schools. Recorded departure follows the original last-up-to-five-open-check rule; it is not verified educational dropout. Units are percentage points. No significance stars are used.')

def interaction_table():
    caption('Table 3 Extension of original Table 10 across recorded departure outcomes')
    rows=[]
    for r in models:
        out=r['outcome']
        rows.append([{'drop':'Recorded departure','gov':'Government-school marker','drop2':'Residual departure'}[out],f'{100*float(r["estimate"]):.1f}',f'[{100*float(r["ci_low"]):.1f}, {100*float(r["ci_high"]):.1f}]',f'{float(r["p_value"]):.3f}'.lstrip('0'),f'{float(r["holm_p_value"]):.3f}'.lstrip('0'),f'{boots[out]["wild_bootstrap_p_value"]:.3f}'.lstrip('0') if out in boots else '—'])
    table(['Outcome','δ','95% confidence interval','Clustered p','Holm p','Wild-bootstrap p'],rows,[4.8,1,3.3,2.2,1.9,3.4])
    notes('Notes: Table reports interaction coefficient δ from equation (1). Estimates and intervals are in percentage points. The sample is 2,195 children in 111 schools. Recorded departure follows the original latest-up-to-five-open-check rule. The government-school marker requires recorded departure and reason “2” in a selected record; residual departure is recorded departure minus this marker. Under the original coding, the government-marker and residual interaction point estimates sum to the total-departure interaction; their SEs, intervals, and p-values do not add. Conventional p-values and intervals use school-clustered SEs and 110 degrees of freedom. Holm adjusts the three conventional interaction p-values. Wild-bootstrap p-values use 9,999 null-imposed school-level Rademacher wild-bootstrap-t draws, seed 20260922, testing δ = 0 with unrestricted main effects. The dash means no government-marker bootstrap p-value was estimated/reported. No significance stars are used.')

for n,text in enumerate(lines,1):
    if n in range(21,40) or n in (41,42):continue
    if not text:continue
    if n==1:doc.add_heading(text,0)
    elif n in (3,15):doc.add_heading(text,1)
    elif n==18:equation()
    else:paragraph(text)
    if n==13:replication_table()
    if n==47:group_table();figure()
    if n==51:interaction_table()

doc.save(TARGET)
assert hashes=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
with ZipFile(TARGET) as z:
    xml=etree.fromstring(z.read('word/document.xml'))
    ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    assert len(xml.xpath('//m:oMath',namespaces=ns))==1
    assert len(xml.xpath('//w:tbl',namespaces=ns))==3
    assert len(xml.xpath('//w:drawing',namespaces=ns))==1
    assert not xml.xpath('//w:ins | //w:del',namespaces=ns)
    body=' '.join(xml.xpath('//w:t/text()',namespaces=ns))
    for bad in ['Table here','Figure here','Table 4','principal was a writer','schools run by writers','schools run by nonwriters','Rademacher randomization','p-values for τ + δ','significantly higher gains','standard errors would not be comparable']:
        assert bad not in body,bad

prose_indices=[n for n in range(5,54) if n not in range(17,19) and n not in range(21,40) and n not in (41,42)]
oldwords=re.findall(r'\S+',' '.join(original[n-1] for n in prose_indices))
newwords=re.findall(r'\S+',' '.join(lines[n-1] for n in prose_indices))
matcher=difflib.SequenceMatcher(a=oldwords,b=newwords,autojunk=False)
retained=sum(block.size for block in matcher.get_matching_blocks())
validation={'output':str(TARGET),'source':str(SOURCE),'protected_source_sha256':hashes,
 'prose_words_original':len(oldwords),'prose_words_revised':len(newwords),
 'original_word_tokens_retained_in_order':retained,
 'original_word_token_retention':round(retained/len(oldwords),4),
 'local_edit_operations':len(changes),'native_equations':1,'tables':3,'figures':1,
 'deleted_duplicate_paragraph_source_lines':[43,45],
 'scope':'Supplied Sections 2 and 3 only; existing appendix and footnote references retained; other manuscript components not rewritten.'}
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
(OUT/'exact_edits.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False)+'\n')
visible='\n\n'.join(lines[n-1] for n in range(1,54) if lines[n-1] and n not in range(21,40) and n not in (41,42))
(OUT/'revised_prose.md').write_text(visible+'\n')
diff='\n'.join(difflib.unified_diff(original,lines,fromfile='Your original pasted text',tofile='Minimal revision',lineterm=''))
(OUT/'prose_diff.txt').write_text(diff+'\n')
log=['# Exact edits to your replication and extension','',
 'The clean DOCX revises only the supplied Sections 2–3. Original source files and the prior reference paper remain unchanged. This log records every local prose substitution. The equation is native Word math; the placeholder exhibits use saved verified results.','',
 'The table transcription was moved to Table 3, expanded to the stated three-outcome family, and given complete inference notes. Tables 1–2 and Figure 1 fill the original exhibit references. Four pasted footnote markers and existing appendix references are retained for integration with the complete manuscript; their unprovided contents were not invented.','',
 f'Original prose word tokens retained in order: {retained}/{len(oldwords)} ({retained/len(oldwords):.1%}); this measure excludes the equation and exhibits. It is a token-preservation metric, not a claim that every retained sentence is unchanged.','']
for i,c in enumerate(changes,1):
    log.extend([f'## Edit {i} at source line {c["source_line"]}',c['reason'],'',f'Before: {c["before"] or "[empty]"}',f'After: {c["after"] or "[deleted]"}',''])
(OUT/'exact_changes.md').write_text('\n'.join(log)+'\n')
print(json.dumps({k:validation[k] for k in ['output','original_word_token_retention','prose_words_original','prose_words_revised','tables','figures']}))
