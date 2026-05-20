Views Analíticas para BI / Dashboards / Relatórios
-- ==================================================

-- 1️⃣ View detalhada: junção completa de fato + todas as dimensões
CREATE OR REPLACE VIEW v_vendas_detalhada AS
SELECT
    f.id_pedido,
    f.vendas,
    f.quantidade,
    f.lucro,
    c.nome_cliente,
    c.segmento,
    l.cidade,
    l.estado,
    l.regiao,
    l.pais,
    p.nome_produto,
    p.categoria,
    p.sub_categoria,
    d.data_pedido,
    d.ano,
    d.mes,
    d.mes_nome
FROM fato_vendas f
LEFT JOIN dim_cliente c ON f.id_cliente = c.id_cliente
LEFT JOIN dim_local l ON c.fk_id_local = l.pk_id_local
LEFT JOIN dim_produto p ON f.fk_id_produto = p.pk_id_produto
LEFT JOIN dim_data d ON f.fk_id_data = d.pk_id_data;

-- 2️⃣ View temporal: faturamento e volume por ano/mês
CREATE OR REPLACE VIEW v_vendas_por_periodo AS
SELECT
    d.ano,
    d.mes,
    d.mes_nome,
    COUNT(DISTINCT f.id_pedido) AS total_pedidos,
    SUM(f.quantidade) AS total_itens_vendidos,
    SUM(f.vendas) AS faturamento_total,
    SUM(f.lucro) AS lucro_total
FROM fato_vendas f
JOIN dim_data d ON f.fk_id_data = d.pk_id_data
GROUP BY d.ano, d.mes, d.mes_nome
ORDER BY d.ano, d.mes;

-- 3️⃣ View de produto: performance por categoria/subcategoria
CREATE OR REPLACE VIEW v_vendas_por_categoria AS
SELECT
    p.categoria,
    p.sub_categoria,
    COUNT(DISTINCT f.id_pedido) AS total_pedidos,
    SUM(f.quantidade) AS total_itens_vendidos,
    SUM(f.vendas) AS faturamento_total,
    SUM(f.lucro) AS lucro_total
FROM fato_vendas f
JOIN dim_produto p ON f.fk_id_produto = p.pk_id_produto
GROUP BY p.categoria, p.sub_categoria
ORDER BY faturamento_total DESC;

-- 4️⃣ View geográfica: vendas por região/estado/cidade
CREATE OR REPLACE VIEW v_vendas_por_regiao AS
SELECT
    l.pais,
    l.regiao,
    l.estado,
    l.cidade,
    COUNT(DISTINCT f.id_pedido) AS total_pedidos,
    SUM(f.quantidade) AS total_itens_vendidos,
    SUM(f.vendas) AS faturamento_total,
    SUM(f.lucro) AS lucro_total
FROM fato_vendas f
JOIN dim_cliente c ON f.id_cliente = c.id_cliente
JOIN dim_local l ON c.fk_id_local = l.pk_id_local
GROUP BY l.pais, l.regiao, l.estado, l.cidade
ORDER BY faturamento_total DESC;

-- 5️⃣ View de cliente: métricas de performance por comprador
CREATE OR REPLACE VIEW v_performance_cliente AS
SELECT
    c.id_cliente,
    c.nome_cliente,
    c.segmento,
    l.estado,
    COUNT(DISTINCT f.id_pedido) AS qtd_pedidos,
    SUM(f.vendas) AS faturamento_total,
    SUM(f.lucro) AS lucro_total,
    ROUND(AVG(f.vendas), 2) AS ticket_medio
FROM fato_vendas f
JOIN dim_cliente c ON f.id_cliente = c.id_cliente
JOIN dim_local l ON c.fk_id_local = l.pk_id_local
GROUP BY c.id_cliente, c.nome_cliente, c.segmento, l.estado
ORDER BY faturamento_total DESC;
