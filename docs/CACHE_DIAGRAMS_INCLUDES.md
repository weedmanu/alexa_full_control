
## 📊 Diagrammes

### Flux de Cache Multi-Niveaux

Le diagramme suivant illustre les trois scénarios possibles lors de la récupération de la liste des appareils :

```plantuml
@startuml
!include diagrams/cache_flow_diagram.puml
@enduml
```

![Cache Flow Diagram](diagrams/cache_flow_diagram.png)

### Architecture Globale

```plantuml
@startuml
!include diagrams/cache_architecture.puml
@enduml
```

![Cache Architecture](diagrams/cache_architecture.png)

### Machine à États

Le cache évolue entre différents états selon l'utilisation :

```plantuml
@startuml
!include diagrams/cache_state_machine.puml
@enduml
```

![Cache State Machine](diagrams/cache_state_machine.png)

### Comparaison de Performances

```plantuml
@startuml
!include diagrams/cache_performance.puml
@enduml
```

![Cache Performance](diagrams/cache_performance.png)

---

**Note:** Pour visualiser les diagrammes PlantUML :
- Dans VS Code: Installer l'extension `PlantUML` (jebbs.plantuml)
- En ligne: Copier le contenu .puml sur http://www.plantuml.com/plantuml/
- En local: `java -jar plantuml.jar docs/diagrams/*.puml`
