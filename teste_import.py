try:
    from app.routes.ml_routes import ml_bp
    print('✅ Import OK - Blueprint:', ml_bp.name)
except Exception as e:
    print('❌ ERRO:', e)
    import traceback
    traceback.print_exc()