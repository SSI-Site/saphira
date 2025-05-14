# Saphira API

Bem-vindo ao projeto **Saphira API**, uma API desenvolvida com Django Rest Framework para gerenciar estudantes, palestras, presenças e tokens (e em breve brindes) em um único sistema. A API fornece endpoints para administração e autenticação, bem como para o gerenciamento de dados de estudantes durante a Semana de Sistemas de Informação.

## Índice

- [Recursos](#recursos)
- [Requisitos](#requisitos)
- [Configuração](#configuração)
- [Uso](#uso)
- [Endpoints](#endpoints)
- [AWS](#aws)
- [Testes](#testes)

## Recursos

A API Saphira oferece os seguintes recursos:

- **Autenticação**: Login e logout para administradores, login para estudantes.
- **Gerenciamento de Estudantes**: Criação, recuperação, atualização e exclusão de estudantes.
- **Gerenciamento de Presenças**: Registro e recuperação de presenças de estudantes em palestras.
- **Gerenciamento de Palestras**: Criação, recuperação, atualização e exclusão de palestras.
- **Gerenciamento de Tokens**: Criação e listagem de tokens para presenças.
<!-- - **Gerenciamento de Brindes**: Criação, recuperação, atualização e exclusão de brindes. -->

## Requisitos

- Python 3.8+
- Django 4.0+
- Django Rest Framework 3.14+
- Django Rest Framework Simple JWT 5.2+
- Firebase Admin SDK
- PostgreSQL (ou outro banco de dados compatível)

## Configuração

1. **Clone o repositório**:

    ```bash
    git clone https://github.com/SSI-Site/Saphira.git
    cd saphira/src
    ```

2. **Crie um ambiente virtual e ative-o**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```

3. **Instale as dependências**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure o banco de dados**:
- Ajuste as configurações do banco de dados em `settings.py`.

5. **Configure as variáveis de ambiente**:
- Defina as variáveis de ambiente para o Firebase e outras configurações no arquivo `.env`.

6. **Aplique as migrações**:

    ```bash
    python3 manage.py migrate
    ```

7. **Crie um superusuário**:

    ```bash
    python3 manage.py createsuperuser
    ```

8. **Inicie o servidor**:

    ```bash
    python3 manage.py runserver
    ```

## Uso
A API pode ser acessada localmente em `http://localhost:8000/`. Utilize ferramentas como Postman, Insomnia ou cURL para interagir com os endpoints.

### Exemplos de Requisições
**Login do Administrador**:

    ```http
    POST /admin/login
    Content-Type: application/json

    {
      "username": "admin",
      "password": "password123"
    }
    ```
**Login do Estudante**:

    ```http
    POST /student/login
    Content-Type: application/json
    Authorization: Bearer <firebase_token>

    {
      "name": "Alexandre Kira",
      "email": "mesmo.email.firebase@example.com"
    }
    ```

**Criar Presença de Estudante**:

    ```http
    POST /student/{student_id}/presence
    Content-Type: application/json
    Authorization: Bearer <access_token>

    {
      "token_code": "TOKEN1"
    }
    ```

## Endpoints

### Públicos

- `GET /`: Página inicial da API.


- `POST /api/token/refresh`
  - **Descrição**: Atualiza o token JWT de acesso usando um token de refresh válido.
  - **Corpo da Requisição:**
    ```json
    {
      "refresh": "tokenJWTdeRefresh"
    }
    ```

### Estudantes

- `POST /student/login`
  - **Descrição**: Login de estudante.
  - **Cabeçalho**:
    ```
    Authorization: Bearer <firebase_token>
    ```
  - **Corpo da Requisição**:
    ```json
    {
      "name": "Alexandre Kira",
      "email": "mesmo.email.firebase@example.com"
    }
    ```

- `GET /student/{student_id}`
  - **Descrição**: Recupera as informações de um estudante.
  - **Cabeçalho**:
    ```
    Authorization: Bearer <access_token>
    ```

- `PUT /student/{student_id}`
  - **Descrição**: Atualiza as informações de um estudante.
  - **Cabeçalho**:
    ```
    Authorization: Bearer <access_token>
    ```

- `POST /student/{student_id}/presence`
  - **Descrição**: Registra a presença de um estudante em uma palestra.
  - **Cabeçalho**:
    ```
    Authorization: Bearer <access_token>
    ```
  - **Corpo da Requisição**:
    ```json
    {
      "token_code": "TOKEN1"
    }
    ```

- `GET /student/{student_id}/presences`
  - **Cabeçalho**:
    ```
    Authorization: Bearer <access_token>
    ```
  - **Descrição**: Recupera as presenças de um estudante.

### Administradores

- `POST /admin/login`
  - **Descrição**: Login de administrador.
  - **Corpo da Requisição**:
    ```json
    {
      "username": "admin",
      "password": "password123"
    }
    ```

- `POST /admin/logout`
  - **Descrição**: Logout de administrador.

- `GET /admin`
  - **Descrição**: Página inicial para administradores.

- `GET /admin/students`
  - **Descrição**: Lista todos os estudantes.

- `GET /admin/students/search/{name}`
  - **Descrição**: Busca estudantes pelo nome.

- `GET /admin/student/{student_document}`
  - **Descrição**: Recupera informações de um estudante pelo documento.

- `DELETE /admin/students/{student_document}`
  - **Descrição**: Remove um estudante pelo documento.

- `POST /admin/tokens`
  - **Descrição**: Cria um novo token.

- `GET /admin/presences`
  - **Descrição**: Lista todas as presenças.

- `DELETE /admin/presence/{talk_id}/{student_document}`
  - **Descrição**: Remove uma presença específica.

## AWS
Para a operação e gerenciamento do banco de dados, será utilizado o `AWS` (Amazon Web Services). AWS é uma plataforma de serviços de computação em nuvem oferecida pela Amazon, fornecendo serviços em diferentes áreas, como computação, armazenamento, redes e segurança. Para tanto, serão utilizados dois principais serviços:
-  [RDS](#RDS)
-  [EC2](#EC2)

### RDS

O **RDS** (Relational Database Service) permite o **gerenciamento de banco de dados relacionais**.

Nele será criado um banco de dados PostgreSQL. E após a sua criação (nome, tamanho, master username, etc.), será necessário configurar o seu acesso. Para isso:
* Guarde as informações importantes, como o endpoint e a porta do banco de dados,
* Configure o Grupo de Segurança, verificando se permite conexões com o Django: adicione o IP público do EC2 e regras de entrada que permitem conexões TCP para a porta `5432` (porta padrão).

> [!NOTE]
>  Ex:
>
>  Na seção de regras de entrada (Inbound Rules) do grupo de segurança, adicione uma nova regra:
>
> - Tipo: `PostgreSQL` (ou Custom TCP Rule, se você não encontrar o tipo).
> - Protocolo: `TCP`.
> - Porta: `5432` (ou a porta que você configurou para o PostgreSQL).
> - Origem: `IP público da instância EC2` ou `Grupo de Segurança da EC2`

Além disso, instale o pacote `psycopg2` (ou psycopg2-binary em casos de erro), pois permitirá que o Django possa se conectar ao PostgreSQL.
```sh
pip install psycopg2
```
```sh
pip install psycopg2-binary
```

Por fim, configure o Django para se conectar com o banco de dados. Por padrão, os projetos do Django utilizam o banco de dados **SQLite**, portanto, primeiramente, será necessário mudar as configuração presentes no arquivo `settings.py`, substituindo as configurações do banco SQLite pelo PostgreSQL.
```bash
DATABASES = {
'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'nome',  # O nome do banco de dados
    'USER': 'admin',  # O usuário master
    'PASSWORD': 'senha',  # A senha
    'HOST': 'endpoint',  # O endpoint do RDS
    'PORT': '5432',  # A porta padrão do PostgreSQL
  }
}
```
Depois disso, execute as migrações para criar os modelos no banco de dados, e verifique se o Django conseguiu se conectar corretamente a ele.
```bash
python manage.py migrate
```

### EC2

Com o banco de dados funcionando, podemos agora rodar o saphira no EC2.

O **EC2** (Elastic Compute Cloud) é um **servidor virtual** na nuvem da AWS, que atua como um **computador remoto**. Então ao criar uma instância EC2, estaremos basicamente alugando um servidor na AWS, e é nesse servidor que o Saphira rodará e ficará acessível na internet.

Dito isso, o primeiro passo é criar uma instância EC2 no AWS.
- Siga os passos para sua criação
- Guarde o **Key Pair** (par de chaves) e o arquivo `.pem` gerado, pois permitirá que você acesse a instância via SSH.
- Certifique-se de que sua instância EC2 está na mesma **VPC (Virtual Private Cloud)** que o RDS.
- Confira o Security Group:
    - Permitir tráfego SSH e TCP nas regras de entrada.
    - Verificar se a instância EC2 pode acessar a porta do PostgreSQL (`5432`) no RDS.

Com o EC2 criado, o segundo passo é se conectar a ele. Para isso, siga os passos de conexão via `SSH` fornecidos no próprio AWS

Se tudo der certo, agora você estará operando no computador remoto.

Então o próximo passo será configurar esse ambiente na linha de comando do servidor EC2. Como fornecido em [Configuração](#Configuração):

- Baixe as dependências, como o python, o pip e o venv;
- Ative o venv
- Clone o repositório do Git
- Instale os requerimentos e o `psycopg2`

Por fim, vale a pena verificar as configurações do Django presentes no EC2, especialmente no arquivo `settings.py` que deve ter as informações corretas sobre o banco de dados RDS.

Rode o Saphira com o comando:

```bash
python manage.py runserver 0.0.0.0:8000
```

Agora, a aplicação estará acessível na internet através do IP público da instância EC2 na porta 8000.


### Load Balancer

O **Load Balancer** distribui o tráfego de entrada em várias instâncias do EC2 para equilibrar a demanda, garantindo uma melhor disponibilidade da aplicação. No entanto, será utilizado principalmente para testar as requisições HTTPS

A criação do load balancer pode ser encontrada na própria interface do EC2.

- Em **"Create Load Balancer"**, será escolhido o **Application Load Balancer (ALB}** como o tipo de Load Balancer
- Escolha um nome, um Scheme, algumas Subnets, e o mesmo VPC onde o EC2 e o RDS estão
- Configure o Security Group para permitir o tráfego HTTP e HTTPS
- Crie um Certificado SSL/TLS no serviço **AWS Certificate Manager (ACM)**
- Adicione um **Listener** para HTTPS e associe o certificado SSL.
- Crie um Target Group:
    - Tipo: `Instances`.
    - Protocolo: `HTTP`.
    - Porta: `8000` (porta onde a aplicação Django está rodando no EC2).
- Adicione e associe o Target Group
    - Selecione as instâncias EC2 que devem receber tráfego do Load Balancer e registre-os.
    - No painel de configuração do Load Balancer, na seção de **Listeners**, adicione uma regra que encaminha todas as requisições para o Target Group em **"View/Edit rules" do HTTPS**


Agora é possível testar as requisições HTTPS. Basta obter o DNS público do Load Balancer e abrí-lo no navegador com  `https://` . Se tudo estiver configurado corretamente, a aplicação Django estará rodando via HTTPS.
> [!NOTE]
> Certifique-se de que o Django está configurado corretamente para usar HTTPS. No arquivo `settings.py`, adicione, se não tiver:
> ```python
> SECURE_SSL_REDIRECT = True  # Redireciona todas as requisições HTTP para HTTPS
> CSRF_COOKIE_SECURE = True   # Utiliza cookies para CSRF
> ```
=======

## Testes

Os testes em Django são realizados por meio da classe *TestCase*, importada do *django.test* que permite a realização de testes em ambiente isolado.

- **Executar todos os testes**:

  ```bash
  uv run src/manage.py test tests
  ```

- **Executar teste específico**:
  ```bash
  uv run src/manage.py test tests.[nome_do_teste]
  ```

- **Estrutura do Teste**:
  - `setUP`
    - **Descrição**: Usado para inicializar objetos, criar dados de teste ou qualquer outra preparação necessária.

  -`Assertions`
    - **Descrição**: Classe de *TesteCase* que oferece métodos usados para verificar se as saídas e estados do código são os esperados
    - **Exemplos de Assertions**:
      - `assertEqual`
      - `assertTrue`
      - `assertFalse`


### Administrador

- `AdminLoginViewTest`
  - **Descrição**: Testa url de AdminLoginView

  - `test_login_admin_success`
    - **Descrição**: Verifica se login foi bem-sucedido

  - `test_login_admin_failure`
    - **Descrição**: Verifica se login falhou
