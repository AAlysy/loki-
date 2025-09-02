# Guide : Configuration de Loki dans Grafana

## 1. Configuration de Loki

### Fichier loki-config.yml
```yaml
auth_enabled: false

server:
  http_listen_port: 3100

limits_config:
  volume_enabled: true    # Important : Activation des volumes de logs

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 5m
  chunk_retain_period: 30s
  wal:
    enabled: true
    dir: /loki/wal

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
    cache_ttl: 24h
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

compactor:
  working_directory: /loki/compactor
  shared_store: filesystem
```

## 2. Vérification dans Grafana

1. Allez dans l'interface Grafana
2. Sélectionnez "Explore"
3. Choisissez "Loki" comme source de données
4. Dans le coin supérieur droit, vous devriez voir "Volume" activé

## 3. Utilisation

Une fois le volume activé, vous pouvez :
- Voir le volume de logs par service
- Analyser les tendances de volume de logs
- Configurer des alertes basées sur le volume

## 4. Dépannage

Si le volume n'apparaît pas :
1. Vérifiez que `volume_enabled: true` est bien configuré
2. Redémarrez Loki :
   ```bash
   docker-compose restart loki
   ```
3. Rafraîchissez l'interface Grafana
