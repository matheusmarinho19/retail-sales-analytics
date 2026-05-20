-- Modelo Estrela (Star Schema) + Índices de Performance
-- ==================================================

CREATE TABLE IF NOT EXISTS dim_local (
    pk_id_local INT PRIMARY KEY,
    cidade VARCHAR(100),
    estado VARCHAR(50),
    regiao VARCHAR(50),
    pais VARCHAR(50)
);

CREATE INDEX idx_dim_local_estado ON dim_local(estado);
CREATE INDEX idx_dim_local_cidade ON dim_local(cidade);

CREATE TABLE IF NOT EXISTS dim_produto (
    pk_id_produto INT PRIMARY KEY,
    id_produto_original VARCHAR(50),
    nome_produto VARCHAR(200),
    categoria VARCHAR(50),
    sub_categoria VARCHAR(50)
);

CREATE INDEX idx_dim_produto_categoria ON dim_produto(categoria, sub_categoria);
CREATE INDEX idx_dim_produto_nome ON dim_produto(nome_produto);

CREATE TABLE IF NOT EXISTS dim_data (
    pk_id_data INT PRIMARY KEY,
    data_pedido DATE,
    ano INT,
    mes INT,
    mes_nome VARCHAR(20)
);

CREATE INDEX idx_dim_data_ano_mes ON dim_data(ano, mes);
CREATE INDEX idx_dim_data_data_pedido ON dim_data(data_pedido);

CREATE TABLE IF NOT EXISTS dim_cliente (
    id_cliente VARCHAR(50) PRIMARY KEY,
    nome_cliente VARCHAR(100),
    segmento VARCHAR(50),
    fk_id_local INT,
    FOREIGN KEY (fk_id_local) REFERENCES dim_local(pk_id_local)
);

CREATE INDEX idx_dim_cliente_segmento ON dim_cliente(segmento);
CREATE INDEX idx_dim_cliente_local ON dim_cliente(fk_id_local);

CREATE TABLE IF NOT EXISTS fato_vendas (
    id_pedido VARCHAR(50),
    fk_id_produto INT,
    id_cliente VARCHAR(50),
    fk_id_data INT,
    vendas DECIMAL(10,2),
    quantidade INT,
    lucro DECIMAL(10,2),
    PRIMARY KEY (id_pedido, fk_id_produto),
    FOREIGN KEY (id_cliente) REFERENCES dim_cliente(id_cliente),
    FOREIGN KEY (fk_id_produto) REFERENCES dim_produto(pk_id_produto),
    FOREIGN KEY (fk_id_data) REFERENCES dim_data(pk_id_data)
);

-- Índices na tabela fato para otimizar JOINs e filtros analíticos
CREATE INDEX idx_fato_vendas_cliente ON fato_vendas(id_cliente);
CREATE INDEX idx_fato_vendas_produto ON fato_vendas(fk_id_produto);
CREATE INDEX idx_fato_vendas_data ON fato_vendas(fk_id_data);
-- Índice composto para consultas frequentes por período + produto
CREATE INDEX idx_fato_vendas_periodo_produto ON fato_vendas(fk_id_data, fk_id_produto);
