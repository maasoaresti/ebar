# Guia de Teste - EventPay MVP

## 🎯 Fluxos Completos Implementados

### 📱 FLUXO DO USUÁRIO COMPLETO

#### 1. Cadastro/Login
- ✅ Tela de login (`/auth/login`)
- ✅ Tela de registro (`/auth/register`)
- ✅ Validação de campos
- ✅ Autenticação JWT
- ✅ Persistência de sessão (AsyncStorage)

**Como testar:**
1. Abra o app
2. Clique em "Não tem conta? Cadastre-se"
3. Preencha os dados e cadastre
4. OU use usuário teste: `user@eventpay.com` / `user123`

#### 2. Visualizar Eventos
- ✅ Lista de eventos ativos (`/(tabs)/events`)
- ✅ Cards com imagem, nome, local e data
- ✅ Pull-to-refresh para atualizar
- ✅ Filtro por status (active)

**Como testar:**
1. Após login, você verá a aba "Eventos"
2. Eventos ativos aparecem automaticamente
3. Arraste para baixo para atualizar (pull-to-refresh)

#### 3. Ver Cardápio do Evento
- ✅ Detalhes do evento (`/event/[id]`)
- ✅ Informações completas (nome, descrição, local, data)
- ✅ Lista de produtos disponíveis
- ✅ Preço e estoque de cada produto
- ✅ Botão "Adicionar ao carrinho"

**Como testar:**
1. Na lista de eventos, toque em um evento
2. Veja os detalhes do evento
3. Role para ver o cardápio completo
4. Observe preços e disponibilidade

#### 4. Adicionar ao Carrinho
- ✅ Botão "+" em cada produto
- ✅ Notificação ao adicionar
- ✅ Badge no botão do carrinho mostrando quantidade
- ✅ Carrinho persiste enquanto navega

**Como testar:**
1. Na tela do evento, clique no botão "+" em um produto
2. Verá confirmação "Produto adicionado ao carrinho"
3. Botão "Ver Carrinho" aparece no rodapé com total

#### 5. Ver e Gerenciar Carrinho
- ✅ Modal do carrinho com todos os itens
- ✅ Aumentar/diminuir quantidade (+ e -)
- ✅ Remover item (ícone lixeira)
- ✅ Cálculo automático do subtotal
- ✅ Taxa de 10% mostrada separadamente
- ✅ Opção de usar créditos
- ✅ Total final calculado

**Como testar:**
1. Após adicionar produtos, clique em "Ver Carrinho"
2. Use os botões + e - para ajustar quantidades
3. Clique no ícone de lixeira para remover item
4. Observe os cálculos atualizando em tempo real

#### 6. Finalizar Compra (Checkout)
- ✅ Tela de checkout (`/checkout/[id]`)
- ✅ Resumo completo do pedido
- ✅ Discriminação de valores:
  - Subtotal dos produtos
  - Taxa da plataforma (10%)
  - Créditos usados (se aplicável)
  - Total a pagar
- ✅ Campo para usar créditos disponíveis
- ✅ Botão "Usar todos os créditos"
- ✅ Pagamento MOCKADO (simulado)

**Como testar:**
1. No carrinho, clique em "Finalizar Pedido"
2. Revise o resumo do pedido
3. (Opcional) Use créditos se tiver saldo
4. Clique em "Confirmar Pagamento"
5. Pedido será criado automaticamente como "pago"

#### 7. Receber QR Code
- ✅ QR Code único gerado automaticamente
- ✅ Tela de confirmação (`/order/[id]`)
- ✅ QR Code visível e escaneável
- ✅ Código alfanumérico exibido
- ✅ Status do pedido (Pendente/Validado)
- ✅ Detalhes completos do pedido
- ✅ Resumo financeiro

**Como testar:**
1. Após pagamento, você é direcionado para a tela do pedido
2. Veja o QR Code gerado
3. Observe o status "Pendente"
4. Role para ver todos os detalhes

#### 8. Histórico de Pedidos
- ✅ Lista de todos os pedidos (`/(tabs)/orders`)
- ✅ Status visual (cores)
- ✅ Data e hora da compra
- ✅ Valor total
- ✅ Nome do evento
- ✅ Botão para ver QR Code

**Como testar:**
1. Vá para a aba "Pedidos"
2. Veja todos os seus pedidos
3. Toque em um pedido para ver detalhes e QR Code

#### 9. Perfil e Créditos
- ✅ Visualização do perfil (`/(tabs)/profile`)
- ✅ Saldo de créditos destacado
- ✅ Informações da conta
- ✅ Botão de logout

**Como testar:**
1. Vá para a aba "Perfil"
2. Veja seu saldo de créditos
3. Revise suas informações

---

### 👨‍💼 FLUXO DO ADMIN COMPLETO

#### 1. Acesso Admin
- ✅ Tab "Admin" visível apenas para administradores
- ✅ Painel com 3 opções principais
- ✅ Controle de acesso baseado em role

**Como testar:**
1. Faça login como admin: `admin@eventpay.com` / `admin123`
2. Veja a aba "Admin" aparecer
3. Toque para ver o painel

#### 2. Criar Evento
- ✅ Painel Admin → "Gerenciar Eventos"
- ✅ Botão "+" (FAB) para criar
- ✅ Formulário completo:
  - Nome do evento *
  - Descrição *
  - Data e hora (formato ISO) *
  - Local *
- ✅ Validação de campos obrigatórios
- ✅ Botão "Criar Evento"

**Como testar:**
1. Admin → Gerenciar Eventos
2. Clique no botão "+" (canto inferior direito)
3. Preencha todos os campos:
   - Nome: "Meu Evento Teste"
   - Descrição: "Evento de teste"
   - Data: "2025-08-15T19:00:00"
   - Local: "Meu Local"
4. Clique em "Criar Evento"
5. Veja confirmação de sucesso

#### 3. Editar Evento
- ✅ Lista de eventos com botão de editar
- ✅ Formulário pré-preenchido
- ✅ Atualização em tempo real

**Como testar:**
1. Admin → Gerenciar Eventos
2. Clique no ícone de lápis em um evento
3. Modifique os campos
4. Clique em "Salvar"

#### 4. Adicionar Produtos ao Evento
- ✅ Botão "fast-food" em cada evento
- ✅ Tela de gerenciamento de produtos (`/admin/events/products/[id]`)
- ✅ Modal para criar/editar produto
- ✅ Formulário com:
  - Nome do produto *
  - Descrição *
  - Preço (R$) *
  - Estoque *
- ✅ Validação de campos

**Como testar:**
1. Admin → Gerenciar Eventos
2. Clique no ícone de "comida" (fast-food) em um evento
3. Clique no botão "+" para adicionar produto
4. Preencha:
   - Nome: "Água Mineral"
   - Descrição: "Água gelada 500ml"
   - Preço: "4.00"
   - Estoque: "100"
5. Clique em "Salvar"
6. Produto aparece na lista

#### 5. Editar/Deletar Produtos
- ✅ Lista de produtos do evento
- ✅ Botão de editar (lápis)
- ✅ Botão de deletar (lixeira)
- ✅ Confirmação antes de deletar

**Como testar:**
1. Na tela de produtos do evento
2. Clique no lápis para editar
3. Ou clique na lixeira para deletar
4. Confirme a ação

#### 6. Validar Pedidos com QR Code Scanner
- ✅ Admin → "Validar Pedidos"
- ✅ Scanner de QR Code (`/admin/scanner`)
- ✅ Permissão de câmera solicitada
- ✅ Frame de scan visual
- ✅ Leitura automática do QR
- ✅ Validação no backend
- ✅ Feedback visual e sonoro
- ✅ Prevenção de dupla validação

**Como testar:**
1. Admin → Validar Pedidos
2. Permita acesso à câmera
3. Aponte para um QR Code de pedido
4. Sistema valida automaticamente
5. Veja confirmação com detalhes do pedido
6. Tente escanear novamente (verá "já validado")

#### 7. Ver Relatórios
- ✅ Admin → "Relatórios"
- ✅ Cards com estatísticas:
  - Total de pedidos
  - Vendas totais
- ✅ Detalhamento financeiro:
  - Receita dos organizadores
  - Taxas da plataforma (10%)
- ✅ Informações sobre o sistema

**Como testar:**
1. Admin → Relatórios
2. Veja os números atualizados
3. Observe a separação clara de valores

#### 8. Visualizar Todos os Pedidos
- ✅ Acesso via API: GET `/api/admin/orders`
- ✅ Lista completa de pedidos de todos os usuários
- ✅ Filtros e controles disponíveis

**Como testar (via API):**
```bash
TOKEN=<seu_token_admin>
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/admin/orders
```

---

## ✅ Checklist de Validação Completa

### Fluxo do Usuário
- [ ] Cadastrar nova conta
- [ ] Fazer login
- [ ] Ver lista de eventos
- [ ] Abrir detalhes de um evento
- [ ] Ver cardápio completo
- [ ] Adicionar 3 produtos ao carrinho
- [ ] Abrir carrinho e ajustar quantidades
- [ ] Remover um item do carrinho
- [ ] Usar créditos (se disponível)
- [ ] Finalizar compra
- [ ] Ver QR Code gerado
- [ ] Acessar histórico de pedidos
- [ ] Ver detalhes de um pedido antigo
- [ ] Verificar saldo de créditos no perfil
- [ ] Fazer logout

### Fluxo do Admin
- [ ] Fazer login como admin
- [ ] Ver aba Admin disponível
- [ ] Criar novo evento
- [ ] Editar evento existente
- [ ] Adicionar 3 produtos a um evento
- [ ] Editar um produto
- [ ] Deletar um produto
- [ ] Abrir scanner de QR Code
- [ ] Escanear QR Code de um pedido
- [ ] Ver confirmação de validação
- [ ] Tentar escanear o mesmo QR novamente (deve avisar já validado)
- [ ] Ver relatórios financeiros
- [ ] Deletar um evento

---

## 🔍 Testes de Integração

### Teste Completo End-to-End
1. **Admin cria evento:**
   - Login como admin
   - Criar evento "Festa de Teste"
   - Adicionar 5 produtos variados

2. **Usuário compra:**
   - Login como usuário normal
   - Ver evento criado na lista
   - Adicionar 3 produtos ao carrinho
   - Finalizar compra
   - Receber QR Code

3. **Admin valida:**
   - Voltar para conta admin
   - Abrir scanner
   - Escanear QR Code do pedido
   - Ver confirmação

4. **Verificar status:**
   - Voltar para conta de usuário
   - Ver pedido como "Validado"
   - Status deve estar verde

---

## 🎨 Aspectos Visuais a Validar

- [ ] Interface em Português
- [ ] Cores consistentes (roxo #6200ee)
- [ ] Ícones apropriados (Ionicons)
- [ ] Loading states em todas as ações
- [ ] Mensagens de erro amigáveis
- [ ] Feedback visual para todas as ações
- [ ] Navegação intuitiva
- [ ] Botões com tamanho apropriado para mobile
- [ ] Campos de formulário responsivos ao teclado
- [ ] Pull-to-refresh funcional

---

## 🐛 Problemas Conhecidos e Limitações

1. **Pagamento MOCKADO:**
   - Todos os pagamentos são automaticamente aprovados
   - Não há integração real com Mercado Pago
   - Estrutura pronta para integração futura

2. **Imagens:**
   - Sistema preparado para base64
   - Não há upload de imagens implementado
   - Placeholders são mostrados

3. **Scanner QR Code:**
   - Requer permissão de câmera
   - Funciona melhor em dispositivo físico
   - No emulador pode não funcionar corretamente

4. **Notificações:**
   - Não há notificações push
   - Usuário precisa atualizar manualmente

---

## 📊 Métricas de Sucesso

- ✅ Cadastro de usuário funcional
- ✅ Login com JWT persistente
- ✅ Listagem de eventos dinâmica
- ✅ Carrinho de compras funcional
- ✅ Checkout com cálculos corretos (taxa 10%)
- ✅ QR Code único por pedido
- ✅ Sistema de créditos operacional
- ✅ CRUD completo de eventos (admin)
- ✅ CRUD completo de produtos (admin)
- ✅ Scanner QR Code funcional
- ✅ Validação de pedidos
- ✅ Relatórios financeiros
- ✅ Controle de estoque em tempo real
- ✅ Interface responsiva e intuitiva

---

## 🚀 Próximos Passos (Pós-MVP)

1. Integração real com Mercado Pago
2. Upload de imagens para eventos e produtos
3. Notificações push
4. Sistema de avaliações e comentários
5. Filtros e busca avançada
6. Conversão automática de saldo em créditos
7. Relatórios mais detalhados com gráficos
8. Suporte a múltiplos organizadores
9. Compartilhamento de eventos nas redes sociais
10. Modo offline básico
