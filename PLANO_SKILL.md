# PLANO_SKILL

## Objetivo

Alinhar a [SKILL.md](C:/Users/Davib/OneDrive/Área%20de%20Trabalho/Stanford-Claw4s/SKILL.md) ao paper atual descrito em [content.md](C:/Users/Davib/OneDrive/Área%20de%20Trabalho/Stanford-Claw4s/content.md), mudando o mínimo possível do contrato executável e preservando o comportamento esperado para teste com OpenClaw.

O princípio é simples:

- manter intacto o caminho canônico de reprodução do repositório;
- atualizar apenas o framing científico e as superfícies de auditoria científica;
- não transformar a skill em uma nova interface;
- não quebrar automação, comandos, verificações, outputs ou expectativas do OpenClaw.

## Regra-Mãe

Existem dois centros diferentes e ambos precisam continuar explícitos:

1. **Centro executável canônico**
   - `TP53`
   - `uv sync --frozen`
   - `uv run spectralbio canonical`
   - `outputs/canonical/*`

2. **Centro científico do paper**
   - `BRCA2` como flagship stronger-baseline
   - `TP53` como validation/structural anchor
   - `scale-repair failure mode`
   - `bounded breadth`
   - `rulebook + orthogonal + multifamily + adjudication + localization`

O erro atual da skill não é técnico. O erro atual é de **desalinhamento narrativo**:

- o contrato executável está razoavelmente certo;
- a narrativa científica da skill está atrasada em relação ao paper atual.

## O Que Não Pode Mudar

Estas partes devem permanecer essencialmente intactas:

### 1. Front matter técnico

Manter:

- `name`
- `description` com mesma função operacional geral
- `allowed-tools`
- `package_manager`
- `repo_url`
- `repo_root`
- `canonical_output_dir`
- `secondary_output_dir`
- `python_version`

Motivo:

- isso é a superfície mais sensível para OpenClaw;
- mexer aqui aumenta risco sem ganho científico real.

### 2. Contrato de execução

Manter:

- `uv sync --frozen`
- `uv run spectralbio canonical`
- `uv run spectralbio transfer`
- `uv run spectralbio verify`
- `uv run python scripts/preflight.py`

Motivo:

- o usuário quer mudar o mínimo;
- o problema da skill não está nos comandos;
- o problema está em quais superfícies científicas ela aponta para explicar o paper.

### 3. Centro canônico TP53

Manter:

- `TP53` como replay canônico
- `outputs/canonical/summary.json`
- `outputs/canonical/verification.json`
- checks de AUC e de bundle

Motivo:

- isso continua correto no paper e no repo;
- o `content.md` não muda essa verdade.

### 4. Truth anchors que o usuário explicitamente quer manter

Manter em `## Truth Boundary`:

- `docs/truth_contract.md`
- `docs/reproducibility.md`
- `outputs/canonical/summary.json`
- `outputs/canonical/verification.json`

Também manter:

- `artifacts/expected/expected_metrics.json`
- `artifacts/expected/expected_files.json`
- `artifacts/expected/output_schema.json`
- `artifacts/expected/verification_rules.json`

Motivo:

- esses anchors continuam corretos;
- o usuário explicitamente pediu que aqui também fosse mantido;
- eles sustentam a parte “repo truth” da skill.

## Diagnóstico Exato do Que Está Desatualizado

### Problema 1. `Mission` está subdimensionada

Hoje a `Mission` fala de:

- BRCA2 flagship
- TP53 validation anchor
- top-25 breadth
- BRCA1 transfer bounded

Mas o paper atual tem um arco mais completo:

- BRCA2 flagship
- TP53 structural smoking gun
- scale-repair failure mode como resultado qualitativo central
- bounded breadth via panel + gallery + anti-case
- final stopping point supportive not nuclear

Consequência:

- a skill ainda “explica” um paper menos maduro do que o paper atual.

### Problema 2. `Scientific And Executable Contract` está estreito demais

Hoje ele cobre bem:

- BRCA2
- TP53
- support-ranked panel
- BRCA1 boundary

Mas não cobre de forma explícita:

- `07c` structural dissociation
- `02` failure-mode chain
- `11` rulebook
- `12` orthogonal TP53
- `12b` multifamily breadth
- `12c` covariance adjudication
- `12d` final localization

Consequência:

- a skill não representa a cadeia final de adjudicação do paper.

### Problema 3. `Truth Boundary` usa superfícies antigas demais

Hoje a seção manda olhar:

- `abstract.md`
- `content.md`
- `notebooks/final_accept_part*.ipynb`

Esses notebooks existem e podem continuar como superfícies legadas úteis, mas o paper atual foi reconstruído usando os `New Notebooks`.

Consequência:

- OpenClaw pode auditar o paper por uma trilha de notebooks antiga, incompleta ou desalinhada.

### Problema 4. `Public Scientific Audit Surfaces` está presa ao conjunto errado

Hoje a seção lista:

- `notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb`
- `notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb`
- `notebooks/final_accept_part1_support_panel.ipynb`
- `notebooks/final_accept_part5_protocol_sweep_A100.ipynb`
- `notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb`

Isso cobre parte da história, mas não cobre a história atual completa.

Consequência:

- o OpenClaw não recebe a lista correta das superfícies científicas que hoje sustentam o paper.

### Problema 5. `Verification Contract` científico está incompleto

Hoje ele inclui:

- BRCA2 flagship delta
- TP53 replay truth
- top-25 panel
- BRCA1 bounded transfer framing

Mas faltam como itens explícitos:

- structural dissociation `0.309 vs 0.036`
- scale-repair matched-pair result
- sister-substitution result
- clinical panel `4/4` and `12 candidates`
- final adjudication `6 supportive / 0 nuclear / 1 supportive_localized`

Consequência:

- a skill fica correta para replay, mas fraca para auditoria científica do paper atual.

### Problema 6. `Failure Modes` não protegem o novo arco do paper

Hoje a seção protege:

- TP53 como default executable path
- BRCA2 não virar CLI default
- BRCA1 não virar co-primary

Mas não protege:

- omissão do `scale-repair failure mode`
- omissão do `07c` structural smoking gun
- omissão da cadeia `11/12/12b/12c/12d`
- apagamento do final `supportive rather than nuclear`

Consequência:

- a skill ainda pode passar em termos operacionais, mas falhar em fidelidade ao paper.

## Estratégia de Edição Mínima

A estratégia será **complementar**, não reescrever tudo.

Em vez de trocar radicalmente a skill, o plano é:

1. preservar tudo que é contrato executável;
2. expandir o framing científico onde ele está curto;
3. adicionar os `New Notebooks` certos como audit surfaces;
4. não remover imediatamente os `final_accept_part*` se eles ainda forem úteis como superfícies legadas.

Essa é a abordagem mais segura para OpenClaw.

## Plano Seção por Seção

## 1. `## Mission`

### Status atual

Boa para:

- replay do repo
- TP53 canonical
- BRCA2 flagship básico

Insuficiente para:

- arco narrativo do paper atual

### Mudança planejada

Editar os bullets para refletir:

- flagship scientific result: `BRCA2`
- validation and structural anchor: `TP53`
- qualitative audit result: `scale-repair failure mode`
- bounded breadth: `top-25 panel + clinical panel + rescue gallery`
- final claim boundary: `supportive rather than nuclear`

### O que fica

- linguagem de “public replay and audit surface”
- ideia de `adaptation recipe only`

### O que entra

- menção explícita ao `scale-repair failure mode`
- menção explícita ao stopping point supportive/not nuclear

### Motivo

Sem isso, a skill começa explicando um paper mais fraco do que o `content.md`.

## 2. `## Scientific And Executable Contract`

### 2.1 `### Manuscript Scientific Center`

### Mudança planejada

Manter:

- BRCA2 flagship
- TP53 validation anchor
- top-25 panel
- BRCA1 boundary

Adicionar:

- `07c` structural dissociation as mechanistic readout
- `02` failure-mode chain as qualitative centerpiece
- `11/12/12b/12c/12d` as the final adjudication chain

### Motivo

Hoje essa seção ainda não conta o paper completo.

### 2.2 `### Frozen Executable Replay Center`

### Mudança planejada

Mudança mínima.

Provavelmente só reforçar:

- `TP53` remains the only canonical scored benchmark
- `BRCA2` remains scientific flagship but not frozen CLI default

### Motivo

Aqui quase nada está errado. Não vale mexer além do necessário.

## 3. `## Scope And Non-Claims`

### 3.1 `### Scope`

### Mudança planejada

Acrescentar uma linha curta dizendo que:

- the current manuscript-level audit also includes structural dissociation, bounded breadth curation, and late adjudication notebooks

### 3.2 `### Non-Claims`

### Mudança planejada

Adicionar, se necessário, uma formulação mais alinhada ao paper:

- no nuclear closure claim
- no universal covariance-native cross-family transfer claim

### Motivo

Isso bate diretamente com o final do `content.md`.

## 4. `## Truth Boundary`

### Status atual

Metade correta, metade desatualizada.

### O que fica obrigatoriamente

Em `repository truth rather than guess`, manter:

- `docs/truth_contract.md`
- `docs/reproducibility.md`
- `artifacts/expected/expected_metrics.json`
- `artifacts/expected/expected_files.json`
- `artifacts/expected/output_schema.json`
- `artifacts/expected/verification_rules.json`
- `outputs/canonical/summary.json`
- `outputs/canonical/verification.json`

### O que muda em `manuscript-aligned scientific framing and public audit surfaces`

Manter:

- `abstract.md`
- `content.md`

Substituir ou complementar os `final_accept_part*` com:

- `New Notebooks/01_block1_baseline_alpha_regime_audit_h100.ipynb`
- `New Notebooks/02_block2_failure_mode_hunt_h100.ipynb`
- `New Notebooks/05_block3_structure_bridge_h100.ipynb`
- `New Notebooks/06_block5_clinical_panel_audit_h100.ipynb`
- `New Notebooks/07c_block10_structural_dissociation_tp53_h100.ipynb`
- `New Notebooks/08_block7_turbo_gallery_rescues_h100.ipynb`
- `New Notebooks/11_block11_covariance_rulebook_h100.ipynb`
- `New Notebooks/12_block12_orthogonal_validation_tp53_h100.ipynb`
- `New Notebooks/12b_block12_multifamily_coverage_aware_generalization_h100.ipynb`
- `New Notebooks/12c_block12_covariance_adjudication_structural_closure_h100.ipynb`
- `New Notebooks/12d_block12_final_nuclear_localization_h100.ipynb`

### Recomendação exata

Para mexer menos:

- manter os `final_accept_part*` como `legacy scientific audit surfaces`
- adicionar nova subseção:
  - `Current manuscript audit surfaces`

### Motivo

Isso reduz risco e preserva retrocompatibilidade.

## 5. `## When to Use This Skill`

### `Case 1 - Canonical replay`

Nenhuma mudança substancial.

### `Case 2 - Public scientific audit`

### Mudança planejada

Trocar:

- “BRCA2 / panel notebooks listed in Truth Boundary”

Por algo mais preciso:

- current manuscript audit surfaces in `New Notebooks`, especially stronger-baseline, failure-mode, structural dissociation, gallery, rulebook, and adjudication blocks

### `Case 3 - Optional bounded auxiliary validation`

Nenhuma mudança substancial.

### `Case 4 - Out of scope`

Nenhuma mudança substancial.

### Motivo

OpenClaw precisa ser encaminhado para a trilha científica certa sem perder o caminho operacional.

## 6. `## Verification Contract`

### 6.1 `### Machine-Verified Replay Contract`

### Mudança planejada

Nenhuma, ou quase nenhuma.

Motivo:

- isso é execução canônica;
- não é onde a skill está desalinhada.

### 6.2 `### Scientific Audit Contract`

### Mudança planejada

Manter:

- BRCA2 flagship delta
- BRCA2 CI
- BRCA2 permutation p-value
- TP53 replay centrality
- top-25 panel breadth framing

Adicionar:

- TP53 structural dissociation: `0.309 vs 0.036`
- scale-repair matched-pair result: `0.7250`, `p = 0.000244`
- sister-substitution support: `p = 0.007812`
- clinical-panel result: `4/4 positive-focus`, `12 rescue candidates`
- final adjudication result:
  - `6 supportive`
  - `0 nuclear`
  - `0 transfer-positive`
  - `1 supportive_localized`

### Motivo

Sem isso, a skill não descreve a ciência final do paper.

## 7. `## Public Scientific Audit Surfaces`

### Status atual

É hoje a seção mais claramente desatualizada.

### Mudança planejada

Manter os `final_accept_part*` apenas se quisermos backward compatibility.

Adicionar uma lista nova com label explícita:

### `Current manuscript audit surfaces`

- `New Notebooks/01_block1_baseline_alpha_regime_audit_h100.ipynb`
- `New Notebooks/02_block2_failure_mode_hunt_h100.ipynb`
- `New Notebooks/05_block3_structure_bridge_h100.ipynb`
- `New Notebooks/06_block5_clinical_panel_audit_h100.ipynb`
- `New Notebooks/07c_block10_structural_dissociation_tp53_h100.ipynb`
- `New Notebooks/08_block7_turbo_gallery_rescues_h100.ipynb`
- `New Notebooks/11_block11_covariance_rulebook_h100.ipynb`
- `New Notebooks/12_block12_orthogonal_validation_tp53_h100.ipynb`
- `New Notebooks/12b_block12_multifamily_coverage_aware_generalization_h100.ipynb`
- `New Notebooks/12c_block12_covariance_adjudication_structural_closure_h100.ipynb`
- `New Notebooks/12d_block12_final_nuclear_localization_h100.ipynb`

### Motivo

É isso que o paper atual realmente usa.

## 8. `## Failure Modes`

### Status atual

Boa para proteger o contrato canônico.

Insuficiente para proteger a narrativa nova do paper.

### Mudança planejada

Adicionar novos failure modes:

- omitir `07c` como structural anchor
- omitir `02` como failure-mode centerpiece
- omitir `11/12/12b/12c/12d` como adjudication chain
- descrever o paper como se BRCA2 e TP53 fossem só um dual-center indistinto
- apagar o stopping point `supportive rather than nuclear`

### Motivo

Isso é exatamente o tipo de drift que queremos evitar no OpenClaw.

## 9. `## Minimal Copy-Paste Path`

### Mudança planejada

Provavelmente nenhuma.

Motivo:

- não é aqui que a skill está errada;
- não vale arriscar o caminho mais sensível para automação.

## Plano de Implementação Real

## Fase 1. Mudanças obrigatórias

Editar:

- `## Mission`
- `## Scientific And Executable Contract`
- `## Truth Boundary`
- `## When to Use This Skill`
- `## Verification Contract` -> `### Scientific Audit Contract`
- `## Public Scientific Audit Surfaces`
- `## Failure Modes`

## Fase 2. Mudanças opcionais e de baixo risco

Editar, só se necessário:

- `## Scope And Non-Claims`

## Fase 3. Não tocar

Não editar:

- front matter técnico
- `Execution Envelope`
- `Runtime Expectations`
- `Step 0` a `Step 5`
- `What Creates And Checks The Files`
- `Canonical Success Criteria`
- `Optional Full Validation`
- `Command Truth`
- `Adaptation Architecture`
- `Optional Revalidation Note`
- `Auxiliary Repository Capabilities`
- `Minimal Copy-Paste Path`

## Critérios de Sucesso da Nova Skill

A skill nova estará boa se, ao mesmo tempo:

1. continuar mandando o OpenClaw para:
   - `uv sync --frozen`
   - `uv run spectralbio canonical`

2. continuar tratando:
   - `TP53` como replay canônico
   - `BRCA2` como flagship científico

3. passar a refletir explicitamente:
   - `TP53 structural smoking gun`
   - `scale-repair failure mode`
   - `bounded breadth + gallery + anti-case`
   - `rulebook + orthogonal + multifamily + adjudication + localization`
   - final claim `supportive rather than nuclear`

4. direcionar OpenClaw para os `New Notebooks` certos

5. não introduzir nenhum comando novo ou superfície executável nova

## Resultado Esperado

Depois dessas mudanças, a skill ficará:

- minimamente alterada no que é executável;
- substancialmente melhor no que é científico;
- alinhada com o paper atual;
- mais segura para OpenClaw;
- forte o bastante para não reproduzir a narrativa antiga por engano.

## Nota Final

Se a prioridade máxima for risco mínimo para OpenClaw, a melhor tática é:

- **não substituir brutalmente** as superfícies antigas;
- **complementar** a skill com as superfícies novas;
- manter TP53 canonical como centro executável;
- adicionar os `New Notebooks` como centro científico atual do manuscrito.

Essa é a estratégia com melhor razão entre:

- fidelidade ao paper,
- preservação do contrato do repo,
- segurança operacional no teste.
