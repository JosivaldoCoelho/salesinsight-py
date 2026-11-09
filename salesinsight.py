import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

def gerar_dataset_vendas(n_registros=200, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor", "Teclado", "Mouse", "Headset"]
    categorias = {"Notebook": "Computadores", "Smartphone": "Celulares",
                  "Tablet": "Celulares", "Monitor": "Computadores",
                  "Teclado": "Perifericos", "Mouse": "Perifericos",
                  "Headset": "Perifericos"}
    precos = {"Notebook": 3500, "Smartphone": 2200, "Tablet": 1800,
              "Monitor": 1200, "Teclado": 250, "Mouse": 120, "Headset": 350}
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
    data_inicio = datetime(2025, 1, 1)

    dados = []
    for i in range(n_registros):
        produto = random.choice(produtos)
        categoria = categorias[produto]
        quantidade = random.randint(1, 10)
        preco = round(precos[produto] * random.uniform(0.85, 1.15), 2)
        data = data_inicio + timedelta(days=random.randint(0, 364))
        data_txt = data.strftime("%Y-%m-%d")
        cliente = f"Cliente_{random.randint(1, 50):03d}"

        if random.random() < 0.03:
            data_txt = "DATA INVALIDA"

        dados.append({
            "id_venda": i + 1,
            "data_venda": data_txt,
            "cliente": cliente,
            "produto": produto,
            "categoria": categoria,
            "regiao": random.choice(regioes),
            "quantidade": quantidade,
            "preco_unitario": preco,
        })
    return pd.DataFrame(dados)

def processar_coluna(df, coluna, funcao_transformacao, nome_saida=None):
    nome_saida = nome_saida or f"{coluna}_transformado"
    df[nome_saida] = df[coluna].apply(funcao_transformacao)
    return df

class AnalisadorDeVendas:
    def __init__(self):
        self.df_bruto = None
        self.df_limpo = None
        self.metricas = {}
        self.clientes = None
        sns.set_theme(style="whitegrid", palette="muted")

    def carregar(self, caminho="vendas.csv"):
        self.df_bruto = pd.read_csv(caminho)
        return self.df_bruto

    def inspecionar_dados(self):
        print("\n=== INSPEÇÃO INICIAL DO DATASET ===")
        print(f"Shape: {self.df_bruto.shape}")
        print(f"\nColunas: {list(self.df_bruto.columns)}")
        print(f"\nTipos de dados:\n{self.df_bruto.dtypes}")
        print(f"\nValores nulos por coluna:\n{self.df_bruto.isnull().sum()}")
        print(f"\nPrimeiros registros:\n{self.df_bruto.head()}")

    def transformar(self):
        df = self.df_bruto.copy()
        total_inicial = len(df)

        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
        invalid_dates = df["data_venda"].isnull().sum()
        df = df.dropna(subset=["data_venda"])

        df["quantidade"] = df["quantidade"].astype(int)
        df["preco_unitario"] = df["preco_unitario"].astype(float)

        total_final = len(df)

        print("\n=== RELATÓRIO DE LIMPEZA ===")
        print(f"Registros iniciais: {total_inicial}")
        print(f"Datas inválidas removidas: {invalid_dates}")
        print(f"Registros finais (pós-limpeza): {total_final}")

        df["receita_total"] = df["quantidade"] * df["preco_unitario"]
        df["mes"] = df["data_venda"].dt.month

        meses_pt = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
                    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        df["mes_nome"] = df["mes"].map(meses_pt)
        df["trimestre"] = "Q" + df["data_venda"].dt.quarter.astype(str)
        df["ano"] = df["data_venda"].dt.year

        condicoes = [
            df["receita_total"] < 500,
            (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
            df["receita_total"] >= 5000
        ]
        faixas = ["Baixo Valor", "Medio Valor", "Alto Valor"]
        df["faixa_receita_item"] = np.select(condicoes, faixas, default="Nao Classificado")

        df = processar_coluna(df, "receita_total", lambda x: round(x / 1000, 2), nome_saida="receita_em_milhares")

        self.df_limpo = df

    def analisar(self):
        df = self.df_limpo

        por_mes = df.groupby("mes").agg(
            receita_total=("receita_total", "sum"),
            quantidade=("quantidade", "sum"),
            n_vendas=("id_venda", "count")
        ).reset_index()

        top_produtos = df.groupby("produto")["receita_total"].sum().reset_index().sort_values(by="receita_total", ascending=False).head(5)
        por_categoria = df.groupby("categoria")["receita_total"].sum().reset_index()
        por_regiao = df.groupby("regiao").agg(
            receita_total=("receita_total", "sum"),
            ticket_medio=("receita_total", "mean")
        ).reset_index()

        self.metricas = {
            "por_mes": por_mes,
            "top_produtos": top_produtos,
            "por_categoria": por_categoria,
            "por_regiao": por_regiao
        }

        print("\n=== MÉTRICAS AGREGADAS ===")
        print("\n--- POR MÊS ---")
        print(por_mes)
        print("\n--- TOP PRODUTOS ---")
        print(top_produtos)

        gasto_clientes = df.groupby("cliente")["receita_total"].sum().reset_index()
        gasto_clientes["segmento"] = gasto_clientes["receita_total"].apply(
            lambda x: "Bronze" if x < 5000 else ("Prata" if x <= 15000 else "Ouro")
        )
        self.clientes = gasto_clientes.sort_values(by="receita_total", ascending=False)

        print("\n=== TOP 10 CLIENTES ===")
        print(self.clientes.head(10))

    def visualizar(self):
        os.makedirs("outputs/graficos", exist_ok=True)
        plt.rcParams["figure.figsize"] = (12, 6)
        plt.rcParams["axes.titlesize"] = 14

        fig, ax = plt.subplots()
        ax.plot(self.metricas["por_mes"]["mes"], self.metricas["por_mes"]["receita_total"], marker="o", linewidth=2, color="teal")
        ax.set_title("Receita Total por Mês")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Receita Total (R$)")
        plt.tight_layout()
        plt.savefig("outputs/graficos/receita_por_mes.png", dpi=100)
        plt.close()

        fig, ax = plt.subplots()
        sns.barplot(data=self.metricas["top_produtos"], y="produto", x="receita_total", hue="produto", legend=False, palette="Blues_r", ax=ax)
        ax.set_title("Top 5 Produtos por Receita")
        ax.set_xlabel("Receita Total (R$)")
        ax.set_ylabel("Produto")
        plt.tight_layout()
        plt.savefig("outputs/graficos/top_produtos.png", dpi=100)
        plt.close()

        fig, ax = plt.subplots()
        sns.scatterplot(data=self.df_limpo, x="quantidade", y="receita_total", hue="categoria", palette="deep", ax=ax)
        ax.set_title("Quantidade vs Receita")
        ax.set_xlabel("Quantidade")
        ax.set_ylabel("Receita (R$)")
        ax.legend(title="Categoria")
        plt.tight_layout()
        plt.savefig("outputs/graficos/quantidade_vs_receita.png", dpi=100)
        plt.close()

        fig, axes = plt.subplots(2, 2, figsize=(14, 9))
        axes[0, 0].plot(self.metricas["por_mes"]["mes"], self.metricas["por_mes"]["receita_total"], marker="o", color="teal")
        axes[0, 0].set_title("Receita por Mês")
        axes[0, 0].set_xlabel("Mês")

        sns.barplot(data=self.metricas["top_produtos"], y="produto", x="receita_total", hue="produto", legend=False, palette="Blues_r", ax=axes[0, 1])
        axes[0, 1].set_title("Top Produtos")

        sns.scatterplot(data=self.df_limpo, x="quantidade", y="receita_total", hue="categoria", palette="deep", ax=axes[1, 0])
        axes[1, 0].set_title("Quant. vs Receita")

        sns.barplot(data=self.metricas["por_regiao"], x="regiao", y="receita_total", hue="regiao", legend=False, palette="Set2", ax=axes[1, 1])
        axes[1, 1].set_title("Receita por Região")
        axes[1, 1].tick_params(axis='x', rotation=45)

        fig.suptitle("SalesInsight PY - Painel Resumo", fontsize=16)
        plt.tight_layout()
        plt.savefig("outputs/graficos/painel_resumo.png", dpi=150)
        plt.close()

    def resumo(self):
        os.makedirs("outputs", exist_ok=True)
        self.metricas["por_mes"].to_csv("outputs/metricas_por_mes.csv", index=False, encoding="utf-8-sig")
        self.clientes.to_csv("outputs/segmentacao_clientes.csv", index=False, encoding="utf-8-sig")

        estatisticas = {
            "total_receita": self.df_limpo["receita_total"].sum(),
            "ticket_medio_geral": self.df_limpo["receita_total"].mean(),
            "total_vendas": len(self.df_limpo)
        }
        serializavel = {k: round(float(v), 2) for k, v in estatisticas.items()}

        caminho_json = "outputs/estatisticas_gerais.json"
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(serializavel, f, indent=4, ensure_ascii=False)

        with open(caminho_json, "r", encoding="utf-8") as f:
            conferencia = json.load(f)
        print(f"\nJSON gravado e lido com sucesso: {conferencia}")

def main():
    print("=" * 60)
    print("SALESINSIGHT PY - Análise de Dados de Vendas")
    print("=" * 60)

    if not os.path.exists("vendas.csv"):
        df_bruto = gerar_dataset_vendas()
        df_bruto.to_csv("vendas.csv", index=False)
        print("Dataset gerado e salvo como 'vendas.csv'.")

    analisador = AnalisadorDeVendas()
    analisador.carregar("vendas.csv")
    analisador.inspecionar_dados()
    analisador.transformar()
    analisador.analisar()
    analisador.visualizar()
    analisador.resumo()
    print("\n[CONCLUIDO] Fluxo finalizado com sucesso.")

if __name__ == "__main__":
    main()
