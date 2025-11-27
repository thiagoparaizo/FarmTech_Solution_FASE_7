/**
 * FarmTech Solutions - Scripts Comuns
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers do Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Manipulação de campos de geometria nos formulários
    const tipoGeometriaSelect = document.getElementById('tipo_geometria');
    if (tipoGeometriaSelect) {
        const geometryFields = document.querySelectorAll('.geometry-fields');
        
        function toggleGeometryFields() {
            // Ocultar todos os campos de geometria
            geometryFields.forEach(field => {
                field.style.display = 'none';
                
                // Desativar validação dos campos ocultos
                const inputs = field.querySelectorAll('input');
                inputs.forEach(input => {
                    input.required = false;
                });
            });
            
            // Exibir campos do tipo de geometria selecionado
            const selectedGeometry = tipoGeometriaSelect.value;
            if (selectedGeometry) {
                const selectedFields = document.getElementById(selectedGeometry + '-fields');
                if (selectedFields) {
                    selectedFields.style.display = 'flex';
                    
                    // Ativar validação dos campos visíveis
                    const inputs = selectedFields.querySelectorAll('input');
                    inputs.forEach(input => {
                        input.required = true;
                    });
                }
            }
        }
        
        // Chamar a função quando a página carrega e quando o select muda
        toggleGeometryFields();
        tipoGeometriaSelect.addEventListener('change', toggleGeometryFields);
    }
    
    // Cálculo de área na calculadora
    const calculoAreaForm = document.getElementById('calculoAreaForm');
    if (calculoAreaForm) {
        calculoAreaForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Obter valores do formulário
            const tipoGeometria = document.getElementById('tipo_geometria').value;
            let params = { tipo_geometria: tipoGeometria };
            
            // Adicionar parâmetros de acordo com o tipo de geometria
            switch (tipoGeometria) {
                case 'retangular':
                    params.comprimento_m = parseFloat(document.getElementById('comprimento_m').value);
                    params.largura_m = parseFloat(document.getElementById('largura_m').value);
                    break;
                case 'triangular':
                    params.base_m = parseFloat(document.getElementById('base_m').value);
                    params.altura_m = parseFloat(document.getElementById('altura_m').value);
                    break;
                case 'circular':
                    params.raio_m = parseFloat(document.getElementById('raio_m').value);
                    break;
                case 'trapezoidal':
                    params.base_maior_m = parseFloat(document.getElementById('base_maior_m').value);
                    params.base_menor_m = parseFloat(document.getElementById('base_menor_m').value);
                    params.altura_m = parseFloat(document.getElementById('altura_t_m').value);
                    break;
            }
            
            // Fazer requisição para a API
            fetch('/api/calculos/area', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao calcular área.');
                }
                return response.json();
            })
            .then(data => {
                // Exibir resultados
                document.getElementById('areaM2').textContent = data.area_m2.toFixed(2);
                document.getElementById('areaHectare').textContent = data.area_hectare.toFixed(4);
                document.getElementById('resultadoAreaCard').style.display = 'block';
                
                // Visualização da área (código simplificado)
                const areaVisualizacao = document.getElementById('areaVisualizacao');
                if (areaVisualizacao) {
                    visualizarArea(areaVisualizacao, tipoGeometria, params);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao calcular área: ' + error.message);
            });
        });
    }
    
    // Cálculo de insumos na calculadora
    const calculoInsumosForm = document.getElementById('calculoInsumosForm');
    if (calculoInsumosForm) {
        calculoInsumosForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Obter valores do formulário
            const cultura = document.getElementById('cultura_insumo').value;
            const areaHectare = parseFloat(document.getElementById('area_hectare').value);
            
            // Fazer requisição para a API
            fetch('/api/calculos/insumos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cultura: cultura,
                    area_hectare: areaHectare
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao calcular insumos.');
                }
                return response.json();
            })
            .then(data => {
                // Exibir resultados
                if (data.quantidades_kg) {
                    document.getElementById('nitrogenio').textContent = data.quantidades_kg.N.toFixed(2);
                    document.getElementById('fosforo').textContent = data.quantidades_kg.P2O5.toFixed(2);
                    document.getElementById('potassio').textContent = data.quantidades_kg.K2O.toFixed(2);
                    document.getElementById('totalFertilizante').textContent = data.quantidades_kg.total_kg.toFixed(2);
                    
                    // Valor fictício de R$ 5 por kg de fertilizante
                    const custoEstimado = data.quantidades_kg.total_kg * 5;
                    document.getElementById('custoEstimado').textContent = `R$ ${custoEstimado.toFixed(2)}`;
                    
                    document.getElementById('resultadoInsumosCard').style.display = 'block';
                    
                    // Gráfico de insumos
                    const insumosChart = document.getElementById('insumosChart');
                    if (insumosChart && window.Plotly) {
                        const data = [{
                            type: 'pie',
                            values: [
                                data.quantidades_kg.N,
                                data.quantidades_kg.P2O5,
                                data.quantidades_kg.K2O
                            ],
                            labels: ['N', 'P2O5', 'K2O'],
                            textinfo: 'label+percent',
                            marker: {
                                colors: ['#28a745', '#17a2b8', '#ffc107']
                            }
                        }];
                        
                        const layout = {
                            title: 'Distribuição de NPK',
                            showlegend: true,
                            legend: {
                                orientation: 'h'
                            },
                            margin: {t: 40, b: 0, l: 0, r: 0}
                        };
                        
                        Plotly.newPlot('insumosChart', data, layout);
                    }
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao calcular insumos: ' + error.message);
            });
        });
    }

    // Função para visualizar área na calculadora
    function visualizarArea(element, tipoGeometria, params) {
        if (!window.Plotly) {
            console.error('Plotly não está disponível.');
            return;
        }
        
        let data = [];
        let layout = {
            showlegend: false,
            margin: {t: 0, b: 0, l: 0, r: 0},
            xaxis: {
                showgrid: false,
                zeroline: false,
                visible: false
            },
            yaxis: {
                showgrid: false,
                zeroline: false,
                visible: false,
                scaleanchor: 'x'
            }
        };
        
        switch (tipoGeometria) {
            case 'retangular':
                data = [{
                    type: 'scatter',
                    mode: 'lines',
                    x: [0, params.comprimento_m, params.comprimento_m, 0, 0],
                    y: [0, 0, params.largura_m, params.largura_m, 0],
                    fill: 'toself',
                    fillcolor: 'rgba(40, 167, 69, 0.5)',
                    line: {
                        color: 'rgb(40, 167, 69)',
                        width: 2
                    },
                    hoverinfo: 'none'
                }];
                break;
                
            case 'triangular':
                data = [{
                    type: 'scatter',
                    mode: 'lines',
                    x: [0, params.base_m, params.base_m/2, 0],
                    y: [0, 0, params.altura_m, 0],
                    fill: 'toself',
                    fillcolor: 'rgba(23, 162, 184, 0.5)',
                    line: {
                        color: 'rgb(23, 162, 184)',
                        width: 2
                    },
                    hoverinfo: 'none'
                }];
                break;
                
            case 'circular':
                // Criar pontos para um círculo
                const points = 100;
                const radius = params.raio_m;
                const x = [];
                const y = [];
                
                for (let i = 0; i <= points; i++) {
                    const angle = (i / points) * 2 * Math.PI;
                    x.push(radius * Math.cos(angle) + radius);
                    y.push(radius * Math.sin(angle) + radius);
                }
                
                data = [{
                    type: 'scatter',
                    mode: 'lines',
                    x: x,
                    y: y,
                    fill: 'toself',
                    fillcolor: 'rgba(255, 193, 7, 0.5)',
                    line: {
                        color: 'rgb(255, 193, 7)',
                        width: 2
                    },
                    hoverinfo: 'none'
                }];
                break;
                
            case 'trapezoidal':
                const baseMaior = params.base_maior_m;
                const baseMenor = params.base_menor_m;
                const altura = params.altura_m;
                const diff = (baseMaior - baseMenor) / 2;
                
                data = [{
                    type: 'scatter',
                    mode: 'lines',
                    x: [0, baseMaior, baseMaior - diff, diff, 0],
                    y: [0, 0, altura, altura, 0],
                    fill: 'toself',
                    fillcolor: 'rgba(220, 53, 69, 0.5)',
                    line: {
                        color: 'rgb(220, 53, 69)',
                        width: 2
                    },
                    hoverinfo: 'none'
                }];
                break;
        }
        
        Plotly.newPlot(element, data, layout, {displayModeBar: false});
    }
    
    // Cálculo de irrigação na calculadora
    const calculoIrrigacaoForm = document.getElementById('calculoIrrigacaoForm');
    if (calculoIrrigacaoForm) {
        calculoIrrigacaoForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Obter valores do formulário
            const cultura = document.getElementById('cultura_irrigacao').value;
            const comprimento = parseFloat(document.getElementById('comprimento_campo').value);
            const largura = parseFloat(document.getElementById('largura_campo').value);
            const volumePorMetro = parseFloat(document.getElementById('volume_por_metro').value);
            
            // Fazer requisição para a API
            fetch('/api/culturas')
            .then(response => response.json())
            .then(culturas => {
                const culturaSelecionada = culturas.find(c => c.nome_cultura === cultura);
                
                if (!culturaSelecionada) {
                    throw new Error('Cultura não encontrada.');
                }
                
                // Obter o espaçamento entre linhas da cultura
                const espacamento = culturaSelecionada.dados_agronomicos.densidade_plantio.espacamento_m.entre_linhas;
                
                // Calcular número de linhas
                const numeroLinhas = Math.floor(largura / espacamento);
                
                // Calcular volume por linha
                const volumePorLinha = volumePorMetro * comprimento;
                
                // Calcular volume total
                const volumeTotal = volumePorLinha * numeroLinhas;
                
                // Exibir resultados
                document.getElementById('numeroLinhas').textContent = numeroLinhas;
                document.getElementById('volumePorLinha').textContent = volumePorLinha.toFixed(2);
                document.getElementById('volumeTotal').textContent = volumeTotal.toFixed(2);
                
                document.getElementById('resultadoIrrigacaoCard').style.display = 'block';
                
                // Visualizar irrigação
                const irrigacaoVisualizacao = document.getElementById('irrigacaoVisualizacao');
                if (irrigacaoVisualizacao && window.Plotly) {
                    visualizarIrrigacao(irrigacaoVisualizacao, numeroLinhas, comprimento, largura);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao calcular irrigação: ' + error.message);
            });
        });
    }
    
    // Função para visualizar irrigação
    function visualizarIrrigacao(element, numeroLinhas, comprimento, largura) {
        // Criar linhas para representar as ruas de plantio
        const data = [];
        
        // Calcular o espaçamento entre as linhas
        const espacamento = largura / (numeroLinhas + 1);
        
        // Adicionar cada linha
        for (let i = 1; i <= numeroLinhas; i++) {
            const y = i * espacamento;
            
            data.push({
                type: 'scatter',
                mode: 'lines',
                x: [0, comprimento],
                y: [y, y],
                line: {
                    color: 'rgb(13, 110, 253)',
                    width: 2,
                    dash: 'solid'
                },
                name: `Linha ${i}`
            });
        }
        
        // Adicionar contorno do campo
        data.push({
            type: 'scatter',
            mode: 'lines',
            x: [0, comprimento, comprimento, 0, 0],
            y: [0, 0, largura, largura, 0],
            line: {
                color: 'rgb(40, 167, 69)',
                width: 2
            },
            fill: 'none',
            name: 'Campo'
        });
        
        const layout = {
            title: 'Visualização das Linhas de Irrigação',
            showlegend: false,
            xaxis: {
                title: 'Comprimento (m)',
                zeroline: false
            },
            yaxis: {
                title: 'Largura (m)',
                zeroline: false,
                scaleanchor: 'x'
            }
        };
        
        Plotly.newPlot(element, data, layout);
    }
});
    
    