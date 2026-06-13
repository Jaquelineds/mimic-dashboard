# 🏥 Dashboard Interativo MIMIC-IV

Dashboard desenvolvido para a disciplina de **Visualização de Dados**, com o objetivo de explorar informações clínicas presentes no conjunto de dados **MIMIC-IV Clinical Database Demo v2.2** por meio de visualizações interativas construídas com **Streamlit**, **Plotly** e **NetworkX**.

A aplicação permite analisar aspectos demográficos, padrões de internação, exames laboratoriais e prescrições médicas, oferecendo uma interface intuitiva para exploração dos dados.

---

## 👥 Autores

- Francisco João Lucca Neto
- Jaqueline Dahmer Steffenon
- João Vitor Gularte
- Letícia Brasil Flores

---

## 🌐 Aplicação Online

Acesse o dashboard em:

🔗 https://mimic-dashboard.streamlit.app/

---

## ✨ Funcionalidades

- 👥 **Análise Demográfica**
  - Distribuição de idade dos pacientes
  - Distribuição por gênero
  - Comparação da idade entre gêneros

- 🏥 **Análise de Internações**
  - Distribuição dos tipos de admissão hospitalar
  - Tempo médio de permanência por tipo de admissão

- 🧪 **Análise de Exames Laboratoriais**
  - Exames mais solicitados
  - Combinações mais frequentes de exames
  - Redes de coocorrência entre exames

- 💊 **Análise de Medicamentos**
  - Medicamentos mais prescritos
  - Combinações mais frequentes de medicamentos
  - Redes de co-prescrição

- 🎛️ **Filtros Interativos**
  - Gênero
  - Faixa etária
  - Tipo de admissão
  - Quantidade de resultados exibidos
  - Frequência mínima das conexões nas redes

---

## 🛠️ Tecnologias Utilizadas

- **Python**
- **Streamlit**
- **Pandas**
- **Plotly**
- **NetworkX**

---

## 📊 Conjunto de Dados

Este projeto utiliza exclusivamente o **MIMIC-IV Clinical Database Demo v2.2**, uma versão demonstrativa da base de dados MIMIC-IV disponibilizada pelo **PhysioNet**.

O conjunto de dados contém informações clínicas **desidentificadas** de aproximadamente **100 pacientes**, sendo destinado exclusivamente para **fins educacionais e de pesquisa**.

Mais informações:

🔗 https://physionet.org/content/mimic-iv-demo/2.2/

---

## 📚 Referências

### Base de Dados Utilizada

Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023).

*MIMIC-IV Clinical Database Demo* (Version 2.2). PhysioNet.

DOI: https://doi.org/10.13026/dp1f-ex47

---

### Artigo Principal do MIMIC-IV

Johnson, A. E. W., Bulgarelli, L., Shen, L., et al. (2023).

*MIMIC-IV, a freely accessible electronic health record dataset*.

**Scientific Data, 10**, 1.

DOI: https://doi.org/10.1038/s41597-022-01899-x

---

## ⚠️ Aviso

Todos os dados utilizados neste projeto são **desidentificados** e fazem parte da versão demonstrativa do **MIMIC-IV**, disponibilizada pelo **PhysioNet** para fins **educacionais e de pesquisa**.

Este projeto foi desenvolvido exclusivamente para fins acadêmicos na disciplina de **Visualização de Dados**.

---