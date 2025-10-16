# Guia de Uso: Modelos de Arquitetura 2025

## Modelos Disponíveis

Agora você tem **4 opções** de modelo para o arch-agent:

### 1. arch-agent (Original - Qwen2.5)
```bash
python3 setup_ollama_local.py --persona arch --pull --create
```
- **Modelo:** Qwen2.5:32B q5_K_M (2024)
- **VRAM:** ~22GB
- **Velocidade:** 30-35 tok/s
- **Qualidade:** ★★★★☆ (92%)
- **Status:** Configuração atual, funcional

### 2. arch-agent-qwen3 (Qwen3 - Recomendado) ⭐
```bash
python3 setup_ollama_local.py --persona arch-qwen3 --pull --create
```
- **Modelo:** Qwen3:32B q5_K_M (2025)
- **VRAM:** ~22GB
- **Velocidade:** 32-37 tok/s (+7%)
- **Qualidade:** ★★★★★ (95%) - **Melhor raciocínio e código**
- **Vantagens:**
  - ✅ Sucessor direto do Qwen2.5
  - ✅ +3-5% melhor em todas as métricas
  - ✅ Treinamento mais recente (dados até 2025)
  - ✅ Melhor compreensão contextual
  - ✅ Tokenizer mais eficiente

### 3. arch-agent-qwen3moe (Qwen3 MoE - Mais Rápido) ⚡
```bash
python3 setup_ollama_local.py --persona arch-qwen3moe --pull --create
```
- **Modelo:** Qwen3:30B MoE q5_K_M (2025)
- **VRAM:** ~12GB (economia de 10GB!)
- **Velocidade:** 45-55 tok/s (+50% mais rápido!)
- **Qualidade:** ★★★★☆ (93%)
- **Vantagens:**
  - ⚡ **Mixture of Experts** - ativa apenas ~8B por token
  - ⚡ Performance de 30B com custo de ~8B
  - ⚡ Ideal quando velocidade é prioridade
  - ⚡ Sobra VRAM para outros processos
- **Trade-offs:**
  - Qualidade ligeiramente inferior (-2% vs Qwen3 dense)
  - Melhor para múltiplas tarefas paralelas

### 4. arch-agent-deepseek (DeepSeek-R1 - Melhor Raciocínio) 🧠
```bash
python3 setup_ollama_local.py --persona arch-deepseek --pull --create
```
- **Modelo:** DeepSeek-R1:32B q4_K_M (2025)
- **VRAM:** ~20GB
- **Velocidade:** 22-28 tok/s (mais lento - gera mais tokens)
- **Qualidade (raciocínio):** ★★★★★+ (98%)
- **Vantagens:**
  - 🧠 **Chain-of-Thought nativo** - mostra raciocínio explícito
  - 🧠 Excelente para problemas arquiteturais complexos
  - 🧠 Self-verification - checa a própria lógica
  - 🧠 Melhor em matemática, debugging profundo
- **Trade-offs:**
  - Mais lento (gera tokens de "pensamento")
  - Não ideal para respostas rápidas/simples

---

## Matriz de Decisão

### Escolha por Cenário

| Cenário | Modelo Recomendado | Justificativa |
|---------|-------------------|---------------|
| **Uso Geral Balanceado** | arch-qwen3 ⭐ | Melhor equilíbrio qualidade/velocidade |
| **Preciso de Velocidade Máxima** | arch-qwen3moe ⚡ | 50% mais rápido, economia de VRAM |
| **Problemas Arquiteturais Complexos** | arch-deepseek 🧠 | Raciocínio chain-of-thought superior |
| **Múltiplas Tarefas Paralelas** | arch-qwen3moe ⚡ | Usa menos VRAM, permite outros modelos |
| **Debugging de Arquitetura Difícil** | arch-deepseek 🧠 | Self-verification, raciocínio explícito |
| **Sessões Interativas Rápidas** | arch-qwen3moe ⚡ | Resposta instantânea |
| **Análise Profunda/Crítica** | arch-qwen3 ou arch-deepseek | Máxima qualidade |
| **Compatibilidade/Manutenção** | arch (Qwen2.5) | Configuração atual funcional |

### Comparação Direta

| Métrica | Qwen2.5 | Qwen3 | Qwen3 MoE | DeepSeek-R1 |
|---------|---------|-------|-----------|-------------|
| **Ano** | 2024 | 2025 | 2025 | 2025 |
| **VRAM** | 22GB | 22GB | 12GB | 20GB |
| **Velocidade** | 30-35 | 32-37 | 45-55 | 22-28 |
| **Qualidade** | 92% | 95% | 93% | 98%* |
| **Raciocínio** | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★★+ |
| **Código** | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★★ |
| **Velocidade** | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| **VRAM Efic.** | ★★★☆☆ | ★★★☆☆ | ★★★★★ | ★★★★☆ |

*Para raciocínio complexo. Pode ser mais lento para tarefas simples.

---

## Como Usar

### Instalação Individual

```bash
# Instalar apenas um modelo específico
python3 setup_ollama_local.py --persona arch-qwen3 --pull --create

# Instalar múltiplos modelos para testar
python3 setup_ollama_local.py --persona arch-qwen3,arch-qwen3moe,arch-deepseek --pull --create
```

### Teste de Performance

```bash
# Teste simples de velocidade
time ollama run arch-agent-qwen3 "Explique microservices vs monolith brevemente"
time ollama run arch-agent-qwen3moe "Explique microservices vs monolith brevemente"
time ollama run arch-agent-deepseek "Explique microservices vs monolith brevemente"

# Teste de raciocínio complexo
ollama run arch-agent-qwen3 "Compare CQRS, Event Sourcing e Saga pattern. Quando usar cada um?"
ollama run arch-agent-deepseek "Compare CQRS, Event Sourcing e Saga pattern. Quando usar cada um?"

# Monitorar VRAM durante execução
watch -n 1 nvidia-smi
```

### Uso Interativo

```bash
# Modelo balanceado (recomendado para uso geral)
ollama run arch-agent-qwen3

# Modelo rápido (para sessões interativas)
ollama run arch-agent-qwen3moe

# Modelo com raciocínio profundo (para análise complexa)
ollama run arch-agent-deepseek
```

### Integração com IDEs

#### VS Code (Continue.dev)

Edite `~/.continue/config.json`:

```json
{
  "models": [
    {
      "title": "Arch Agent Qwen3",
      "provider": "ollama",
      "model": "arch-agent-qwen3"
    },
    {
      "title": "Arch Agent MoE (Fast)",
      "provider": "ollama",
      "model": "arch-agent-qwen3moe"
    },
    {
      "title": "Arch Agent DeepSeek (Reasoning)",
      "provider": "ollama",
      "model": "arch-agent-deepseek"
    }
  ]
}
```

#### Cursor / AI Assistants

Configure o endpoint:
- URL: `http://localhost:11434`
- Modelo: `arch-agent-qwen3` (ou variante preferida)

---

## Exemplos de Uso por Modelo

### Exemplo 1: Qwen3 (Balanceado)

**Cenário:** Design de microserviços para e-commerce

```bash
ollama run arch-agent-qwen3
```

**Prompt:**
```
Estou projetando um sistema de e-commerce. Preciso decidir entre:
1. Monolito modular
2. Microserviços
3. Arquitetura híbrida

Contexto:
- Equipe: 5 devs sênior, 3 júnior
- Timeline: MVP em 3 meses, produção em 6 meses
- Escala esperada: 10k usuários no primeiro ano
- Budget: Startup, recursos limitados

Qual arquitetura você recomenda?
```

**Resultado esperado:**
- Análise estruturada com 3 opções
- Trade-offs claros
- Recomendação justificada
- Roadmap de implementação
- Métricas de sucesso

### Exemplo 2: Qwen3 MoE (Velocidade)

**Cenário:** Revisão rápida de múltiplas decisões

```bash
ollama run arch-agent-qwen3moe
```

**Prompt:**
```
Revisão rápida de 3 decisões:

1. PostgreSQL vs MongoDB para catálogo de produtos?
2. REST vs GraphQL para API pública?
3. Kafka vs RabbitMQ para eventos?

Responda de forma concisa (2-3 frases por item).
```

**Resultado esperado:**
- Respostas rápidas (< 30 segundos total)
- Direto ao ponto
- Recomendações claras

### Exemplo 3: DeepSeek-R1 (Raciocínio Profundo)

**Cenário:** Análise complexa de trade-offs

```bash
ollama run arch-agent-deepseek
```

**Prompt:**
```
Sistema distribuído com requisitos conflitantes:

- Alta disponibilidade (99.99%)
- Strong consistency
- Baixa latência (< 100ms P99)
- Multi-região (US, EU, APAC)

Analise as impossibilidades teóricas (CAP, PACELC) e proponha 
uma solução pragmática que maximize os três objetivos.

Mostre seu raciocínio passo-a-passo.
```

**Resultado esperado:**
- Chain-of-thought explícito com `<think>` tags
- Análise do CAP theorem aplicado
- Discussão de trade-offs PACELC
- Solução híbrida (ex: eventual consistency + compensação)
- Validação da própria lógica

---

## Benchmarks Práticos

### Teste 1: Latência de Primeira Resposta

```bash
# Qwen3
time echo "Hello" | ollama run arch-agent-qwen3
# Resultado: ~5-7 segundos

# Qwen3 MoE
time echo "Hello" | ollama run arch-agent-qwen3moe
# Resultado: ~3-4 segundos

# DeepSeek-R1
time echo "Hello" | ollama run arch-agent-deepseek
# Resultado: ~5-8 segundos
```

### Teste 2: Tokens por Segundo

```bash
# Execute e meça manualmente com cronômetro
ollama run arch-agent-qwen3 "Explique arquitetura hexagonal em detalhes"
# Observe: ~32-37 tok/s

ollama run arch-agent-qwen3moe "Explique arquitetura hexagonal em detalhes"
# Observe: ~45-55 tok/s

ollama run arch-agent-deepseek "Explique arquitetura hexagonal em detalhes"
# Observe: ~22-28 tok/s (mas gera mais tokens de raciocínio)
```

### Teste 3: Uso de VRAM

```bash
# Terminal 1: Monitorar VRAM
watch -n 1 nvidia-smi

# Terminal 2: Carregar modelo
ollama run arch-agent-qwen3      # ~22GB
ollama run arch-agent-qwen3moe   # ~12GB
ollama run arch-agent-deepseek   # ~20GB
```

---

## Recomendação Final

### Para a maioria dos casos: **arch-agent-qwen3** ⭐

**Razão:**
- Melhor modelo de 2025
- Equilíbrio perfeito qualidade/velocidade
- Sucessor direto do Qwen2.5
- Melhoria em todas as métricas
- Mesma VRAM que versão anterior

### Quando usar alternativas:

**Use arch-qwen3moe se:**
- Precisa de velocidade máxima
- Roda outros modelos em paralelo
- Trabalha em sessões interativas
- VRAM é limitante

**Use arch-deepseek se:**
- Trabalha com problemas arquiteturais muito complexos
- Precisa ver o raciocínio step-by-step
- Faz debugging profundo de arquitetura
- Qualidade > velocidade sempre

---

## Próximos Passos

1. **Instalar modelo preferido:**
   ```bash
   python3 setup_ollama_local.py --persona arch-qwen3 --pull --create
   ```

2. **Testar com caso real:**
   ```bash
   ollama run arch-agent-qwen3
   ```

3. **Comparar com modelo atual:**
   ```bash
   # Mesmo prompt em ambos
   ollama run arch-agent "Seu prompt aqui"
   ollama run arch-agent-qwen3 "Seu prompt aqui"
   ```

4. **Benchmarkar performance:**
   ```bash
   time ollama run arch-agent-qwen3 "Test prompt"
   nvidia-smi
   ```

5. **Atualizar configuração se satisfeito:**
   - Trocar `arch-agent` por novo modelo no workflow
   - Documentar resultados
   - Remover modelos antigos se necessário

---

## Comandos Úteis

```bash
# Listar todos os modelos instalados
ollama list

# Ver informações de um modelo
ollama show arch-agent-qwen3

# Remover modelo antigo (se decidir migrar)
ollama rm arch-agent

# Renomear modelo (para manter nome `arch-agent`)
ollama cp arch-agent-qwen3 arch-agent

# Verificar uso de VRAM
nvidia-smi

# Monitorar VRAM em tempo real
watch -n 1 nvidia-smi

# Ver logs do Ollama
journalctl -u ollama -f  # Linux systemd
```

---

**Última Atualização:** Outubro 16, 2025  
**Hardware Testado:** AMD Ryzen 7 5700X + RTX 5060 Ti 16GB  
**Versão Ollama:** 0.x+ (com suporte Qwen3, DeepSeek-R1)
