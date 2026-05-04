# Лабораторная работа: Kubernetes (задание №7)

## Ссылка на демонстрацию работы
https://drive.google.com/file/d/19M1Vnkc3MYYQ4imigWI685mGlv4oNW2y/view

## Описание файлов
`app.py` - Flask: `/`, `/health`, `/load` (нагрузка на CPU для демо HPA)
`Dockerfile` - Сборка образа `my-app:latest`
`k8s/deployment.yaml` - Deployment `my-app`
`k8s/service.yaml` - Service `my-app` (порт 80 → 8080 в pod)

## 1. Запуск Minikube

```bash
minikube start
```

Проверка:
```bash
kubectl get nodes
```

## 2. Сборка образа внутри Docker Minikube

```bash
eval $(minikube docker-env)
docker build -t my-app:latest .
eval $(minikube docker-env -u)
```

## 3. Deployment и Service

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## 4. Количество подов: 3

```bash
kubectl scale deployment my-app --replicas=3
```

```bash
kubectl get deployment my-app
kubectl get pods -l app=my-app
```

## 5. Metrics Server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Подождать где-то 30 секунд появления сервера, проверять такой командой

```bash
kubectl top nodes
```

Если сервер не появляется может помочь такая команда, после этого опять ждать 30 секунд
```bash
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

## 6. Horizontal Pod Autoscaler

Вариант из задания (командная строка):

```bash
kubectl autoscale deployment my-app --cpu=50% --min=2 --max=5
```

При перезапуске может быть полезно
```bash
kubectl get hpa
kubectl delete hpa my-app
```

## 6.5. Нагрузка для проверки масштабирования

Временный pod с `curl` в цикле на `/load`:
```bash
kubectl run load --rm -it --restart=Never --image=curlimages/curl -- \
  sh -c 'while true; do curl -s "http://my-app.default.svc.cluster.local/load"; done'
```

Удаление нагрузки:
```bash
kubectl get pod load
kubectl delete pod load --force --grace-period=0
```

Смотрим статистику:

```bash
watch kubectl get pods -l app=my-app
kubectl get hpa my-app
```

## 7. Prometheus и Grafana (Helm)

Добавляем репозиторий и установливаем стек:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

Дождаться готовности подов в `monitoring`.

### Вход в Grafana

```bash
kubectl get secret -n monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d && echo

kubectl get secret -n monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-user}" | base64 -d && echo

kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Открыть в браузере: `http://localhost:3000`

Открыть dashboard.

И так же можно посмотреть на вывод в консоле:
```bash
kubectl describe hpa my-app
```

Остановка всего:
```bash
minikube stop
```

