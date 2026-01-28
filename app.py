import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="PensionRoute - Specialist Tool", layout="wide")

st.title("🛡️ PensionRoute: Simulatore Specialistico 2026")
st.markdown("""
Analisi avanzata della previdenza pubblica e complementare basata sulla **Legge di Bilancio 2026 (L. 199/2025)** e sui dati tecnici **Mefop/INPS**.
""")

# --- COSTANTI TECNICHE 2025-2026 ---
COEFFICIENTI_TRASFORMAZIONE = {
    62: 0.04795,
    63: 0.04900,
    64: 0.05050,
    65: 0.05220,
    66: 0.05400,
    67: 0.05608,
    70: 0.06200,
    71: 0.06510
}

# --- SIDEBAR: INPUT CLIENTE ---
st.sidebar.header("Dati del Cliente")
nome = st.sidebar.text_input("Nome Cliente", "Esempio Cliente")
eta_attuale = st.sidebar.number_input("Età Attuale", 18, 70, 45)
reddito_annuo = st.sidebar.number_input("Reddito Annuo Lordo (RAL) / Reddito Netto (€)", 0, 500000, 400000)
anzianita_contributiva = st.sidebar.number_input("Anni di contributi versati", 0, 50, 20)
eta_pensionamento_target = st.sidebar.slider("Età pensionamento obiettivo", 62, 71, 67)

categoria = st.sidebar.selectbox("Categoria Professionale", [
    "Dipendente Settore Privato",
    "Agente di Assicurazione (INPS + FPA)",
    "Medico (ENPAM)",
    "Avvocato (Cassa Forense)",
    "Geometra (CIPAG)",
    "Libero Professionista (Gestione Separata)"
])

# --- LOGICA DI CALCOLO ---
def calcolo_previdenza(categoria, ral, anni_cont, eta_pensionamento):
    # Stima del montante basata sulla categoria
    if "Agente" in categoria:
        aliquota = 0.2448 # INPS Commercianti
        contributo_integrativo = 3100 # Stima FPA (Agente + Compagnia)
    elif "Medico" in categoria:
        aliquota = 0.1950
        contributo_integrativo = 0
    elif "Dipendente" in categoria:
        aliquota = 0.33
        contributo_integrativo = 0
    else:
        aliquota = 0.25
        contributo_integrativo = 0

    # Calcolo Montante Futuro Semplificato
    anni_mancanti = eta_pensionamento - eta_attuale
    montante_attuale = (ral * aliquota * anni_cont) 
    montante_futuro = montante_attuale + (ral * aliquota * anni_mancanti)
    
    # Applicazione Coefficiente
    coeff = COEFFICIENTI_TRASFORMAZIONE.get(eta_pensionamento, 0.05608)
    pensione_annua_lorda = montante_futuro * coeff
    
    return round(pensione_annua_lorda, 2), round(montante_futuro, 2)

pensione_stima, montante_finale = calcolo_previdenza(categoria, reddito_annuo, anzianita_contributiva, eta_pensionamento_target)
stipendio_mensile_stima = reddito_annuo / 13
pensione_mensile_stima = pensione_stima / 13
gap_mensile = stipendio_mensile_stima - pensione_mensile_stima
tasso_sostituzione = (pensione_mensile_stima / stipendio_mensile_stima) * 100

# --- VISUALIZZAZIONE RISULTATI ---
col1, col2, col3 = st.columns(3)
col1.metric("Pensione Mensile Stimata", f"€ {pensione_mensile_stima:,.2f}")
col2.metric("Gap Previdenziale", f"€ {gap_mensile:,.2f}", delta_color="inverse")
col3.metric("Tasso di Sostituzione", f"{tasso_sostituzione:.1f}%")

st.divider()

# --- GRAFICO DEL GAP ---
fig = go.Figure()
fig.add_trace(go.Bar(
    x=['Ultimo Reddito', 'Pensione Pubblica'],
    y=[stipendio_mensile_stima, pensione_mensile_stima],
    marker_color=['#1f77b4', '#ef553b']
))
# Riga corretta qui sotto:
fig.update_layout(title="Confronto Reddito vs Pensione (Mensile)", yaxis_title="Euro €")
st.plotly_chart(fig, use_container_width=True)

# --- FOCUS RIFORMA 2026 & SOLUZIONI ---
st.subheader("💡 Analisi dello Specialista")
with st.expander("Vedi dettagli Riforma 2026 e Strategia"):
    st.write(f"""
    **Adesione Automatica:** In base alla Legge 199/2025, se fossi un nuovo assunto, il 50% del tuo TFR verrebbe 
    destinato automaticamente alla previdenza complementare salvo tua rinuncia.
    
    **Strategia Consigliata per {categoria}:**
    * **Vantaggio Fiscale:** Versando 5.164€/anno, otterresti un risparmio IRPEF immediato di circa **€ {(5164 * 0.35):,.2f}** (ipotizzando aliquota 35%).
    * **Per gli Agenti:** Non dimenticare che il contributo della Compagnia nel Fondo Pensione Agenti è 'denaro regalato' che aumenta il tuo tasso di sostituzione senza intaccare il tuo netto in busta.
    """)

# --- TABELLA RIASSUNTIVA ---
df_dati = pd.DataFrame({
    "Parametro": ["Montante Contributivo Stimato", "Età Uscita", "Coefficiente Applicato", "Gap Annuale"],
    "Valore": [f"€ {montante_finale:,.2f}", f"{eta_pensionamento_target} anni", f"{COEFFICIENTI_TRASFORMAZIONE.get(eta_pensionamento_target):.5f}", f"€ {(gap_mensile*13):,.2f}"]
})
st.table(df_dati)


st.info("Nota: I calcoli sono simulazioni basate su proiezioni medie e non costituiscono certezza del diritto pensionistico.")
