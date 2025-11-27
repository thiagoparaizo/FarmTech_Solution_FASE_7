# test_flask_routes.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app

app = create_app()

print("🔍 Verificando rotas registradas no Flask:")
print("=" * 50)

# Listar todas as rotas
for rule in app.url_map.iter_rules():
    print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")

print("\n🔍 Procurando rotas ML especificamente:")
ml_routes = [rule for rule in app.url_map.iter_rules() if '/api/ml' in rule.rule]

if ml_routes:
    print("✅ Rotas ML encontradas:")
    for route in ml_routes:
        print(f"  {route.methods} {route.rule}")
else:
    print("❌ Nenhuma rota ML encontrada!")

print("\n🔍 Verificando blueprints registrados:")
for bp_name, bp in app.blueprints.items():
    print(f"  Blueprint: {bp_name} (url_prefix: {bp.url_prefix})")