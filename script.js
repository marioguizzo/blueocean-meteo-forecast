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
        // CLASSE DO CARD
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
            // COR UV
            //////////////////////////////////////////////////////

            let corUV = ""

            if (p.risco_uv === "Verde") {

                corUV = "#00c853"

            } else if (p.risco_uv === "Amarelo") {

                corUV = "#ffd600"

            } else {

                corUV = "#ff1744"
            }

            //////////////////////////////////////////////////////

            html += `

                <div class="dia">

                    <div class="data">
                        ${p.data}
                    </div>

                    <div class="info">

🌧️ ${p.condicao}<br>

🌡️ ${p.temp_min}° |
${p.temp_max}°<br>

<span style="
color:${corUV};
font-weight:bold;
">
☀️ UV: ${p.uv}
(${p.categoria_uv})
</span><br>

⚡ ${p.prob_raios}%<br>

💨 ${p.rajada} km/h

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