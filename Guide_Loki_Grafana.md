# Guide Détaillé : Configuration Loki avec Grafana

## 1. Comprendre l'Architecture Loki

Loki se compose de trois composants principaux :
- **Loki** : Le backend qui stocke et traite les logs
- **Promtail** : L'agent qui collecte et envoie les logs à Loki
- **Grafana** : L'interface pour visualiser les logs

## 2. Structure des Fichiers
```
loki/
  ├── docker-compose.yml
  ├── loki-config.yml
  ├── promtail-config.yml
  └── prometheus.yml (optionnel)
```

## 3. Comprendre le fichier docker-compose.yml

```yaml
version: "3"

services:
  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"                    # Port de l'API Loki
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml  # Configuration
    command: -config.file=/etc/loki/local-config.yaml
    restart: unless-stopped

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - /var/log:/var/log             # Logs du système
      - ./promtail-config.yml:/etc/promtail/config.yml  # Configuration
      # Pour Windows, utilisez :
      # - /c/Windows/System32/LogFiles:/var/log/windows
    command: -config.file=/etc/promtail/config.yml
    restart: unless-stopped
    depends_on:
      - loki

  grafana:
    image: grafana/grafana:latest
    container_name: grafana-loki
    ports:
      - "3000:3000"                   # Interface web Grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped
    depends_on:
      - loki

volumes:
  grafana-data:
```

## 4. Configuration de Loki (loki-config.yml)

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 1h
  chunk_retain_period: 30s
  max_chunk_age: 1h

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
    active_index_directory: /tmp/loki/boltdb-shipper-active
    cache_location: /tmp/loki/boltdb-shipper-cache
    cache_ttl: 24h
    shared_store: filesystem
  filesystem:
    directory: /tmp/loki/chunks

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: false
  retention_period: 0s
```

## 5. Configuration de Promtail (promtail-config.yml)

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Pour Linux
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*log

  # Pour Windows
  - job_name: windows
    static_configs:
      - targets:
          - localhost
        labels:
          job: windows
          __path__: /var/log/windows/*
```

## 6. Démarrage et Configuration Étape par Étape

### 6.1. Lancement des Services
1. Ouvrez PowerShell dans le répertoire du projet
2. Exécutez :
   ```powershell
   docker-compose up -d
   ```
3. Vérifiez les conteneurs :
   ```powershell
   docker-compose ps
   ```
   Tous les conteneurs doivent être "Up"

### 6.2. Configuration de Grafana pour Loki

1. Accédez à Grafana (http://localhost:3000)
2. Connectez-vous avec :
   - Username : admin
   - Password : admin

3. Ajout de Loki comme Source de Données :
   - Allez dans Configuration > Data Sources
   - Cliquez sur "Add data source"
   - Sélectionnez "Loki"
   - Configurez :
     - Name: Loki
     - URL: http://loki:3100
     - Access: Server (default)
   - Cliquez sur "Save & Test"

## 7. Utilisation de Loki dans Grafana

### 7.1. Explorer les Logs
1. Cliquez sur "Explore" dans le menu latéral
2. Sélectionnez "Loki" comme source de données
3. Utilisez le LogQL pour requêter vos logs :
   ```
   {job="varlogs"}  # Tous les logs du système
   {job="windows"}  # Logs Windows
   ```

### 7.2. Exemples de Requêtes LogQL
```
# Recherche de texte
{job="varlogs"} |= "error"

# Comptage d'occurrences
count_over_time({job="varlogs"} [1h])

# Filtrage par labels
{job="varlogs", filename="/var/log/syslog"}
```

## 8. Résolution des Problèmes Courants

### 8.1. Pas de Logs Visibles
1. Vérifiez que Promtail est en cours d'exécution :
   ```powershell
   docker-compose logs promtail
   ```
2. Vérifiez les permissions des fichiers de logs
3. Vérifiez la configuration des paths dans promtail-config.yml

### 8.2. Erreurs de Connexion
1. Vérifiez que Loki est accessible :
   ```powershell
   curl http://localhost:3100/ready
   ```
2. Vérifiez les logs de Loki :
   ```powershell
   docker-compose logs loki
   ```

### 8.3. Problèmes de Performance
1. Ajustez les limites dans loki-config.yml
2. Vérifiez l'utilisation des ressources :
   ```powershell
   docker stats
   ```

## 9. Commandes Utiles

```powershell
# Voir les logs des composants
docker-compose logs loki
docker-compose logs promtail

# Redémarrer un service
docker-compose restart loki
docker-compose restart promtail

# Vérifier l'état des services
docker-compose ps

# Nettoyer complètement et redémarrer
docker-compose down -v
docker-compose up -d
```

## 10. Bonnes Pratiques

1. **Labels** :
   - Utilisez des labels pertinents
   - Évitez trop de valeurs uniques
   - Structurez vos labels de manière cohérente

2. **Rétention** :
   - Configurez une politique de rétention adaptée
   - Surveillez l'utilisation du stockage

3. **Performance** :
   - Limitez le nombre de streams concurrents
   - Utilisez des filtres efficaces
   - Optimisez vos requêtes LogQL
