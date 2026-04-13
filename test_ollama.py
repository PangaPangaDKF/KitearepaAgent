import ollama

# HTML de prueba (simulando Binance)
test_html = """
<div class="order-card">
    <span class="order-id">Orden #123456789</span>
    <div class="amounts">
        <span class="usdt-amount">500 USDT</span>
        <span class="ves-amount">2,750,000 Bs</span>
    </div>
    <span class="buyer-name">Juan123</span>
    <span class="order-status">Esperando pago</span>
    <span class="time-left">28:45</span>
</div>
"""

# Ollama analiza
response = ollama.generate(
    model='llama3.2:3b',
    prompt=f"""
    Analiza este HTML de una orden de Binance P2P.
    Extrae los datos en formato JSON.
    
    HTML:
    {test_html}
    
    Responde SOLO con JSON válido:
    {{
        "order_id": "...",
        "usdt": ...,
        "ves": ...,
        "buyer": "...",
        "status": "...",
        "time_left": "..."
    }}
    """
)

print("RESPUESTA DE OLLAMA:")
print(response['response'])

# Intentar parsear como JSON
import json
try:
    data = json.loads(response['response'])
    print("\n✅ JSON válido:")
    print(json.dumps(data, indent=2))
except:
    print("\n⚠️ No es JSON válido, pero Ollama respondió")
