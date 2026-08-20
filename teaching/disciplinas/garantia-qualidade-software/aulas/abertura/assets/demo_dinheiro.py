"""Aula 1 — demo: dinheiro em float. Código que 'funciona' e some com centavo."""

print("=== 1. A aritmética que você aprendeu não vale aqui ===")
print("0.1 + 0.2      =", 0.1 + 0.2)
print("0.1 + 0.2 == 0.3 ?", 0.1 + 0.2 == 0.3)

print()
print("=== 2. Arredondar também não salva ===")
print("round(2.675, 2) =", round(2.675, 2), " <- esperado 2.68")
print("round(1.005, 2) =", round(1.005, 2), " <- esperado 1.01")

print()
print("=== 3. Parcelamento do pedidos-api ===")


def parcelas(total, n):
    valor = round(total / n, 2)
    return [valor] * n


for total, n in [(100.00, 3), (19.90, 7), (250.00, 6)]:
    p = parcelas(total, n)
    soma = round(sum(p), 2)
    print(f"  R$ {total:>7.2f} em {n}x = {n} x R$ {p[0]:.2f}"
          f" -> soma R$ {soma:.2f} | diferença R$ {round(soma - total, 2):+.2f}")

print()
print("=== 4. Um ano de operação ===")
perda = round(sum(parcelas(100.00, 3)), 2) - 100.00
print(f"  diferença por pedido : R$ {perda:+.2f}")
print(f"  x 500 pedidos/dia    : R$ {perda * 500:+.2f} por dia")
print(f"  x 365 dias           : R$ {perda * 500 * 365:+.2f} por ano")

print()
print("=== 5. O teste que ninguém escreveu ===")
try:
    assert sum(parcelas(100.00, 3)) == 100.00, "as parcelas não somam o total"
    print("  OK")
except AssertionError as e:
    print("  FALHOU:", e)
