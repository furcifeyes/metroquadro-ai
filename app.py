import streamlit as st
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
import io

load_dotenv()

# ─── CONFIGURAZIONE PAGINA ───────────────────────────
st.set_page_config(
    page_title="Metroquadro — Genera Annunci",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Metroquadro Immobiliare")
st.subheader("Generatore Annunci AI")
st.divider()

# ─── FORM DATI IMMOBILE ──────────────────────────────
with st.form("form_immobile"):
    col1, col2 = st.columns(2)
    
    with col1:
        tipo = st.text_input("🏠 Tipo immobile", placeholder="es. appartamento, villa")
        zona = st.text_input("📍 Zona/Via", placeholder="es. Via Scitè, Centro")
        prezzo = st.text_input("💶 Prezzo", placeholder="es. 250.000")
        mq = st.text_input("📐 Metri quadri", placeholder="es. 145")
    
    with col2:
        locali = st.text_input("🚪 Locali", placeholder="es. 5")
        bagni = st.text_input("🚿 Bagni", placeholder="es. 2")
        piano = st.text_input("🏢 Piano", placeholder="es. 4 su 5, con ascensore")
        stato = st.text_input("🔧 Stato", placeholder="es. ottimo, da ristrutturare")
    
    caratteristiche = st.text_area(
        "✨ Caratteristiche principali",
        placeholder="es. terrazzo, box, parquet, cabina armadio...",
        height=80
    )
    extra = st.text_area(
        "📝 Note aggiuntive (opzionale)",
        height=60
    )
    
    submitted = st.form_submit_button(
        "🚀 GENERA ANNUNCIO",
        use_container_width=True,
        type="primary"
    )

# ─── FUNZIONE GENERA PDF ─────────────────────────────
def genera_pdf(immobile, testo_annuncio, testo_social, testo_whatsapp):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    elementi = []
    
    # Header
    header_style = ParagraphStyle('header', fontSize=18, textColor=colors.HexColor('#1a3c5e'),
                                  fontName='Helvetica-Bold', alignment=1, spaceAfter=6)
    sub_style = ParagraphStyle('sub', fontSize=11, textColor=colors.HexColor('#666666'),
                               fontName='Helvetica', alignment=1, spaceAfter=20)
    
    elementi.append(Paragraph("METROQUADRO IMMOBILIARE", header_style))
    elementi.append(Paragraph("Messina — Annuncio Generato con AI", sub_style))
    
    # Dati immobile
    section_style = ParagraphStyle('section', fontSize=13, textColor=colors.HexColor('#1a3c5e'),
                                   fontName='Helvetica-Bold', spaceBefore=15, spaceAfter=8)
    body_style = ParagraphStyle('body', fontSize=10, textColor=colors.HexColor('#333333'),
                                fontName='Helvetica', spaceAfter=6, leading=14)
    
    elementi.append(Paragraph("DATI IMMOBILE", section_style))
    
    dati = [
        ["Tipo", immobile['tipo']], ["Zona", immobile['zona']],
        ["Prezzo", f"€ {immobile['prezzo']}"], ["Superficie", f"{immobile['mq']} mq"],
        ["Locali", immobile['locali']], ["Bagni", immobile['bagni']],
        ["Piano", immobile['piano']], ["Stato", immobile['stato']],
    ]
    
    tabella = Table(dati, colWidths=[4*cm, 13*cm])
    tabella.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f0f4f8')),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#1a3c5e')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elementi.append(tabella)
    elementi.append(Spacer(1, 0.4*cm))
    
    # Annuncio portali
    elementi.append(Paragraph("ANNUNCIO PORTALI", section_style))
    elementi.append(Paragraph(testo_annuncio.replace('\n', '<br/>'), body_style))
    elementi.append(Spacer(1, 0.3*cm))
    
    # Social
    elementi.append(Paragraph("POST FACEBOOK / INSTAGRAM", section_style))
    elementi.append(Paragraph(testo_social.replace('\n', '<br/>'), body_style))
    elementi.append(Spacer(1, 0.3*cm))
    
    # WhatsApp
    elementi.append(Paragraph("MESSAGGIO WHATSAPP", section_style))
    elementi.append(Paragraph(testo_whatsapp.replace('\n', '<br/>'), body_style))
    
    doc.build(elementi)
    buffer.seek(0)
    return buffer

# ─── ESECUZIONE SWARM ────────────────────────────────
if submitted:
    if not all([tipo, zona, prezzo, mq, locali, bagni, piano, stato]):
        st.error("⚠️ Compila tutti i campi obbligatori!")
    else:
        IMMOBILE = {
            "tipo": tipo, "zona": zona, "prezzo": prezzo,
            "mq": mq, "locali": locali, "bagni": bagni,
            "piano": piano, "stato": stato,
            "caratteristiche": caratteristiche, "extra": extra
        }
        
        with st.spinner("🤖 Gli agenti AI stanno lavorando..."):
            llm = LLM(
                model="groq/llama-3.3-70b-versatile",
                api_key=os.getenv("GROQ_API_KEY")
            )
            
            analista = Agent(
                role="Analista Immobiliare",
                goal="Identificare punti di forza e target acquirente",
                backstory="Esperto immobiliare con 15 anni di esperienza a Messina.",
                llm=llm, verbose=False
            )
            copywriter = Agent(
                role="Copywriter Immobiliare",
                goal="Scrivere annunci professionali per portali immobiliari",
                backstory="Scrivi annunci che vendono per Immobiliare.it e Casa.it.",
                llm=llm, verbose=False
            )
            social = Agent(
                role="Social Media Manager",
                goal="Creare contenuti per Facebook, Instagram e WhatsApp",
                backstory="Gestisci social di agenzie immobiliari da anni.",
                llm=llm, verbose=False
            )
            
            t1 = Task(
                description=f"""
                Analizza questo immobile a Messina:
                Tipo: {IMMOBILE['tipo']}, Zona: {IMMOBILE['zona']},
                Prezzo: {IMMOBILE['prezzo']}, Superficie: {IMMOBILE['mq']} mq,
                Locali: {IMMOBILE['locali']}, Bagni: {IMMOBILE['bagni']},
                Piano: {IMMOBILE['piano']}, Stato: {IMMOBILE['stato']},
                Caratteristiche: {IMMOBILE['caratteristiche']}
                Trova 3 punti di forza e il target ideale. Max 100 parole.
                """,
                expected_output="3 punti di forza e target acquirente",
                agent=analista
            )
            t2 = Task(
                description=f"""
                Scrivi annuncio professionale per portali immobiliari.
                TITOLO: max 60 caratteri
                DESCRIZIONE: 150-200 parole professionale
                DETTAGLI TECNICI (usa ESATTAMENTE questi valori):
                - Superficie: {IMMOBILE['mq']} mq
                - Locali: {IMMOBILE['locali']}
                - Bagni: {IMMOBILE['bagni']}
                - Piano: {IMMOBILE['piano']}
                - Prezzo: {IMMOBILE['prezzo']}
                CONTATTO: Per info contattare Metroquadro Messina
                Non inventare dati tecnici diversi da quelli forniti.
                """,
                expected_output="Annuncio completo con titolo, descrizione, dettagli, contatto",
                agent=copywriter, context=[t1]
            )
            t3 = Task(
                description=f"""
                Crea:
                1. POST FACEBOOK/INSTAGRAM: hook + 100 parole + 5 emoji + 5 hashtag locali + CTA
                2. MESSAGGIO WHATSAPP: max 50 parole, diretto, niente hashtag
                Dati: {IMMOBILE['tipo']} in {IMMOBILE['zona']}, {IMMOBILE['mq']} mq,
                {IMMOBILE['locali']} locali, {IMMOBILE['bagni']} bagni, € {IMMOBILE['prezzo']}
                """,
                expected_output="Post Facebook/Instagram e messaggio WhatsApp",
                agent=social, context=[t1, t2]
            )
            
            crew = Crew(
                agents=[analista, copywriter, social],
                tasks=[t1, t2, t3],
                verbose=False
            )
            
            risultato = crew.kickoff()
            output_annuncio = t2.output.raw if t2.output else ""
            output_social = t3.output.raw if t3.output else ""
            
            # Estrai WhatsApp dal social
            whatsapp = ""
            if "WHATSAPP" in output_social.upper():
                parti = output_social.upper().split("WHATSAPP")
                if len(parti) > 1:
                    whatsapp = output_social[len(parti[0])+9:]
            
        st.success("✅ Annuncio generato con successo!")
        st.divider()
        
        # Mostra risultati
        st.subheader("📋 Annuncio Portali")
        st.text_area("", output_annuncio, height=300, label_visibility="collapsed")
        
        st.subheader("📱 Post Facebook / Instagram")
        st.text_area("", output_social, height=200, label_visibility="collapsed")
        
        # Salva file
        data = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        zona_pulita = zona.replace(" ", "_").replace("/", "-")
        cartella = os.path.expanduser(f"~/agenti/output/metroquadro/{zona_pulita}")
        os.makedirs(cartella, exist_ok=True)
        nome_file = f"{cartella}/{tipo.replace(' ','_')}_{data}.txt"
        
        with open(nome_file, "w", encoding="utf-8") as f:
            f.write(f"METROQUADRO MESSINA\nGenerato: {data}\n\n")
            f.write(f"ANNUNCIO PORTALI:\n{output_annuncio}\n\n")
            f.write(f"SOCIAL & WHATSAPP:\n{output_social}\n")
        
        # Download PDF
        st.divider()
        pdf = genera_pdf(IMMOBILE, output_annuncio, output_social, whatsapp)
        st.download_button(
            label="📄 SCARICA PDF PROFESSIONALE",
            data=pdf,
            file_name=f"metroquadro_{zona_pulita}_{data}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
