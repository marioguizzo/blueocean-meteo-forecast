async function carregarCSV() {

    const response = await fetch(
        "previsoes_operacionais.csv"
    )

    const texto = await response.text()

    const linhas = texto.split("\n")

    const cabecalho = linhas[0]
        .split(",")

    const dados = linhas
        .slice(1)
        .filter(l => l.trim() !== "")
        .map(linha => {

            const valores = linha.split(",")

            let obj = {}

            cabecalho.forEach((col, i) => {

                obj[col.trim()] =
                    valores[i]?.trim()
            })

            return obj
        })

    montarCards(dados)
}

//////////////////////////////////////////////////////////////////

function montarCards(dados) {

    const grid =
        document.getElementById("grid")

    //////////////////////////////////////////////////////////////

    grid.innerHTML = ""

    //////////////////////////////////////////////////////////////

    const agrupado = {}

    dados.forEach(item => {

        if (!agrupado[item.estacao]) {

            agrupado[item.estacao] = []
        }

        agrupado[item.estacao]
            .push(item)
    })

    //////////////////////////////////////////////////////////////

    Object.keys(agrupado)
        .forEach(estacao => {

        const previsoes =
            agrupado[estacao]

        //////////////////////////////////////////////////////////

        const risco =
            previsoes[0].risco
                ?.toLowerCase()

        //////////////////////////////////////////////////////////

        const card =
            document.createElement("div")

        //////////////////////////////////////////////////////////

        card.className =
            `card ${risco}`

        //////////////////////////////////////////////////////////

        let html = `

            <h2>${estacao}</h2>

        `

        //////////////////////////////////////////////////////////

        previsoes.forEach(p => {

            //////////////////////////////////////////////////////
            // UV
            //////////////////////////////////////////////////////

            let corUV = ""

            const uv =
                Number(p.uv)

            if (uv <= 5) {

                corUV = "#00c853"

            } else if (uv <= 10) {

                corUV = "#ffd600"

            } else {

                corUV = "#ff1744"
            }

            //////////////////////////////////////////////////////
            // CHUVA
            //////////////////////////////////////////////////////

            let corChuva = ""

            const precipitacao =
                Number(p.precipitacao)

            if (precipitacao < 10) {

                corChuva = "#00c853"

            } else if (precipitacao <= 25) {

                corChuva = "#ffd600"

            } else {

                corChuva = "#ff1744"
            }

            //////////////////////////////////////////////////////
            // VENTO
            //////////////////////////////////////////////////////

            let corVento = ""

            const rajada =
                Number(p.rajada)

            if (rajada <= 28) {

                corVento = "#00c853"

            } else if (rajada <= 40) {

                corVento = "#ffd600"

            } else {

                corVento = "#ff1744"
            }

            //////////////////////////////////////////////////////
            // UMIDADE
            //////////////////////////////////////////////////////

            let corUR = ""

            const ur =
                Number(p.umidade)

            if (ur >= 40) {

                corUR = "#00c853"

            } else if (ur >= 12) {

                corUR = "#ffd600"

            } else {

                corUR = "#ff1744"
            }

            //////////////////////////////////////////////////////
            // ALERTA / RAIOS
            //////////////////////////////////////////////////////

            let corRaios = ""

            const risco =
                p.risco?.toLowerCase()

            if (risco === "verde") {

                corRaios = "#00c853"

            } else if (risco === "amarelo") {

                corRaios = "#ffd600"

            } else {

                corRaios = "#ff1744"
            }

            //////////////////////////////////////////////////////

            html += `

                <div class="dia">

                    <div class="data">
                        ${p.data}
                    </div>

                    <div class="info">

<span style="
color:${corChuva};
font-weight:bold;
">
🌧️ ${p.condicao}
</span><br>

<span style="
font-weight:bold;
">
🌡️ ${p.temp_min}° |
${p.temp_max}°
</span><br>

<span style="
color:${corUV};
font-weight:bold;
">
☀️ UV: ${p.uv}
(${p.categoria_uv})
</span><br>

<span style="
color:${corUR};
font-weight:bold;
">
💧 UR: ${p.umidade}%
</span><br>

<span style="
color:${corRaios};
font-weight:bold;
">
⚡ ${p.prob_raios}%
</span><br>

<span style="
color:${corVento};
font-weight:bold;
">
💨 ${p.rajada} km/h
</span>

                    </div>

                </div>

            `
        })

        //////////////////////////////////////////////////////////

        card.innerHTML = html

        grid.appendChild(card)
    })
}

//////////////////////////////////////////////////////////////////

carregarCSV()