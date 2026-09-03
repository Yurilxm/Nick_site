# Nick_site

## Visão Geral

O **Nick_site** é uma loja virtual completa desenvolvida para oferecer uma experiência de compra simples e segura para os clientes.

A plataforma permite:

* Navegar por um catálogo de produtos organizados em categorias.
* Adicionar itens a um carrinho interativo.
* Escolher entre receber o pedido em casa ou retirar no local.
* Realizar pagamentos com confirmação instantânea.
* Fazer login por código enviado por e-mail.
* Acompanhar detalhadamente o status dos pedidos.

## Tecnologias

* **Linguagem:** Python
* **Framework Web:** Django
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Remix Icon e Bootstrap Icons
* **Integrações de serviços:**

  * **Mercado Pago:** processamento de pagamentos, Pix e Webhooks com assinatura de segurança.
  * **Melhor Envio:** cálculo de frete e prazos de entrega.
* **Geração de documentos:** biblioteca para renderização de comprovantes em PDF.

## Funcionalidades

### Autenticação e Gestão de Usuários (`app`)

* Cadastro de novos usuários com verificação de e-mail por link/token seguro.
* Autenticação via senha ou código de acesso temporário enviado por e-mail.
* Fluxo de recuperação e redefinição de senha.
* Gerenciamento completo do perfil, incluindo:

  * Dados pessoais.
  * CPF.
  * Telefone.
  * Endereço.

### Catálogo de Produtos (`produtos`)

* Listagem geral de produtos.
* Filtragem por categorias.
* Página detalhada do produto.
* Controle de disponibilidade.
* Validação de upload de imagens, permitindo apenas:

  * JPG
  * JPEG
  * PNG
  * WEBP

### Carrinho de Compras e Checkout (`carrinho`)

* Carrinho lateral interativo via AJAX.
* Página dedicada para visualização do carrinho.
* Adição, remoção e alteração da quantidade de itens.
* Migração e associação automática do carrinho anônimo à conta do usuário após o login.
* Suporte a duas modalidades de entrega:

  * Cálculo de frete em tempo real via Melhor Envio.
  * Retirada presencial na loja.
* Validação dinâmica dos dados de envio e contato durante o checkout.

### Pedidos e Pagamentos (`pedidos`)

* Integração com o gateway de pagamentos Mercado Pago.
* Suporte a pagamentos via Pix.
* Cálculo de parcelamento.
* Controle de expiração de pagamentos.
* Validações de segurança e antifraude.
* Processamento automatizado de notificações de pagamento via Webhooks.
* Validação do segredo `MERCADO_PAGO_WEBHOOK_SECRET`.
* Painel **Meus Pedidos** para histórico e acompanhamento dos pedidos.
* Emissão e download de comprovantes de compra em formato PDF.

### Notificações e Comunicação

* Envio de e-mails transacionais para:

  * Boas-vindas.
  * Verificação de conta.
  * Código de acesso.
  * Recuperação de senha.
  * Confirmação de pedidos.
* Páginas institucionais informativas.

## Segurança

O projeto possui diversas medidas de segurança, incluindo:

* Proteção **CSRF** em todos os formulários.
* **SRI (Subresource Integrity)** para recursos externos carregados via CDN.
* Escape de variáveis em JavaScript para prevenção de **XSS**.
* Tratamento de erros sem exposição de informações internas.
* Restrição de tipos de arquivos de imagem.
* Validação de e-mail em formulários de marketing.

## Estrutura do Projeto

```text
Nick_site/
├── app/
│   └── Núcleo da aplicação, autenticação, perfil, tokens e páginas institucionais
├── produtos/
│   └── Catálogo, produtos, categorias e detalhes
├── carrinho/
│   └── Carrinho, cálculo de frete, checkout e retirada
├── pedidos/
│   └── Pedidos, pagamentos, webhooks, PDF e histórico
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

### Principais Aplicações

* **`app/`** — Núcleo da aplicação, autenticação, perfil, tokens e páginas institucionais.
* **`produtos/`** — Catálogo, modelos de produtos, categorias e detalhes.
* **`carrinho/`** — Carrinho, cálculo de frete, checkout e retirada.
* **`pedidos/`** — Pedidos, pagamentos, Webhooks, geração de PDF e histórico.

## Instalação

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd Nick_site
```

### 2. Crie e ative um ambiente virtual

#### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

No Windows, caso o comando `cp` não esteja disponível, copie o arquivo manualmente ou utilize:

```powershell
Copy-Item .env.example .env
```

Depois, preencha as variáveis necessárias no arquivo `.env`.

### 5. Execute as migrações

```bash
python manage.py migrate
```

### 6. Crie um superusuário

```bash
python manage.py createsuperuser
```

## Configuração

As principais variáveis de ambiente utilizadas pelo projeto estão listadas abaixo. Consulte o arquivo `.env.example` para a configuração completa.

| Variável                      | Descrição                                                    |
| ----------------------------- | ------------------------------------------------------------ |
| `SECRET_KEY`                  | Chave secreta do Django                                      |
| `ALLOWED_HOSTS`               | Hosts autorizados                                            |
| `CSRF_TRUSTED_ORIGINS`        | Origens confiáveis para CSRF                                 |
| `DB_NAME`                     | Nome do banco de dados                                       |
| `DB_USER`                     | Usuário do banco de dados                                    |
| `DB_PASSWORD`                 | Senha do banco de dados                                      |
| `DB_HOST`                     | Host do banco de dados                                       |
| `DB_PORT`                     | Porta do banco de dados                                      |
| `MERCADO_PAGO_ACCESS_TOKEN`   | Token de acesso do Mercado Pago                              |
| `MERCADO_PAGO_PUBLIC_KEY`     | Chave pública do Mercado Pago                                |
| `MERCADO_PAGO_WEBHOOK_SECRET` | Segredo utilizado para validar Webhooks                      |
| `MELHOR_ENVIO_TOKEN`          | Token de acesso do Melhor Envio                              |
| `EMAIL_HOST`                  | Servidor SMTP                                                |
| `EMAIL_PORT`                  | Porta do servidor SMTP                                       |
| `EMAIL_USE_TLS`               | Define se o TLS será utilizado                               |
| `EMAIL_HOST_USER`             | Usuário do servidor SMTP                                     |
| `EMAIL_HOST_PASSWORD`         | Senha do servidor SMTP                                       |
| `CLOUDINARY_CLOUD_NAME`       | Nome da conta Cloudinary                                     |
| `CLOUDINARY_API_KEY`          | Chave da API do Cloudinary                                   |
| `CLOUDINARY_API_SECRET`       | Segredo da API do Cloudinary                                 |
| `LOJA_*`                      | Configurações relacionadas ao endereço da loja para retirada |

> **Importante:** nunca versionar o arquivo `.env` ou expor tokens, senhas e chaves de API no repositório.

## Uso

### 1. Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

### 2. Acesse a aplicação

* **Loja:** `http://localhost:8000/`
* **Painel administrativo:** `http://localhost:8000/admin/`

## Testes

O projeto possui suítes de testes cobrindo funcionalidades de:

* Autenticação.
* Produtos.
* Carrinho.
* Pedidos.
* Pagamentos.
* Segurança.

### Executar todos os testes

```bash
python manage.py test
```

### Executar testes de uma aplicação específica

```bash
python manage.py test app
python manage.py test carrinho
```