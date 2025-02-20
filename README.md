# 📖 Sistema de Gestão de Biblioteca

Este projeto é um sistema de gerenciamento de biblioteca que permite o controle de empréstimos de livros por administradores e estudantes. O código original foi atualizado e aprimorado para melhor segurança e funcionalidade.  

---

## 🚀 Funcionalidades  

### 🔹 Admin  
- Criar conta de administrador e fazer login.  
- Adicionar, visualizar e gerenciar livros.  
- Emitir livros cadastrados para estudantes registrados.  
- Acompanhar livros emitidos com data de emissão e data de devolução.  
- Calcular multas (R$10 por dia de atraso na devolução).  
- Gerenciar os estudantes cadastrados no sistema.  

### 🔹 Estudante  
- Criar conta e fazer login.  
- Visualizar os livros emitidos, incluindo data de expiração e multa (se houver atraso na devolução).  

---

## 🛠 Como Executar este Projeto  

1. **Instale o Python (3.7.6 ou superior)**  
   > *Não se esqueça de marcar a opção “Adicionar ao PATH” durante a instalação.*  
2. **Abra o terminal e instale as dependências:**  

   ```sh
   python -m pip install -r requirements.txt
   ```

3. **Baixe e extraia o repositório:**  
   - Clone o repositório ou faça o download do ZIP.  
   - Navegue até a pasta do projeto no terminal.  

4. **Execute as migrações do banco de dados:**  

   ```sh
   py manage.py makemigrations
   py manage.py migrate
   ```

5. **Inicie o servidor:**  

   ```sh
   py manage.py runserver
   ```

6. **Abra o navegador e acesse:**  

   ```
   http://127.0.0.1:8000/
   ```

---

## ✉ Configuração do Contato  

Para que a página **"Fale Conosco"** funcione corretamente, configure seu e-mail no arquivo `settings.py`:  

```python
EMAIL_HOST_USER = 'seuemail@gmail.com'
EMAIL_HOST_PASSWORD = 'sua senha de e-mail'
EMAIL_RECEIVING_USER = 'seuemail@gmail.com'
```

---

## 🔄 Melhorias e Atualizações  

- 🔐 **Segurança aprimorada:** O sistema agora protege melhor o acesso ao painel administrativo.  
- ⚡ **Correções de bugs:** Diversas falhas foram corrigidas para maior estabilidade.  
- 📚 **Interface aprimorada:** Layout atualizado para facilitar a usabilidade.  
- 🔍 **Melhor controle de permissões:** Apenas usuários autorizados podem acessar funções administrativas.  

---

## ⚠ Problemas Corrigidos  
 
✅ **Correção no cálculo de multas:** O sistema agora calcula corretamente a multa por atraso.  
✅ **Melhorias no login:** Implementação de validação extra para evitar acessos indevidos.  

---

## 💡 Agradecimentos ao Sumit Kumar (Desenvolvedor do projeto original) 
Aqui está o link para o repositório do projeto inspecionado e refatorado: https://github.com/sumitkumar1503/librarymanagement 
```
