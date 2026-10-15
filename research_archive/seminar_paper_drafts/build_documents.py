"""Build the reference paper and separate research memos from saved evidence.

Run with the Codex bundled Python. Data and original analyses are read only.
"""
from pathlib import Path
import csv, json, re, subprocess
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.graphics.shapes import Drawing, Line, Circle, String
from reportlab.graphics import renderSVG

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
SRC = BASE / 'source'
ASSETS = BASE / 'assets'
ASSETS.mkdir(exist_ok=True)
NODE = '/Users/shayb/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
NODE_MODULES = '/Users/shayb/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'

def rows(path):
    with (ROOT/path).open() as f:
        return list(csv.DictReader(f))

FAMILY = rows('outputs/scope_search_2026_09_22/transition/transition_scope_model_results.csv')
GROUP = rows('outputs/scope_search_2026_09_22/transition/transition_scope_group_effects.csv')
SENTINEL = rows('outputs/scope_search_2026_09_22/transition/sentinel_drop_interaction.csv')
REPLICATION = rows('outputs/research_direction_audit/transition_table10_reproduction.csv')
ATT = json.loads((SRC/'attendance_recheck.json').read_text())

def fmt(x, digits=1):
    return f'{float(x):.{digits}f}'

def pp(x):
    return fmt(100*float(x))

def interval(lo,hi,scale=100):
    return f'[{fmt(float(lo)*scale)}, {fmt(float(hi)*scale)}]'

def pval(x):
    return '< .001' if float(x)<.001 else f'{float(x):.3f}'.lstrip('0')

def chart():
    # ReportLab vector drawing keeps the publication plot deterministic.
    width,height=640,240
    d=Drawing(width,height)
    left,right,bottom,top=210,595,58,207
    scale=lambda x:left+(x+10)/60*(right-left)
    for tick in [-10,0,10,20,30,40,50]:
        x=scale(tick)
        if tick==0:d.add(Line(x,bottom,x,top,strokeColor=__import__('reportlab').lib.colors.HexColor('#777777'),strokeWidth=.7))
        d.add(Line(x,bottom,x,bottom-4,strokeWidth=.5))
        d.add(String(x,bottom-20,str(tick),fontName='Times-Roman',fontSize=12,textAnchor='middle'))
    d.add(Line(left,bottom,right,bottom,strokeWidth=.5))
    data=[]
    for label,g in [('Baseline nonwriters',0),('Baseline writers',1)]:
        r=next(z for z in GROUP if z['outcome']=='drop' and int(z['pre_writ'])==g)
        data.append((label,float(r['treatment_effect'])*100,float(r['ci_low'])*100,float(r['ci_high'])*100))
    r=next(z for z in FAMILY if z['outcome']=='drop' and z['specification']=='primary_consensus_no_fe')
    data.append(('Writer minus nonwriter',float(r['estimate'])*100,float(r['ci_low'])*100,float(r['ci_high'])*100))
    for y,(label,v,lo,hi) in zip([187,139,91],data):
        d.add(String(0,y-4,label,fontName='Times-Roman',fontSize=13))
        d.add(Line(scale(lo),y,scale(hi),y,strokeWidth=1.4))
        for x in [scale(lo),scale(hi)]:d.add(Line(x,y-5,x,y+5,strokeWidth=1))
        d.add(Circle(scale(v),y,4,fillColor=__import__('reportlab').lib.colors.black,strokeWidth=0))
        d.add(String(scale(v),y+12,f'{v:.1f}',fontName='Times-Roman',fontSize=11,textAnchor='middle'))
    d.add(String((left+right)/2,12,'Program effect on recorded departure in percentage points',fontName='Times-Roman',fontSize=12,textAnchor='middle'))
    svg=ASSETS/'main_effects.svg'
    renderSVG.drawToFile(d,str(svg))
    script=ASSETS/'rasterize.cjs'
    script.write_text("const sharp = require("+json.dumps(NODE_MODULES+'/sharp')+");\nsharp(process.argv[2], {density:300}).png().toFile(process.argv[3]).catch(e=>{console.error(e);process.exit(1)});\n")
    subprocess.run([NODE,str(script),str(svg),str(ASSETS/'main_effects.png')],check=True)

def base_doc():
    doc=Document()
    s=doc.sections[0]
    s.page_width=Inches(8.5);s.page_height=Inches(11)
    s.top_margin=s.bottom_margin=Inches(.85)
    s.left_margin=s.right_margin=Inches(1)
    s.header_distance=s.footer_distance=Inches(.35)
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
        sty=doc.styles[name]
        sty.font.name='Times New Roman';sty.font.size=Pt(12)
        sty.font.color.rgb=RGBColor(0,0,0)
        rpr=sty._element.get_or_add_rPr()
        rf=rpr.find(qn('w:rFonts'))
        if rf is not None:
            for attr in list(rf.attrib):
                if attr.split('}')[-1].lower().endswith('theme'):del rf.attrib[attr]
            for attr in ['ascii','hAnsi','eastAsia','cs']:rf.set(qn('w:'+attr),'Times New Roman')
        for b in list(sty._element.iter(qn('w:pBdr'))):b.getparent().remove(b)
        sty.paragraph_format.line_spacing=1.5
        sty.paragraph_format.space_after=Pt(6)
    doc.styles['Normal'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    doc.styles['Normal'].paragraph_format.widow_control=True
    doc.styles['Title'].font.size=Pt(16);doc.styles['Title'].font.bold=True
    doc.styles['Title'].paragraph_format.space_after=Pt(10)
    for h in ['Heading 1','Heading 2','Heading 3']:
        doc.styles[h].font.bold=True
        doc.styles[h].paragraph_format.space_before=Pt(12)
        doc.styles[h].paragraph_format.space_after=Pt(6)
        doc.styles[h].paragraph_format.keep_with_next=True
        doc.styles[h].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
    footer=s.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
    doc.core_properties.author='Author name to be completed'
    doc.core_properties.subject='Reference draft for a replication and extension seminar paper'
    return doc

def text_runs(p,txt):
    # Basic inline markdown, with URLs kept readable and clickable in Word.
    parts=re.split(r'(\*\*.*?\*\*|`[^`]+`|\[[^\]]+\]\([^\)]+\))',txt)
    for part in parts:
        if not part:continue
        if part.startswith('**'):
            p.add_run(part[2:-2]).bold=True
        elif part.startswith('`'):
            p.add_run(part[1:-1])
        elif re.match(r'^\[[^\]]+\]\(',part):
            label,url=re.match(r'^\[([^\]]+)\]\(([^\)]+)\)$',part).groups()
            p.add_run(f'{label} ({url})')
        else:p.add_run(part)

def para(doc,txt,style=None,keep=None):
    p=doc.add_paragraph(style=style)
    text_runs(p,txt)
    if keep is not None:p.paragraph_format.keep_with_next=keep
    return p

def note(doc,txt):
    p=para(doc,'Notes. '+txt)
    p.paragraph_format.line_spacing=1.15
    p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(9)
    p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
    return p

def caption(doc,txt):
    p=para(doc,txt,keep=True)
    p.paragraph_format.line_spacing=1.15
    p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
    for r in p.runs:r.bold=True
    return p

def table(doc,heads,data,widths=None):
    t=doc.add_table(rows=1,cols=len(heads));t.autofit=False
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    if widths is None:
        widths=[6.5/len(heads)]*len(heads)
    for i,w in enumerate(widths):t.columns[i].width=Inches(w)
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for i,s in enumerate(heads):t.rows[0].cells[i].text=s
    for row in data:
        cs=t.add_row().cells
        for i,s in enumerate(row):cs[i].text=str(s)
    for ri,row in enumerate(t.rows):
        for ci,cell in enumerate(row.cells):
            cell.width=Inches(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=cell._tc.get_or_add_tcPr()
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');borders.append(x)
            pr.append(borders)
            margin=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                x=OxmlElement('w:'+edge);x.set(qn('w:w'),'75');x.set(qn('w:type'),'dxa');margin.append(x)
            pr.append(margin)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E8E8E8');pr.append(sh)
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing=1.1;p.paragraph_format.space_after=Pt(2)
                p.paragraph_format.keep_with_next=True
                p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT if ci==0 else WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:r.font.size=Pt(12);r.font.bold=ri==0
        no_split=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(no_split)
    return t

def mr(txt):
    r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=txt;r.append(t);return r

def sub(base,index,sup=None):
    node=OxmlElement('m:sSubSup' if sup else 'm:sSub')
    e=OxmlElement('m:e');e.append(mr(base));node.append(e)
    s=OxmlElement('m:sub');s.append(mr(index));node.append(s)
    if sup:
        u=OxmlElement('m:sup');u.append(mr(sup));node.append(u)
    return node

def frac(a,b):
    node=OxmlElement('m:f')
    for tag,v in [('m:num',a),('m:den',b)]:
        e=OxmlElement(tag);e.append(mr(v));node.append(e)
    return node

def eq(doc,name):
    expr=[]
    if name=='departure':
        expr=[sub('Y','is'),mr(' = α + τ '),sub('T','s'),mr(' + β '),sub('W','is'),mr(' + δ ('),sub('T','s'),mr(' × '),sub('W','is'),mr(') + '),sub('ε','is')]
    elif name=='teacher_standard':
        expr=[sub('Z','s'),mr(' = '),frac('Teacher score - 34.2617','10.4632')]
    elif name=='teacher_learning':
        expr=[sub('Y','isd','post'),mr(' = '),sub('α','d'),mr(' + '),sub('β','d'),sub('T','s'),mr(' + '),sub('γ','d'),sub('Z','s'),mr(' + '),sub('δ','d'),mr('('),sub('T','s'),mr(' × '),sub('Z','s'),mr(') + '),sub('θ','d'),mr('′'),sub('X','is'),mr(' + '),sub('ε','isd')]
    elif name=='quantile':
        expr=[sub('Δ','τ'),mr(' = '),sub('Q','1'),mr('(τ) − '),sub('Q','0'),mr('(τ),   τ ∈ {0.25, 0.50, 0.75}')]
    elif name=='iqr':
        expr=[sub('Δ','IQR'),mr(' = ['),sub('Q','1'),mr('(0.75) − '),sub('Q','1'),mr('(0.25)] − ['),sub('Q','0'),mr('(0.75) − '),sub('Q','0'),mr('(0.25)]')]
    else:raise ValueError(name)
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    mp=OxmlElement('m:oMathPara');m=OxmlElement('m:oMath')
    for e in expr:m.append(e)
    mp.append(m);p._p.append(mp)
    p.paragraph_format.space_before=Pt(6);p.paragraph_format.space_after=Pt(9)

def exhibit(doc,key):
    if key=='replication':
        caption(doc,'Table 1 Replication of the headline attendance and average departure results')
        data=[['School opening', '0.21 (0.03)',f"{ATT['estimate']:.3f} ({ATT['se']:.3f})",'3,071 visits'],]
        for z,label in zip(REPLICATION,['Total recorded departure','Government school marker','Residual departure']):
            data.append([label,f"{float(z['reference_csv_coef_rounded']):.2f} ({float(z['reference_csv_se_rounded']):.2f})",f"{float(z['estimate']):.3f} ({float(z['se_clustered']):.3f})",'2,197 children'])
        table(doc,['Outcome','Published effect (SE)','Reproduced effect (SE)','N'],data,[2.0,1.5,1.6,1.4])
        note(doc,'Effects and standard errors are in probability units; multiply by 100 for percentage points. Attendance uses 113 schools and the original September 2003 to February 2006 time construction. Departure uses 111 schools and the last up-to-five open-check rule. Government school marker and residual departure follow the original reason-code convention. Models contain an intercept and treatment assignment; standard errors are clustered by school. Sources are the original raw files, Table 2 and Table 10, and the audited Python reconstructions. No significance stars are used.')
    elif key=='group_rates':
        caption(doc,'Table 2 Recorded departure rates by treatment and baseline written test status')
        data=[]
        for g,label in [(0,'Baseline nonwriters'),(1,'Baseline writers')]:
            z=next(v for v in GROUP if v['outcome']=='drop' and int(v['pre_writ'])==g)
            data.append([label,f"{round(float(z['control_mean'])*int(z['n_control']))} / {z['n_control']}",pp(z['control_mean'])+'%',f"{round(float(z['treated_mean'])*int(z['n_treated']))} / {z['n_treated']}",pp(z['treated_mean'])+'%'])
        table(doc,['Baseline group','Control departures / N','Control rate','Program departures / N','Program rate'],data,[1.6,1.5,.95,1.5,.95])
        note(doc,'Rates are observed cell proportions, not estimates of calendar-aligned permanent exit. The sample contains 2,195 children in 111 schools, after excluding two conflicting baseline-writing records. Writers took the written baseline test; nonwriters did not. Departure means zero recorded attendance in the selected latest up-to-five open-school checks. This descriptive table has no individual-independent standard errors; Figure 1 reports school-clustered uncertainty for the estimated contrasts. Source is the raw-reconstructed departure cohort.')
    elif key=='main_effects':
        caption(doc,'Figure 1 The program departure response is larger among baseline writers')
        p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        run=p.add_run();run.add_picture(str(ASSETS/'main_effects.png'),width=Inches(6.5))
        for prop in run._r.xpath('.//wp:docPr'):prop.set('descr','Coefficient plot showing nonwriter effect 5.0, writer effect 26.1, and their difference 21.1 percentage points, with school-clustered 95 percent confidence intervals.')
        note(doc,'Dots show linear probability model treatment effects; lines show 95 percent intervals using school-clustered covariance and t critical values with 110 degrees of freedom. N = 2,195 children in 111 schools (57 treatment and 54 control). The horizontal axis is percentage points of operational recorded departure. The nonwriter interval is [-2.4, 12.4], the writer interval [10.0, 42.3], and their direct interaction interval [6.9, 35.3]. The vertical line marks zero. Source is the main treatment by baseline-writing model; neither writing status nor later educational destinations are randomized.')
    elif key=='outcome_family':
        caption(doc,'Table 3 The full departure outcome family and multiplicity adjustment')
        labels={'drop':'Total departure','gov':'Government marker','drop2':'Residual departure'};data=[]
        for z in FAMILY:
            if z['specification']=='primary_consensus_no_fe':
                data.append([labels[z['outcome']],pp(z['estimate']),interval(z['ci_low'],z['ci_high']),pval(z['p_value']),pval(z['holm_p_value'])])
        table(doc,['Outcome','Interaction pp','95% CI pp','Raw p','Holm p'],data,[1.9,1.15,1.75,.85,.85])
        note(doc,'Every row uses 2,195 children and 111 schools (57 treatment and 54 control) in the same linear probability model with treatment, baseline written-test status, and their interaction. Interactions are writer minus nonwriter treatment effects in percentage points. Intervals and raw p-values use school-clustered covariance and 110 degrees of freedom; Holm p-values adjust the three fixed interactions. Government and residual measures depend on the original recorded reason marker. Source is transition_scope_model_results.csv. Adjusted values remain exploratory and do not cover the full earlier candidate search.')
    elif key=='robustness':
        caption(doc,'Table A1 Fixed sensitivity analyses of the departure interaction')
        data=[]
        for spec,label in [('primary_consensus_no_fe','Main model'),('same_sample_randomization_block_fe','Geographic block controls'),('fixed_2005_12_31_endpoint','December 2005 endpoint')]:
            z=next(v for v in FAMILY if v['outcome']=='drop' and v['specification']==spec)
            data.append([label,pp(z['estimate']),interval(z['ci_low'],z['ci_high']),pval(z['p_value']),z['n']])
        z=SENTINEL[1];data.append(['Exclude ambiguous codes',pp(z['estimate']),interval(z['ci_low'],z['ci_high']),pval(z['p_value']),z['n']])
        table(doc,['Specification','Interaction pp','95% CI pp','p','Children'],data,[2.0,1.05,1.7,.75,1.0])
        note(doc,'Every model has 111 school clusters and reports the writer minus nonwriter contrast. Standard errors are clustered by school; 95 percent intervals and p-values use 110 degrees of freedom. The block model uses the existing geographic school block field, not established randomization strata. The calendar check truncates source dates but preserves the original observation rule. The exclusion changes the analyzed population. Sources are the fixed scope and sentinel sensitivity CSVs. No stars are used.')
    elif key=='measurement_bounds':
        caption(doc,'Table A2 Algebraic bounds for documented outcome ambiguity')
        data=[['Undocumented attendance codes','113','[16.3, 34.1]'],['Fewer than five open checks','145','[11.9, 36.4]'],['Either concern with overlap removed','230','[8.8, 45.6]']]
        table(doc,['Outcomes treated as unknown','Flagged children','Interaction range pp'],data,[3.35,1.35,1.8])
        note(doc,'Bounds assign any binary outcome to flagged children while retaining all other outcomes and cell denominators in the 2,195-child, 111-school sample. There are 28 overlapping flags. Ranges are writer minus nonwriter treatment-effect differences in percentage points. They are algebraic ranges with no standard errors or p-values, not confidence intervals. Sources are transition_incomplete_last5_bounds.csv and measurement/sentinel_interaction_bounds.json.')
    else:raise ValueError(key)

def normalize_math(txt):
    replacements=[('Z_s=(\\text{teacher score}_s-34.2617)/10.4632.','teacher_standard'),('Y_{isd}^{post}=','teacher_learning'),('\\Delta_{\\tau}=','quantile'),('\\Delta_{IQR}=','iqr')]
    def display(m):
        v=m.group(1).strip()
        for prefix,name in replacements:
            if v.startswith(prefix):return '[[EQUATION '+name+']]'
        raise ValueError('Unhandled math '+v)
    txt=re.sub(r'\\\[\s*(.*?)\s*\\\]',display,txt,flags=re.S)
    inline={'d':'domain','T_s':'treatment assignment','X_{is}':'the baseline control vector','\\delta_d':'the domain interaction','F_t(y)':'the arm-specific empirical distribution','t':'the treatment arm','Q_t(\\tau)':'the arm-specific empirical quantile'}
    txt=re.sub(r'\\\((.*?)\\\)',lambda m:inline.get(m.group(1),m.group(1)),txt)
    return txt

def from_markdown(path,out,main=False):
    txt=normalize_math(path.read_text())
    doc=base_doc();lines=txt.splitlines();i=0;table_count=0
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line=='[[PAGEBREAK]]':doc.add_page_break();continue
        if line.startswith('[[TABLE '):exhibit(doc,line[8:-2]);continue
        if line.startswith('[[FIGURE '):exhibit(doc,line[9:-2]);continue
        if line.startswith('[[EQUATION '):eq(doc,line[11:-2]);continue
        if line.startswith('# '):
            title=line[2:]
            if not main:title=re.sub(r'[^\w\s]',' ',title).replace('_',' ');title=re.sub(r'\s+',' ',title).strip()
            para(doc,title,'Title');doc.core_properties.title=title;continue
        if line.startswith('##'):
            level=2 if line.startswith('###') else 1
            h=line.lstrip('#').strip()
            h=re.sub(r'[^\w\s]',' ',h);h=re.sub(r'\s+',' ',h).strip()
            para(doc,h,'Heading '+str(level));continue
        if line.startswith('|'):
            block=[line]
            while i<len(lines) and lines[i].strip().startswith('|'):block.append(lines[i].strip());i+=1
            data=[[c.strip() for c in z.strip('|').split('|')] for z in block]
            data=[z for z in data if not all(re.match(r'^:?-+:?$',c.replace(' ','')) for c in z)]
            table_count+=1
            caption(doc,f'Table {table_count} '+('Current evidence for the alternative approach' if len(data[0])>4 else 'Comparison of research approaches'))
            if len(data[0])>6:
                # Sample dimensions are described in prose; show quantiles compactly.
                if data[0][0]=='Assignment arm':
                    keep=[0,4,5,6,7]
                else:keep=[j for j,c in enumerate(data[0]) if c not in ['Role','Bootstrap SE']]
                data=[[z[j] for j in keep] for z in data]
            n=len(data[0]);widths=[2.0]+[(6.5-2)/(n-1)]*(n-1) if n>1 else [6.5]
            if n==6:widths=[1.35,1.0,.75,1.65,.8,.95]
            data[0]=[c.replace('Teacher-score interaction','Interaction').replace('Clustered SE','SE').replace('Holm p (3 outcomes)','Holm p').replace('Holm p (4 contrasts)','Holm p') for c in data[0]]
            table(doc,data[0],data[1:],widths)
            if '02_' in path.name:
                note(doc,'Learning effects are standard deviation units per one standard deviation higher baseline teacher score. Main and block models use 1,625 source rows, 1,610 unique school-child keys, and 101 schools. Confidence intervals use school-clustered covariance with 100 degrees of freedom. Holm p-values adjust the fixed mathematics, language, and total family; no stars are used. Source is the fixed learning-family audit. All results are exploratory.')
            elif '03_' in path.name:
                note(doc,'Quantiles and contrasts use normalized post-test total learning in standard deviation units. N = 1,737 source rows, 1,720 unique school-child keys, 107 schools. Contrast intervals are percentile intervals from 9,999 school pairs bootstrap draws within arm; centered p-values are approximate and Holm adjustment covers four contrasts. Arm quantiles are descriptive, not paired-child effects. Source is the fixed distribution audit.')
            continue
        if re.match(r'^\d+\. ',line):
            p=para(doc,line)
            p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
            continue
        if line.startswith('- '):
            p=para(doc,'• '+line[2:]);p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
            continue
        buf=[line]
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','[[','- ')) and not re.match(r'^\d+\. ',lines[i]):buf.append(lines[i].strip());i+=1
        p=para(doc,' '.join(buf))
        if '[Author name]' in line or line.startswith('Reference draft'):
            p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after=Pt(5)
    if not main:
        for idx,p in enumerate(doc.paragraphs):
            if p.text.startswith('Notes.'):
                p.paragraph_format.keep_together=True
            if len(p.text.split())<40 and idx+1<len(doc.paragraphs) and doc.paragraphs[idx+1].text.startswith('Table '):
                p.paragraph_format.keep_with_next=True
    doc.save(out)
    return len(doc.paragraphs)

if __name__=='__main__':
    chart()
    outputs=[('01_main_paper.md','01_Main_Paper_Reference_Draft.docx',True),('02_learning_by_teacher_score.md','02_Alternative_Learning_by_Teacher_Score.docx',False),('03_learning_distribution.md','03_Alternative_Learning_Distribution.docx',False),('04_author_guide.md','04_Author_Revision_and_Defense_Guide.docx',False)]
    for src,name,main in outputs:
        n=from_markdown(SRC/src,BASE/name,main)
        print(name,'paragraphs',n)
