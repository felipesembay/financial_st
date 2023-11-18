CREATE DATABASE financial;

USE financial;

CREATE TABLE users (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Data_Cadastramento DATETIME DEFAULT CURRENT_TIMESTAMP,
    Usuario VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Senha VARCHAR(255) NOT NULL,
    Data_Acesso DATETIME,
    Data_Logout DATETIME
);

CREATE TABLE receitas (
    ID_Receita INT AUTO_INCREMENT PRIMARY KEY,
    ID_Users INT NOT NULL,
    Valor DECIMAL(10,2) NOT NULL,
    Data DATE NOT NULL,
    Fonte VARCHAR(255) NOT NULL,
    Categoria VARCHAR(100),
    Descricao TEXT,
    Metodo_Pagamento VARCHAR(100),
    Frequencia VARCHAR(100),
    Banco_Corretora VARCHAR(255),
    FOREIGN KEY (ID_Users) REFERENCES users(ID)
);

CREATE TABLE despesas (
    ID_Despesa INT AUTO_INCREMENT PRIMARY KEY,
    ID_Users INT NOT NULL,
    Valor DECIMAL(10,2) NOT NULL,
    Data DATE NOT NULL,
    Fornecedor VARCHAR(255) NOT NULL,
    Categoria VARCHAR(100),
    Descricao TEXT,
    Metodo_Pagamento VARCHAR(100),
    Bandeira_cartao VARCHAR(50),
    Frequencia VARCHAR(100),
    Banco_Corretora VARCHAR(255),
    FOREIGN KEY (ID_Users) REFERENCES users(ID)
);

CREATE TABLE despesas (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    ID_Users INT,
    Despesas DECIMAL(10,2),
    Fornecedor_Fonte VARCHAR(255),
    Centro_Despesas VARCHAR(255),
    Data_Cadastramento_Despesas DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Users) REFERENCES users(ID)
);

CREATE TABLE investimentos (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    ID_Users INT,
    Investimentos DECIMAL(10,2),
    Fonte VARCHAR(255),
    Centro_Investimentos VARCHAR(255),
    Data_Cadastramento_Investimentos DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Users) REFERENCES users(ID)
);
