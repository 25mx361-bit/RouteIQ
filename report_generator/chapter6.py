import docx
from report_generator.styles import (
    add_chapter_heading, add_main_heading, add_sub_heading,
    add_hint_paragraph, add_body_paragraph, add_bullet_point
)

def build_chapter_6(doc):
    add_chapter_heading(doc, "CHAPTER 6\nCONCLUSION AND FUTURE ENHANCEMENTS")

    # 6.1 Introduction
    add_main_heading(doc, "6.1 Introduction")
    add_hint_paragraph(doc, 
        "Concluding an engineering dissertation requires synthesizing research achievements, evaluating deliverables against original objectives, "
        "and charting future research trajectories. This section introduces the concluding review of the RouteIQ project."
    )
    add_body_paragraph(doc, 
        "This chapter synthesizes the technical achievements, research insights, and software engineering outcomes realized through the development "
        "of RouteIQ. The chapter reviews the core problem addressed, details the architectural and algorithmic contributions, summarizes system performance, "
        "evaluates key operational limitations, outlines promising future research extensions, and provides final concluding reflections."
    )

    # 6.2 Summary of the Work
    add_main_heading(doc, "6.2 Summary of the Work")
    add_hint_paragraph(doc, 
        "Summarizing the comprehensive development lifecycle clarifies how the initial technical vision was executed. This section recaps the major phases of the project."
    )
    add_body_paragraph(doc, 
        "RouteIQ was conceptualized, designed, and implemented to overcome the inherent limitations of reactive vehicular navigation systems. "
        "The project united spatial routing engines, real-time meteorological services, deep-learning time-series forecasting, and gradient-boosted tabular ranking "
        "into a responsive web platform. The frontend was engineered using React.js and Tailwind CSS, supported by Leaflet.js mapping canvases. "
        "The application tier was built with Python Flask and MySQL. A two-stage machine learning pipeline was constructed: PatchTST was trained to "
        "forecast corridor speeds and congestion indices across a 9-hour lookahead horizon, and CatBoost was trained to evaluate candidate routes based on "
        "predicted delays, physical distances, weather risks, and administrative incident notices."
    )

    # 6.3 Major Contributions
    add_main_heading(doc, "6.3 Major Contributions")
    add_hint_paragraph(doc, 
        "Highlighting core contributions underscores the intellectual and engineering value of the project. This section articulates the primary innovations delivered by RouteIQ."
    )
    add_body_paragraph(doc, 
        "The primary contributions of this project encompass:"
    )
    add_bullet_point(doc, "Decoupled Two-Stage Intelligence Pipeline: ", 
        "Successfully separating time-series corridor congestion forecasting (PatchTST) from multi-attribute route evaluation (CatBoost), ensuring modularity, interpretability, and robust performance."
    )
    add_bullet_point(doc, "Long-Horizon Traffic Forecasting via PatchTST: ", 
        "Demonstrated the application of sub-series patching and channel-independent self-attention to urban vehicular traffic telemetry, projecting conditions up to 9 hours ahead (e.g., forecasting 5:00 PM peak traffic from 8:00 AM data)."
    )
    add_bullet_point(doc, "Integrated Weather-Aware Routing: ", 
        "Synthesized real-time and forecasted atmospheric parameters (precipitation, temperature, wind speed) from Open-Meteo into both the predictive feature matrix and route scoring formulas."
    )
    add_bullet_point(doc, "Open-Source Geospatial Ecosystem: ", 
        "Engineered an enterprise-grade spatial recommendation system leveraging open-source OpenStreetMap and OpenRouteService APIs without recurring proprietary licensing costs."
    )
    add_bullet_point(doc, "Administrative Disruption Governance: ", 
        "Established an administrative management portal enabling verified real-time road closures, construction zones, and severe hazard alerts to dynamically override routing recommendations."
    )

    # 6.4 System Outcomes
    add_main_heading(doc, "6.4 System Outcomes")
    add_hint_paragraph(doc, 
        "Evaluating tangible system deliverables confirms whether functional goals were accomplished. This section summarizes the operational capabilities delivered by RouteIQ."
    )
    add_body_paragraph(doc, 
        "The developed RouteIQ system successfully achieves all target operational outcomes: commuters can register accounts, log in, configure origin-destination "
        "queries with future departure timestamps, view multi-route alternatives on an interactive Leaflet map, inspect color-coded congestion severity overlays, "
        "examine forecasted speed profiles up to 9 hours ahead, evaluate side-by-side trade-off matrices, and follow algorithmic route recommendations that minimize "
        "transit delays and meteorological risks."
    )

    # 6.5 Limitations
    add_main_heading(doc, "6.5 Limitations")
    add_hint_paragraph(doc, 
        "Objective self-assessment identifies areas requiring ongoing refinement. This section outlines the existing limitations of the current implementation."
    )
    add_body_paragraph(doc, 
        "The project notes several operational limitations: (1) Telemetry Volume: The empirical evaluation was conducted over 7 days of real TomTom sensor data (augmented with synthetic corridor telemetry). Expanding telemetry collection over multiple seasons is needed to capture annual cyclic variations. (2) Spatial Scope: Deep learning weights were validated on 41 monitored road segments across Coimbatore, Tamil Nadu; porting to other cities requires local telemetry retraining. (3) Reliance on External APIs: System response latency is partially bounded by third-party web services."
    )

    # 6.6 Future Enhancements
    add_main_heading(doc, "6.6 Future Enhancements")
    add_hint_paragraph(doc, 
        "Anticipating future technological trends provides a roadmap for continuing research and industrialization. This section details planned future enhancements for RouteIQ."
    )
    add_body_paragraph(doc, 
        "Future enhancements for the RouteIQ platform encompass:"
    )
    add_bullet_point(doc, "Graph Neural Network (GNN) Integration: ", 
        "Augmenting PatchTST with Spatio-Temporal Graph Neural Networks (e.g., STGCN, DCRNN) to explicitly model spatial topological dependencies between adjacent road segments."
    )
    add_bullet_point(doc, "Real-Time Telemetry Streaming: ", 
        "Transitioning from 15-minute polling to real-time event streaming architectures using Apache Kafka or MQTT, enabling immediate reaction to micro-congestion events."
    )
    add_bullet_point(doc, "Native Mobile Applications: ", 
        "Developing cross-platform mobile applications in React Native or Flutter equipped with turn-by-turn voice guidance and on-device GPS tracking."
    )
    add_bullet_point(doc, "Automated Incident Sensing: ", 
        "Integrating computer vision models over municipal CCTV feeds or crowd-sourced hazard voting to supplement administrator-logged disruption notices."
    )
    add_bullet_point(doc, "Personalized Driver Preferences: ", 
        "Incorporating commuter behavioral profiling to adapt CatBoost route ranking according to individual driving styles, vehicle fuel types, or toll preferences."
    )

    # 6.7 Conclusion
    add_main_heading(doc, "6.7 Conclusion")
    add_hint_paragraph(doc, 
        "This section delivers the overarching conclusions drawn from the design, implementation, and evaluation of RouteIQ."
    )
    add_body_paragraph(doc, 
        "RouteIQ demonstrates that combining deep-learning time-series forecasting with gradient-boosted decision trees offers a compelling, practical solution "
        "to the challenges of urban vehicular congestion. By projecting traffic conditions up to nine hours into the future, RouteIQ transforms route recommendation "
        "from a reactive snapshot into a forward-looking decision process. The integration of OpenStreetMap, OpenRouteService, Open-Meteo, PyTorch PatchTST, "
        "CatBoost, Flask, and React establishes a robust, extensible architectural template for next-generation intelligent transportation systems."
    )

    # 6.8 Final Concluding Remarks
    add_main_heading(doc, "6.8 Final Concluding Remarks")
    add_hint_paragraph(doc, 
        "This concluding section summarizes the entire dissertation, providing closing academic remarks on the project's journey."
    )
    add_body_paragraph(doc, 
        "This chapter concluded the mini project report for RouteIQ: Smart Traffic Congestion Prediction and Route Recommendation System. "
        "The project work was summarized, major technological contributions were highlighted, and system deliverables were confirmed against original objectives. "
        "Current constraints were objectively acknowledged, and concrete avenues for future exploration—including Graph Neural Networks, real-time telemetry streaming, "
        "and mobile applications—were delineated. RouteIQ represents a significant step toward smarter, more sustainable urban mobility."
    )
