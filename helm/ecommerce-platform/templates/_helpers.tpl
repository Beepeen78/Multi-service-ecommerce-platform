{{/*
Expand the name of the chart.
*/}}
{{- define "ecommerce-platform.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "ecommerce-platform.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ecommerce-platform.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ecommerce-platform.labels" -}}
helm.sh/chart: {{ include "ecommerce-platform.chart" . }}
{{ include "ecommerce-platform.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ecommerce-platform.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ecommerce-platform.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service template
*/}}
{{- define "ecommerce-platform.service" -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ .name }}
  labels:
    {{- include "ecommerce-platform.labels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ .name }}
spec:
  type: ClusterIP
  ports:
    - port: {{ .port }}
      targetPort: {{ .port }}
      protocol: TCP
      name: http
  selector:
    app.kubernetes.io/name: {{ include "ecommerce-platform.name" $ }}
    app.kubernetes.io/instance: {{ .Release.Name }}
    app.kubernetes.io/component: {{ .name }}
{{- end }}

{{/*
Deployment template
*/}}
{{- define "ecommerce-platform.deployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .name }}
  labels:
    {{- include "ecommerce-platform.labels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ .name }}
spec:
  replicas: {{ .replicas }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ include "ecommerce-platform.name" $ }}
      app.kubernetes.io/instance: {{ .Release.Name }}
      app.kubernetes.io/component: {{ .name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ include "ecommerce-platform.name" $ }}
        app.kubernetes.io/instance: {{ .Release.Name }}
        app.kubernetes.io/component: {{ .name }}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "{{ .port }}"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: {{ .name }}
        image: "{{ .image.repository }}:{{ .image.tag }}"
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: {{ .port }}
          protocol: TCP
        env:
        - name: PORT
          value: "{{ .port }}"
        - name: DB_HOST
          value: "{{ include "ecommerce-platform.fullname" $ }}-postgresql"
        - name: DB_PORT
          value: "5432"
        - name: DB_NAME
          value: {{ $.Values.postgresql.auth.database | quote }}
        - name: DB_USER
          value: "postgres"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {{ include "ecommerce-platform.fullname" $ }}-postgresql
              key: postgres-password
        - name: REDIS_URL
          value: "redis://{{ include "ecommerce-platform.fullname" $ }}-redis-master:6379"
        - name: REDIS_HOST
          value: "{{ include "ecommerce-platform.fullname" $ }}-redis-master"
        - name: REDIS_PORT
          value: "6379"
        - name: KAFKA_BROKER
          value: "{{ include "ecommerce-platform.fullname" $ }}-kafka:9092"
        resources:
          {{- toYaml .resources | nindent 10 }}
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
{{- end }}

{{/*
HPA template
*/}}
{{- define "ecommerce-platform.hpa" -}}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ .name }}
  labels:
    {{- include "ecommerce-platform.labels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ .name }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ .name }}
  minReplicas: {{ .autoscaling.minReplicas }}
  maxReplicas: {{ .autoscaling.maxReplicas }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ .autoscaling.targetCPUUtilizationPercentage }}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: {{ .autoscaling.targetMemoryUtilizationPercentage | default 80 }}
{{- end }}

