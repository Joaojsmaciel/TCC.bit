#!/usr/bin/env bash
set -euo pipefail

GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_AUTH="${GRAFANA_AUTH:-admin:admin}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://prometheus:9090}"

echo "⏳ Verificando se o Grafana está online..."

if ! command -v curl >/dev/null 2>&1; then
  echo "❌ curl não encontrado. Instale o curl para executar este script."
  exit 1
fi

grafana_ready=false
for _ in {1..60}; do
  if curl -fsS "$GRAFANA_URL/api/health" >/dev/null 2>&1; then
    grafana_ready=true
    break
  fi

  sleep 2
done

if [[ "$grafana_ready" != "true" ]]; then
  echo "❌ Grafana não respondeu em $GRAFANA_URL após 120 segundos."
  exit 1
fi

echo "✅ Grafana está online!"

NODE_PAYLOAD="$(mktemp)"
P2P_PAYLOAD="$(mktemp)"
trap 'rm -f "$NODE_PAYLOAD" "$P2P_PAYLOAD"' EXIT

echo "🔌 Configurando o Prometheus como Data Source..."
curl -fsS -X DELETE -u "$GRAFANA_AUTH" \
  "$GRAFANA_URL/api/datasources/name/Prometheus" >/dev/null 2>&1 || true

curl -fsS -X POST \
  -H "Content-Type: application/json" \
  -u "$GRAFANA_AUTH" \
  --data-binary @- \
  "$GRAFANA_URL/api/datasources" >/dev/null <<JSON
{
  "name": "Prometheus",
  "uid": "prometheus",
  "type": "prometheus",
  "url": "$PROMETHEUS_URL",
  "access": "proxy",
  "isDefault": true,
  "jsonData": {
    "timeInterval": "5s"
  }
}
JSON
echo "✅ Data Source configurado!"

echo "📊 Importando o Dashboard do Node Exporter (ID: 1860)..."
NODE_JSON="$(curl -fsSL https://grafana.com/api/dashboards/1860/revisions/latest/download)"

cat > "$NODE_PAYLOAD" <<JSON
{
  "dashboard": $NODE_JSON,
  "overwrite": true,
  "inputs": [
    {
      "name": "DS_PROMETHEUS",
      "type": "datasource",
      "pluginId": "prometheus",
      "value": "Prometheus"
    }
  ]
}
JSON

curl -fsS -X POST \
  -H "Content-Type: application/json" \
  -u "$GRAFANA_AUTH" \
  --data-binary @"$NODE_PAYLOAD" \
  "$GRAFANA_URL/api/dashboards/import" >/dev/null
echo "✅ Node Exporter importado!"

echo "🚀 Criando o Dashboard customizado do Tracker P2P..."
cat > "$P2P_PAYLOAD" <<'JSON'
{
  "dashboard": {
    "uid": "p2p-tracker",
    "title": "📡 Controle da Rede P2P",
    "refresh": "5s",
    "schemaVersion": 39,
    "time": {
      "from": "now-15m",
      "to": "now"
    },
    "panels": [
      {
        "type": "stat",
        "title": "NÓS ATIVOS NA REDE",
        "datasource": {
          "type": "prometheus",
          "uid": "prometheus"
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        },
        "targets": [
          {
            "expr": "p2p_active_peers",
            "refId": "A",
            "datasource": {
              "type": "prometheus",
              "uid": "prometheus"
            }
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "decimals": 0
          },
          "overrides": []
        },
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "center",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": false
          },
          "textMode": "auto"
        }
      },
      {
        "type": "timeseries",
        "title": "Histórico de Peers (Quedas e Re-replicação)",
        "datasource": {
          "type": "prometheus",
          "uid": "prometheus"
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        },
        "targets": [
          {
            "expr": "p2p_active_peers",
            "refId": "A",
            "datasource": {
              "type": "prometheus",
              "uid": "prometheus"
            }
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "decimals": 0
          },
          "overrides": []
        },
        "options": {
          "legend": {
            "displayMode": "list",
            "placement": "bottom",
            "showLegend": true
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        }
      }
    ]
  },
  "overwrite": true
}
JSON

curl -fsS -X POST \
  -H "Content-Type: application/json" \
  -u "$GRAFANA_AUTH" \
  --data-binary @"$P2P_PAYLOAD" \
  "$GRAFANA_URL/api/dashboards/db" >/dev/null
echo "✅ Dashboard P2P criado!"

echo "🎉 Tudo pronto! Acesse: $GRAFANA_URL"
