#!/usr/bin/env python3
"""
Script para converter Jupyter Notebook para HTML
"""
import os
import sys
from pathlib import Path

def converter_notebook_para_html(notebook_path, output_path=None):
    """
    Converte um Jupyter Notebook para HTML
    
    Args:
        notebook_path: Caminho para o arquivo .ipynb
        output_path: Caminho de saída do HTML (opcional)
    """
    try:
        import nbconvert
        from nbconvert import HTMLExporter
        
        # Configurar exporter
        html_exporter = HTMLExporter()
        html_exporter.template_name = 'lab'  # Template moderno
        
        # Ler notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = f.read()
        
        # Converter para HTML
        (body, resources) = html_exporter.from_filename(notebook_path)
        
        # Definir caminho de saída
        if output_path is None:
            output_path = notebook_path.replace('.ipynb', '.html')
        
        # Salvar HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(body)
        
        print(f"✓ Notebook convertido com sucesso!")
        print(f"  Entrada: {notebook_path}")
        print(f"  Saída: {output_path}")
        
        return output_path
        
    except ImportError:
        print("ERRO: nbconvert não está instalado.")
        print("Execute: pip install nbconvert")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO ao converter notebook: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Configurar caminhos
    base_dir = Path(__file__).parent.parent.parent
    notebook_path = base_dir / "fase6" / "pbl.ipynb"
    output_path = base_dir / "app" / "static" / "fase6" / "pbl.html"
    
    # Criar diretório de saída se não existir
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Converter
    if notebook_path.exists():
        converter_notebook_para_html(str(notebook_path), str(output_path))
    else:
        print(f"ERRO: Notebook não encontrado em {notebook_path}")
        sys.exit(1)

# 5. **Atualizar `requirements.txt`:**
# ```
# nbconvert>=7.0.0
# ```

# 6. **Estrutura de diretórios necessária:**
# ```
# projeto/
# ├── notebooks/
# │   └── analise_sensores.ipynb  (seu notebook original)
# ├── app/
# │   ├── static/
# │   │   └── fase6/
# │   │       └── pbl.html  (gerado automaticamente)