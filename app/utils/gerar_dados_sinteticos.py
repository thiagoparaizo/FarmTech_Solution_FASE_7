
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Gerar dados sintéticos mais realísticos
np.random.seed(42)
n_samples = 100

data = []
base_time = datetime.now() - timedelta(days=30)

for i in range(n_samples):
    timestamp = int((base_time + timedelta(hours=i*6)).timestamp() * 1000)
    
    # Gerar dados com variabilidade
    umidade = np.random.uniform(10, 90)
    ph = np.random.uniform(5.0, 8.5)
    fosforo = np.random.choice([0, 1], p=[0.7, 0.3])
    potassio = np.random.choice([0, 1], p=[0.6, 0.4])
    
    # Lógica de irrigação baseada em condições
    irrigacao = 1 if (umidade < 30 and 6.0 <= ph <= 7.5) else 0
    
    data.append({
        'timestamp': timestamp,
        'umidade': umidade,
        'ph': ph,
        'fosforo': fosforo,
        'potassio': potassio,
        'irrigacao': irrigacao
    })

print(f'Dados sintéticos: {len(data)} amostras')
print(f'Irrigação ativa: {sum(d["irrigacao"] for d in data)} casos')
print(
    f'Variabilidade umidade: '
    f'{min(d["umidade"] for d in data):.1f} - {max(d["umidade"] for d in data):.1f}'
)