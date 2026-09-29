import docx
from report_generator.styles import (
    add_chapter_heading, add_main_heading, add_sub_heading,
    add_hint_paragraph, add_body_paragraph, add_bullet_point,
    add_figure_custom
)

def build_chapter_1(doc):
    add_chapter_heading(doc, "CHAPTER 1\nINTRODUCTION")

    # 1.1 Project Overview
    add_main_heading(doc, "1.1 Project Overview")
    add_hint_paragraph(doc, 
        "Modern urban transportation infrastructure faces intense pressure from exponential vehicular growth and stochastic traffic events. "
        "This section outlines the overarching domain, high-level objectives, and core architectural philosophy behind the RouteIQ system."
    )
    add_body_paragraph(doc, 
        "RouteIQ is an intelligent web-based platform designed to address urban vehicular congestion through advanced deep-learning "
        "traffic forecasting and multi-attribute route recommendation. Unlike conventional navigation platforms that depend exclusively "
        "on instantaneous traffic measurements or static road network geometries, the proposed RouteIQ platform anticipates road network "
        "conditions hours into the future. By synchronizing historical traffic patterns, current sensor feeds, meteorological dynamics, "
        "and administrative road disruption advisories, the platform determines the most reliable and efficient paths across metropolitan corridors."
    )
    add_body_paragraph(doc, 
        "The system operates through an end-to-end computational pipeline that bridges spatial route generation with artificial intelligence. "
        "Commuters provide trip parameters, including origin, destination, planned departure date, and target time. Using spatial geocoding "
        "and routing engines, RouteIQ computes viable corridor alternatives and extracts comprehensive road telemetry. These candidates "
        "are evaluated using a deep-learning time-series forecasting model (PatchTST) to predict future corridor speeds and traffic congestion indices, "
        "followed by a gradient-boosted route recommendation engine (CatBoost) that ranks alternatives based on travel time, distance, predicted bottlenecks, "
        "weather severity, and physical road blockages."
    )

    # 1.2 Background
    add_main_heading(doc, "1.2 Background")
    add_hint_paragraph(doc, 
        "A rigorous study of vehicular movement requires an understanding of how traffic conditions evolve across spatial networks and temporal dimensions. "
        "This section presents the technological and socioeconomic background of modern urban traffic management."
    )
    add_body_paragraph(doc, 
        "Over the past three decades, rapid metropolitan expansion, population centralization, and increased private vehicle ownership have "
        "outpaced urban road capacity expansion. Urban transportation networks are characterized by non-linear physical dynamics where localized "
        "disruptions—such as intersection signal failures, minor collisions, weather disturbances, or sudden volume surges—rapidly propagate across "
        "interconnected corridors. These cascading bottlenecks induce severe delays, elevated vehicular emissions, heightened fuel consumption, "
        "and diminished economic productivity across modern cities."
    )
    add_body_paragraph(doc, 
        "Early attempts at computerized navigation utilized static graph search algorithms, such as Dijkstra's algorithm and the A* heuristic search, "
        "operating over pre-computed road network edge weights representing physical distances or statutory speed limits. While computationally "
        "tractable, these systems ignored real-time road conditions. The subsequent generation of GPS-enabled navigation systems incorporated live "
        "telemetry from floating car data (FCD) and loop detectors. However, real-time reactive routing exhibits a fundamental systemic limitation: "
        "routes are computed based on conditions existing at the moment of search, failing to account for how traffic will evolve during transit. "
        "Consequently, vehicles dispatched onto an open artery often encounter severe gridlock upon arrival at intermediate transit hubs. RouteIQ is "
        "formulated to overcome this reactive bottleneck through forward-looking predictive intelligence."
    )

    # 1.3 Problem Statement
    add_main_heading(doc, "1.3 Problem Statement")
    add_hint_paragraph(doc, 
        "Identifying the specific computational and algorithmic deficiencies of prevailing route guidance platforms is essential for designing an effective solution. "
        "This section formally defines the problem addressed by the proposed RouteIQ system."
    )
    add_body_paragraph(doc, 
        "Existing commercial and open-source navigation systems operate predominantly in a reactive paradigm. When a user requests a route for a future "
        "time or undertakes a trip spanning significant travel time, conventional systems compute recommendations using either historical static averages "
        "or current instantaneous speeds. This approach causes significant errors because urban traffic states are highly non-stationary and non-linear, "
        "governed by cyclic commuter patterns, weather events, and localized disruptions."
    )
    add_body_paragraph(doc, 
        "Furthermore, existing platforms often recommend identical 'least-duration' corridors to large commuter volumes simultaneously, inadvertently "
        "transferring congestion from primary arterial roads to secondary residential thoroughfares. Furthermore, these systems frequently treat route "
        "selection as a single-objective optimization problem focusing strictly on instantaneous travel time or physical distance, while ignoring "
        "compound multi-criteria dimensions such as adverse meteorological hazards, corridor bottleneck volatility, and temporary administrative "
        "road restrictions. Therefore, a comprehensive system is required that simultaneously models long-horizon temporal dependencies, multi-scale "
        "environmental contexts, and diverse route trade-offs to deliver robust, proactive route recommendations."
    )

    # 1.4 Need for the Project
    add_main_heading(doc, "1.4 Need for the Project")
    add_hint_paragraph(doc, 
        "The socio-economic and technological incentives for deploying predictive traffic analytics are substantial. This section outlines the imperative "
        "need for developing an intelligent traffic forecasting and route optimization platform."
    )
    add_body_paragraph(doc, 
        "The necessity of developing RouteIQ stems from three fundamental urban mobility challenges:"
    )
    add_bullet_point(doc, "Proactive Congestion Mitigation: ", 
        "By anticipating traffic states up to nine hours ahead, urban commuters can schedule departures and select resilient travel corridors prior to the onset of peak gridlock, evening out traffic distribution across metropolitan networks."
    )
    add_bullet_point(doc, "Environmental and Economic Sustainability: ", 
        "Prolonged idling and stop-and-go driving cycles in congested corridors contribute disproportionately to urban carbon footprints and fuel waste. Recommending stable, free-flowing corridors directly reduces vehicular emissions and commuter travel expenditures."
    )
    add_bullet_point(doc, "Weather and Incident Resilience: ", 
        "Adverse meteorological conditions such as intense precipitation and high winds reduce road friction and visibility, exacerbating transit delays. RouteIQ provides multi-factor route evaluation that penalizes hazard-prone corridors and incorporates administrative road closure data."
    )

    # 1.5 Objectives
    add_main_heading(doc, "1.5 Objectives")
    add_hint_paragraph(doc, 
        "The project is structured around clear, measurable, and academically rigorous engineering goals. This section delineates the core objectives of the RouteIQ system."
    )
    add_body_paragraph(doc, 
        "The primary objectives of the RouteIQ project encompass:"
    )
    add_bullet_point(doc, "Intelligent Spatial Routing: ", 
        "To implement automated geocoding and alternative corridor generation between user-specified origins and destinations using OpenStreetMap and OpenRouteService APIs."
    )
    add_bullet_point(doc, "Multi-Source Telemetry Ingestion: ", 
        "To establish automated data collection mechanisms for ingesting live traffic speeds, travel durations, and historical sensor telemetry alongside real-time atmospheric data from Open-Meteo."
    )
    add_bullet_point(doc, "Deep-Learning Traffic Forecasting: ", 
        "To develop and train a Patch Time Series Transformer (PatchTST) architecture capable of predicting multi-step corridor speeds and Traffic Congestion Indices (TCI) up to 36 steps (9 hours) ahead."
    )
    add_bullet_point(doc, "Multi-Attribute Route Recommendation: ", 
        "To construct a CatBoost gradient-boosted decision model that synthesizes predicted congestion, physical distance, duration, meteorological risk scores, and event indicators into an interpretable route score."
    )
    add_bullet_point(doc, "Administrative Disruption Management: ", 
        "To provide a dedicated administrative interface for introducing verified temporary road restrictions, construction activities, and hazard notices that dynamically alter routing recommendations."
    )
    add_bullet_point(doc, "Interactive Web Visualization: ", 
        "To design an intuitive, responsive frontend dashboard using React.js and Tailwind CSS that visualizes routes, congestion states, comparative metrics, and environmental parameters."
    )

    # 1.6 Scope of the Project
    add_main_heading(doc, "1.6 Scope of the Project")
    add_hint_paragraph(doc, 
        "Defining the functional and operational boundaries of the software ensures realistic development and focused evaluation. This section describes the scope and operational assumptions of RouteIQ."
    )
    add_body_paragraph(doc, 
        "The functional scope of RouteIQ encompasses the development of a complete web-based decision-support system tested across metropolitan corridors "
        "(with specific empirical validation across eight major traffic hubs and corridors in Coimbatore, Tamil Nadu). The platform provides user authentication, "
        "interactive origin-destination selection, automated geocoding, multi-route spatial rendering, real-time meteorological feature extraction, "
        "PatchTST-driven 9-hour predictive inference, CatBoost route scoring, and administrative hazard logging. The operational scope focuses on "
        "passenger and light vehicular urban road transit under civilian driving conditions."
    )
    add_body_paragraph(doc, 
        "The system explicitly excludes real-time hardware-in-the-loop traffic signal control, automated connected-vehicle guidance, and in-vehicle CAN bus "
        "telemetry monitoring. In scenarios where physical road conditions alter abruptly due to unmonitored emergencies, the platform relies on administrator "
        "incident logging rather than autonomous satellite or computer vision detection."
    )

    # 1.7 Significance of the Project
    add_main_heading(doc, "1.7 Significance of the Project")
    add_hint_paragraph(doc, 
        "The intellectual and practical contributions of the system highlight its value within applied computer science and intelligent transportation. "
        "This section details the academic and practical significance of RouteIQ."
    )
    add_body_paragraph(doc, 
        "The significance of RouteIQ lies in its synthesis of modern transformer-based time-series forecasting with robust gradient-boosted tabular ranking. "
        "While standard transformers applied to time-series often encounter severe computational bottlenecks and overfitting on noisy temporal signals, "
        "RouteIQ leverages channel-independent sub-series patching (PatchTST) to capture localized temporal patterns and long-range semantic dependencies "
        "with reduced computational overhead. Furthermore, the combination of PatchTST with CatBoost decouples the time-series forecasting problem from "
        "the multi-attribute decision-making problem, ensuring modularity, transparent feature attribution, and flexible operational deployment."
    )

    # 1.8 Project Workflow
    add_main_heading(doc, "1.8 Project Workflow")
    add_hint_paragraph(doc, 
        "The operational lifecycle of RouteIQ spans user query capture, spatial expansion, multi-source feature extraction, deep forecasting, and decision ranking. "
        "This section describes the end-to-end execution flow of the system."
    )
    add_body_paragraph(doc, 
        "The operational flow begins when an authenticated commuter inputs origin and destination place names, accompanied by departure date and target time. "
        "The system coordinates geocoding, spatial graph expansion, environmental querying, temporal feature synthesis, transformer forecasting, and decision tree ranking, "
        "ultimately presenting an ordered dashboard of candidate paths."
    )

    workflow_visual = (
        "+-----------------------------------------------------------------------------------------+\n"
        "|                             ROUTEIQ END-TO-END WORKFLOW                                 |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "  [User Input: Source, Destination, Date, Target Time]\n"
        "                         |\n"
        "                         v\n"
        "  [Geocoding Engine: OpenStreetMap / Nominatim] ---> Coordinates (Lat, Lng)\n"
        "                         |\n"
        "                         v\n"
        "  [Spatial Router: OpenRouteService API] ----------> Candidate Corridors & Waypoints\n"
        "                         |\n"
        "                         v\n"
        "  [Context Aggregator: Open-Meteo & TomTom API] ---> Weather & Current Traffic Telemetry\n"
        "                         |\n"
        "                         v\n"
        "  [Feature Pipeline & StandardScaler] -------------> 12 Temporal & Environmental Features\n"
        "                         |\n"
        "                         v\n"
        "  [PatchTST Deep Transformer (9-Hr Forecast)] -----> Predicted Speed, Travel Time & TCI\n"
        "                         |\n"
        "                         v\n"
        "  [CatBoost Decision Tree Recommender] ------------> Multi-Criteria Scoring & Ranking\n"
        "                         |\n"
        "                         v\n"
        "  [Interactive React Dashboard & Leaflet Map] -----> Recommended vs Alternative Paths\n"
        "+-----------------------------------------------------------------------------------------+"
    )
    add_figure_custom(
        doc,
        "Figure 1.1 High-Level Architectural Flow of RouteIQ",
        workflow_visual,
        "The workflow diagram illustrates the sequential propagation of commuter input data across spatial geocoding, corridor routing, "
        "multi-source telemetry ingestion, PatchTST time-series inference, CatBoost multi-attribute evaluation, and final visual dashboard rendering."
    )

    # 1.9 Technologies Used
    add_main_heading(doc, "1.9 Technologies Used")
    add_hint_paragraph(doc, 
        "Developing a robust, production-grade intelligent transportation platform requires a scalable, maintainable, and modern software stack. "
        "This section reviews the core programming frameworks, libraries, database engines, and external APIs utilized in RouteIQ."
    )
    add_body_paragraph(doc, 
        "The RouteIQ technology stack has been selected to deliver high performance, modularity, and rapid prototyping capabilities:"
    )
    add_bullet_point(doc, "User Interface Tier: ", 
        "React.js (v18) paired with Tailwind CSS for building a highly responsive, modern, single-page application dashboard featuring interactive mapping controls and dynamic data visualizers."
    )
    add_bullet_point(doc, "Application Server Tier: ", 
        "Python Flask microframework providing modular RESTful API endpoints, cross-origin resource sharing (CORS), secure session handling, and background task dispatching."
    )
    add_bullet_point(doc, "Relational Persistence Tier: ", 
        "MySQL relational database providing ACID-compliant storage for commuter accounts, query histories, spatial trajectories, telemetry logs, and administrator updates."
    )
    add_bullet_point(doc, "Spatial and Routing Services: ", 
        "OpenStreetMap (OSM) via Nominatim for geographic entity resolution and OpenRouteService (ORS) for high-performance isochrone and path topology computation."
    )
    add_bullet_point(doc, "Meteorological Services: ", 
        "Open-Meteo API for historical, current, and forecasted atmospheric parameters including precipitation, temperature, relative humidity, and wind velocity."
    )
    add_bullet_point(doc, "Deep Learning Framework: ", 
        "PyTorch (v2.0+) implementing the Patch Time Series Transformer (PatchTST) with customized patching, channel-independent multi-head self-attention, and projection layers."
    )
    add_bullet_point(doc, "Gradient Boosting Library: ", 
        "CatBoost library utilized for tabular route evaluation, leveraging symmetric decision tree ensembles and efficient categorical feature encoding."
    )

    # 1.10 Concluding Remarks
    add_main_heading(doc, "1.10 Concluding Remarks")
    add_hint_paragraph(doc, 
        "This section synthesizes the introductory concepts and sets the stage for the detailed requirements and system analysis discussed in the following chapter."
    )
    add_body_paragraph(doc, 
        "This chapter presented the foundational overview, background, problem statement, and scope of RouteIQ. The systemic limitations of reactive "
        "navigation paradigms were established, motivating the development of a hybrid deep-learning and gradient-boosted decision framework. "
        "The project objectives, end-to-end workflow, and primary software technologies were outlined. The detailed examination of existing systems, "
        "requirements specifications, and feasibility analyses will be addressed in Chapter 2."
    )
