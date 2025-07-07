# Project Collector

O **Project Collector** é uma ferramenta de linha de comando (CLI) que percorre um diretório de código, aplica filtros configuráveis (inclusões/exclusões) e produz:

* 🗂️ **Árvore de diretórios ASCII**, destacando arquivos incluídos ou ignorados.
* 📦 **Conteúdo selecionado** opcional, encapsulado entre marcadores `START`/`END`.

Ideal para análises iterativas de projetos, auxiliando tanto desenvolvedores quanto IAs a explorarem, filtrarem e extraírem informações de forma controlada.

---

## 🚀 Instalação

```bash
pip install project-collector
```

---

## ⌨️ Uso da CLI

O comando principal é **`hpc`** (atalho de *Hephoria Project Collector*). Sua sintaxe básica:

```bash
hpc [<diretório>] [opções]
```

* `<diretório>` (opcional): caminho para a raiz do projeto. Se omitido em comandos de configuração, usa apenas a ação de gerenciamento.
* Se for análise de projeto, é recomendado usar `.` para o diretório atual.

### Exemplos

1. **Gerar apenas a árvore** com perfil `Amazilium-Foundation`:

   ```bash
   hpc . -ucfg Amazilium-Foundation --only-tree
   ```

   * Mostra estrutura sem coletar conteúdo.

2. **Coletar árvore + conteúdo** usando padrão de requisição `Project_Collector` e ignorando defaults:

   ```bash
   hpc . -ucfg Project_Collector --no-defaults
   ```

   * Aplica apenas `configs/requests/Project_Collector.json`.

3. **Definir perfil padrão** para execuções futuras:

   ```bash
   hpc -scfg gepe-frontend
   hpc .  # agora usa gepe-frontend sem precisar de -ucfg
   ```

4. **Listar todos os perfis** disponíveis:

   ```bash
   hpc -lcfg
   ```

5. **Iniciar um novo perfil** (gerar skeleton de JSON):

   ```bash
   hpc -icfg MeuProjeto
   ```

6. **Debug detalhado** durante a execução:

   ```bash
   hpc . -ucfg Amazilium-Foundation --verbose
   ```

   * Exibe mensagens de inclusão/ignoração de cada arquivo.

---

## 📖 Estrutura de Configurações

Os padrões de exclusão e inclusão são definidos em arquivos JSON **internos** ao Project Collector (dentro do pacote, em `configs/`), e **não** no projeto que você está analisando. Ao executar, o CLI carrega automaticamente essas configurações:

```python
configs/
├── defaults/      # padrões de exclusão por projeto
└── requests/      # overrides e padrões de inclusão por projeto
```

Cada arquivo JSON de *request* deve conter:

```jsonc
{
    "ADDITIONAL_IGNORED_DIRS": {
        "GLOBS": [],
        "REGEX": [],
        "SUBSTRINGS": []
    },
    "ADDITIONAL_IGNORED_FILES": {
        "GLOBS": [],
        "REGEX": [],
        "SUBSTRINGS": []
    },
    "INCLUDE_FOLDER_PATTERNS": {
        "GLOBS": [],
        "REGEX": [],
        "SUBSTRINGS": []
    },
    "INCLUDE_FILE_PATTERNS": {
        "GLOBS": [],
        "REGEX": [],
        "SUBSTRINGS": []
    },
    "INCLUDE_CONTENT_PATTERNS": {
        "REGEX": [],
        "SUBSTRINGS": []
    }
}
```

* **Defaults** (`configs/defaults/<projeto>.json`): padrões de exclusão globais (nome de pastas/arquivos).
* **Requests** (`configs/requests/<projeto>.json`): adicionais de exclusão e regras de inclusão.

---

## 💡 Abordagens Iterativas

Cada situação de uso pode demandar um fluxo diferente, sempre de forma iterativa — ajuste um filtro por vez, avalie o resultado e decida se precisa de nova iteração:

1. **Explorar sem contexto (descoberta)**

   * **Quando usar**: você ou a IA não conhecem a estrutura interna do projeto.
   * **Objetivo**: mapear o espaço de arquivos disponíveis.
   * **Passos**:

     1. Rode: `hpc <diretório> --use-config <perfil> --only-tree`
     2. Analise a árvore (arquivos `>>> incluído <<<` x `(ignored)`).
     3. Identifique possíveis pastas/arquivos de interesse.
   * **Iteração**: ajuste os padrões iniciais em `configs/requests/<perfil>.json` e repita até ter escopo adequado.

2. **Focar em um alvo conhecido**

   * **Quando usar**: você já sabe o arquivo ou pasta de interesse (ex.: `ClasseX.js`, módulo `user`).
   * **Objetivo**: filtrar exatamente aquele alvo.
   * **Passos**:

     1. Defina `INCLUDE_FILE_PATTERNS` para o nome exato ou glob (ex.: `"ClasseX.js"`).
     2. Ou use `INCLUDE_FOLDER_PATTERNS` com substring ou multi-segmento (ex.: `"src/user"`).
     3. Rode `hpc <diretório> --use-config <perfil> --only-tree` para validar árvore ou sem `--only-tree` para trazer conteúdo.
   * **Iteração**: se incluir demais ou de menos, refina o padrão (glob ↔ regex ↔ substring).

3. **Reaproveitar lógica existente**

   * **Quando usar**: quer ver implementações já prontas ou padrões de código.
   * **Objetivo**: localizar trechos por conteúdo (nomes de funções, classes, variáveis).
   * **Passos**:

     1. Use `INCLUDE_CONTENT_PATTERNS` com substring ou regex (ex.: `"process.env"`, `"funçãoA"`).
     2. Rode sem `--only-tree` para coletar blocos START/END e revisar o código.
   * **Iteração**: combine com `INCLUDE_FOLDER_PATTERNS` ou `INCLUDE_FILE_PATTERNS` para restringir a pastas específicas.

4. **Fluxo misto e refinamento contínuo**

   * **Quando usar**: necessidade de combinar filtros de pasta, arquivo e conteúdo.
   * **Objetivo**: equilibrar escopo amplo e precisão, sem excluir demais.
   * **Passos**:

     1. Comece amplo (ex.: só `INCLUDE_FOLDER_PATTERNS`).
     2. Analise resultados e adicione `INCLUDE_FILE_PATTERNS` ou `INCLUDE_CONTENT_PATTERNS` gradualmente.
     3. Utilize `--verbose` para entender por que cada arquivo foi incluído ou ignorado.
   * **Iteração**: monitore quantidade de resultados; ajuste filtros um a um para evitar uso excessivo ou insuficiente.

> **Dica**: mantenha sempre o objetivo principal em mente, trace onde você está no fluxo, e só avance para novos ajustes após validar cada etapa.

## 🎯 Exemplos de Cenários

### 1. Apenas excluir pasta de testes (substring)

```jsonc
"ADDITIONAL_IGNORED_DIRS": {"SUBSTRINGS":["__tests__"]}
```

* **Comportamento**: desce na árvore, mas ignora completamente `__tests__`.

### 2. Apenas incluir pastas `models` (substring)

```jsonc
"INCLUDE_FOLDER_PATTERNS": {"SUBSTRINGS":["models"]}
```

* **Comportamento**: todos os arquivos em qualquer diretório cujo nome ou caminho contenha `models` são mostrados; todo o resto é ignorado.

### 3. Apenas incluir arquivos de teste (glob)

```jsonc
"INCLUDE_FILE_PATTERNS": {"GLOBS":["*.test.js"]}
```

* **Comportamento**: apenas arquivos cujo nome bata o padrão `*.test.js` são incluídos.

### 4. Apenas filtrar por conteúdo (substring)

```jsonc
"INCLUDE_CONTENT_PATTERNS": {"SUBSTRINGS":["UsersRepository"]}
```

* **Comportamento**: somente arquivos que contenham `UsersRepository` no texto são retornados; o filtro de conteúdo é aplicado mesmo sem `--only-tree`.

### 5. Excluir arquivos temporários (regex)

```jsonc
"ADDITIONAL_IGNORED_FILES": {"REGEX":["^temp_.*\.js$"]}
```

* **Comportamento**: remove todo arquivo cujo nome comece com `temp_` e termine em `.js`.

### 6. Incluir controladores via regex no nome (regex)

```jsonc
"INCLUDE_FILE_PATTERNS": {"REGEX":["Controller.*\.js$"]}
```

* **Comportamento**: inclui apenas arquivos cujo nome casem com a regex, por exemplo `UserController.js`, `OrderController.js`.

### 7. Apenas excluir diretório `dist` e incluir tudo o mais (mix ignore + include)

```jsonc
"ADDITIONAL_IGNORED_DIRS": {"SUBSTRINGS":["dist"]},
"INCLUDE_FOLDER_PATTERNS": {"SUBSTRINGS":["src"]}
```

* **Comportamento**: ignora pastas `dist`, mas só inclui arquivos dentro de qualquer `src`.

### 8. Uso combinado de glob, regex e substring

```jsonc
{
  "ADDITIONAL_IGNORED_DIRS":    { "GLOBS":[".*"],            "REGEX":[],              "SUBSTRINGS":["__pycache__"] },
  "INCLUDE_FOLDER_PATTERNS":    { "GLOBS":["*/models"],      "REGEX":["^usecases$"],"SUBSTRINGS":["utils"] },
  "INCLUDE_FILE_PATTERNS":      { "GLOBS":["*.js","*.ts"],  "REGEX":["^Base.*\.js$"],"SUBSTRINGS":["Schema"] },
  "INCLUDE_CONTENT_PATTERNS":   { "REGEX":["TODO:"],           "SUBSTRINGS":["// FIXME"] }
}
```

* **Comportamento**:

  1. Exclui todas as pastas ocultas (glob `.*`) e `__pycache__`.
  2. Inclui pastas que:

     * Batam o glob: qualquer `models` em qualquer nível;
     * Batam o regex: pasta exatamente chamada `usecases`;
     * Contenham substring `utils`.
  3. Dentro dessas, inclui arquivos que:

     * Batam glob em `.js` ou `.ts`;
     * Batam regex `^Base.*\.js$`;
     * Contenham substring `Schema`.
  4. Ainda dentro desses arquivos, só retorna os que tenham `TODO:` ou `// FIXME` no código.

---

## 🛠️ Comandos Úteis

* `-ucfg, --use-config <nome>`: escolhe perfil temporário.
* `-scfg, --set-config <nome>`: define perfil padrão.
* `-ccfg, --clear-config`  : limpa perfil padrão.
* `-gcfg, --get-config`    : mostra perfil padrão.
* `-lcfg, --list-configs`  : lista todos os perfis.
* `-icfg, --init-config X` : cria skeleton em `defaults/X.json` e `requests/X.json`.
* `--no-defaults`          : ignora arquivos de `defaults/`.
* `--only-tree`            : só exibe árvore, sem coletar conteúdo.
* `-v, --verbose`          : logs de debug.

---

## 🔍 Boas Práticas

Para humanos e IAs usarem o Project Collector sem erros, foque nestes pontos-chave:

* **Use `--verbose` para debugar**: entenda por que cada arquivo foi incluído ou ignorado antes de ajustar filtros.
* **Evite padrões conflitantes**: defina globs, regex e substrings de forma hierárquica (excludes → include\_folder → include\_file → include\_content) para não neutralizar regras específicas.
* **Refinamento progressivo**: aplique primeiro substrings simples, depois expanda para regex ou globs conforme necessário; teste cada ajuste isoladamente.
* **Gere somente o `requests` config necessário**: crie/edit o JSON em `configs/requests/`, sem alterar defaults a menos que seja imprescindível.

## 🤖 Integração com IAs

Quando uma IA interagir com o Project Collector, é vital que ela siga um método iterativo e evite armadilhas de alucinação:

1. **Siga rigorosamente 'Abordagens Iterativas'**: em vez de misturar filtros arbitrariamente, a IA deve sempre aplicar o método descrito na seção de Abordagens Iterativas para cada caso de uso, ajustando um filtro por vez e validando antes de avançar.
2. **Detecte uso inútil**: se um filtro não reduzir resultados ou produzir árvore idêntica, a IA deve reconhecer e parar para redefinir padrões.
3. **Previna loops sem fim**: limite o número de iterações ou mudanças de filtro; se após 3 ajustes não houver progresso, peça feedback adicional.
4. **Reaproveite lógica existente**: antes de criar novos padrões, a IA deve pesquisar implementações semelhantes no código e sugerir reutilização.
5. **Mantenha o objetivo em mente**: em cada passo, verifique se a filtragem aproxima ao alvo; caso contrário, avalie se precisa de mais contexto ou se deve abortar a busca.
6. **Sempre forneça o config quando quiser fazer a busca**: SEMPRE que quiser fazer uma busca, forneça um ou os 2 configs, sempre enviando o config de request e, somente quando necessário, enviando o default. Só mexa no config default se realmente for necessário, se n tiver como solucionar rodando Project_Collector em uma subpasta diferente, tiver que alterar algo de lá pois está ignorando uma informação que precisa ou pegando algo desnecesário em muitas requisições diferentes.

Seguindo essas práticas, IAs evitarão filtros muito nichados ou vagos, loops intermináveis e intervenções humanas constantes.

### 🧠 Pensamento Crítico para IAs

Antes de acionar qualquer comando:

1. **Defina seu objetivo com precisão**

   * Que pergunta você quer responder?
   * Que tipo de informação (arquivo inteiro, método específico, trecho de código) é realmente necessária?

2. **Formule hipóteses de escopo usando pistas de contexto**

      > **Nunca presuma nomes de pasta, arquivo ou conteúdo**.
         Se você não tem certeza, comece usando filtros de conteúdo para descobrir onde o termo aparece, depois refine.

   * Reúna tudo o que você já sabe sobre o alvo: nomes de arquivos, diretórios, conteúdo presente nos arquivos como funções, variáveis, tipos, comentários padrões de código relevantes ou qualquer outro.
   * Combine filtros que aproveitem essas pistas, por exemplo:

     * **Diretório + nome de arquivo** (ex.: `/sales/` + `subscriptions_controller.dart`)
     * **Arquivo + trecho de código** (ex.: `subscriptions_controller.dart` + `void update(`)
     * **Diretório + padrão de conteúdo** (ex.: `home/cash_register` + `history`)
   * Avalie se a combinação reduz ruído sem omitir dados cruciais: busque o melhor equilíbrio entre foco e cobertura.

3. **Avalie trade-offs de complexidade e volume de saída**

   * **Complexidade do filtro:** padrões muito sofisticados podem ser frágeis e custosos para ajustar.
   * **Tamanho do output:**

     * Escopo estreito → risco de perder informações relevantes.
     * Escopo amplo → excesso de dados e sobrecarga.
   * Use julgamento crítico para decidir quais e quantos filtros aplicar em cada iteração, visando um resultado manejável e relevante.

4. **Execute e revise qualitativamente**

   * Rode o comando no escopo definido.
   * Avalie:

     * "Encontrei exatamente o que procurava?"
     * "Faltou contexto para a próxima etapa?"
     * "Veio ruído demais?"
   * Registre brevemente o que funcionou e o que não foi eficaz.

5. **Itere com propósito**

   * Se o resultado atender ao objetivo → prossiga.
   * Se não → ajuste seus filtros com base no feedback; reformule sua hipótese inicial se necessário.
   * Documente suas decisões para facilitar futuras iterações.

6. **Seleção e alternância de estratégias de busca**

   * Identifique camadas de abordagem:
      Utilizando prioridade filtro dependendo da abordagem, só incluindo um filtro de menor prioridade se realmente ouver necessiade.

     * **Micro:** foco em arquivo ou conteúdo, com pistas claras.

         * **Relação de prioridade**:

            conteúdo > arquivo > diretório,

     * **Médio:** foco em diretórios, módulos ou grupos de arquivos relacionados.
     * **Macro:** visão do projeto inteiro, analisando estrutura geral, padrões ou dependências.

         * **Relação de prioridade**:

            diretório > arquivo > conteúdo,

   * Escolha a camada inicial dependendo do seu conhecimento do alvo e do volume de dados esperado.
   * Avalie a eficácia de cada camada:

     * Se **micro** não for suficiente, escale para **médio** (ex.: filtrar pastas inteiras).
     * Se **médio** ainda gerar ruído ou faltar contexto, escale para **macro** (mapear estrutura ampla) ou refine filtros.
   * Mude de camada de forma consciente, anotando o motivo da transição para orientar futuras buscas.

> **Dica:** antes de fornecer seu JSON de request, forneça um breve comentário sobre o “Objetivo da busca” e a “Hipótese de escopo” para dar contexto a qualquer iteração futura.

* **Tarefas isoladas**: especifique uma única busca por vez (ex.: buscar padrões de pasta OU de conteúdo, não ambos simultaneamente sem validação).
* **Confirmação de contexto**: peça à IA para validar a árvore e sugerir ajustes no JSON antes de coletar conteúdo.
