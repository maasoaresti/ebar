# EventPay - Plataforma de Vendas para Eventos

## 🎯 Sobre o Projeto

Plataforma mobile para compra antecipada de produtos em eventos, com sistema de QR Code para validação, taxa de plataforma automática e sistema de créditos.

## 👥 Usuários de Teste

### Administrador
- **Email:** admin@eventpay.com
- **Senha:** admin123
- **Créditos:** R$ 100,00

### Usuário Regular
- **Email:** user@eventpay.com
- **Senha:** user123
- **Créditos:** R$ 50,00

## 🎉 Evento de Demonstração

**Festival de Música 2025**
- Local: Parque Ibirapuera, São Paulo
- Data: 31/12/2025

### Produtos Disponíveis:
1. Cerveja Lata 350ml - R$ 8,00
2. Refrigerante 600ml - R$ 6,00
3. Hambúrguer Artesanal - R$ 25,00
4. Porção de Batata Frita - R$ 18,00
5. Água Mineral 500ml - R$ 4,00

## ✨ Funcionalidades Implementadas

### 👤 Usuário
- ✅ Cadastro e login com JWT
- ✅ Visualização de eventos ativos
- ✅ Card ápio digital por evento
- ✅ Carrinho de compras
- ✅ Checkout com cálculo automático da taxa (10%)
- ✅ Sistema de créditos (usar saldo em compras futuras)
- ✅ Geração automática de QR Code único por pedido
- ✅ Histórico de pedidos
- ✅ Visualização do perfil e créditos

### 🎯 Admin
- ✅ CRUD completo de eventos
- ✅ CRUD completo de produtos por evento
- ✅ Scanner de QR Code para validação de pedidos
- ✅ Relatórios financeiros (vendas, taxas, etc.)
- ✅ Visualização de todos os pedidos
- ✅ Controle de estoque em tempo real

### 💰 Sistema Financeiro
- ✅ Taxa de 10% calculada automaticamente
- ✅ Discriminação clara dos valores (subtotal + taxa - créditos)
- ✅ Sistema de créditos para eventos futuros
- ✅ Pagamento MOCKADO (pronto para integração com Mercado Pago)
- ✅ Relatórios separando valor do organizador vs taxa da plataforma

## 🔧 Tecnologias Utilizadas

### Backend
- FastAPI
- MongoDB (Motor - async driver)
- JWT Authentication
- Passlib + Bcrypt (hash de senhas)
- Pydantic (validação)

### Frontend
- React Native
- Expo Router (navegação file-based)
- React Context API (state management)
- AsyncStorage (persistência local)
- Expo Vector Icons
- react-native-qrcode-svg (geração de QR)
- expo-barcode-scanner (leitura de QR - admin)

## 📱 Estrutura de Navegação

```
/
├── auth/
│   ├── login
│   └── register
├── (tabs)/
│   ├── events (lista de eventos)
│   ├── orders (meus pedidos)
│   ├── profile (perfil e créditos)
│   └── admin (painel admin - apenas para admins)
├── event/[id] (detalhes do evento + cardápio)
├── checkout/[id] (finalização da compra)
├── order/[id] (detalhes do pedido com QR)
└── admin/
    ├── events (gerenciar eventos)
    ├── scanner (validar QR codes)
    └── reports (relatórios)
```

## 🚀 API Endpoints

### Autenticação
- `POST /api/auth/register` - Cadastro
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Perfil do usuário

### Eventos
- `GET /api/events` - Listar eventos
- `POST /api/events` - Criar evento (admin)
- `GET /api/events/{id}` - Detalhes do evento
- `PUT /api/events/{id}` - Atualizar evento (admin)
- `DELETE /api/events/{id}` - Deletar evento (admin)

### Produtos
- `GET /api/events/{event_id}/products` - Listar produtos
- `POST /api/events/{event_id}/products` - Criar produto (admin)
- `PUT /api/products/{id}` - Atualizar produto (admin)
- `DELETE /api/products/{id}` - Deletar produto (admin)

### Pedidos
- `POST /api/orders` - Criar pedido
- `GET /api/orders` - Meus pedidos
- `GET /api/orders/{id}` - Detalhes do pedido
- `POST /api/orders/validate-qr` - Validar QR code (admin)

### Créditos
- `GET /api/credits/balance` - Saldo de créditos
- `POST /api/credits/add` - Adicionar créditos

### Admin
- `GET /api/admin/orders` - Todos os pedidos (admin)
- `GET /api/admin/reports` - Relatórios (admin)

## 🎨 Características do Design

- Interface em Português
- Design mobile-first
- Componentes nativos React Native
- Tema roxo (#6200ee) como cor primária
- Ícones do Ionicons
- Cards com elevação e sombras
- Feedback visual para todas as ações
- Loading states apropriados
- Mensagens de erro amigáveis

## 📝 Próximos Passos (Melhorias Futuras)

1. **Integração Real de Pagamentos**
   - Mercado Pago (PIX, cartões)
   - Validação de pagamentos em tempo real

2. **Sistema de Créditos Avançado**
   - Conversão automática de saldo não utilizado ao fim do evento
   - Histórico de transações de créditos

3. **Notificações Push**
   - Confirmação de pedido
   - QR code validado
   - Novos eventos disponíveis

4. **Redes Sociais**
   - Login com Google/Facebook
   - Compartilhamento de eventos

5. **Analytics**
   - Dashboard admin mais completo
   - Gráficos de vendas
   - Relatórios exportáveis

6. **Imagens**
   - Upload de imagens para eventos
   - Upload de imagens para produtos
   - Galeria de fotos dos eventos

## 🔐 Segurança

- Senhas com hash bcrypt
- Tokens JWT com expiração
- Validação de inputs com Pydantic
- Controle de acesso baseado em roles
- CORS configurado
- QR Codes únicos e não reutilizáveis

## 📊 Modelo de Negócio

- Taxa de 10% sobre cada transação
- Discriminação clara nos relatórios
- Separação automática entre valor do organizador e taxa da plataforma
- Pagamento direto ao organizador (menos taxa)

---

**Status:** MVP Completo e Funcional ✅

**Última atualização:** 23/02/2026
