# TaskFlow

A microservices-based task management application.

## Architecture

This project consists of multiple microservices with a modern microservices architecture:

### System Architecture Diagram

```mermaid
graph TB
    %% External Layer
    User[👤 User]
    
    %% Load Balancer / Proxy Layer
    LB[🌐 Nginx Load Balancer<br/>Port 8000]
    
    %% Frontend Layer
    Frontend[⚛️ React Frontend<br/>Port 3000<br/>TypeScript + Tailwind]
    
    %% API Gateway / Service Mesh
    subgraph "API Gateway"
        AuthAPI[🔐 Auth Service<br/>Port 8001<br/>Django + JWT]
        TasksAPI[📋 Tasks Service<br/>Port 8002<br/>Django + CRUD]
        NotificationsAPI[🔔 Notifications Service<br/>Port 8003<br/>FastAPI + Events]
    end
    
    %% Message Queue Layer
    subgraph "Message Queue"
        RabbitMQ[🐰 RabbitMQ<br/>Port 5672<br/>Event Streaming]
    end
    
    %% Data Layer
    subgraph "Data Storage"
        PostgreSQL[(🐘 PostgreSQL<br/>Port 5432<br/>Primary Database)]
        Redis[(🔴 Redis<br/>Port 6379<br/>Cache + Sessions)]
    end
    
    %% Infrastructure Layer
    subgraph "Infrastructure"
        K8s[☸️ Kubernetes Cluster<br/>AWS EKS]
        Terraform[🏗️ Terraform<br/>Infrastructure as Code]
    end
    
    %% CI/CD Layer
    subgraph "CI/CD Pipeline"
        GitHub[📦 GitHub Actions<br/>Build & Deploy]
        Docker[🐳 Docker Registry<br/>Container Images]
    end
    
    %% User Flow
    User --> LB
    LB --> Frontend
    Frontend --> AuthAPI
    Frontend --> TasksAPI
    Frontend --> NotificationsAPI
    
    %% Service Communication
    AuthAPI --> PostgreSQL
    AuthAPI --> Redis
    TasksAPI --> PostgreSQL
    TasksAPI --> Redis
    TasksAPI --> RabbitMQ
    NotificationsAPI --> RabbitMQ
    NotificationsAPI --> Redis
    
    %% Event Flow
    TasksAPI -.->|Task Events| RabbitMQ
    RabbitMQ -.->|Process Events| NotificationsAPI
    NotificationsAPI -.->|Store Notifications| Redis
    
    %% Infrastructure
    K8s --> AuthAPI
    K8s --> TasksAPI
    K8s --> NotificationsAPI
    K8s --> Frontend
    K8s --> PostgreSQL
    K8s --> Redis
    K8s --> RabbitMQ
    
    Terraform --> K8s
    GitHub --> Docker
    Docker --> K8s
    
    %% Styling
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef database fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef infrastructure fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef queue fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class Frontend frontend
    class AuthAPI,TasksAPI,NotificationsAPI backend
    class PostgreSQL,Redis database
    class K8s,Terraform,GitHub,Docker infrastructure
    class RabbitMQ queue
```

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant LB as Nginx LB
    participant A as Auth Service
    participant T as Tasks Service
    participant N as Notifications Service
    participant R as RabbitMQ
    participant DB as PostgreSQL
    participant C as Redis

    %% User Login Flow
    U->>F: 1. Login Request
    F->>LB: 2. POST /api/auth/login
    LB->>A: 3. Forward to Auth Service
    A->>DB: 4. Validate Credentials
    DB-->>A: 5. User Data
    A->>C: 6. Store Session
    A-->>LB: 7. JWT Tokens
    LB-->>F: 8. Auth Response
    F-->>U: 9. Login Success

    %% Task Creation Flow
    U->>F: 10. Create Task
    F->>LB: 11. POST /api/tasks (with JWT)
    LB->>T: 12. Forward to Tasks Service
    T->>A: 13. Validate JWT Token
    A-->>T: 14. Token Valid
    T->>DB: 15. Save Task
    T->>R: 16. Publish Task Created Event
    T-->>LB: 17. Task Created
    LB-->>F: 18. Success Response
    F-->>U: 19. Task Created

    %% Notification Flow
    R->>N: 20. Consume Task Event
    N->>C: 21. Store Notification
    N-->>R: 22. Event Processed

    %% Real-time Updates
    F->>LB: 23. GET /api/notifications
    LB->>N: 24. Fetch Notifications
    N->>C: 25. Get Stored Notifications
    C-->>N: 26. Notification Data
    N-->>LB: 27. Notifications
    LB-->>F: 28. Real-time Updates
    F-->>U: 29. Show Notifications
```

### Microservices Overview

- **Auth Service**: User authentication and authorization with JWT tokens
- **Tasks Service**: Task management and CRUD operations
- **Notifications Service**: Event-driven notifications and real-time updates
- **Frontend**: React/TypeScript web application with modern UI
- **Proxy**: Nginx reverse proxy with load balancing and security

### Deployment Architecture

```mermaid
graph TB
    subgraph "AWS Cloud"
        subgraph "EKS Cluster"
            subgraph "Ingress Layer"
                Ingress[🌐 Ingress Controller<br/>Nginx Ingress]
            end
            
            subgraph "Application Layer"
                subgraph "Frontend Pods"
                    Frontend1[⚛️ Frontend Pod 1]
                    Frontend2[⚛️ Frontend Pod 2]
                end
                
                subgraph "API Gateway Pods"
                    AuthPod1[🔐 Auth Pod 1]
                    AuthPod2[🔐 Auth Pod 2]
                    TasksPod1[📋 Tasks Pod 1]
                    TasksPod2[📋 Tasks Pod 2]
                    NotifPod1[🔔 Notifications Pod 1]
                    NotifPod2[🔔 Notifications Pod 2]
                end
            end
            
            subgraph "Data Layer"
                subgraph "Database Pods"
                    PostgresPod[🐘 PostgreSQL Pod<br/>Primary + Replica]
                end
                
                subgraph "Cache Layer"
                    RedisPod[🔴 Redis Pod<br/>Cluster Mode]
                end
                
                subgraph "Message Queue"
                    RabbitMQPod[🐰 RabbitMQ Pod<br/>High Availability]
                end
            end
            
            subgraph "Storage"
                EBS1[💾 EBS Volume 1<br/>PostgreSQL Data]
                EBS2[💾 EBS Volume 2<br/>RabbitMQ Data]
            end
        end
        
        subgraph "Infrastructure"
            subgraph "VPC"
                subgraph "Public Subnets"
                    ALB[⚖️ Application Load Balancer]
                    NAT[🌐 NAT Gateway]
                end
                
                subgraph "Private Subnets"
                    EKS[☸️ EKS Worker Nodes]
                end
            end
            
            subgraph "Security"
                IAM[🔐 IAM Roles & Policies]
                SG[🛡️ Security Groups]
                Secrets[🔑 AWS Secrets Manager]
            end
        end
        
        subgraph "CI/CD"
            ECR[📦 Amazon ECR<br/>Container Registry]
            CodePipeline[🔄 AWS CodePipeline]
        end
    end
    
    subgraph "External"
        User[👤 Users]
        GitHub[📦 GitHub Repository]
        Terraform[🏗️ Terraform State]
    end
    
    %% External connections
    User --> ALB
    GitHub --> CodePipeline
    Terraform --> EKS
    
    %% Load balancer flow
    ALB --> Ingress
    Ingress --> Frontend1
    Ingress --> Frontend2
    
    %% Frontend to API
    Frontend1 --> AuthPod1
    Frontend1 --> TasksPod1
    Frontend1 --> NotifPod1
    Frontend2 --> AuthPod2
    Frontend2 --> TasksPod2
    Frontend2 --> NotifPod2
    
    %% API to data layer
    AuthPod1 --> PostgresPod
    AuthPod1 --> RedisPod
    AuthPod2 --> PostgresPod
    AuthPod2 --> RedisPod
    
    TasksPod1 --> PostgresPod
    TasksPod1 --> RedisPod
    TasksPod1 --> RabbitMQPod
    TasksPod2 --> PostgresPod
    TasksPod2 --> RedisPod
    TasksPod2 --> RabbitMQPod
    
    NotifPod1 --> RabbitMQPod
    NotifPod1 --> RedisPod
    NotifPod2 --> RabbitMQPod
    NotifPod2 --> RedisPod
    
    %% Storage connections
    PostgresPod --> EBS1
    RabbitMQPod --> EBS2
    
    %% CI/CD flow
    CodePipeline --> ECR
    ECR --> EKS
    
    %% Security
    IAM --> EKS
    SG --> EKS
    Secrets --> EKS
    
    %% Styling
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef database fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef infrastructure fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef queue fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef storage fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    
    class Frontend1,Frontend2 frontend
    class AuthPod1,AuthPod2,TasksPod1,TasksPod2,NotifPod1,NotifPod2 backend
    class PostgresPod,RedisPod database
    class EKS,ALB,NAT,IAM,SG,Secrets infrastructure
    class RabbitMQPod queue
    class EBS1,EBS2,ECR storage
```

## Services

### Backend Services
- `auth_service/` - Django-based authentication service
- `tasks_service/` - Django-based task management service
- `notifications_service/` - FastAPI-based notification service

### Frontend
- `frontend/` - React/TypeScript application

### Infrastructure
- `infra/` - Kubernetes and Terraform configurations
- `proxy/` - Nginx configuration

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/bryandev95/taskflow.git
   cd taskflow
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Auth Service: http://localhost:8001
   - Tasks Service: http://localhost:8002
   - Notifications Service: http://localhost:8003

### Production Deployment

See individual service directories for setup instructions.

## Development

Use `docker-compose.yml` for local development with all services.
