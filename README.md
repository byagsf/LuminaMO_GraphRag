# Proyecto: Módulo GraphRAG para Lumina

## Información General
- **Base:** GraphRAG de Microsoft
- **Vector DB:** Milvus ([https://milvus.io/](https://milvus.io/))
- **IA:** Google Gemini API (AIzaSyD2emQC2huUXTcykYTM2uSgVxZPuAH_dqc)
- **Arquitectura:** Servicio externo que envuelve GraphRAG
- **Autenticación:** Sistema de usuarios/roles existente en Lumina

---

## 1. Objetivos Principales

### Procesamiento de Documentos
- Subir y procesar documentos empresariales (PDF, DOCX, XLSX, TXT)
- Guardar metadatos y embeddings en Milvus + PostgreSQL
- Conservar archivo original para trazabilidad

### Integración en Tiempo Real
- **Servicios soportados:** Google Drive, Dropbox, NAS
- **Funcionalidad:** Indexación automática de documentos nuevos/actualizados

### Control de Accesos Granular
Los documentos pueden ser:
- **Públicos:** Accesibles para todos los usuarios de todas las empresas
- **Empresariales:** Restringidos a una o varias empresas específicas
- **Por Roles:** Limitados a ciertos roles dentro de empresas
- **Privados:** Exclusivos de un usuario

### Portabilidad Total
- Instalación independiente en cualquier empresa
- Dockerización completa para despliegues rápidos

---

## 2. Arquitectura del Sistema

### Diagrama de Conexiones

```mermaid
graph LR
    subgraph "Frontend"
        U[👤 Usuario Lumina]
    end
    
    subgraph "Backend Lumina"
        LA[🔐 Lumina API<br/>JWT Auth]
    end
    
    subgraph "GraphRAG Service"
        API[🚀 API GraphRAG<br/>Orquestador]
        AUTH[🔒 Validador JWT]
        PERM[👥 Control Permisos]
        PROC[📄 Procesador Docs]
        SYNC[🔄 Sync Manager]
    end
    
    subgraph "Bases de Datos"
        PG[(🗄️ PostgreSQL<br/>Metadatos & Permisos)]
        MV[(🧠 Milvus Vector DB<br/>Embeddings)]
    end
    
    subgraph "Almacenamiento"
        S3[☁️ S3/NAS<br/>Archivos Originales]
    end
    
    subgraph "IA & Procesamiento"
        GR[🤖 GraphRAG Core<br/>Microsoft]
        GEMINI[✨ Google Gemini<br/>AIzaSyD2emQC2huUXTcykYTM2uSgVxZPuAH_dqc]
    end
    
    subgraph "Servicios Externos"
        GD[📁 Google Drive]
        DB[📦 Dropbox]
        NAS_EXT[🏢 NAS Empresarial]
    end
    
    %% Conexiones principales
    U --> LA
    LA --> API
    API --> AUTH
    AUTH --> PERM
    PERM --> PG
    
    API --> PROC
    PROC --> S3
    PROC --> GR
    PROC --> GEMINI
    
    GR --> MV
    GEMINI --> MV
    
    %% Sincronización externa
    SYNC --> GD
    SYNC --> DB
    SYNC --> NAS_EXT
    
    GD --> PROC
    DB --> PROC
    NAS_EXT --> PROC
    
    %% Estilos fondo negro
    classDef frontend fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef backend fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef service fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef database fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef storage fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef ai fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef external fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    
    class U frontend
    class LA backend
    class API,AUTH,PERM,PROC,SYNC service
    class PG,MV database
    class S3 storage
    class GR,GEMINI ai
    class GD,DB,NAS_EXT external
```

### Flujo de Datos Principal

```mermaid
flowchart TD
    START([Usuario hace consulta]) --> AUTH{Validar JWT}
    AUTH -->|❌| REJECT[Acceso Denegado]
    AUTH -->|✅| PERMS[Obtener permisos del usuario]
    
    PERMS --> FILTER[Filtrar documentos accesibles]
    FILTER --> QUERY[Enviar query a GraphRAG + Gemini]
    
    QUERY --> SEARCH[Búsqueda vectorial en Milvus]
    SEARCH --> RESULTS[Procesar resultados con IA]
    RESULTS --> FINAL_FILTER[Filtro final de seguridad]
    
    FINAL_FILTER --> RESPONSE[Respuesta al usuario]
    
    %% Estilos fondo negro
    classDef process fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef decision fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef security fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef success fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    
    class PERMS,FILTER,QUERY,SEARCH,RESULTS process
    class AUTH decision
    class FINAL_FILTER,REJECT security
    class RESPONSE success
```

---

## 3. Integración con Google Gemini

### Configuración API
- **API Key:** AIzaSyD2emQC2huUXTcykYTM2uSgVxZPuAH_dqc
- **Modelo:** gemini-pro para texto, gemini-pro-vision para documentos con imágenes
- **Función:** Procesamiento inteligente de consultas y generación de respuestas contextuales

### Flujo de Trabajo con Gemini

```mermaid
graph TD
    DOC[📄 Documento subido] --> EXTRACT[Extraer texto y metadatos]
    EXTRACT --> GEMINI[🤖 Procesar con Gemini]
    GEMINI --> SUMMARY[📝 Generar resumen]
    GEMINI --> KEYWORDS[🏷️ Extraer palabras clave]
    GEMINI --> EMBEDDING[🧠 Crear embeddings]
    
    SUMMARY --> MILVUS[(Milvus Vector DB)]
    KEYWORDS --> POSTGRES[(PostgreSQL)]
    EMBEDDING --> MILVUS
    
    style DOC fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style EXTRACT fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style GEMINI fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style SUMMARY fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style KEYWORDS fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style EMBEDDING fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style MILVUS fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style POSTGRES fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style QUERY fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style CONTEXT fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style GEMINI_QUERY fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    style RESPONSE fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    
    QUERY[❓ Consulta usuario] --> CONTEXT[Obtener contexto de Milvus]
    CONTEXT --> GEMINI_QUERY[🤖 Procesar con Gemini]
    GEMINI_QUERY --> RESPONSE[📋 Respuesta contextual]
```

---

## 4. Modelo de Datos

### Tablas Principales

**companies**
- id (PK) → Identificador único de empresa
- name → Nombre de la empresa
- created_at → Fecha de creación

**roles** (estos roles ya existen en lumina solo seria consultarlos)
- id (PK) → Identificador único del rol  
- name → Nombre del rol
- company_id (FK) → Referencia a companies
- permissions → Permisos en JSON

**users**
- lumina_user_id (PK) → ID del usuario en Lumina
- role_id (FK) → Referencia a roles
- company_id (FK) → Referencia a companies
- last_login → Último acceso

**documents**
- id (PK) → Identificador único
- title → Título del documento
- file_type → Tipo de archivo (PDF, DOCX, etc.)
- storage_path → Ruta en almacenamiento externo
- status → Estado (processing, indexed, error)
- owner_user_id (FK) → Propietario del documento
- gemini_summary → Resumen generado por Gemini
- created_at, updated_at → Timestamps

**document_access**
- id (PK) → Identificador único
- document_id (FK) → Referencia a documents
- access_type → Tipo (public, company, role, user)
- target_id → ID del objetivo según el tipo
- granted_at → Fecha de otorgamiento

**document_embeddings**
- id (PK) → Identificador único
- document_id (FK) → Referencia a documents
- vector_id → ID del vector en Milvus
- chunk_content → Fragmento de texto
- gemini_processed → Indica si fue procesado por Gemini
- indexed_at → Fecha de indexación

---

## 5. Endpoints de la API

### Gestión de Documentos
- **POST /api/v1/documents** → Subir documento
- **GET /api/v1/documents** → Listar documentos accesibles
- **GET /api/v1/documents/{id}** → Obtener documento específico
- **DELETE /api/v1/documents/{id}** → Eliminar documento

### Integraciones Externas
- **POST /api/v1/sync/drive** → Configurar Google Drive
- **POST /api/v1/sync/dropbox** → Configurar Dropbox
- **POST /api/v1/sync/nas** → Configurar NAS empresarial
- **GET /api/v1/sync/status** → Estado de sincronizaciones

### Consultas Inteligentes
- **POST /api/v1/query** → Consulta con GraphRAG + Gemini
- **POST /api/v1/query/semantic** → Búsqueda semántica pura
- **POST /api/v1/summarize/{document_id}** → Resumen con Gemini

### Administración
- **GET /api/v1/permissions/{user_id}** → Permisos del usuario
- **POST /api/v1/permissions** → Otorgar permisos
- **GET /api/v1/analytics** → Métricas del sistema

---

## 6. Flujo de Seguridad Detallado

### Proceso de Autenticación

```mermaid
sequenceDiagram
    participant U as 👤 Usuario
    participant L as 🔐 Lumina
    participant G as 🚀 GraphRAG API
    participant P as 🗄️ PostgreSQL
    participant M as 🧠 Milvus
    participant AI as ✨ Gemini
    
    U->>L: Login con credenciales
    L->>U: JWT Token
    
    U->>G: Query con JWT
    G->>G: Validar JWT signature
    G->>P: Obtener user_id, company_id, role_id
    P->>G: Datos del usuario
    
    G->>P: Consultar documentos permitidos
    P->>G: Lista de document_ids accesibles
    
    G->>M: Buscar vectores filtrados
    M->>G: Embeddings relevantes
    
    G->>AI: Procesar con contexto + Gemini
    AI->>G: Respuesta inteligente
    
    G->>G: Filtro final de seguridad
    G->>U: Respuesta autorizada
```

---

## 7. Plan de Implementación por Fases

### Fase 1: Infraestructura Base
- Configurar Docker con GraphRAG, Milvus y PostgreSQL
- Estructura básica del API Service
- Integración inicial con Gemini API
- Autenticación JWT con Lumina

### Fase 2: Procesamiento de Documentos 
- Endpoints básicos de documentos
- Sistema de permisos granular
- Almacenamiento externo (S3)
- Procesamiento con Gemini para resúmenes

### Fase 3: Integraciones Externas 
- Google Drive API con webhooks
- Dropbox sincronización
- NAS y otros servicios
- Workers para indexación automática

### Fase 4: Optimización y Deploy 
- Pruebas de rendimiento
- Dockerización 

---

## 8. Recursos y Enlaces

### Tecnologías Principales
- **Milvus Vector Database:** [https://milvus.io/](https://milvus.io/)
- **Microsoft GraphRAG:** [https://github.com/microsoft/graphrag](https://github.com/microsoft/graphrag)

### API Keys y Configuración
- **Gemini API Key:** AIzaSyD2emQC2huUXTcykYTM2uSgVxZPuAH_dqc
- **Milvus Connection:** (es necesario descargarlo https://github.com/milvus-io/milvus)
- **PostgreSQL** 

---

## 🧪 Criterios de Aceptación

### Entregables del Proyecto

####  **API GraphRAG Service**
- [ ] Servicio API completamente funcional
- [ ] Endpoints documentados y testeados
- [ ] Sistema de autenticación JWT integrado con Lumina
- [ ] Control de permisos granular implementado
- [ ] Manejo de errores y logging completo
- [ ] Validación de datos de entrada robusta

#### 🗄️ **Base de Datos y Almacenamiento**
- [ ] Configuración de Milvus para embeddings
- [ ] Sistema de almacenamiento externo (S3) configurado
- [ ] Scripts de migración y backup automatizados
- [ ] Índices optimizados para consultas de permisos
- [ ] Conexiones SSL/TLS

#### 📄 **Procesamiento de Documentos**
- [ ] Soporte completo para PDF, DOCX, XLSX, TXT
- [ ] Integración funcional con Google Gemini API
- [ ] Sistema de indexación con GraphRAG + Milvus
- [ ] Generación automática de resúmenes con IA
- [ ] Extracción de metadatos y palabras clave
- [ ] Validación de formatos y tamaños de archivo

#### 🔄 **Integraciones Externas**
- [ ] Conexión con Google Drive API funcionando
- [ ] Integración con Dropbox completamente operativa
- [ ] Soporte para NAS empresariales (esto se tiene que desarrollar aparte y se tiene que solicitar permiso para el NAS
- [ ] Sistema de webhooks para sincronización automática
- [ ] Workers/jobs para procesamiento en background

#### 🔒 **Seguridad y Permisos**
- [ ] Sistema de permisos por empresa, rol y usuario
- [ ] Validación de JWT sin crear usuarios nuevos
- [ ] Filtrado de resultados según autorización


### 🧑‍💻 **Entorno de Pruebas**

#### Plataforma de Testing
- **Lumina Demo:** Las pruebas iniciales se realizarán integradas con la versión demo de Lumina junto con n8n
- **Datos de Prueba:** Conjunto de documentos empresariales reales (Paolo se los pasa)

#### Escenarios de Prueba
- [ ] Subida manual de documentos al graph y se realizan preguntas relacionados a este desde Lumina
- [ ] Sincronización automática con Google Drive de prueba
- [ ] Consultas con diferentes roles y permisos (desde Lumina)
- [ ] Tests de carga con múltiples usuarios
- [ ] Validación de respuestas ya con varios documentos de diferentes temas

### ✅ **Criterios de Aceptación Final**

#### Funcionalidad
[ ] Sistema completamente operativo con todos los componentes
[ ] Integración perfecta con Lumina Demo
[ ] Respuestas precisas y contextuales de GraphRAG + Gemini
[ ] Control de permisos funcionando al 100%
