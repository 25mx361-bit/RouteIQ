import docx
from report_generator.styles import (
    add_chapter_heading, add_main_heading, add_sub_heading,
    add_hint_paragraph, add_body_paragraph, add_bullet_point,
    add_table_custom, add_figure_custom
)

def build_chapter_3(doc):
    add_chapter_heading(doc, "CHAPTER 3\nSYSTEM DESIGN")

    # 3.1 Introduction
    add_main_heading(doc, "3.1 Introduction")
    add_hint_paragraph(doc, 
        "System design transforms functional and non-functional requirements into robust architectural blueprints, database schemas, and mathematical formulations. This section introduces the multi-tiered design methodology adopted for RouteIQ."
    )
    add_body_paragraph(doc, 
        "The design phase establishes the architectural blueprints, database structures, and mathematical formulations required for RouteIQ. The design orchestrates interactive map rendering, asynchronous REST microservices, relational persistence, and machine learning forecasting pipelines. This chapter details the architectural models through standardized UML diagrams, data flow representations, complete database schemas, and formulations of PatchTST and CatBoost models."
    )

    # 3.2 Overall System Architecture
    add_main_heading(doc, "3.2 Overall System Architecture")
    add_hint_paragraph(doc, 
        "A modular, multi-tier architecture ensures scalability, decoupled maintenance, and robust data isolation. This section details the overarching tiered architecture of the RouteIQ platform."
    )
    add_body_paragraph(doc, 
        "RouteIQ is structured across four primary tiers: Client Presentation Tier (React.js, Tailwind CSS, Leaflet), Application Gateway Tier (Python Flask REST controllers and feature engineering services), Core Intelligence Tier (PyTorch PatchTST and CatBoost ranker), and Data Persistence Tier (MySQL relational storage). External web services supply geocoding, route topologies, weather telemetry, and live traffic feeds."
    )

    arch_diagram = (
        "+-----------------------------------------------------------------------------+\n"
        "| PRESENTATION TIER: React.js SPA, Tailwind CSS, Interactive Leaflet Canvas   |\n"
        "+--------------------------------------|--------------------------------------+\n"
        "                                       | HTTPS / JSON REST API\n"
        "+--------------------------------------v--------------------------------------+\n"
        "| APPLICATION GATEWAY (FLASK): Auth, Routes, Prediction, Admin Blueprints     |\n"
        "+-------------------|--------------------------------------|------------------+\n"
        "                    | Telemetry & Geocoding                | Predictive Queries\n"
        "+-------------------v-------------------+  +---------------v------------------+\n"
        "| EXTERNAL APIS: OSM, ORS, Open-Meteo   |  | ML CORE: PatchTST + CatBoost     |\n"
        "+---------------------------------------+  +---------------|------------------+\n"
        "                                                           | Persist / Query\n"
        "+----------------------------------------------------------v------------------+\n"
        "| DATA PERSISTENCE: MySQL 8.0 (Users, Routes, Telemetry, Predictions, Admins) |\n"
        "+-----------------------------------------------------------------------------+"
    )
    add_figure_custom(
        doc,
        "Figure 3.1 Overall System Architecture of RouteIQ",
        arch_diagram,
        "Figure 3.1 depicts the four-tier architectural topology of RouteIQ, delineating client presentation, application routing logic, external web services, machine learning inference, and relational persistence."
    )

    # 3.3 System Workflow
    add_main_heading(doc, "3.3 System Workflow")
    add_hint_paragraph(doc, 
        "Tracing the operational pipeline step-by-step clarifies how individual subsystems cooperate to deliver predictions. This section details the sequential operational workflow executed upon each user request."
    )
    add_body_paragraph(doc, 
        "The workflow begins when an authenticated commuter inputs origin, destination, planned departure date, and target time. Geocoding resolves WGS84 coordinates; OpenRouteService derives geometric path candidates; external APIs extract weather and traffic telemetry; the feature pipeline normalizes temporal windows; PatchTST forecasts future congestion; and CatBoost executes composite ranking."
    )

    sys_wf_diagram = (
        "[User Input: Origin, Destination, Time] ---> [OSM Nominatim Geocoding]\n"
        "                                                   |\n"
        "[Feature Window (L=96)] <--- [Open-Meteo & TomTom] <--- [OpenRouteService Routes]\n"
        "         |\n"
        "         v\n"
        "[PatchTST: 9-Hr Forecast] ---> [CatBoost: Route Utility Scoring] ---> [Ranked Dashboard]"
    )
    add_figure_custom(
        doc,
        "Figure 3.2 System Workflow Diagram from Input to Route Recommendation",
        sys_wf_diagram,
        "Figure 3.2 illustrates the sequential execution pipeline of RouteIQ, highlighting data handoffs between external spatial engines, meteorological services, deep forecasting, and gradient boosted evaluation."
    )

    # 3.4 Use Case Diagram
    add_main_heading(doc, "3.4 Use Case Diagram")
    add_hint_paragraph(doc, 
        "Use case diagrams delineate system functionality from the perspective of external actors, illustrating authorization boundaries and operational scopes. This section details the use case model for the Commuter and Administrator actors."
    )
    add_body_paragraph(doc, 
        "The use case model defines interactions for two primary actors: Commuters (account registration, login, route searching, viewing congestion forecasts, comparing alternative paths, and viewing search history) and Administrators (logging road disruptions, triggering model retraining, and inspecting validation metrics)."
    )

    uc_diagram = (
        "  COMMUTER ACTOR:                               ADMINISTRATOR ACTOR:\n"
        "  ├── Register Account                          ├── Authenticate / Login\n"
        "  ├── Login / Session Management                ├── Log Incident / Road Closure\n"
        "  ├── Query Origin & Destination                ├── View Telemetry Health\n"
        "  ├── View Congestion Forecast Heatmap          ├── Trigger Model Retraining\n"
        "  └── Compare Alternative Routes                └── Inspect Validation Metrics"
    )
    add_figure_custom(
        doc,
        "Figure 3.3 Use Case Diagram for RouteIQ Actors",
        uc_diagram,
        "Figure 3.3 presents the formal use case model of RouteIQ, defining the interaction boundaries and privileges allocated to commuters and system administrators."
    )

    # 3.5 Activity Diagram
    add_main_heading(doc, "3.5 Activity Diagram")
    add_hint_paragraph(doc, 
        "Activity diagrams represent the procedural logic, decision branches, and concurrent flows executing within business processes. This section presents the behavioral activity flow of a commuter route search."
    )
    add_body_paragraph(doc, 
        "The activity flow captures dynamic control logic when a user submits a query. Inputs are validated; coordinates resolved; routes queried; weather and telemetry ingested; PatchTST forecast executed; CatBoost evaluation performed; and recommendations rendered on the client map."
    )

    act_diagram = (
        "(Start) -> [Input Origin, Destination, Time] -> [Validate Form Inputs]\n"
        "   | Valid\n"
        "   v\n"
        "[Resolve OSM Coordinates] -> [Fetch ORS Candidate Routes] -> [Ingest Weather & Traffic]\n"
        "   |\n"
        "   v\n"
        "[Run PatchTST Forecast] -> [Run CatBoost Route Evaluation] -> [Filter Restricted Routes]\n"
        "   |\n"
        "   v\n"
        "[Render Interactive Map with Color-Coded Polylines & Ranked Comparison Table] -> (End)"
    )
    add_figure_custom(
        doc,
        "Figure 3.4 Activity Diagram of Commuter Route Search and Evaluation",
        act_diagram,
        "Figure 3.4 diagrams the procedural control flow, decision branches, validation gates, and external service synchronization executed during an end-to-end routing request."
    )

    # 3.6 Data Flow Diagram
    add_main_heading(doc, "3.6 Data Flow Diagram")
    add_hint_paragraph(doc, 
        "Data Flow Diagrams (DFDs) track the flow of information across external entities, processing functions, and data stores. This section details both the Level 0 context diagram and the decomposed Level 1 functional DFD."
    )
    add_body_paragraph(doc, 
        "The Level 0 DFD illustrates RouteIQ as a single centralized system interacting with Commuters, Administrators, OpenStreetMap, OpenRouteService, Open-Meteo, and the Traffic Data API."
    )

    dfd0_diagram = (
        "[Commuter] ----(Origin, Destination, Target Time)----> [0.0 ROUTEIQ SYSTEM]\n"
        "[Admin] -------(Disruptions & Closures)---------------> [0.0 ROUTEIQ SYSTEM]\n"
        "[0.0 ROUTEIQ] <===(Coordinates, Routes, Weather, Speed)===> [External Web APIs]\n"
        "[0.0 ROUTEIQ] ----(Ranked Recommended Routes)---------> [Commuter Dashboard]"
    )
    add_figure_custom(
        doc,
        "Figure 3.5 Context Analysis: Data Flow Diagram (Level 0)",
        dfd0_diagram,
        "Figure 3.5 provides the Level 0 Context DFD, characterizing the boundary of RouteIQ and all external human actors and web APIs."
    )

    add_body_paragraph(doc, 
        "The Level 1 DFD decomposes the system into five sub-processes: Authentication (1.0), Spatial Routing (2.0), Telemetry Ingestion (3.0), Predictive Intelligence (4.0), and Route Scoring & Dashboard Rendering (5.0)."
    )

    dfd1_diagram = (
        "[Credentials] -> (1.0 Auth) <---> [D1: users]\n"
        "[Trip Query]  -> (2.0 Spatial Routing) <---> [OSM & ORS] ---> [D2: routes]\n"
        "                 (3.0 Telemetry Ingestion) <---> [Meteo & TomTom] ---> [D3: telemetry]\n"
        "                 (4.0 PatchTST Forecasting) <---> [D4: predictions]\n"
        "                 (5.0 CatBoost Evaluation) <---> [D5: admin_updates] ---> [D6: recomm.]\n"
        "                 (Dashboard Output) ----> [Interactive Client Map]"
    )
    add_figure_custom(
        doc,
        "Figure 3.6 Detailed Functional Flow: Data Flow Diagram (Level 1)",
        dfd1_diagram,
        "Figure 3.6 presents the decomposed Level 1 DFD, detailing data transitions across authentication, spatial routing, telemetry collection, deep forecasting, and decision ranking data stores."
    )

    # 3.7 Sequence Diagram
    add_main_heading(doc, "3.7 Sequence Diagram")
    add_hint_paragraph(doc, 
        "Sequence diagrams illustrate temporal message exchanges between software objects and services over time. This section presents the chronological sequence of interactions triggered by a commuter route search."
    )
    add_body_paragraph(doc, 
        "The sequence model captures asynchronous messaging between the React UI, Flask API controller, Geocoding Service, ORS client, Context Aggregator, PatchTST predictor, CatBoost ranker, and the MySQL database."
    )

    seq_diagram = (
        "User -> React UI: Submit Search Form (Origin, Destination, Time)\n"
        "React UI -> Flask API: POST /api/v1/routes/search\n"
        "Flask API -> External APIs: Geocode (OSM) & Get Alternative Routes (ORS)\n"
        "Flask API -> Open-Meteo & TomTom: Retrieve Weather and Traffic Telemetry\n"
        "Flask API -> ML Services: Execute PatchTST 9-Hr Forecast & CatBoost Ranking\n"
        "Flask API -> MySQL Database: Persist Search Query & Candidate Evaluations\n"
        "Flask API -> React UI: Return Ranked Route DTOs & Polyline GeoJSON\n"
        "React UI -> User: Render Visual Path Map, Travel Duration, and Congestion Badges"
    )
    add_figure_custom(
        doc,
        "Figure 3.7 Sequence Diagram for Predictive Route Recommendation Request",
        seq_diagram,
        "Figure 3.7 captures the chronological sequence of function calls, API requests, and database transactions executing during a routing evaluation."
    )
    # 3.8 Component Diagram
    add_main_heading(doc, "3.8 Component Diagram")
    add_hint_paragraph(doc, 
        "Component diagrams illustrate the physical or logical packaging of software code into reusable modules, components, and interfaces. This section outlines the modular breakdown of the RouteIQ codebase."
    )
    add_body_paragraph(doc, 
        "The component architecture partitions the system into cohesive packages: Frontend Client Package (React UI components), REST Controller Package (Flask Blueprints), Domain Services (Geocoding, Routing, Telemetry), Machine Learning Inference Services (PatchTST, CatBoost), and Data Repositories."
    )

    comp_diagram = (
        "[React Frontend] ----(REST/JSON)----> [Flask REST API Gateway]\n"
        "                                            |\n"
        "       +------------------------------------+-----------------------------------+\n"
        "       |                                    |                                   |\n"
        "       v                                    v                                   v\n"
        " [Geocoding & ORS Svc]            [Telemetry Ingestion Svc]             [ML Inference Svc]\n"
        "       |                                    |                                   |\n"
        "       +------------------------------------+-----------------------------------+\n"
        "                                            |\n"
        "                                            v\n"
        "                                [MySQL Data Access Repositories]"
    )
    add_figure_custom(
        doc,
        "Figure 3.8 Component Diagram of RouteIQ System Modules",
        comp_diagram,
        "Figure 3.8 exhibits the structural software components of RouteIQ, highlighting clean separation of concerns and interface contracts."
    )

    # 3.9 Deployment Diagram
    add_main_heading(doc, "3.9 Deployment Diagram")
    add_hint_paragraph(doc, 
        "Deployment diagrams delineate the physical hardware nodes, network topologies, and runtime execution environments hosting the software. This section describes the deployment infrastructure of RouteIQ."
    )
    add_body_paragraph(doc, 
        "The deployment topology consists of client browser nodes communicating over secure HTTPS/TLS with an application server hosting Gunicorn/Flask, PyTorch execution runtimes with CUDA acceleration, and an isolated MySQL 8.0 relational database server."
    )

    dep_diagram = (
        "+-----------------------------+              +------------------------------------------+\n"
        "|     CLIENT BROWSER NODE     |  TLS / HTTPS |          APPLICATION SERVER NODE         |\n"
        "|  React.js Single Page App   |<------------>|  Flask WSGI + PyTorch ML CUDA Runtime    |\n"
        "|  HTML5 Leaflet Map Canvas   |   Port 443   |  MySQL 8.0 Relational Database Engine    |\n"
        "+-----------------------------+              +------------------------------------------+"
    )
    add_figure_custom(
        doc,
        "Figure 3.9 Deployment Diagram of RouteIQ Infrastructure",
        dep_diagram,
        "Figure 3.9 diagrams the physical deployment topology, network boundaries, and execution environments supporting the platform."
    )

    # 3.10 Database Design
    add_main_heading(doc, "3.10 Database Design")
    add_hint_paragraph(doc, 
        "A well-structured relational schema guarantees data consistency, prevents anomalies, and optimizes query execution. This section details the relational data modeling approach implemented in MySQL."
    )
    add_body_paragraph(doc, 
        "The database design enforces Third Normal Form (3NF) across eight primary relational entities. Commuters execute searches; searches yield candidate routes; routes aggregate time-series traffic and weather telemetry; and machine learning models store predictive and evaluative scores. Administrative entities record verified road disruptions."
    )

    # 3.11 ER Diagram
    add_main_heading(doc, "3.11 ER Diagram")
    add_hint_paragraph(doc, 
        "Entity Relationship (ER) diagrams formally model entity classes, cardinalities, and foreign key relationships. This section presents the complete ER diagram for the RouteIQ database."
    )
    er_diagram = (
        "[users] (1) <---has---> (N) [search_history] (1) <---generates---> (N) [routes]\n"
        "                                                                     |\n"
        "               +----------------------+------------------------------+\n"
        "               | 1:N                  | 1:1                          | 1:1\n"
        "               v                      v                              v\n"
        "        [traffic_data]          [predictions]              [route_recommendations]\n"
        "        [weather_data]                                               ^\n"
        "                                                                     | N:1\n"
        "                                                              [admin_updates]"
    )
    add_figure_custom(
        doc,
        "Figure 3.10 Entity Relationship (ER) Diagram of Relational Database Schema",
        er_diagram,
        "Figure 3.10 displays the relational entities, primary-foreign key linkages, and cardinalities governing data persistence in RouteIQ."
    )

    # 3.12 Database Tables
    add_main_heading(doc, "3.12 Database Tables")
    add_hint_paragraph(doc, 
        "Physical table specifications translate ER models into concrete database structures. This section details the physical schema, column data types, constraints, and descriptions for all eight relational tables."
    )

    t1_data = [
        ["user_id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique identifier for commuter account."],
        ["username", "VARCHAR(50)", "NOT NULL, UNIQUE", "Unique username chosen by user."],
        ["email", "VARCHAR(100)", "NOT NULL, UNIQUE", "Validated email address for communication."],
        ["password_hash", "VARCHAR(255)", "NOT NULL", "Salted bcrypt cryptographic password hash."],
        ["role", "ENUM('user','admin')", "DEFAULT 'user'", "Role-based privilege level."],
        ["created_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Timestamp of account registration."]
    ]
    add_table_custom(doc, "Table 3.1 Database Table: users", ["Column Name", "Data Type", "Constraints", "Description"], t1_data)

    t2_data = [
        ["search_id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique identifier for search query."],
        ["user_id", "INT", "FOREIGN KEY (users.user_id)", "Associated commuter account ID."],
        ["source_name", "VARCHAR(255)", "NOT NULL", "User-specified textual origin."],
        ["source_lat", "DECIMAL(10,7)", "NOT NULL", "WGS84 latitude of origin."],
        ["source_lng", "DECIMAL(10,7)", "NOT NULL", "WGS84 longitude of origin."],
        ["dest_name", "VARCHAR(255)", "NOT NULL", "User-specified textual destination."],
        ["dest_lat", "DECIMAL(10,7)", "NOT NULL", "WGS84 latitude of destination."],
        ["dest_lng", "DECIMAL(10,7)", "NOT NULL", "WGS84 longitude of destination."],
        ["target_time", "DATETIME", "NOT NULL", "Commuter planned departure timestamp."]
    ]
    add_table_custom(doc, "Table 3.2 Database Table: search_history", ["Column Name", "Data Type", "Constraints", "Description"], t2_data)

    t3_data = [
        ["route_id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique identifier for candidate route."],
        ["search_id", "INT", "FOREIGN KEY (search_history.search_id)", "Associated parent search query."],
        ["route_index", "INT", "NOT NULL", "Route alternative sequence (0, 1, 2)."],
        ["summary", "VARCHAR(255)", "NULL", "ORS corridor summary or road names."],
        ["distance_km", "FLOAT", "NOT NULL", "Physical trajectory distance in kilometers."],
        ["duration_min", "FLOAT", "NOT NULL", "Standard free-flow duration in minutes."],
        ["geometry_geojson", "LONGTEXT", "NOT NULL", "Encoded polyline coordinates in GeoJSON format."]
    ]
    add_table_custom(doc, "Table 3.3 Database Table: routes", ["Column Name", "Data Type", "Constraints", "Description"], t3_data)

    t4_data = [
        ["traffic_id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Telemetry record identifier."],
        ["segment_id", "VARCHAR(64)", "NOT NULL", "Unique identifier of monitored road corridor."],
        ["timestamp", "DATETIME", "NOT NULL", "Timestamp of observation."],
        ["speed_kmh", "FLOAT", "NOT NULL", "Observed vehicular speed in km/h."],
        ["free_flow_speed", "FLOAT", "NOT NULL", "Statutory free-flow speed in km/h."],
        ["current_travel_time", "INT", "NOT NULL", "Observed corridor traversal time in seconds."],
        ["free_flow_travel_time", "INT", "NOT NULL", "Free-flow corridor traversal time in seconds."],
        ["data_source", "VARCHAR(32)", "DEFAULT 'tomtom'", "Source indicator ('tomtom', 'synthetic')."]
    ]
    add_table_custom(doc, "Table 3.4 Database Table: traffic_data", ["Column Name", "Data Type", "Constraints", "Description"], t4_data)

    t5_data = [
        ["weather_id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique weather observation record ID."],
        ["latitude", "DECIMAL(10,7)", "NOT NULL", "Observation station latitude."],
        ["longitude", "DECIMAL(10,7)", "NOT NULL", "Observation station longitude."],
        ["timestamp", "DATETIME", "NOT NULL", "Observation timestamp."],
        ["temperature", "FLOAT", "NOT NULL", "Air temperature in degrees Celsius."],
        ["precipitation", "FLOAT", "NOT NULL", "Precipitation volume in millimeters."],
        ["relative_humidity", "FLOAT", "NOT NULL", "Relative atmospheric humidity percentage."],
        ["wind_speed", "FLOAT", "NOT NULL", "Wind speed in kilometers per hour."]
    ]
    add_table_custom(doc, "Table 3.5 Database Table: weather_data", ["Column Name", "Data Type", "Constraints", "Description"], t5_data)

    t6_data = [
        ["prediction_id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique prediction record ID."],
        ["route_id", "INT", "FOREIGN KEY (routes.route_id)", "Associated candidate route."],
        ["forecast_horizon_step", "INT", "NOT NULL", "Prediction step index (1 to 36)."],
        ["predicted_speed_kmh", "FLOAT", "NOT NULL", "PatchTST forecasted speed in km/h."],
        ["predicted_travel_time", "FLOAT", "NOT NULL", "PatchTST forecasted travel duration in seconds."],
        ["predicted_tci", "FLOAT", "NOT NULL", "Computed Traffic Congestion Index (TCI)."],
        ["model_version", "VARCHAR(32)", "NOT NULL", "Identifier of active PatchTST model checkpoint."]
    ]
    add_table_custom(doc, "Table 3.6 Database Table: predictions", ["Column Name", "Data Type", "Constraints", "Description"], t6_data)

    t7_data = [
        ["recommendation_id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique route recommendation record ID."],
        ["route_id", "INT", "FOREIGN KEY (routes.route_id)", "Associated candidate route."],
        ["catboost_score", "FLOAT", "NOT NULL", "CatBoost composite route ranking score."],
        ["weather_risk_level", "VARCHAR(20)", "NOT NULL", "Evaluated weather hazard category."],
        ["event_delay_mult", "FLOAT", "DEFAULT 1.0", "Delay multiplier derived from active events."],
        ["is_recommended", "BOOLEAN", "NOT NULL", "True if selected as optimal candidate path."]
    ]
    add_table_custom(doc, "Table 3.7 Database Table: route_recommendations", ["Column Name", "Data Type", "Constraints", "Description"], t7_data)

    t8_data = [
        ["update_id", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique administrative incident record ID."],
        ["admin_id", "INT", "FOREIGN KEY (users.user_id)", "Admin user who logged the incident."],
        ["event_type", "VARCHAR(50)", "NOT NULL", "Disruption type ('construction', 'landslide', etc.)."],
        ["latitude", "DECIMAL(10,7)", "NOT NULL", "Disruption focal point latitude."],
        ["longitude", "DECIMAL(10,7)", "NOT NULL", "Disruption focal point longitude."],
        ["radius_km", "FLOAT", "DEFAULT 1.0", "Impact radius in kilometers."],
        ["severity", "VARCHAR(20)", "NOT NULL", "Severity rating ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')."],
        ["is_blocked", "BOOLEAN", "DEFAULT FALSE", "True if road is completely impassable."],
        ["start_time", "DATETIME", "NOT NULL", "Commencement timestamp of disruption."],
        ["end_time", "DATETIME", "NOT NULL", "Expected termination timestamp of disruption."]
    ]
    add_table_custom(doc, "Table 3.8 Database Table: admin_updates", ["Column Name", "Data Type", "Constraints", "Description"], t8_data)
    # 3.13 API Architecture
    add_main_heading(doc, "3.13 API Architecture")
    add_hint_paragraph(doc, 
        "Application Programming Interfaces govern secure communication between the client, backend services, and external microservices. This section details the RESTful API gateway architecture of RouteIQ."
    )
    add_body_paragraph(doc, 
        "RouteIQ implements a RESTful API architecture structured around stateless HTTP endpoints, standard JSON serialization, and uniform resource identifiers. Endpoints are organized into four Flask Blueprints: Authentication (/api/v1/auth), Route Discovery (/api/v1/routes), Congestion Forecasting (/api/v1/prediction), and Administrative Management (/api/admin)."
    )

    api_diagram = (
        "+-----------------------------------------------------------------------------+\n"
        "| ROUTEIQ REST API BLUEPRINTS:                                                |\n"
        "| - /api/v1/auth: POST /register, POST /login                                 |\n"
        "| - /api/v1/routes: POST /search, GET /alternatives/:id                       |\n"
        "| - /api/v1/prediction: POST /predict, GET /history                           |\n"
        "| - /api/admin: POST /incidents, GET /forecast-evaluations, POST /train       |\n"
        "+-----------------------------------------------------------------------------+"
    )
    add_figure_custom(
        doc,
        "Figure 3.11 API Interaction and Gateway Architecture",
        api_diagram,
        "Figure 3.11 outlines the RESTful endpoint routes, request verbs, and functional mappings exposed by the RouteIQ Flask API."
    )

    # 3.14 Machine Learning Pipeline
    add_main_heading(doc, "3.14 Machine Learning Pipeline")
    add_hint_paragraph(doc, 
        "A decoupled two-stage machine learning pipeline separates time-series corridor forecasting from multi-attribute route ranking. This section details the end-to-end data preparation, training, and inference pipeline."
    )
    add_body_paragraph(doc, 
        "The machine learning pipeline decouples temporal dynamics from static-tabular multi-criteria optimization. Stage 1 ingests 96 historical observations (24 hours of 15-minute telemetry intervals) across 12 temporal and weather features. PatchTST projects these into 12 temporal patches, executing channel-independent multi-head self-attention to generate a 36-step forecast (9 hours). Stage 2 receives predicted corridor metrics, joins route distance and geometric waypoints, computes weather risk indices, evaluates administrative incident penalties, and passes the synthesized 36-feature vector to CatBoost for final route scoring."
    )

    ml_pipe_diagram = (
        "[12 Telemetry Features] -> [StandardScaler] -> [Context Window L=96]\n"
        "                                                      |\n"
        "                                                      v\n"
        "                         +------------------------------------------------+\n"
        "                         | Stage 1: PatchTST Transformer (12 Patches)     |\n"
        "                         | Forecast Horizon H=36 (9-Hour Speed & TCI)     |\n"
        "                         +------------------------------------------------+\n"
        "                                                      |\n"
        "                                                      v\n"
        "[Predicted Speed & TCI] + [ORS Distance/Duration] + [Open-Meteo Weather] + [Incidents]\n"
        "                                                      |\n"
        "                                                      v\n"
        "                         +------------------------------------------------+\n"
        "                         | Stage 2: CatBoost Oblivious Decision Trees     |\n"
        "                         | Multi-Attribute Route Scoring S(R) & Ranking   |\n"
        "                         +------------------------------------------------+\n"
        "                                                      |\n"
        "                                                      v\n"
        "                                          [Ranked Recommended Route]"
    )
    add_figure_custom(
        doc,
        "Figure 3.12 End-to-End Machine Learning Pipeline of RouteIQ",
        ml_pipe_diagram,
        "Figure 3.12 charts the end-to-end data transformation pipeline linking PatchTST deep temporal forecasting with CatBoost tabular evaluation."
    )

    # 3.15 PatchTST Architecture
    add_main_heading(doc, "3.15 PatchTST Architecture")
    add_hint_paragraph(doc, 
        "Traditional transformers applied to raw point-wise time series suffer from high computational complexity and semantic noise. This section presents the mathematical and architectural formulation of the Patch Time Series Transformer (PatchTST) utilized in RouteIQ."
    )
    add_body_paragraph(doc, 
        "PatchTST (Nie et al., 2023) is a deep-learning architecture engineered specifically for multi-variate time-series forecasting. Standard transformers map individual time steps to attention tokens, leading to quadratic memory complexity with respect to sequence length L and losing localized semantic context. PatchTST resolves these vulnerabilities through Sub-series Patching and Channel Independence."
    )
    add_body_paragraph(doc, 
        "Sub-series Patching aggregates adjacent time steps into compact vector patches. Given a univariate time-series sequence of context length L, patching extracts overlapping segments of patch length P with stride S. The resulting number of patches N is given by: N = floor((L - P) / S) + 2. In RouteIQ, with L = 96 time steps (24 hours), patch length P = 16 (4 hours), and stride S = 8 (50% overlap), the sequence is transformed into N = 12 distinct patches. Each patch is projected into a d_model = 128 embedding space via learnable linear matrix W_p and summed with learnable positional embedding W_pos: x_p = W_p * x^(patch) + W_pos."
    )
    add_body_paragraph(doc, 
        "Channel Independence dictates that each input feature dimension m in {1, 2, ..., 12} is processed through the transformer encoder independently, sharing identical weights. The transformer encoder consists of 3 layers with 8 attention heads, FFN dimension of 512, and dropout 0.1. A linear prediction head projects flattened patch representations to generate a forecast horizon of H = 36 steps (9 hours ahead): y_hat_m = Flatten(Encoder(x_p_m)) * W_out + b_out."
    )

    patchtst_diagram = (
        "[Batch, L=96, M=12] -> [Channel Independence: [Batch * M, 96]]\n"
        "                               |\n"
        "                               v\n"
        "[Patching: P=16, S=8 -> N=12 Patches] -> [Linear Projection: 16 -> d_model=128]\n"
        "                               |\n"
        "                               v\n"
        "[3 Transformer Encoder Layers: 8 Heads, FFN=512, Dropout=0.1]\n"
        "                               |\n"
        "                               v\n"
        "[Flatten: 12 * 128 = 1536] -> [Linear Prediction Head: 1536 -> H=36]\n"
        "                               |\n"
        "                               v\n"
        "[Output Forecast: 36 Steps (9-Hour Speed, Travel Time, TCI)]"
    )
    add_figure_custom(
        doc,
        "Figure 3.13 PatchTST Patch-Based Transformer Architecture for Time-Series Traffic Forecasting",
        patchtst_diagram,
        "Figure 3.13 illustrates the structural data transformations occurring within PatchTST, depicting sub-series patch formation, channel-independent multi-head self-attention, and linear multi-step projection."
    )

    # 3.16 CatBoost Route Recommendation Architecture
    add_main_heading(doc, "3.16 CatBoost Route Recommendation Architecture")
    add_hint_paragraph(doc, 
        "Evaluating candidate routes requires synthesizing heterogeneous numerical metrics, categorical weather risk classifications, and administrative disruption tags. This section details the CatBoost route recommendation and scoring formulation."
    )
    add_body_paragraph(doc, 
        "CatBoost (Prokhorenkova et al., 2018) is a gradient-boosting library built on oblivious decision trees. Oblivious decision trees enforce identical splitting criteria across each tree depth level, guaranteeing balanced tree topologies, rapid execution latency, and resistance to overfitting on heterogeneous tabular data. CatBoost implements ordered boosting to handle categorical features (such as weather_risk_level and landslide_severity) without target statistics leakage."
    )
    add_body_paragraph(doc, 
        "The CatBoost model evaluates 34 numeric variables and 2 categorical variables per candidate route. The composite Route Score S(R) is formulated as: S(R) = w_1 * (1 / T_pred) + w_2 * (1 / D_km) - w_3 * TCI_pred - w_4 * W_risk - w_5 * E_penalty, where T_pred is predicted travel time, D_km is route distance, TCI_pred is the forecasted congestion index, W_risk is atmospheric hazard score, and E_penalty is the administrative disruption penalty. The model identifies the path maximizing S(R) as the recommended route."
    )

    catboost_diagram = (
        "[Route Metrics + Predicted Speed/TCI + Open-Meteo Weather + Incident Alerts]\n"
        "                                    |\n"
        "                                    v\n"
        "[CatBoost Oblivious Tree Ensemble: Depth=6, 500 Trees, Categorical Encoding]\n"
        "                                    |\n"
        "                                    v\n"
        "[Route Score S(R) -> Candidate Ranking & Optimal Route Selection]"
    )
    add_figure_custom(
        doc,
        "Figure 3.14 CatBoost Decision Forest for Multi-Attribute Route Recommendation",
        catboost_diagram,
        "Figure 3.14 details the feature ingestion, symmetric oblivious tree evaluation, and scoring logic implemented in CatBoost to rank candidate paths."
    )

    # 3.17 Concluding Remarks
    add_main_heading(doc, "3.17 Concluding Remarks")
    add_hint_paragraph(doc, 
        "This section concludes the system design chapter, summarizing architectural models and transitioning to system implementation."
    )
    add_body_paragraph(doc, 
        "This chapter established the complete system design of RouteIQ. The four-tier architecture, standardized UML structural and behavioral models, normalized relational database schemas across eight tables, and the mathematical formulations of PatchTST and CatBoost were detailed. Chapter 4 provides the software implementation details across frontend, backend, database, and artificial intelligence modules."
    )
