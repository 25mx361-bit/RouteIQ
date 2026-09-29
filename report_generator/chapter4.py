import docx
from report_generator.styles import (
    add_chapter_heading, add_main_heading, add_sub_heading,
    add_hint_paragraph, add_body_paragraph, add_bullet_point,
    add_table_custom, add_figure_custom, add_code_block
)

def build_chapter_4(doc):
    add_chapter_heading(doc, "CHAPTER 4\nSYSTEM IMPLEMENTATION")

    # 4.1 Introduction
    add_main_heading(doc, "4.1 Introduction")
    add_hint_paragraph(doc, 
        "System implementation translates abstract architectural specifications, database designs, and algorithmic models into functional software artifacts. This section introduces the implementation methodology employed in RouteIQ."
    )
    add_body_paragraph(doc, 
        "The implementation phase of RouteIQ realizes the full functional vision of a predictive intelligent transportation platform. Software development spans frontend single-page development, backend microservice scripting, spatial service adapters, relational schema instantiation, and the concrete implementation of machine learning models. This chapter details the software modules, telemetry ingestion pipelines, PatchTST forecasting routines, CatBoost route evaluators, API integrations, and security controls that constitute the working platform."
    )

    # 4.2 Development Environment
    add_main_heading(doc, "4.2 Development Environment")
    add_hint_paragraph(doc, 
        "A standardized development environment ensures reproducible dependency management and collaborative compilation. This section outlines the development tools and runtime environments utilized."
    )
    add_body_paragraph(doc, 
        "RouteIQ was implemented on a dual-platform workstation running Microsoft Windows 11 (64-bit) and Ubuntu Linux 22.04 LTS. Backend code and machine learning scripts were developed in Python 3.10 within isolated virtual environments (venv), utilizing pip and wheel package managers. The frontend was built using Node.js (v18.16) and Vite. Development, debugging, and linting were conducted in Visual Studio Code equipped with Python, ESLint, and Tailwind CSS IntelliSense extensions. Relational schemas were managed via MySQL Workbench and MySQL CLI."
    )

    # 4.3 Frontend Implementation
    add_main_heading(doc, "4.3 Frontend Implementation")
    add_hint_paragraph(doc, 
        "Modern single-page applications require responsive layouts, declarative state management, and smooth spatial map interactions. This section describes the frontend engineering built with React.js and Tailwind CSS."
    )
    add_body_paragraph(doc, 
        "The frontend is constructed as a React.js single-page application adhering to modular component design. React hooks (useState, useEffect, useContext, useMemo) manage sessions, search parameters, asynchronous API states, and map layers. Tailwind CSS provides a responsive design system with accessible high-contrast palettes."
    )
    add_body_paragraph(doc, 
        "Mapping capabilities are integrated through Leaflet.js and React-Leaflet, rendering OpenStreetMap tiles on an HTML5 canvas. Candidate routes are rendered as dynamic polyline overlays color-coded by congestion severity: emerald green for free-flow (TCI < 1.15), amber for moderate delay (1.15 <= TCI <= 1.40), and crimson red for severe congestion (TCI > 1.40)."
    )

    scr_home = (
        "[SCREENSHOT PLACEHOLDER: Figure 4.1 Home and Navigation Landing Interface]\n"
        "Visible Components: Navigation header, search configuration card, departure datetime picker, interactive map canvas."
    )
    add_figure_custom(
        doc,
        "Figure 4.1 Home and Navigation Landing Interface [INSERT SCREENSHOT HERE]",
        scr_home,
        "Figure 4.1 displays the landing and search interface of RouteIQ. Purpose: Allows commuters to initiate trip searches and view metropolitan traffic overviews."
    )

    # 4.4 Backend Implementation
    add_main_heading(doc, "4.4 Backend Implementation")
    add_hint_paragraph(doc, 
        "A decoupled REST backend coordinates external API communications, executes feature transformations, and serves predictions. This section details the Python Flask application architecture."
    )
    add_body_paragraph(doc, 
        "The backend is developed in Python using Flask, organized via the Application Factory pattern and modular Blueprints. This ensures loose coupling between HTTP routing, business logic, persistence, and machine learning inference. Asynchronous request handling is supported by Gunicorn WSGI workers, while Flask-CORS manages cross-origin headers."
    )
    add_body_paragraph(doc, 
        "The backend encapsulates four specialized services: GeocodingService (interfacing with Nominatim), RoutingService (interfacing with OpenRouteService), TelemetryService (polling TomTom and Open-Meteo), and MLInferenceService (dispatching tensor computations to PyTorch and CatBoost)."
    )

    # 4.5 Database Implementation
    add_main_heading(doc, "4.5 Database Implementation")
    add_hint_paragraph(doc, 
        "Reliable persistence requires physical relational schemas, foreign key integrity, and optimized index configurations. This section details the MySQL database implementation."
    )
    add_body_paragraph(doc, 
        "The data layer is implemented in MySQL 8.0 utilizing the InnoDB storage engine to guarantee full ACID transaction semantics. Tables use utf8mb4 encoding to support international place names. Composite B-tree indexes are deployed across heavily queried dimensions, including (segment_id, timestamp) in traffic_data, (search_id, route_index) in routes, and (latitude, longitude) in spatial lookups."
    )

    # 4.6 User Registration and Login
    add_main_heading(doc, "4.6 User Registration and Login")
    add_hint_paragraph(doc, 
        "User identification and session authorization protect commuter data and restrict administrative operations. This section details the authentication module."
    )
    add_body_paragraph(doc, 
        "The authentication module manages commuter registration, credential verification, and session token distribution. Passwords are salted and hashed using bcrypt with a work factor of 12 before persistence. Login requests verify credentials using constant-time cryptographic checks, issuing signed JSON Web Tokens (JWT) valid for 24 hours."
    )

    scr_auth = (
        "[SCREENSHOT PLACEHOLDER: Figure 4.2 User Authentication Interface]\n"
        "Visible Components: Tabbed Login/Sign-up modal, email validation, password masking, error feedback banner."
    )
    add_figure_custom(
        doc,
        "Figure 4.2 User Authentication and Registration Interface [INSERT SCREENSHOT HERE]",
        scr_auth,
        "Figure 4.2 illustrates the user authentication and registration modal interface. Purpose: Authenticates commuters and administrators, establishing secure JWT sessions."
    )

    # 4.7 Source and Destination Module
    add_main_heading(doc, "4.7 Source and Destination Module")
    add_hint_paragraph(doc, 
        "Accurate trip configuration requires intuitive user input, debounced auto-completion, and spatial validation. This section describes the source and destination selection component."
    )
    add_body_paragraph(doc, 
        "The module provides interactive input fields equipped with client-side debounced auto-completion. As the commuter enters place names, the interface sends throttled requests to the backend geocoder, displaying matching landmarks. Commuters can also activate map-pinning mode, clicking directly on the Leaflet canvas to set origin and destination coordinates."
    )

    scr_search = (
        "[SCREENSHOT PLACEHOLDER: Figure 4.3 Interactive Route Search and Geocoding View]\n"
        "Visible Components: Origin auto-complete list, destination pin marker, datetime selector, route generation trigger."
    )
    add_figure_custom(
        doc,
        "Figure 4.3 Interactive Route Search and Geocoding View [INSERT SCREENSHOT HERE]",
        scr_search,
        "Figure 4.3 displays the origin and destination selection interface featuring auto-complete suggestions and spatial marker placement. Purpose: Captures commuter travel endpoints."
    )

    # 4.8 Geocoding Module
    add_main_heading(doc, "4.8 Geocoding Module")
    add_hint_paragraph(doc, 
        "Geocoding converts human-readable location descriptions into standardized geographic coordinates. This section details the OpenStreetMap Nominatim geocoding integration."
    )
    add_body_paragraph(doc, 
        "The Geocoding module communicates with OpenStreetMap's Nominatim REST service. The module parses user query strings, applies regional bounding boxes, and retrieves top candidate results. Each response is parsed to extract WGS84 decimal latitude and longitude. An in-memory LRU cache stores recent geocoding responses, respecting public rate-limit policies."
    )

    # 4.9 Route Generation Module
    add_main_heading(doc, "4.9 Route Generation Module")
    add_hint_paragraph(doc, 
        "Generating alternative vehicular paths requires high-performance spatial graph routing engines. This section details the OpenRouteService API integration."
    )
    add_body_paragraph(doc, 
        "The Route Generation module interfaces with the OpenRouteService (ORS) Directions API. Upon receiving origin and destination coordinates, the module constructs an HTTP POST request targeting the /v2/directions/driving-car endpoint with alternative_routes enabled. ORS returns multiple distinct graph trajectories formatted as GeoJSON feature collections, including distance, base duration, and coordinates."
    )

    scr_routes = (
        "[SCREENSHOT PLACEHOLDER: Figure 4.4 Candidate Alternative Route Display]\n"
        "Visible Components: Multi-path polyline rendering, distance/duration badges, primary vs secondary corridor highlights."
    )
    add_figure_custom(
        doc,
        "Figure 4.4 Candidate Alternative Route Display [INSERT SCREENSHOT HERE]",
        scr_routes,
        "Figure 4.4 illustrates candidate alternative trajectories rendered on the Leaflet canvas. Purpose: Presents commuter with viable path choices generated by OpenRouteService."
    )

    # 4.10 Traffic Data Collection
    add_main_heading(doc, "4.10 Traffic Data Collection")
    add_hint_paragraph(doc, 
        "Sensing real-world traffic states requires automated periodic telemetry ingestion. This section outlines the traffic data harvesting module."
    )
    add_body_paragraph(doc, 
        "The Traffic Data Collection module operates as an automated background daemon scheduled via APScheduler. Every 15 minutes, the collector queries the TomTom Traffic Flow API for monitored road segments across major metropolitan hubs (including Gandhipuram, RS Puram, Coimbatore Junction, Peelamedu, Airport Corridor, Saravanampatti, Singanallur, and Ukkadam). For each corridor segment, the module retrieves current vehicular speed, free-flow velocity, observed traversal duration, and free-flow duration, persisting them into the traffic_data MySQL table."
    )
    # 4.11 Weather Data Collection
    add_main_heading(doc, "4.11 Weather Data Collection")
    add_hint_paragraph(doc, 
        "Atmospheric conditions exert direct physical influence over road friction, visibility, and vehicular flow rates. This section details the Open-Meteo weather integration."
    )
    add_body_paragraph(doc, 
        "The Weather Data Collection module queries the Open-Meteo Forecast and Historical Weather API without requiring proprietary API keys. The module queries coordinates along candidate route corridors to retrieve hourly and 15-minute weather metrics: air temperature (°C), precipitation (mm), relative humidity (%), surface air pressure (hPa), and wind speed (km/h). A specialized utility parses these values and computes an aggregate Weather Risk Score (0.0 to 1.0) and assigns categorical classifications ('Low', 'Moderate', 'High', 'Severe')."
    )

    scr_weather = (
        "[SCREENSHOT PLACEHOLDER: Figure 4.5 Weather and Environmental Impact Panel]\n"
        "Visible Components: Current temperature tile, precipitation gauge, wind speed, atmospheric risk badge, corridor weather alerts."
    )
    add_figure_custom(
        doc,
        "Figure 4.5 Weather and Environmental Impact Panel [INSERT SCREENSHOT HERE]",
        scr_weather,
        "Figure 4.5 illustrates the environmental analytics card displaying meteorological conditions along candidate paths. Purpose: Informs commuters of weather-related travel risks."
    )

    # 4.12 Historical Dataset Processing
    add_main_heading(doc, "4.12 Historical Dataset Processing")
    add_hint_paragraph(doc, 
        "Deep time-series forecasting requires structured, chronologically continuous sensor archives. This section describes the dataset composition and processing procedures."
    )
    add_body_paragraph(doc, 
        "The historical dataset utilized for training PatchTST comprises traffic telemetry collected across 41 unique road segments in the Coimbatore metropolitan region. The archive contains 1,992 total traffic observation records (spanning 494 real TomTom observations collected between August 25 and August 31, 2026, augmented with 1,440 synthetic corridor records generated by the RouteIQ telemetry simulation engine for training augmentation, alongside 265 synchronized Open-Meteo weather observations). Strict data labeling policies ensure that synthetic telemetry is used exclusively for training weight updates and is never introduced into validation or test partitions."
    )

    # 4.13 Data Preprocessing
    add_main_heading(doc, "4.13 Data Preprocessing")
    add_hint_paragraph(doc, 
        "Raw sensor streams exhibit missing intervals, anomalies, and multi-scale feature ranges. This section describes the cleaning, imputation, and scaling pipeline."
    )
    add_body_paragraph(doc, 
        "Preprocessing establishes data consistency prior to neural tensor ingestion. Timestamps are aligned to regular 15-minute intervals. Missing sensor readings are imputed using forward-fill for gaps under one hour and linear interpolation for longer intervals. To eliminate data leakage, a Scikit-Learn StandardScaler is fitted strictly on the training partition (70% chronological split, comprising 1,366 records), computing feature means and standard deviations. The validation partition (15%, 293 records) and test partition (15%, 293 records) are transformed using the pre-fitted training scaler parameters."
    )

    # 4.14 Feature Engineering
    add_main_heading(doc, "4.14 Feature Engineering")
    add_hint_paragraph(doc, 
        "Extracting expressive temporal, physical, and environmental representations enhances machine learning accuracy. This section details the twelve primary features engineered for time-series forecasting."
    )
    add_body_paragraph(doc, 
        "Feature engineering derives twelve distinct continuous and cyclic features for every 15-minute observation step: observed vehicular speed (speed_kmh), free-flow speed, current travel time, free-flow travel time, temperature, precipitation, relative humidity, wind speed, cyclic sine-encoded hour (sin(2pi * hour / 24)), cyclic cosine-encoded hour (cos(2pi * hour / 24)), day of the week (0 to 6), and a binary weekend indicator. Furthermore, the Traffic Congestion Index (TCI) is formulated as: TCI = current_travel_time / free_flow_travel_time, providing an invariant dimensionless metric of delay."
    )

    # 4.15 PatchTST Implementation
    add_main_heading(doc, "4.15 PatchTST Implementation")
    add_hint_paragraph(doc, 
        "Implementing modern transformer architectures in PyTorch requires customized patching, channel-independent attention, and linear heads. This section details the PatchTST implementation."
    )
    add_body_paragraph(doc, 
        "The PatchTST architecture is implemented in PyTorch as a custom nn.Module. The model accepts input tensors of dimension [Batch, context_length=96, num_features=12]. The patching layer extracts 12 patches of length 16 with a stride of 8 steps across each feature independently. A linear projection layer projects each 16-dimensional patch into a 128-dimensional embedding, summed with learnable 1D positional encodings. Three stacked TransformerEncoderLayer modules (configured with 8 attention heads, hidden dimension 512, and dropout 0.1) process the patch sequence. A linear prediction head flattens the resulting tensor and projects it to the 36-step forecast horizon."
    )

    # 4.16 Future Traffic Prediction
    add_main_heading(doc, "4.16 Future Traffic Prediction")
    add_hint_paragraph(doc, 
        "Projecting traffic conditions across extended time horizons enables proactive travel planning. This section details the 9-hour forecasting workflow, focusing on the 8:00 AM to 5:00 PM validation cycle."
    )
    add_body_paragraph(doc, 
        "The future traffic prediction engine is deployed to solve the operational commuter challenge: estimating 5:00 PM evening peak conditions using morning telemetry available up to 8:00 AM. This corresponds to an exact 36-step lookahead horizon (9 hours at 15-minute intervals). At 8:00 AM IST, the automated scheduler constructs a 96-step context tensor for each monitored corridor and executes PatchTST forward inference. The resulting predictions (predicted speed, predicted travel duration, and predicted TCI at step 36) are stored in the database. At 5:00 PM IST, actual ground-truth telemetry is collected, and prediction error metrics are automatically computed."
    )

    scr_pred = (
        "[SCREENSHOT PLACEHOLDER: Figure 4.6 PatchTST Congestion Forecasting Visualizer]\n"
        "Visible Components: 9-hour temporal timeline chart, predicted speed curves, confidence intervals, TCI congestion heat bars."
    )
    add_figure_custom(
        doc,
        "Figure 4.6 PatchTST 9-Hour Congestion Forecasting Visualizer [INSERT SCREENSHOT HERE]",
        scr_pred,
        "Figure 4.6 displays the interactive time-series forecasting graph rendering projected corridor speeds up to 9 hours ahead. Purpose: Visualizes future congestion curves."
    )

    # 4.17 CatBoost Implementation
    add_main_heading(doc, "4.17 CatBoost Implementation")
    add_hint_paragraph(doc, 
        "Evaluating candidate routes demands a resilient decision-tree model capable of processing heterogeneous numeric and categorical features. This section details the CatBoost route recommendation implementation."
    )
    add_body_paragraph(doc, 
        "The route recommendation engine is implemented using CatBoostRegressor and CatBoostRanker. For each candidate route generated by OpenRouteService, a feature vector is constructed containing 34 numeric variables (including distance, duration, waypoints, PatchTST forecasted speed, predicted TCI, weather risk metrics, and active event indicators) and 2 categorical variables (weather_risk_level and landslide_severity). The CatBoost model utilizes symmetric oblivious trees with a maximum depth of 6, trained over 500 iterations with RMSE loss and L2 regularization to prevent overfitting."
    )

    # 4.18 Route Recommendation
    add_main_heading(doc, "4.18 Route Recommendation")
    add_hint_paragraph(doc, 
        "Translating multi-attribute model outputs into definitive commuter advice requires transparent scoring and ranking. This section describes the route recommendation logic."
    )
    add_body_paragraph(doc, 
        "Once CatBoost infers composite utility scores for all candidate paths, the Route Recommendation module executes post-processing validation. Corridors flagged with administrative road closures (is_blocked = True) are assigned an infinite penalty score, immediately disqualifying them from recommendation. The remaining viable paths are sorted in descending order of their CatBoost utility score. The candidate achieving the highest score is tagged as the Recommended Route and decorated with a prominent 'RouteIQ Recommended' badge on the user interface."
    )

    scr_recomm = (
        "[SCREENSHOT PLACEHOLDER: Figure 4.7 CatBoost Comparative Route Ranking]\n"
        "Visible Components: Recommended path highlight card, CatBoost score breakdown, time saved indicator, weather advisory tag."
    )
    add_figure_custom(
        doc,
        "Figure 4.7 CatBoost Comparative Route Ranking and Recommendation [INSERT SCREENSHOT HERE]",
        scr_recomm,
        "Figure 4.7 illustrates the recommended path selection card and ranking breakdown. Purpose: Explains the algorithmic justification behind the optimal route selection."
    )

    # 4.19 Alternative Route Comparison
    add_main_heading(doc, "4.19 Alternative Route Comparison")
    add_hint_paragraph(doc, 
        "Providing transparent trade-off analysis empowers commuters to make informed travel decisions. This section details the alternative route comparison matrix."
    )
    add_body_paragraph(doc, 
        "The Alternative Route Comparison component compiles a side-by-side trade-off matrix evaluating all candidate trajectories. Commuters can inspect total distance (km), standard duration vs predicted duration under traffic, forecasted congestion index (TCI), weather risk levels, and active disruption tags. Interactive toggles allow commuters to highlight individual candidate paths on the Leaflet map canvas."
    )

    # 4.20 Dashboard
    add_main_heading(doc, "4.20 Dashboard")
    add_hint_paragraph(doc, 
        "The commuter dashboard consolidates spatial, temporal, predictive, and meteorological analytics into a unified interface. This section describes the dashboard layout."
    )
    add_body_paragraph(doc, 
        "The RouteIQ commuter dashboard synthesizes all platform capabilities into a cohesive single-page experience. The layout features a collapsible left-hand configuration panel for trip parameters, a central high-resolution Leaflet map canvas, an expandable bottom drawer displaying the PatchTST forecasting timeline, and a right-hand sidebar presenting CatBoost route evaluations, comparative trade-offs, and weather advisories."
    )
    # 4.21 Admin Module
    add_main_heading(doc, "4.21 Admin Module")
    add_hint_paragraph(doc, 
        "Privileged administration ensures operational supervision, data integrity, and disruption event logging. This section describes the administrative module."
    )
    add_body_paragraph(doc, 
        "The Admin Module provides an authenticated console accessible exclusively to users with administrator privileges. The portal exposes three management panels: Incident Management (for logging road work, accidents, and temporary blockages), Model Governance (for monitoring PatchTST validation metrics and triggering background retraining), and Telemetry Inspection (for tracking automated collector health and API quota status)."
    )

    scr_admin = (
        "[SCREENSHOT PLACEHOLDER: Figure 4.8 Administrative Incident Control Panel]\n"
        "Visible Components: Incident logging form, active road blockages table, model retraining trigger, live 8AM->5PM metrics."
    )
    add_figure_custom(
        doc,
        "Figure 4.8 Administrative Incident and Road Disruption Control Panel [INSERT SCREENSHOT HERE]",
        scr_admin,
        "Figure 4.8 displays the administrative console for managing road disruptions and tracking machine learning accuracy. Purpose: Empowers administrators to maintain system integrity."
    )

    # 4.22 Exceptional Road Condition Handling
    add_main_heading(doc, "4.22 Exceptional Road Condition Handling")
    add_hint_paragraph(doc, 
        "Unforeseen incidents like construction, landslides, waterlogging, or festival assemblies alter corridor throughput dramatically. This section details how RouteIQ handles exceptional road conditions."
    )
    add_body_paragraph(doc, 
        "Exceptional road conditions are incorporated through structured administrative updates or verified municipal feeds. When an administrator logs an event (specifying event type, coordinates, radius, severity, and start/end timestamps), the record is persisted into admin_updates. During route evaluation, the backend spatial service checks whether any segment of a candidate route intersects an active incident zone. If a complete blockage is flagged (is_blocked = True), the corridor is penalized with an infinite cost and excluded from recommendations. If partial disruption is indicated, delay multipliers are applied to transit time estimates."
    )

    # 4.23 API Integration
    add_main_heading(doc, "4.23 API Integration")
    add_hint_paragraph(doc, 
        "External web services supply essential geographic, routing, weather, and traffic data. This section summarizes the operational roles and technical endpoints of all external APIs."
    )
    add_body_paragraph(doc, 
        "RouteIQ coordinates four distinct external REST APIs, each selected for high data fidelity and compliance with open-source development standards:"
    )

    api_table_data = [
        ["OpenStreetMap (Nominatim)", "https://nominatim.openstreetmap.org/search", "Forward geocoding; converts place names to WGS84 coordinates."],
        ["OpenRouteService (ORS)", "https://api.openrouteservice.org/v2/directions", "Generates alternative driving paths, polylines, and base durations."],
        ["Open-Meteo Weather API", "https://api.open-meteo.com/v1/forecast", "Retrieves temperature, precipitation, wind speed, and humidity."],
        ["TomTom Traffic Flow API", "https://api.tomtom.com/traffic/services/4/flowSegmentData", "Ingests live traffic speeds, free-flow speeds, and traversal times."]
    ]
    add_table_custom(
        doc,
        "Table 4.1 External API Specifications and Operational Roles",
        ["API Service", "Endpoint URL Pattern", "Operational Role in RouteIQ"],
        api_table_data,
        col_widths=[2.0, 2.7, 2.5]
    )

    # 4.24 Database Operations
    add_main_heading(doc, "4.24 Database Operations")
    add_hint_paragraph(doc, 
        "Data persistence requires parameterized queries, transaction safety, and clean connection pooling. This section outlines database access operations."
    )
    add_body_paragraph(doc, 
        "Database interactions are encapsulated within repository classes utilizing PyMySQL and connection pooling. All queries utilize parameterized SQL statements to eliminate SQL injection vulnerabilities. Write operations across multi-table updates (such as saving a search record alongside multiple candidate routes and predictions) are wrapped in atomic database transactions, ensuring rollback on failure."
    )

    # 4.25 Security Considerations
    add_main_heading(doc, "4.25 Security Considerations")
    add_hint_paragraph(doc, 
        "Securing user data and API endpoints is critical for production deployment. This section outlines the cybersecurity measures implemented across the application."
    )
    add_body_paragraph(doc, 
        "RouteIQ incorporates defense-in-depth security mechanisms: bcrypt cryptographic hashing for passwords, signed JWT tokens with 24-hour expiration for stateless session authorization, Cross-Origin Resource Sharing (CORS) whitelisting to restrict API invocation to trusted frontend origins, input sanitization to prevent Cross-Site Scripting (XSS), and parameterized queries to mitigate SQL injection."
    )

    # 4.26 Important Code Snippets
    add_main_heading(doc, "4.26 Important Code Snippets")
    add_hint_paragraph(doc, 
        "Examining core implementation routines illustrates the programmatic realization of system capabilities. This section presents annotated code snippets across frontend, backend, and machine learning components."
    )

    # Snippet 1: Nominatim Geocoding
    add_code_block(
        doc,
        "The following Python method illustrates forward geocoding resolution using the OpenStreetMap Nominatim REST endpoint with caching and error handling:",
        "def geocode_location(place_name: str) -> dict:\n"
        "    url = 'https://nominatim.openstreetmap.org/search'\n"
        "    params = {'q': place_name, 'format': 'json', 'limit': 1}\n"
        "    headers = {'User-Agent': 'RouteIQ-Academic-Project/1.0'}\n"
        "    response = requests.get(url, params=params, headers=headers, timeout=5)\n"
        "    if response.status_code == 200 and len(response.json()) > 0:\n"
        "        data = response.json()[0]\n"
        "        return {'lat': float(data['lat']), 'lng': float(data['lon'])}\n"
        "    return None",
        "The geocode_location routine queries Nominatim, validates the HTTP response, and extracts standardized WGS84 coordinate pairs for subsequent route generation."
    )

    # Snippet 2: OpenRouteService Route Retrieval
    add_code_block(
        doc,
        "The following snippet demonstrates route generation using the OpenRouteService Directions API with alternative paths enabled:",
        "def fetch_routes_ors(start_coords: tuple, end_coords: tuple) -> list:\n"
        "    url = 'https://api.openrouteservice.org/v2/directions/driving-car/geojson'\n"
        "    body = {'coordinates': [list(start_coords), list(end_coords)], 'alternative_routes': {'target_count': 3}}\n"
        "    headers = {'Authorization': ORS_API_KEY, 'Content-Type': 'application/json'}\n"
        "    response = requests.post(url, json=body, headers=headers, timeout=8)\n"
        "    if response.status_code == 200:\n"
        "        return response.json().get('features', [])\n"
        "    return []",
        "This function dispatches origin and destination coordinates to OpenRouteService, extracting candidate polyline geometries and path distance/duration summaries."
    )

    # Snippet 3: PatchTST Patching Layer
    add_code_block(
        doc,
        "The following PyTorch snippet details the sub-series patch extraction and linear projection layer of PatchTST:",
        "class PatchLayer(nn.Module):\n"
        "    def __init__(self, patch_len=16, stride=8, d_model=128):\n"
        "        super().__init__()\n"
        "        self.patch_len, self.stride = patch_len, stride\n"
        "        self.proj = nn.Linear(patch_len, d_model)\n"
        "    def forward(self, x):\n"
        "        # x: [Batch * M, Context_Len=96]\n"
        "        patches = x.unfold(dimension=-1, size=self.patch_len, step=self.stride)\n"
        "        return self.proj(patches) # [Batch * M, 12, 128]",
        "The PatchLayer module unfolds the continuous 96-step time-series tensor into overlapping 16-step patches and linearly projects each patch into the transformer embedding space."
    )

    # Snippet 4: CatBoost Route Scoring
    add_code_block(
        doc,
        "The following Python snippet illustrates CatBoost feature matrix preparation and route score inference:",
        "def evaluate_candidate_routes(candidate_routes: list, model: CatBoostRegressor) -> list:\n"
        "    feature_rows = [build_route_feature_vector(route) for route in candidate_routes]\n"
        "    pool = Pool(data=feature_rows, cat_features=['weather_risk_level', 'landslide_severity'])\n"
        "    scores = model.predict(pool)\n"
        "    for idx, route in enumerate(candidate_routes):\n"
        "        route['catboost_score'] = float(scores[idx])\n"
        "        if route.get('road_blocked', False):\n"
        "            route['catboost_score'] = -9999.0\n"
        "    return sorted(candidate_routes, key=lambda r: r['catboost_score'], reverse=True)",
        "This routine assembles multi-attribute feature vectors, invokes the pre-trained CatBoost model, applies road blockage overrides, and ranks candidate paths."
    )

    # 4.27 Concluding Remarks
    add_main_heading(doc, "4.27 Concluding Remarks")
    add_hint_paragraph(doc, 
        "This section concludes the system implementation chapter, summarizing the technical achievements and transitioning to system verification."
    )
    add_body_paragraph(doc, 
        "This chapter detailed the complete implementation of RouteIQ. The development environment, React.js frontend interface, Flask REST microservice architecture, and normalized MySQL schemas were thoroughly described. The data ingestion workflows spanning TomTom traffic feeds and Open-Meteo weather streams were explained alongside the preprocessing, scaling, and feature engineering pipelines. The concrete PyTorch implementation of PatchTST for 9-hour forecasting and CatBoost for multi-attribute route evaluation were detailed alongside security controls and core source code routines. Chapter 5 presents the comprehensive testing methodologies, quantitative evaluation metrics, and validation results."
    )
