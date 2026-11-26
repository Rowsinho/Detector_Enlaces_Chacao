const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function say(text, ok = false) { 
    const m = $('#msg'); 
    m.textContent = text; 
    m.className = ok ? 'good' : 'err'; 
}

$('#analyzeForm').onsubmit = async (e) => {
    e.preventDefault();
    say('Analizando enlaces, por favor espere...', true);
    
    const texto = e.target.elements.texto.value;
    
    try {
        const res = await fetch('/api/analizar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ texto })
        });
        
        const data = await res.json();
        
        if (!res.ok) throw new Error(data.error || 'Error en el servidor');
        
        renderResults(data);
        say('Análisis completado con éxito', true);
        
    } catch (err) {
        say(err.message);
    }
};

function renderResults(data) {
    const box = $('#results');
    box.hidden = false;

    if (!data.resultados || data.resultados.length === 0) {
        box.innerHTML = '<div class="empty">No se encontraron enlaces para analizar en el texto proporcionado.</div>';
        return;
    }

    // Mapeamos las clasificaciones de la API a las clases del CSS
    const mapClass = (clasificacion) => {
        if (clasificacion === 'malicioso') return 'CRITICO';
        if (clasificacion === 'sospechoso') return 'ALERTA';
        return 'OK';
    };

    const globalClass = mapClass(data.riesgo_global);

    let html = `
        <div class="result ${globalClass}">
            <h3 style="margin:0;">Riesgo Global del Correo: <span class="tag ${globalClass}">${esc(data.riesgo_global.toUpperCase())}</span></h3>
        </div>
    `;

    data.resultados.forEach(res => {
        const cls = mapClass(res.clasificacion);
        
        html += `
            <div class="link-card ${cls}">
                <h4 style="margin:0 0 .5rem; font-family:monospace; font-size:1rem;">${esc(res.url)}</h4>
                <p style="margin:.2rem 0;"><b>Clasificación:</b> <span class="tag ${cls}">${esc(res.clasificacion.toUpperCase())}</span> (${res.puntuacion}/100 puntos)</p>
                <p style="margin:.2rem 0;"><b>Dominio base:</b> ${esc(res.dominio_registrable)}</p>
                ${res.senales.length > 0 ? `
                    <div style="margin-top:.8rem; padding-top:.8rem; border-top:1px solid var(--line);">
                        <b style="font-size:.85rem; color:var(--crit);">Señales de riesgo detectadas:</b>
                        <ul style="margin:.4rem 0 0; padding-left:1.2rem; color:var(--crit); font-size:.9rem;">
                            ${res.senales.map(s => `<li>${esc(s)}</li>`).join('')}
                        </ul>
                    </div>` : 
                    `<p style="margin-top:.8rem; font-size:.9rem; color:var(--ok);">No se detectaron señales de riesgo.</p>`
                }
            </div>
        `;
    });

    box.innerHTML = html;
}